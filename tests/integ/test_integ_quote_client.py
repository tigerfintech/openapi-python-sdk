# -*- coding: utf-8 -*-
"""Integration tests - require real API credentials.

Run with: TIGER_RUN_INTEG=true pytest tests/integ/ -v
"""
import logging
import unittest

import pytest

from tigeropen.quote.quote_client import QuoteClient
from tests.support import integ_client_config, is_integ_run

logger = logging.getLogger(__name__)


@pytest.mark.skipif(not is_integ_run(), reason="requires TIGER_RUN_INTEG=true")
class TestIntegQuoteClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client_config = integ_client_config()
        cls.client = QuoteClient(cls.client_config, logger=logger, is_grab_permission=False)

    def test_get_symbols(self):
        result = self.client.get_symbols(market='US')
        logger.debug(f"Symbols: {result}")

    def test_get_market_status(self):
        result = self.client.get_market_status(market=Market.US)
        logger.debug(f"Market Status: {result}")

    def test_get_symbol_names(self):
        result = self.client.get_symbol_names(market='US')
        logger.debug(f"Symbol Names: {result}")

    def test_get_trade_metas(self):
        result = self.client.get_trade_metas(symbols=['AAPL', 'MSFT'])
        logger.debug(f"Trade Metas:\n {result}")

    def test_get_stock_briefs(self):
        result = self.client.get_stock_briefs(symbols=['AAPL'],
                                              include_hour_trading=True)
        logger.debug(f"Stock Briefs:\n {result}")

    def test_get_briefs(self):
        result = self.client.get_briefs(symbols=['AAPL'],
                                        include_hour_trading=True,
                                        include_ask_bid=True)
        logger.debug(f"Briefs: {result}")

    def test_get_stock_delay_briefs(self):
        result = self.client.get_stock_delay_briefs(symbols=['AAPL'])
        logger.debug(f"Stock Delay Briefs:\n {result}")

    def test_get_timeline(self):
        result = self.client.get_timeline(symbols=['AAPL'],
                                          # trade_session=TradingSession.OverNight
                                          )
        logger.debug(f"Timeline (real):\n {result}")

    def test_get_timeline_history(self):
        result = self.client.get_timeline_history(symbols=['AAPL'],
                                                  date="2025-08-21",
                                                  trade_session=TradingSession.OverNight
                                                  )
        logger.debug(f"Timeline History (real):\n {result}")

    def test_get_bars(self):
        result = self.client.get_bars(symbols=['AAPL', 'MSFT'],
                                      period=BarPeriod.DAY,
                                      limit=10,
                                      page_token='',
                                      # trade_session=TradingSession.OverNight
                                      )
        logger.debug(f"Bars (real):\n {result}")

    def test_get_trade_ticks(self):
        result = self.client.get_trade_ticks(symbols=['AAPL'],
                                             # trade_session=TradingSession.OverNight
                                             )
        logger.debug(f"Trade Ticks (real): \n {result}")

    def test_get_short_interest(self):
        result = self.client.get_short_interest(symbols=['AAPL'])
        logger.debug(f"Short Interest:\n {result}")

    def test_get_depth_quote(self):
        # 实际调用API
        result = self.client.get_depth_quote(symbols=['AAPL', 'MSFT'],
                                             market=Market.US,
                                             # trade_session=TradingSession.OverNight
                                             )
        logger.debug(f"Depth Quote (real):\n {result}")

    def test_get_option_expirations(self):
        result = self.client.get_option_expirations(symbols=['AAPL'],
                                                    market=Market.US)  # todo hk stock
        logger.debug(f"Option Expirations (real):\n {result}")

    def test_get_option_chain(self):
        option_filter = OptionFilter(implied_volatility_min=0.05, implied_volatility_max=1, delta_min=0,
                                     delta_max=1,
                                     open_interest_min=10, open_interest_max=20000, in_the_money=True)
        result = self.client.get_option_chain(symbol='AAPL',
                                              expiry=1755230400000,
                                              market=Market.US,
                                              timezone='America/New_York',
                                              option_filter=option_filter,
                                              return_greek_value=True)
        logger.debug(f"Option Chain (real):\n {result}")

    def test_get_option_brief(self):
        result = self.client.get_option_briefs(
            identifiers=['PDD 260121C00090000'])
        logger.debug(f"Option Brief (real):\n {result}")

    def test_get_option_bars(self):
        # result = self.client.get_option_bars(
        #     identifiers=['AAPL 250815C00200000'], period=BarPeriod.DAY, limit=5)
        result = self.client.get_option_bars(
            identifiers=['TCH.HK250828C00590000'], period=BarPeriod.DAY, limit=5,
            end_time='2025-08-22', timezone='Asia/Hong_Kong'
        )
        logger.debug(f"Option Bars (real):\n {result}")

    def test_get_option_trade_ticks(self):
        result = self.client.get_option_trade_ticks(
            identifiers=['AAPL250829P00200000'])
        logger.debug(f"Option Trade Ticks (real):\n {result}")

    def test_get_option_symbols(self):
        result = self.client.get_option_symbols(market=Market.HK)
        logger.debug(f"Option Symbols (real):\n {result}")

    def test_get_option_depth(self):
        result = self.client.get_option_depth(identifiers=['AAPL 250815C00210000', 'AAPL 250815P00200000'],
                                              market=Market.US)
        logger.debug(f"Option Depth (real): {result}")

    def test_get_option_timeline(self):
        result = self.client.get_option_timeline(identifiers=['TCH.HK 250828C00610000'], market=Market.HK)
        logger.debug(f"Option Timeline (real):\n {result}")

    def test_get_option_analysis(self):
        # Real API tests
        result = self.client.get_option_analysis(
            symbols=['AAPL', 'TSLA'],
            period=OptionAnalysisPeriod.FIFTY_TWO_WEEK,
            market=Market.US
        )
        logger.debug(f"Option Analysis (real):\n {result}")

    def test_get_future_exchanges(self):
        result = self.client.get_future_exchanges()
        logger.debug(f"Future Exchanges (real):\n {result}")

    def test_get_future_contracts(self):
        result = self.client.get_future_contracts(exchange='CME')
        logger.debug(f"Future Contracts (real):\n {result}")

    def test_get_future_contract(self):
        result = self.client.get_future_contract(contract_code='CLmain')
        logger.debug(f"Future Contract (real):\n {result}")

    def test_get_future_continuous_contracts(self):
        result = self.client.get_future_continuous_contracts(future_type='CL')
        logger.debug(f"Future Continuous Contracts (real):\n {result}")

    def test_get_current_future_contract(self):
        result = self.client.get_current_future_contract(future_type='ES')
        logger.debug(f"Future Current Contract (real):\n {result}")

    def test_get_future_history_main_contract(self):
        result = self.client.get_future_history_main_contract(identifiers=['CLmain'],
                                                              begin_time=1755035100000,
                                                              end_time=1765035100000)
        logger.debug(f"Future History Main Contract (real):\n {result}")

    def test_get_all_future_contracts(self):
        result = self.client.get_all_future_contracts(future_type='ES')
        logger.debug(f"All Future Contracts (real):\n {result}")

    def test_get_future_trading_times(self):
        result = self.client.get_future_trading_times(identifier='CL2609')
        logger.debug(f"Future Trading Times: \n {result}")

    def test_get_future_bars(self):
        result = self.client.get_future_bars(identifiers=['CL2609'],
                                             period='day', limit=5)
        logger.debug(f"Future Bars: \n{result}")

    def test_get_future_trade_ticks(self):
        result = self.client.get_future_trade_ticks(identifier='CL2509')
        logger.debug(f"Future Ticks:\n {result}")

    def test_get_future_brief(self):
        result = self.client.get_future_brief(identifiers=['ES2509'])
        logger.debug(f"Future Brief: \n {result}")

    def test_get_future_depth(self):
        result = self.client.get_future_depth(identifiers=['ES2509', 'ES2512'])
        logger.debug(f"Future Depth: \n {result}")

    def test_get_trading_calendar(self):
        result = self.client.get_trading_calendar(market='US')
        logger.debug(f"Trading Calendar:\n {result}")

    def test_get_stock_broker(self):
        # 实际调用API
        result = self.client.get_stock_broker(symbol='00700')
        logger.debug(f"Stock Broker (real):\n {result}")

    def test_get_broker_hold(self):
        result = self.client.get_broker_hold()
        logger.debug(f"Broker Hold:\n {result}")

    def test_market_scanner(self):
        # 创建筛选条件和排序设置
        base_filter = StockFilter(StockField.current_ChangeRate,
                                  filter_min=0.01,
                                  filter_max=0.5)
        sort_field_data = SortFilterData(StockField.current_ChangeRate,
                                         sort_dir=SortDirection.DESC)
        page_size = 5
        # 调用市场扫描器方法
        result = self.client.market_scanner(
            market=Market.US,
            filters=[base_filter],
            sort_field_data=sort_field_data,
            page_size=page_size,

        )
        logger.debug(f"Market Scanner (real): {result}")

    def test_get_corporate_split(self):
        # 实际调用API
        result = self.client.get_corporate_split(symbols=['UVXY'],
                                                 market='US',
                                                 begin_date="2024-01-01",
                                                 end_date="2024-12-31")
        logger.debug(f"Corporate Action Split:\n {result}")

    def test_get_corporate_symbol_change(self):
        result = self.client.get_corporate_symbol_change(symbols=['X', 'TWTR'],
                                                         market='US',
                                                         begin_date="2020-01-01",
                                                         end_date="2025-12-31")
        logger.debug(f"Corporate Symbol Change:\n {result}")

    def test_get_corporate_delisting(self):
        result = self.client.get_corporate_delisting(symbols=['TWTR', 'GME'],
                                                     market='US',
                                                     begin_date="2018-01-01",
                                                     end_date="2025-12-31")
        logger.debug(f"Corporate Delisting:\n {result}")

    def test_get_corporate_ipo(self):
        result = self.client.get_corporate_ipo(symbols=['RIVN', 'ABNB', 'COIN'],
                                               market='US',
                                               begin_date="2018-01-01",
                                               end_date="2025-12-31")
        logger.debug(f"Corporate IPO:\n {result}")

    def test_get_financial_daily(self):
        # 实际调用API
        result = self.client.get_financial_daily(
            symbols=['AAPL'],
            market='US',
            fields=[Valuation.shares_outstanding],
            begin_date="2023-01-01",
            end_date="2023-12-31")
        logger.debug(f"Financial Daily:\n {result}")

    def test_get_financial_report(self):
        result = self.client.get_financial_report(
            symbols=['AAPL'],
            market='US',
            fields=[Income.net_income],
            period_type=FinancialPeriod.LTM,
            begin_date="2023-01-01",
            end_date="2023-12-31")
        logger.debug(f"Financial Report: \n {result}")

        # 验证真实API调用的基本结构
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Financial report data should not be empty")
        expected_columns = ['symbol', 'currency', 'field', 'value', 'period_end_date', 'filing_date']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"Expected column {col} not found in result")

    def test_get_industry_list(self):
        result = self.client.get_industry_list()
        logger.debug(f"Industry List: {result}")

    def test_get_capital_flow(self):
        result = self.client.get_capital_flow(symbol="AAPL",
                                              market='US',
                                              period=CapitalPeriod.DAY)
        logger.debug(f"Capital Flow: \n{result}")

    def test_get_capital_distribution(self):
        result = self.client.get_capital_distribution(symbol="AAPL", market='US')
        logger.debug(f"Capital Distribution: \n {result}")

    def test_get_kline_quota(self):
        result = self.client.get_kline_quota()
        logger.debug(f"Kline Quota:\n {result}")

    def test_get_addon_entitlement(self):
        result = self.client.get_addon_entitlement()
        logger.debug(f"Addon Entitlement:\n {result}")
