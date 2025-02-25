from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class SocketCommon(_message.Message):
    __slots__ = ()
    class Command(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[SocketCommon.Command]
        CONNECT: _ClassVar[SocketCommon.Command]
        CONNECTED: _ClassVar[SocketCommon.Command]
        SEND: _ClassVar[SocketCommon.Command]
        SUBSCRIBE: _ClassVar[SocketCommon.Command]
        UNSUBSCRIBE: _ClassVar[SocketCommon.Command]
        DISCONNECT: _ClassVar[SocketCommon.Command]
        MESSAGE: _ClassVar[SocketCommon.Command]
        HEARTBEAT: _ClassVar[SocketCommon.Command]
        ERROR: _ClassVar[SocketCommon.Command]
    UNKNOWN: SocketCommon.Command
    CONNECT: SocketCommon.Command
    CONNECTED: SocketCommon.Command
    SEND: SocketCommon.Command
    SUBSCRIBE: SocketCommon.Command
    UNSUBSCRIBE: SocketCommon.Command
    DISCONNECT: SocketCommon.Command
    MESSAGE: SocketCommon.Command
    HEARTBEAT: SocketCommon.Command
    ERROR: SocketCommon.Command
    class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Unknown: _ClassVar[SocketCommon.DataType]
        Quote: _ClassVar[SocketCommon.DataType]
        Option: _ClassVar[SocketCommon.DataType]
        Future: _ClassVar[SocketCommon.DataType]
        QuoteDepth: _ClassVar[SocketCommon.DataType]
        TradeTick: _ClassVar[SocketCommon.DataType]
        Asset: _ClassVar[SocketCommon.DataType]
        Position: _ClassVar[SocketCommon.DataType]
        OrderStatus: _ClassVar[SocketCommon.DataType]
        OrderTransaction: _ClassVar[SocketCommon.DataType]
        StockTop: _ClassVar[SocketCommon.DataType]
        OptionTop: _ClassVar[SocketCommon.DataType]
        Kline: _ClassVar[SocketCommon.DataType]
    Unknown: SocketCommon.DataType
    Quote: SocketCommon.DataType
    Option: SocketCommon.DataType
    Future: SocketCommon.DataType
    QuoteDepth: SocketCommon.DataType
    TradeTick: SocketCommon.DataType
    Asset: SocketCommon.DataType
    Position: SocketCommon.DataType
    OrderStatus: SocketCommon.DataType
    OrderTransaction: SocketCommon.DataType
    StockTop: SocketCommon.DataType
    OptionTop: SocketCommon.DataType
    Kline: SocketCommon.DataType
    class QuoteType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        None: _ClassVar[SocketCommon.QuoteType]
        BASIC: _ClassVar[SocketCommon.QuoteType]
        BBO: _ClassVar[SocketCommon.QuoteType]
        ALL: _ClassVar[SocketCommon.QuoteType]
    None: SocketCommon.QuoteType
    BASIC: SocketCommon.QuoteType
    BBO: SocketCommon.QuoteType
    ALL: SocketCommon.QuoteType
    def __init__(self) -> None: ...
