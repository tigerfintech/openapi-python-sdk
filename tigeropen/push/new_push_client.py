# -*- coding: utf-8 -*-
# 
# @Date    : 2023/2/17
# @Author  : sukai
import logging
import sys

from google.protobuf.json_format import MessageToJson

from tigeropen.common.consts import QuoteKeyType
from tigeropen.common.consts.push_types import ResponseType
from tigeropen.common.util.signature_utils import sign_with_rsa, read_private_key
from tigeropen.push import _patch_ssl
from tigeropen.push.network.connect import PushConnection
from tigeropen.push.network.exception import ConnectFailedException
from tigeropen.push.network.listener import HeartbeatListener, ConnectionListener
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
from tigeropen.push.pb.util import ProtoMessageUtil

if sys.platform == 'linux' or sys.platform == 'linux2':
    KEEPALIVE = True
else:
    KEEPALIVE = False




class NewPushClient(ConnectionListener):
    def __init__(self, host, port, use_ssl=True, connection_timeout=120, heartbeats=(30 * 1000, 30 * 1000)):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self._tiger_id = None
        self._private_key = None
        self._sign = None
        self._connection = None

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

    def connect(self, tiger_id, private_key):
        self._tiger_id = tiger_id
        self._private_key = private_key
        self._sign = sign_with_rsa(self._private_key, self._tiger_id, 'utf-8')
        self._connect()

    def _connect(self):
        try:
            if self._connection:
                self._connection.remove_listener('push')
                self._connection.transport.cleanup()
        except:
            pass

        self._connection = PushConnection(host_and_ports=[(self.host, self.port)],
                                          keepalive=KEEPALIVE, timeout=self._connection_timeout,
                                          heartbeats=self._heartbeats, reconnect_attempts_max=60)
        self._connection.set_listener('push', self)
        try:
            if self.use_ssl:
                self._connection.set_ssl([(self.host, self.port)])
            con_req = ProtoMessageUtil.build_connect_message(self._tiger_id, self._sign,
                                                             send_interval=self._heartbeats[0],
                                                             receive_interval=self._heartbeats[1])
            self._connection.connect(con_req, wait=True,
                                     )
        except ConnectFailedException as e:
            raise e

    def disconnect(self):
        if self._connection:
            self._connection.disconnect()

    def on_connected(self, frame):
        if self.connect_callback:
            self.connect_callback(frame)

    def on_disconnected(self):
        if self.disconnect_callback:
            self.disconnect_callback()
        else:
            self._connect()

    def on_error(self, frame):
        self.logger.error(frame)

    def on_message(self, frame):
        # self.logger.info(f'receive message: {MessageToJson(frame)}')
        # self.logger.debug(frame.code)
        # self.logger.debug(frame.body.dataType)
        # self.logger.debug(frame)
        if frame.code == ResponseType.GET_SUB_SYMBOLS_END.value:
            if self.query_subscribed_callback:
                self.query_subscribed_callback(frame)
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
                if self.quote_changed:
                    self.quote_changed(frame)
            elif frame.body.dataType == SocketCommon.DataType.OrderStatus:
                if self.order_changed:
                    self.order_changed(frame)
            elif frame.body.dataType == SocketCommon.DataType.OrderTransaction:
                if self.transaction_changed:
                    self.transaction_changed(frame)
            elif frame.body.dataType == SocketCommon.DataType.Asset:
                if self.asset_changed:
                    self.asset_changed(frame)
            elif frame.body.dataType == SocketCommon.DataType.Position:
                if self.position_changed:
                    self.position_changed(frame)
            elif frame.body.dataType == SocketCommon.DataType.TradeTick:
                if self.tick_changed:
                    self.tick_changed(frame)
            else:
                self.logger.info(f'unhandled frame: {frame}')

    def subscribe_asset(self, account=None):
        """
        订阅账户资产更新
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_trade_message(SocketCommon.DataType.Asset, account)
        self._connection.subscribe(req)

    def unsubscribe_asset(self, id=None):
        """
        退订账户资产更新
        :return:
        """

    def subscribe_position(self, account=None):
        """
        订阅账户持仓更新
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_trade_message(SocketCommon.DataType.Position, account)
        self._connection.subscribe(req)

    def unsubscribe_position(self, id=None):
        """
        退订账户持仓更新
        :return:
        """

    def subscribe_order(self, account=''):
        """
        订阅账户订单更新
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_trade_message(SocketCommon.DataType.OrderStatus, account)
        self._connection.subscribe(req)

    def unsubscribe_order(self, id=None):
        """
        退订账户订单更新
        :return:
        """

    def subscribe_transaction(self, account=None):
        """
        订阅订单执行明细
        :return:
        """

    def unsubscribe_transaction(self, id=None):
        """
        退订订单执行明细
        :return:
        """

    def subscribe_quote(self, symbols, market=''):
        """
        订阅行情更新
        :param symbols:
        :return:
        """
        req = ProtoMessageUtil.build_subscribe_quote_message(symbols, market)
        self._connection.subscribe(req)

    def subscribe_tick(self, symbols):
        """
        subscribe trade tick
        :param symbols: symbol列表
        :return:
        """

    def subscribe_depth_quote(self, symbols):
        """
        订阅深度行情
        :param symbols: symbol列表
        :return:
        """

    def subscribe_option(self, symbols):
        """
        订阅期权行情
        :param symbols: symbol列表
        :return:
        """

    def subscribe_future(self, symbols):
        """
        订阅期货行情
        :param symbols: symbol列表
        :return:
        """

    def query_subscribed_quote(self):
        """
        查询已订阅行情的合约
        :return:
        """

    def unsubscribe_quote(self, symbols=None, id=None):
        """
        退订行情更新
        :return:
        """

    def unsubscribe_tick(self, symbols=None, id=None):
        """
        退订行情更新
        :return:
        """

    def unsubscribe_depth_quote(self, symbols=None, id=None):
        """
        退订深度行情更新
        :return:
        """


if __name__ == '__main__':
    tiger_id = '2'
    key = read_private_key('/data0/conf/tiger-quant/openapi_test_private.pem')
    # con_req = ProtoMessageUtil.build_connect_message(tiger_id, 'signxxxx')
    #
    # js = MessageToJson(con_req)
    # print(js)
    NewPushClient()
    # h = 'openapi-sandbox.tigerfintech.com'
    # p = 9885
    # client = NewPushClient(h, p)
    # client.connect('2', read_private_key('/data0/conf/tiger-quant/openapi_test_private.pem'))
