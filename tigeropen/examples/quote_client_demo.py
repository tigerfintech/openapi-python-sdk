# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import logging
import time

import pandas as pd
from tigeropen.common.consts import Market, QuoteRight, FinancialReportPeriodType, Valuation, \
    Income, Balance, CashFlow, BalanceSheetRatio, Growth, Leverage, Profitability, IndustryLevel, BarPeriod
from tigeropen.quote.domain.filter import OptionFilter

from tigeropen.quote.quote_client import QuoteClient

from tigeropen.examples.client_config import get_client_config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a', )
logger = logging.getLogger('TigerOpenApi')

client_config = get_client_config()
openapi_client = QuoteClient(client_config, logger=logger)


def get_quote():
    # 抢占行情权限
    quote_permissions = openapi_client.grab_quote_permission()
    print(quote_permissions)
    # 查询行情权限
    perms = openapi_client.get_quote_permission()
    print(perms)

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
    history_timelines = openapi_client.get_timeline_history(['AAPL'], date='2022-04-11')
    print(history_timelines)
    bars = openapi_client.get_bars(['AAPL'])
    print(bars)
    ticks = openapi_client.get_trade_ticks(['00700'])
    print(ticks)
    short_interest = openapi_client.get_short_interest(['GOOG', 'AAPL', '00700'])
    print(short_interest)
    # 获取深度行情
    order_book = openapi_client.get_depth_quote(['02828'], Market.HK)
    print(order_book)
    # 股票详情
    stock_details = openapi_client.get_stock_details(['AAPL', '03690'])
    print(stock_details)

    # 获取延迟行情
    delay_brief = openapi_client.get_stock_delay_briefs(['AAPL', 'GOOG'])
    print(delay_brief)


def test_gat_bars_by_page():
    bars = openapi_client.get_bars_by_page(['AAPL'], period=BarPeriod.DAY,
                                           end_time='2022-05-01',
                                           total=10,
                                           page_size=4,
                                           )
    bars['cn_date'] = pd.to_datetime(bars['time'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    bars['us_date'] = pd.to_datetime(bars['time'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    print(bars)


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

    # option chain filter
    option_filter = OptionFilter(implied_volatility_min=0.5, implied_volatility_max=0.9, delta_min=0, delta_max=1,
                                 open_interest_min=100, gamma_min=0.005, theta_max=-0.05, in_the_money=True)
    chains = openapi_client.get_option_chain('AAPL', '2023-01-20', option_filter=option_filter)
    print(chains)
    # or
    chains = openapi_client.get_option_chain('AAPL', '2023-01-20', implied_volatility_min=0.5, open_interest_min=200,
                                             vega_min=0.1, rho_max=0.9)
    # convert expiry date to US/Eastern
    chains['expiry_date'] = pd.to_datetime(chains['expiry'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(
        'US/Eastern')
    print(chains)


def get_future_quote():
    exchanges = openapi_client.get_future_exchanges()
    print(exchanges)
    bars = openapi_client.get_future_bars(['CN1901'], begin_time=-1, end_time=1545105097358)
    print(bars)
    ticks = openapi_client.get_future_trade_ticks(['CN1901'])
    print(ticks)
    contracts = openapi_client.get_future_contracts('CME')
    print(contracts)
    contract = openapi_client.get_future_contract('VIX2206')
    print(contract)
    trading_times = openapi_client.get_future_trading_times('CN1901', trading_date=1545049282852)
    print(trading_times)
    briefs = openapi_client.get_future_brief(['ES1906', 'CN1901'])
    print(briefs)


def test_get_future_bars_by_page():
    bars = openapi_client.get_future_bars_by_page('CLmain',
                                                  end_time=1648526400000,
                                                  total=10,
                                                  page_size=4)
    bars['cn_date'] = pd.to_datetime(bars['time'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    bars['us_date'] = pd.to_datetime(bars['time'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    print(bars)


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

    # 财报日历
    earnings_calendar = openapi_client.get_corporate_earnings_calendar(Market.US, '2020-01-01', '2020-02-01')
    print(earnings_calendar)

    # 行业数据
    # 获取行业列表
    industries = openapi_client.get_industry_list(IndustryLevel.GGROUP)
    print(industries)
    # 获取某行业下公司列表
    industry_stocks = openapi_client.get_industry_stocks(50101020)
    print(industry_stocks)
    # 获取某股票的行业
    stock_industry = openapi_client.get_stock_industry('AAPL', Market.US)
    print(stock_industry)


if __name__ == '__main__':
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        get_quote()
        get_option_quote()
        get_future_quote()
        get_fundamental()
