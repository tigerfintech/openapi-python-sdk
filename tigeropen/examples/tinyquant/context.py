import os
import pickle
from tigeropen.common.consts import SecurityType, Currency
from .setting import MARKET, CONTEXT_FILE_PATH

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
    Currency.HKD.name: Currency.HKD,  # 港币
    Currency.CNH.name: Currency.CNH,  # 离岸人民币
}


class Context:
    _store_exclude_list = ('account', 'asset_manager', 'position_manager', 'order_manager', 'active_order_manager',
                           'contract_map', 'security_type_map', 'currency_map', 'subscribed_symbols',
                           'schedule_function', 'portfolio')
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

    def load(self):
        if os.path.isfile(CONTEXT_FILE_PATH):
            with open(CONTEXT_FILE_PATH, 'rb') as f:
                try:
                    loaded_state = pickle.load(f)
                except (pickle.UnpicklingError, IndexError, EOFError):
                    raise ValueError("Bad context file: {}".format(CONTEXT_FILE_PATH))
                else:
                    for k, v in loaded_state.items():
                        setattr(self, k, v)

    def store(self):
        if CONTEXT_FILE_PATH:
            context = {}
            fields_to_store = list(set(self.__dict__.keys()) - set(self._store_exclude_list))

            for field in fields_to_store:
                context[field] = getattr(self, field)

            with open(CONTEXT_FILE_PATH, 'wb') as f:
                pickle.dump(context, f)


global_context = Context()
