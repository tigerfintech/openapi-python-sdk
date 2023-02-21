from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuoteDepthData(_message.Message):
    __slots__ = ["ask", "bid", "symbol", "timestamp"]
    class OrderBook(_message.Message):
        __slots__ = ["orderCount", "price", "volume"]
        ORDERCOUNT_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        VOLUME_FIELD_NUMBER: _ClassVar[int]
        orderCount: _containers.RepeatedScalarFieldContainer[int]
        price: _containers.RepeatedScalarFieldContainer[float]
        volume: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, price: _Optional[_Iterable[float]] = ..., volume: _Optional[_Iterable[int]] = ..., orderCount: _Optional[_Iterable[int]] = ...) -> None: ...
    ASK_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ask: QuoteDepthData.OrderBook
    bid: QuoteDepthData.OrderBook
    symbol: str
    timestamp: int
    def __init__(self, symbol: _Optional[str] = ..., timestamp: _Optional[int] = ..., ask: _Optional[_Union[QuoteDepthData.OrderBook, _Mapping]] = ..., bid: _Optional[_Union[QuoteDepthData.OrderBook, _Mapping]] = ...) -> None: ...
