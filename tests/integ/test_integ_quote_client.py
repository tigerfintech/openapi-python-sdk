# -*- coding: utf-8 -*-
"""Integration tests - require real API credentials."""
import logging
import unittest

import pandas as pd
import pytest

from tigeropen.common.consts import Market, TradingSession, BarPeriod, CapitalPeriod, Valuation, Income, \
    OptionAnalysisPeriod, SortDirection
from tigeropen.common.consts.filter_fields import StockField, FinancialPeriod
from tigeropen.quote.domain.filter import StockFilter, SortFilterData, OptionFilter
from tigeropen.quote.domain.quote_brief import QuoteBrief
from tigeropen.quote.domain.option_analysis import OptionAnalysis
from tigeropen.quote.domain.capital_distribution import CapitalDistribution
from tigeropen.quote.domain.addon_entitlement import AddonEntitlement
from tigeropen.quote.domain.stock_broker import StockBroker
from tigeropen.quote.domain.filter import ScannerResult
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
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], str)
        self.assertTrue(len(result[0]) > 0)
        logger.debug(f"Symbols count: {len(result)}")

    def test_get_market_status(self):
        result = self.client.get_market_status(market=Market.US)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        item = result[0]
        self.assertIsNotNone(item.market)
        self.assertIsNotNone(item.status)
        self.assertIsNotNone(item.trading_status)
        self.assertIsNotNone(item.open_time)
        logger.debug(f"Market Status: {result}")

    def test_get_symbol_names(self):
        result = self.client.get_symbol_names(market='US')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, tuple)
        self.assertEqual(len(first), 2)
        self.assertTrue(len(first[0]) > 0)
        self.assertIsNotNone(first[1])
        logger.debug(f"Symbol Names count: {len(result)}")

    def test_get_trade_metas(self):
        result = self.client.get_trade_metas(symbols=['AAPL', 'MSFT'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('AAPL', result['symbol'].values)
        self.assertIn('MSFT', result['symbol'].values)
        self.assertIn('lot_size', result.columns)
        self.assertIn('min_tick', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['lot_size'], 0)
        self.assertGreater(first['min_tick'], 0)
        logger.debug(f"Trade Metas:\n {result}")

    def test_get_stock_briefs(self):
        result = self.client.get_stock_briefs(symbols=['AAPL'],
                                              include_hour_trading=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]['symbol'], 'AAPL')
        self.assertGreater(result.iloc[0]['latest_price'], 0)
        self.assertGreaterEqual(result.iloc[0]['volume'], 0)
        self.assertGreater(result.iloc[0]['high'], 0)
        self.assertGreater(result.iloc[0]['low'], 0)
        logger.debug(f"Stock Briefs:\n {result}")

    def test_get_briefs(self):
        result = self.client.get_briefs(symbols=['AAPL'],
                                        include_hour_trading=True,
                                        include_ask_bid=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        brief = result[0]
        self.assertIsInstance(brief, QuoteBrief)
        self.assertEqual(brief.symbol, 'AAPL')
        self.assertIsNotNone(brief.market)
        self.assertIsNotNone(brief.sec_type)
        self.assertGreater(brief.latest_price, 0)
        logger.debug(f"Briefs: {result}")

    def test_get_stock_delay_briefs(self):
        result = self.client.get_stock_delay_briefs(symbols=['AAPL'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0].symbol, 'AAPL')
        self.assertGreater(result.iloc[0].pre_close, 0)
        self.assertGreaterEqual(result.iloc[0].volume, 0)
        logger.debug(f"Stock Delay Briefs:\n {result}")

    def test_get_timeline(self):
        result = self.client.get_timeline(symbols=['AAPL'],
                                          # trade_session=TradingSession.OverNight
                                          )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Timeline (real):\n {result}")

    def test_get_timeline_history(self):
        result = self.client.get_timeline_history(symbols=['AAPL'],
                                                  date="2025-08-21",
                                                  trade_session=TradingSession.OverNight
                                                  )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['price'], 0)
        logger.debug(f"Timeline History (real):\n {result}")

    def test_get_bars(self):
        result = self.client.get_bars(symbols=['AAPL', 'MSFT'],
                                      period=BarPeriod.DAY,
                                      limit=10,
                                      page_token='',
                                      # trade_session=TradingSession.OverNight
                                      )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('high', result.columns)
        self.assertIn('low', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertIn(first['symbol'], ['AAPL', 'MSFT'])
        self.assertGreater(first['open'], 0)
        self.assertGreater(first['close'], 0)
        self.assertGreater(first['high'], 0)
        self.assertGreater(first['low'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Bars (real):\n {result}")

    def test_get_trade_ticks(self):
        result = self.client.get_trade_ticks(symbols=['AAPL'],
                                             # trade_session=TradingSession.OverNight
                                             )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Trade Ticks (real): \n {result}")

    def test_get_short_interest(self):
        result = self.client.get_short_interest(symbols=['AAPL'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        if not result.empty:
            self.assertEqual(result.iloc[0]['symbol'], 'AAPL')
            self.assertIn('short_interest', result.columns)
            self.assertGreaterEqual(result.iloc[0]['short_interest'], 0)
        logger.debug(f"Short Interest:\n {result}")

    def test_get_depth_quote(self):
        # 实际调用API
        result = self.client.get_depth_quote(symbols=['AAPL', 'MSFT'],
                                             market=Market.US,
                                             # trade_session=TradingSession.OverNight
                                             )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn('AAPL', result)
        aapl = result['AAPL']
        self.assertEqual(aapl['symbol'], 'AAPL')
        self.assertIsInstance(aapl['asks'], list)
        self.assertIsInstance(aapl['bids'], list)
        self.assertGreater(len(aapl['asks']), 0)
        self.assertGreater(len(aapl['bids']), 0)
        self.assertGreater(aapl['asks'][0][0], 0)
        self.assertGreater(aapl['bids'][0][0], 0)
        logger.debug(f"Depth Quote (real):\n {result}")

    def test_get_option_expirations(self):
        result = self.client.get_option_expirations(symbols=['AAPL'],
                                                    market=Market.US)  # todo hk stock
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('date', result.columns)
        self.assertIn('timestamp', result.columns)
        self.assertEqual(result.iloc[0]['symbol'], 'AAPL')
        self.assertIsNotNone(result.iloc[0]['date'])
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
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('identifier', result.columns)
        self.assertIn('strike', result.columns)
        self.assertIn('put_call', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertTrue(len(str(first['identifier']).strip()) > 0)
        self.assertIsNotNone(first['strike'])
        logger.debug(f"Option Chain (real):\n {result}")

    def test_get_option_brief(self):
        result = self.client.get_option_briefs(
            identifiers=['PDD 260121C00090000'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('identifier', result.columns)
        self.assertIn('symbol', result.columns)
        first = result.iloc[0]
        self.assertIn('PDD', str(first['identifier']))
        self.assertIsNotNone(first['symbol'])
        self.assertGreater(first['multiplier'], 0)
        logger.debug(f"Option Brief (real):\n {result}")

    def test_get_option_bars(self):
        # result = self.client.get_option_bars(
        #     identifiers=['AAPL 250815C00200000'], period=BarPeriod.DAY, limit=5)
        result = self.client.get_option_bars(
            identifiers=['TCH.HK250828C00590000'], period=BarPeriod.DAY, limit=5,
            end_time='2025-08-22', timezone='Asia/Hong_Kong'
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('identifier', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['identifier']).strip()) > 0)
        self.assertGreater(first['open'], 0)
        self.assertGreater(first['close'], 0)
        logger.debug(f"Option Bars (real):\n {result}")

    def test_get_option_trade_ticks(self):
        result = self.client.get_option_trade_ticks(
            identifiers=['AAPL250829P00200000'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('identifier', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['identifier']).strip()) > 0)
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Option Trade Ticks (real):\n {result}")

    def test_get_option_symbols(self):
        result = self.client.get_option_symbols(market=Market.HK)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('name', result.columns)
        self.assertIn('underlying_symbol', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['symbol']).strip()) > 0)
        self.assertIsNotNone(first['name'])
        logger.debug(f"Option Symbols (real):\n {result}")

    def test_get_option_depth(self):
        result = self.client.get_option_depth(identifiers=['AAPL 250815C00210000', 'AAPL 250815P00200000'],
                                              market=Market.US)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)
        for key, val in result.items():
            self.assertIn('asks', val)
            self.assertIn('bids', val)
            self.assertIsInstance(val['asks'], list)
            self.assertIsInstance(val['bids'], list)
            self.assertGreater(len(val['asks']), 0)
            self.assertGreater(len(val['bids']), 0)
            self.assertGreater(val['asks'][0][0], 0)
            self.assertGreater(val['bids'][0][0], 0)
        logger.debug(f"Option Depth (real): {result}")

    def test_get_option_timeline(self):
        result = self.client.get_option_timeline(identifiers=['TCH.HK 250828C00610000'], market=Market.HK)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('identifier', result.columns)
        self.assertIn('symbol', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('time', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['symbol']).strip()) > 0)
        self.assertGreaterEqual(first['price'], 0)
        logger.debug(f"Option Timeline (real):\n {result}")

    def test_get_option_analysis(self):
        # Real API tests
        result = self.client.get_option_analysis(
            symbols=['AAPL', 'TSLA'],
            period=OptionAnalysisPeriod.FIFTY_TWO_WEEK,
            market=Market.US
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        first = result[0]
        self.assertIsInstance(first, OptionAnalysis)
        self.assertIn(first.symbol, ['AAPL', 'TSLA'])
        self.assertGreater(first.implied_vol_30_days, 0)
        self.assertGreater(first.his_volatility, 0)
        self.assertIsNotNone(first.iv_his_v_ratio)
        self.assertIsNotNone(first.call_put_ratio)
        self.assertIsNotNone(first.iv_metric)
        self.assertIsNotNone(first.iv_metric.period)
        logger.debug(f"Option Analysis (real):\n {result}")

    def test_get_future_exchanges(self):
        result = self.client.get_future_exchanges()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('code', result.columns)
        self.assertIn('name', result.columns)
        self.assertIn('zone', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['code']).strip()) > 0)
        self.assertIsNotNone(first['name'])
        self.assertIsNotNone(first['zone'])
        logger.debug(f"Future Exchanges (real):\n {result}")

    def test_get_future_contracts(self):
        result = self.client.get_future_contracts(exchange='CME')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('contract_code', result.columns)
        self.assertIn('type', result.columns)
        self.assertIn('name', result.columns)
        self.assertIn('multiplier', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['contract_code']).strip()) > 0)
        self.assertIsNotNone(first['name'])
        self.assertGreater(first['multiplier'], 0)
        logger.debug(f"Future Contracts (real):\n {result}")

    def test_get_future_contract(self):
        result = self.client.get_future_contract(contract_code='CLmain')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        row = result.iloc[0]
        self.assertEqual(row['contract_code'], 'CLmain')
        self.assertGreater(row['multiplier'], 0)
        self.assertGreater(row['min_tick'], 0)
        self.assertIsNotNone(row['currency'])
        self.assertIsNotNone(row['exchange'])
        logger.debug(f"Future Contract (real):\n {result}")

    def test_get_future_continuous_contracts(self):
        result = self.client.get_future_continuous_contracts(future_type='CL')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('contract_code', result.columns)
        self.assertIn('type', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['type'], 'CL')
        self.assertTrue(len(str(first['contract_code']).strip()) > 0)
        logger.debug(f"Future Continuous Contracts (real):\n {result}")

    def test_get_current_future_contract(self):
        result = self.client.get_current_future_contract(future_type='ES')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        row = result.iloc[0]
        self.assertEqual(row['type'], 'ES')
        self.assertTrue(len(str(row['contract_code']).strip()) > 0)
        self.assertGreater(row['multiplier'], 0)
        self.assertGreater(row['min_tick'], 0)
        logger.debug(f"Future Current Contract (real):\n {result}")

    def test_get_future_history_main_contract(self):
        result = self.client.get_future_history_main_contract(identifiers=['CLmain'],
                                                              begin_time=1755035100000,
                                                              end_time=1765035100000)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('contract_code', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('refer_contract_code', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['contract_code'], 'CLmain')
        self.assertIsNotNone(first['time'])
        self.assertTrue(len(str(first['refer_contract_code']).strip()) > 0)
        logger.debug(f"Future History Main Contract (real):\n {result}")

    def test_get_all_future_contracts(self):
        result = self.client.get_all_future_contracts(future_type='ES')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('contract_code', result.columns)
        self.assertIn('type', result.columns)
        for _, row in result.iterrows():
            self.assertEqual(row['type'], 'ES')
            self.assertTrue(len(str(row['contract_code']).strip()) > 0)
        logger.debug(f"All Future Contracts (real):\n {result}")

    def test_get_future_trading_times(self):
        result = self.client.get_future_trading_times(identifier='CL2609')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('start', result.columns)
        self.assertIn('end', result.columns)
        self.assertIn('trading', result.columns)
        self.assertIn('bidding', result.columns)
        first = result.iloc[0]
        self.assertIsNotNone(first['start'])
        self.assertIsNotNone(first['end'])
        logger.debug(f"Future Trading Times: \n {result}")

    def test_get_future_bars(self):
        result = self.client.get_future_bars(identifiers=['CL2609'],
                                             period='day', limit=5)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('identifier', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['identifier'], 'CL2609')
        self.assertGreater(first['open'], 0)
        self.assertGreater(first['close'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Future Bars: \n{result}")

    def test_get_future_trade_ticks(self):
        result = self.client.get_future_trade_ticks(identifier='CL2509')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('identifier', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['identifier'], 'CL2509')
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Future Ticks:\n {result}")

    def test_get_future_brief(self):
        result = self.client.get_future_brief(identifiers=['ES2509'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('identifier', result.columns)
        self.assertIn('latest_price', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['identifier'], 'ES2509')
        self.assertGreater(first['latest_price'], 0)
        logger.debug(f"Future Brief: \n {result}")

    def test_get_future_depth(self):
        result = self.client.get_future_depth(identifiers=['ES2509', 'ES2512'])
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn('ES2509', result)
        es = result['ES2509']
        self.assertEqual(es['identifier'], 'ES2509')
        self.assertIsInstance(es['asks'], list)
        self.assertIsInstance(es['bids'], list)
        self.assertGreater(len(es['asks']), 0)
        self.assertGreater(len(es['bids']), 0)
        self.assertGreater(es['asks'][0][0], 0)
        self.assertGreater(es['bids'][0][0], 0)
        logger.debug(f"Future Depth: \n {result}")

    def test_get_trading_calendar(self):
        result = self.client.get_trading_calendar(market='US')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, dict)
        self.assertIn('date', first)
        self.assertIn('type', first)
        self.assertTrue(len(str(first['date']).strip()) > 0)
        self.assertIsNotNone(first['type'])
        logger.debug(f"Trading Calendar:\n {result}")

    def test_get_stock_broker(self):
        # 实际调用API
        result = self.client.get_stock_broker(symbol='00700')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StockBroker)
        self.assertEqual(result.symbol, '00700')
        has_data = (result.bid_broker and len(result.bid_broker) > 0) or \
                   (result.ask_broker and len(result.ask_broker) > 0)
        self.assertTrue(has_data, "Should have bid_broker or ask_broker data")
        if result.bid_broker and len(result.bid_broker) > 0:
            first_bid = result.bid_broker[0]
            self.assertGreaterEqual(first_bid.level, 1)
            self.assertGreater(first_bid.price, 0)
        if result.ask_broker and len(result.ask_broker) > 0:
            first_ask = result.ask_broker[0]
            self.assertGreaterEqual(first_ask.level, 1)
            self.assertGreater(first_ask.price, 0)
        logger.debug(f"Stock Broker (real):\n {result}")

    def test_get_broker_hold(self):
        result = self.client.get_broker_hold()
        self.assertIsInstance(result, pd.DataFrame)
        if not result.empty:
            self.assertIn('org_id', result.columns)
            self.assertIn('org_name', result.columns)
            self.assertIn('date', result.columns)
            first = result.iloc[0]
            self.assertTrue(len(str(first['org_id']).strip()) > 0)
            self.assertIsNotNone(first['org_name'])
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
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ScannerResult)
        self.assertIsNotNone(result.page)
        self.assertIsNotNone(result.total_count)
        self.assertGreaterEqual(len(result.items), 1)
        first = result.items[0]
        self.assertTrue(len(str(first.symbol).strip()) > 0)
        self.assertIsNotNone(first.market)
        logger.debug(f"Market Scanner (real): {result}")

    def test_get_corporate_split(self):
        # 实际调用API
        result = self.client.get_corporate_split(symbols=['UVXY'],
                                                 market='US',
                                                 begin_date="2024-01-01",
                                                 end_date="2024-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        self.assertIn('from_factor', result.columns)
        self.assertIn('to_factor', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'UVXY')
        self.assertEqual(first['action_type'], 'SPLIT')
        self.assertGreater(first['from_factor'], 0)
        self.assertGreater(first['to_factor'], 0)
        logger.debug(f"Corporate Action Split:\n {result}")

    def test_get_corporate_symbol_change(self):
        result = self.client.get_corporate_symbol_change(symbols=['X', 'TWTR'],
                                                         market='US',
                                                         begin_date="2020-01-01",
                                                         end_date="2025-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        self.assertIn('old_symbol', result.columns)
        self.assertIn('new_symbol', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['action_type'], 'SYMBOL_CHANGE')
        self.assertTrue(len(str(first['old_symbol']).strip()) > 0)
        self.assertTrue(len(str(first['new_symbol']).strip()) > 0)
        logger.debug(f"Corporate Symbol Change:\n {result}")

    def test_get_corporate_delisting(self):
        result = self.client.get_corporate_delisting(symbols=['TWTR', 'GME'],
                                                     market='US',
                                                     begin_date="2018-01-01",
                                                     end_date="2025-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['action_type'], 'DELISTING')
        self.assertTrue(len(str(first['symbol']).strip()) > 0)
        logger.debug(f"Corporate Delisting:\n {result}")

    def test_get_corporate_ipo(self):
        result = self.client.get_corporate_ipo(symbols=['RIVN', 'ABNB', 'COIN'],
                                               market='US',
                                               begin_date="2018-01-01",
                                               end_date="2025-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        self.assertIn('ipo_name', result.columns)
        self.assertIn('listing_price', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['action_type'], 'IPO')
        self.assertTrue(len(str(first['ipo_name']).strip()) > 0)
        self.assertGreater(first['listing_price'], 0)
        logger.debug(f"Corporate IPO:\n {result}")

    def test_get_financial_daily(self):
        # 实际调用API
        result = self.client.get_financial_daily(
            symbols=['AAPL'],
            market='US',
            fields=[Valuation.shares_outstanding],
            begin_date="2023-01-01",
            end_date="2023-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('field', result.columns)
        self.assertIn('date', result.columns)
        self.assertIn('value', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertEqual(first['field'], 'shares_outstanding')
        self.assertGreater(first['value'], 0)
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
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertEqual(first['field'], 'net_income')
        self.assertIsNotNone(first['currency'])
        self.assertTrue(len(str(first['value']).strip()) > 0)
        self.assertIsNotNone(first['period_end_date'])

    def test_get_industry_list(self):
        result = self.client.get_industry_list()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, dict)
        self.assertIn('id', first)
        self.assertIn('name_en', first)
        self.assertTrue(len(str(first['id']).strip()) > 0)
        self.assertIsNotNone(first['name_en'])
        logger.debug(f"Industry List: {result}")

    def test_get_capital_flow(self):
        result = self.client.get_capital_flow(symbol="AAPL",
                                              market='US',
                                              period=CapitalPeriod.DAY)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('time', result.columns)
        self.assertIn('net_inflow', result.columns)
        self.assertIn('symbol', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertIsNotNone(first['net_inflow'])
        logger.debug(f"Capital Flow: \n{result}")

    def test_get_capital_distribution(self):
        result = self.client.get_capital_distribution(symbol="AAPL", market='US')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CapitalDistribution)
        self.assertEqual(result.symbol, 'AAPL')
        self.assertIsNotNone(result.net_inflow)
        self.assertGreaterEqual(result.in_all, 0)
        self.assertGreaterEqual(result.out_all, 0)
        logger.debug(f"Capital Distribution:\n {result}")

    def test_get_kline_quota(self):
        result = self.client.get_kline_quota()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, dict)
        self.assertIn('remain', first)
        self.assertIn('used', first)
        self.assertIn('method', first)
        self.assertIsNotNone(first['method'])
        logger.debug(f"Kline Quota:\n {result}")

    def test_get_addon_entitlement(self):
        result = self.client.get_addon_entitlement()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, AddonEntitlement)
        self.assertIsNotNone(result.user_level)
        self.assertIsNotNone(result.active_plan)
        self.assertIsNotNone(result.effective_entitlement)
        logger.debug(f"Addon Entitlement:\n {result}")
