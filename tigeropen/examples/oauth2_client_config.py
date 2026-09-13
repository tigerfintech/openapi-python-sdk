# -*- coding: utf-8 -*-
"""
Shared configuration for the OAuth2 demos.

**The issuer, the business gateway and the response-verification public key must all
point at the same environment.** Any mismatch produces an error that points nowhere near
the real cause:

- production gateway with a token from a test authorization server ->
  ``common param error(tigerId null is illegal)``. The production gateway has OAuth2
  disabled, so a body without ``sign`` takes the signature-verification branch and it
  complains that tigerId is missing
- test gateway with the production public key -> ``response sign verify failed``. The
  test gateway signs responses with the sandbox private key

The built-in issuer is now production, so the pairing table below does not match and the
SDK defaults apply -- nothing to configure for the normal case.

The table still matters when ``TIGEROPEN_OAUTH2_ISSUER`` points at a test authorization
server: the matching gateway and public key are then paired automatically, instead of
everyone hitting ``tigerId null is illegal`` once and going looking for an environment
variable. ``TIGEROPEN_SERVER_URL`` overrides either way.
"""
import os

from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2SessionManager
from tigeropen.tiger_open_config import SANDBOX_TIGER_PUBLIC_KEY, TigerOpenClientConfig

#: Business gateway. Unset means pair by issuer, then fall back to the SDK default.
ENV_SERVER_URL = 'TIGEROPEN_SERVER_URL'
#: Push endpoint, e.g. ``ws://10.68.171.142:9889`` or ``ssl://host:9883``
ENV_SOCKET_URL = 'TIGEROPEN_SOCKET_URL'

#: Business gateway matching a test issuer. Only consulted when the issuer is overridden
#: to point at a test environment; the production issuer is absent on purpose, so the SDK
#: defaults apply untouched.
_TEST_ENV_GATEWAY = {
    'https://openapi-oauth2-test.qa.tigerbrokers.net':
        'https://openapi-test.qa.tigerbrokers.net/gateway',
}

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
        # Unset falls back to TIGEROPEN_OAUTH2_ISSUER, then the built-in default
        issuer=os.environ.get('TIGEROPEN_OAUTH2_ISSUER'),
        # Unset means dynamic registration: the client_id is obtained and stored locally
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

    # An explicit setting wins; otherwise pair by issuer
    server_url = os.environ.get(ENV_SERVER_URL)
    paired = server_url or _TEST_ENV_GATEWAY.get(sessions.issuer)
    if paired:
        config.server_url = paired
        # QuoteClient uses quote_server_url; without it quote requests still go to production
        config.quote_server_url = paired
        # The test gateway signs responses with the sandbox private key. Response
        # verification still runs under OAuth2 -- it proves the response came from Tiger,
        # which is independent of how the request was authenticated.
        config.tiger_public_key = SANDBOX_TIGER_PUBLIC_KEY
        if not server_url:
            print('提示        : issuer 是测试地址，已自动把网关指向 %s' % paired)
            print('              设 %s 可以覆盖' % ENV_SERVER_URL)

    socket_url = os.environ.get(ENV_SOCKET_URL)
    if socket_url:
        config.socket_host_port = _parse_socket_url(socket_url)

    return config


def describe(config, sessions, token):
    """Print the environment actually in effect -- the fastest clue on a mismatch."""
    print('issuer      :', sessions.issuer)
    print('client_id   :', sessions.client_id)
    print('业务网关    :', config.server_url)
    print('行情网关    :', config.quote_server_url)
    print('拿到的 scope :', token.scope)
    print('access token 还有 %d 秒到期' % (token.remaining_millis() // 1000))
    print('有 refresh token:', token.has_refresh_token())
    # Still mismatched here means a test issuer that _TEST_ENV_GATEWAY does not know
    if _looks_like_test(sessions.issuer) and not _looks_like_test(config.server_url):
        print()
        print('注意        : issuer 指向测试环境，网关却是生产地址。')
        print('              请设置 %s 指向同一套环境，否则会得到' % ENV_SERVER_URL)
        print('              "common param error(tigerId null is illegal)"。')
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


def _looks_like_test(url):
    return any(marker in (url or '') for marker in ('.qa.', '-test.', 'sandbox'))


def _parse_socket_url(url):
    """``ws://host:9889`` / ``ssl://host:9883`` -> ``(protocol, host, port)``"""
    protocol, _, rest = url.rpartition('://')
    host, _, port = rest.partition(':')
    # push_client turns on TLS when protocol == 'ssl'
    protocol = 'ssl' if protocol in ('ssl', 'wss', 'https') else 'tcp'
    return protocol, host, int(port)
