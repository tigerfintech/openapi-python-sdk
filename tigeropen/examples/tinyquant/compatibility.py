"""
provide compatibility for tiger quant platform strategies.
"""
from .context import global_context
from logbook import Logger
log = Logger(__name__)


def symbol(symbol_str, currency='USD', security_type='STK', exchange=None):
    """
    :param symbol_str: 证券类型, 默认股票
    :param security_type: 非股票需要指定security_type
    :param currency: 非美股symbol需要制定currency
    :param exchange:
    :return:
    """
    global_context.subscribe(symbol_str, currency=currency, security_type=security_type, exchange=exchange)
    return symbol_str


def symbols(*args, currency='USD', security_type='STK', exchange=None):
    for sym in list(*args):
        global_context.subscribe(sym, currency=currency, security_type=security_type, exchange=exchange)
    return list(*args)


def record(**kwargs):
    pass


def schedule_function(func, date_rule, time_rule):
    pass


def set_benchmark(symbol):
    pass
