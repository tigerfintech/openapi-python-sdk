from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OptionTopData(_message.Message):
    __slots__ = ("market", "timestamp", "topData")
    class TopData(_message.Message):
        __slots__ = ("targetName", "bigOrder", "item")
        TARGETNAME_FIELD_NUMBER: _ClassVar[int]
        BIGORDER_FIELD_NUMBER: _ClassVar[int]
        ITEM_FIELD_NUMBER: _ClassVar[int]
        targetName: str
        bigOrder: _containers.RepeatedCompositeFieldContainer[OptionTopData.BigOrder]
        item: _containers.RepeatedCompositeFieldContainer[OptionTopData.OptionItem]
        def __init__(self, targetName: _Optional[str] = ..., bigOrder: _Optional[_Iterable[_Union[OptionTopData.BigOrder, _Mapping]]] = ..., item: _Optional[_Iterable[_Union[OptionTopData.OptionItem, _Mapping]]] = ...) -> None: ...
    class BigOrder(_message.Message):
        __slots__ = ("symbol", "expiry", "strike", "right", "dir", "volume", "price", "amount", "tradeTime")
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        EXPIRY_FIELD_NUMBER: _ClassVar[int]
        STRIKE_FIELD_NUMBER: _ClassVar[int]
        RIGHT_FIELD_NUMBER: _ClassVar[int]
        DIR_FIELD_NUMBER: _ClassVar[int]
        VOLUME_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        TRADETIME_FIELD_NUMBER: _ClassVar[int]
        symbol: str
        expiry: str
        strike: str
        right: str
        dir: str
        volume: float
        price: float
        amount: float
        tradeTime: int
        def __init__(self, symbol: _Optional[str] = ..., expiry: _Optional[str] = ..., strike: _Optional[str] = ..., right: _Optional[str] = ..., dir: _Optional[str] = ..., volume: _Optional[float] = ..., price: _Optional[float] = ..., amount: _Optional[float] = ..., tradeTime: _Optional[int] = ...) -> None: ...
    class OptionItem(_message.Message):
        __slots__ = ("symbol", "expiry", "strike", "right", "totalAmount", "totalVolume", "totalOpenInt", "volumeToOpenInt", "latestPrice", "updateTime")
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        EXPIRY_FIELD_NUMBER: _ClassVar[int]
        STRIKE_FIELD_NUMBER: _ClassVar[int]
        RIGHT_FIELD_NUMBER: _ClassVar[int]
        TOTALAMOUNT_FIELD_NUMBER: _ClassVar[int]
        TOTALVOLUME_FIELD_NUMBER: _ClassVar[int]
        TOTALOPENINT_FIELD_NUMBER: _ClassVar[int]
        VOLUMETOOPENINT_FIELD_NUMBER: _ClassVar[int]
        LATESTPRICE_FIELD_NUMBER: _ClassVar[int]
        UPDATETIME_FIELD_NUMBER: _ClassVar[int]
        symbol: str
        expiry: str
        strike: str
        right: str
        totalAmount: float
        totalVolume: float
        totalOpenInt: float
        volumeToOpenInt: float
        latestPrice: float
        updateTime: int
        def __init__(self, symbol: _Optional[str] = ..., expiry: _Optional[str] = ..., strike: _Optional[str] = ..., right: _Optional[str] = ..., totalAmount: _Optional[float] = ..., totalVolume: _Optional[float] = ..., totalOpenInt: _Optional[float] = ..., volumeToOpenInt: _Optional[float] = ..., latestPrice: _Optional[float] = ..., updateTime: _Optional[int] = ...) -> None: ...
    MARKET_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOPDATA_FIELD_NUMBER: _ClassVar[int]
    market: str
    timestamp: int
    topData: _containers.RepeatedCompositeFieldContainer[OptionTopData.TopData]
    def __init__(self, market: _Optional[str] = ..., timestamp: _Optional[int] = ..., topData: _Optional[_Iterable[_Union[OptionTopData.TopData, _Mapping]]] = ...) -> None: ...
