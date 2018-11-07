# -*- coding: utf-8 -*-
"""
Created on 2018/10/30

@author: gaoan
"""
import json
import stomp
import six
import traceback
from tigeropen.common.util.signature_utils import sign_with_rsa
from tigeropen.common.consts.push_types import RequestType, ResponseType

QUOTE_KEYS_MAPPINGS = {'latestTime': 'latest_time', 'latestPrice': 'latest_price', 'LatestPrice': 'latest_price',
                       'preClose': 'prev_close', 'PreClose': 'prev_close', 'volume': 'volume', 'Volume': 'volume',
                       'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'askPrice': 'ask_price',
                       'askSize': 'ask_size', 'bidPrice': 'bid_price', 'bidSize': 'bid_size',
                       'timestamp': 'latest_time'}

ASSET_KEYS_MAPPINGS = {'buyingPower': 'buying_power', 'cashBalance': 'cash',
                       'grossPositionValue': 'gross_position_value',
                       'netLiquidation': 'net_liquidation', 'equityWithLoan': 'equity_with_loan',
                       'initMarginReq': 'initial_margin_requirement',
                       'maintMarginReq': 'maintenance_margin_requirement',
                       'availableFunds': 'available_funds', 'excessLiquidity': 'excess_liquidity',
                       'dayTradesRemaining': 'day_trades_remaining', 'currency': 'currency'}

POSITION_KEYS_MAPPINGS = {'averageCost': 'average_cost', 'position': 'quantity', 'latestPrice': 'market_price',
                          'marketValue': 'market_value', 'orderType': 'order_type', 'realizedPnl': 'realized_pnl',
                          'unrealizedPnl': 'unrealized_pnl', 'secType': 'sec_type', 'localSymbol': 'local_symbol',
                          'originSymbol': 'origin_symbol', 'contractId': 'contract_id'}

ORDER_KEYS_MAPPINGS = {'parentId': 'parent_id', 'orderId': 'order_id', 'orderType': 'order_type',
                       'limitPrice': 'limit_price', 'auxPrice': 'aux_price', 'avgFillPrice': 'avg_fill_price',
                       'totalQuantity': 'quantity', 'filledQuantity': 'filled', 'lastFillPrice': 'last_fill_price',
                       'orderType': 'order_type', 'realizedPnl': 'realized_pnl', 'secType': 'sec_type',
                       'remark': 'reason', 'localSymbol': 'local_symbol', 'originSymbol': 'origin_symbol',
                       'outsideRth': 'outside_rth', 'timeInForce': 'time_in_force', 'openTime': 'order_time',
                       'latestTime': 'trade_time', 'contractId': 'contract_id', 'trailStopPrice': 'trail_stop_price',
                       'trailingPercent': 'trailing_percent', 'percentOffset': 'percent_offset'}


