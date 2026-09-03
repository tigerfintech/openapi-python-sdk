import unittest

import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.fundamental.response.corporate_dividend_response import CorporateDividendResponse
from tigeropen.fundamental.response.dataframe_response import DataframeResponse
from tigeropen.fundamental.response.financial_exchange_rate_response import FinancialExchangeRateResponse
from tigeropen.quote.response.quote_bar_response import QuoteBarResponse
from tigeropen.quote.response.quote_brief_response import QuoteBriefResponse
from tigeropen.quote.response.quote_dataframe_response import QuoteDataframeResponse
from tigeropen.quote.response.stock_briefs_response import StockBriefsResponse
from tigeropen.quote.response.quote_timeline_response import QuoteTimelineResponse
from tigeropen.quote.response.stock_short_interest_response import ShortInterestResponse
from tigeropen.trade.response.assets_response import AssetsResponse
from tigeropen.trade.response.segment_fund_response import (
    SegmentFundAvailableResponse,
    SegmentFundCancelResponse,
    SegmentFundHistoryResponse,
    SegmentFundTransferResponse,
)

import pytest


# 纯单测：永远不碰真实接口，contract / integ job 会跳过
pytestmark = pytest.mark.unit


class TestBaseResponse(unittest.TestCase):

    def test_parse_fields_and_json_encoded_data(self):
        response = TigerResponse()
        parsed = response.parse_response_content({
            'code': 0,
            'message': 'success',
            'data': '{"items": [1, 2]}',
        })
        self.assertEqual(parsed['code'], 0)
        self.assertTrue(response.is_success())
        self.assertEqual(response.data, {'items': [1, 2]})


class TestDataframeResponses(unittest.TestCase):

    def test_quote_bar_volume_decimal_mapping_and_stock_omission(self):
        crypto = QuoteBarResponse()
        crypto.parse_response_content({
            'code': 0,
            'data': [{'symbol': 'BTCUSD', 'items': [{
                'time': 1754366400000,
                'volume': 1,
                'volumeDecimal': 0.00012345,
            }]}],
        })
        self.assertEqual(crypto.result.iloc[0]['volume_decimal'], 0.00012345)

        stock = QuoteBarResponse()
        stock.parse_response_content({
            'code': 0,
            'data': [{'symbol': 'AAPL', 'items': [{'volume': 123}]}],
        })
        self.assertNotIn('volume_decimal', stock.result.columns)

    def test_quote_bar_explicit_null_volume_decimal_retains_nullable_column(self):
        response = QuoteBarResponse()
        response.parse_response_content({
            'code': 0,
            'data': [{'symbol': 'AAPL', 'items': [{
                'volume': 123,
                'volumeDecimal': None,
            }]}],
        })

        self.assertIn('volume_decimal', response.result.columns)
        self.assertTrue(pd.isna(response.result.iloc[0]['volume_decimal']))

    def test_quote_timeline_volume_decimal_mapping_and_stock_omission(self):
        crypto = QuoteTimelineResponse()
        crypto.parse_response_content({
            'code': 0,
            'data': [{'symbol': 'BTCUSD', 'preClose': 115000.0, 'intraday': {'items': [{
                'time': 1754919000000,
                'volume': 1,
                'volumeDecimal': 0.00012345,
            }]}}],
        })
        self.assertEqual(crypto.result.iloc[0]['volume_decimal'], 0.00012345)

        stock = QuoteTimelineResponse()
        stock.parse_response_content({
            'code': 0,
            'data': [{'symbol': 'AAPL', 'preClose': 200.0, 'intraday': {'items': [{'volume': 123}]}}],
        })
        self.assertNotIn('volume_decimal', stock.result.columns)

    def test_quote_timeline_explicit_null_volume_decimal_omits_key(self):
        response = QuoteTimelineResponse()
        response.parse_response_content({
            'code': 0,
            'data': [{'symbol': 'AAPL', 'preClose': 200.0, 'intraday': {'items': [{
                'volume': 123,
                'volumeDecimal': None,
            }]}}],
        })

        self.assertNotIn('volume_decimal', response.result.columns)

    def test_generic_dataframe_response(self):
        response = DataframeResponse()
        response.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': [{'reportDate': '2026-01-01', 'netIncome': 10}],
        })
        self.assertTrue(response._is_success)
        self.assertEqual(list(response.result.columns), ['report_date', 'net_income'])
        self.assertEqual(response.result.iloc[0]['net_income'], 10)

    def test_quote_dataframe_list_and_dict_shapes(self):
        list_response = QuoteDataframeResponse()
        list_response.parse_response_content({
            'code': 0,
            'data': [
                {'symbol': 'AAPL', 'items': [{'latestPrice': 100}]},
                {'symbol': 'MSFT', 'items': [{'latestPrice': 200}]},
            ],
        })
        self.assertEqual(list(list_response.result['symbol']), ['AAPL', 'MSFT'])
        self.assertEqual(list(list_response.result['latest_price']), [100, 200])

        dict_response = QuoteDataframeResponse()
        dict_response.parse_response_content({'code': 0, 'data': {'items': [{'tradeDate': '2026-01-01'}]}})
        self.assertEqual(list(dict_response.result.columns), ['trade_date'])

        empty_response = QuoteDataframeResponse()
        self.assertIsNone(empty_response.parse_response_content({'code': 0, 'data': []}))
        self.assertIsNone(empty_response.result)

    def test_quote_brief_amount_mapping(self):
        response = QuoteBriefResponse()
        response.parse_response_content({
            'code': 0,
            'data': {'items': [{
                'symbol': 'AAPL',
                'latestPrice': 100,
                'volume': 123,
                'amount': 4567.89,
            }]},
        })

        self.assertEqual(response.briefs[0].symbol, 'AAPL')
        self.assertEqual(response.briefs[0].amount, 4567.89)

    def test_stock_briefs_amount_mapping_for_stock_and_crypto(self):
        response = StockBriefsResponse()
        response.parse_response_content({
            'code': 0,
            'data': [
                {'symbol': 'AAPL', 'latestPrice': 100, 'volume': 123, 'amount': 4567.89},
                {'symbol': 'BTCUSD', 'latestPrice': 65000, 'volume': 0, 'amount': 987654.32},
            ],
        })

        self.assertEqual(list(response.briefs['symbol']), ['AAPL', 'BTCUSD'])
        self.assertIn('amount', response.briefs.columns)
        self.assertEqual(list(response.briefs['amount']), [4567.89, 987654.32])

    def test_dividend_exchange_rate_and_short_interest(self):
        dividend = CorporateDividendResponse()
        dividend.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {'AAPL': [{'actionType': 'DIVIDEND', 'amount': 0.25, 'payDate': '2026-02-01'}]},
        })
        self.assertEqual(dividend.corporate_dividend.iloc[0]['symbol'], 'AAPL')
        self.assertEqual(dividend.corporate_dividend.iloc[0]['action_type'], 'DIVIDEND')
        self.assertIn('announced_date', dividend.corporate_dividend.columns)

        rates = FinancialExchangeRateResponse()
        rates.parse_response_content({
            'code': 0,
            'data': [
                {'currency': 'USD', 'dailyValueList': [{'date': '2026-01-01', 'rate': 1.0}]},
                {'currency': 'HKD', 'dailyValueList': [{'date': '2026-01-01', 'rate': 7.8}]},
            ],
        })
        self.assertEqual(list(rates.result['currency']), ['USD', 'HKD'])

        short_interest = ShortInterestResponse()
        short_interest.parse_response_content({
            'code': 0,
            'data': [{'symbol': 'AAPL', 'items': [{
                'settlementDate': '2026-01-15',
                'shortInterest': 100,
                'avgDailyVolume': 20,
                'daysToCover': 5,
                'percentOfFloat': None,
            }]}],
        })
        row = short_interest.short_interests.iloc[0]
        self.assertEqual((row['symbol'], row['short_interest'], row['days_to_cover']), ('AAPL', 100, 5))
        self.assertTrue(pd.isna(row['percent_of_float']))


