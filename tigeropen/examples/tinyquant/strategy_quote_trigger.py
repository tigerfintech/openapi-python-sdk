from tigeropen.examples.tinyquant.compatibility import symbols
from .compatibility import *
from .order_methods import *


def initialize(context):
    symbol_set = symbols('00700', '01810')


def on_ticker(context, symbol_str, items, hour_trading):
    print(f'{symbol_str}, {items}')


def before_trading_start(context, data):
    pass


def dump(context):
    pass
