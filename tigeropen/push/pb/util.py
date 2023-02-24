# -*- coding: utf-8 -*-
# 
# @Date    : 2023/2/21
# @Author  : sukai
import time
import uuid
from tigeropen import __VERSION__

from tigeropen.common.consts.params import P_SDK_VERSION_PREFIX
from tigeropen.push.pb import Request_pb2, SocketCommon_pb2, Response_pb2


class ProtoMessageUtil:

    increment_count = 0

    @classmethod
    @property
    def increment(cls):
        cls.increment_count += 1
        return cls.increment_count

    @classmethod
    def is_heart_beat(cls, resp):
        return resp.command == SocketCommon_pb2.SocketCommon.HEARTBEAT

    @classmethod
    def parse_response_message(cls, data):
        response = Response_pb2.Response()
        response.ParseFromString(data)
        return response

    @classmethod
    def build_connect_message(cls, tiger_id, sign, version='3', send_interval=0, receive_interval=0):
        if send_interval < 0 or receive_interval < 0:
            raise ValueError("sendInterval < 0 or receiveInterval < 0")
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.CONNECT
        request.id = cls.increment

        con = Request_pb2.Request.Connect()
        con.acceptVersion = version
        con.sdkVersion = P_SDK_VERSION_PREFIX + __VERSION__  # Replace with the appropriate SDK version
        con.tigerId = tiger_id
        con.sign = sign
        con.sendInterval = send_interval
        con.receiveInterval = receive_interval
        request.connect.CopyFrom(con)
        return request

    @classmethod
    def build_disconnect_message(cls):
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.DISCONNECT
        request.id = cls.increment
        return request

    @classmethod
    def build_send_message(cls):
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.SEND
        request.id = cls.increment
        return request

    @classmethod
    def build_heart_beat_message(cls):
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.HEARTBEAT
        request.id = cls.increment
        return request

    @classmethod
    def build_subscribe_trade_message(cls, data_type, account):
        return cls.build_trade_message(data_type, account, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_unsubscribe_trade_message(cls, data_type, account):
        return cls.build_trade_message(data_type, account, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_subscribe_query_message(cls):
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.SEND
        request.id = cls.increment
        return request

    @classmethod
    def build_subscribe_quote_message(cls, symbols, market=None):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.Quote, symbols, market, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_unsubscribe_quote_message(cls, symbols, market=None):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.Quote, symbols, market, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_subscribe_tick_quote_message(cls, symbols, market):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.TradeTick, symbols, market, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_unsubscribe_tick_quote_message(cls, symbols, market):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.TradeTick, symbols, market, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_subscribe_depth_quote_message(cls, symbols, market):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.QuoteDepth, symbols, market, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_unsubscribe_depth_quote_message(cls, symbols, market):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.QuoteDepth, symbols, market, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_quote_message(cls, data_type, symbols, market, command):
        request = Request_pb2.Request()
        request.command = command
        request.id = cls.increment

        sub = Request_pb2.Request.Subscribe()
        sub.dataType = data_type
        sub.symbols = ','.join(symbols) if isinstance(symbols, list) else symbols
        if market:
            sub.market = market
        request.subscribe.CopyFrom(sub)
        return request

    @classmethod
    def build_trade_message(cls, data_type, account, command):
        request = Request_pb2.Request()
        request.command = command
        request.id = cls.increment

        sub = Request_pb2.Request.Subscribe()
        sub.dataType = data_type
        if account:
            sub.account = account
        request.subscribe.CopyFrom(sub)
        return request