class PushClient(object):
    def __init__(self, host, port, use_ssl=True):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.stomp_connection = None
        self.counter = 0
        self.subscriptions = {}  # subscription callbacks indexed by subscriber's ID

        self.subscribed_symbols = None
        self.quote_changed = None
        self.asset_changed = None
        self.position_changed = None
        self.order_changed = None
        self.connect_callback = None
        self.disconnect_callback = None
        self.error_callback = None

    def connect(self, tiger_id, private_key):
        sign = sign_with_rsa(private_key, tiger_id, 'utf-8')
        self.stomp_connection = stomp.Connection10(host_and_ports=[(self.host, self.port), ], use_ssl=self.use_ssl,
                                                   keepalive=True)
        # self.stomp_connection.set_listener('stats', stomp.StatsListener())
        self.stomp_connection.set_listener('push', self)
        self.stomp_connection.start()
        self.stomp_connection.connect(tiger_id, sign, wait=True)

    def disconnect(self):
        if self.stomp_connection:
            self.stomp_connection.disconnect()

    def on_connected(self, headers, body):
        if self.connect_callback:
            self.connect_callback()

    def on_disconnected(self):
        if self.disconnect_callback:
            self.disconnect_callback()

    def on_message(self, headers, body):
        """
        Called by the STOMP connection when a MESSAGE frame is received.

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload - the message body.
        """
        try:
            response_type = headers.get('ret-type')
            if response_type == str(ResponseType.GET_SUB_SYMBOLS_END.value):
                if self.subscribed_symbols:
                    data = json.loads(body)
                    limit = data.get('limit')
                    symbols = data.get('subscribedSymbols')
                    focus_keys = data.get('symbolFocusKeys')
                    used = data.get('used')
                    self.subscribed_symbols(symbols, focus_keys, limit, used)
            elif response_type == str(ResponseType.GET_QUOTE_CHANGE_END.value):
                if self.quote_changed:
                    data = json.loads(body)
                    hour_trading = False
                    if 'hourTradingLatestPrice' in data:
                        hour_trading = True
                    if 'symbol' in data:
                        symbol = data.get('symbol')
                        items = []
                        for key, value in data.items():
                            if key.startswith('hourTrading'):
                                key = key[11:]
                            if key == 'latestTime' and isinstance(value, six.string_types):
                                continue
                            if key in QUOTE_KEYS_MAPPINGS:
                                items.append((QUOTE_KEYS_MAPPINGS.get(key), value))
                        if items:
                            self.quote_changed(symbol, items, hour_trading)
            elif response_type == str(ResponseType.SUBSCRIBE_ASSET.value):
                if self.asset_changed:
                    data = json.loads(body)
                    if 'account' in data:
                        account = data.get('account')
                        items = []
                        for key, value in data.items():
                            if key in ASSET_KEYS_MAPPINGS:
                                items.append((ASSET_KEYS_MAPPINGS.get(key), value))
                        if items:
                            self.asset_changed(account, items)
            elif response_type == str(ResponseType.SUBSCRIBE_POSITION.value):
                if self.position_changed:
                    data = json.loads(body)
                    if 'account' in data:
                        account = data.get('account')
                        items = []
                        for key, value in data.items():
                            if key in POSITION_KEYS_MAPPINGS:
                                items.append((POSITION_KEYS_MAPPINGS.get(key), value))
                        if items:
                            self.position_changed(account, items)
            elif response_type == str(ResponseType.SUBSCRIBE_ORDER_STATUS.value):
                if self.order_changed:
                    data = json.loads(body)
                    if 'account' in data:
                        account = data.get('account')
                        items = []
                        for key, value in data.items():
                            if key in ORDER_KEYS_MAPPINGS:
                                items.append((ORDER_KEYS_MAPPINGS.get(key), value))
                        if items:
                            self.order_changed(account, items)
        except Exception as e:
            print(traceback.format_exc())

    def on_error(self, headers, body):
        pass

    def subscribe_asset(self, account=None):
        """
        订阅账户资产更新
        :return:
        """
        id = "sub-" + str(self.counter)
        headers = dict()
        headers['destination'] = 'trade/asset'
        headers['subscription'] = 'Asset'
        headers['id'] = id
        self.counter += 1

        self.stomp_connection.subscribe('trade/asset', id=id, headers=headers)

        return id

    def unsubscribe_asset(self, id=None, account=None):
        """
        退订账户资产更新
        :return:
        """
        headers = dict()
        headers['destination'] = 'trade/asset'
        headers['subscription'] = 'Asset'
        if id:
            headers['id'] = id
        self.stomp_connection.subscribe('trade/asset', id=id, headers=headers)

    def subscribe_position(self, account=None):
        """
        订阅账户持仓更新
        :return:
        """
        id = "sub-" + str(self.counter)
        headers = dict()
        headers['destination'] = 'trade/position'
        headers['subscription'] = 'Position'
        headers['id'] = id
        self.counter += 1

        self.stomp_connection.subscribe('trade/position', id=id, headers=headers)

    def unsubscribe_position(self, id=None, account=None):
        """
        退订账户持仓更新
        :return:
        """
        headers = dict()
        headers['destination'] = 'trade/position'
        headers['subscription'] = 'Position'
        if id:
            headers['id'] = id

        self.stomp_connection.subscribe('trade/position', id=id, headers=headers)

    def subscribe_order(self):
        """
        订阅账户订单更新
        :return:
        """
        id = "sub-" + str(self.counter)
        headers = dict()
        headers['destination'] = 'trade/order'
        headers['subscription'] = 'OrderStatus'
        headers['id'] = id
        self.counter += 1

        self.stomp_connection.subscribe('trade/order', id=id, headers=headers)

    def unsubscribe_order(self, id=None, account=None):
        """
        退订账户订单更新
        :return:
        """
        headers = dict()
        headers['destination'] = 'trade/order'
        headers['subscription'] = 'OrderStatus'
        if id:
            headers['id'] = id

        self.stomp_connection.unsubscribe('trade/order', id=id, headers=headers)

    def subscribe_quote(self, symbols, focus_keys=None):
        """
        订阅行情更新
        :return:
        """
        id = "sub-" + str(self.counter)
        headers = dict()
        headers['destination'] = 'quote'
        headers['subscription'] = 'Quote'
        headers['id'] = id
        if symbols:
            headers['symbols'] = ','.join(symbols)
        if focus_keys:
            headers['keys'] = ','.join(focus_keys)
        self.counter += 1

        self.stomp_connection.subscribe('quote', id=id, headers=headers)

    def query_subscribed_quote(self):
        """
        查询已订阅行情的合约
        :return:
        """
        headers = dict()
        headers['destination'] = 'quote'
        headers['req-type'] = RequestType.REQ_SUB_SYMBOLS.value
        self.stomp_connection.send('quote', "{}", headers=headers)

    def unsubscribe_quote(self, id=None, symbols=None):
        """
        退订行情更新
        :return:
        """
        headers = dict()
        headers['destination'] = 'quote'
        headers['subscription'] = 'Quote'
        if id:
            headers['id'] = id
        if symbols:
            headers['symbols'] = ','.join(symbols)

        self.stomp_connection.unsubscribe('quote', id=id, headers=headers)
