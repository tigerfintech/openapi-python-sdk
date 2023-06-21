from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OrderStatusData(_message.Message):
    __slots__ = ["account", "action", "attrDesc", "avgFillPrice", "canCancel", "canModify", "cancelStatus", "commissionAndFee", "currency", "errorMsg", "expiry", "filledQuantity", "filledQuantityScale", "id", "identifier", "isLong", "limitPrice", "liquidation", "market", "multiplier", "name", "openTime", "orderType", "outsideRth", "realizedPnl", "replaceStatus", "right", "secType", "segType", "source", "status", "stopPrice", "strike", "symbol", "timestamp", "totalQuantity", "totalQuantityScale", "userMark"]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    ATTRDESC_FIELD_NUMBER: _ClassVar[int]
    AVGFILLPRICE_FIELD_NUMBER: _ClassVar[int]
    CANCANCEL_FIELD_NUMBER: _ClassVar[int]
    CANCELSTATUS_FIELD_NUMBER: _ClassVar[int]
    CANMODIFY_FIELD_NUMBER: _ClassVar[int]
    COMMISSIONANDFEE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    ERRORMSG_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    FILLEDQUANTITYSCALE_FIELD_NUMBER: _ClassVar[int]
    FILLEDQUANTITY_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ISLONG_FIELD_NUMBER: _ClassVar[int]
    LIMITPRICE_FIELD_NUMBER: _ClassVar[int]
    LIQUIDATION_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPENTIME_FIELD_NUMBER: _ClassVar[int]
    ORDERTYPE_FIELD_NUMBER: _ClassVar[int]
    OUTSIDERTH_FIELD_NUMBER: _ClassVar[int]
    REALIZEDPNL_FIELD_NUMBER: _ClassVar[int]
    REPLACESTATUS_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    SECTYPE_FIELD_NUMBER: _ClassVar[int]
    SEGTYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STOPPRICE_FIELD_NUMBER: _ClassVar[int]
    STRIKE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOTALQUANTITYSCALE_FIELD_NUMBER: _ClassVar[int]
    TOTALQUANTITY_FIELD_NUMBER: _ClassVar[int]
    USERMARK_FIELD_NUMBER: _ClassVar[int]
    account: str
    action: str
    attrDesc: str
    avgFillPrice: float
    canCancel: bool
    canModify: bool
    cancelStatus: str
    commissionAndFee: float
    currency: str
    errorMsg: str
    expiry: str
    filledQuantity: int
    filledQuantityScale: int
    id: int
    identifier: str
    isLong: bool
    limitPrice: float
    liquidation: bool
    market: str
    multiplier: int
    name: str
    openTime: int
    orderType: str
    outsideRth: bool
    realizedPnl: float
    replaceStatus: str
    right: str
    secType: str
    segType: str
    source: str
    status: str
    stopPrice: float
    strike: str
    symbol: str
    timestamp: int
    totalQuantity: int
    totalQuantityScale: int
    userMark: str
    def __init__(self, id: _Optional[int] = ..., account: _Optional[str] = ..., symbol: _Optional[str] = ..., expiry: _Optional[str] = ..., strike: _Optional[str] = ..., right: _Optional[str] = ..., identifier: _Optional[str] = ..., multiplier: _Optional[int] = ..., action: _Optional[str] = ..., market: _Optional[str] = ..., currency: _Optional[str] = ..., segType: _Optional[str] = ..., secType: _Optional[str] = ..., orderType: _Optional[str] = ..., isLong: bool = ..., totalQuantity: _Optional[int] = ..., totalQuantityScale: _Optional[int] = ..., filledQuantity: _Optional[int] = ..., filledQuantityScale: _Optional[int] = ..., avgFillPrice: _Optional[float] = ..., limitPrice: _Optional[float] = ..., stopPrice: _Optional[float] = ..., realizedPnl: _Optional[float] = ..., status: _Optional[str] = ..., replaceStatus: _Optional[str] = ..., cancelStatus: _Optional[str] = ..., outsideRth: bool = ..., canModify: bool = ..., canCancel: bool = ..., liquidation: bool = ..., name: _Optional[str] = ..., source: _Optional[str] = ..., errorMsg: _Optional[str] = ..., attrDesc: _Optional[str] = ..., commissionAndFee: _Optional[float] = ..., openTime: _Optional[int] = ..., timestamp: _Optional[int] = ..., userMark: _Optional[str] = ...) -> None: ...