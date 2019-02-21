from tigeropen.common.consts import SecurityType, Currency
from .setting import MARKET

SECURITY_TYPE_MAP = {
    SecurityType.STK.name: SecurityType.STK,  # 股票
    SecurityType.OPT.name: SecurityType.OPT,  # 期权
    SecurityType.WAR.name: SecurityType.WAR,  # 窝轮
    SecurityType.IOPT.name: SecurityType.IOPT,  # 权证(牛熊证)
    SecurityType.FUT.name: SecurityType.FUT,  # 期货
    SecurityType.FOP.name: SecurityType.FOP,  # 期货期权
    SecurityType.CASH.name: SecurityType.CASH,  # 外汇
}
CURRENCY_MAP = {
    Currency.USD.name: Currency.USD,  # 美元
    Currency.HKD.name: Currency.HKD,  # 港毕
    Currency.CNH.name: Currency.CNH,  # 离岸人民币
}


class Context:
    def __init__(self):
        self.account = None
        self.asset_manager = None
        self.position_manager = None
        self.order_manager = None
        self.active_order_manager = None
        self.contract_map = {}
        self.security_type_map = {}
        self.currency_map = {}
        self.subscribed_symbols = set()

    def subscribe(self, symbols, currency=MARKET.CURRENCY, security_type='STK', exchange=None):
        if not (isinstance(symbols, list) or isinstance(symbols, set)):
            symbols = [symbols]
        for symbol in symbols:
            self.subscribed_symbols.add(symbol)
            self.security_type_map[symbol] = SECURITY_TYPE_MAP.get(security_type.upper())
            self.currency_map[symbol] = CURRENCY_MAP.get(currency.upper())


global_context = Context()
