# -*- coding: utf-8 -*-
"""
Created on 2018/10/30

@author: gaoan
"""
import time
# from tigeropen.common.consts import QuoteKeyType
import pandas as pd

from tigeropen.common.consts import StockRankingIndicator, OptionRankingIndicator
from tigeropen.push.pb.AssetData_pb2 import AssetData
from tigeropen.push.pb.KlineData_pb2 import KlineData
from tigeropen.push.pb.OptionTopData_pb2 import OptionTopData
from tigeropen.push.pb.OrderStatusData_pb2 import OrderStatusData
from tigeropen.push.pb.OrderTransactionData_pb2 import OrderTransactionData
from tigeropen.push.pb.PositionData_pb2 import PositionData
from tigeropen.push.pb.QuoteBBOData_pb2 import QuoteBBOData
from tigeropen.push.pb.QuoteBasicData_pb2 import QuoteBasicData
from tigeropen.push.pb.QuoteDepthData_pb2 import QuoteDepthData
from tigeropen.push.pb.StockTopData_pb2 import StockTopData
from tigeropen.push.pb.TradeTickData_pb2 import TradeTickData
from tigeropen.push.pb.trade_tick import TradeTick
from tigeropen.common.consts import OrderStatus
from tigeropen.push.push_client import PushClient
from tigeropen.examples.client_config import get_client_config


def query_subscribed_callback(data):
    """
    data example:
        {'subscribed_symbols': ['QQQ'], 'limit': 1200, 'used': 1, 'symbol_focus_keys': {'qqq': ['open', 'prev_close', 'low', 'volume', 'latest_price', 'close', 'high']},
         'subscribed_quote_depth_symbols': ['NVDA'], 'quote_depth_limit': 20, 'quote_depth_used': 1,
         'subscribed_trade_tick_symbols': ['QQQ', 'AMD', '00700'], 'trade_tick_limit': 1200, 'trade_tick_used': 3,
         'kline_limit': 1200, 'kline_used': 0}
    """
    print(f'subscribed data:{data}')
    print(f'subscribed symbols:{data["subscribed_symbols"]}')


def on_quote_changed(frame: QuoteBasicData):
    """
    行情基本数据回调
    example:
    symbol: "00700"
    type: BASIC
    timestamp: 1677742483530
    serverTimestamp: 1677742483586
    avgPrice: 365.37
    latestPrice: 363.8
    latestPriceTimestamp: 1677742483369
    latestTime: "03-02 15:34:43"
    preClose: 368.8
    volume: 12674730
    amount: 4630947968
    open: 368.2
    high: 369
    low: 362.4
    marketStatus: "交易中"
    mi {
      p: 363.8
      a: 365.37
      t: 1677742440000
      v: 27300
      h: 364
      l: 363.6
    }
    """
    print(frame)


def on_quote_bbo_changed(frame: QuoteBBOData):
    """行情最优报价，ask/bid
    example:
    symbol: "01810"
    type: BBO
    timestamp: 1677741267291
    serverTimestamp: 1677741267329
    askPrice: 12.54
    askSize: 397600
    askTimestamp: 1677741266304
    bidPrice: 12.52
    bidSize: 787400
    bidTimestamp: 1677741266916
    """
    print(f'quote bbo changed: {frame}')


def on_quote_depth_changed(frame: QuoteDepthData):
    """深度行情回调
    example:
    symbol: "00700"
    timestamp: 1677742734822
    ask {
      price: 363.8
      price: 364
      price: 364.2
      price: 364.4
      price: 364.6
      price: 364.8
      price: 365
      price: 365.2
      price: 365.4
      price: 365.6
      volume: 26900
      volume: 14800
      volume: 15200
      volume: 31500
      volume: 15800
      volume: 7700
      volume: 29400
      volume: 6300
      volume: 6000
      volume: 5500
      orderCount: 27
      orderCount: 20
      orderCount: 19
      orderCount: 22
      orderCount: 14
      orderCount: 10
      orderCount: 20
      orderCount: 12
      orderCount: 10
      orderCount: 11
    }
    bid {
      price: 363.6
      price: 363.4
      price: 363.2
      price: 363
      price: 362.8
      price: 362.6
      price: 362.4
      price: 362.2
      price: 362
      price: 361.8
      volume: 9400
      volume: 19900
      volume: 35300
      volume: 74200
      volume: 26300
      volume: 16700
      volume: 22500
      volume: 21100
      volume: 40500
      volume: 5600
      orderCount: 16
      orderCount: 23
      orderCount: 36
      orderCount: 79
      orderCount: 30
      orderCount: 32
      orderCount: 31
      orderCount: 34
      orderCount: 143
      orderCount: 26
    }
    """
    print(f'quote depth changed: {frame}')


def on_tick_changed(frame: TradeTick):
    """逐笔成交回调
    example:
    TradeTick<{'symbol': '00700', 'sec_type': 'STK', 'quote_level': 'hkStockQuoteLv2', 'timestamp': 1685602618145, 'ticks': [TradeTickItem<{'tick_type': '+', 'price': 316.6, 'volume': 100, 'part_code': None, 'part_code_name': None, 'cond': None, 'time': 1685602617046, 'sn': 42055}>, TradeTickItem<{'tick_type': '-', 'price': 316.4, 'volume': 600, 'part_code': None, 'part_code_name': None, 'cond': None, 'time': 1685602617639, 'sn': 42056}>, TradeTickItem<{'tick_type': '-', 'price': 316.4, 'volume': 200, 'part_code': None, 'part_code_name': None, 'cond': None, 'time': 1685602617639, 'sn': 42057}>]}>
    TradeTick<{'symbol': 'CLmain', 'sec_type': 'FUT', 'quote_level': '', 'timestamp': 1685602618153, 'ticks': [TradeTickItem<{'tick_type': None, 'price': 68.7, 'volume': 1, 'part_code': None, 'part_code_name': None, 'cond': None, 'time': 1685602616000, 'sn': 109150}>, TradeTickItem<{'tick_type': None, 'price': 68.7, 'volume': 1, 'part_code': None, 'part_code_name': None, 'cond': None, 'time': 1685602616000, 'sn': 109151}>]}>
    """
    print(frame)


