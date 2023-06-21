from tigeropen.push.pb import SocketCommon_pb2 as _SocketCommon_pb2
from tigeropen.push.pb import PushData_pb2 as _PushData_pb2
from tigeropen.push.pb import SocketCommon_pb2 as _SocketCommon_pb2_1
from tigeropen.push.pb import OrderStatusData_pb2 as _OrderStatusData_pb2
from tigeropen.push.pb import PositionData_pb2 as _PositionData_pb2
from tigeropen.push.pb import AssetData_pb2 as _AssetData_pb2
from tigeropen.push.pb import QuoteData_pb2 as _QuoteData_pb2
from tigeropen.push.pb import QuoteDepthData_pb2 as _QuoteDepthData_pb2
from tigeropen.push.pb import TradeTickData_pb2 as _TradeTickData_pb2
from tigeropen.push.pb import OrderTransactionData_pb2 as _OrderTransactionData_pb2
from tigeropen.push.pb import StockTopData_pb2 as _StockTopData_pb2
from tigeropen.push.pb import OptionTopData_pb2 as _OptionTopData_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
from tigeropen.push.pb.PushData_pb2 import PushData
DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ["body", "code", "command", "id", "msg"]
    BODY_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    body: _PushData_pb2.PushData
    code: int
    command: _SocketCommon_pb2_1.SocketCommon.Command
    id: int
    msg: str
    def __init__(self, command: _Optional[_Union[_SocketCommon_pb2_1.SocketCommon.Command, str]] = ..., id: _Optional[int] = ..., code: _Optional[int] = ..., msg: _Optional[str] = ..., body: _Optional[_Union[_PushData_pb2.PushData, _Mapping]] = ...) -> None: ...
