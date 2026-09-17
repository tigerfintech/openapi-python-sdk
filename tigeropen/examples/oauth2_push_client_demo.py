# -*- coding: utf-8 -*-
"""
Subscribe to push data with an OAuth2 access token -- no tigerId, no private key, no
signing.

Normally run ``oauth2_login_demo`` or ``oauth2_device_code_demo`` first so a token is
already on disk; if there is none, this demo authorizes once itself. A real long-lived
subscriber should **not** do that -- a process holding a connection for hours should not
start a user interaction on its own. It is here only so the demo runs from a clean state.

**Protobuf only.** OAuth2 over STOMP is rejected when ``PushClient`` is constructed: a
STOMP frame has nowhere to carry a token and the protocol has no REFRESH_TOKEN equivalent.

Token rotation is driven by the heartbeat and only fires with less than 5 minutes
remaining, so a short-lived connection normally shows no rotation logs.

Optional::

    export TIGEROPEN_HOLD_SECONDS=600      # how long to stay connected, default 600

See oauth2_client_config.py for the rest.
"""
import logging
import os
import time
import webbrowser

from tigeropen.examples.oauth2_client_config import (
    describe,
    get_oauth2_client_config,
    get_session_manager,
    sample_symbols,
)
from tigeropen.push.pb.QuoteBasicData_pb2 import QuoteBasicData
from tigeropen.push.push_client import PushClient
from tigeropen.quote.quote_client import QuoteClient

SCOPE_QUOTE = 'api.quote:read'


def on_quote_changed(frame: QuoteBasicData):
    print('quote:', frame.symbol, frame.latestPrice)


def show_authorization_url(url):
    print('请在浏览器里打开下面的链接完成登录与授权：')
    print()
    print('  ' + url)
    print()
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    sessions = get_session_manager()
    token = sessions.login_if_needed(show_authorization_url)

    config = get_oauth2_client_config(sessions)
    print()
    describe(config, sessions, token)

    if not token.has_refresh_token():
        # Worth calling out before connecting: the connection outlives the token, and
        # without a refresh_token there is no way to rotate it in place, so the server
        # closes the connection once the token it pinned expires
        print('注意        : 没有 refresh token，连接活过 token TTL 后会被服务端关掉')
    if token.scope and SCOPE_QUOTE not in token.scope:
        print('注意        : scope 里没有 %s，行情订阅会被拒' % SCOPE_QUOTE)

    # A QuoteClient is built only to obtain the market data permissions; claiming device
    # access before subscribing is what a real subscriber does too
    quote_client = QuoteClient(config)
    symbols = sample_symbols(quote_client.permissions)
    print('行情权限    :', quote_client.permissions)

    protocol, host, port = config.socket_host_port
    print('推送地址    : %s://%s:%s' % (protocol, host, port))
    print()

    # use_protobuf must stay True (the default); OAuth2 does not support STOMP
    push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'), client_config=config)
    push_client.quote_changed = on_quote_changed

    # connect() needs no tigerId or private key in OAuth2 mode
    push_client.connect()
    try:
        print('订阅行情    :', symbols)
        push_client.subscribe_quote(symbols)
        hold_seconds = int(os.environ.get('TIGEROPEN_HOLD_SECONDS') or 600)
        print('保持连接 %d 秒。期间关注日志里的：' % hold_seconds)
        print('  refresh token sent         token 快到期，已就地轮换（不重连）')
        print('  refresh token accepted     服务端接受了新 token')
        print('  refresh token got no reply 服务端不支持轮换，连接继续可用')
        time.sleep(hold_seconds)
    finally:
        push_client.disconnect()


if __name__ == '__main__':
    main()
