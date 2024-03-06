from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TickData(_message.Message):
    __slots__ = ["source", "symbol", "ticks", "timestamp"]
    class Tick(_message.Message):
        __slots__ = ["cond", "partCode", "price", "sn", "time", "type", "volume"]
        COND_FIELD_NUMBER: _ClassVar[int]
        PARTCODE_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        SN_FIELD_NUMBER: _ClassVar[int]
        TIME_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        VOLUME_FIELD_NUMBER: _ClassVar[int]
        cond: str
        partCode: str
        price: float
        sn: int
        time: int
        type: str
        volume: int
        def __init__(self, sn: _Optional[int] = ..., time: _Optional[int] = ..., price: _Optional[float] = ..., volume: _Optional[int] = ..., type: _Optional[str] = ..., cond: _Optional[str] = ..., partCode: _Optional[str] = ...) -> None: ...
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TICKS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    source: str
    symbol: str
    ticks: _containers.RepeatedCompositeFieldContainer[TickData.Tick]
    timestamp: int
    def __init__(self, symbol: _Optional[str] = ..., ticks: _Optional[_Iterable[_Union[TickData.Tick, _Mapping]]] = ..., timestamp: _Optional[int] = ..., source: _Optional[str] = ...) -> None: ...
