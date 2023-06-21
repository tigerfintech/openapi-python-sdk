from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class SocketCommon(_message.Message):
    __slots__ = []
    class Command(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class QuoteType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ALL: SocketCommon.QuoteType
    Asset: SocketCommon.DataType
    BASIC: SocketCommon.QuoteType
    BBO: SocketCommon.QuoteType
    CONNECT: SocketCommon.Command
    CONNECTED: SocketCommon.Command
    DISCONNECT: SocketCommon.Command
    ERROR: SocketCommon.Command
    Future: SocketCommon.DataType
    HEARTBEAT: SocketCommon.Command
    MESSAGE: SocketCommon.Command
    None: SocketCommon.QuoteType
    Option: SocketCommon.DataType
    OptionTop: SocketCommon.DataType
    OrderStatus: SocketCommon.DataType
    OrderTransaction: SocketCommon.DataType
    Position: SocketCommon.DataType
    Quote: SocketCommon.DataType
    QuoteDepth: SocketCommon.DataType
    SEND: SocketCommon.Command
    SUBSCRIBE: SocketCommon.Command
    StockTop: SocketCommon.DataType
    TradeTick: SocketCommon.DataType
    UNKNOWN: SocketCommon.Command
    UNSUBSCRIBE: SocketCommon.Command
    Unknown: SocketCommon.DataType
    def __init__(self) -> None: ...
