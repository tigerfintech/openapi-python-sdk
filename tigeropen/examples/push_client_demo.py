# -*- coding: utf-8 -*-
"""
Created on 2018/10/30

@author: gaoan
"""
import time
from tigeropen.push.push_client import PushClient
from tigeropen.examples.client_config import get_client_config


def on_query_subscribed_quote(symbols, focus_keys, limit, used):
    print(symbols, focus_keys, limit, used)


def on_quote_changed(symbol, items, hour_trading):
    print(symbol, items, hour_trading)


if __name__ == '__main__':
    client_config = get_client_config()
    protocol, host, port = client_config.socket_host_port
    push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))
    push_client.quote_changed = on_quote_changed
    push_client.subscribed_symbols = on_query_subscribed_quote
    push_client.connect(client_config.tiger_id, client_config.private_key)

    push_client.query_subscribed_quote()
    push_client.subscribe_quote(['AAPL', 'GOOG'])
    push_client.subscribe_asset()

    time.sleep(600)
    push_client.disconnect()
