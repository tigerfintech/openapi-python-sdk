# -*- coding: utf-8 -*-
"""
Created on 2018/10/30

@author: gaoan
"""

from tigeropen.push.protobuf_push_client import ProtobufPushClient
from tigeropen.push.stomp_push_client import StompPushClient

USE_STOMP = False


class PushClient:
    def __init__(self, host, port, use_ssl=True, connection_timeout=120, heartbeats=(30 * 1000, 30 * 1000),
                 use_protobuf=False):
        """
        :param host:
        :param port:
        :param use_ssl:
        :param connection_timeout: unit: second. The timeout value should be greater the heartbeats interval
        :param heartbeats: tuple of millisecond
        :param use_protobuf: use stomp protocol or protobuf
        """
        if use_protobuf:
            self.client = ProtobufPushClient(host=host, port=port, use_ssl=use_ssl,
                                             connection_timeout=connection_timeout,
                                             heartbeats=heartbeats)
        else:
            self.client = StompPushClient(host=host, port=port, use_ssl=use_ssl, connection_timeout=connection_timeout,
                                          heartbeats=heartbeats)


    @property
    def subscribed_symbols(self):
        """deprecated, use query_subscribed_callback instead"""
        return self.client.subscribed_symbols

    @subscribed_symbols.setter
    def subscribed_symbols(self, value):
        self.client.subscribed_symbols = value

    @property
    def query_subscribed_callback(self):
        return self.client.query_subscribed_callback

    @query_subscribed_callback.setter
    def query_subscribed_callback(self, value):
        self.client.query_subscribed_callback = value

    @property
    def quote_changed(self):
        return self.client.quote_changed

    @quote_changed.setter
    def quote_changed(self, value):
        self.client.quote_changed = value

    @property
    def quote_bbo_changed(self):
        return self.client.quote_bbo_changed

    @quote_bbo_changed.setter
    def quote_bbo_changed(self, value):
        self.client.quote_bbo_changed = value

    @property
    def quote_depth_changed(self):
        return self.client.quote_depth_changed

    @quote_depth_changed.setter
    def quote_depth_changed(self, value):
        self.client.quote_depth_changed = value

    @property
    def tick_changed(self):
        return self.client.tick_changed

    @tick_changed.setter
    def tick_changed(self, value):
        self.client.tick_changed = value

    @property
    def asset_changed(self):
        return self.client.asset_changed

    @asset_changed.setter
    def asset_changed(self, value):
        self.client.asset_changed = value

    @property
    def position_changed(self):
        return self.client.position_changed

    @position_changed.setter
    def position_changed(self, value):
        self.client.position_changed = value

    @property
    def order_changed(self):
        return self.client.order_changed

    @order_changed.setter
    def order_changed(self, value):
        self.client.order_changed = value

    @property
    def transaction_changed(self):
        return self.client.transaction_changed

    @transaction_changed.setter
    def transaction_changed(self, value):
        self.client.transaction_changed = value

    @property
    def connect_callback(self):
        return self.client.connect_callback

    @connect_callback.setter
    def connect_callback(self, value):
        self.client.connect_callback = value

    @property
    def disconnect_callback(self):
        return self.client.disconnect_callback

    @disconnect_callback.setter
    def disconnect_callback(self, value):
        self.client.disconnect_callback = value

    @property
    def subscribe_callback(self):
        return self.client.subscribe_callback

    @subscribe_callback.setter
    def subscribe_callback(self, value):
        self.client.subscribe_callback = value

    @property
    def unsubscribe_callback(self):
        return self.client.unsubscribe_callback

    @unsubscribe_callback.setter
    def unsubscribe_callback(self, value):
        self.client.unsubscribe_callback = value

    @property
    def error_callback(self):
        return self.client.error_callback

    @error_callback.setter
    def error_callback(self, value):
        self.client.error_callback = value

    def connect(self, tiger_id, private_key):
        self.client.connect(tiger_id=tiger_id, private_key=private_key)

    def disconnect(self):
        self.client.disconnect()

    def on_connected(self, frame):
        self.client.on_connected(frame)

    def on_disconnected(self):
        self.client.on_disconnected()

    def on_message(self, frame):
        self.client.on_message(frame)

    def on_error(self, frame):
        self.client.on_error(frame)

    def subscribe_asset(self, account=None):
        """
        订阅账户资产更新
        :return:
        """
        return self.client.subscribe_asset(account=account)

    def unsubscribe_asset(self):
        """
        退订账户资产更新
        :return:
        """
        self.client.unsubscribe_asset()

    def subscribe_position(self, account=None):
        """
        订阅账户持仓更新
        :return:
        """
        return self.client.subscribe_position(account=account)

    def unsubscribe_position(self):
        """
        退订账户持仓更新
        :return:
        """
        self.client.unsubscribe_position()

    def subscribe_order(self, account=None):
        """
        订阅账户订单更新
        :return:
        """
        return self.client.subscribe_order(account=account)

    def unsubscribe_order(self):
        """
        退订账户订单更新
        :return:
        """
        self.client.unsubscribe_order()

    def subscribe_transaction(self, account=None):
        """
        订阅订单执行明细
        :return:
        """
        return self.client.subscribe_transaction(account=account)

    def unsubscribe_transaction(self):
        """
        退订订单执行明细
        :return:
        """
        self.client.unsubscribe_transaction()

    def subscribe_quote(self, symbols, **kwargs):
        """
        订阅行情更新
        :param symbols:
        :return:
        """

        return self.client.subscribe_quote(symbols=symbols)

    def subscribe_tick(self, symbols):
        """
        subscribe trade tick
        :param symbols: symbol列表
        :return:
        """
        return self.client.subscribe_tick(symbols=symbols)

    def subscribe_depth_quote(self, symbols):
        """
        订阅深度行情
        :param symbols: symbol列表
        :return:
        """
        return self.client.subscribe_depth_quote(symbols=symbols)

    def subscribe_option(self, symbols):
        """
        订阅期权行情
        :param symbols: symbol列表
        :return:
        """
        return self.client.subscribe_option(symbols=symbols)

    def subscribe_future(self, symbols):
        """
        订阅期货行情
        :param symbols: symbol列表
        :return:
        """
        return self.client.subscribe_future(symbols=symbols)

    def query_subscribed_quote(self):
        """
        查询已订阅行情的合约
        :return:
        """
        return self.client.query_subscribed_quote()

    def unsubscribe_quote(self, symbols=None):
        """
        退订行情更新
        :return:
        """
        return self.client.unsubscribe_quote(symbols=symbols)

    def unsubscribe_tick(self, symbols=None):
        """
        退订行情更新
        :return:
        """
        return self.client.unsubscribe_tick(symbols=symbols)

    def unsubscribe_depth_quote(self, symbols=None):
        """
        退订深度行情更新
        :return:
        """
        self.client.unsubscribe_depth_quote(symbols=symbols)

