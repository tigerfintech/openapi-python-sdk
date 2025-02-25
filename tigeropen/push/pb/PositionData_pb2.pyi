from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PositionData(_message.Message):
    __slots__ = ("account", "symbol", "expiry", "strike", "right", "identifier", "multiplier", "market", "currency", "segType", "secType", "position", "positionScale", "averageCost", "latestPrice", "marketValue", "unrealizedPnl", "name", "timestamp", "saleable", "positionQty", "salableQty")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    STRIKE_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    SEGTYPE_FIELD_NUMBER: _ClassVar[int]
    SECTYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    POSITIONSCALE_FIELD_NUMBER: _ClassVar[int]
    AVERAGECOST_FIELD_NUMBER: _ClassVar[int]
    LATESTPRICE_FIELD_NUMBER: _ClassVar[int]
    MARKETVALUE_FIELD_NUMBER: _ClassVar[int]
    UNREALIZEDPNL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SALEABLE_FIELD_NUMBER: _ClassVar[int]
    POSITIONQTY_FIELD_NUMBER: _ClassVar[int]
    SALABLEQTY_FIELD_NUMBER: _ClassVar[int]
    account: str
    symbol: str
    expiry: str
    strike: str
    right: str
    identifier: str
    multiplier: int
    market: str
    currency: str
    segType: str
    secType: str
    position: int
    positionScale: int
    averageCost: float
    latestPrice: float
    marketValue: float
    unrealizedPnl: float
    name: str
    timestamp: int
    saleable: int
    positionQty: float
    salableQty: float
    def __init__(self, account: _Optional[str] = ..., symbol: _Optional[str] = ..., expiry: _Optional[str] = ..., strike: _Optional[str] = ..., right: _Optional[str] = ..., identifier: _Optional[str] = ..., multiplier: _Optional[int] = ..., market: _Optional[str] = ..., currency: _Optional[str] = ..., segType: _Optional[str] = ..., secType: _Optional[str] = ..., position: _Optional[int] = ..., positionScale: _Optional[int] = ..., averageCost: _Optional[float] = ..., latestPrice: _Optional[float] = ..., marketValue: _Optional[float] = ..., unrealizedPnl: _Optional[float] = ..., name: _Optional[str] = ..., timestamp: _Optional[int] = ..., saleable: _Optional[int] = ..., positionQty: _Optional[float] = ..., salableQty: _Optional[float] = ...) -> None: ...
