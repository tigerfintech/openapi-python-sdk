# -*- coding: utf-8 -*-
"""Unit tests for previously uncovered wire methods (auto-generated)."""
import json
import unittest
from unittest.mock import MagicMock

import pytest

from tigeropen.common.util import web_utils
from tigeropen.trade.trade_client import TradeClient
from tests.support import client_config

pytestmark = pytest.mark.unit


class TestUncoveredTradeClient(unittest.TestCase):

    def setUp(self):
        self.client_config = client_config()
        self.client = TradeClient(self.client_config)
        self.origin_do_request = web_utils.do_request

    def tearDown(self):
        web_utils.do_request = self.origin_do_request

    def test_get_managed_accounts(self):
        """Covers wire method ACCOUNTS."""
        mock_data = '{"data": ["ACC001"], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_managed_accounts()
        # Wire method ACCOUNTS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_open_orders(self):
        """Covers wire method ACTIVE_ORDERS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_open_orders()
        # Wire method ACTIVE_ORDERS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_aggregate_assets(self):
        """Covers wire method AGGREGATE_ASSETS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_aggregate_assets()
        # Wire method AGGREGATE_ASSETS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_analytics_asset(self):
        """Covers wire method ANALYTICS_ASSET."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_analytics_asset()
        # Wire method ANALYTICS_ASSET exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_assets(self):
        """Covers wire method ASSETS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_assets()
        # Wire method ASSETS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_cancel_segment_fund(self):
        """Covers wire method CANCEL_SEGMENT_FUND."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.cancel_segment_fund()
        # Wire method CANCEL_SEGMENT_FUND exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_contracts(self):
        """Covers wire method CONTRACTS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_contracts(["AAPL"])
        # Wire method CONTRACTS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_estimate_tradable_quantity(self):
        """Covers wire method ESTIMATE_TRADABLE_QUANTITY."""
        mock_data = '{"data": {"tradableQuantity": 100}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        from tigeropen.common.util.contract_utils import stock_contract
        from tigeropen.common.util.order_utils import limit_order
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order(account='00000000000000000', contract=contract, action='BUY', limit_price=150.0, quantity=100)
        result = self.client.get_estimate_tradable_quantity(order)
        # Wire method ESTIMATE_TRADABLE_QUANTITY exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_filled_orders(self):
        """Covers wire method FILLED_ORDERS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_filled_orders()
        # Wire method FILLED_ORDERS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_fund_details(self):
        """Covers wire method FUND_DETAILS."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_fund_details(None)
        # Wire method FUND_DETAILS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_cancelled_orders(self):
        """Covers wire method INACTIVE_ORDERS."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_cancelled_orders()
        # Wire method INACTIVE_ORDERS exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_create_order(self):
        """Covers wire method ORDER_NO."""
        mock_data = '{"data": {"id": 123, "orderId": 456}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        from tigeropen.common.util.contract_utils import stock_contract
        contract = stock_contract(symbol='AAPL', currency='USD')
        result = self.client.create_order(account='00000000000000000', contract=contract, action='BUY', order_type='LMT', quantity=1, limit_price=150.0)
        # Wire method ORDER_NO exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_place_forex_order(self):
        """Covers wire method PLACE_FOREX_ORDER."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.place_forex_order(None, None, None, None)
        # Wire method PLACE_FOREX_ORDER exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_preview_order(self):
        """Covers wire method PREVIEW_ORDER."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        from tigeropen.common.util.contract_utils import stock_contract
        from tigeropen.common.util.order_utils import limit_order
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order(account='00000000000000000', contract=contract, action='BUY', limit_price=150.0, quantity=1)
        result = self.client.preview_order(order)
        # Wire method PREVIEW_ORDER exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_derivative_contracts(self):
        """Covers wire method QUOTE_CONTRACT."""
        mock_data = '{"data": [], "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_derivative_contracts("AAPL", None, None)
        # Wire method QUOTE_CONTRACT exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_segment_fund_available(self):
        """Covers wire method SEGMENT_FUND_AVAILABLE."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_segment_fund_available()
        # Wire method SEGMENT_FUND_AVAILABLE exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_segment_fund_history(self):
        """Covers wire method SEGMENT_FUND_HISTORY."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_segment_fund_history()
        # Wire method SEGMENT_FUND_HISTORY exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_get_funding_history(self):
        """Covers wire method TRANSFER_FUND."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.get_funding_history()
        # Wire method TRANSFER_FUND exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_transfer_segment_fund(self):
        """Covers wire method TRANSFER_SEGMENT_FUND."""
        mock_data = '{"data": {}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.transfer_segment_fund()
        # Wire method TRANSFER_SEGMENT_FUND exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_query_license(self):
        """Covers wire method USER_LICENSE."""
        mock_data = '{"data": {"license": "TBNZ"}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.query_license()
        # Wire method USER_LICENSE exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()

    def test_query_token(self):
        """Covers wire method USER_TOKEN_REFRESH."""
        mock_data = '{"data": {"token": "fake_token"}, "code": 0, "message": "success", "timestamp": 1700000000}'
        web_utils.do_request = MagicMock(return_value=json.dumps(json.loads(mock_data)).encode())
        result = self.client.query_token()
        # Wire method USER_TOKEN_REFRESH exercised - request was constructed and mock was called
        web_utils.do_request.assert_called_once()
