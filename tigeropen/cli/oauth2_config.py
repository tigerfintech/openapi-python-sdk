# -*- coding: utf-8 -*-
"""
Shared OAuth2 helpers for the CLI.

Pulls together the pieces a CLI command needs to run in OAuth2 mode: building a
session manager and attaching it to a client config. The pairing of a test issuer
with its business gateway mirrors ``examples/oauth2_client_config.py`` so CLI users
get the same environment-matched defaults without copying the table everywhere.
"""
from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2SessionManager
from tigeropen.tiger_open_config import SANDBOX_TIGER_PUBLIC_KEY

#: Environment variable for a manually registered clientId (dynamic registration otherwise)
TIGEROPEN_CLIENT_ID = 'TIGEROPEN_CLIENT_ID'


def _looks_like_test(url):
    return any(marker in (url or '') for marker in ('.qa.', '-test.', 'sandbox'))


def _pair_test_gateway(issuer):
    """Return the test-environment business gateway for a test issuer, else None.

    The issuer is the built-in test authorization server address and the business
    gateway is its ``/gateway`` twin. The substitution is written out so the test
    hostname appears in this repo only where it is the issuer (session_manager),
    not repeated as a second hardcoded gateway address.
    """
    if not issuer:
        return None
    if not _looks_like_test(issuer):
        return None
    # https://openapi-oauth2-test.<test-domain> -> https://openapi-test.<test-domain>/gateway
    rest = issuer.split('-oauth2-test', 1)[-1]
    if rest == issuer:
        return None
    return 'https://openapi-test' + rest + '/gateway'


def looks_like_test(url):
    """Whether a URL points at a test / sandbox environment."""
    return _looks_like_test(url)


def build_session_manager(issuer=None, client_id=None):
    """Build an OAuth2SessionManager. Sends no requests, so it works offline."""
    return OAuth2SessionManager(
        issuer=issuer,
        client_id=client_id,
    )


def attach_oauth2(config, sessions):
    """Attach OAuth2 authentication to a client config.

    Sets ``config.authentication`` and, when the issuer is a known test address,
    points the business and quote gateways at the matching test environment along
    with the sandbox response-verification public key.

    In OAuth2 mode the private key plays no part at all. It is cleared here so a
    pre-existing signature config (props with ``private_key_pk8``) cannot leak a
    key into a session that never signs; nothing in the request path reads it, and
    leaving it in place would only mislead anyone inspecting the config.
    """
    config.authentication = OAuth2Authentication(sessions)
    config.private_key = ''
    config.tiger_id = ''
    paired = _pair_test_gateway(sessions.issuer)
    if paired:
        config.server_url = paired
        config.quote_server_url = paired
        config.tiger_public_key = SANDBOX_TIGER_PUBLIC_KEY
    return config
