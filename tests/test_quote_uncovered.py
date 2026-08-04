# -*- coding: utf-8 -*-
"""Unit tests for previously uncovered wire methods (auto-generated)."""
import json
import unittest
from unittest.mock import MagicMock

import pytest

from tigeropen.common.util import web_utils
from tigeropen.quote.quote_client import QuoteClient
from tests.support import client_config

pytestmark = pytest.mark.unit


class TestUncoveredQuoteClient(unittest.TestCase):

    def setUp(self):
        self.client_config = client_config()
        self.client = QuoteClient(self.client_config, is_grab_permission=False)
        self.origin_do_request = web_utils.do_request

    def tearDown(self):
        web_utils.do_request = self.origin_do_request

    def test_get_financial_currency(self):
        """Covers wire method FINANCIAL_CURRENCY."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_financial_currency("AAPL", "US")
        # Wire method FINANCIAL_CURRENCY exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_financial_exchange_rate(self):
        """Covers wire method FINANCIAL_EXCHANGE_RATE."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_financial_exchange_rate(None, None)
        # Wire method FINANCIAL_EXCHANGE_RATE exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_fund_symbols(self):
        """Covers wire method FUND_ALL_SYMBOLS."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_fund_symbols()
        # Wire method FUND_ALL_SYMBOLS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_fund_contracts(self):
        """Covers wire method FUND_CONTRACTS."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_fund_contracts(["AAPL"])
        # Wire method FUND_CONTRACTS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_fund_history_quote(self):
        """Covers wire method FUND_HISTORY_QUOTE."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_fund_history_quote("AAPL", None, None)
        # Wire method FUND_HISTORY_QUOTE exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_fund_quote(self):
        """Covers wire method FUND_QUOTE."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_fund_quote(["AAPL"])
        # Wire method FUND_QUOTE exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_quote_permission(self):
        """Covers wire method GET_QUOTE_PERMISSION."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_quote_permission()
        # Wire method GET_QUOTE_PERMISSION exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_grab_quote_permission(self):
        """Covers wire method GRAB_QUOTE_PERMISSION."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.grab_quote_permission()
        # Wire method GRAB_QUOTE_PERMISSION exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_industry_stocks(self):
        """Covers wire method INDUSTRY_STOCKS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_industry_stocks(None)
        # Wire method INDUSTRY_STOCKS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_market_scanner_tags(self):
        """Covers wire method MARKET_SCANNER_TAGS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_market_scanner_tags()
        # Wire method MARKET_SCANNER_TAGS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_quote_overnight(self):
        """Covers wire method QUOTE_OVERNIGHT."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_quote_overnight(["AAPL"])
        # Wire method QUOTE_OVERNIGHT exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_short_interest(self):
        """Covers wire method QUOTE_SHORTABLE_STOCKS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_short_interest(["AAPL"])
        # Wire method QUOTE_SHORTABLE_STOCKS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_stock_details(self):
        """Covers wire method STOCK_DETAIL."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_stock_details(["AAPL"])
        # Wire method STOCK_DETAIL exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_stock_fundamental(self):
        """Covers wire method STOCK_FUNDAMENTAL."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_stock_fundamental("AAPL", "US")
        # Wire method STOCK_FUNDAMENTAL exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_stock_industry(self):
        """Covers wire method STOCK_INDUSTRY."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_stock_industry(["AAPL"])
        # Wire method STOCK_INDUSTRY exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_trade_rank(self):
        """Covers wire method TRADE_RANK."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_trade_rank(market="US")
        # Wire method TRADE_RANK exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_warrant_filter(self):
        """Covers wire method WARRANT_FILTER."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_warrant_filter(["AAPL"])
        # Wire method WARRANT_FILTER exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_warrant_briefs(self):
        """Covers wire method WARRANT_REAL_TIME_QUOTE."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_warrant_briefs(["AAPL"])
        # Wire method WARRANT_REAL_TIME_QUOTE exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()
