from tigeropen.push.pb import SocketCommon_pb2 as _SocketCommon_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ["command", "connect", "id", "subscribe"]
    class Connect(_message.Message):
        __slots__ = ["acceptVersion", "receiveInterval", "sdkVersion", "sendInterval", "sign", "tigerId"]
        ACCEPTVERSION_FIELD_NUMBER: _ClassVar[int]
        RECEIVEINTERVAL_FIELD_NUMBER: _ClassVar[int]
        SDKVERSION_FIELD_NUMBER: _ClassVar[int]
        SENDINTERVAL_FIELD_NUMBER: _ClassVar[int]
        SIGN_FIELD_NUMBER: _ClassVar[int]
        TIGERID_FIELD_NUMBER: _ClassVar[int]
        acceptVersion: str
        receiveInterval: int
        sdkVersion: str
        sendInterval: int
        sign: str
        tigerId: str
        def __init__(self, tigerId: _Optional[str] = ..., sign: _Optional[str] = ..., sdkVersion: _Optional[str] = ..., acceptVersion: _Optional[str] = ..., sendInterval: _Optional[int] = ..., receiveInterval: _Optional[int] = ...) -> None: ...
    class Subscribe(_message.Message):
        __slots__ = ["account", "dataType", "market", "symbols"]
        ACCOUNT_FIELD_NUMBER: _ClassVar[int]
        DATATYPE_FIELD_NUMBER: _ClassVar[int]
        MARKET_FIELD_NUMBER: _ClassVar[int]
        SYMBOLS_FIELD_NUMBER: _ClassVar[int]
        account: str
        dataType: _SocketCommon_pb2.SocketCommon.DataType
        market: str
        symbols: str
        def __init__(self, dataType: _Optional[_Union[_SocketCommon_pb2.SocketCommon.DataType, str]] = ..., symbols: _Optional[str] = ..., account: _Optional[str] = ..., market: _Optional[str] = ...) -> None: ...
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    command: _SocketCommon_pb2.SocketCommon.Command
    connect: Request.Connect
    id: int
    subscribe: Request.Subscribe
    def __init__(self, command: _Optional[_Union[_SocketCommon_pb2.SocketCommon.Command, str]] = ..., id: _Optional[int] = ..., subscribe: _Optional[_Union[Request.Subscribe, _Mapping]] = ..., connect: _Optional[_Union[Request.Connect, _Mapping]] = ...) -> None: ...
