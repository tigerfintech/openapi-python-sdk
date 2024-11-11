from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuoteDepthData(_message.Message):
    __slots__ = ("symbol", "timestamp", "ask", "bid")
    class OrderBook(_message.Message):
        __slots__ = ("price", "volume", "orderCount", "exchange", "time")
        PRICE_FIELD_NUMBER: _ClassVar[int]
        VOLUME_FIELD_NUMBER: _ClassVar[int]
        ORDERCOUNT_FIELD_NUMBER: _ClassVar[int]
        EXCHANGE_FIELD_NUMBER: _ClassVar[int]
        TIME_FIELD_NUMBER: _ClassVar[int]
        price: _containers.RepeatedScalarFieldContainer[float]
        volume: _containers.RepeatedScalarFieldContainer[int]
        orderCount: _containers.RepeatedScalarFieldContainer[int]
        exchange: _containers.RepeatedScalarFieldContainer[str]
        time: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, price: _Optional[_Iterable[float]] = ..., volume: _Optional[_Iterable[int]] = ..., orderCount: _Optional[_Iterable[int]] = ..., exchange: _Optional[_Iterable[str]] = ..., time: _Optional[_Iterable[int]] = ...) -> None: ...
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    timestamp: int
    ask: QuoteDepthData.OrderBook
    bid: QuoteDepthData.OrderBook
    def __init__(self, symbol: _Optional[str] = ..., timestamp: _Optional[int] = ..., ask: _Optional[_Union[QuoteDepthData.OrderBook, _Mapping]] = ..., bid: _Optional[_Union[QuoteDepthData.OrderBook, _Mapping]] = ...) -> None: ...
