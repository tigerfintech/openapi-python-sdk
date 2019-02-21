"""
provide compatibility for tiger quant platform strategies.
"""
from .context import global_context
from .setting import MARKET
from logbook import Logger
log = Logger('engine')


def symbol(symbol_str, currency=MARKET.CURRENCY, security_type='STK', exchange=None):
    """
    :param symbol_str: 证券类型, 默认股票
    :param security_type: 非股票需要指定security_type
    :param currency: 非美股symbol需要制定currency
    :param exchange:
    :return:
    """
    global_context.subscribe(symbol_str.upper(), currency=currency, security_type=security_type, exchange=exchange)
    return symbol_str


def symbols(*args, currency=MARKET.CURRENCY, security_type='STK', exchange=None):
    for sym in list(*args):
        symbol(sym, currency=currency, security_type=security_type, exchange=exchange)
    return list(*args)


def record(**kwargs):
    pass


def set_benchmark(symbol):
    pass


def schedule_function(func, date_rule, time_rule):
    pass

