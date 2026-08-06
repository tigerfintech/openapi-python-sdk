# -*- coding: utf-8 -*-
"""Unit tests for low-coverage domain classes and response parsers."""
import json
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

import pytest

from tigeropen.common.consts import THREAD_LOCAL
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import web_utils
from tigeropen.common.exceptions import RequestException, ResponseException
from tigeropen.quote.domain.bar import Bar
from tigeropen.quote.domain.tick import TradeTick
from tigeropen.quote.domain.timeline import Timeline
from tigeropen.quote.domain.option_analysis import OptionAnalysis, IVMetric, VolatilityListItem
from tigeropen.quote.domain.filter import WarrantFilterItem, WarrantFilterBounds
from tigeropen.quote.response.trade_rank_response import TradeRankResponse
from tigeropen.quote.response.option_briefs_response import OptionBriefsResponse
from tigeropen.quote.response.option_analysis_response import OptionAnalysisResponse
from tigeropen.quote.response.fund_contracts_response import FundContractsResponse
from tigeropen.quote.response.future_depth_response import FutureDepthResponse
from tigeropen.quote.response.warrant_filter_response import WarrantFilterResponse
from tigeropen.quote.response.warrant_briefs_response import WarrantBriefsResponse
from tigeropen.trade.domain.profile import AccountProfile
from tigeropen.trade.response.fund_details_response import FundDetailsResponse
from tigeropen.trade.response.funding_history_response import FundingHistoryResponse
from tigeropen.trade.response.analytics_asset_response import AnalyticsAssetResponse
from tigeropen.trade.response.account_profile_response import ProfilesResponse
from tigeropen.fundamental.response.corporate_earnings_calendar_response import EarningsCalendarResponse
from tigeropen.fundamental.response.industry_response import (
    IndustryListResponse,
    IndustryStocksResponse,
    StockIndustryResponse,
)

pytestmark = pytest.mark.unit


class TestDomainClasses(unittest.TestCase):
    """Test simple domain data classes with 0% / low coverage."""

    def test_bar_construction_and_repr(self):
        bar = Bar()
        bar.time = 1700000000
        bar.open = 100.0
        bar.high = 105.0
        bar.low = 99.0
        bar.close = 103.0
        bar.volume = 10000
        self.assertEqual(bar.open, 100.0)
        self.assertEqual(bar.volume, 10000)
        repr_str = repr(bar)
        self.assertIn("Bar(", repr_str)
        self.assertIn("'open'", repr_str)

    def test_trade_tick_construction_and_repr(self):
        tick = TradeTick()
        tick.index = 1
        tick.timestamp = 1700000000
        tick.price = 150.0
        tick.size = 100
        tick.direction = 1
        self.assertEqual(tick.price, 150.0)
        repr_str = repr(tick)
        self.assertIn("TradeTick(", repr_str)
        self.assertIn("'price'", repr_str)

    def test_timeline_construction_and_repr(self):
        tl = Timeline()
        tl.latest_time = 1700000000
        tl.price = 200.0
        tl.avg_price = 198.0
        tl.volume = 5000
        self.assertEqual(tl.price, 200.0)
        repr_str = repr(tl)
        self.assertIn("Timeline(", repr_str)
        self.assertIn("'avg_price'", repr_str)

    def test_account_profile_construction_and_repr(self):
        profile = AccountProfile(account="ACC001", capability="TRADE", status="ACTIVE")
        self.assertEqual(profile.account, "ACC001")
        self.assertEqual(profile.capability, "TRADE")
        self.assertEqual(profile.status, "ACTIVE")
        self.assertIsNone(profile.account_type)

        profile2 = AccountProfile(account="ACC002", capability="TRADE", status="ACTIVE", account_type="MARGIN")
        self.assertEqual(profile2.account_type, "MARGIN")
        repr_str = repr(profile2)
        self.assertIn("AccountProfile(", repr_str)
        self.assertIn("'account'", repr_str)

    def test_option_analysis_domain_objects(self):
        analysis = OptionAnalysis()
        analysis.symbol = "AAPL"
        analysis.implied_vol_30_days = 0.35
        repr_str = repr(analysis)
        self.assertIn("OptionAnalysis(", repr_str)

        iv = IVMetric()
        iv.period = "52week"
        iv.percentile = 0.65
        iv.rank = 0.7
        self.assertEqual(iv.period, "52week")
        self.assertIn("IVMetric(", repr(iv))

        vol = VolatilityListItem()
        vol.implied_vol = 0.4
        vol.timestamp = 1700000000
        self.assertEqual(vol.implied_vol, 0.4)
        self.assertIn("VolatilityListItem(", repr(vol))

    def test_warrant_filter_domain_objects(self):
        bounds = WarrantFilterBounds(
            issuer_name={"IssuerA"},
            expire_date={"2026-01-01"},
            lot_size={1000},
            entitlement_ratio={1.0},
            leverage_ratio=2.5,
            strike=150.0,
        )
        self.assertEqual(bounds.leverage_ratio, 2.5)
        self.assertIn("IssuerA", bounds.issuer_name)
        self.assertEqual(bounds.call_price, None)
        repr_str = repr(bounds)
        self.assertIn("FilterBounds(", repr_str)

        item = WarrantFilterItem(items=pd.DataFrame(), page=1, total_page=5, total_count=100, bounds=bounds)
        self.assertEqual(item.page, 1)
        self.assertIs(item.bounds, bounds)
        self.assertIn("WarrantFilterItem(", repr(item))


