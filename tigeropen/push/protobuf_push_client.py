# -*- coding: utf-8 -*-
# 
# @Date    : 2023/2/17
# @Author  : sukai
import logging
import sys
import threading
import time
from itertools import accumulate, zip_longest

from tigeropen.auth.authentication import AuthenticationType, RequestAuthContext
from tigeropen.push.thread_pool import CallbackThreadPoolExecutor
from tigeropen.common.consts.push_types import ResponseType
from tigeropen.common.util.common_utils import get_enum_value
from tigeropen.common.util.order_utils import get_order_status
from tigeropen.common.util.signature_utils import sign_with_rsa
from tigeropen.common.util.tick_util import get_part_code, get_part_code_name, get_trade_condition_map, \
    get_trade_condition
from tigeropen.push import _patch_ssl
from tigeropen.push.network.connect import PushConnection
from tigeropen.push.network.exception import ConnectFailedException
from tigeropen.push.network.listener import ConnectionListener
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
from tigeropen.push.pb.TradeTickData_pb2 import TradeTickData
from tigeropen.push.pb.trade_tick import TradeTickItem, TradeTick
from tigeropen.push.pb.util import ProtoMessageUtil, convert_to_basic_data, convert_to_bbo_data

if sys.platform == 'linux' or sys.platform == 'linux2':
    KEEPALIVE = True
else:
    KEEPALIVE = False

# How early to rotate the access token. Deliberately the same as the session manager's
# default refresh-ahead window: this check only decides whether to *ask* for a token, and
# the session manager hands back the existing one until its own window opens, so a wider
# window here would only spend the extra margin finding the token unchanged.
TOKEN_REFRESH_AHEAD_MILLIS = 5 * 60 * 1000

# How long to wait for a REFRESH_TOKEN reply before giving up on that attempt. Required,
# not optional: an older server silently ignores the command, so without a timeout the
# pending marker would never clear and no later attempt could be made.
TOKEN_REFRESH_REPLY_TIMEOUT_MILLIS = 30 * 1000

# Placeholder held while the token exchange is still running and the new token is not
# known yet. The marker must be claimed before the exchange starts, or the next heartbeat
# would start a second one. Not a real token, and never sent.
_REFRESH_IN_PROGRESS = '__refresh_in_progress__'

_SUCCESS_CODE = 0

_BEARER_PREFIX = 'Bearer '


def _now_millis():
    return int(time.time() * 1000)

