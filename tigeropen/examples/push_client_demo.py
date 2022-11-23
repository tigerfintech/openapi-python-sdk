# -*- coding: utf-8 -*-
"""
Created on 2018/10/30

@author: gaoan
"""
import time
# from tigeropen.common.consts import QuoteKeyType
import pandas as pd

from tigeropen.push.push_client import PushClient
from tigeropen.examples.client_config import get_client_config


def query_subscribed_callback(data):
    """
    callback of PushClient.query_subscribed_quote
    :param data:
        example:
        {'subscribed_symbols': ['QQQ'], 'limit': 1200, 'used': 1, 'symbol_focus_keys': {'qqq': ['open', 'prev_close', 'low', 'volume', 'latest_price', 'close', 'high']},
         'subscribed_quote_depth_symbols': ['NVDA'], 'quote_depth_limit': 20, 'quote_depth_used': 1,
         'subscribed_trade_tick_symbols': ['QQQ', 'AMD', '00700'], 'trade_tick_limit': 1200, 'trade_tick_used': 3
         }
    :return:
    """
    print(data)


def on_query_subscribed_quote(symbols, focus_keys, limit, used):
    """
    deprecated. Use query_subscribed_callback instead.
    查询已订阅symbol回调
    :param symbols: 订阅合约的列表
    :param focus_keys: 每个合约订阅的 key 列表
    :param limit: 当前 tigerid 可以订阅的合约数量
    :param used: 目前已订阅的合约数量
    :return:
        返回示例:
        symbols: ['00700', 'SPY'],
        focus_keys: {'00700': ['ask_size', 'latest_price', 'ask_price', 'prev_close', 'open', 'minute', 'low', 'volume',
         'bid_price', 'bid_size', 'high', 'close'], 'SPY': ['ask_size', 'latest_price', 'ask_price', 'prev_close',
         'open', 'minute', 'low', 'volume', 'bid_price', 'bid_size', 'high', 'close']},
        limit: 100,
        used: 2

    """
    print(symbols, focus_keys, limit, used)


def on_quote_changed(symbol, items, hour_trading):
    """
    行情推送回调
    :param symbol: 订阅的证券代码
    :param items: list，每个元素是一个tuple，对应订阅的字段名称和值
    :param hour_trading: 是否为盘前盘后的交易
    :return:
    items 数据示例
        [('latest_price', 339.8), ('ask_size', 42500), ('ask_price', 340.0), ('bid_size', 1400), ('bid_price', 339.8),
         ('high', 345.0), ('prev_close', 342.4), ('low', 339.2), ('open', 344.0), ('volume', 7361440),
         ('minute', {'p': 339.8, 'a': 341.084, 't': 1568098440000, 'v': 7000, 'h': 340.0, 'l': 339.8}),
         ('timestamp', '1568098469463')]
    深度行情 items 数据示例. 最多只推送前 40 档, 由 3 个等长数组构成，分别代表：price(价格)/volume(数量)/count(单量),
    相邻档位价格可能一样, 其中 count 是可选的
        [('bid_depth',
            '[[127.87,127.86,127.86,127.86,127.85,127.85,127.85,127.84,127.84,127.84,127.84,127.83,127.83, 127.83,127.83,127.83,127.82,127.81,127.8,127.8,127.8,127.8,127.8,127.8,127.8,127.79,127.79,127.78, 127.78, 127.75,127.68,127.6,127.6,127.55,127.5,127.5,127.5,127.5,127.29,127.28],
              [69,2,5,20,1,1,1,18,1,70,80,40,2,330,330,1,40,80,20,10,131,2,30,50,300,1,38,1,1,15,6,20,1,3,100,15,25,30,49,43]
             ]'),
        ('ask_depth',
            '[[127.91,127.94,127.95,127.95,127.95,127.95,127.95,127.96,127.98,127.98,127.98,127.98,127.99,127.99, 128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0, 128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0,128.0],
              [822,4,98,50,5,5,500,642,300,40,1,36,19,1,1,1,1,50,1,1,50,1,100,10,1,1,10,1,1,1,1,5,1,8,1,1,120,70,1,4]
            ]'),
        ('timestamp', 1621933454191)]

    """
    print(symbol, items, hour_trading)