class TestTradeRankResponse(unittest.TestCase):

    def test_parse_with_data(self):
        resp = TradeRankResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {'symbol': 'AAPL', 'volume': 10000, 'hourTrading': {'volume': 500}},
                {'symbol': 'MSFT', 'volume': 8000},
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertFalse(resp.result.empty)
        self.assertIn('hour_trading_volume', resp.result.columns)

    def test_parse_empty_data(self):
        resp = TradeRankResponse()
        resp.parse_response_content({'code': 0, 'data': []})
        self.assertTrue(resp.result.empty)


class TestFundDetailsResponse(unittest.TestCase):

    def test_parse_with_items(self):
        resp = FundDetailsResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {
                'items': [{'fundCode': 'FU001', 'fundName': 'Test Fund'}],
                'page': 1,
                'limit': 10,
                'itemCount': 1,
                'pageCount': 1,
                'timestamp': 1700000000,
            },
        })
        self.assertTrue(resp._is_success)
        self.assertFalse(resp.result.empty)
        self.assertIn('fund_code', resp.result.columns)
        self.assertEqual(resp.result.iloc[0]['page'], 1)

    def test_parse_without_items(self):
        resp = FundDetailsResponse()
        resp.parse_response_content({'code': 0, 'data': {'page': 1}})
        self.assertTrue(resp.result.empty)


class TestFundingHistoryResponse(unittest.TestCase):

    def test_parse_list_data(self):
        resp = FundingHistoryResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {'amount': 100.0, 'currency': 'USD'},
                {'amount': 200.0, 'currency': 'HKD'},
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertFalse(resp.result.empty)
        self.assertEqual(len(resp.result), 2)

    def test_parse_single_dict_data(self):
        resp = FundingHistoryResponse()
        resp.parse_response_content({
            'code': 0,
            'data': {'amount': 50.0, 'currency': 'USD'},
        })
        self.assertFalse(resp.result.empty)
        self.assertEqual(len(resp.result), 1)


