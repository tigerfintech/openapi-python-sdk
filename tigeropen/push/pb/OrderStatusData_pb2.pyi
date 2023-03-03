from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OrderStatusData(_message.Message):
    __slots__ = ["account", "action", "avgFillPrice", "canCancel", "canModify", "commissionAndFee", "currency", "errorMsg", "filledQuantity", "filledQuantityScale", "id", "identifier", "isLong", "limitPrice", "market", "multiplier", "name", "openTime", "orderType", "outsideRth", "realizedPnl", "secType", "segType", "source", "status", "symbol", "timestamp", "totalQuantity", "totalQuantityScale"]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    AVGFILLPRICE_FIELD_NUMBER: _ClassVar[int]
    CANCANCEL_FIELD_NUMBER: _ClassVar[int]
    CANMODIFY_FIELD_NUMBER: _ClassVar[int]
    COMMISSIONANDFEE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    ERRORMSG_FIELD_NUMBER: _ClassVar[int]
    FILLEDQUANTITYSCALE_FIELD_NUMBER: _ClassVar[int]
    FILLEDQUANTITY_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ISLONG_FIELD_NUMBER: _ClassVar[int]
    LIMITPRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPENTIME_FIELD_NUMBER: _ClassVar[int]
    ORDERTYPE_FIELD_NUMBER: _ClassVar[int]
    OUTSIDERTH_FIELD_NUMBER: _ClassVar[int]
    REALIZEDPNL_FIELD_NUMBER: _ClassVar[int]
    SECTYPE_FIELD_NUMBER: _ClassVar[int]
    SEGTYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOTALQUANTITYSCALE_FIELD_NUMBER: _ClassVar[int]
    TOTALQUANTITY_FIELD_NUMBER: _ClassVar[int]
    account: str
    action: str
    avgFillPrice: float
    canCancel: bool
    canModify: bool
    commissionAndFee: float
    currency: str
    errorMsg: str
    filledQuantity: int
    filledQuantityScale: int
    id: int
    identifier: str
    isLong: bool
    limitPrice: float
    market: str
    multiplier: int
    name: str
    openTime: int
    orderType: str
    outsideRth: bool
    realizedPnl: float
    secType: str
    segType: str
    source: str
    status: str
    symbol: str
    timestamp: int
    totalQuantity: int
    totalQuantityScale: int
    def __init__(self, id: _Optional[int] = ..., account: _Optional[str] = ..., symbol: _Optional[str] = ..., identifier: _Optional[str] = ..., multiplier: _Optional[int] = ..., action: _Optional[str] = ..., market: _Optional[str] = ..., currency: _Optional[str] = ..., segType: _Optional[str] = ..., secType: _Optional[str] = ..., orderType: _Optional[str] = ..., isLong: bool = ..., totalQuantity: _Optional[int] = ..., totalQuantityScale: _Optional[int] = ..., filledQuantity: _Optional[int] = ..., filledQuantityScale: _Optional[int] = ..., avgFillPrice: _Optional[float] = ..., limitPrice: _Optional[float] = ..., realizedPnl: _Optional[float] = ..., status: _Optional[str] = ..., outsideRth: bool = ..., canModify: bool = ..., canCancel: bool = ..., name: _Optional[str] = ..., source: _Optional[str] = ..., errorMsg: _Optional[str] = ..., commissionAndFee: _Optional[float] = ..., openTime: _Optional[int] = ..., timestamp: _Optional[int] = ...) -> None: ...
