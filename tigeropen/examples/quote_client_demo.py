# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import logging
import pandas as pd
from tigeropen.common.consts import Market, QuoteRight, FinancialReportPeriodType, Valuation, \
    Income, Balance, CashFlow, BalanceSheetRatio, Growth, Leverage, Profitability

from tigeropen.quote.quote_client import QuoteClient

from tigeropen.examples.client_config import get_client_config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a', )
logger = logging.getLogger('TigerOpenApi')

client_config = get_client_config()
openapi_client = QuoteClient(client_config, logger=logger)


def get_quote():
    market_status_list = openapi_client.get_market_status(Market.US)
    print(market_status_list)
    briefs = openapi_client.get_briefs(symbols=['AAPL', '00700', '600519'], include_ask_bid=True, right=QuoteRight.BR)
    print(briefs)
    briefs = openapi_client.get_stock_briefs(symbols=['AAPL', '00700', '600519'])
    print(briefs)
    metas = openapi_client.get_trade_metas(symbols=['00700'])
    print(metas)
    timelines = openapi_client.get_timeline(['AAPL'], include_hour_trading=True)
    print(timelines)
    bars = openapi_client.get_bars(['AAPL'])
    print(bars)
    ticks = openapi_client.get_trade_ticks(['00700'])
    print(ticks)
    short_interest = openapi_client.get_short_interest(['GOOG', 'AAPL', '00700'])
    print(short_interest)


def get_option_quote():
    symbol = 'AAPL'
    expirations = openapi_client.get_option_expirations(symbols=[symbol])
    if len(expirations) > 1:
        expiry = int(expirations[expirations['symbol'] == symbol].at[0, 'timestamp'])
        chains = openapi_client.get_option_chain(symbol, expiry)
        print(chains)

    briefs = openapi_client.get_option_briefs(['AAPL  190104C00121000'])
    print(briefs)
    bars = openapi_client.get_option_bars(['AAPL  190104P00134000'])
    print(bars)
    ticks = openapi_client.get_option_trade_ticks(['AAPL  190104P00134000'])
    print(ticks)


def get_future_quote():
    exchanges = openapi_client.get_future_exchanges()
    print(exchanges)
    bars = openapi_client.get_future_bars(['CN1901'], begin_time=-1, end_time=1545105097358)
    print(bars)
    ticks = openapi_client.get_future_trade_ticks(['CN1901'])
    print(ticks)
    contracts = openapi_client.get_future_contracts('CME')
    print(contracts)
    trading_times = openapi_client.get_future_trading_times('CN1901', trading_date=1545049282852)
    print(trading_times)
    briefs = openapi_client.get_future_brief(['ES1906', 'CN1901'])
    print(briefs)


def get_fundamental():
    """获取基础数据"""
    
    # 日级财务数据
    financial_daily = openapi_client.get_financial_daily(symbols=['AAPL', 'MSFT'],
                                                         market=Market.US,
                                                         fields=[Valuation.shares_outstanding],
                                                         begin_date='2019-01-01',
                                                         end_date='2019-01-10')
    print(financial_daily)
    
    # 财报数据(季报或年报)
    financial_report = openapi_client.get_financial_report(symbols=['AAPL', 'GOOG'],
                                                           market=Market.US,
                                                           fields=[Income.revenues, CashFlow.cash_from_investing],
                                                           period_type=FinancialReportPeriodType.ANNUAL)
    print(financial_report)

    # 拆合股数据
    corporate_split = openapi_client.get_corporate_split(symbols=['UVXY', 'TQQQ'],
                                                         market=Market.US,
                                                         begin_date='2017-01-01',
                                                         end_date='2019-01-01')
    print(corporate_split)

    # 派息数据
    corporate_dividend = openapi_client.get_corporate_dividend(symbols=['MSFT', 'AAPL'],
                                                               market=Market.US,
                                                               begin_date='2018-01-01',
                                                               end_date='2019-01-01')
    print(corporate_dividend)


if __name__ == '__main__':
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        get_quote()
        get_option_quote()
        get_future_quote()
        get_fundamental()
