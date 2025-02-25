from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TradeTickData(_message.Message):
    __slots__ = ("symbol", "type", "cond", "sn", "priceBase", "priceOffset", "time", "price", "volume", "partCode", "quoteLevel", "timestamp", "secType", "mergedVols")
    class MergedVol(_message.Message):
        __slots__ = ("mergeTimes", "vol")
        MERGETIMES_FIELD_NUMBER: _ClassVar[int]
        VOL_FIELD_NUMBER: _ClassVar[int]
        mergeTimes: int
        vol: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, mergeTimes: _Optional[int] = ..., vol: _Optional[_Iterable[int]] = ...) -> None: ...
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COND_FIELD_NUMBER: _ClassVar[int]
    SN_FIELD_NUMBER: _ClassVar[int]
    PRICEBASE_FIELD_NUMBER: _ClassVar[int]
    PRICEOFFSET_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    PARTCODE_FIELD_NUMBER: _ClassVar[int]
    QUOTELEVEL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SECTYPE_FIELD_NUMBER: _ClassVar[int]
    MERGEDVOLS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    type: str
    cond: str
    sn: int
    priceBase: int
    priceOffset: int
    time: _containers.RepeatedScalarFieldContainer[int]
    price: _containers.RepeatedScalarFieldContainer[int]
    volume: _containers.RepeatedScalarFieldContainer[int]
    partCode: _containers.RepeatedScalarFieldContainer[str]
    quoteLevel: str
    timestamp: int
    secType: str
    mergedVols: _containers.RepeatedCompositeFieldContainer[TradeTickData.MergedVol]
    def __init__(self, symbol: _Optional[str] = ..., type: _Optional[str] = ..., cond: _Optional[str] = ..., sn: _Optional[int] = ..., priceBase: _Optional[int] = ..., priceOffset: _Optional[int] = ..., time: _Optional[_Iterable[int]] = ..., price: _Optional[_Iterable[int]] = ..., volume: _Optional[_Iterable[int]] = ..., partCode: _Optional[_Iterable[str]] = ..., quoteLevel: _Optional[str] = ..., timestamp: _Optional[int] = ..., secType: _Optional[str] = ..., mergedVols: _Optional[_Iterable[_Union[TradeTickData.MergedVol, _Mapping]]] = ...) -> None: ...
