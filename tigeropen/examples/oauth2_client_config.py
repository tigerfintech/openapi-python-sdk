# -*- coding: utf-8 -*-
"""
Shared setup for the OAuth2 demos.

Building a client for OAuth2 is a one-line change from signature mode: set
``config.authentication``. After that, ``tiger_id`` and the private key play no part --
every request carries ``Authorization: Bearer <access_token>`` instead of a signature.

Optional environment variables::

    TIGEROPEN_OAUTH2_ISSUER   authorization server; defaults to the production address
    TIGEROPEN_CLIENT_ID       a client_id you registered yourself; omit to let the SDK
                              register one automatically and store it locally
    TIGEROPEN_SERVER_URL      business gateway; defaults to production
    TIGEROPEN_SOCKET_URL      push endpoint, e.g. ``ssl://host:9883``
    TIGEROPEN_HOME            where tokens are stored; defaults to ``~/.tiger/openapi``
"""
import os

from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2SessionManager
from tigeropen.tiger_open_config import TigerOpenClientConfig

ENV_SERVER_URL = 'TIGEROPEN_SERVER_URL'
ENV_SOCKET_URL = 'TIGEROPEN_SOCKET_URL'

#: Sample symbols per market. Market data permissions are granted per market, so
#: hardcoding US symbols makes an HK-only account report "permission denied", which reads
#: like an authentication failure but is not one.
_SAMPLE_SYMBOLS = (
    ('us', ['AAPL', 'NVDA']),
    ('hk', ['00700']),
    ('a', ['600519']),
)


def get_session_manager():
    """Build the session. Sends no requests, so it works offline."""
    return OAuth2SessionManager(
        # Unset falls back to TIGEROPEN_OAUTH2_ISSUER, then the production default
        issuer=os.environ.get('TIGEROPEN_OAUTH2_ISSUER'),
        # Unset means the SDK registers a client itself and stores the id locally
        client_id=os.environ.get('TIGEROPEN_CLIENT_ID'),
    )


def get_oauth2_client_config(sessions):
    """
    :param sessions: :class:`OAuth2SessionManager`
    :return: a :class:`TigerOpenClientConfig` set up for OAuth2
    """
    config = TigerOpenClientConfig()
    # The whole change relative to signature mode: once set, tiger_id and the private key
    # play no part at all
    config.authentication = OAuth2Authentication(sessions)

    server_url = os.environ.get(ENV_SERVER_URL)
    if server_url:
        config.server_url = server_url
        # QuoteClient reads quote_server_url; without it quote requests would still go to
        # the default gateway
        config.quote_server_url = server_url

    socket_url = os.environ.get(ENV_SOCKET_URL)
    if socket_url:
        config.socket_host_port = _parse_socket_url(socket_url)

    return config


def describe(config, sessions, token):
    """Print what is actually in effect -- the quickest way to see how a run is set up."""
    print('issuer      :', sessions.issuer)
    print('client_id   :', sessions.client_id)
    print('业务网关    :', config.server_url)
    print('行情网关    :', config.quote_server_url)
    print('拿到的 scope :', token.scope)
    print('access token 还有 %d 秒到期' % (token.remaining_millis() // 1000))
    print('有 refresh token:', token.has_refresh_token())
    print()


def sample_symbols(permissions):
    """Pick symbols the account can actually query.

    :param permissions: ``QuoteClient.permissions``, e.g.
        ``[{'name': 'hkStockQuoteLv2', ...}, ...]``
    """
    names = [str(p.get('name', '')).lower() for p in (permissions or [])]
    for prefix, symbols in _SAMPLE_SYMBOLS:
        if any(n.startswith(prefix) for n in names):
            return symbols
    # No permissions reported, or names we do not recognise: try US
    return _SAMPLE_SYMBOLS[0][1]


def _parse_socket_url(url):
    """``ssl://host:9883`` / ``tcp://host:9889`` -> ``(protocol, host, port)``"""
    protocol, _, rest = url.rpartition('://')
    host, _, port = rest.partition(':')
    # push_client turns on TLS when protocol == 'ssl'
    protocol = 'ssl' if protocol in ('ssl', 'wss', 'https') else 'tcp'
    return protocol, host, int(port)
