"""
provide compatibility for tiger quant platform strategies.
"""
import pytz
from datetime import datetime, timedelta
from tigeropen.common.consts import BarPeriod
from .context import global_context
from .client import quote_client
from .setting import MARKET
import logbook
logbook.set_datetime_format("local")
log = logbook.Logger('engine')


def symbol(symbol_str, currency=MARKET.CURRENCY, security_type='STK', exchange=None):
    """
    :param symbol_str: 证券类型, 默认股票
    :param security_type: 非股票需要指定security_type
    :param currency: 非美股symbol需要指定currency
    :param exchange:
    :return:
    """
    global_context.subscribe(symbol_str.upper(), currency=currency, security_type=security_type, exchange=exchange)
    return symbol_str


def symbols(*args, currency=MARKET.CURRENCY, security_type='STK', exchange=None):
    for sym in list(args):
        symbol(sym, currency=currency, security_type=security_type, exchange=exchange)
    return list(args)


def record(**kwargs):
    pass


def set_benchmark(symbol):
    pass


def schedule_function(func, date_rule=None, time_rule=None):
    global_context.schedule_function = Schedule(func, date_rule, time_rule)


class Schedule:
    def __init__(self, func, date_rule=None, time_rule=None):
        self.func = func
        self.date_rule = date_rule
        self.time_rule = time_rule
        self.last_trade_date = self.get_last_trade_date()
        self.market_end_time = MARKET.CLOSE_TIME - timedelta(minutes=2)

    def get_last_trade_date(self):
        ms_timestamp = quote_client.get_bars(symbols=[MARKET.INDEX], period=BarPeriod.DAY, limit=1).time.iloc[0]
        return datetime.fromtimestamp(ms_timestamp // 1000, tz=pytz.timezone(MARKET.TIMEZONE))

    def run(self, data):
        curr_time = datetime.now(tz=pytz.timezone(MARKET.TIMEZONE))
        curr_clock = curr_time.replace(second=0).strftime('%H:%M:%S')
        if (self.date_rule == 'month_start' and self.last_trade_date.month != curr_time.month) or self.date_rule is None:
            if (self.time_rule == 'market_open' or self.time_rule is None) and curr_clock == MARKET.OPEN_TIME:
                self.func(global_context, data)
            elif self.time_rule == 'market_end' and curr_clock == self.market_end_time:
                self.func(global_context, data)
            elif self.time_rule == 'always':
                self.func(global_context, data)