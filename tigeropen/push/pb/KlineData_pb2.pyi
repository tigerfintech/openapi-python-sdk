from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class KlineData(_message.Message):
    __slots__ = ["amount", "avg", "barTime", "close", "count", "high", "low", "open", "serverTimestamp", "symbol", "volume"]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AVG_FIELD_NUMBER: _ClassVar[int]
    BARTIME_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    SERVERTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    amount: float
    avg: float
    barTime: int
    close: float
    count: int
    high: float
    low: float
    open: float
    serverTimestamp: int
    symbol: str
    volume: int
    def __init__(self, barTime: _Optional[int] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., avg: _Optional[float] = ..., volume: _Optional[int] = ..., count: _Optional[int] = ..., symbol: _Optional[str] = ..., amount: _Optional[float] = ..., serverTimestamp: _Optional[int] = ...) -> None: ...
