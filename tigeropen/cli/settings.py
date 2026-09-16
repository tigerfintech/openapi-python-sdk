# -*- coding: utf-8 -*-
"""Where CLI settings come from. One resolver, shared by every command."""
import os
from pathlib import Path

from jproperties import Properties

DEFAULT_CONFIG_DIR = str(Path.home() / '.tigeropen')

#: Environment variable for a manually registered clientId (dynamic registration otherwise)
ENV_CLIENT_ID = 'TIGEROPEN_CLIENT_ID'

#: Environment variable for the trading account
ENV_ACCOUNT = 'TIGEROPEN_ACCOUNT'

#: Signature credentials. Read here only to recognise a signature installation; the SDK
#: config layer is what consumes them.
ENV_TIGER_ID = 'TIGEROPEN_TIGER_ID'
ENV_PRIVATE_KEY = 'TIGEROPEN_PRIVATE_KEY'


def load_props(config_path):
    """Load the properties file at a config dir / file path, or an empty dict."""
    if os.path.isdir(config_path):
        from tigeropen.tiger_open_config import DEFAULT_PROPS_FILE
        props_file = os.path.join(config_path, DEFAULT_PROPS_FILE)
    else:
        props_file = config_path
    if not os.path.exists(props_file):
        return {}
    p = Properties()
    with open(props_file, 'rb') as f:
        p.load(f, 'utf-8')
    return {k: v.data for k, v in p.items()}


def resolve_settings(ctx_obj):
    """Resolve the settings every command shares.

    Precedence: command-line option, environment variable, properties file, built-in default.
    Click applies the environment for options declared with ``envvar``, so what arrives here is
    already option-or-environment.

    An option that also lives in the properties file must be declared ``default=None``, or it
    shadows the file.

    :param ctx_obj: the click context dict
    :return: dict with config_path, auth, issuer, client_id, account
    """
    config_path = ctx_obj.get('config_path') or DEFAULT_CONFIG_DIR
    props = load_props(config_path)
    issuer = ctx_obj.get('issuer') or props.get('issuer')
    client_id = ctx_obj.get('client_id') or props.get('client_id')
    return {
        'config_path': config_path,
        'auth': (ctx_obj.get('auth') or props.get('auth_mode')
                 or _preferred_auth_mode(ctx_obj, props, issuer, client_id)),
        'issuer': issuer,
        'client_id': client_id,
        'account': ctx_obj.get('account') or props.get('account'),
    }


def _preferred_auth_mode(ctx_obj, props, issuer, client_id):
    """Pick an authentication mode when nothing says which one to use.

    OAuth2 unless this machine is set up for signature mode. Reads local files only.
    """
    if _has_oauth2_authorization(issuer, client_id):
        return 'oauth2'
    if _has_signature_credentials(ctx_obj, props):
        return 'signature'
    return 'oauth2'


#: Every properties key the SDK config layer accepts for the private key.
PRIVATE_KEY_PROPS_KEYS = ('private_key', 'private_key_pk8', 'private_key_pk1')


def _has_signature_credentials(ctx_obj, props):
    """Whether a tigerId and a private key are available from any of their sources."""
    tiger_id = (ctx_obj.get('tiger_id') or props.get('tiger_id')
                or os.environ.get(ENV_TIGER_ID))
    private_key = (ctx_obj.get('private_key')
                   or next((props[k] for k in PRIVATE_KEY_PROPS_KEYS if props.get(k)), None)
                   or os.environ.get(ENV_PRIVATE_KEY))
    return bool(tiger_id and private_key)


def _has_oauth2_authorization(issuer, client_id):
    """Whether a usable authorization is already stored for this issuer."""
    try:
        from tigeropen.cli.oauth2_config import build_session_manager
        return build_session_manager(issuer=issuer, client_id=client_id).is_authorized()
    except Exception:
        # An unreadable store answers nothing; leave it to the other signals.
        return False
