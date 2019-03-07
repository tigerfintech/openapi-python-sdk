from .compatibility import *
from .order_methods import *


def initialize(context):
    symbol_set = symbols('AAPL', 'BABA')


def on_ticker(context, symbol_str, items, hour_trading):
    print(f'{symbol_str}, {items}')


def before_trading_start(context, data):
    pass


def dump(context):
    pass
