from tigeropen.push.pb import SocketCommon_pb2 as _SocketCommon_pb2
from tigeropen.push.pb import OrderStatusData_pb2 as _OrderStatusData_pb2
from tigeropen.push.pb import PositionData_pb2 as _PositionData_pb2
from tigeropen.push.pb import AssetData_pb2 as _AssetData_pb2
from tigeropen.push.pb import QuoteData_pb2 as _QuoteData_pb2
from tigeropen.push.pb import QuoteDepthData_pb2 as _QuoteDepthData_pb2
from tigeropen.push.pb import TradeTickData_pb2 as _TradeTickData_pb2
from tigeropen.push.pb import OrderTransactionData_pb2 as _OrderTransactionData_pb2
from tigeropen.push.pb import StockTopData_pb2 as _StockTopData_pb2
from tigeropen.push.pb import OptionTopData_pb2 as _OptionTopData_pb2
from tigeropen.push.pb import KlineData_pb2 as _KlineData_pb2
from tigeropen.push.pb import TickData_pb2 as _TickData_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon as SocketCommon
from tigeropen.push.pb.OrderStatusData_pb2 import OrderStatusData as OrderStatusData
from tigeropen.push.pb.PositionData_pb2 import PositionData as PositionData
from tigeropen.push.pb.AssetData_pb2 import AssetData as AssetData
from tigeropen.push.pb.QuoteData_pb2 import QuoteData as QuoteData
from tigeropen.push.pb.QuoteDepthData_pb2 import QuoteDepthData as QuoteDepthData
from tigeropen.push.pb.TradeTickData_pb2 import TradeTickData as TradeTickData
from tigeropen.push.pb.OrderTransactionData_pb2 import OrderTransactionData as OrderTransactionData
from tigeropen.push.pb.StockTopData_pb2 import StockTopData as StockTopData
from tigeropen.push.pb.OptionTopData_pb2 import OptionTopData as OptionTopData
from tigeropen.push.pb.KlineData_pb2 import KlineData as KlineData
from tigeropen.push.pb.TickData_pb2 import TickData as TickData

DESCRIPTOR: _descriptor.FileDescriptor

class PushData(_message.Message):
    __slots__ = ("dataType", "quoteData", "quoteDepthData", "tradeTickData", "positionData", "assetData", "orderStatusData", "orderTransactionData", "stockTopData", "optionTopData", "klineData", "tickData")
    DATATYPE_FIELD_NUMBER: _ClassVar[int]
    QUOTEDATA_FIELD_NUMBER: _ClassVar[int]
    QUOTEDEPTHDATA_FIELD_NUMBER: _ClassVar[int]
    TRADETICKDATA_FIELD_NUMBER: _ClassVar[int]
    POSITIONDATA_FIELD_NUMBER: _ClassVar[int]
    ASSETDATA_FIELD_NUMBER: _ClassVar[int]
    ORDERSTATUSDATA_FIELD_NUMBER: _ClassVar[int]
    ORDERTRANSACTIONDATA_FIELD_NUMBER: _ClassVar[int]
    STOCKTOPDATA_FIELD_NUMBER: _ClassVar[int]
    OPTIONTOPDATA_FIELD_NUMBER: _ClassVar[int]
    KLINEDATA_FIELD_NUMBER: _ClassVar[int]
    TICKDATA_FIELD_NUMBER: _ClassVar[int]
    dataType: _SocketCommon_pb2.SocketCommon.DataType
    quoteData: _QuoteData_pb2.QuoteData
    quoteDepthData: _QuoteDepthData_pb2.QuoteDepthData
    tradeTickData: _TradeTickData_pb2.TradeTickData
    positionData: _PositionData_pb2.PositionData
    assetData: _AssetData_pb2.AssetData
    orderStatusData: _OrderStatusData_pb2.OrderStatusData
    orderTransactionData: _OrderTransactionData_pb2.OrderTransactionData
    stockTopData: _StockTopData_pb2.StockTopData
    optionTopData: _OptionTopData_pb2.OptionTopData
    klineData: _KlineData_pb2.KlineData
    tickData: _TickData_pb2.TickData
    def __init__(self, dataType: _Optional[_Union[_SocketCommon_pb2.SocketCommon.DataType, str]] = ..., quoteData: _Optional[_Union[_QuoteData_pb2.QuoteData, _Mapping]] = ..., quoteDepthData: _Optional[_Union[_QuoteDepthData_pb2.QuoteDepthData, _Mapping]] = ..., tradeTickData: _Optional[_Union[_TradeTickData_pb2.TradeTickData, _Mapping]] = ..., positionData: _Optional[_Union[_PositionData_pb2.PositionData, _Mapping]] = ..., assetData: _Optional[_Union[_AssetData_pb2.AssetData, _Mapping]] = ..., orderStatusData: _Optional[_Union[_OrderStatusData_pb2.OrderStatusData, _Mapping]] = ..., orderTransactionData: _Optional[_Union[_OrderTransactionData_pb2.OrderTransactionData, _Mapping]] = ..., stockTopData: _Optional[_Union[_StockTopData_pb2.StockTopData, _Mapping]] = ..., optionTopData: _Optional[_Union[_OptionTopData_pb2.OptionTopData, _Mapping]] = ..., klineData: _Optional[_Union[_KlineData_pb2.KlineData, _Mapping]] = ..., tickData: _Optional[_Union[_TickData_pb2.TickData, _Mapping]] = ...) -> None: ...
