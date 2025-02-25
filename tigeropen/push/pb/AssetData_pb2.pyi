from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AssetData(_message.Message):
    __slots__ = ("account", "currency", "segType", "availableFunds", "excessLiquidity", "netLiquidation", "equityWithLoan", "buyingPower", "cashBalance", "grossPositionValue", "initMarginReq", "maintMarginReq", "timestamp")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    SEGTYPE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLEFUNDS_FIELD_NUMBER: _ClassVar[int]
    EXCESSLIQUIDITY_FIELD_NUMBER: _ClassVar[int]
    NETLIQUIDATION_FIELD_NUMBER: _ClassVar[int]
    EQUITYWITHLOAN_FIELD_NUMBER: _ClassVar[int]
    BUYINGPOWER_FIELD_NUMBER: _ClassVar[int]
    CASHBALANCE_FIELD_NUMBER: _ClassVar[int]
    GROSSPOSITIONVALUE_FIELD_NUMBER: _ClassVar[int]
    INITMARGINREQ_FIELD_NUMBER: _ClassVar[int]
    MAINTMARGINREQ_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    account: str
    currency: str
    segType: str
    availableFunds: float
    excessLiquidity: float
    netLiquidation: float
    equityWithLoan: float
    buyingPower: float
    cashBalance: float
    grossPositionValue: float
    initMarginReq: float
    maintMarginReq: float
    timestamp: int
    def __init__(self, account: _Optional[str] = ..., currency: _Optional[str] = ..., segType: _Optional[str] = ..., availableFunds: _Optional[float] = ..., excessLiquidity: _Optional[float] = ..., netLiquidation: _Optional[float] = ..., equityWithLoan: _Optional[float] = ..., buyingPower: _Optional[float] = ..., cashBalance: _Optional[float] = ..., grossPositionValue: _Optional[float] = ..., initMarginReq: _Optional[float] = ..., maintMarginReq: _Optional[float] = ..., timestamp: _Optional[int] = ...) -> None: ...
