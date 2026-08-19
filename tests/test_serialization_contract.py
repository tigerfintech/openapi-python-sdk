"""
Serialization contract tests — wire field name locking.

These tests pin the exact JSON key names that PlaceModifyOrderParams and the
core quote/trade request models emit via to_openapi_dict(). If a rename or
refactor changes a wire key, the test will fail before the change reaches the
live gateway.

Design rationale (mirrors C# SerializationContractTest):
  - Each assertion locks one Python-attribute → wire-key mapping.
  - Tests are pure unit tests: no network, no credentials.
  - New fields MUST add a corresponding assertion here before merging.
"""

import unittest

import pytest

from tigeropen.common.util.contract_utils import stock_contract, option_contract_by_symbol
from tigeropen.trade.request.model import (
    AccountsParams,
    AssetParams,
    CancelOrderParams,
    OrderParams,
    OrdersParams,
    PlaceModifyOrderParams,
    PositionParams,
)
from tigeropen.quote.request.model import (
    DepthQuoteParams,
    FutureQuoteParams,
    MarketScannerParams,
    MultipleQuoteParams,
    SingleQuoteParams,
    TradingCalendarParams,
)

pytestmark = pytest.mark.unit


class TestPlaceModifyOrderWireKeys(unittest.TestCase):
    """Pin Python attribute → wire JSON key for PlaceModifyOrderParams."""

    def _build_base(self):
        p = PlaceModifyOrderParams()
        p.account = 'U1234567'
        p.secret_key = 'sk'
        p.contract = stock_contract('AAPL', 'USD')
        p.action = 'BUY'
        p.order_type = 'LMT'
        p.quantity = 100
        p.limit_price = 150.0
        p.time_in_force = 'DAY'
        p.outside_rth = False
        return p

    def test_quantity_maps_to_total_quantity(self):
        """Python .quantity → wire 'total_quantity' (NOT 'quantity')."""
        p = self._build_base()
        d = p.to_openapi_dict()
        self.assertIn('total_quantity', d)
        self.assertNotIn('quantity', d)
        self.assertEqual(d['total_quantity'], 100)

    def test_limit_price_wire_key(self):
        p = self._build_base()
        d = p.to_openapi_dict()
        self.assertIn('limit_price', d)
        self.assertEqual(d['limit_price'], 150.0)

    def test_aux_price_wire_key(self):
        """aux_price (stop price) wire key stays 'aux_price'."""
        p = self._build_base()
        p.order_type = 'STP'
        p.aux_price = 148.0
        d = p.to_openapi_dict()
        self.assertIn('aux_price', d)
        self.assertEqual(d['aux_price'], 148.0)

    def test_trail_stop_price_wire_key(self):
        p = self._build_base()
        p.order_type = 'TRAIL'
        p.trail_stop_price = 5.0
        d = p.to_openapi_dict()
        self.assertIn('trail_stop_price', d)

    def test_trailing_percent_wire_key(self):
        p = self._build_base()
        p.trailing_percent = 2.0
        d = p.to_openapi_dict()
        self.assertIn('trailing_percent', d)

    def test_time_in_force_wire_key(self):
        p = self._build_base()
        d = p.to_openapi_dict()
        self.assertIn('time_in_force', d)
        self.assertEqual(d['time_in_force'], 'DAY')

    def test_outside_rth_wire_key(self):
        p = self._build_base()
        d = p.to_openapi_dict()
        self.assertIn('outside_rth', d)
        self.assertFalse(d['outside_rth'])

    def test_display_size_wire_key(self):
        """Iceberg: display_size wire key."""
        p = self._build_base()
        p.order_type = 'ICEBERG'
        p.display_size = 20
        p.min_display_size = 10
        d = p.to_openapi_dict()
        self.assertIn('display_size', d)
        self.assertIn('min_display_size', d)

    def test_start_end_time_wire_keys(self):
        """Algo orders: start_time / end_time wire keys."""
        p = self._build_base()
        p.start_time = 1700000000000
        p.end_time = 1700003600000
        d = p.to_openapi_dict()
        self.assertIn('start_time', d)
        self.assertIn('end_time', d)

    def test_contract_put_call_maps_to_right(self):
        """Option contract: Python .put_call → wire 'right'."""
        from tigeropen.common.util.contract_utils import option_contract_by_symbol as _opt
        p = PlaceModifyOrderParams()
        p.account = 'U1'
        p.secret_key = 'sk'
        p.contract = _opt('AAPL', '20240119', 150.0, 'CALL', 'USD')
        p.action = 'BUY'
        p.order_type = 'LMT'
        p.quantity = 1
        p.limit_price = 2.0
        d = p.to_openapi_dict()
        # put_call attribute must serialize as 'right' on wire
        self.assertIn('right', d)
        self.assertNotIn('put_call', d)

    def test_action_wire_key(self):
        p = self._build_base()
        d = p.to_openapi_dict()
        self.assertIn('action', d)
        self.assertEqual(d['action'], 'BUY')

    def test_order_type_wire_key(self):
        p = self._build_base()
        d = p.to_openapi_dict()
        self.assertIn('order_type', d)
        self.assertEqual(d['order_type'], 'LMT')

    def test_zero_values_serialized(self):
        """Zero-value numeric fields must appear in wire output, not be dropped."""
        p = self._build_base()
        p.quantity = 0
        p.limit_price = 0.0
        d = p.to_openapi_dict()
        self.assertIn('total_quantity', d)
        self.assertEqual(d['total_quantity'], 0)
        self.assertIn('limit_price', d)
        self.assertEqual(d['limit_price'], 0.0)


