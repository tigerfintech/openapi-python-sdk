import json
import logging
import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd

from tigeropen.common.consts import CapitalPeriod, Valuation, Income, Market, SortDirection, TradingSession, BarPeriod
from tigeropen.common.consts.filter_fields import FinancialPeriod, StockField
from tigeropen.common.util import web_utils
from tigeropen.quote.domain.filter import StockFilter, SortFilterData, OptionFilter
from tigeropen.quote.domain.quote_brief import QuoteBrief
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import TigerOpenClientConfig

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 5000)
pd.set_option('display.width', 5000)


class TestQuoteClient(unittest.TestCase):

    def setUp(self):
        self.is_mock = True
        current_dir = os.path.dirname(__file__)
        self.client_config = TigerOpenClientConfig(
            props_path=os.path.join(current_dir, ".config/prod_20150899/"))
        self.client: QuoteClient = QuoteClient(self.client_config,
                                               logger=logger,
                                               is_grab_permission=False)
        self.origin_do_request = web_utils.do_request

    def tearDown(self):
        web_utils.do_request = self.origin_do_request

    def test_get_symbols(self):
        if self.is_mock:
            mock_data = {
                "data": ["AAPL", "SPY"],
                "code": 0,
                "message": "success",
                "timestamp": 1753444350498
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_symbols(market='US')
            self.assertIn("AAPL", mock_result)
        else:
            result = self.client.get_symbols(market='US')
            logger.debug(f"Symbols: {result}")

    def test_get_market_status(self):
        if self.is_mock:
            mock_data = {
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1754978785570,
                "data": [{
                    "market": "US",
                    "marketStatus": "Not Yet Opened",
                    "status": "NOT_YET_OPEN",
                    "openTime": "08-12 09:30:00 EDT"
                }, {
                    "market": "HK",
                    "marketStatus": "Trading",
                    "status": "TRADING",
                    "openTime": "08-13 09:30:00"
                }, {
                    "market": "CN",
                    "marketStatus": "Trading",
                    "status": "TRADING",
                    "openTime": "08-13 09:30:00"
                }]
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_market_status()
            self.assertGreaterEqual(len(mock_result), 1)
            for item in mock_result:
                self.assertIn(item.market, ['US', 'HK', 'CN'])
                self.assertIn(item.status, ['Not Yet Opened', 'Trading'])
                self.assertIsNotNone(item.open_time)
                self.assertIn(item.trading_status, ['NOT_YET_OPEN', 'TRADING'])
                self.assertTrue(isinstance(item.open_time, datetime))
        else:
            result = self.client.get_market_status(market=Market.US)
            logger.debug(f"Market Status: {result}")

    def test_get_symbol_names(self):
        if self.is_mock:
            mock_data = {
                "data": [{
                    "symbol": "AAPL",
                    "name": "Apple Inc."
                }, {
                    "symbol": "MSFT",
                    "name": "Microsoft Corporation"
                }, {
                    "symbol": "GOOG",
                    "name": "Alphabet Inc."
                }],
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1753444350498
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_symbol_names(market='US')
            self.assertEqual(len(mock_result), 3)
            for item in mock_result:
                self.assertIn(item[0], ['AAPL', 'MSFT', 'GOOG'])
                self.assertIn(
                    item[1],
                    ['Apple Inc.', 'Microsoft Corporation', 'Alphabet Inc.'])
        else:
            result = self.client.get_symbol_names(market='US')
            logger.debug(f"Symbol Names: {result}")

    def test_get_trade_metas(self):
        if self.is_mock:
            mock_data = {
                "data": [{
                    "symbol": "AAPL",
                    "lotSize": 1,
                    "minTick": 0.01,
                    "spreadScale": 1
                }, {
                    "symbol": "MSFT",
                    "lotSize": 1,
                    "minTick": 0.01,
                    "spreadScale": 1
                }],
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1753444350498
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result: pd.DataFrame = self.client.get_trade_metas(
                symbols=['AAPL', 'MSFT'])
            self.assertEqual(mock_result.shape[0], 2)
            self.assertIn('AAPL', mock_result['symbol'].values)
            self.assertIn('MSFT', mock_result['symbol'].values)
            self.assertEqual(mock_result['lot_size'].iloc[0], 1)
            self.assertEqual(mock_result['min_tick'].iloc[0], 0.01)
        else:
            result = self.client.get_trade_metas(symbols=['AAPL', 'MSFT'])
            logger.debug(f"Trade Metas:\n {result}")

    def test_get_stock_briefs(self):
        if self.is_mock:
            mock_data = {
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1754987523451,
                "data": [{
                    "symbol": "AAPL",
                    "open": 227.92,
                    "high": 229.56,
                    "low": 224.76,
                    "close": 227.18,
                    "preClose": 229.09,
                    "latestPrice": 227.18,
                    "latestTime": 1754942400000,
                    "askPrice": 226.38,
                    "askSize": 363,
                    "bidPrice": 226.3,
                    "bidSize": 227,
                    "volume": 61806132,
                    "status": "NORMAL",
                    "hourTrading": {
                        "tag": "Pre-Mkt",
                        "latestPrice": 226.37,
                        "preClose": 227.18,
                        "latestTime": "04:31 EDT",
                        "volume": 5841,
                        "timestamp": 1754987488932
                    },
                    "adjPreClose": 227.18
                }]
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_stock_briefs(
                symbols=['AAPL'], include_hour_trading=True)
            self.assertEqual(mock_result.iloc[0]['symbol'], 'AAPL')
            self.assertEqual(mock_result.iloc[0]['open'], 227.92)
            self.assertEqual(mock_result.iloc[0]['high'], 229.56)
            self.assertEqual(mock_result.iloc[0]['low'], 224.76)
            self.assertEqual(mock_result.iloc[0]['close'], 227.18)
            self.assertEqual(mock_result.iloc[0]['pre_close'], 229.09)
            self.assertEqual(mock_result.iloc[0]['latest_price'], 227.18)
            self.assertEqual(mock_result.iloc[0]['latest_time'], 1754942400000)
            self.assertEqual(mock_result.iloc[0]['ask_price'], 226.38)
            self.assertEqual(mock_result.iloc[0]['ask_size'], 363)
            self.assertEqual(mock_result.iloc[0]['bid_price'], 226.3)
            self.assertEqual(mock_result.iloc[0]['bid_size'], 227)
            self.assertEqual(mock_result.iloc[0]['volume'], 61806132)
            self.assertEqual(mock_result.iloc[0]['status'], 'NORMAL')
            self.assertEqual(mock_result.iloc[0]['adj_pre_close'], 227.18)
            self.assertEqual(mock_result.iloc[0]['hour_trading_tag'],
                             'Pre-Mkt')
            self.assertEqual(mock_result.iloc[0]['hour_trading_latest_price'],
                             226.37)
            self.assertEqual(mock_result.iloc[0]['hour_trading_pre_close'],
                             227.18)
            self.assertEqual(mock_result.iloc[0]['hour_trading_latest_time'],
                             "04:31 EDT")
            self.assertEqual(mock_result.iloc[0]['hour_trading_volume'], 5841)
            self.assertEqual(mock_result.iloc[0]['hour_trading_timestamp'],
                             1754987488932)
        else:
            result = self.client.get_stock_briefs(symbols=['AAPL'],
                                                  include_hour_trading=True)
            logger.debug(f"Stock Briefs:\n {result}")

    def test_get_briefs(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1754983985719,
                "data": {
                    "items": [{
                        "symbol": "AAPL",
                        "market": "US",
                        "secType": "STK",
                        "name": "Apple",
                        "latestPrice": 227.18,
                        "timestamp": 1754942400000,
                        "preClose": 229.09,
                        "halted": 0.0,
                        "delay": 0,
                        "hourTrading": {
                            "tag": "盘后",
                            "latestPrice": 226.322,
                            "preClose": 227.18,
                            "latestTime": "19:59 EDT",
                            "volume": 2431140,
                            "timestamp": 1754956795127
                        }
                    }]
                }
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result: list[QuoteBrief] = self.client.get_briefs(
                symbols=['AAPL'],
                include_hour_trading=True,
                include_ask_bid=True)
            self.assertEqual(len(mock_result), 1)
            self.assertEqual(mock_result[0].symbol, 'AAPL')
            self.assertEqual(mock_result[0].market, "US")
            self.assertEqual(mock_result[0].sec_type, "STK")
            self.assertEqual(mock_result[0].latest_price, 227.18)
            self.assertEqual(mock_result[0].latest_time, 1754942400000)
            self.assertEqual(mock_result[0].prev_close, 229.09)
            self.assertEqual(mock_result[0].halted, 0.0)
            self.assertEqual(mock_result[0].delay, 0)
            self.assertEqual(mock_result[0].name, "Apple")
            self.assertEqual(mock_result[0].hour_trading.latest_price, 226.322)
            self.assertEqual(mock_result[0].hour_trading.latest_time,
                             1754956795127)
            self.assertEqual(mock_result[0].hour_trading.volume, 2431140)
            self.assertEqual(mock_result[0].hour_trading.prev_close, 227.18)
            self.assertEqual(mock_result[0].hour_trading.trading_session,
                             TradingSession.AfterHours)

        else:
            result = self.client.get_briefs(symbols=['AAPL'],
                                            include_hour_trading=True,
                                            include_ask_bid=True)
            logger.debug(f"Briefs: {result}")

    def test_get_stock_delay_briefs(self):
        if self.is_mock:
            mock_data = {
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1754988336588,
                "data": [{
                    "symbol": "AAPL",
                    "preClose": 229.09,
                    "halted": 0.0,
                    "time": 1754942400000,
                    "open": 227.92,
                    "high": 229.56,
                    "low": 224.76,
                    "close": 227.18,
                    "volume": 61806132
                }]
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_stock_delay_briefs(symbols=['AAPL'])
            self.assertEqual(len(mock_result), 1)
            self.assertEqual(mock_result.iloc[0].symbol, 'AAPL')
            self.assertEqual(mock_result.iloc[0].pre_close, 229.09)
            self.assertEqual(mock_result.iloc[0].halted, 0.0)
            self.assertEqual(mock_result.iloc[0].time, 1754942400000)
            self.assertEqual(mock_result.iloc[0].open, 227.92)
            self.assertEqual(mock_result.iloc[0].high, 229.56)
            self.assertEqual(mock_result.iloc[0].low, 224.76)
            self.assertEqual(mock_result.iloc[0].close, 227.18)
            self.assertEqual(mock_result.iloc[0].volume, 61806132)
        else:
            result = self.client.get_stock_delay_briefs(symbols=['AAPL'])
            logger.debug(f"Stock Delay Briefs:\n {result}")

    def test_get_timeline(self):
        if self.is_mock:
            mock_data = {
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1754988901893,
                "data": [{
                    "symbol": "AAPL",
                    "period": "day",
                    "preClose": 229.09,
                    "intraday": {
                        "items": [{"time": 1754919000000, "volume": 1656620, "price": 226.75, "avgPrice": 227.75438},
                                  {"time": 1754919060000, "volume": 426781, "price": 226.6, "avgPrice": 227.51157},
                                  {"time": 1754919120000, "volume": 267382, "price": 226.31, "avgPrice": 227.40694},
                                  {"time": 1754919180000, "volume": 322976, "price": 226.045, "avgPrice": 227.25978},
                                  {"time": 1754919240000, "volume": 229321, "price": 226.06, "avgPrice": 226.0}],
                        "beginTime":
                            -1,
                        "endTime":
                            1754942340000
                    }
                }]
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            result = self.client.get_timeline(symbols=['AAPL'])
            logger.debug(f"Timeline (mock):\n {result}")
            self.assertIsNotNone(result)
            self.assertFalse(result.empty)
            self.assertIn('symbol', result.columns)
            self.assertIn('time', result.columns)
            self.assertIn('price', result.columns)
            self.assertIn('avg_price', result.columns)
            self.assertIn('pre_close', result.columns)
            self.assertIn('volume', result.columns)
            self.assertIn('trading_session', result.columns)
            first_row = result.iloc[0]
            self.assertEqual(first_row['symbol'], 'AAPL')
            self.assertEqual(first_row['time'], 1754919000000)
            self.assertAlmostEqual(first_row['price'], 226.75, places=2)
            self.assertAlmostEqual(first_row['avg_price'], 227.75438, places=5)
            self.assertEqual(first_row['pre_close'], 229.09)
            self.assertEqual(first_row['volume'], 1656620)
            self.assertEqual(first_row['trading_session'], 'regular')
        else:
            result = self.client.get_timeline(symbols=['AAPL'],
                                              # trade_session=TradingSession.OverNight
                                              )
            logger.debug(f"Timeline (real):\n {result}")

    def test_get_timeline_history(self):
        if self.is_mock:
            mock_data = {
                "code": 0, "message": "success", "timestamp": 1754990360538, "data": [{"symbol": "AAPL", "items": [
                    {"time": 1698845400000, "volume": 654691, "price": 171.1, "avgPrice": 171.0484},
                    {"time": 1698845460000, "volume": 175598, "price": 170.595, "avgPrice": 171.01788},
                    {"time": 1698845520000, "volume": 186093, "price": 170.535, "avgPrice": 170.9575},
                    {"time": 1698845580000, "volume": 145550, "price": 170.2719, "avgPrice": 170.90828},
                    {"time": 1698845640000, "volume": 221063, "price": 170.41, "avgPrice": 170.82759}]}]
            }

            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            result = self.client.get_timeline_history(symbols=['AAPL'],
                                                      date="2023-11-01")
            logger.debug(f"Timeline History (mock):\n {result}")
            self.assertIsNotNone(result)
            self.assertFalse(result.empty)
            self.assertIn('symbol', result.columns)
            self.assertIn('time', result.columns)
            self.assertIn('price', result.columns)
            self.assertIn('avg_price', result.columns)
            self.assertIn('volume', result.columns)
            first_row = result.iloc[0]
            self.assertEqual(first_row['symbol'], 'AAPL')
            self.assertEqual(first_row['time'], 1698845400000)
            self.assertAlmostEqual(first_row['price'], 171.1, places=2)
            self.assertAlmostEqual(first_row['avg_price'], 171.0484, places=5)
            self.assertEqual(first_row['volume'], 654691)
        else:
            result = self.client.get_timeline_history(symbols=['AAPL'],
                                                      date="2025-08-21",
                                                      # trade_session=TradingSession.OverNight
                                                      )
            logger.debug(f"Timeline History (real):\n {result}")

    def test_get_bars(self):
        if self.is_mock:
            mock_data = {
                "code": 0, "message": "success", "timestamp": 1754990841014, "data": [
                    {"symbol": "AAPL", "period": "day", "items": [
                        {"time": 1754366400000, "volume": 44155079, "open": 203.4, "close": 202.92, "high": 205.34,
                         "low": 202.16, "amount": 8.987659222543882E9},
                        {"time": 1754452800000, "volume": 108483103, "open": 205.63, "close": 213.25, "high": 215.38,
                         "low": 205.59, "amount": 2.315468887474085E10},
                        {"time": 1754539200000, "volume": 90224834, "open": 218.875, "close": 220.03, "high": 220.85,
                         "low": 216.58, "amount": 1.9798494559887737E10},
                        {"time": 1754625600000, "volume": 113853967, "open": 220.83, "close": 229.35, "high": 231.0,
                         "low": 219.25, "amount": 2.589128470726625E10},
                        {"time": 1754884800000, "volume": 61806132, "open": 227.92, "close": 227.18, "high": 229.56,
                         "low": 224.76, "amount": 1.4164248430829714E10}]
                     }]
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_bars(symbols=['AAPL'],
                                               period=BarPeriod.DAY,
                                               limit=5)
            logger.debug(f"Bars (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 5)

            # 验证数据框架的列
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('time', mock_result.columns)
            self.assertIn('open', mock_result.columns)
            self.assertIn('high', mock_result.columns)
            self.assertIn('low', mock_result.columns)
            self.assertIn('close', mock_result.columns)
            self.assertIn('volume', mock_result.columns)
            self.assertIn('amount', mock_result.columns)
            self.assertIn('next_page_token', mock_result.columns)

            # 验证第一行数据
            first_row = mock_result.iloc[0]
            self.assertEqual(first_row['symbol'], 'AAPL')
            self.assertEqual(first_row['time'], 1754366400000)
            self.assertEqual(first_row['open'], 203.4)
            self.assertEqual(first_row['close'], 202.92)
            self.assertEqual(first_row['high'], 205.34)
            self.assertEqual(first_row['low'], 202.16)
            self.assertEqual(first_row['volume'], 44155079)
            self.assertAlmostEqual(first_row['amount'],
                                   8.987659222543882E9,
                                   delta=1E5)

            # 验证最后一行数据
            last_row = mock_result.iloc[4]
            self.assertEqual(last_row['symbol'], 'AAPL')
            self.assertEqual(last_row['time'], 1754884800000)
            self.assertEqual(last_row['open'], 227.92)
            self.assertEqual(last_row['close'], 227.18)
            self.assertEqual(last_row['high'], 229.56)
            self.assertEqual(last_row['low'], 224.76)
            self.assertEqual(last_row['volume'], 61806132)
        else:
            result = self.client.get_bars(symbols=['AAPL', 'MSFT'],
                                          period=BarPeriod.DAY,
                                          limit=10,
                                          page_token='',
                                          # trade_session=TradingSession.OverNight
                                          )
            logger.debug(f"Bars (real):\n {result}")

    def test_get_trade_ticks(self):
        if self.is_mock:
            mock_data = {
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1754991710630,
                "data": [{
                    "symbol": "AAPL", "beginIndex": 482299, "endIndex": 482499,
                    "items": [{"time": 1754942403109, "volume": 406, "price": 227.18, "type": "-"},
                              {"time": 1754942403109, "volume": 26215, "price": 227.18, "type": "-"},
                              {"time": 1754942403109, "volume": 884, "price": 227.18, "type": "-"},
                              {"time": 1754942403109, "volume": 200, "price": 227.18, "type": "-"}]
                }]
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_trade_ticks(symbols=['AAPL'])
            logger.debug(f"Trade Ticks (mock): \n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 4)  # 检查行数与mock数据中的items数量一致

            # 验证数据框架的列
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('time', mock_result.columns)
            self.assertIn('price', mock_result.columns)
            self.assertIn('volume', mock_result.columns)
            self.assertIn('direction', mock_result.columns)
            self.assertIn('index', mock_result.columns)

            # 验证第一行数据
            first_row = mock_result.iloc[0]
            self.assertEqual(first_row['symbol'], 'AAPL')
            self.assertEqual(first_row['time'], 1754942403109)
            self.assertEqual(first_row['price'], 227.18)
            self.assertEqual(first_row['volume'], 406)
            self.assertEqual(first_row['direction'], '-')
            self.assertEqual(first_row['index'], 482299)

            # 验证第二行数据
            second_row = mock_result.iloc[1]
            self.assertEqual(second_row['symbol'], 'AAPL')
            self.assertEqual(second_row['time'], 1754942403109)
            self.assertEqual(second_row['price'], 227.18)
            self.assertEqual(second_row['volume'], 26215)
            self.assertEqual(second_row['direction'], '-')
            self.assertEqual(second_row['index'], 482300)
        else:
            result = self.client.get_trade_ticks(symbols=['AAPL'],
                                                 # trade_session=TradingSession.OverNight
                                                 )
            logger.debug(f"Trade Ticks (real): \n {result}")

    def test_get_short_interest(self):
        if self.is_mock:
            mock_data = {}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

        else:
            result = self.client.get_short_interest(symbols=['AAPL'])
            logger.debug(f"Short Interest:\n {result}")

    def test_get_depth_quote(self):
        if self.is_mock:
            mock_data = {
                "code": 0, "message": "success", "timestamp": 1754992687363,
                "data": [
                    {"symbol": "AAPL", "asks": [{"price": 226.38, "count": 3, "volume": 363},
                                                {"price": 226.40, "count": 2, "volume": 500},
                                                {"price": 226.45, "count": 1, "volume": 200}],
                     "bids": [{"price": 226.30, "count": 5, "volume": 700},
                              {"price": 226.25, "count": 2, "volume": 300},
                              {"price": 226.20, "count": 1, "volume": 100}]
                     },
                    {"symbol": "MSFT", "asks": [{"price": 523.50, "count": 2, "volume": 200},
                                                {"price": 523.60, "count": 1, "volume": 100},
                                                {"price": 523.70, "count": 3, "volume": 300}],
                     "bids": [{"price": 523.25, "count": 1, "volume": 150},
                              {"price": 523.20, "count": 2, "volume": 200},
                              {"price": 523.10, "count": 4, "volume": 400}]
                     }]
            }
            mock_data_single = {
                "code": 0, "message": "success", "timestamp": 1754992687363,
                "data": [
                    {
                        "symbol": "AAPL",
                        "asks": [{"price": 226.38, "count": 3, "volume": 363},
                                 {"price": 226.40, "count": 2, "volume": 500},
                                 {"price": 226.45, "count": 1, "volume": 200}],
                        "bids": [{"price": 226.30, "count": 5, "volume": 700},
                                 {"price": 226.25, "count": 2, "volume": 300},
                                 {"price": 226.20, "count": 1, "volume": 100}]
                    }
                ]
            }

            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用 get_depth_quote 方法
            mock_result = self.client.get_depth_quote(symbols=['AAPL', 'MSFT'],
                                                      market=Market.US)
            logger.debug(f"Depth Quote (mock multi):\n {mock_result}")

            # 验证返回的数据结构
            self.assertIsNotNone(mock_result)
            self.assertEqual(len(mock_result), 2)  # 应该有两个股票的数据

            # 验证 AAPL 的数据
            self.assertIn('AAPL', mock_result)
            aapl_data = mock_result['AAPL']
            self.assertEqual(aapl_data['symbol'], 'AAPL')

            # 验证 AAPL 的 asks 数据
            self.assertIsNotNone(aapl_data['asks'])
            self.assertEqual(len(aapl_data['asks']), 3)
            # 验证第一个 ask
            self.assertEqual(aapl_data['asks'][0][0], 226.38)  # 价格
            self.assertEqual(aapl_data['asks'][0][1], 363)  # 数量
            self.assertEqual(aapl_data['asks'][0][2], 3)  # 订单数
            # 验证 AAPL 的 bids 数据
            self.assertIsNotNone(aapl_data['bids'])
            self.assertEqual(len(aapl_data['bids']), 3)
            # 验证第一个 bid
            self.assertEqual(aapl_data['bids'][0][0], 226.30)  # 价格
            self.assertEqual(aapl_data['bids'][0][1], 700)  # 数量
            self.assertEqual(aapl_data['bids'][0][2], 5)  # 订单数
            # 验证 MSFT 的数据
            self.assertIn('MSFT', mock_result)
            msft_data = mock_result['MSFT']
            self.assertEqual(msft_data['symbol'], 'MSFT')
            # 验证 MSFT 的 asks 数据
            self.assertEqual(len(msft_data['asks']), 3)
            self.assertEqual(msft_data['asks'][0][0], 523.50)  # 价格
            self.assertEqual(msft_data['asks'][0][1], 200)  # 数量
            self.assertEqual(msft_data['asks'][0][2], 2)  # 订单数
            # 验证 MSFT 的 bids 数据
            self.assertEqual(len(msft_data['bids']), 3)
            self.assertEqual(msft_data['bids'][0][0], 523.25)  # 价格
            self.assertEqual(msft_data['bids'][0][1], 150)  # 数量
            self.assertEqual(msft_data['bids'][0][2], 1)  # 订单数

            # 测试单个股票
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data_single).encode())
            mock_result = self.client.get_depth_quote(symbols=['AAPL'],
                                                      market=Market.US)
            logger.debug(f"Depth Quote (mock single):\n {mock_result}")
            self.assertEqual(mock_result['symbol'], 'AAPL')
            self.assertEqual(mock_result['asks'][0][0], 226.38)  # 价格
            self.assertEqual(mock_result['asks'][0][1], 363)  # 数量
            self.assertEqual(mock_result['asks'][0][2], 3)  # 订单数
            self.assertEqual(mock_result['bids'][0][0], 226.30)  # 价格
            self.assertEqual(mock_result['bids'][0][1], 700)  # 数量
            self.assertEqual(mock_result['bids'][0][2], 5)  # 订单数
        else:
            # 实际调用API
            result = self.client.get_depth_quote(symbols=['AAPL', 'MSFT'],
                                                 market=Market.US,
                                                 # trade_session=TradingSession.OverNight
                                                 )
            logger.debug(f"Depth Quote (real):\n {result}")

    def test_get_option_expirations(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1754998100471,
                         "data": [{"symbol": "AAPL",
                                   "optionSymbols": ["AAPL", "AAPL"],
                                   "dates": ["2025-08-15", "2025-08-22"],
                                   "timestamps": [1755230400000, 1755835200000],
                                   "periodTags": ["m", "w"],
                                   "count": 2}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_option_expirations(symbols=['AAPL'],
                                                             market=Market.US)
            logger.debug(f"Option Expirations (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 2)  # 应该有2行数据

            # 验证数据框架的列
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('option_symbol', mock_result.columns)
            self.assertIn('date', mock_result.columns)
            self.assertIn('timestamp', mock_result.columns)
            self.assertIn('period_tag', mock_result.columns)

            # 验证具体内容
            self.assertEqual(mock_result['symbol'].iloc[0], 'AAPL')
            self.assertEqual(mock_result['option_symbol'].iloc[0], 'AAPL')
            self.assertEqual(mock_result['date'].iloc[0], '2025-08-15')
            self.assertEqual(mock_result['timestamp'].iloc[0], 1755230400000)
            self.assertEqual(mock_result['period_tag'].iloc[0], 'm')

            # 验证第二行和第三行
            self.assertEqual(mock_result['date'].iloc[1], '2025-08-22')
            self.assertEqual(mock_result['period_tag'].iloc[1], 'w')
        else:
            result = self.client.get_option_expirations(symbols=['AAPL'],
                                                        market=Market.US)  # todo hk stock
            logger.debug(f"Option Expirations (real):\n {result}")

    def test_get_option_chain(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1754999649552,
                         "data": [
                             {"symbol": "AAPL",
                              "expiry": 1755230400000,
                              "items": [
                                  {
                                      "put": {"identifier": "AAPL  250815P00090000", "strike": "90.0", "right": "put",
                                              "askPrice": 0.01, "askSize": 750, "volume": 4, "latestPrice": 0.01,
                                              "preClose": 0.01, "openInterest": 1984, "multiplier": 100,
                                              "lastTimestamp": 1754927160721, "impliedVol": 2.81666, "delta": -5.14E-4,
                                              "gamma": 2.7E-5, "theta": -0.016986, "vega": 4.82E-4, "rho": -1.4E-5
                                              },
                                      "call": {"identifier": "AAPL  250815C00090000", "strike": "90.0", "right": "call",
                                               "bidPrice": 136.85, "bidSize": 67, "askPrice": 137.9, "askSize": 86,
                                               "volume": 10, "latestPrice": 137.62, "preClose": 140.35,
                                               "openInterest": 2, "multiplier": 100, "lastTimestamp": 1754940397131,
                                               "impliedVol": 3.65214, "delta": 0.995457, "gamma": 1.51E-4,
                                               "theta": -0.157473, "vega": 0.00359, "rho": 0.009734}
                                  }
                              ]
                              }
                         ]
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_option_chain(symbol='AAPL',
                                                       expiry=1755230400000,
                                                       market=Market.US,
                                                       timezone='America/New_York',
                                                       return_greek_value=True)
            logger.debug(f"Option Chain (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertGreaterEqual(len(mock_result), 2)

            # 验证数据框架的列
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('expiry', mock_result.columns)
            self.assertIn('identifier', mock_result.columns)
            self.assertIn('strike', mock_result.columns)
            self.assertIn('put_call', mock_result.columns)
            self.assertIn('multiplier', mock_result.columns)
            self.assertIn('ask_price', mock_result.columns)
            self.assertIn('ask_size', mock_result.columns)
            self.assertIn('volume', mock_result.columns)
            self.assertIn('latest_price', mock_result.columns)
            self.assertIn('pre_close', mock_result.columns)
            self.assertIn('open_interest', mock_result.columns)
            self.assertIn('last_timestamp', mock_result.columns)
            self.assertIn('implied_vol', mock_result.columns)

            # 检查行数
            self.assertEqual(len(mock_result), 2)  # 1个行权价，每个有看涨和看跌期权，共2个

            # 验证第一个期权合约 - 90.0执行价的看跌期权
            put_90 = mock_result.iloc[0]
            self.assertEqual(put_90['symbol'], 'AAPL')
            self.assertEqual(put_90['expiry'], 1755230400000)
            self.assertEqual(put_90['identifier'].strip(), 'AAPL  250815P00090000')
            self.assertEqual(put_90['strike'], '90.0')
            self.assertEqual(put_90['put_call'], 'PUT')
            self.assertEqual(put_90['ask_price'], 0.01)
            self.assertEqual(put_90['ask_size'], 750)
            self.assertEqual(put_90['volume'], 4)
            self.assertEqual(put_90['latest_price'], 0.01)
            self.assertEqual(put_90['pre_close'], 0.01)
            self.assertEqual(put_90['open_interest'], 1984)
            self.assertEqual(put_90['multiplier'], 100)
            self.assertEqual(put_90['last_timestamp'], 1754927160721)
            self.assertAlmostEqual(put_90['implied_vol'], 2.81666, places=4)
            self.assertAlmostEqual(put_90['delta'], -0.000514, places=6)
            self.assertAlmostEqual(put_90['gamma'], 0.000027, places=6)
            self.assertAlmostEqual(put_90['theta'], -0.016986, places=6)
            self.assertAlmostEqual(put_90['vega'], 0.000482, places=6)
            self.assertAlmostEqual(put_90['rho'], -0.000014, places=6)
        else:
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
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755001774695,
                         "data": [
                             {"symbol": "PDD", "identifier": "PDD   260121C00090000", "strike": "90.0", "volume": 130,
                              "multiplier": 100, "right": "call", "volatility": "26.29%", "expiry": 1768971600000,
                              "ratesBonds": 0.039494}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用 get_option_briefs 方法
            mock_result = self.client.get_option_briefs(
                identifiers=['PDD 260121C00090000'])
            logger.debug(f"Option Brief (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 1)  # 应该只有1个期权

            # 验证数据框架的列
            self.assertIn('identifier', mock_result.columns)
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('expiry', mock_result.columns)
            self.assertIn('strike', mock_result.columns)
            self.assertIn('put_call', mock_result.columns)
            self.assertIn('multiplier', mock_result.columns)
            self.assertIn('volume', mock_result.columns)
            self.assertIn('rates_bonds', mock_result.columns)
            self.assertIn('volatility', mock_result.columns)

            # 验证具体数据
            first_row = mock_result.iloc[0]
            self.assertEqual(first_row['identifier'].strip(), 'PDD   260121C00090000')
            self.assertEqual(first_row['symbol'], 'PDD')
            self.assertEqual(first_row['expiry'], 1768971600000)
            self.assertEqual(first_row['strike'], '90.0')
            self.assertEqual(first_row['put_call'], 'CALL')
            self.assertEqual(first_row['multiplier'], 100)
            self.assertEqual(first_row['volume'], 130)
            self.assertAlmostEqual(first_row['rates_bonds'], 0.039494)
            self.assertEqual(first_row['volatility'], '26.29%')
        else:
            result = self.client.get_option_briefs(
                identifiers=['PDD 260121C00090000'])
            logger.debug(f"Option Brief (real):\n {result}")

    def test_get_option_bars(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755002577624,
                         "data": [
                             {"symbol": "AAPL", "expiry": 1755230400000, "right": "CALL", "strike": "200.0",
                              "period": "day",
                              "items": [{"time": 1722830400000, "volume": 9, "open": 33.0, "close": 29.5, "high": 33.0,
                                         "low": 29.5, "markPrice": 29.5, "midPrice": 0.0, "openInterest": 0},
                                        {"time": 1722916800000, "volume": 18, "open": 27.95, "close": 31.6,
                                         "high": 31.6,
                                         "low": 27.88, "markPrice": 31.6, "midPrice": 0.0, "openInterest": 9}]}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期权K线数据方法
            mock_result = self.client.get_option_bars(
                identifiers=['AAPL 250815C00200000'], period=BarPeriod.DAY, limit=5)
            logger.debug(f"Option Bars (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 2)  # 应该有2条K线记录

            # 验证数据框架的列
            self.assertIn('identifier', mock_result.columns)
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('expiry', mock_result.columns)
            self.assertIn('put_call', mock_result.columns)
            self.assertIn('strike', mock_result.columns)
            self.assertIn('time', mock_result.columns)
            self.assertIn('open', mock_result.columns)
            self.assertIn('high', mock_result.columns)
            self.assertIn('low', mock_result.columns)
            self.assertIn('close', mock_result.columns)
            self.assertIn('volume', mock_result.columns)
            self.assertIn('open_interest', mock_result.columns)

            # 验证第一条K线数据
            first_bar = mock_result.iloc[0]
            self.assertEqual(first_bar['identifier'].strip(), 'AAPL  250815C00200000')
            self.assertEqual(first_bar['symbol'], 'AAPL')
            self.assertEqual(first_bar['expiry'], 1755230400000)
            self.assertEqual(first_bar['put_call'], 'CALL')
            self.assertEqual(first_bar['strike'], 200.0)
            self.assertEqual(first_bar['time'], 1722830400000)
            self.assertEqual(first_bar['open'], 33.0)
            self.assertEqual(first_bar['high'], 33.0)
            self.assertEqual(first_bar['low'], 29.5)
            self.assertEqual(first_bar['close'], 29.5)
            self.assertEqual(first_bar['volume'], 9)
            self.assertEqual(first_bar['open_interest'], 0)

            # 验证第二条K线数据
            second_bar = mock_result.iloc[1]
            self.assertEqual(second_bar['time'], 1722916800000)
            self.assertEqual(second_bar['open'], 27.95)
            self.assertEqual(second_bar['high'], 31.6)
            self.assertEqual(second_bar['low'], 27.88)
            self.assertEqual(second_bar['close'], 31.6)
            self.assertEqual(second_bar['volume'], 18)
            self.assertEqual(second_bar['open_interest'], 9)

        else:
            # result = self.client.get_option_bars(
            #     identifiers=['AAPL 250815C00200000'], period=BarPeriod.DAY, limit=5)
            result = self.client.get_option_bars(
                identifiers=['TCH.HK250828C00590000'], period=BarPeriod.DAY, limit=5,
                end_time='2025-08-22', timezone='Asia/Hong_Kong'
            )
            logger.debug(f"Option Bars (real):\n {result}")

    def test_get_option_trade_ticks(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755052112739,
                         "data": [{"symbol": "AAPL", "expiry": 1755230400000, "strike": "200.0", "right": "call",
                                   "items": [{"time": 1755005504417, "volume": 2, "price": 30.0},
                                             {"time": 1755005515034, "volume": 3, "price": 30.2},
                                             {"time": 1755005863136, "volume": 1, "price": 28.6}]
                                   }
                                  ]
                         }

            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期权逐笔成交方法
            mock_result = self.client.get_option_trade_ticks(
                identifiers=['AAPL 250815C00200000'])
            logger.debug(f"Option Trade Ticks (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 3)  # 应该有3条逐笔成交记录

            # 验证数据框架的列
            self.assertIn('identifier', mock_result.columns)
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('expiry', mock_result.columns)
            self.assertIn('put_call', mock_result.columns)
            self.assertIn('strike', mock_result.columns)
            self.assertIn('time', mock_result.columns)
            self.assertIn('price', mock_result.columns)
            self.assertIn('volume', mock_result.columns)

            # 验证第一条逐笔成交数据
            first_tick = mock_result.iloc[0]
            self.assertEqual(first_tick['identifier'].strip(), 'AAPL  250815C00200000')
            self.assertEqual(first_tick['symbol'], 'AAPL')
            self.assertEqual(first_tick['expiry'], 1755230400000)
            self.assertEqual(first_tick['put_call'], 'CALL')
            self.assertEqual(first_tick['strike'], 200.0)
            self.assertEqual(first_tick['time'], 1755005504417)
            self.assertEqual(first_tick['price'], 30.0)
            self.assertEqual(first_tick['volume'], 2)

            # 验证最后一条逐笔成交数据
            last_tick = mock_result.iloc[-1]
            self.assertEqual(last_tick['time'], 1755005863136)
            self.assertEqual(last_tick['price'], 28.6)
            self.assertEqual(last_tick['volume'], 1)

        else:
            result = self.client.get_option_trade_ticks(
                identifiers=['AAPL250829P00200000'])
            logger.debug(f"Option Trade Ticks (real):\n {result}")

    def test_get_option_symbols(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755054108505,
                         "data": [{"symbol": "ALC.HK", "name": "ALC", "underlyingSymbol": "02600"},
                                  {"symbol": "CRG.HK", "name": "CRG", "underlyingSymbol": "00390"}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期权合约代码方法
            mock_result = self.client.get_option_symbols(market=Market.HK)
            logger.debug(f"Option Symbols (mock):\n {mock_result}")
            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            # 验证数据框架的列
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('name', mock_result.columns)
            self.assertIn('underlying_symbol', mock_result.columns)

            # 验证第一个期权合约
            first_symbol = mock_result.iloc[0]
            self.assertEqual(first_symbol['symbol'], 'ALC.HK')
            self.assertEqual(first_symbol['name'], 'ALC')
            self.assertEqual(first_symbol['underlying_symbol'], '02600')

        else:
            result = self.client.get_option_symbols(market=Market.HK)
            logger.debug(f"Option Symbols (real):\n {result}")

    def test_get_option_depth(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755055831507, "data": [
                {"symbol": "AAPL", "expiry": 1755230400000, "strike": "210.0", "right": "CALL",
                 "timestamp": 1755028801000,
                 "ask": [{"price": 20.0, "code": "AMEX", "timestamp": 1755028800000, "volume": 26},
                         {"price": 20.0, "code": "BOX", "timestamp": 1755028799000, "volume": 25},
                         {"price": 20.75, "code": "C2", "timestamp": 1755028799000, "volume": 2}],
                 "bid": [{"price": 19.75, "code": "AMEX", "timestamp": 1755028800000, "volume": 23},
                         {"price": 19.75, "code": "CBOE", "timestamp": 1755028799000, "volume": 19},
                         {"price": 19.0, "code": "C2", "timestamp": 1755028799000, "volume": 1}]},
                {"symbol": "AAPL", "expiry": 1755230400000, "strike": "200.0", "right": "PUT",
                 "timestamp": 1755028801000,
                 "ask": [{"price": 0.04, "code": "NSDQ", "timestamp": 1755028798000, "volume": 127},
                         {"price": 0.05, "code": "CBOE", "timestamp": 1755028799000, "volume": 206},
                         {"price": 0.25, "code": "AMEX", "timestamp": 1755028800000, "volume": 1}],
                 "bid": [{"price": 0.03, "code": "ARCA", "timestamp": 1755028798000, "volume": 432},
                         {"price": 0.03, "code": "NSDQ", "timestamp": 1755028798000, "volume": 137},
                         {"price": 0.02, "code": "CBOE", "timestamp": 1755028799000, "volume": 125}]}]
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期权深度方法
            mock_result = self.client.get_option_depth(identifiers=['AAPL 250815C00210000', 'AAPL 250815P00200000'],
                                                       market=Market.US)
            logger.debug(f"Option Depth (mock): {mock_result}")

            # 验证返回的数据结构
            self.assertIsNotNone(mock_result)
            self.assertIsInstance(mock_result, dict)
            self.assertEqual(len(mock_result), 2)  # 应该返回两个期权的深度数据

            # 验证第一个期权的数据 (CALL)
            call_key = 'AAPL  250815C00210000'
            self.assertIn(call_key, mock_result)
            call_data = mock_result[call_key]
            self.assertEqual(call_data['identifier'].strip(), 'AAPL  250815C00210000')

            # 验证卖盘深度
            self.assertIn('asks', call_data)
            self.assertIsInstance(call_data['asks'], list)
            self.assertGreater(len(call_data['asks']), 0)
            first_ask = call_data['asks'][0]
            self.assertEqual(len(first_ask), 4)  # 每项应包含价格、数量、时间戳和交易所
            self.assertEqual(first_ask[0], 20.0)  # 价格
            self.assertEqual(first_ask[1], 26)  # 数量
            self.assertEqual(first_ask[2], 1755028800000)  # 时间戳
            self.assertEqual(first_ask[3], 'AMEX')  # 交易所

            # 验证买盘深度
            self.assertIn('bids', call_data)
            self.assertIsInstance(call_data['bids'], list)
            self.assertGreater(len(call_data['bids']), 0)
            first_bid = call_data['bids'][0]
            self.assertEqual(len(first_bid), 4)  # 每项应包含价格、数量、时间戳和交易所
            self.assertEqual(first_bid[0], 19.75)  # 价格
            self.assertEqual(first_bid[1], 23)  # 数量
            self.assertEqual(first_bid[2], 1755028800000)  # 时间戳
            self.assertEqual(first_bid[3], 'AMEX')  # 交易所

            # 验证第二个期权的数据 (PUT)
            put_key = 'AAPL  250815P00200000'
            self.assertIn(put_key, mock_result)
            put_data = mock_result[put_key]
            self.assertEqual(put_data['identifier'].strip(), 'AAPL  250815P00200000')

            # 验证卖盘深度
            self.assertIn('asks', put_data)
            self.assertIsInstance(put_data['asks'], list)
            self.assertGreater(len(put_data['asks']), 0)
            first_put_ask = put_data['asks'][0]
            self.assertEqual(first_put_ask[0], 0.04)  # 价格
            self.assertEqual(first_put_ask[1], 127)  # 数量
            self.assertEqual(first_put_ask[3], 'NSDQ')  # 交易所

            # 验证买盘深度
            self.assertIn('bids', put_data)
            self.assertIsInstance(put_data['bids'], list)
            self.assertGreater(len(put_data['bids']), 0)
            first_put_bid = put_data['bids'][0]
            self.assertEqual(first_put_bid[0], 0.03)  # 价格
            self.assertEqual(first_put_bid[1], 432)  # 数量
            self.assertEqual(first_put_bid[3], 'ARCA')  # 交易所

            # 测试单个期权请求
            mock_data_single = {"code": 0, "message": "success", "timestamp": 1755055831507, "data": [
                {"symbol": "AAPL", "expiry": 1755230400000, "strike": "210.0", "right": "CALL",
                 "timestamp": 1755028801000,
                 "ask": [{"price": 20.0, "code": "AMEX", "timestamp": 1755028800000, "volume": 26}],
                 "bid": [{"price": 19.75, "code": "AMEX", "timestamp": 1755028800000, "volume": 23}]}]}

            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data_single).encode())

            mock_single_result = self.client.get_option_depth(identifiers='AAPL 250815C00210000',
                                                              market=Market.US)
            logger.debug(f"Option Depth Single (mock): {mock_single_result}")

            # 验证单个期权返回的数据结构
            self.assertIsNotNone(mock_single_result)
            self.assertIn('identifier', mock_single_result)
            self.assertIn('asks', mock_single_result)
            self.assertIn('bids', mock_single_result)

        else:
            result = self.client.get_option_depth(identifiers=['AAPL 250815C00210000', 'AAPL 250815P00200000'],
                                                  market=Market.US)
            logger.debug(f"Option Depth (real): {result}")

    def test_get_option_timeline(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755057863524,
                         "data": [
                             {"symbol": "TCH.HK", "expiry": 1756310400000, "strike": "610.00", "right": "CALL",
                              "preClose": 1.87,
                              "openAndCloseTimeList": [[1755048600000, 1755057600000], [1755061200000, 1755072000000]],
                              "minutes": [{"price": 1.87, "avgPrice": 1.87, "time": 1755048600000, "volume": 0},
                                          {"price": 3.0, "avgPrice": 3.0, "time": 1755048660000, "volume": 3},
                                          {"price": 3.0, "avgPrice": 3.0, "time": 1755048720000, "volume": 0},
                                          {"price": 2.9, "avgPrice": 2.9018183, "time": 1755048780000, "volume": 162},
                                          {"price": 3.0, "avgPrice": 2.948896, "time": 1755048840000, "volume": 152},
                                          {"price": 3.14, "avgPrice": 2.9843256, "time": 1755048900000, "volume": 76}
                                          ]
                              }
                         ]
                         }

            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期权时间线方法
            mock_result = self.client.get_option_timeline(
                identifiers=['TCH.HK 250828C00610000'], market=Market.HK)
            logger.debug(f"Option Timeline (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 6)  # 应该有6条数据记录

            # 验证数据框架的列
            self.assertIn('identifier', mock_result.columns)
            self.assertIn('symbol', mock_result.columns)
            self.assertIn('expiry', mock_result.columns)
            self.assertIn('put_call', mock_result.columns)
            self.assertIn('strike', mock_result.columns)
            self.assertIn('pre_close', mock_result.columns)
            self.assertIn('price', mock_result.columns)
            self.assertIn('avg_price', mock_result.columns)
            self.assertIn('time', mock_result.columns)
            self.assertIn('volume', mock_result.columns)

            # 验证第一条数据记录
            first_record = mock_result.iloc[0]
            self.assertEqual(first_record['identifier'].strip(), 'TCH.HK250828C00610000')
            self.assertEqual(first_record['symbol'], 'TCH.HK')
            self.assertEqual(first_record['expiry'], 1756310400000)
            self.assertEqual(first_record['put_call'], 'CALL')
            self.assertEqual(first_record['strike'], '610.00')
            self.assertEqual(first_record['pre_close'], 1.87)
            self.assertEqual(first_record['price'], 1.87)
            self.assertEqual(first_record['avg_price'], 1.87)
            self.assertEqual(first_record['time'], 1755048600000)
            self.assertEqual(first_record['volume'], 0)

            # 验证第三条数据记录
            third_record = mock_result.iloc[2]
            self.assertEqual(third_record['price'], 3.0)
            self.assertEqual(third_record['avg_price'], 3.0)
            self.assertEqual(third_record['time'], 1755048720000)
            self.assertEqual(third_record['volume'], 0)

            # 验证最后一条数据记录
            last_record = mock_result.iloc[5]
            self.assertEqual(last_record['price'], 3.14)
            self.assertAlmostEqual(last_record['avg_price'], 2.9843256, places=6)
            self.assertEqual(last_record['time'], 1755048900000)
            self.assertEqual(last_record['volume'], 76)
        else:
            result = self.client.get_option_timeline(identifiers=['TCH.HK 250828C00610000'], market=Market.HK)
            logger.debug(f"Option Timeline (real):\n {result}")

    def test_get_future_exchanges(self):
        if not self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755062040054,
                         "data": [{"code": "CME", "name": "CME", "zoneId": "America/Chicago"},
                                  {"code": "NYMEX", "name": "NYMEX", "zoneId": "America/New_York"},
                                  {"code": "COMEX", "name": "COMEX", "zoneId": "America/New_York"},
                                  {"code": "SGX", "name": "SGX", "zoneId": "Singapore"},
                                  {"code": "HKEX", "name": "HKEX", "zoneId": "Asia/Hong_Kong"},
                                  {"code": "CBOT", "name": "CBOT", "zoneId": "America/Chicago"},
                                  {"code": "OSE", "name": "OSE", "zoneId": "Asia/Tokyo"},
                                  {"code": "CBOE", "name": "CBOE", "zoneId": "America/Chicago"},
                                  {"code": "EUREX", "name": "EUREX", "zoneId": "Europe/Berlin"}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期货交易所列表方法
            mock_result = self.client.get_future_exchanges()
            logger.debug(f"Future Exchanges (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 9)  # 应该有9个交易所

            # 验证数据框架的列
            self.assertIn('code', mock_result.columns)
            self.assertIn('name', mock_result.columns)
            self.assertIn('zone', mock_result.columns)

            # 验证第一个交易所
            first_exchange = mock_result.iloc[0]
            self.assertEqual(first_exchange['code'], 'CME')
            self.assertEqual(first_exchange['name'], 'CME')
            self.assertEqual(first_exchange['zone'], 'America/Chicago')

            # 验证第四个交易所
            fourth_exchange = mock_result.iloc[3]
            self.assertEqual(fourth_exchange['code'], 'SGX')
            self.assertEqual(fourth_exchange['name'], 'SGX')
            self.assertEqual(fourth_exchange['zone'], 'Singapore')

            # 验证最后一个交易所
            last_exchange = mock_result.iloc[8]
            self.assertEqual(last_exchange['code'], 'EUREX')
            self.assertEqual(last_exchange['name'], 'EUREX')
            self.assertEqual(last_exchange['zone'], 'Europe/Berlin')
        else:
            result = self.client.get_future_exchanges()
            logger.debug(f"Future Exchanges (real):\n {result}")

    def test_get_future_contracts(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755062339514,
                         "data": [
                             {"continuous": True, "trade": True, "type": "MEUR", "contractCode": "MEUR2509",
                              "ibCode": "M6E",
                              "name": "E-Micro EUR/USD - Sep 2025", "contractMonth": "202509",
                              "lastTradingDate": "20250915",
                              "firstNoticeDate": "", "lastBiddingCloseTime": 0, "currency": "USD",
                              "exchangeCode": "GLOBEX",
                              "multiplier": 1.25E+4, "minTick": 0.0001, "displayMultiplier": 1, "exchange": "CME",
                              "productWorth": "12,500 x futures price (USD)", "deliveryMode": "Physical",
                              "productType": "FX"},
                             {"continuous": False, "trade": True, "type": "MEUR", "contractCode": "MEUR2512",
                              "ibCode": "M6E",
                              "name": "E-Micro EUR/USD - Dec 2025", "contractMonth": "202512",
                              "lastTradingDate": "20251215",
                              "firstNoticeDate": "", "lastBiddingCloseTime": 0, "currency": "USD",
                              "exchangeCode": "GLOBEX",
                              "multiplier": 1.25E+4, "minTick": 0.0001, "displayMultiplier": 1, "exchange": "CME",
                              "productWorth": "12,500 x futures price (USD)", "deliveryMode": "Physical",
                              "productType": "FX"}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期货合约方法
            mock_result = self.client.get_future_contracts(exchange='CME')
            logger.debug(f"Future Contracts (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 2)  # 应该有2个期货合约

            # 验证数据框架的列
            self.assertIn('contract_code', mock_result.columns)
            self.assertIn('type', mock_result.columns)
            self.assertIn('name', mock_result.columns)
            self.assertIn('contract_month', mock_result.columns)
            self.assertIn('currency', mock_result.columns)
            self.assertIn('last_trading_date', mock_result.columns)
            self.assertIn('multiplier', mock_result.columns)
            self.assertIn('min_tick', mock_result.columns)
            self.assertIn('exchange', mock_result.columns)
            self.assertIn('exchange_code', mock_result.columns)
            self.assertIn('trade', mock_result.columns)
            self.assertIn('continuous', mock_result.columns)
            self.assertIn('symbol', mock_result.columns)

            # 验证第一个期货合约
            first_contract = mock_result.iloc[0]
            self.assertEqual(first_contract['contract_code'], 'MEUR2509')
            self.assertEqual(first_contract['type'], 'MEUR')
            self.assertEqual(first_contract['name'], 'E-Micro EUR/USD - Sep 2025')
            self.assertEqual(first_contract['contract_month'], '202509')
            self.assertEqual(first_contract['currency'], 'USD')
            self.assertEqual(first_contract['last_trading_date'], '20250915')
            self.assertEqual(first_contract['multiplier'], 12500.0)
            self.assertEqual(first_contract['min_tick'], 0.0001)
            self.assertEqual(first_contract['exchange'], 'CME')
            self.assertEqual(first_contract['exchange_code'], 'GLOBEX')
            self.assertTrue(first_contract['trade'])
            self.assertTrue(first_contract['continuous'])
            self.assertEqual(first_contract['symbol'], 'M6E')
            self.assertEqual(first_contract['delivery_mode'], 'Physical')
            self.assertEqual(first_contract['product_type'], 'FX')

        else:
            result = self.client.get_future_contracts(exchange='CME')
            logger.debug(f"Future Contracts (real):\n {result}")

    def test_get_future_contract(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755065781016,
                         "data": {"continuous": False, "trade": True, "type": "CL", "contractCode": "CLmain",
                                  "ibCode": "CL", "name": "WTI Crude Oil - main", "contractMonth": "",
                                  "lastTradingDate": "", "firstNoticeDate": "", "lastBiddingCloseTime": 0,
                                  "currency": "USD", "exchangeCode": "NYMEX", "multiplier": 1E+3, "minTick": 0.01,
                                  "displayMultiplier": 1, "exchange": "NYMEX",
                                  "productWorth": "US$1,000 x futures price", "deliveryMode": "Physical",
                                  "productType": "Energy"}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期货合约方法
            mock_result = self.client.get_future_contract(contract_code='CLmain')
            logger.debug(f"Future Contract (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsInstance(mock_result, pd.DataFrame)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 1)

            # 详细验证各字段值
            self.assertEqual(mock_result.iloc[0]['contract_code'], 'CLmain')
            self.assertEqual(mock_result.iloc[0]['continuous'], False)
            self.assertEqual(mock_result.iloc[0]['contract_month'], '')
            self.assertEqual(mock_result.iloc[0]['currency'], 'USD')
            self.assertEqual(mock_result.iloc[0]['delivery_mode'], 'Physical')
            self.assertEqual(mock_result.iloc[0]['display_multiplier'], 1)
            self.assertEqual(mock_result.iloc[0]['exchange'], 'NYMEX')
            self.assertEqual(mock_result.iloc[0]['exchange_code'], 'NYMEX')
            self.assertEqual(mock_result.iloc[0]['first_notice_date'], '')
            self.assertEqual(mock_result.iloc[0]['last_bidding_close_time'], 0)
            self.assertEqual(mock_result.iloc[0]['last_trading_date'], '')
            self.assertEqual(mock_result.iloc[0]['min_tick'], 0.01)
            self.assertEqual(mock_result.iloc[0]['multiplier'], 1000.0)
            self.assertEqual(mock_result.iloc[0]['name'], 'WTI Crude Oil - main')
            self.assertEqual(mock_result.iloc[0]['product_type'], 'Energy')
            self.assertEqual(mock_result.iloc[0]['product_worth'], 'US$1,000 x futures price')
            self.assertEqual(mock_result.iloc[0]['symbol'], 'CL')
            self.assertEqual(mock_result.iloc[0]['trade'], True)
            self.assertEqual(mock_result.iloc[0]['type'], 'CL')

        else:
            result = self.client.get_future_contract(contract_code='CLmain')
            logger.debug(f"Future Contract (real):\n {result}")

    def test_get_future_continuous_contracts(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755062931981,
                         "data": {"continuous": False, "trade": True, "type": "CL", "contractCode": "CLmain",
                                  "ibCode": "CL", "name": "WTI Crude Oil - main", "contractMonth": "",
                                  "lastTradingDate": "", "firstNoticeDate": "", "lastBiddingCloseTime": 0,
                                  "currency": "USD", "exchangeCode": "NYMEX", "multiplier": 1E+3, "minTick": 0.01,
                                  "displayMultiplier": 1, "exchange": "NYMEX",
                                  "productWorth": "US$1,000 x futures price", "deliveryMode": "Physical",
                                  "productType": "Energy"}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期货连续合约方法
            mock_result = self.client.get_future_continuous_contracts(future_type='CL')
            logger.debug(f"Future Continuous Contracts (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 1)  # 应该只有一条连续合约记录

            # 验证数据框架的列
            self.assertIn('contract_code', mock_result.columns)
            self.assertIn('continuous', mock_result.columns)
            self.assertIn('trade', mock_result.columns)
            self.assertIn('type', mock_result.columns)
            self.assertIn('name', mock_result.columns)
            self.assertIn('contract_month', mock_result.columns)
            self.assertIn('currency', mock_result.columns)
            self.assertIn('exchange', mock_result.columns)
            self.assertIn('exchange_code', mock_result.columns)
            self.assertIn('multiplier', mock_result.columns)
            self.assertIn('min_tick', mock_result.columns)
            self.assertIn('product_worth', mock_result.columns)
            self.assertIn('delivery_mode', mock_result.columns)
            self.assertIn('product_type', mock_result.columns)

            # 验证连续合约的具体值
            contract = mock_result.iloc[0]
            self.assertEqual(contract['contract_code'], 'CLmain')
            self.assertFalse(contract['continuous'])
            self.assertTrue(contract['trade'])
            self.assertEqual(contract['type'], 'CL')
            self.assertEqual(contract['name'], 'WTI Crude Oil - main')
            self.assertEqual(contract['contract_month'], '')
            self.assertEqual(contract['currency'], 'USD')
            self.assertEqual(contract['exchange'], 'NYMEX')
            self.assertEqual(contract['exchange_code'], 'NYMEX')
            self.assertEqual(contract['multiplier'], 1000.0)
            self.assertEqual(contract['min_tick'], 0.01)
            self.assertEqual(contract['product_worth'], 'US$1,000 x futures price')
            self.assertEqual(contract['delivery_mode'], 'Physical')
            self.assertEqual(contract['product_type'], 'Energy')
        else:
            result = self.client.get_future_continuous_contracts(future_type='CL')
            logger.debug(f"Future Continuous Contracts (real):\n {result}")

    def test_get_current_future_contract(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755063553419,
                         "data": {"continuous": True, "trade": True, "type": "ES", "contractCode": "ES2509",
                                  "ibCode": "ES", "name": "E-mini S&P 500 - Sep 2025", "contractMonth": "202509",
                                  "lastTradingDate": "20250919", "firstNoticeDate": "", "lastBiddingCloseTime": 0,
                                  "currency": "USD", "exchangeCode": "GLOBEX", "multiplier": 5E+1, "minTick": 0.25,
                                  "displayMultiplier": 1, "exchange": "CME",
                                  "productWorth": "US$50 USD per index point", "deliveryMode": "Cash",
                                  "productType": "Equity Index"}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期货当前合约方法
            mock_result = self.client.get_current_future_contract(future_type='ES')
            logger.debug(f"Future Current Contract (mock):\n {mock_result}")

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 1)  # 应该只有一条当前合约记录

            # 验证数据框架的列
            self.assertIn('contract_code', mock_result.columns)
            self.assertIn('continuous', mock_result.columns)
            self.assertIn('trade', mock_result.columns)
            self.assertIn('type', mock_result.columns)
            self.assertIn('name', mock_result.columns)
            self.assertIn('contract_month', mock_result.columns)
            self.assertIn('currency', mock_result.columns)
            self.assertIn('exchange', mock_result.columns)
            self.assertIn('exchange_code', mock_result.columns)
            self.assertIn('multiplier', mock_result.columns)
            self.assertIn('min_tick', mock_result.columns)
            self.assertIn('product_worth', mock_result.columns)
            self.assertIn('delivery_mode', mock_result.columns)
            self.assertIn('product_type', mock_result.columns)

            # 验证当前合约的具体值
            contract = mock_result.iloc[0]
            self.assertEqual(contract['contract_code'], 'ES2509')
            self.assertTrue(contract['continuous'])
            self.assertTrue(contract['trade'])
            self.assertEqual(contract['type'], 'ES')
            self.assertEqual(contract['name'], 'E-mini S&P 500 - Sep 2025')
            self.assertEqual(contract['contract_month'], '202509')
            self.assertEqual(contract['currency'], 'USD')
            self.assertEqual(contract['exchange'], 'CME')
            self.assertEqual(contract['exchange_code'], 'GLOBEX')
            self.assertEqual(contract['multiplier'], 50.0)
            self.assertEqual(contract['min_tick'], 0.25)
            self.assertEqual(contract['last_trading_date'], '20250919')
            self.assertEqual(contract['product_worth'], 'US$50 USD per index point')
            self.assertEqual(contract['delivery_mode'], 'Cash')
            self.assertEqual(contract['product_type'], 'Equity Index')
        else:
            result = self.client.get_current_future_contract(future_type='ES')
            logger.debug(f"Future Current Contract (real):\n {result}")

    def test_get_all_future_contracts(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755064020186,
                         "data": [
                             {"continuous": False, "trade": True, "type": "ES", "contractCode": "ES2509",
                              "ibCode": "ES",
                              "name": "E-mini S&P 500 - Sep 2025", "contractMonth": "202509",
                              "lastTradingDate": "20250919",
                              "firstNoticeDate": "", "lastBiddingCloseTime": 0, "currency": "USD",
                              "exchangeCode": "GLOBEX",
                              "multiplier": 5E+1, "minTick": 0.25, "displayMultiplier": 1, "exchange": "CME",
                              "productWorth": "US$50 USD per index point", "deliveryMode": "Cash",
                              "productType": "Equity Index"},
                             {"continuous": False, "trade": True, "type": "ES", "contractCode": "ES2512",
                              "ibCode": "ES",
                              "name": "E-mini S&P 500 - Dec 2025", "contractMonth": "202512",
                              "lastTradingDate": "20251219",
                              "firstNoticeDate": "", "lastBiddingCloseTime": 0, "currency": "USD",
                              "exchangeCode": "GLOBEX",
                              "multiplier": 5E+1, "minTick": 0.25, "displayMultiplier": 1, "exchange": "CME",
                              "productWorth": "US$50 USD per index point", "deliveryMode": "Cash",
                              "productType": "Equity Index"}
                         ]
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取所有期货合约方法
            mock_result = self.client.get_all_future_contracts("ES")
            logger.debug(f"All Future Contracts (mock):\n {mock_result}")

            # 验证返回结果
            self.assertIsInstance(mock_result, pd.DataFrame)
            self.assertEqual(len(mock_result), 2)

            # 验证第一条数据
            self.assertEqual(mock_result.iloc[0]['contract_code'], 'ES2509')
            self.assertEqual(mock_result.iloc[0]['continuous'], False)
            self.assertEqual(mock_result.iloc[0]['contract_month'], '202509')
            self.assertEqual(mock_result.iloc[0]['currency'], 'USD')
            self.assertEqual(mock_result.iloc[0]['delivery_mode'], 'Cash')
            self.assertEqual(mock_result.iloc[0]['exchange'], 'CME')
            self.assertEqual(mock_result.iloc[0]['exchange_code'], 'GLOBEX')
            self.assertEqual(mock_result.iloc[0]['last_trading_date'], '20250919')
            self.assertEqual(mock_result.iloc[0]['min_tick'], 0.25)
            self.assertEqual(mock_result.iloc[0]['multiplier'], 50.0)
            self.assertEqual(mock_result.iloc[0]['name'], 'E-mini S&P 500 - Sep 2025')
            self.assertEqual(mock_result.iloc[0]['product_type'], 'Equity Index')
            self.assertEqual(mock_result.iloc[0]['product_worth'], 'US$50 USD per index point')
            self.assertEqual(mock_result.iloc[0]['symbol'], 'ES')
            self.assertEqual(mock_result.iloc[0]['trade'], True)
            self.assertEqual(mock_result.iloc[0]['type'], 'ES')

            # 验证第二条数据
            self.assertEqual(mock_result.iloc[1]['contract_code'], 'ES2512')
            self.assertEqual(mock_result.iloc[1]['contract_month'], '202512')
            self.assertEqual(mock_result.iloc[1]['last_trading_date'], '20251219')

            # 验证返回的数据框架
            self.assertIsNotNone(mock_result)
            self.assertFalse(mock_result.empty)
            self.assertEqual(len(mock_result), 2)
        else:
            result = self.client.get_all_future_contracts(future_type='ES')
            logger.debug(f"All Future Contracts (real):\n {result}")

    def test_get_future_trading_times(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755064389047,
                         "data": {"biddingTimes": [{"start": 1755035100000, "end": 1755036000000}],
                                  "tradingTimes": [{"start": 1755036000000, "end": 1755118800000}],
                                  "timeSection": "America/New_York"}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期货交易时间方法
            mock_result = self.client.get_future_trading_times(identifier='CL2609')
            logger.debug(f"Future Trading Times (mock): \n {mock_result}")

            # 验证返回结果
            self.assertIsInstance(mock_result, pd.DataFrame)
            self.assertEqual(len(mock_result), 2)  # 应该有两行数据（一行竞价，一行交易）

            # 验证竞价时段数据
            self.assertEqual(mock_result.iloc[0]['start'], 1755035100000)
            self.assertEqual(mock_result.iloc[0]['end'], 1755036000000)
            self.assertEqual(mock_result.iloc[0]['trading'], False)
            self.assertEqual(mock_result.iloc[0]['bidding'], True)
            self.assertEqual(mock_result.iloc[0]['zone'], 'America/New_York')

            # 验证交易时段数据
            self.assertEqual(mock_result.iloc[1]['start'], 1755036000000)
            self.assertEqual(mock_result.iloc[1]['end'], 1755118800000)
            self.assertEqual(mock_result.iloc[1]['trading'], True)
            self.assertEqual(mock_result.iloc[1]['bidding'], False)
            self.assertEqual(mock_result.iloc[1]['zone'], 'America/New_York')
        else:
            result = self.client.get_future_trading_times(identifier='CL2609')
            logger.debug(f"Future Trading Times: \n {result}")

    def test_get_future_bars(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755066247698, "data": [
                {"nextPageToken": "ZnV0dXJlX2tsaW5lfENMMjYwOXxkYXl8MTc1NTA2NjI0NzY5NnwxNzU0NTEzOTcwMDAw", "items": [
                    {"time": 1755032400000, "volume": 2459, "open": 61.25, "close": 61.25, "high": 61.25, "low": 61.13,
                     "lastTime": 1755032400000, "openInterest": 47604, "settlement": 61.25},
                    {"time": 1754946000000, "volume": 707, "open": 61.19, "close": 61.19, "high": 61.19, "low": 61.19,
                     "lastTime": 1754904392000, "openInterest": 47604, "settlement": 61.47},
                    {"time": 1754686800000, "volume": 1340, "open": 61.35, "close": 61.21, "high": 61.59, "low": 61.21,
                     "lastTime": 1754669837000, "openInterest": 47375, "settlement": 61.2},
                    {"time": 1754600400000, "volume": 0, "open": 61.37, "close": 61.37, "high": 61.37, "low": 61.37,
                     "lastTime": 1754600400000, "openInterest": 46496, "settlement": 61.37},
                    {"time": 1754514000000, "volume": 762, "open": 61.88, "close": 62.26, "high": 62.28, "low": 61.88,
                     "lastTime": 1754498885000, "openInterest": 46535, "settlement": 61.36}],
                 "contractCode": "CL2609"}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取期货K线数据方法
            mock_result = self.client.get_future_bars(identifiers=['CL2609'],
                                                      period='day', limit=5)
            logger.debug(f"Future Bars (mock): \n{mock_result}")

            # 验证返回结果
            self.assertIsInstance(mock_result, pd.DataFrame)
            self.assertEqual(len(mock_result), 5)  # 应该有5条K线数据

            # 验证返回的数据框架结构
            expected_columns = ['identifier', 'time', 'latest_time', 'open', 'high',
                                'low', 'close', 'settlement', 'volume', 'open_interest',
                                'next_page_token']
            for col in expected_columns:
                self.assertIn(col, mock_result.columns)

            # 验证第一条K线数据
            self.assertEqual(mock_result.iloc[0]['identifier'], 'CL2609')
            self.assertEqual(mock_result.iloc[0]['time'], 1755032400000)
            self.assertEqual(mock_result.iloc[0]['latest_time'], 1755032400000)
            self.assertEqual(mock_result.iloc[0]['open'], 61.25)
            self.assertEqual(mock_result.iloc[0]['high'], 61.25)
            self.assertEqual(mock_result.iloc[0]['low'], 61.13)
            self.assertEqual(mock_result.iloc[0]['close'], 61.25)
            self.assertEqual(mock_result.iloc[0]['settlement'], 61.25)
            self.assertEqual(mock_result.iloc[0]['volume'], 2459)
            self.assertEqual(mock_result.iloc[0]['open_interest'], 47604)
            self.assertEqual(mock_result.iloc[0]['next_page_token'],
                             "ZnV0dXJlX2tsaW5lfENMMjYwOXxkYXl8MTc1NTA2NjI0NzY5NnwxNzU0NTEzOTcwMDAw")

            # 验证最后一条K线数据
            self.assertEqual(mock_result.iloc[4]['time'], 1754514000000)
            self.assertEqual(mock_result.iloc[4]['latest_time'], 1754498885000)
            self.assertEqual(mock_result.iloc[4]['open'], 61.88)
            self.assertEqual(mock_result.iloc[4]['close'], 62.26)
            self.assertEqual(mock_result.iloc[4]['high'], 62.28)
            self.assertEqual(mock_result.iloc[4]['low'], 61.88)
            self.assertEqual(mock_result.iloc[4]['settlement'], 61.36)
            self.assertEqual(mock_result.iloc[4]['volume'], 762)
            self.assertEqual(mock_result.iloc[4]['open_interest'], 46535)

        else:
            result = self.client.get_future_bars(identifiers=['CL2609'],
                                                 period='day', limit=5)
            logger.debug(f"Future Bars: \n{result}")

    def test_get_future_trade_ticks(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755066650865,
                         "data": {"contractCode": "CL2509",
                                  "items": [{"index": 0, "price": 63.07, "volume": 10, "time": 1755036000000},
                                            {"index": 1, "price": 63.07, "volume": 7, "time": 1755036000000},
                                            {"index": 2, "price": 63.07, "volume": 9, "time": 1755036000000},
                                            {"index": 3, "price": 63.06, "volume": 4, "time": 1755036000000},
                                            {"index": 4, "price": 63.05, "volume": 6, "time": 1755036000000}
                                            ]}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # Call the method
            result = self.client.get_future_trade_ticks(identifier='CL2509')

            # Verify the result
            self.assertIsNotNone(result)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), 5)

            # Check DataFrame columns
            expected_columns = ['identifier', 'index', 'price', 'volume', 'time']
            self.assertListEqual(list(result.columns), expected_columns)

            # Verify data values
            self.assertEqual(result['identifier'].iloc[0], 'CL2509')
            self.assertEqual(result['index'].iloc[0], 0)
            self.assertEqual(result['price'].iloc[0], 63.07)
            self.assertEqual(result['volume'].iloc[0], 10)
            self.assertEqual(result['time'].iloc[0], 1755036000000)

            # Verify last row
            self.assertEqual(result['index'].iloc[4], 4)
            self.assertEqual(result['price'].iloc[4], 63.05)
            self.assertEqual(result['volume'].iloc[4], 6)
        else:
            result = self.client.get_future_trade_ticks(identifier='CL2509')
            logger.debug(f"Future Ticks:\n {result}")

    def test_get_future_brief(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755067666670, "data": [
                {"contractCode": "ES2509", "latestPrice": 6469.50, "latestSize": 5, "latestTime": 1755067657000,
                 "bidPrice": 6469.50, "askPrice": 6469.75, "bidSize": 11, "askSize": 14, "openInterest": 1938507,
                 "openInterestChange": 26858, "volume": 46493, "open": 6468.00, "high": 6474.75, "low": 6461.00,
                 "settlement": 6468.50, "limitUp": 6919.50, "limitDown": 6017.50}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # Call the method
            result = self.client.get_future_brief(identifiers=['ES2509'])

            # Verify the result
            self.assertIsNotNone(result)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), 1)

            # Check DataFrame columns
            expected_columns = ['identifier', 'latest_price', 'latest_size', 'latest_time', 'bid_price', 'ask_price',
                                'bid_size', 'ask_size', 'open_interest', 'open_interest_change', 'volume', 'open',
                                'high', 'low', 'settlement', 'limit_up', 'limit_down']
            for col in expected_columns:
                self.assertIn(col, result.columns)

            # Verify data values
            self.assertEqual(result['identifier'].iloc[0], 'ES2509')
            self.assertEqual(result['latest_price'].iloc[0], 6469.50)
            self.assertEqual(result['latest_size'].iloc[0], 5)
            self.assertEqual(result['latest_time'].iloc[0], 1755067657000)
            self.assertEqual(result['bid_price'].iloc[0], 6469.50)
            self.assertEqual(result['ask_price'].iloc[0], 6469.75)
            self.assertEqual(result['bid_size'].iloc[0], 11)
            self.assertEqual(result['ask_size'].iloc[0], 14)
            self.assertEqual(result['open_interest'].iloc[0], 1938507)
            self.assertEqual(result['open_interest_change'].iloc[0], 26858)
            self.assertEqual(result['volume'].iloc[0], 46493)
            self.assertEqual(result['open'].iloc[0], 6468.00)
            self.assertEqual(result['high'].iloc[0], 6474.75)
            self.assertEqual(result['low'].iloc[0], 6461.00)
            self.assertEqual(result['settlement'].iloc[0], 6468.50)
            self.assertEqual(result['limit_up'].iloc[0], 6919.50)
            self.assertEqual(result['limit_down'].iloc[0], 6017.50)
        else:
            result = self.client.get_future_brief(identifiers=['ES2509'])
            logger.debug(f"Future Brief: \n {result}")

    def test_get_future_depth(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755847046112, "data": [
                {"contractId": "d2cf66f761354eda8ddbecc242f6d245", "contractCode": "ES2509",
                 "ask": [{"price": 6385.00, "volume": 1}, {"price": 6385.25, "volume": 23},
                         {"price": 6385.50, "volume": 30}, {"price": 6385.75, "volume": 26}],
                 "bid": [{"price": 6384.75, "volume": 22}, {"price": 6384.50, "volume": 28},
                         {"price": 6384.25, "volume": 36}, {"price": 6384.00, "volume": 33}]},
                {"contractId": "2971d762658f43c7bb26d353cc314b4d", "contractCode": "ES2512",
                 "ask": [{"price": 6440.75, "volume": 2}, {"price": 6441.00, "volume": 3}],
                 "bid": [{"price": 6439.75, "volume": 1}, {"price": 6439.50, "volume": 2}]}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # {'identifier': 'ES2509', 'asks': [(6385.0, 1), (6385.25, 23), (6385.5, 30), (6385.75, 26), (6386.0, 43), (6386.25, 37), (6386.5, 31), (6386.75, 39), (6387.0, 39), (6387.25, 30)], 'bids': [(6384.75, 22), (6384.5, 28), (6384.25, 36), (6384.0, 33), (6383.75, 44), (6383.5, 32), (6383.25, 35), (6383.0, 38), (6382.75, 33), (6382.5, 42)]}
            result_single = self.client.get_future_depth(identifiers=['ES2509'])

            logger.debug(f"Future Depth (single): \n {result_single}")
            # Verify the result
            self.assertIsNotNone(result_single)
            self.assertIsInstance(result_single, dict)
            self.assertIn('ES2509', result_single)
            self.assertIn('asks', result_single['ES2509'])
            self.assertIn('bids', result_single['ES2509'])
            self.assertEqual(len(result_single['ES2509']['asks']), 4)
            self.assertEqual(len(result_single['ES2509']['bids']), 4)
            self.assertEqual(result_single['ES2509']['identifier'], 'ES2509')
            self.assertEqual(result_single['ES2509']['asks'][0], (6385.00, 1))
            self.assertEqual(result_single['ES2509']['bids'][0], (6384.75, 22))

            # {'ES2509': {'identifier': 'ES2509', 'asks': [(6385.0, 1), (6385.25, 23), (6385.5, 30), (6385.75, 26), (6386.0, 43), (6386.25, 37), (6386.5, 31), (6386.75, 39), (6387.0, 39), (6387.25, 30)], 'bids': [(6384.75, 22), (6384.5, 28), (6384.25, 36), (6384.0, 33), (6383.75, 44), (6383.5, 32), (6383.25, 35), (6383.0, 38), (6382.75, 33), (6382.5, 42)]}, 'ES2512': {'identifier': 'ES2512', 'asks': [(6440.75, 2), (6441.0, 3), (6441.25, 2), (6441.5, 2), (6441.75, 2), (6442.0, 4), (6442.25, 2), (6442.5, 1), (6442.75, 3), (6443.0, 4)], 'bids': [(6439.75, 1), (6439.5, 2), (6439.25, 1), (6439.0, 4), (6438.75, 2), (6438.5, 2), (6438.25, 2), (6438.0, 4), (6437.75, 2), (6437.5, 2)]}}
            result_multi = self.client.get_future_depth(identifiers=['ES2509', 'ES2512'])

            # Verify the result
            self.assertIsNotNone(result_multi)
            self.assertIsInstance(result_multi, dict)
            self.assertIn('ES2509', result_multi)
            self.assertIn('ES2512', result_multi)
            self.assertIn('asks', result_multi['ES2509'])
            self.assertIn('bids', result_multi['ES2509'])
            self.assertIn('asks', result_multi['ES2512'])
            self.assertIn('bids', result_multi['ES2512'])
            self.assertEqual(len(result_multi['ES2509']['asks']), 4)
            self.assertEqual(len(result_multi['ES2509']['bids']), 4)
            self.assertEqual(len(result_multi['ES2512']['asks']), 2)
            self.assertEqual(len(result_multi['ES2512']['bids']), 2)
            self.assertEqual(result_multi['ES2509']['identifier'], 'ES2509')
            self.assertEqual(result_multi['ES2512']['identifier'], 'ES2512')
            self.assertEqual(result_multi['ES2509']['asks'][0], (6385.00, 1))
            self.assertEqual(result_multi['ES2509']['bids'][0], (6384.75, 22))
            self.assertEqual(result_multi['ES2512']['asks'][0], (6440.75, 2))
            self.assertEqual(result_multi['ES2512']['bids'][0], (6439.75, 1))

        else:
            result = self.client.get_future_depth(identifiers=['ES2509', 'ES2512'])
            logger.debug(f"Future Depth: \n {result}")

    def test_get_trading_calendar(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755068224574,
                         "data": [{"date": "2025-08-13", "type": "TRADING"}, {"date": "2025-08-14", "type": "TRADING"},
                                  {"date": "2025-08-15", "type": "TRADING"}, {"date": "2025-08-18", "type": "TRADING"},
                                  {"date": "2025-08-19", "type": "TRADING"}, {"date": "2025-08-20", "type": "TRADING"},
                                  {"date": "2025-08-21", "type": "TRADING"}, {"date": "2025-08-22", "type": "TRADING"},
                                  {"date": "2025-08-25", "type": "TRADING"}, {"date": "2025-08-26", "type": "TRADING"},
                                  {"date": "2025-08-27", "type": "TRADING"}, {"date": "2025-08-28", "type": "TRADING"},
                                  {"date": "2025-08-29", "type": "TRADING"}, {"date": "2025-09-02", "type": "TRADING"},
                                  {"date": "2025-09-03", "type": "TRADING"}, {"date": "2025-09-04", "type": "TRADING"},
                                  {"date": "2025-09-05", "type": "TRADING"}, {"date": "2025-09-08", "type": "TRADING"},
                                  {"date": "2025-09-09", "type": "TRADING"}, {"date": "2025-09-10", "type": "TRADING"},
                                  {"date": "2025-09-11", "type": "TRADING"}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # Call the method
            result = self.client.get_trading_calendar(market='US')

            # Verify the result
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 21)

            # Check first day data
            first_day = result[0]
            self.assertIsInstance(first_day, dict)
            self.assertIn('date', first_day)
            self.assertIn('type', first_day)
            self.assertEqual(first_day['date'], '2025-08-13')
            self.assertEqual(first_day['type'], 'TRADING')

            # Check last day data
            last_day = result[-1]
            self.assertEqual(last_day['date'], '2025-09-11')
            self.assertEqual(last_day['type'], 'TRADING')

            # Check sequential days
            sequential_days = [result[0], result[1], result[2]]
            self.assertEqual(sequential_days[0]['date'], '2025-08-13')
            self.assertEqual(sequential_days[1]['date'], '2025-08-14')
            self.assertEqual(sequential_days[2]['date'], '2025-08-15')
        else:
            result = self.client.get_trading_calendar(market='US')
            logger.debug(f"Trading Calendar:\n {result}")

    def test_get_stock_broker(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755068617474,
                         "data": {"symbol": "00700", "bidBroker": [{"level": 1, "price": 581.5, "brokerCount": 31,
                                                                    "broker": [{"id": "5337", "name": "J.P. Morgan"},
                                                                               {"id": "6998",
                                                                                "name": "China Investment"},
                                                                               {"id": "2204",
                                                                                "name": "TIGER BROKERS (HK)"},
                                                                               {"id": "2845", "name": "Macquarie"}]},
                                                                   {"level": 2, "price": 581.0, "brokerCount": 8,
                                                                    "broker": [
                                                                        {"id": "6996", "name": "China Investment"},
                                                                        {"id": "6999", "name": "China Investment"},
                                                                        {"id": "0757", "name": "Jefferies"}]},
                                                                   {"level": 3, "price": 580.5, "brokerCount": 1,
                                                                    "broker": [
                                                                        {"id": "6997", "name": "China Investment"}]}],
                                  "askBroker": [{"level": 1, "price": 582.0, "brokerCount": 40,
                                                 "broker": [{"id": "8594", "name": "KGI Asia"},
                                                            {"id": "5999", "name": "China Innovation"},
                                                            {"id": "5344", "name": "J.P. Morgan"},
                                                            {"id": "8136", "name": "BOCI"},
                                                            {"id": "8948", "name": "BOCI"}]}]}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取股票券商方法
            mock_result = self.client.get_stock_broker(symbol='00700')
            logger.debug(f"Stock Broker (mock):\n {mock_result}")

            # 验证返回对象是 StockBroker 类型
            self.assertIsNotNone(mock_result)
            from tigeropen.quote.domain.stock_broker import StockBroker
            self.assertIsInstance(mock_result, StockBroker)

            # 验证基本属性
            self.assertEqual(mock_result.symbol, '00700')

            # 验证买方券商数据
            self.assertIsNotNone(mock_result.bid_broker)
            self.assertEqual(len(mock_result.bid_broker), 3)  # 应该有3个买方价格等级

            # 验证第一个买方价格等级
            first_bid_level = mock_result.bid_broker[0]
            self.assertEqual(first_bid_level.level, 1)
            self.assertEqual(first_bid_level.price, 581.5)
            self.assertEqual(first_bid_level.broker_count, 31)
            self.assertEqual(len(first_bid_level.broker), 4)
            # 验证第一个买方券商
            self.assertEqual(first_bid_level.broker[0].id, '5337')
            self.assertEqual(first_bid_level.broker[0].name, 'J.P. Morgan')

            # 验证卖方券商数据
            self.assertIsNotNone(mock_result.ask_broker)
            self.assertEqual(len(mock_result.ask_broker), 1)  # 应该有1个卖方价格等级

            # 验证第一个卖方价格等级
            first_ask_level = mock_result.ask_broker[0]
            self.assertEqual(first_ask_level.level, 1)
            self.assertEqual(first_ask_level.price, 582.0)
            self.assertEqual(first_ask_level.broker_count, 40)
            self.assertEqual(len(first_ask_level.broker), 5)
            # 验证第一个卖方券商
            self.assertEqual(first_ask_level.broker[0].id, '8594')
            self.assertEqual(first_ask_level.broker[0].name, 'KGI Asia')
        else:
            # 实际调用API
            result = self.client.get_stock_broker(symbol='00700')
            logger.debug(f"Stock Broker (real):\n {result}")

    def test_get_broker_hold(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755073236671,
                         "data": {"page": 0, "totalPage": 14, "totalCount": 675, "items": [
                             {"orgId": "C00019", "orgName": "HONGKONG SHANGHAI BANKING", "date": "2025-08-12",
                              "sharesHold": 679751035124, "marketValue": 1.0840978605348338E13, "buyAmount": 25783546,
                              "buyAmount5": -1398518479, "buyAmount20": -1925856646, "buyAmount60": -11992723448,
                              "market": "HK"}]}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # Get result and assert
            mock_result = self.client.get_broker_hold()

            # Verify DataFrame structure and type
            self.assertIsInstance(mock_result, pd.DataFrame)
            self.assertEqual(len(mock_result), 1)  # Should contain one record

            # Verify pagination information
            self.assertEqual(mock_result['page'].iloc[0], 0)
            self.assertEqual(mock_result['total_page'].iloc[0], 14)
            self.assertEqual(mock_result['total_count'].iloc[0], 675)

            # Verify broker data fields
            self.assertEqual(mock_result['org_id'].iloc[0], 'C00019')
            self.assertEqual(mock_result['org_name'].iloc[0], 'HONGKONG SHANGHAI BANKING')
            self.assertEqual(mock_result['date'].iloc[0], '2025-08-12')
            self.assertEqual(mock_result['shares_hold'].iloc[0], 679751035124)
            self.assertEqual(mock_result['market_value'].iloc[0], 1.0840978605348338E13)
            self.assertEqual(mock_result['buy_amount'].iloc[0], 25783546)
            self.assertEqual(mock_result['buy_amount5'].iloc[0], -1398518479)
            self.assertEqual(mock_result['buy_amount20'].iloc[0], -1925856646)
            self.assertEqual(mock_result['buy_amount60'].iloc[0], -11992723448)
            self.assertEqual(mock_result['market'].iloc[0], 'HK')
        else:
            result = self.client.get_broker_hold()
            logger.debug(f"Broker Hold:\n {result}")

    def test_market_scanner(self):
        """测试市场扫描器功能"""
        if self.is_mock:
            # 模拟响应数据
            mock_data = {"code": 0, "message": "success", "timestamp": 1755069245307,
                         "data": {"page": 0, "totalPage": 1466, "totalCount": 7329, "pageSize": 5,
                                  "cursorId": "da16fdda-d784-4041-9e7e-4820a75d7b3c", "items": [
                                 {"symbol": "AAGH", "market": "US",
                                  "baseDataList": [{"index": 59, "name": "curChangeRate", "value": 0.5}],
                                  "accumulateDataList": [], "financialDataList": [],
                                  "multiTagDataList": [{"index": 4, "name": "symbol", "value": "AAGH"},
                                                       {"index": 21, "name": "marketName", "value": "US"}]},
                                 {"symbol": "ECHQF", "market": "US",
                                  "baseDataList": [{"index": 59, "name": "curChangeRate", "value": 0.5}],
                                  "accumulateDataList": [], "financialDataList": [],
                                  "multiTagDataList": [{"index": 4, "name": "symbol", "value": "ECHQF"},
                                                       {"index": 21, "name": "marketName", "value": "US"}]},
                                 {"symbol": "GTMLF", "market": "US",
                                  "baseDataList": [{"index": 59, "name": "curChangeRate", "value": 0.5}],
                                  "accumulateDataList": [], "financialDataList": [],
                                  "multiTagDataList": [{"index": 4, "name": "symbol", "value": "GTMLF"},
                                                       {"index": 21, "name": "marketName", "value": "US"}]},
                                 {"symbol": "IBXXF", "market": "US",
                                  "baseDataList": [{"index": 59, "name": "curChangeRate", "value": 0.5}],
                                  "accumulateDataList": [], "financialDataList": [],
                                  "multiTagDataList": [{"index": 4, "name": "symbol", "value": "IBXXF"},
                                                       {"index": 21, "name": "marketName", "value": "US"}]},
                                 {"symbol": "LEHNQ", "market": "US",
                                  "baseDataList": [{"index": 59, "name": "curChangeRate", "value": 0.5}],
                                  "accumulateDataList": [], "financialDataList": [],
                                  "multiTagDataList": [{"index": 4, "name": "symbol", "value": "LEHNQ"},
                                                       {"index": 21, "name": "marketName", "value": "US"}]}]}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
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
            logger.debug(f"Market Scanner (mock): {result}")
            # 验证返回的数据结构
            self.assertIsNotNone(result)
            self.assertEqual(result.page, 0)
            self.assertEqual(result.total_page, 1466)
            self.assertEqual(result.total_count, 7329)
            self.assertEqual(result.page_size, 5)
            # 验证返回的项目
            self.assertEqual(len(result.items), 5)
            self.assertEqual(len(result.symbols), 5)
            # 验证第一个项目
            first_item = result.items[0]
            self.assertEqual(first_item.symbol, 'AAGH')
            self.assertEqual(first_item.market, 'US')
            self.assertIn(StockField.current_ChangeRate, first_item.field_data)
            self.assertEqual(first_item.field_data[StockField.current_ChangeRate], 0.5)
            # 验证符号列表包含预期的股票代码
            expected_symbols = ['AAGH', 'ECHQF', 'GTMLF', 'IBXXF', 'LEHNQ']
            for symbol in expected_symbols:
                self.assertIn(symbol, result.symbols)

        else:
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
        """测试获取公司拆合股数据"""
        if self.is_mock:
            # 模拟响应数据
            mock_data = {"code": 0, "message": "success", "timestamp": 1755070680167,
                         "data": {"UVXY": [
                             {"symbol": "UVXY", "market": "US", "exchange": "CBOE", "executeDate": "2024-04-11",
                              "actionType": "SPLIT", "fromFactor": 5.0, "toFactor": 1.0, "ratio": 5.0}]}
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用方法获取拆合股数据
            result = self.client.get_corporate_split(symbols=['UVXY'],
                                                     market='US',
                                                     begin_date="2024-01-01",
                                                     end_date="2024-12-31")
            logger.debug(f"Corporate Action Split:\n {result}")

            # 验证返回结果
            self.assertIsNotNone(result)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)

            # 验证返回的数据结构
            expected_columns = ['symbol', 'action_type', 'from_factor', 'to_factor', 'ratio', 'execute_date', 'market',
                                'exchange']
            for col in expected_columns:
                self.assertIn(col, result.columns)

            # 验证返回的具体数据
            self.assertEqual(len(result), 1)
            self.assertEqual(result['symbol'][0], 'UVXY')
            self.assertEqual(result['action_type'][0], 'SPLIT')
            self.assertEqual(result['from_factor'][0], 5.0)
            self.assertEqual(result['to_factor'][0], 1.0)
            self.assertEqual(result['ratio'][0], 5.0)
            self.assertEqual(result['execute_date'][0], '2024-04-11')
            self.assertEqual(result['market'][0], 'US')
            self.assertEqual(result['exchange'][0], 'CBOE')
        else:
            # 实际调用API
            result = self.client.get_corporate_split(symbols=['UVXY'],
                                                     market='US',
                                                     begin_date="2024-01-01",
                                                     end_date="2024-12-31")
            logger.debug(f"Corporate Action Split:\n {result}")

    def test_get_financial_daily(self):
        """测试获取日级财务数据"""
        if self.is_mock:
            # 模拟响应数据
            mock_data = {"code": 0, "message": "success", "timestamp": 1755070929465, "data": [
                {"symbol": "AAPL", "date": 1672502400000, "field": "shares_outstanding", "value": 1.5908118E10},
                {"symbol": "AAPL", "date": 1672588800000, "field": "shares_outstanding", "value": 1.5908118E10},
                {"symbol": "AAPL", "date": 1672675200000, "field": "shares_outstanding", "value": 1.5908118E10},
                {"symbol": "AAPL", "date": 1672761600000, "field": "shares_outstanding", "value": 1.5908118E10},
                {"symbol": "AAPL", "date": 1672848000000, "field": "shares_outstanding", "value": 1.5908118E10}]
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用方法获取财务数据
            result = self.client.get_financial_daily(
                symbols=['AAPL'],
                market='US',
                fields=[Valuation.shares_outstanding],
                begin_date="2023-01-01",
                end_date="2023-12-31")
            logger.debug(f"Financial Daily:\n {result}")

            # 验证返回结果
            self.assertIsNotNone(result)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)

            # 验证返回的数据结构
            expected_columns = ['symbol', 'field', 'date', 'value']
            for col in expected_columns:
                self.assertIn(col, result.columns)

            self.assertEqual(len(result), 5)  # 模拟数据中有5条记录
            self.assertEqual(result['symbol'][0], 'AAPL')
            self.assertEqual(result['field'][0], 'shares_outstanding')
            self.assertEqual(result['date'][0], 1672502400000)  # 验证时间戳
            self.assertIsInstance(result['value'][0], float)
            self.assertAlmostEqual(result['value'][0], 1.5908118e+10, delta=1e+5)
        else:
            # 实际调用API
            result = self.client.get_financial_daily(
                symbols=['AAPL'],
                market='US',
                fields=[Valuation.shares_outstanding],
                begin_date="2023-01-01",
                end_date="2023-12-31")
            logger.debug(f"Financial Daily:\n {result}")

    def test_get_financial_report(self):
        """
        测试获取财务报表数据
        Tests retrieving financial report data
        """
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755071182333,
                         "data": [{"symbol": "AAPL", "currency": "USD", "field": "net_income", "value": "9.4321E10",
                                   "filingDate": "2024-05-03", "periodEndDate": "2023-04-01"},
                                  {"symbol": "AAPL", "currency": "USD", "field": "net_income", "value": "9.476E10",
                                   "filingDate": "2024-08-02", "periodEndDate": "2023-07-01"},
                                  {"symbol": "AAPL", "currency": "USD", "field": "net_income", "value": "9.6995E10",
                                   "filingDate": "2024-11-01", "periodEndDate": "2023-09-30"},
                                  {"symbol": "AAPL", "currency": "USD", "field": "net_income", "value": "1.00913E11",
                                   "filingDate": "2025-01-31", "periodEndDate": "2023-12-30"}]
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取财务报表方法
            mock_result = self.client.get_financial_report(
                symbols=['AAPL'],
                market='US',
                fields=[Income.net_income],
                period_type=FinancialPeriod.LTM,
                begin_date="2023-01-01",
                end_date="2023-12-31")
            logger.debug(f"Financial Report (mock): \n {mock_result}")

            # 验证返回结果
            self.assertIsInstance(mock_result, pd.DataFrame)
            self.assertEqual(len(mock_result), 4)  # 应该有4条记录

            # 验证数据框结构
            expected_columns = ['symbol', 'currency', 'field', 'value', 'period_end_date', 'filing_date']
            self.assertListEqual(list(mock_result.columns), expected_columns)

            # 验证第一条数据
            self.assertEqual(mock_result.iloc[0]['symbol'], 'AAPL')
            self.assertEqual(mock_result.iloc[0]['currency'], 'USD')
            self.assertEqual(mock_result.iloc[0]['field'], 'net_income')
            self.assertEqual(mock_result.iloc[0]['value'], '9.4321E10')
            self.assertEqual(mock_result.iloc[0]['period_end_date'], '2023-04-01')
            self.assertEqual(mock_result.iloc[0]['filing_date'], '2024-05-03')

            # 验证第四条数据
            self.assertEqual(mock_result.iloc[3]['symbol'], 'AAPL')
            self.assertEqual(mock_result.iloc[3]['value'], '1.00913E11')
            self.assertEqual(mock_result.iloc[3]['period_end_date'], '2023-12-30')
            self.assertEqual(mock_result.iloc[3]['filing_date'], '2025-01-31')

        else:
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
        """
        测试获取行业列表
        Tests retrieving industry list
        """
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755071779860, "data": [
                {"id": "5020", "industryLevel": "GGROUP", "nameCN": "媒体与娱乐", "nameEN": "Media & Entertainment"},
                {"id": "2550", "industryLevel": "GGROUP", "nameCN": "零售业",
                 "nameEN": "Consumer Discretionary Distribution & Retail"},
                {"id": "3510", "industryLevel": "GGROUP", "nameCN": "医疗保健设备与服务",
                 "nameEN": "Health Care Equipment & Services"}]
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取行业列表方法
            mock_result = self.client.get_industry_list()
            logger.debug(f"Industry List (mock): {mock_result}")

            # 验证返回结果
            self.assertIsInstance(mock_result, list)
            self.assertEqual(len(mock_result), 3)

            # 验证第一个行业信息
            first_industry = mock_result[0]
            self.assertIsInstance(first_industry, dict)
            self.assertEqual(first_industry['id'], '5020')
            self.assertEqual(first_industry['industry_level'], 'GGROUP')
            self.assertEqual(first_industry['name_cn'], '媒体与娱乐')
            self.assertEqual(first_industry['name_en'], 'Media & Entertainment')

            # 验证第二个行业信息
            second_industry = mock_result[1]
            self.assertEqual(second_industry['id'], '2550')
            self.assertEqual(second_industry['name_cn'], '零售业')
            self.assertEqual(second_industry['name_en'], 'Consumer Discretionary Distribution & Retail')

            # 验证第三个行业信息
            third_industry = mock_result[2]
            self.assertEqual(third_industry['id'], '3510')
            self.assertEqual(third_industry['name_cn'], '医疗保健设备与服务')
            self.assertEqual(third_industry['name_en'], 'Health Care Equipment & Services')

            # 验证所有必要的字段都存在
            required_fields = ['id', 'industry_level', 'name_cn', 'name_en']
            for industry in mock_result:
                for field in required_fields:
                    self.assertIn(field, industry, f"Field '{field}' missing in industry {industry}")

        else:
            result = self.client.get_industry_list()
            logger.debug(f"Industry List: {result}")

    def test_get_capital_flow(self):
        """
        测试获取资金流向数据
        Tests retrieving capital flow data
        """
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755072130182,
                         "data": {"symbol": "AAPL", "period": "day", "items": [
                             {"time": "2024-10-23", "timestamp": 1729656000000, "netInflow": -3.0512958226E8},
                             {"time": "2024-10-24", "timestamp": 1729742400000, "netInflow": -3.889793733E8},
                             {"time": "2024-10-25", "timestamp": 1729828800000, "netInflow": -3.0113531436E8},
                             {"time": "2024-10-28", "timestamp": 1730088000000, "netInflow": -1.662332963E7},
                             {"time": "2024-10-29", "timestamp": 1730174400000, "netInflow": -7.020034883E7}]}
                         }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取资金流向方法
            mock_result = self.client.get_capital_flow(symbol="AAPL",
                                                       market='US',
                                                       period=CapitalPeriod.DAY)
            logger.debug(f"Capital Flow (mock): \n{mock_result}")

            # 验证返回结果
            self.assertIsInstance(mock_result, pd.DataFrame)
            self.assertEqual(len(mock_result), 5)  # 验证返回5条记录

            # 验证数据框的列
            expected_columns = ['time', 'timestamp', 'net_inflow', 'symbol', 'period']
            self.assertListEqual(list(mock_result.columns), expected_columns)

            # 验证第一条记录内容
            self.assertEqual(mock_result.iloc[0]['time'], '2024-10-23')
            self.assertEqual(mock_result.iloc[0]['timestamp'], 1729656000000)
            self.assertEqual(mock_result.iloc[0]['net_inflow'], -3.0512958226E8)
            self.assertEqual(mock_result.iloc[0]['symbol'], 'AAPL')
            self.assertEqual(mock_result.iloc[0]['period'], 'day')

            # 验证最后一条记录内容
            self.assertEqual(mock_result.iloc[4]['time'], '2024-10-29')
            self.assertEqual(mock_result.iloc[4]['timestamp'], 1730174400000)
            self.assertEqual(mock_result.iloc[4]['net_inflow'], -7.020034883E7)

            # 验证净流入数据类型是浮点数
            self.assertIsInstance(mock_result['net_inflow'].iloc[0], float)

        else:
            result = self.client.get_capital_flow(symbol="AAPL",
                                                  market='US',
                                                  period=CapitalPeriod.DAY)
            logger.debug(f"Capital Flow: \n{result}")

    def test_get_capital_distribution(self):
        """
        测试获取资金分布数据
        Tests retrieving capital distribution data
        """
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755072571700,
                         "data": {"symbol": "AAPL", "netInflow": -2.8444076035E8, "inAll": 3.50150423605E9,
                                  "inBig": 3.6302115816980004E8, "inMid": 3.251985633328E8,
                                  "inSmall": 2.8132845145437512E9, "outAll": 3.7859449964E9, "outBig": 5.528750332554E8,
                                  "outMid": 3.326939928277004E8, "outSmall": 2.9003759703170733E9}}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # 调用获取资金分布方法
            mock_result = self.client.get_capital_distribution(symbol="AAPL", market='US')
            logger.debug(f"Capital Distribution (mock): \n {mock_result}")

            # 验证返回结果
            self.assertIsNotNone(mock_result, "Result should not be None")

            # 验证结果为CapitalDistribution对象
            self.assertEqual(mock_result.__class__.__name__, "CapitalDistribution")

            # 验证各个字段的值
            self.assertEqual(mock_result.symbol, "AAPL")
            self.assertEqual(mock_result.net_inflow, -2.8444076035E8)
            self.assertEqual(mock_result.in_all, 3.50150423605E9)
            self.assertEqual(mock_result.in_big, 3.6302115816980004E8)
            self.assertEqual(mock_result.in_mid, 3.251985633328E8)
            self.assertEqual(mock_result.in_small, 2.8132845145437512E9)
            self.assertEqual(mock_result.out_all, 3.7859449964E9)
            self.assertEqual(mock_result.out_big, 5.528750332554E8)
            self.assertEqual(mock_result.out_mid, 3.326939928277004E8)
            self.assertEqual(mock_result.out_small, 2.9003759703170733E9)

            # 验证净流入为所有流入减去所有流出的差
            self.assertAlmostEqual(mock_result.net_inflow, mock_result.in_all - mock_result.out_all, places=2)

            # 验证流入、流出类别金额之和与总量相符
            self.assertAlmostEqual(mock_result.in_big + mock_result.in_mid + mock_result.in_small,
                                   mock_result.in_all, places=2)
            self.assertAlmostEqual(mock_result.out_big + mock_result.out_mid + mock_result.out_small,
                                   mock_result.out_all, places=2)
        else:
            result = self.client.get_capital_distribution(symbol="AAPL", market='US')
            logger.debug(f"Capital Distribution: \n {result}")

    def test_get_kline_quota(self):
        if self.is_mock:
            mock_data = {"code": 0, "message": "success", "timestamp": 1755072687500,
                         "data": [{"remain": 1900, "used": 100, "method": "kline", "details": [], "symbolDetails": []},
                                  {"remain": 500, "used": 100, "method": "future_kline", "details": [],
                                   "symbolDetails": []},
                                  {"remain": 5000, "used": 0, "method": "option_kline", "details": [],
                                   "symbolDetails": []}]}
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # Get result and assert
            mock_result = self.client.get_kline_quota()

            # Basic assertions
            self.assertIsInstance(mock_result, list)
            self.assertEqual(len(mock_result), 3)

            # Check first item - kline
            self.assertEqual(mock_result[0]['method'], 'kline')
            self.assertEqual(mock_result[0]['remain'], 1900)
            self.assertEqual(mock_result[0]['used'], 100)
            self.assertIn('details', mock_result[0])
            self.assertIn('symbol_details', mock_result[0])

            # Check second item - future_kline
            self.assertEqual(mock_result[1]['method'], 'future_kline')
            self.assertEqual(mock_result[1]['remain'], 500)
            self.assertEqual(mock_result[1]['used'], 100)

            # Check third item - option_kline
            self.assertEqual(mock_result[2]['method'], 'option_kline')
            self.assertEqual(mock_result[2]['remain'], 5000)
            self.assertEqual(mock_result[2]['used'], 0)
        else:
            result = self.client.get_kline_quota()
            logger.debug(f"Kline Quota:\n {result}")
