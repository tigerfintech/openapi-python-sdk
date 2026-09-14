# -*- coding: utf-8 -*-
"""
Browser authorization with OAuth2, then a business call -- no tigerId, no private key,
no signing.

Authorization uses loopback + PKCE: the SDK starts a temporary callback listener on
127.0.0.1, hands you the authorization URL, and the browser redirects the code back to
this machine. The token is exchanged and stored under ``~/.tiger/openapi/tokens/`` with
mode 0600, and later runs reuse it without opening a browser again.

Compared with signature mode, the only change to business code is the
``config.authentication`` line.

Everything is optional to configure -- run it as is and it uses the production
authorization server. See oauth2_client_config.py for the environment variables.
"""
import datetime
import logging
import webbrowser

from tigeropen.auth.oauth2 import OAuth2Exception
from tigeropen.examples.oauth2_client_config import (
    describe,
    get_oauth2_client_config,
    get_session_manager,
    sample_symbols,
)
from tigeropen.quote.quote_client import QuoteClient


def show_authorization_url(url):
    print('请在浏览器里打开下面的链接完成登录与授权：')
    print()
    print('  ' + url)
    print()
    print('等待回调…')
    try:
        webbrowser.open(url)
    except Exception:
        # Headless environment: the printed URL above is the fallback, not an error
        pass


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    sessions = get_session_manager()
    # Reuse a usable token, else refresh silently, else open a browser
    token = sessions.login_if_needed(show_authorization_url)

    config = get_oauth2_client_config(sessions)
    print()
    describe(config, sessions, token)

    # Reaching this point proves authentication works: constructing a QuoteClient issues
    # grab_quote_permission, a full Bearer-authenticated request whose response is verified
    quote_client = QuoteClient(config)
    print('行情权限    :', quote_client.permissions)
    print()

    # The calls below are wrapped: a failure is usually a market permission or environment
    # issue, not an authentication one, and should not kill the demo
    today = datetime.date.today()
    _try('交易日历', lambda: quote_client.get_trading_calendar(
        'HK', str(today), str(today + datetime.timedelta(days=7))))
    # get_market_status(market, lang) takes two arguments, not the calendar's three
    _try('市场状态', lambda: quote_client.get_market_status('HK'))
    # Market data permissions are granted per market, so an account without US access gets
    # "permission denied" for AAPL -- a business permission issue, not an auth one
    symbols = sample_symbols(quote_client.permissions)
    _try('行情快照 %s' % symbols, lambda: quote_client.get_briefs(symbols))


def _try(name, fn):
    try:
        # Responses can be long; what matters here is whether the call went through
        text = str(fn())
        print('%-14s: %s' % (name, text if len(text) <= 160 else text[:160] + ' …'))
    except Exception as e:
        print('%-14s: 调用失败 -> %s' % (name, e))
        print('%-14s  （认证是好的，否则前面 grab_quote_permission 就过不去）' % '')


if __name__ == '__main__':
    try:
        main()
    except OAuth2Exception as e:
        # The category already says what to do: re-authorize, fix the config, or retry
        print('授权失败:', e)
        print('类别    :', e.category.name)
