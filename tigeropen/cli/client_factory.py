# -*- coding: utf-8 -*-
"""
Client factory module for CLI.
Handles config resolution, private key loading, and lazy client creation.
"""
import os
from pathlib import Path

from jproperties import Properties

from tigeropen import __VERSION__
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.cli.oauth2_config import attach_oauth2, build_session_manager

DEFAULT_CONFIG_DIR = str(Path.home() / '.tigeropen')


def _load_props(config_path):
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


def _resolve_oauth2_ctx(ctx_obj, props):
    """Merge OAuth2 settings: explicit CLI options win over props, props over defaults."""
    auth = ctx_obj.get('auth') or props.get('auth_mode') or 'signature'
    issuer = ctx_obj.get('issuer') or props.get('issuer')
    client_id = ctx_obj.get('client_id') or props.get('client_id')
    return {'auth': auth, 'issuer': issuer, 'client_id': client_id}


def resolve_private_key(key_input):
    """
    Resolve private key from file path, PEM string, or raw key string.

    :param key_input: file path, PEM string with headers, or raw key string
    :return: stripped private key string (no PEM headers)
    """
    if not key_input:
        return ''

    # If it's an existing file path, read from file
    if os.path.isfile(key_input):
        return read_private_key(key_input)

    # If it's a full PEM string with headers, strip them
    if '-----BEGIN RSA PRIVATE KEY-----' in key_input:
        return key_input.replace('-----BEGIN RSA PRIVATE KEY-----', '') \
            .replace('-----END RSA PRIVATE KEY-----', '') \
            .replace('\n', '').strip()

    # Otherwise treat as raw key string
    return key_input


def build_config(ctx_obj):
    """
    Build TigerOpenClientConfig from CLI context dict.

    In signature mode (the default) tiger_id / private_key are set as before; in
    OAuth2 mode the config is given an OAuth2Authentication and tiger_id / the
    private key play no part at all.

    :param ctx_obj: dict with optional keys: config_path, auth, issuer, client_id,
        tiger_id, account, private_key, language
    :return: TigerOpenClientConfig
    """
    config_path = ctx_obj.get('config_path') or DEFAULT_CONFIG_DIR
    config = TigerOpenClientConfig(enable_dynamic_domain=False,
                                   props_path=config_path)
    config._channel = f"tigercli"

    # OAuth2 settings may come from --auth/--issuer/--client-id or from the props
    # file written by `config init --auth oauth2`. Explicit CLI options win.
    props = _load_props(config_path)
    oauth2 = _resolve_oauth2_ctx(ctx_obj, props)

    if oauth2['auth'] == 'oauth2':
        sessions = build_session_manager(issuer=oauth2['issuer'],
                                         client_id=oauth2['client_id'])
        attach_oauth2(config, sessions)
    else:
        if ctx_obj.get('tiger_id'):
            config.tiger_id = ctx_obj['tiger_id']
        if ctx_obj.get('private_key'):
            config.private_key = resolve_private_key(ctx_obj['private_key'])

    # account is a business parameter, not an authentication one: needed in both modes
    if ctx_obj.get('account'):
        config.account = ctx_obj['account']
    if ctx_obj.get('language'):
        config.language = ctx_obj['language']

    return config


def get_quote_client(ctx_obj):
    """Lazily create and cache a QuoteClient.

    Grabs quote permission by default. The device_id is this machine's MAC address,
    so on a given machine grabbing is idempotent: it re-binds market-data permission
    to the same device every time and kicks nothing else off. Without it, quote
    commands fail with "permission denied" even when the account has the entitlement.
    """
    if '_quote_client' not in ctx_obj:
        from tigeropen.quote.quote_client import QuoteClient
        config = build_config(ctx_obj)
        ctx_obj['_quote_client'] = QuoteClient(config)
    return ctx_obj['_quote_client']


def get_trade_client(ctx_obj):
    """Lazily create and cache a TradeClient."""
    if '_trade_client' not in ctx_obj:
        from tigeropen.trade.trade_client import TradeClient
        config = build_config(ctx_obj)
        ctx_obj['_trade_client'] = TradeClient(config)
    return ctx_obj['_trade_client']
