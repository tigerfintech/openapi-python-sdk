from tigeropen.push.pb import SocketCommon_pb2 as _SocketCommon_pb2
from tigeropen.push.pb import QuoteData_pb2 as _QuoteData_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon as SocketCommon
from tigeropen.push.pb.QuoteData_pb2 import QuoteData as QuoteData

DESCRIPTOR: _descriptor.FileDescriptor

class QuoteBasicData(_message.Message):
    __slots__ = ("symbol", "type", "timestamp", "serverTimestamp", "avgPrice", "latestPrice", "latestPriceTimestamp", "latestTime", "preClose", "volume", "amount", "open", "high", "low", "hourTradingTag", "marketStatus", "identifier", "openInt", "tradeTime", "preSettlement", "minTick", "mi")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SERVERTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AVGPRICE_FIELD_NUMBER: _ClassVar[int]
    LATESTPRICE_FIELD_NUMBER: _ClassVar[int]
    LATESTPRICETIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LATESTTIME_FIELD_NUMBER: _ClassVar[int]
    PRECLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    HOURTRADINGTAG_FIELD_NUMBER: _ClassVar[int]
    MARKETSTATUS_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    OPENINT_FIELD_NUMBER: _ClassVar[int]
    TRADETIME_FIELD_NUMBER: _ClassVar[int]
    PRESETTLEMENT_FIELD_NUMBER: _ClassVar[int]
    MINTICK_FIELD_NUMBER: _ClassVar[int]
    MI_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    type: _SocketCommon_pb2.SocketCommon.QuoteType
    timestamp: int
    serverTimestamp: int
    avgPrice: float
    latestPrice: float
    latestPriceTimestamp: int
    latestTime: str
    preClose: float
    volume: int
    amount: float
    open: float
    high: float
    low: float
    hourTradingTag: str
    marketStatus: str
    identifier: str
    openInt: int
    tradeTime: int
    preSettlement: float
    minTick: float
    mi: _QuoteData_pb2.QuoteData.Minute
    def __init__(self, symbol: _Optional[str] = ..., type: _Optional[_Union[_SocketCommon_pb2.SocketCommon.QuoteType, str]] = ..., timestamp: _Optional[int] = ..., serverTimestamp: _Optional[int] = ..., avgPrice: _Optional[float] = ..., latestPrice: _Optional[float] = ..., latestPriceTimestamp: _Optional[int] = ..., latestTime: _Optional[str] = ..., preClose: _Optional[float] = ..., volume: _Optional[int] = ..., amount: _Optional[float] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., hourTradingTag: _Optional[str] = ..., marketStatus: _Optional[str] = ..., identifier: _Optional[str] = ..., openInt: _Optional[int] = ..., tradeTime: _Optional[int] = ..., preSettlement: _Optional[float] = ..., minTick: _Optional[float] = ..., mi: _Optional[_Union[_QuoteData_pb2.QuoteData.Minute, _Mapping]] = ...) -> None: ...