class TestAnalyticsAssetResponse(unittest.TestCase):

    def test_parse_with_history(self):
        resp = AnalyticsAssetResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {
                'totalValue': 100000,
                'history': [
                    {'date': 1700006400000, 'value': 99000},
                    {'date': 1700086400000, 'value': 100000},
                ],
            },
        })
        self.assertTrue(resp._is_success)
        self.assertIsNotNone(resp.result)
        self.assertEqual(resp.result['total_value'], 100000)
        self.assertEqual(resp.result['history'][0]['dt'], '2023-11-15')

    def test_parse_without_data(self):
        resp = AnalyticsAssetResponse()
        resp.parse_response_content({'code': 0, 'data': None})
        self.assertIsNone(resp.result)


class TestProfilesResponse(unittest.TestCase):

    def test_parse_with_items(self):
        resp = ProfilesResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {
                'items': [
                    {'account': 'ACC001', 'capability': 'TRADE', 'status': 'ACTIVE', 'accountType': 'MARGIN'},
                    {'account': 'ACC002', 'capability': 'QUOTE', 'status': 'INACTIVE'},
                ],
            },
        })
        self.assertTrue(resp._is_success)
        self.assertEqual(len(resp.profiles), 2)
        self.assertEqual(resp.profiles[0].account, 'ACC001')
        self.assertEqual(resp.profiles[0].account_type, 'MARGIN')
        self.assertIsNone(resp.profiles[1].account_type)

    def test_parse_empty(self):
        resp = ProfilesResponse()
        resp.parse_response_content({'code': 0, 'data': None})
        self.assertEqual(len(resp.profiles), 0)


class TestOptionBriefsResponse(unittest.TestCase):

    def test_parse_with_identifier(self):
        resp = OptionBriefsResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {'identifier': 'AAPL20260119C00150000', 'symbol': 'AAPL', 'right': 'CALL',
                 'strike': 150.0, 'expiry': 1700000000000, 'open': 5.0, 'openInt': 100},
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertFalse(resp.briefs.empty)
        self.assertIn('put_call', resp.briefs.columns)
        self.assertIn('open_interest', resp.briefs.columns)

    def test_parse_without_identifier_us_option(self):
        resp = OptionBriefsResponse()
        resp.parse_response_content({
            'code': 0,
            'data': [
                {'symbol': 'AAPL', 'right': 'PUT', 'strike': 145.0, 'expiry': 1700000000000},
            ],
        })
        self.assertFalse(resp.briefs.empty)
        self.assertIn('identifier', resp.briefs.columns)

    def test_parse_empty(self):
        resp = OptionBriefsResponse()
        resp.parse_response_content({'code': 0, 'data': []})
        self.assertIsNone(resp.briefs)


class TestOptionAnalysisResponse(unittest.TestCase):

    def test_parse_full_data(self):
        resp = OptionAnalysisResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {
                    'symbol': 'AAPL',
                    'impliedVol30Days': 0.35,
                    'hisVolatility': 0.30,
                    'ivHisVRatio': 1.17,
                    'callPutRatio': 1.5,
                    'impliedVolMetric': {'period': '52week', 'percentile': 0.65, 'rank': 0.7},
                    'volatilityList': [
                        {'impliedVol': 0.35, 'percentile': 0.6, 'timestamp': 1700000000000},
                    ],
                },
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertEqual(len(resp.analysis_list), 1)
        analysis = resp.analysis_list[0]
        self.assertEqual(analysis.symbol, 'AAPL')
        self.assertEqual(analysis.implied_vol_30_days, 0.35)
        self.assertEqual(analysis.iv_his_v_ratio, 1.17)
        self.assertIsNotNone(analysis.iv_metric)
        self.assertEqual(analysis.iv_metric.period, '52week')
        self.assertEqual(len(analysis.volatility_list), 1)
        self.assertEqual(analysis.volatility_list[0].implied_vol, 0.35)

    def test_parse_empty_data(self):
        resp = OptionAnalysisResponse()
        resp.parse_response_content({'code': 0, 'data': None})
        self.assertEqual(resp.analysis_list, [])

    def test_parse_non_list_data(self):
        resp = OptionAnalysisResponse()
        resp.parse_response_content({'code': 0, 'data': {'key': 'value'}})
        self.assertEqual(resp.analysis_list, [])


