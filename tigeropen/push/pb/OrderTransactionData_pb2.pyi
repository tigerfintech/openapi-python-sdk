from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OrderTransactionData(_message.Message):
    __slots__ = ("id", "orderId", "account", "symbol", "identifier", "multiplier", "action", "market", "currency", "segType", "secType", "filledPrice", "filledQuantity", "createTime", "updateTime", "transactTime", "timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    SEGTYPE_FIELD_NUMBER: _ClassVar[int]
    SECTYPE_FIELD_NUMBER: _ClassVar[int]
    FILLEDPRICE_FIELD_NUMBER: _ClassVar[int]
    FILLEDQUANTITY_FIELD_NUMBER: _ClassVar[int]
    CREATETIME_FIELD_NUMBER: _ClassVar[int]
    UPDATETIME_FIELD_NUMBER: _ClassVar[int]
    TRANSACTTIME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: int
    orderId: int
    account: str
    symbol: str
    identifier: str
    multiplier: int
    action: str
    market: str
    currency: str
    segType: str
    secType: str
    filledPrice: float
    filledQuantity: int
    createTime: int
    updateTime: int
    transactTime: int
    timestamp: int
    def __init__(self, id: _Optional[int] = ..., orderId: _Optional[int] = ..., account: _Optional[str] = ..., symbol: _Optional[str] = ..., identifier: _Optional[str] = ..., multiplier: _Optional[int] = ..., action: _Optional[str] = ..., market: _Optional[str] = ..., currency: _Optional[str] = ..., segType: _Optional[str] = ..., secType: _Optional[str] = ..., filledPrice: _Optional[float] = ..., filledQuantity: _Optional[int] = ..., createTime: _Optional[int] = ..., updateTime: _Optional[int] = ..., transactTime: _Optional[int] = ..., timestamp: _Optional[int] = ...) -> None: ...