class TestTradeResponses(unittest.TestCase):

    def test_assets_response_dict_shapes(self):
        response = AssetsResponse()
        response.parse_response_content({
            'code': 0,
            'is_success': True,
            'data': {'items': [{
                'account': 'DU123',
                'netLiquidation': 1000,
                'updateTime': 123,
                'ignoredField': None,
                'marketValues': {
                    'USD': {'currency': 'USD', 'cashBalance': 500, 'updateTime': 123},
                },
                'segments': {
                    'S': {'cash': 400, 'netLiquidation': 900},
                    'C': {'cash': 100},
                },
            }]},
        })
        asset = response.assets[0]
        self.assertEqual((asset.account, asset.summary.net_liquidation, asset.summary.timestamp), ('DU123', 1000, 123))
        self.assertEqual(asset.market_values['USD'].cash_balance, 500)
        self.assertEqual(asset.market_values['USD'].timestamp, 123)
        self.assertEqual(asset.segments['S'].cash, 400)
        self.assertEqual(asset.segments['C'].cash, 100)

    def test_assets_response_list_shapes_and_missing_keys(self):
        response = AssetsResponse()
        response.parse_response_content({
            'code': 0,
            'data': {'items': [{
                'account': 'DU456',
                'marketValues': [
                    {'currency': 'HKD', 'stockMarketValue': 300},
                    {'stockMarketValue': 999},
                ],
                'segments': [
                    {'category': 'F', 'cash': 200},
                    {'cash': 999},
                ],
            }]},
        })
        asset = response.assets[0]
        self.assertEqual(asset.market_values['HKD'].stock_market_value, 300)
        self.assertEqual(asset.segments['F'].cash, 200)
        self.assertEqual(len(asset.market_values), 1)
        self.assertEqual(len(asset.segments), 1)

    def test_segment_fund_responses(self):
        available = SegmentFundAvailableResponse()
        available.parse_response_content({
            'code': 0,
            'data': [{'fromSegment': 'S', 'currency': 'USD', 'amount': 100}],
        })
        self.assertEqual((available.data[0].from_segment, available.data[0].amount), ('S', 100))

        payload = {
            'id': 1,
            'fromSegment': 'S',
            'toSegment': 'C',
            'statusDesc': 'Pending',
            'createdAt': 123,
        }
        history = SegmentFundHistoryResponse()
        history.parse_response_content({'code': 0, 'data': [payload]})
        self.assertEqual((history.data[0].to_segment, history.data[0].status_desc), ('C', 'Pending'))

        transfer = SegmentFundTransferResponse()
        parsed = transfer.parse_response_content({'code': 0, 'is_success': True, 'data': payload})
        self.assertEqual(parsed['code'], 0)
        self.assertTrue(transfer._is_success)
        self.assertEqual(transfer.data.created_at, 123)

        cancel = SegmentFundCancelResponse()
        cancel.parse_response_content({'code': 0, 'data': payload})
        self.assertEqual(cancel.data.id, 1)


if __name__ == '__main__':
    unittest.main()
