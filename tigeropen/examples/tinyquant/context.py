from tigeropen.common.consts import SecurityType, Currency


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

    def subscribe(self, symbols, security_type=SecurityType.STK, currency=Currency.USD, exchange=None):
        if not (isinstance(symbols, list) or isinstance(symbols, set)):
            symbols = [symbols]
        for symbol in symbols:
            self.subscribed_symbols.add(symbol)
            self.security_type_map[symbol] = security_type
            self.currency_map[symbol] = currency


global_context = Context()