class ProtobufPushClient(ConnectionListener):
    def __init__(self, host, port, use_ssl=True, connection_timeout=30, heartbeats=(10 * 1000, 10 * 1000),
                 client_config=None, callback_executor=None):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self._tiger_id = None
        self._private_key = None
        self._sign = None
        self._connection = None
        self.callback_executor = callback_executor
        if not self.callback_executor:
            max_workers = client_config.callback_thread_pool_size if client_config else None
            self.callback_executor = CallbackThreadPoolExecutor(max_workers=max_workers)

        self.subscribed_symbols = None
        self.query_subscribed_callback = None
        self.quote_changed = None
        self.quote_bbo_changed = None
        self.quote_depth_changed = None
        self.tick_changed = None
        self.full_tick_changed = None
        self.asset_changed = None
        self.position_changed = None
        self.order_changed = None
        self.transaction_changed = None
        self.stock_top_changed = None
        self.option_top_changed = None
        self.kline_changed = None
        self.cc_changed = None
        self.cc_bbo_changed = None
        self.connect_callback = None
        self.disconnect_callback = None
        self.subscribe_callback = None
        self.unsubscribe_callback = None
        self.error_callback = None
        self.heartbeat_callback = None
        self.kickout_callback = None
        self._connection_timeout = connection_timeout
        self._heartbeats = heartbeats
        self._client_config = client_config
        self._use_full_tick = self._client_config.use_full_tick if self._client_config else False
        self._authentication = getattr(client_config, 'authentication', None) if client_config else None
        self._oauth2_mode = self._authentication is not None \
            and self._authentication.auth_type == AuthenticationType.OAUTH2
        # The access token this connection is authenticated with. Per-connection rather
        # than per-client: a reconnect builds a new connection and sends a fresh connect
        # message, so it must start clean instead of inheriting a stale value.
        self._access_token = None
        # Token carried by an in-flight REFRESH_TOKEN; None when none is outstanding
        self._refresh_pending = None
        self._refresh_sent_at = 0
        self._refresh_lock = threading.Lock()
        self.logger = logging.getLogger('tiger_openapi')
        try:
            _patch_ssl()
        except:
            pass

    def connect(self, tiger_id=None, private_key=None):
        """
        :param tiger_id: required in signature mode; unused in OAuth2 mode
        :param private_key: required in signature mode; unused in OAuth2 mode
        """
        if self._oauth2_mode:
            # tigerId and the private key play no part in OAuth2 mode. An empty string is
            # the proto3 default and is not serialized.
            self._tiger_id = ''
            self._sign = ''
        else:
            self._tiger_id = tiger_id
            self._private_key = private_key
            self._sign = sign_with_rsa(self._private_key, self._tiger_id, 'utf-8')
        self._connect()

    def _current_access_token(self):
        """Return a currently usable access token, refreshing if close to expiry."""
        if not self._oauth2_mode:
            return None
        context = RequestAuthContext({}, place_order=False)
        self._authentication.apply(context)
        header = context.authorization_header or ''
        return header[len(_BEARER_PREFIX):] if header.startswith(_BEARER_PREFIX) else header

    def _connect(self):
        try:
            if self._connection:
                self._connection.remove_listener('push')
                self._connection.transport.cleanup()
        except:
            pass

        self._connection = PushConnection(host_and_ports=[(self.host, self.port)],
                                          keepalive=KEEPALIVE, timeout=self._connection_timeout,
                                          heartbeats=self._heartbeats, reconnect_attempts_max=60,
                                          callback_executor=self.callback_executor)
        self._connection.set_listener('push', self)
        # Fetched on every (re)connect: a reconnect must present the token that is valid
        # now. None in signature mode, which is what keeps the connect message unchanged.
        access_token = None
        if self._oauth2_mode:
            with self._refresh_lock:
                self._refresh_pending = None
                self._refresh_sent_at = 0
            access_token = self._current_access_token()
            if not access_token:
                # Connecting without a credential would just be rejected, and by then the
                # reason (never authorized / refresh failed) would be lost
                raise ConnectFailedException('no oauth2 access token available, cannot connect')
            self._access_token = access_token
        try:
            if self.use_ssl:
                self._connection.set_ssl([(self.host, self.port)])
            con_req = ProtoMessageUtil.build_connect_message(self._tiger_id, self._sign,
                                                             send_interval=self._heartbeats[0],
                                                             receive_interval=self._heartbeats[1],
                                                             use_full_tick=self._use_full_tick,
                                                             access_token=access_token
                                                             )
            self._connection.connect(con_req, wait=True,
                                     )
        except ConnectFailedException as e:
            raise e

    def disconnect(self):
        if self._connection:
            self._connection.disconnect()
            self.callback_executor.shutdown()

    def on_connected(self, frame):
        if self.connect_callback:
            self.connect_callback(frame)

    def on_disconnected(self):
        if self.disconnect_callback:
            self.disconnect_callback()
        elif self._oauth2_mode:
            # A reconnect refetches the token; if that fails, abandon this attempt rather
            # than raise into the receiving thread
            try:
                self._connect()
            except Exception as e:
                self.logger.error('reconnect with oauth2 failed: %s', e)
        else:
            self._connect()

    def on_disconnecting(self):
        self.on_disconnected()

    def on_heartbeat(self, frame):
        self.logger.debug('heart-beat')
        if self._oauth2_mode:
            self._refresh_token_if_needed()
        if self.heartbeat_callback:
            self.heartbeat_callback(frame)

    def _refresh_token_if_needed(self):
        """Rotate this connection's access token if the current one is close to expiry.

        Driven by the heartbeat rather than a timer of its own: the heartbeat already runs
        on a live connection at a known interval, and a token with a day-long TTL needs no
        finer granularity. A separate timer would have to track connection liveness again.

        Silent on an older server: REFRESH_TOKEN lands in the default branch of its
        command switch and no reply ever comes, so a pending rotation is abandoned after
        the timeout instead of blocking further attempts forever. The connection keeps
        working until the server drops it.
        """
        with self._refresh_lock:
            if self._refresh_pending is not None:
                if _now_millis() - self._refresh_sent_at < TOKEN_REFRESH_REPLY_TIMEOUT_MILLIS:
                    # Still waiting for a reply; do not send a second one. This also
                    # covers an exchange still running, since the marker is claimed first.
                    return
                # No reply within the window: an older server ignoring the command, a lost
                # reply, or a stuck exchange. Clear it so a later attempt can happen.
                self.logger.info('refresh token got no reply within %sms',
                                 TOKEN_REFRESH_REPLY_TIMEOUT_MILLIS)
                self._refresh_pending = None
                self._refresh_sent_at = 0

            sessions = getattr(self._authentication, 'session_manager', None)
            current = sessions.status() if sessions is not None else None
            if current is None or not current.needs_refresh(TOKEN_REFRESH_AHEAD_MILLIS):
                return

            # Claimed before the exchange starts: the next heartbeat must find a rotation
            # already in progress
            self._refresh_pending = _REFRESH_IN_PROGRESS
            self._refresh_sent_at = _now_millis()

        try:
            # The exchange is a synchronous HTTP call and must not block the callback thread
            threading.Thread(target=self._obtain_and_send_token,
                             name='tiger-socket-token-refresh', daemon=True).start()
        except Exception as e:
            self._clear_refresh_claim()
            self.logger.error('refresh token not scheduled: %s', e)

    def _obtain_and_send_token(self):
        try:
            new_token = self._current_access_token()
        except Exception as e:
            self._clear_refresh_claim()
            self.logger.error('refresh token fail: %s', e)
            return
        if not new_token:
            # A failed refresh is no reason to drop the connection: the token pinned on
            # the server is usually still valid, and the server closes the connection
            # itself if it is not
            self._clear_refresh_claim()
            self.logger.warning('refresh token skipped, no usable access token')
            return

        with self._refresh_lock:
            if new_token == self._access_token:
                # Unchanged: the session manager's window had not opened yet, so it handed
                # back the token the server already has
                self._refresh_pending = None
                self._refresh_sent_at = 0
                return
            self._refresh_pending = new_token
            self._refresh_sent_at = _now_millis()
        try:
            self._connection.send_frame(ProtoMessageUtil.build_refresh_token_message(new_token))
            self.logger.info('refresh token sent')
        except Exception as e:
            self._clear_refresh_claim()
            self.logger.error('send refresh token fail: %s', e)

    def _clear_refresh_claim(self):
        with self._refresh_lock:
            self._refresh_pending = None
            self._refresh_sent_at = 0

    def on_refresh_token(self, frame):
        """Apply the server's acknowledgement of a rotation.

        Only moves the pinned token forward on success. On rejection it stays as it was,
        matching what the server still has: the server explicitly leaves its own
        connection attributes untouched when it rejects a rotation.
        """
        with self._refresh_lock:
            pending = self._refresh_pending
            self._refresh_pending = None
            self._refresh_sent_at = 0
            if frame.code == _SUCCESS_CODE:
                # Never pin the in-progress placeholder: a reply arriving while it is
                # still held did not come from a message we sent
                if pending is not None and pending != _REFRESH_IN_PROGRESS:
                    self._access_token = pending
        if frame.code == _SUCCESS_CODE:
            self.logger.info('refresh token accepted. detail:%s', frame.msg)
        else:
            self.logger.warning('refresh token rejected. code:%s, msg:%s', frame.code, frame.msg)

    def on_error(self, frame):
        if frame.code == 4001 and self.kickout_callback:
            self.kickout_callback(frame)
        elif self.error_callback:
            self.error_callback(frame)
        else:
            self.logger.error(frame)

    def on_message(self, frame):
        try:
            if frame.code == ResponseType.GET_SUB_SYMBOLS_END.value:
                if self.query_subscribed_callback:
                    self.query_subscribed_callback(frame.msg)
            elif frame.code == ResponseType.GET_SUBSCRIBE_END.value:
                if self.subscribe_callback:
                    self.subscribe_callback(frame)
            elif frame.code == ResponseType.GET_CANCEL_SUBSCRIBE_END.value:
                if self.unsubscribe_callback:
                    self.unsubscribe_callback(frame)
            elif frame.code == ResponseType.ERROR_END.value:
                if self.error_callback:
                    self.error_callback(frame)
            else:
                if frame.body.dataType == SocketCommon.DataType.Quote:
                    if frame.body.quoteData.type == SocketCommon.QuoteType.BASIC and self.quote_changed:
                        self.quote_changed(frame.body.quoteData)
                    if frame.body.quoteData.type == SocketCommon.QuoteType.BBO and self.quote_bbo_changed:
                        self.quote_bbo_changed(frame.body.quoteData)
                    if frame.body.quoteData.type == SocketCommon.QuoteType.ALL:
                        if self.quote_changed:
                            basic_data = convert_to_basic_data(frame.body.quoteData)
                            if basic_data:
                                self.quote_changed(basic_data)
                        if self.quote_bbo_changed:
                            bbo_data = convert_to_bbo_data(frame.body.quoteData)
                            if bbo_data:
                                self.quote_bbo_changed(bbo_data)
                elif frame.body.dataType in {SocketCommon.DataType.Future, SocketCommon.DataType.Option}:
                    if self.quote_changed:
                        basic_data = convert_to_basic_data(frame.body.quoteData)
                        if basic_data:
                            self.quote_changed(basic_data)
                    if self.quote_bbo_changed:
                        bbo_data = convert_to_bbo_data(frame.body.quoteData)
                        if bbo_data:
                            self.quote_bbo_changed(bbo_data)
                elif frame.body.dataType == SocketCommon.DataType.QuoteDepth:
                    if self.quote_depth_changed:
                        self.quote_depth_changed(frame.body.quoteDepthData)
                elif frame.body.dataType == SocketCommon.DataType.TradeTick:
                    if self._use_full_tick:
                        if self.full_tick_changed:
                            self.full_tick_changed(frame.body.tickData)
                    else:
                        if self.tick_changed:
                            self.tick_changed(self._convert_tick(frame.body.tradeTickData))
                elif frame.body.dataType == SocketCommon.DataType.OrderStatus:
                    if self.order_changed:
                        frame.body.orderStatusData.status = get_order_status(frame.body.orderStatusData.status,
                                                                             frame.body.orderStatusData.filledQuantity).name
                        self.order_changed(frame.body.orderStatusData)
                elif frame.body.dataType == SocketCommon.DataType.OrderTransaction:
                    if self.transaction_changed:
                        self.transaction_changed(frame.body.orderTransactionData)
                elif frame.body.dataType == SocketCommon.DataType.Asset:
                    if self.asset_changed:
                        self.asset_changed(frame.body.assetData)
                elif frame.body.dataType == SocketCommon.DataType.Position:
                    if self.position_changed:
                        self.position_changed(frame.body.positionData)
                elif frame.body.dataType == SocketCommon.DataType.StockTop:
                    if self.stock_top_changed:
                        self.stock_top_changed(frame.body.stockTopData)
                elif frame.body.dataType == SocketCommon.DataType.OptionTop:
                    if self.option_top_changed:
                        self.option_top_changed(frame.body.optionTopData)
                elif frame.body.dataType == SocketCommon.DataType.Kline:
                    if self.kline_changed:
                        self.kline_changed(frame.body.klineData)
                elif frame.body.dataType == SocketCommon.DataType.Cc:
                    if self.cc_changed:
                        basic_data = convert_to_basic_data(frame.body.quoteData)
                        if basic_data:
                            self.cc_changed(basic_data)
                    if self.cc_bbo_changed:
                        bbo_data = convert_to_bbo_data(frame.body.quoteData)
                        if bbo_data:
                            self.cc_bbo_changed(bbo_data)
                else:
                    self.logger.warning(f'unhandled frame: {frame}')
        except Exception:
            self.logger.error(f'error in on_message ', exc_info=True)

    def subscribe_asset(self, account=None):
        """
        订阅账户资产更新
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_trade_message(SocketCommon.DataType.Asset, account)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_asset(self, account=None):
        """
        退订账户资产更新
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_trade_message(SocketCommon.DataType.Asset, account)
        self._connection.send_frame(req)
        return req.id

    def subscribe_position(self, account=None):
        """
        订阅账户持仓更新
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_trade_message(SocketCommon.DataType.Position, account)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_position(self, account=None):
        """
        退订账户持仓更新
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_trade_message(SocketCommon.DataType.Position, account)
        self._connection.send_frame(req)
        return req.id

    def subscribe_order(self, account=''):
        """
        订阅账户订单更新
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_trade_message(SocketCommon.DataType.OrderStatus, account)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_order(self, account=None):
        """
        退订账户订单更新
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_trade_message(SocketCommon.DataType.OrderStatus, account)
        self._connection.send_frame(req)
        return req.id

    def subscribe_transaction(self, account=None):
        """
        订阅订单执行明细
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_trade_message(SocketCommon.DataType.OrderTransaction, account)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_transaction(self, account=None):
        """
        退订订单执行明细
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_trade_message(SocketCommon.DataType.OrderTransaction, account)
        self._connection.send_frame(req)
        return req.id

    def subscribe_quote(self, symbols):
        """
        订阅行情更新
        :param symbols:
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_quote_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def subscribe_tick(self, symbols):
        """
        subscribe trade tick
        :param symbols: symbol列表
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_tick_quote_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def subscribe_depth_quote(self, symbols):
        """
        订阅深度行情
        :param symbols: symbol列表
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_depth_quote_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def subscribe_option(self, symbols):
        """
        订阅期权行情
        :param symbols: symbol列表
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_quote_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def subscribe_future(self, symbols):
        """
        订阅期货行情
        :param symbols: symbol列表
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_quote_message(symbols, data_type=SocketCommon.Future)
        self._connection.send_frame(req)
        return req.id

    def subscribe_stock_top(self, market, indicators):
        """
        订阅股票榜单行情
        :param market: 市场
        :param indicators: indicator列表
        :return:
        """
        indicator_names = []
        if indicators:
            indicator_names = [get_enum_value(indicator) for indicator in indicators]
        req = ProtoMessageUtil.build_subscribe_quote_message(symbols=indicator_names, data_type=SocketCommon.StockTop,
                                                             market=market)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_stock_top(self, market, indicators):
        """
        退订股票榜单行情
        :param market: 市场
        :param indicators: indicator列表
        :return:
        """
        indicator_names = []
        if indicators:
            indicator_names = [get_enum_value(indicator) for indicator in indicators]
        req = ProtoMessageUtil.build_unsubscribe_quote_message(symbols=indicator_names, data_type=SocketCommon.StockTop,
                                                               market=market)
        self._connection.send_frame(req)
        return req.id

    def subscribe_option_top(self, market, indicators):
        """
        订阅期权榜单行情
        :param market: 市场
        :param indicators: indicator列表
        :return:
        """
        indicator_names = []
        if indicators:
            indicator_names = [get_enum_value(indicator) for indicator in indicators]
        req = ProtoMessageUtil.build_subscribe_quote_message(symbols=indicator_names, data_type=SocketCommon.OptionTop,
                                                             market=market)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_option_top(self, market, indicators):
        """
        退订期权榜单行情
        :param market: 市场
        :param indicators: indicator列表
        :return:
        """
        indicator_names = []
        if indicators:
            indicator_names = [get_enum_value(indicator) for indicator in indicators]
        req = ProtoMessageUtil.build_unsubscribe_quote_message(symbols=indicator_names, data_type=SocketCommon.OptionTop,
                                                               market=market)
        self._connection.send_frame(req)
        return req.id

    def query_subscribed_quote(self):
        """
        查询已订阅行情的合约
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_query_message()
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_quote(self, symbols=None):
        """
        退订行情更新
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_quote_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_tick(self, symbols=None):
        """
        退订行情更新
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_tick_quote_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_depth_quote(self, symbols=None):
        """
        退订深度行情更新
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_depth_quote_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def subscribe_kline(self, symbols=None):
        """
        订阅K线
        :param symbols:
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_kline_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_kline(self, symbols=None):
        """
        退订K线
        :param symbols:
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_kline_message(symbols)
        self._connection.send_frame(req)
        return req.id

    def subscribe_cc(self, symbols):
        """
        订阅数字货币行情
        :param symbols: symbol列表
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_quote_message(symbols, data_type=SocketCommon.Cc)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_cc(self, symbols=None):
        """
        退订数字货币行情
        :param symbols: symbol列表
        :return:
        """
        req = ProtoMessageUtil.build_unsubscribe_quote_message(symbols, data_type=SocketCommon.Cc)
        self._connection.send_frame(req)
        return req.id

    def subscribe_market(self, market):
        req = ProtoMessageUtil.build_subscribe_market_message(market)
        self._connection.send_frame(req)
        return req.id

    def unsubscribe_market(self, market):
        req = ProtoMessageUtil.build_unsubscribe_market_message(market)
        self._connection.send_frame(req)
        return req.id

    def _convert_tick(self, data: TradeTickData):
        symbol = data.symbol
        price_offset = 10 ** data.priceOffset
        price_base = data.priceBase
        timestamp = data.timestamp
        sec_type = data.secType
        quote_level = data.quoteLevel
        # The latter time is equal to the sum of all previous values
        price_items = [('price', (float(item) + price_base) / price_offset) for item in data.price]
        time_items = [('time', item) for item in accumulate(data.time)]
        volume_items = [('volume', int(item)) for item in data.volume]
        tick_types = data.type
        if tick_types:
            tick_type_items = [('tick_type', item) for item in tick_types]
        else:
            tick_type_items = [('tick_type', None) for _ in range(len(time_items))]
        part_codes = data.partCode
        if part_codes:
            part_code_items = [('part_code', get_part_code(item)) for item in part_codes]
            part_code_name_items = [('part_code_name', get_part_code_name(item)) for item in part_codes]
        else:
            part_code_items = [('part_code', None) for _ in range(len(time_items))]
            part_code_name_items = [('part_code_name', None) for _ in range(len(time_items))]
        conds = data.cond
        cond_map = get_trade_condition_map(data.quoteLevel)
        if conds:
            cond_items = [('cond', get_trade_condition(item, cond_map)) for item in conds]
        else:
            cond_items = [('cond', None) for _ in range(len(time_items))]
        sn = int(data.sn)
        sn_list = [('sn', sn + i) for i in range(len(time_items))]
        merged_vols = data.mergedVols
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
            if item_dict.get('merged_vols'):
                vols = item_dict.pop('merged_vols').vol
                for i, vol in enumerate(vols):
                    sub_item = dict(item_dict)
                    sub_item['sn'] = sub_item['sn'] * 10 + i
                    sub_item['volume'] = vol
                    tick_item = TradeTickItem()
                    tick_item.__dict__ = sub_item
                    items.append(tick_item)
            else:
                item_dict.pop('merged_vols', None)
                tick_item = TradeTickItem()
                tick_item.__dict__ = item_dict
                items.append(tick_item)
        tick =  TradeTick()
        tick.__dict__ = {'symbol': symbol, 'sec_type': sec_type, 'quote_level': quote_level, 'timestamp': timestamp,
                'ticks': items}
        return tick
