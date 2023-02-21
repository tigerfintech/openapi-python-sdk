from tigeropen.push.pb import SocketCommon_pb2 as _SocketCommon_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuoteData(_message.Message):
    __slots__ = ["amount", "askPrice", "askSize", "askTimestamp", "avgPrice", "bidPrice", "bidSize", "bidTimestamp", "high", "hourTradingTag", "identifier", "latestPrice", "latestPriceTimestamp", "latestTime", "low", "marketStatus", "mi", "minTick", "open", "openInt", "preClose", "preSettlement", "serverTimestamp", "symbol", "timestamp", "tradeTime", "type", "volume"]
    class Minute(_message.Message):
        __slots__ = ["a", "h", "l", "o", "p", "t", "v"]
        A_FIELD_NUMBER: _ClassVar[int]
        H_FIELD_NUMBER: _ClassVar[int]
        L_FIELD_NUMBER: _ClassVar[int]
        O_FIELD_NUMBER: _ClassVar[int]
        P_FIELD_NUMBER: _ClassVar[int]
        T_FIELD_NUMBER: _ClassVar[int]
        V_FIELD_NUMBER: _ClassVar[int]
        a: float
        h: float
        l: float
        o: float
        p: float
        t: int
        v: int
        def __init__(self, p: _Optional[float] = ..., a: _Optional[float] = ..., t: _Optional[int] = ..., v: _Optional[int] = ..., o: _Optional[float] = ..., h: _Optional[float] = ..., l: _Optional[float] = ...) -> None: ...
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ASKPRICE_FIELD_NUMBER: _ClassVar[int]
    ASKSIZE_FIELD_NUMBER: _ClassVar[int]
    ASKTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AVGPRICE_FIELD_NUMBER: _ClassVar[int]
    BIDPRICE_FIELD_NUMBER: _ClassVar[int]
    BIDSIZE_FIELD_NUMBER: _ClassVar[int]
    BIDTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    HOURTRADINGTAG_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    LATESTPRICETIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LATESTPRICE_FIELD_NUMBER: _ClassVar[int]
    LATESTTIME_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    MARKETSTATUS_FIELD_NUMBER: _ClassVar[int]
    MINTICK_FIELD_NUMBER: _ClassVar[int]
    MI_FIELD_NUMBER: _ClassVar[int]
    OPENINT_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    PRECLOSE_FIELD_NUMBER: _ClassVar[int]
    PRESETTLEMENT_FIELD_NUMBER: _ClassVar[int]
    SERVERTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TRADETIME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    amount: float
    askPrice: float
    askSize: int
    askTimestamp: int
    avgPrice: float
    bidPrice: float
    bidSize: int
    bidTimestamp: int
    high: float
    hourTradingTag: str
    identifier: str
    latestPrice: float
    latestPriceTimestamp: int
    latestTime: str
    low: float
    marketStatus: str
    mi: QuoteData.Minute
    minTick: float
    open: float
    openInt: int
    preClose: float
    preSettlement: float
    serverTimestamp: int
    symbol: str
    timestamp: int
    tradeTime: int
    type: _SocketCommon_pb2.SocketCommon.QuoteType
    volume: int
    def __init__(self, symbol: _Optional[str] = ..., type: _Optional[_Union[_SocketCommon_pb2.SocketCommon.QuoteType, str]] = ..., timestamp: _Optional[int] = ..., serverTimestamp: _Optional[int] = ..., avgPrice: _Optional[float] = ..., latestPrice: _Optional[float] = ..., latestPriceTimestamp: _Optional[int] = ..., latestTime: _Optional[str] = ..., preClose: _Optional[float] = ..., volume: _Optional[int] = ..., amount: _Optional[float] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., hourTradingTag: _Optional[str] = ..., marketStatus: _Optional[str] = ..., askPrice: _Optional[float] = ..., askSize: _Optional[int] = ..., askTimestamp: _Optional[int] = ..., bidPrice: _Optional[float] = ..., bidSize: _Optional[int] = ..., bidTimestamp: _Optional[int] = ..., identifier: _Optional[str] = ..., openInt: _Optional[int] = ..., tradeTime: _Optional[int] = ..., preSettlement: _Optional[float] = ..., minTick: _Optional[float] = ..., mi: _Optional[_Union[QuoteData.Minute, _Mapping]] = ...) -> None: ...
