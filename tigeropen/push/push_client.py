# -*- coding: utf-8 -*-
"""
Created on 2018/10/30

@author: gaoan
"""
import json
import logging
import sys
from collections import defaultdict
from itertools import accumulate, zip_longest

import stomp
from stomp.exception import ConnectFailedException

from tigeropen import __VERSION__
from tigeropen.common.consts import OrderStatus
from tigeropen.common.consts.params import P_SDK_VERSION, P_SDK_VERSION_PREFIX
from tigeropen.common.consts.push_destinations import QUOTE, QUOTE_DEPTH, QUOTE_FUTURE, QUOTE_OPTION, TRADE_ASSET, \
    TRADE_ORDER, TRADE_POSITION, TRADE_TICK, TRADE_TRANSACTION
from tigeropen.common.consts.push_subscriptions import SUBSCRIPTION_QUOTE, SUBSCRIPTION_QUOTE_DEPTH, \
    SUBSCRIPTION_QUOTE_OPTION, SUBSCRIPTION_QUOTE_FUTURE, SUBSCRIPTION_TRADE_ASSET, SUBSCRIPTION_TRADE_POSITION, \
    SUBSCRIPTION_TRADE_ORDER, SUBSCRIPTION_TRADE_TICK, SUBSCRIPTION_TRADE_TRANSACTION
from tigeropen.common.consts.push_types import RequestType, ResponseType
from tigeropen.common.consts.quote_keys import QuoteChangeKey, QuoteKeyType
from tigeropen.common.exceptions import ApiException
from tigeropen.common.util.common_utils import get_enum_value
from tigeropen.common.util.order_utils import get_order_status
from tigeropen.common.util.signature_utils import sign_with_rsa
from tigeropen.common.util.string_utils import camel_to_underline, camel_to_underline_obj
from tigeropen.common.util.tick_util import get_part_code, get_part_code_name, get_trade_condition_map, \
    get_trade_condition
from tigeropen.push import _patch_ssl

HOUR_TRADING_QUOTE_KEYS_MAPPINGS = {'hourTradingLatestPrice': 'latest_price', 'hourTradingPreClose': 'pre_close',
                                    'hourTradingLatestTime': 'latest_time', 'hourTradingVolume': 'volume',
                                    }
QUOTE_KEYS_MAPPINGS = {field.value: field.name for field in QuoteChangeKey}  # like {'askPrice': 'ask_price'}
QUOTE_KEYS_MAPPINGS.update(HOUR_TRADING_QUOTE_KEYS_MAPPINGS)
PRICE_FIELDS = {'open', 'high', 'low', 'close', 'prev_close', 'ask_price', 'bid_price', 'latest_price'}

ASSET_KEYS_MAPPINGS = {'buyingPower': 'buying_power', 'cashBalance': 'cash',
                       'grossPositionValue': 'gross_position_value',
                       'netLiquidation': 'net_liquidation', 'equityWithLoan': 'equity_with_loan',
                       'initMarginReq': 'initial_margin_requirement',
                       'maintMarginReq': 'maintenance_margin_requirement',
                       'availableFunds': 'available_funds', 'excessLiquidity': 'excess_liquidity',
                       'dayTradesRemaining': 'day_trades_remaining', 'currency': 'currency', 'segment': 'segment'}

POSITION_KEYS_MAPPINGS = {'averageCost': 'average_cost', 'position': 'quantity', 'latestPrice': 'market_price',
                          'marketValue': 'market_value', 'orderType': 'order_type', 'realizedPnl': 'realized_pnl',
                          'unrealizedPnl': 'unrealized_pnl', 'secType': 'sec_type', 'localSymbol': 'local_symbol',
                          'originSymbol': 'origin_symbol', 'contractId': 'contract_id', 'symbol': 'symbol',
                          'currency': 'currency', 'strike': 'strike', 'expiry': 'expiry', 'right': 'right',
                          'segment': 'segment', 'identifier': 'identifier'}

