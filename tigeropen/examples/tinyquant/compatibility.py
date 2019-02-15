"""
provide compatibility for tiger quant platform strategies.
"""
from .context import global_context, SecurityType, Currency
from logbook import Logger
log = Logger(__name__)

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


def symbol(symbol_str, sec_type=SecurityType.STK.name, currency=Currency.USD.name, exchange=None):
    """

    :param symbol_str: 证券类型, 默认股票
    :param sec_type: 非股票需要指定sec_type
    :param currency: 非美股symbol需要制定currency
    :param exchange:
    :return:
    """
    global_context.subscribe(symbol_str, security_type=SECURITY_TYPE_MAP.get(sec_type.upper()), currency=CURRENCY_MAP.get(currency.upper()), exchange=exchange)
    return symbol_str


def symbols(*args, sec_type=SecurityType.STK.name, currency=Currency.USD.name, exchange=None):
    for sym in list(*args):
        global_context.subscribe(sym, security_type=SECURITY_TYPE_MAP.get(sec_type.upper()),
                                 currency=CURRENCY_MAP.get(currency.upper()), exchange=exchange)
    return list(*args)


def record(**kwargs):
    pass


def schedule_function(func, date_rule, time_rule):
    pass


def set_benchmark(symbol):
    pass