def on_tick_changed(symbol, items):
    """

    :param symbol:
    :param items:
      items example:
        [{'tick_type': '*', 'price': 293.87, 'volume': 102, 'part_code': 'NSDQ',
            'part_code_name': 'NASDAQ Stock Market, LLC (NASDAQ)', 'cond': 'US_FORM_T', 'time': 1656405615779,
            'server_timestamp': 1656405573461, 'type': 'TradeTick', 'quote_level': 'usStockQuote', 'sn': 342,
            'timestamp': 1656405617385},
         {'tick_type': '*', 'price': 293.87, 'volume': 102, 'part_code': 'NSDQ',
          'part_code_name': 'NASDAQ Stock Market, LLC (NASDAQ)', 'cond': 'US_FORM_T', 'time': 1656405616573,
          'server_timestamp': 1656405573461,
          'type': 'TradeTick', 'quote_level': 'usStockQuote', 'sn': 343, 'timestamp': 1656405617385}]

      Futures tick items example:
          [{'tick_type': None, 'price': 15544.0, 'volume': 1, 'part_code': None, 'part_code_name': None, 'cond': None,
           'time': 1667285183000, 'sn': 636960, 'server_timestamp': 1667285184162, 'quote_level': 'quote-fut-tick',
            'type': 'TradeTick', 'timestamp': 1667285184156},
            {'tick_type': None, 'price': 15544.0, 'volume': 1, 'part_code': None, 'part_code_name': None, 'cond': None,
             'time': 1667285183000, 'sn': 636961, 'server_timestamp': 1667285184162, 'quote_level': 'quote-fut-tick',
              'type': 'TradeTick', 'timestamp': 1667285184156},
            {'tick_type': None, 'price': 15544.0, 'volume': 2, 'part_code': None, 'part_code_name': None,
              'cond': None, 'time': 1667285183000, 'sn': 636962, 'server_timestamp': 1667285184162,
              'quote_level': 'quote-fut-tick', 'type': 'TradeTick', 'timestamp': 1667285184156}]
    :return:
    """
    print(symbol, items)
    # convert to DataFrame
    # frame = pd.DataFrame(items)
    # print(frame)


def on_order_changed(account, items):
    """

    :param account:
    :param items:
    :return:
    items 数据示例:
        [('order_type', 'LMT'), ('symbol', 'ABCD'), ('order_id', 1000101463), ('sec_type', 'STK'), ('filled', 100),
        ('quantity', 100), ('segment', 'summary'), ('action', 'BUY'), ('currency', 'USD'), ('id', 173612806463631360),
        ('order_time', 1568095814556), ('time_in_force', 'DAY'), ('identifier', 'ABCD'), ('limit_price', 113.7),
        ('outside_rth', True), ('avg_fill_price', 113.7), ('trade_time', 1568095815418),
        ('status', <OrderStatus.FILLED: 'Filled'>)]
    """
    print(account, items)

def on_transaction_changed(account, items):
    """

    :param account:
    :param items:
    :return:
    account:11111,
    items: [('id', 28819544190616576), ('currency', 'USD'), ('sec_type', 'FUT'), ('market', 'SG'), ('symbol', 'CN'),
     ('multiplier', 1.0), ('action', 'BUY'), ('filled_quantity', 1.0), ('filled_price', 12309.0),
     ('order_id', 28819544031364096), ('transact_time', 1668774872538), ('create_time', 1668774872946),
      ('update_time', 1668774872946), ('identifier', 'CN2212'), ('timestamp', 1668774873002), ('segment', 'C')]
    """
    print(f'account:{account}, items: {items}')

def on_asset_changed(account, items):
    """

    :param account:
    :param items:
    :return:
    items 数据示例:
        [('equity_with_loan', 721583.83), ('gross_position_value', 1339641.94),
        ('excess_liquidity', 378624.18), ('available_funds', 320059.1), ('initial_margin_requirement', 497419.25),
        ('buying_power', 2293551.51), ('cash', 950059.0), ('segment', 'summary'), ('net_liquidation', 817685.72),
        ('maintenance_margin_requirement', 439061.54)]
    """
    print(account, items)