def on_stock_top_changed(frame: StockTopData):
    print(f'stock top changed: {frame}')


def on_option_top_changed(frame: OptionTopData):
    print(f'option top changed: {frame}')


def on_kline_changed(frame: KlineData):
    print(frame)


def on_order_changed(frame: OrderStatusData):
    """订单回调
    {"id":"28875370355884032","account":"736845","symbol":"CL","identifier":"CL2312","multiplier":1000,
    "action":"BUY","market":"US","currency":"USD","segment":"C","secType":"FUT","orderType":"LMT",
    "isLong":true,"totalQuantity":"1","filledQuantity":"1","avgFillPrice":77.76,"limitPrice":77.76,
    "status":"Filled","outsideRth":true,"name":"WTI原油2312","source":"android","commissionAndFee":4.0,
    "openTime":"1669200792000","timestamp":"1669200782221"}

    """
    print(f'order changed: {frame}')
    # 忽略部分成交、初始状态、已提交状态的订单
    if frame.status in [OrderStatus.PARTIALLY_FILLED, OrderStatus.PENDING_NEW, OrderStatus.NEW, OrderStatus.HELD]:
        print(f'ignore order status {frame.status}, frame: {frame}')
    # 处理完全成交的订单
    elif frame.status in [OrderStatus.FILLED]:
        print(f'order filled, frame: {frame}')
        # 其他逻辑 todo
    # 其他，如已取消/被拒绝的订单
    else:
        print(f'order status {frame.status}, frame: {frame}')


def on_transaction_changed(frame: OrderTransactionData):
    """订单执行明细回调
    id: 2999543887211111111
    orderId: 29995438111111111
    account: "1111111"
    symbol: "ZC"
    identifier: "ZC2305"
    multiplier: 5000
    action: "BUY"
    market: "US"
    currency: "USD"
    segType: "C"
    secType: "FUT"
    filledPrice: 6.385
    filledQuantity: 1
    createTime: 1677746237303
    updateTime: 1677746237303
    transactTime: 1677746237289
    timestamp: 1677746237313
    """
    print(f'transaction changed: {frame}')


def on_asset_changed(frame: AssetData):
    """可进行自定义处理，此处仅打印
    account: "111111"
    currency: "USD"
    segType: "S"
    availableFunds: 1593.1191893
    excessLiquidity: 1730.5666908
    netLiquidation: 2856.1016998
    equityWithLoan: 2858.1016998
    buyingPower: 6372.4767571
    cashBalance: 484.1516697
    grossPositionValue: 2373.95003
    initMarginReq: 1264.9825105
    maintMarginReq: 1127.535009
    timestamp: 1677745420121
    """
    print(f'asset change. {frame}')
    # 查看可用资金
    print(frame.availableFunds)
    # 查看持仓市值
    print(frame.grossPositionValue)


def on_position_changed(frame: PositionData):
    """持仓回调
    account: "111111"
    symbol: "BILI"
    identifier: "BILI"
    multiplier: 1
    market: "US"
    currency: "USD"
    segType: "S"
    secType: "STK"
    position: 100
    averageCost: 80
    latestPrice: 19.83
    marketValue: 1983
    unrealizedPnl: -6017
    timestamp: 1677745420121
    """
    print(f'position change. {frame}')
    # 持仓标的
    print(frame.symbol)
    # 持仓成本
    print(frame.averageCost)


def subscribe_callback(frame):
    """
    订阅成功与否的回调
    id: 2
    code: 112
    msg: "{\"code\":0,\"message\":\"success\"}"
    body {
      dataType: OrderStatus
    }
    """
    print(f'subscribe callback:{frame}')


def unsubscribe_callback(frame):
    """
    取消订阅成功与否的回调
    """
    print(f'unsubscribe callback:{frame}')


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
    push_client.quote_depth_changed = on_quote_depth_changed
    push_client.quote_bbo_changed = on_quote_bbo_changed
    # 逐笔数据回调
    push_client.tick_changed = on_tick_changed
    # 已订阅 symbol 查询回调
    push_client.query_subscribed_callback = query_subscribed_callback

    # 订单变动回调
    push_client.order_changed = on_order_changed
    # 订单执行明细回调
    push_client.transaction_changed = on_transaction_changed
    # 资产变动回调
    push_client.asset_changed = on_asset_changed
    # 持仓变动回调
    push_client.position_changed = on_position_changed

    # 股票榜单回调
    push_client.stock_top_changed = on_stock_top_changed
    # 期权榜单回调
    push_client.option_top_changed = on_option_top_changed
    # k线变动回调
    push_client.kline_changed = on_kline_changed

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

    # 订阅股票榜单数据
    push_client.subscribe_stock_top("HK", [StockRankingIndicator.Amount, StockRankingIndicator.ChangeRate])
    # 订阅期权榜单数据
    push_client.subscribe_option_top("US", [OptionRankingIndicator.Amount])

    # 订阅k线数据
    push_client.subscribe_kline(["AAPL", "GOOG"])

    time.sleep(600)
    push_client.disconnect()
