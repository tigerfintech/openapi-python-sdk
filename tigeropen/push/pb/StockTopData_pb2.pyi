from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StockTopData(_message.Message):
    __slots__ = ["market", "timestamp", "topData"]
    class StockItem(_message.Message):
        __slots__ = ["latestPrice", "symbol", "targetValue"]
        LATESTPRICE_FIELD_NUMBER: _ClassVar[int]
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        TARGETVALUE_FIELD_NUMBER: _ClassVar[int]
        latestPrice: float
        symbol: str
        targetValue: float
        def __init__(self, symbol: _Optional[str] = ..., latestPrice: _Optional[float] = ..., targetValue: _Optional[float] = ...) -> None: ...
    class TopData(_message.Message):
        __slots__ = ["item", "targetName"]
        ITEM_FIELD_NUMBER: _ClassVar[int]
        TARGETNAME_FIELD_NUMBER: _ClassVar[int]
        item: _containers.RepeatedCompositeFieldContainer[StockTopData.StockItem]
        targetName: str
        def __init__(self, targetName: _Optional[str] = ..., item: _Optional[_Iterable[_Union[StockTopData.StockItem, _Mapping]]] = ...) -> None: ...
    MARKET_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOPDATA_FIELD_NUMBER: _ClassVar[int]
    market: str
    timestamp: int
    topData: _containers.RepeatedCompositeFieldContainer[StockTopData.TopData]
    def __init__(self, market: _Optional[str] = ..., timestamp: _Optional[int] = ..., topData: _Optional[_Iterable[_Union[StockTopData.TopData, _Mapping]]] = ...) -> None: ...