class TestAccountRequestWireKeys(unittest.TestCase):
    """Pin wire keys for account/position/order query params."""

    def test_accounts_params_wire_keys(self):
        p = AccountsParams()
        p.account = 'U1'
        p.secret_key = 'sk'
        d = p.to_openapi_dict()
        self.assertIn('account', d)

    def test_asset_params_wire_keys(self):
        p = AssetParams()
        p.account = 'U1'
        p.secret_key = 'sk'
        d = p.to_openapi_dict()
        self.assertIn('account', d)

    def test_position_params_wire_keys(self):
        p = PositionParams()
        p.account = 'U1'
        p.secret_key = 'sk'
        d = p.to_openapi_dict()
        self.assertIn('account', d)

    def test_orders_params_wire_keys(self):
        p = OrdersParams()
        p.account = 'U1'
        p.secret_key = 'sk'
        d = p.to_openapi_dict()
        self.assertIn('account', d)

    def test_order_params_id_wire_key(self):
        p = OrderParams()
        p.account = 'U1'
        p.secret_key = 'sk'
        p.id = 12345678901234567
        d = p.to_openapi_dict()
        self.assertIn('id', d)
        self.assertEqual(d['id'], 12345678901234567)

    def test_cancel_order_params_wire_keys(self):
        p = CancelOrderParams()
        p.account = 'U1'
        p.secret_key = 'sk'
        p.id = 987
        d = p.to_openapi_dict()
        self.assertIn('id', d)


class TestQuoteRequestWireKeys(unittest.TestCase):
    """Pin wire keys for quote request models."""

    def test_single_quote_symbol_wire_key(self):
        p = SingleQuoteParams()
        p.symbol = 'AAPL'
        p.market = 'US'
        p.currency = 'USD'
        p.sec_type = 'STK'
        d = p.to_openapi_dict()
        self.assertIn('symbol', d)
        self.assertEqual(d['symbol'], 'AAPL')

    def test_multiple_quote_symbols_wire_key(self):
        p = MultipleQuoteParams()
        p.symbols = ['AAPL', 'TSLA']
        p.market = 'US'
        p.sec_type = 'STK'
        d = p.to_openapi_dict()
        self.assertIn('symbols', d)
        self.assertEqual(d['symbols'], ['AAPL', 'TSLA'])

    def test_depth_quote_symbols_wire_key(self):
        """DepthQuoteParams uses 'symbols' (list), not 'symbol'."""
        p = DepthQuoteParams()
        p.symbols = ['AAPL', 'TSLA']
        p.market = 'US'
        d = p.to_openapi_dict()
        self.assertIn('symbols', d)
        self.assertEqual(d['symbols'], ['AAPL', 'TSLA'])

    def test_trading_calendar_market_wire_key(self):
        p = TradingCalendarParams()
        p.market = 'US'
        d = p.to_openapi_dict()
        self.assertIn('market', d)
        self.assertEqual(d['market'], 'US')

    def test_future_quote_contract_code_wire_key(self):
        p = FutureQuoteParams()
        p.contract_codes = ['ES2412', 'NQ2412']
        d = p.to_openapi_dict()
        self.assertIn('contract_codes', d)

    def test_market_scanner_page_size_wire_key(self):
        """MarketScanner page_size wire key is snake_case (not camelCase)."""
        p = MarketScannerParams()
        p.market = 'US'
        p.page_size = 20
        d = p.to_openapi_dict()
        self.assertIn('page_size', d)
        self.assertNotIn('pageSize', d)
        self.assertEqual(d['page_size'], 20)

    def test_market_scanner_filter_lists_wire_keys(self):
        """MarketScanner filter list wire keys are snake_case (not camelCase)."""
        p = MarketScannerParams()
        p.market = 'US'
        p.base_filter_list = [{'field_name': 'StockField_MarketValue', 'filter_min': 1e8}]
        d = p.to_openapi_dict()
        self.assertIn('base_filter_list', d)
        self.assertNotIn('baseFilterList', d)


if __name__ == '__main__':
    unittest.main()