class TestFundContractsResponse(unittest.TestCase):

    def test_parse_list_data(self):
        resp = FundContractsResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {'fundCode': 'FU001', 'fundName': 'Test', 'netAsset': 1000000},
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertIsNotNone(resp.result)
        self.assertIn('fund_code', resp.result.columns)

    def test_parse_empty(self):
        resp = FundContractsResponse()
        resp.parse_response_content({'code': 0, 'data': []})
        self.assertIsNone(resp.result)


class TestFutureDepthResponse(unittest.TestCase):

    def test_parse_single_contract(self):
        resp = FutureDepthResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {
                    'contractCode': 'CL2024',
                    'ask': [{'price': 75.0, 'volume': 10}, {'price': 75.1, 'volume': 20}],
                    'bid': [{'price': 74.9, 'volume': 15}, {'price': 74.8, 'volume': 25}],
                },
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertEqual(resp.result['identifier'], 'CL2024')
        self.assertEqual(len(resp.result['asks']), 2)
        self.assertEqual(resp.result['asks'][0], (75.0, 10))

    def test_parse_multiple_contracts(self):
        resp = FutureDepthResponse()
        resp.parse_response_content({
            'code': 0,
            'data': [
                {'contractCode': 'CL2024', 'ask': [{'price': 75.0, 'volume': 10}], 'bid': []},
                {'contractCode': 'NG2024', 'ask': [], 'bid': [{'price': 2.5, 'volume': 5}]},
            ],
        })
        self.assertIn('CL2024', resp.result)
        self.assertIn('NG2024', resp.result)
        self.assertEqual(resp.result['CL2024']['asks'], [(75.0, 10)])
        self.assertEqual(resp.result['NG2024']['bids'], [(2.5, 5)])

    def test_parse_empty(self):
        resp = FutureDepthResponse()
        resp.parse_response_content({'code': 0, 'data': []})
        self.assertEqual(resp.result, {})


class TestWarrantFilterResponse(unittest.TestCase):

    def test_parse_with_data(self):
        resp = WarrantFilterResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {
                'page': 1,
                'totalPage': 3,
                'totalCount': 50,
                'items': [{'symbol': 'ABC', 'name': 'Warrant ABC'}],
                'bounds': {
                    'issuerName': ['IssuerA'],
                    'expireDate': ['2026-01-01'],
                    'lotSize': [1000],
                    'entitlementRatio': [1.0],
                },
            },
        })
        self.assertTrue(resp._is_success)
        self.assertIsNotNone(resp.result)
        self.assertEqual(resp.result.page, 1)
        self.assertEqual(resp.result.total_page, 3)
        self.assertFalse(resp.result.items.empty)


class TestWarrantBriefsResponse(unittest.TestCase):

    def test_parse_with_items(self):
        resp = WarrantBriefsResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {'items': [{'symbol': 'ABC', 'warrantType': 'CALL'}]},
        })
        self.assertTrue(resp._is_success)
        self.assertFalse(resp.result.empty)
        self.assertIn('warrant_type', resp.result.columns)

    def test_parse_empty(self):
        resp = WarrantBriefsResponse()
        resp.parse_response_content({'code': 0, 'data': {}})
        self.assertIsNone(resp.result)


class TestEarningsCalendarResponse(unittest.TestCase):

    def test_parse_with_data(self):
        resp = EarningsCalendarResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {
                'US': [
                    {'symbol': 'AAPL', 'reportDate': '2026-01-15', 'reportTime': 'AMC',
                     'expectedEps': 1.5, 'actualEps': 1.6, 'executeDate': '2026-01-20',
                     'fiscalQuarterEnding': 'Q1', 'exchange': 'NASDAQ', 'market': 'US',
                     'actionType': 'EARNINGS'},
                ],
            },
        })
        self.assertTrue(resp._is_success)
        self.assertIsNotNone(resp.earnings_calendar)
        self.assertIn('action_type', resp.earnings_calendar.columns)
        self.assertIn('expected_eps', resp.earnings_calendar.columns)
        self.assertEqual(len(resp.earnings_calendar), 1)

    def test_parse_empty(self):
        resp = EarningsCalendarResponse()
        resp.parse_response_content({'code': 0, 'data': None})
        self.assertIsNone(resp.earnings_calendar)


