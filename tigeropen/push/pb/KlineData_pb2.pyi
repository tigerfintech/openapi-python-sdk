from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class KlineData(_message.Message):
    __slots__ = ("time", "open", "high", "low", "close", "avg", "volume", "count", "symbol", "amount", "serverTimestamp")
    TIME_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    AVG_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SERVERTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    time: int
    open: float
    high: float
    low: float
    close: float
    avg: float
    volume: int
    count: int
    symbol: str
    amount: float
    serverTimestamp: int
    def __init__(self, time: _Optional[int] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., avg: _Optional[float] = ..., volume: _Optional[int] = ..., count: _Optional[int] = ..., symbol: _Optional[str] = ..., amount: _Optional[float] = ..., serverTimestamp: _Optional[int] = ...) -> None: ...
