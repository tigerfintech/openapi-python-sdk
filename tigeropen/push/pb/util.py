# -*- coding: utf-8 -*-
# 
# @Date    : 2023/2/21
# @Author  : sukai
import json
import time
import uuid
from typing import Optional

from tigeropen import __VERSION__

from tigeropen.common.consts.params import P_SDK_VERSION_PREFIX
from tigeropen.push.pb import Request_pb2, SocketCommon_pb2, Response_pb2
from tigeropen.push.pb.QuoteBBOData_pb2 import QuoteBBOData
from tigeropen.push.pb.QuoteBasicData_pb2 import QuoteBasicData
from tigeropen.push.pb.QuoteData_pb2 import QuoteData
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon


class ProtoMessageUtil:

    increment_count = 0

    @classmethod
    def increment(cls):
        cls.increment_count += 1
        return cls.increment_count

    @classmethod
    def extract_heart_beat(cls, resp):
        if resp.command == SocketCommon_pb2.SocketCommon.CONNECTED and "heart-beat" in resp.msg:
            msg = json.loads(resp.msg)
            hb_str = msg.get("heart-beat")
            send, recv = (int(i) for i in hb_str.split(','))
            return send, recv
        return None

    @classmethod
    def parse_response_message(cls, data):
        response = Response_pb2.Response()
        try:
            response.ParseFromString(data)
        except Exception as e:
            print(f'parse msg error: {e}, data:{data}')
        return response

    @classmethod
    def build_connect_message(cls, tiger_id, sign, version='3', send_interval=0, receive_interval=0,
                              use_full_tick=False):
        if send_interval < 0 or receive_interval < 0:
            raise ValueError("sendInterval < 0 or receiveInterval < 0")
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.CONNECT
        request.id = cls.increment()

        con = Request_pb2.Request.Connect()
        con.acceptVersion = version
        con.sdkVersion = P_SDK_VERSION_PREFIX + __VERSION__  # Replace with the appropriate SDK version
        con.tigerId = tiger_id
        con.sign = sign
        con.sendInterval = send_interval
        con.receiveInterval = receive_interval
        con.useFullTick = use_full_tick
        request.connect.CopyFrom(con)
        return request

    @classmethod
    def build_disconnect_message(cls):
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.DISCONNECT
        request.id = cls.increment()
        return request

    @classmethod
    def build_send_message(cls):
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.SEND
        request.id = cls.increment()
        return request

    @classmethod
    def build_heart_beat_message(cls):
        request = Request_pb2.Request()
        request.command = SocketCommon_pb2.SocketCommon.HEARTBEAT
        request.id = cls.increment()
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
        request.id = cls.increment()
        return request

    @classmethod
    def build_subscribe_quote_message(cls, symbols, data_type=SocketCommon_pb2.SocketCommon.Quote, market=None):
        return cls.build_quote_message(data_type, symbols, SocketCommon_pb2.SocketCommon.SUBSCRIBE, market=market)

    @classmethod
    def build_unsubscribe_quote_message(cls, symbols, data_type=SocketCommon_pb2.SocketCommon.Quote, market=None):
        return cls.build_quote_message(data_type, symbols, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE, market=market)

    @classmethod
    def build_subscribe_tick_quote_message(cls, symbols):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.TradeTick, symbols, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_unsubscribe_tick_quote_message(cls, symbols):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.TradeTick, symbols, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_subscribe_depth_quote_message(cls, symbols):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.QuoteDepth, symbols, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_unsubscribe_depth_quote_message(cls, symbols):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.QuoteDepth, symbols, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_subscribe_market_message(cls, market):
        return cls.build_market_quote_message(market, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_subscribe_kline_message(cls, symbols):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.Kline, symbols, SocketCommon_pb2.SocketCommon.SUBSCRIBE)

    @classmethod
    def build_unsubscribe_kline_message(cls, symbols):
        return cls.build_quote_message(SocketCommon_pb2.SocketCommon.Kline, symbols, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_unsubscribe_market_message(cls, market):
        return cls.build_market_quote_message(market, SocketCommon_pb2.SocketCommon.UNSUBSCRIBE)

    @classmethod
    def build_quote_message(cls, data_type, symbols, command, market=None):
        request = Request_pb2.Request()
        request.command = command
        request.id = cls.increment()

        sub = Request_pb2.Request.Subscribe()
        sub.dataType = data_type
        if symbols:
            sub.symbols = ','.join(symbols) if isinstance(symbols, list) else symbols
        if market:
            sub.market = market
        request.subscribe.CopyFrom(sub)
        return request

    @classmethod
    def build_market_quote_message(cls, market, command):
        request = Request_pb2.Request()
        request.command = command
        request.id = cls.increment()

        sub = Request_pb2.Request.Subscribe()
        sub.dataType = SocketCommon_pb2.SocketCommon.Quote
        sub.market = market
        request.subscribe.CopyFrom(sub)
        return request

    @classmethod
    def build_trade_message(cls, data_type, account, command):
        request = Request_pb2.Request()
        request.command = command
        request.id = cls.increment()

        sub = Request_pb2.Request.Subscribe()
        sub.dataType = data_type
        if account:
            sub.account = account
        request.subscribe.CopyFrom(sub)
        return request


def convert_to_bbo_data(quote_data):
    if not quote_data or not quote_data.type:
        return None
    quote_type = quote_data.type
    if quote_type != SocketCommon.QuoteType.ALL and quote_type != SocketCommon.QuoteType.BBO:
        return None
    builder = QuoteBBOData()
    builder.symbol = quote_data.symbol
    builder.type = SocketCommon.QuoteType.BBO
    builder.timestamp = quote_data.timestamp
    builder.askPrice = quote_data.askPrice
    builder.askSize = quote_data.askSize
    builder.bidPrice = quote_data.bidPrice
    builder.bidSize = quote_data.bidSize
    if quote_data.HasField('askTimestamp'):
        builder.askTimestamp = quote_data.askTimestamp
    if quote_data.HasField('bidTimestamp'):
        builder.bidTimestamp = quote_data.bidTimestamp
    return builder


def convert_to_basic_data(quote_data):
    if not quote_data or not quote_data.type:
        return None
    quote_type = quote_data.type
    if quote_type != SocketCommon.QuoteType.ALL and quote_type != SocketCommon.QuoteType.BASIC:
        return None
    builder = QuoteBasicData()
    builder.symbol = quote_data.symbol
    builder.type = SocketCommon.QuoteType.BASIC
    builder.timestamp = quote_data.timestamp
    if quote_data.HasField('serverTimestamp'):
        builder.serverTimestamp = quote_data.serverTimestamp
    if quote_data.HasField('avgPrice'):
        builder.avgPrice = quote_data.avgPrice
    builder.latestPrice = quote_data.latestPrice
    if quote_data.HasField('latestPriceTimestamp'):
        builder.latestPriceTimestamp = quote_data.latestPriceTimestamp
    builder.latestTime = quote_data.latestTime
    builder.preClose = quote_data.preClose
    builder.volume = quote_data.volume
    if quote_data.HasField('amount'):
        builder.amount = quote_data.amount
    if quote_data.HasField('open'):
        builder.open = quote_data.open
    if quote_data.HasField('high'):
        builder.high = quote_data.high
    if quote_data.HasField('low'):
        builder.low = quote_data.low
    if quote_data.HasField('hourTradingTag'):
        builder.hourTradingTag = quote_data.hourTradingTag
    if quote_data.HasField('marketStatus'):
        builder.marketStatus = quote_data.marketStatus
    if quote_data.HasField('identifier'):
        builder.identifier = quote_data.identifier
    if quote_data.HasField('openInt'):
        builder.openInt = quote_data.openInt
    if quote_data.HasField('tradeTime'):
        builder.tradeTime = quote_data.tradeTime
    if quote_data.HasField('preSettlement'):
        builder.preSettlement = quote_data.preSettlement
    if quote_data.HasField('minTick'):
        builder.minTick = quote_data.minTick
    if quote_data.HasField('mi'):
        builder.mi.CopyFrom(quote_data.mi)
    return builder

    