ORDER_KEYS_MAPPINGS = {'parentId': 'parent_id', 'orderId': 'order_id', 'orderType': 'order_type',
                       'limitPrice': 'limit_price', 'auxPrice': 'aux_price', 'avgFillPrice': 'avg_fill_price',
                       'totalQuantity': 'quantity', 'filledQuantity': 'filled', 'lastFillPrice': 'last_fill_price',
                       'realizedPnl': 'realized_pnl', 'secType': 'sec_type', 'symbol': 'symbol',
                       'remark': 'reason', 'localSymbol': 'local_symbol', 'originSymbol': 'origin_symbol',
                       'outsideRth': 'outside_rth', 'timeInForce': 'time_in_force', 'openTime': 'order_time',
                       'latestTime': 'trade_time', 'contractId': 'contract_id', 'trailStopPrice': 'trail_stop_price',
                       'trailingPercent': 'trailing_percent', 'percentOffset': 'percent_offset', 'action': 'action',
                       'status': 'status', 'currency': 'currency', 'remaining': 'remaining', 'id': 'id',
                       'segment': 'segment', 'identifier': 'identifier', 'replaceStatus': 'replace_status',
                       'updateTime': 'update_time'}

if sys.platform == 'linux' or sys.platform == 'linux2':
    KEEPALIVE = True
else:
    KEEPALIVE = False


