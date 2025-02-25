from tigeropen.push.pb import SocketCommon_pb2 as _SocketCommon_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon as SocketCommon

DESCRIPTOR: _descriptor.FileDescriptor

class QuoteBBOData(_message.Message):
    __slots__ = ("symbol", "type", "timestamp", "askPrice", "askSize", "askTimestamp", "bidPrice", "bidSize", "bidTimestamp")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ASKPRICE_FIELD_NUMBER: _ClassVar[int]
    ASKSIZE_FIELD_NUMBER: _ClassVar[int]
    ASKTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    BIDPRICE_FIELD_NUMBER: _ClassVar[int]
    BIDSIZE_FIELD_NUMBER: _ClassVar[int]
    BIDTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    type: _SocketCommon_pb2.SocketCommon.QuoteType
    timestamp: int
    askPrice: float
    askSize: int
    askTimestamp: int
    bidPrice: float
    bidSize: int
    bidTimestamp: int
    def __init__(self, symbol: _Optional[str] = ..., type: _Optional[_Union[_SocketCommon_pb2.SocketCommon.QuoteType, str]] = ..., timestamp: _Optional[int] = ..., askPrice: _Optional[float] = ..., askSize: _Optional[int] = ..., askTimestamp: _Optional[int] = ..., bidPrice: _Optional[float] = ..., bidSize: _Optional[int] = ..., bidTimestamp: _Optional[int] = ...) -> None: ...
