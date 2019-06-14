# -*- coding: utf-8 -*-
"""
Created on 2018/10/30

@author: gaoan
"""
import time
# from tigeropen.common.consts import QuoteChangeKey
from tigeropen.push.push_client import PushClient
from tigeropen.examples.client_config import get_client_config


def on_query_subscribed_quote(symbols, focus_keys, limit, used):
    """
    查询已订阅symbol回调
    :param symbols: 订阅合约的列表
    :param focus_keys: 每个合约订阅的 key 列表
    :param limit: 当前 tigerid 可以订阅的合约数量
    :param used: 目前已订阅的合约数量
    :return:
    """
    print(symbols, focus_keys, limit, used)


def on_quote_changed(symbol, items, hour_trading):
    """
    行情推送回调
    :param symbol: 订阅的证券代码
    :param items: list，每个元素是一个tuple，对应订阅的字段名称和值
    :param hour_trading: 是否为盘前盘后的交易
    :return:
    """
    print(symbol, items, hour_trading)


def on_order_changed(account, items):
    print(account, items)


def on_asset_changed(account, items):
    print(account, items)


def on_position_changed(account, items):
    print(account, items)


if __name__ == '__main__':
    client_config = get_client_config()
    protocol, host, port = client_config.socket_host_port
    push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))

    # 行情变动回调
    push_client.quote_changed = on_quote_changed
    # 已订阅 symbol 查询回调
    push_client.subscribed_symbols = on_query_subscribed_quote
    # 订单变动回调
    # push_client.order_changed = on_order_changed
    # 资产变动回调
    # push_client.asset_changed = on_asset_changed
    # 持仓变动回调
    # push_client.position_changed = on_position_changed

    # 建立推送连接
    push_client.connect(client_config.tiger_id, client_config.private_key)

    # 订阅行情
    push_client.subscribe_quote(['AAPL', 'GOOG'])
    # 可以指定关注的 key
    # push_client.subscribe_quote(['MSFT', 'AMD'], focus_keys=[QuoteChangeKey.ask_price, QuoteChangeKey.bid_price])
    # 订阅资产变动
    push_client.subscribe_asset()
    # 订阅订单变动
    push_client.subscribe_order()
    # 订阅持仓变动
    push_client.subscribe_position()
    # 查询已订阅的 symbol
    push_client.query_subscribed_quote()

    time.sleep(600)
    push_client.disconnect()