def on_position_changed(account, items):
    """

    :param account:
    :param items:
    :return:
    items 数据示例:
        [('symbol', 'ABCD'), ('market_price', 3.68525), ('market_value', 0.0), ('sec_type', 'STK'),
        ('segment', 'summary'), ('currency', 'USD'), ('quantity', 0.0), ('average_cost', 3.884548)]
    """
    print(account, items)


def subscribe_callback(destination, content):
    """
    订阅成功与否的回调
    :param destination: 订阅的类型. 有 quote, trade/asset, trade/position, trade/order
    :param content: 回调信息. 如成功 {'code': 0, 'message': 'success'}; 若失败则 code 不为0, message 为错误详情
    """
    print('subscribe:{}, callback content:{}'.format(destination, content))


def unsubscribe_callback(destination, content):
    """
    退订成功与否的回调
    :param destination: 取消订阅的类型. 有 quote, trade/asset, trade/position, trade/order
    :param content: 回调信息.
    """
    print('subscribe:{}, callback content:{}'.format(destination, content))


def error_callback(frame):
    """错误回调"""
    print(frame)


def connect_callback(frame):
    """连接建立回调"""
    print('connected')


def disconnect_callback():
    """连接断开回调. 此处利用回调进行重连"""
    for t in range(1, 200):
        try:
            print('disconnected, reconnecting')
            push_client.connect(client_config.tiger_id, client_config.private_key)
        except:
            print('connect failed, retry')
            time.sleep(t)
        else:
            print('reconnect success')
            return
    print('reconnect failed, please check your network')


if __name__ == '__main__':
    client_config = get_client_config()
    protocol, host, port = client_config.socket_host_port
    push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))

    # 行情变动回调
    push_client.quote_changed = on_quote_changed
    # 逐笔数据回调
    push_client.tick_changed = on_tick_changed
    # 已订阅 symbol 查询回调
    push_client.query_subscribed_callback = query_subscribed_callback
    # 已订阅 symbol 查询回调(已废弃)
    # push_client.subscribed_symbols = on_query_subscribed_quote
    # 订单变动回调
    push_client.order_changed = on_order_changed
    # 订单执行明细回调
    push_client.transaction_changed = on_transaction_changed
    # 资产变动回调
    push_client.asset_changed = on_asset_changed
    # 持仓变动回调
    push_client.position_changed = on_position_changed

    # 订阅成功与否的回调
    push_client.subscribe_callback = subscribe_callback
    # 退订成功与否的回调
    push_client.unsubscribe_callback = unsubscribe_callback

    # 错误信息回调
    push_client.error_callback = error_callback

    # 建立推送连接
    push_client.connect(client_config.tiger_id, client_config.private_key)
    # 断线重连回调
    push_client.disconnect_callback = disconnect_callback

    # 订阅行情
    push_client.subscribe_quote(['AAPL', 'GOOG'])
    # 可以指定关注的行情key的类型, QuoteKeyType.TRADE 为成交数据, QuoteKeyType.QUOTE 为盘口数据
    # push_client.subscribe_quote(['MSFT', 'AMD'], quote_key_type=QuoteKeyType.TRADE)

    # 订阅深度行情
    push_client.subscribe_depth_quote(['AMD', 'BABA'])

    # 订阅逐笔数据
    push_client.subscribe_tick(['AMD', 'QQQ'])
    push_client.subscribe_tick(['HSImain'])

    # 订阅资产变动
    push_client.subscribe_asset()
    # 订阅订单变动
    push_client.subscribe_order()
    # 订阅订单执行明细
    push_client.subscribe_transaction()
    # 订阅持仓变动
    push_client.subscribe_position()
    # 查询已订阅的 symbol
    push_client.query_subscribed_quote()

    time.sleep(600)
    push_client.disconnect()