class TestIndustryResponses(unittest.TestCase):

    def test_industry_list_response(self):
        resp = IndustryListResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {'industryLevel': 1, 'id': 100, 'nameCN': '科技', 'nameEN': 'Technology'},
                {'industryLevel': 2, 'id': 200, 'nameCN': '金融', 'nameEN': 'Finance'},
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertEqual(len(resp.industry_list), 2)
        self.assertEqual(resp.industry_list[0]['industry_level'], 1)
        self.assertEqual(resp.industry_list[0]['name_cn'], '科技')
        self.assertEqual(resp.industry_list[1]['name_en'], 'Finance')

    def test_industry_list_empty(self):
        resp = IndustryListResponse()
        resp.parse_response_content({'code': 0, 'data': None})
        self.assertEqual(len(resp.industry_list), 0)

    def test_industry_stocks_response(self):
        resp = IndustryStocksResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {
                    'symbol': 'AAPL',
                    'companyName': 'Apple Inc',
                    'market': 'US',
                    'industryDetailDTOList': [
                        {'industryLevel': 1, 'id': 100, 'nameCN': '科技', 'nameEN': 'Technology'},
                    ],
                },
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertEqual(len(resp.industry_stocks), 1)
        stock = resp.industry_stocks[0]
        self.assertEqual(stock['symbol'], 'AAPL')
        self.assertEqual(stock['company_name'], 'Apple Inc')
        self.assertEqual(len(stock['industry_list']), 1)
        self.assertEqual(stock['industry_list'][0]['name_cn'], '科技')

    def test_stock_industry_response(self):
        resp = StockIndustryResponse()
        resp.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [
                {'industryLevel': 1, 'id': 100, 'nameCN': '科技', 'nameEN': 'Technology'},
            ],
        })
        self.assertTrue(resp._is_success)
        self.assertEqual(len(resp.stock_industry), 1)
        self.assertEqual(resp.stock_industry[0]['name_en'], 'Technology')


class TestWebUtils(unittest.TestCase):
    """Test web_utils with mocked urllib3 PoolManager."""

    def setUp(self):
        THREAD_LOCAL.uuid = 'test-uuid'

    @patch('tigeropen.common.util.web_utils.http_pool')
    def test_do_post_success(self, mock_pool):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.data = b'{"code": 0}'
        mock_pool.request.return_value = mock_response

        result = web_utils.do_post('https://example.com', params={'key': 'value'})
        self.assertEqual(result, b'{"code": 0}')
        mock_pool.request.assert_called_once()

    @patch('tigeropen.common.util.web_utils.http_pool')
    def test_do_get_success(self, mock_pool):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.data = b'{"data": []}'
        mock_pool.request.return_value = mock_response

        result = web_utils.do_get('https://example.com')
        self.assertEqual(result, b'{"data": []}')

    @patch('tigeropen.common.util.web_utils.http_pool')
    def test_do_request_request_exception(self, mock_pool):
        mock_pool.request.side_effect = Exception('Connection refused')
        with self.assertRaises(RequestException):
            web_utils.do_request('GET', url='https://example.com')

    @patch('tigeropen.common.util.web_utils.http_pool')
    def test_do_request_response_exception(self, mock_pool):
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.data = b'Internal Server Error'
        mock_pool.request.return_value = mock_response

        with self.assertRaises(ResponseException):
            web_utils.do_request('GET', url='https://example.com')
