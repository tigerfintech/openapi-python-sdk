# -*- coding: utf-8 -*-
"""
Device code authorization (RFC 8628), for environments with no local browser: a server
reached over ssh, a container, a Raspberry Pi.

The SDK obtains a short user code and a verification URI; the user opens that URI on
*another* device, enters the code and approves, while the SDK polls until approval.

This path is **less secure** than the loopback + PKCE flow in ``oauth2_login_demo``: the
user approves on another device, so the SDK cannot confirm the approver is the person
operating this machine. Prefer that demo wherever a browser exists.

Environment variables are the same as ``oauth2_login_demo``; see oauth2_client_config.py.
"""
import logging

from tigeropen.auth.oauth2 import OAuth2Exception
from tigeropen.examples.oauth2_client_config import (
    describe,
    get_oauth2_client_config,
    get_session_manager,
    sample_symbols,
)
from tigeropen.quote.quote_client import QuoteClient


def show_device_code(device):
    print()
    print('请在另一台有浏览器的设备上打开：')
    print()
    if device.verification_uri_complete:
        # This URI already carries the code, saving the user a manual entry step
        print('  ' + device.verification_uri_complete)
        print()
        print('或者打开 %s 后输入验证码：' % device.verification_uri)
    else:
        print('  ' + device.verification_uri)
        print()
        print('然后输入验证码：')
    print()
    print('      ' + device.user_code)
    print()
    print('等待授权…（%d 秒内有效）' % device.expires_in)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    sessions = get_session_manager()
    token = sessions.status()
    if token is None:
        token = sessions.login_with_device_code(show_device_code)
    else:
        print('本地已有授权，直接复用。')

    config = get_oauth2_client_config(sessions)
    print()
    describe(config, sessions, token)

    # Constructing a QuoteClient issues grab_quote_permission, a full Bearer-authenticated
    # request; if it succeeds, authentication works
    quote_client = QuoteClient(config)
    print('行情权限    :', quote_client.permissions)
    symbols = sample_symbols(quote_client.permissions)
    try:
        print('行情快照 %s: %s' % (symbols, quote_client.get_briefs(symbols)))
    except Exception as e:
        # A market permission or environment issue, not an authentication one
        print('行情快照调用失败 ->', e)


if __name__ == '__main__':
    try:
        main()
    except OAuth2Exception as e:
        print('授权失败:', e)
        print('类别    :', e.category.name)
