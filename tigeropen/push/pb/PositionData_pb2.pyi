from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PositionData(_message.Message):
    __slots__ = ["account", "averageCost", "currency", "expiry", "identifier", "latestPrice", "market", "marketValue", "multiplier", "name", "position", "positionScale", "right", "saleable", "secType", "segType", "strike", "symbol", "timestamp", "unrealizedPnl"]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    AVERAGECOST_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    LATESTPRICE_FIELD_NUMBER: _ClassVar[int]
    MARKETVALUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POSITIONSCALE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    SALEABLE_FIELD_NUMBER: _ClassVar[int]
    SECTYPE_FIELD_NUMBER: _ClassVar[int]
    SEGTYPE_FIELD_NUMBER: _ClassVar[int]
    STRIKE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    UNREALIZEDPNL_FIELD_NUMBER: _ClassVar[int]
    account: str
    averageCost: float
    currency: str
    expiry: str
    identifier: str
    latestPrice: float
    market: str
    marketValue: float
    multiplier: int
    name: str
    position: int
    positionScale: int
    right: str
    saleable: int
    secType: str
    segType: str
    strike: str
    symbol: str
    timestamp: int
    unrealizedPnl: float
    def __init__(self, account: _Optional[str] = ..., symbol: _Optional[str] = ..., expiry: _Optional[str] = ..., strike: _Optional[str] = ..., right: _Optional[str] = ..., identifier: _Optional[str] = ..., multiplier: _Optional[int] = ..., market: _Optional[str] = ..., currency: _Optional[str] = ..., segType: _Optional[str] = ..., secType: _Optional[str] = ..., position: _Optional[int] = ..., positionScale: _Optional[int] = ..., averageCost: _Optional[float] = ..., latestPrice: _Optional[float] = ..., marketValue: _Optional[float] = ..., unrealizedPnl: _Optional[float] = ..., name: _Optional[str] = ..., timestamp: _Optional[int] = ..., saleable: _Optional[int] = ...) -> None: ...
