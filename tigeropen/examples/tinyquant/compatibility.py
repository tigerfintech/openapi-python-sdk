"""
provide compatibility for tiger quant platform strategies.
"""
from logbook import Logger
log = Logger(__name__)


def symbol(symbol_str):
    """
    :param symbol_str:
    :return: symbol_str
    """
    return symbol_str


def symbols(*args):
    """"""
    return list(*args)


def record(**kwargs):
    pass


def schedule_function(func, date_rule, time_rule):
    pass


def set_benchmark(symbol):
    pass