class PushClient(stomp.ConnectionListener):
    def __init__(self, host, port, use_ssl=True, connection_timeout=120, heartbeats=(30 * 1000, 30 * 1000)):
        """
        :param host:
        :param port:
        :param use_ssl:
        :param connection_timeout: unit: second. The timeout value should be greater the heartbeats interval
        :param heartbeats: tuple of millisecond
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self._tiger_id = None
        self._private_key = None
        self._sign = None
        self._stomp_connection = None
        self._destination_counter_map = defaultdict(lambda: 0)

        self.subscribed_symbols = None
        self.query_subscribed_callback = None
        self.quote_changed = None
        self.tick_changed = None
        self.asset_changed = None
        self.position_changed = None
        self.order_changed = None
        self.transaction_changed = None
        self.connect_callback = None
        self.disconnect_callback = None
        self.subscribe_callback = None
        self.unsubscribe_callback = None
        self.error_callback = None
        self._connection_timeout = connection_timeout
        self._heartbeats = heartbeats
        self.logger = logging.getLogger('tiger_openapi')
        _patch_ssl()

    def _connect(self):
        try:
            if self._stomp_connection:
                self._stomp_connection.remove_listener('push')
                self._stomp_connection.transport.cleanup()
        except:
            pass

        self._stomp_connection = stomp.Connection12(host_and_ports=[(self.host, self.port)],
                                                    keepalive=KEEPALIVE, timeout=self._connection_timeout,
                                                    heartbeats=self._heartbeats, reconnect_attempts_max=60)
        self._stomp_connection.set_listener('push', self)
        try:
            if self.use_ssl:
                self._stomp_connection.set_ssl([(self.host, self.port)])
            self._stomp_connection.connect(self._tiger_id, self._sign, wait=True, headers=self._generate_headers())
        except ConnectFailedException as e:
            raise e

    def connect(self, tiger_id, private_key):
        self._tiger_id = tiger_id
        self._private_key = private_key
        self._sign = sign_with_rsa(self._private_key, self._tiger_id, 'utf-8')
        self._connect()

    def disconnect(self):
        if self._stomp_connection:
            self._stomp_connection.disconnect()

    def on_connected(self, frame):
        if self.connect_callback:
            self.connect_callback(frame)

    def on_disconnected(self):
        if self.disconnect_callback:
            self.disconnect_callback()
        else:
            self._connect()

    def on_message(self, frame):
        """
        Called by the STOMP connection when a MESSAGE frame is received.

        :param Frame frame: the stomp frame. stomp.utils.Frame
            A STOMP frame's attributes:
                cmd: the protocol command
                headers: a map of headers for the frame
                body: the content of the frame.
        """
        headers = frame.headers
        body = frame.body
        try:
            response_type = headers.get('ret-type')
            if response_type == str(ResponseType.GET_SUB_SYMBOLS_END.value):
                if self.subscribed_symbols or self.query_subscribed_callback:
                    data = json.loads(body)
                    formatted_data = camel_to_underline_obj(data)

                    limit = formatted_data.get('limit')
                    subscribed_symbols = formatted_data.get('subscribed_symbols')
                    used = formatted_data.get('used')
                    symbol_focus_keys = formatted_data.get('symbol_focus_keys')
                    focus_keys = dict()
                    for sym, keys in symbol_focus_keys.items():
                        keys = set(QUOTE_KEYS_MAPPINGS.get(key, camel_to_underline(key)) for key in keys)
                        focus_keys[sym] = list(keys)
                    formatted_data['symbol_focus_keys'] = focus_keys
                    formatted_data['subscribed_quote_depth_symbols'] = formatted_data.pop('subscribed_ask_bid_symbols')
                    formatted_data['quote_depth_limit'] = formatted_data.pop('ask_bid_limit')
                    formatted_data['quote_depth_used'] = formatted_data.pop('ask_bid_used')
                    if self.subscribed_symbols:
                        self.logger.warning('PushClient.subscribed_symbols is deprecated, '
                                            'use PushClient.query_subscribed_callback instead.')
                        self.subscribed_symbols(subscribed_symbols, focus_keys, limit, used)
                    if self.query_subscribed_callback:
                        self.query_subscribed_callback(formatted_data)

            elif response_type == str(ResponseType.GET_QUOTE_CHANGE_END.value):
                if self.quote_changed:
                    data = json.loads(body)
                    hour_trading = False
                    if 'hourTradingLatestPrice' in data:
                        hour_trading = True
                    if 'symbol' in data:
                        symbol = data.pop('symbol', None)
                        offset = data.get('offset', 0)
                        items = []
                        # 期货行情推送的价格都乘了 10 的 offset 次方变成了整数, 需要除回去变为正常单位的价格
                        if offset:
                            for key, value in data.items():
                                if key == 'latestTime' or key == 'hourTradingLatestTime':
                                    continue
                                if key in QUOTE_KEYS_MAPPINGS:
                                    key = QUOTE_KEYS_MAPPINGS.get(key)
                                    if key in PRICE_FIELDS:
                                        value /= 10 ** offset
                                    elif key == 'minute':
                                        minute_item = dict()
                                        for m_key, m_value in value.items():
                                            if m_key in {'p', 'h', 'l'}:
                                                m_value /= 10 ** offset
                                            minute_item[m_key] = m_value
                                            value = minute_item
                                    items.append((key, value))
                                else:
                                    items.append((camel_to_underline(key), value))
                        else:
                            for key, value in data.items():
                                if key == 'latestTime' or key == 'hourTradingLatestTime':
                                    continue
                                if key in QUOTE_KEYS_MAPPINGS:
                                    key = QUOTE_KEYS_MAPPINGS.get(key)
                                    items.append((key, value))
                                else:
                                    items.append((camel_to_underline(key), value))
                        if items:
                            self.quote_changed(symbol, items, hour_trading)
            elif response_type == str(ResponseType.GET_TRADING_TICK_END.value):
                if self.tick_changed:
                    symbol, items = self._convert_tick(body)
                    self.tick_changed(symbol, items)

            elif response_type == str(ResponseType.SUBSCRIBE_ASSET.value):
                if self.asset_changed:
                    data = json.loads(body)
                    if 'account' in data:
                        account = data.pop('account', None)
                        items = []
                        for key, value in data.items():
                            if key in ASSET_KEYS_MAPPINGS:
                                items.append((ASSET_KEYS_MAPPINGS.get(key), value))
                            else:
                                items.append((camel_to_underline(key), value))
                        if items:
                            self.asset_changed(account, items)
            elif response_type == str(ResponseType.SUBSCRIBE_POSITION.value):
                if self.position_changed:
                    data = json.loads(body)
                    if 'account' in data:
                        account = data.pop('account', None)
                        items = []
                        for key, value in data.items():
                            if key in POSITION_KEYS_MAPPINGS:
                                items.append((POSITION_KEYS_MAPPINGS.get(key), value))
                            else:
                                items.append((camel_to_underline(key), value))
                        if items:
                            self.position_changed(account, items)
            elif response_type == str(ResponseType.SUBSCRIBE_ORDER_STATUS.value):
                if self.order_changed:
                    data = json.loads(body)
                    if 'account' in data:
                        account = data.pop('account', None)
                        items = []
                        for key, value in data.items():
                            if key in ORDER_KEYS_MAPPINGS:
                                if key == 'status':
                                    value = get_order_status(value)
                                    # 部分成交 (服务端推送 'Submitted' 状态)
                                    if value == OrderStatus.HELD and data.get('filledQuantity'):
                                        value = OrderStatus.PARTIALLY_FILLED
                                items.append((ORDER_KEYS_MAPPINGS.get(key), value))
                            else:
                                items.append((camel_to_underline(key), value))
                        if items:
                            self.order_changed(account, items)
            elif response_type == str(ResponseType.SUBSCRIBE_TRADE_EXECUTION.value):
                data = json.loads(body)
                if self.transaction_changed:
                    if 'account' in data:
                        account = data.pop('account', None)
                        items = []
                        for key, value in data.items():
                            items.append((camel_to_underline(key), value))
                        if items:
                            self.transaction_changed(account, items)
            elif response_type == str(ResponseType.GET_SUBSCRIBE_END.value):
                if self.subscribe_callback:
                    self.subscribe_callback(headers.get('destination'), json.loads(body))
            elif response_type == str(ResponseType.GET_CANCEL_SUBSCRIBE_END.value):
                if self.unsubscribe_callback:
                    self.unsubscribe_callback(headers.get('destination'), json.loads(body))
            elif response_type == str(ResponseType.ERROR_END.value):
                if self.error_callback:
                    self.error_callback(body)
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def on_error(self, frame):
        body = json.loads(frame.body)
        if body.get('code') == 4001:
            self.logger.error(body)
            self.disconnect_callback = None
            raise ApiException(4001, body.get('message'))

        if self.error_callback:
            self.error_callback(frame)
        else:
            self.logger.error(frame.body)

    def _update_subscribe_id(self, destination):
        self._destination_counter_map[destination] += 1

    def _get_subscribe_id(self, destination):
        return 'sub-' + str(self._destination_counter_map[destination])

    def subscribe_asset(self, account=None):
        """
        订阅账户资产更新
        :return:
        """
        return self._handle_trade_subscribe(TRADE_ASSET, SUBSCRIPTION_TRADE_ASSET, account)

    def unsubscribe_asset(self, id=None):
        """
        退订账户资产更新
        :return:
        """
        self._handle_trade_unsubscribe(TRADE_ASSET, SUBSCRIPTION_TRADE_ASSET, sub_id=id)

    def subscribe_position(self, account=None):
        """
        订阅账户持仓更新
        :return:
        """
        return self._handle_trade_subscribe(TRADE_POSITION, SUBSCRIPTION_TRADE_POSITION, account)

    def unsubscribe_position(self, id=None):
        """
        退订账户持仓更新
        :return:
        """
        self._handle_trade_unsubscribe(TRADE_POSITION, SUBSCRIPTION_TRADE_POSITION, sub_id=id)

    def subscribe_order(self, account=None):
        """
        订阅账户订单更新
        :return:
        """
        return self._handle_trade_subscribe(TRADE_ORDER, SUBSCRIPTION_TRADE_ORDER, account)

    def unsubscribe_order(self, id=None):
        """
        退订账户订单更新
        :return:
        """
        self._handle_trade_unsubscribe(TRADE_ORDER, SUBSCRIPTION_TRADE_ORDER, sub_id=id)

    def subscribe_transaction(self, account=None):
        """
        订阅订单执行明细
        :return:
        """
        return self._handle_trade_subscribe(TRADE_TRANSACTION, SUBSCRIPTION_TRADE_TRANSACTION, account)

    def unsubscribe_transaction(self, id=None):
        """
        退订订单执行明细
        :return:
        """
        self._handle_trade_unsubscribe(TRADE_TRANSACTION, SUBSCRIPTION_TRADE_TRANSACTION, sub_id=id)

    def subscribe_quote(self, symbols, quote_key_type=QuoteKeyType.TRADE, focus_keys=None):
        """
        订阅行情更新
        :param symbols:
        :param quote_key_type: 行情类型, 值为 common.consts.quote_keys.QuoteKeyType 枚举类型
        :param focus_keys: 行情 key, common.consts.quote_keys.QuoteChangeKey 枚举类型的列表
        :return:
        """
        extra_headers = dict()
        if focus_keys:
            if isinstance(focus_keys, list):
                keys = list()
                for key in focus_keys:
                    keys.append(get_enum_value(key))
                extra_headers['keys'] = ','.join(keys)
            else:
                extra_headers['keys'] = focus_keys
        elif quote_key_type:
            extra_headers['keys'] = get_enum_value(quote_key_type)
        return self._handle_quote_subscribe(destination=QUOTE, subscription=SUBSCRIPTION_QUOTE, symbols=symbols,
                                            extra_headers=extra_headers)

    def subscribe_tick(self, symbols):
        """
        subscribe trade tick
        :param symbols: symbol列表
        :return:
        """
        return self._handle_quote_subscribe(destination=TRADE_TICK, subscription=SUBSCRIPTION_TRADE_TICK,
                                            symbols=symbols)

    def subscribe_depth_quote(self, symbols):
        """
        订阅深度行情
        :param symbols: symbol列表
        :return:
        """
        return self._handle_quote_subscribe(destination=QUOTE_DEPTH, subscription=SUBSCRIPTION_QUOTE_DEPTH, symbols=symbols)

    def subscribe_option(self, symbols):
        """
        订阅期权行情
        :param symbols: symbol列表
        :return:
        """
        return self._handle_quote_subscribe(destination=QUOTE_OPTION, subscription=SUBSCRIPTION_QUOTE_OPTION, symbols=symbols)

    def subscribe_future(self, symbols):
        """
        订阅期货行情
        :param symbols: symbol列表
        :return:
        """
        return self._handle_quote_subscribe(destination=QUOTE_FUTURE, subscription=SUBSCRIPTION_QUOTE_FUTURE, symbols=symbols)

    def query_subscribed_quote(self):
        """
        查询已订阅行情的合约
        :return:
        """
        headers = self._generate_headers()
        headers['destination'] = QUOTE
        headers['req-type'] = RequestType.REQ_SUB_SYMBOLS.value
        self._stomp_connection.send(QUOTE, "{}", headers=headers)

    def unsubscribe_quote(self, symbols=None, id=None):
        """
        退订行情更新
        :return:
        """
        self._handle_quote_unsubscribe(destination=QUOTE, subscription=SUBSCRIPTION_QUOTE, sub_id=id, symbols=symbols)

    def unsubscribe_tick(self, symbols=None, id=None):
        """
        退订行情更新
        :return:
        """
        self._handle_quote_unsubscribe(destination=TRADE_TICK, subscription=SUBSCRIPTION_TRADE_TICK, sub_id=id,
                                       symbols=symbols)

    def unsubscribe_depth_quote(self, symbols=None, id=None):
        """
        退订深度行情更新
        :return:
        """
        self._handle_quote_unsubscribe(destination=QUOTE_DEPTH, subscription=SUBSCRIPTION_QUOTE_DEPTH, sub_id=id, symbols=symbols)

    def _handle_trade_subscribe(self, destination, subscription, account=None, extra_headers=None):
        if extra_headers is None:
            extra_headers = dict()
        if account is not None:
            extra_headers['account'] = account
        return self._handle_subscribe(destination=destination, subscription=subscription, extra_headers=extra_headers)

    def _handle_quote_subscribe(self, destination, subscription, symbols=None, extra_headers=None):
        if extra_headers is None:
            extra_headers = dict()
        if symbols is not None:
            extra_headers['symbols'] = ','.join(symbols)
        return self._handle_subscribe(destination=destination, subscription=subscription, extra_headers=extra_headers)

    def _handle_trade_unsubscribe(self, destination, subscription, sub_id=None):
        self._handle_unsubscribe(destination=destination, subscription=subscription, sub_id=sub_id)

    def _handle_quote_unsubscribe(self, destination, subscription, sub_id=None, symbols=None):
        extra_headers = dict()
        if symbols is not None:
            extra_headers['symbols'] = ','.join(symbols)
        self._handle_unsubscribe(destination=destination, subscription=subscription, sub_id=sub_id,
                                 extra_headers=extra_headers)

    def _handle_subscribe(self, destination, subscription, extra_headers=None):
        headers = self._generate_headers(extra_headers)
        headers['destination'] = destination
        headers['subscription'] = subscription
        self._update_subscribe_id(destination)
        sub_id = self._get_subscribe_id(destination)
        headers['id'] = sub_id

        self._stomp_connection.subscribe(destination, id=sub_id, headers=headers)
        return sub_id

    def _handle_unsubscribe(self, destination, subscription, sub_id=None, extra_headers=None):
        headers = self._generate_headers(extra_headers)
        headers['destination'] = destination
        headers['subscription'] = subscription
        id_ = sub_id if sub_id is not None else self._get_subscribe_id(destination)
        headers['id'] = id_

        self._stomp_connection.unsubscribe(id=id_, headers=headers)

    def _generate_headers(self, extra_headers=None):
        headers = {P_SDK_VERSION: P_SDK_VERSION_PREFIX + __VERSION__}
        if extra_headers is not None:
            headers.update(extra_headers)
        return headers

    def _convert_tick(self, tick):
        data = json.loads(tick)
        symbol = data.pop('symbol')
        data = camel_to_underline_obj(data)
        price_offset = 10 ** data.pop('price_offset')
        price_base = float(data.pop('price_base'))
        data['timestamp'] = int(data.get('timestamp'))
        prices = data.pop('prices') if 'prices' in data else data.pop('price')
        # The latter time is equal to the sum of all previous values
        price_items = [('price', (float(item) + price_base) / price_offset) for item in prices]
        times = [int(i) for i in (data.pop('times') if 'times' in data else data.pop('time'))]
        time_items = [('time', item) for item in accumulate(times)]
        volumes = data.pop('volumes') if 'volumes' in data else data.pop('volume')
        volume_items = [('volume', int(item)) for item in volumes]
        tick_types = data.pop('tick_type') if 'tick_type' in data else data.pop('type')
        if tick_types:
            tick_type_items = [('tick_type', item) for item in tick_types]
        else:
            tick_type_items = [('tick_type', None) for _ in range(len(time_items))]
        part_codes = data.pop('part_code') if 'part_code' in data else None
        if part_codes:
            part_code_items = [('part_code', get_part_code(item)) for item in part_codes]
            part_code_name_items = [('part_code_name', get_part_code_name(item)) for item in part_codes]
        else:
            part_code_items = [('part_code', None) for _ in range(len(time_items))]
            part_code_name_items = [('part_code_name', None) for _ in range(len(time_items))]
        conds = data.pop('cond') if 'cond' in data else None
        cond_map = get_trade_condition_map(data.get('quote_level'))
        if conds:
            cond_items = [('cond', get_trade_condition(item, cond_map)) for item in conds]
        else:
            cond_items = [('cond', None) for _ in range(len(time_items))]
        sn = int(data.pop('sn'))
        sn_list = [('sn', sn + i) for i in range(len(time_items))]
        merged_vols = data.pop('merged_vols') if 'merged_vols' in data else None
        if merged_vols:
            merged_vols_items = [('merged_vols', item) for item in merged_vols]
        else:
            merged_vols_items = [('merged_vols', None) for _ in range(len(time_items))]
        tick_data = zip_longest(tick_type_items, price_items, volume_items, part_code_items,
                                part_code_name_items, cond_items, time_items, sn_list, merged_vols_items)
        items = []
        for item in tick_data:
            try:
                item_dict = dict(item)
            except:
                self.logger.error('convert tick error')
                continue
            item_dict.update(data)
            if item_dict.get('merged_vols'):
                vols = item_dict.pop('merged_vols').get('vols')
                for i, vol in enumerate(vols):
                    sub_item = dict(item_dict)
                    sub_item['sn'] = sub_item['sn'] * 10 + i
                    sub_item['volume'] = vol
                    items.append(sub_item)
            else:
                item_dict.pop('merged_vols', None)
                items.append(item_dict)
        return symbol, items

