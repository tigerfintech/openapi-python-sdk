# -*- coding: utf-8 -*-
"""
Tests for CLI trade commands with mocked TradeClient.
"""
import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


def make_mock_obj(**kwargs):
    """Create a simple object with given attributes as instance attrs."""
    obj = object.__new__(type('MockObj', (), {}))
    for k, v in kwargs.items():
        object.__setattr__(obj, k, v)
    return obj


class TestTradeOrderList(unittest.TestCase):
    """Tests for 'tigeropen trade order list'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_list_basic(self, mock_get_client):
        """trade order list should call get_orders and output results."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_order = make_mock_obj(
            id=12345, symbol='AAPL', action='BUY',
            order_type='LMT', quantity=100, filled=0,
            status='Submitted', limit_price=150.0,
        )
        mock_client.get_orders.return_value = [mock_order]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'list'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('AAPL', result.output)

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_list_with_status_filter(self, mock_get_client):
        """trade order list --status Filled should filter by status."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_orders.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'list', '--status', 'Filled'])
        self.assertEqual(result.exit_code, 0)


class TestTradeOrderGet(unittest.TestCase):
    """Tests for 'tigeropen trade order get'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_get(self, mock_get_client):
        """trade order get 12345 should call get_order and display details."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_order = make_mock_obj(
            id=12345, symbol='AAPL', action='BUY',
            order_type='LMT', quantity=100, filled=50,
            status='Partial', limit_price=150.0,
        )
        mock_client.get_order.return_value = mock_order
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'get', '12345'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('12345', result.output)

    def test_order_get_invalid_id(self):
        """trade order get abc should fail with Click validation error."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['trade', 'order', 'get', 'abc'])
        self.assertNotEqual(result.exit_code, 0)


class TestTradeOrderCancel(unittest.TestCase):
    """Tests for 'tigeropen trade order cancel'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_cancel_with_confirmation(self, mock_get_client):
        """trade order cancel 12345 should prompt for confirmation."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.cancel_order.return_value = True
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'cancel', '12345'], input='y\n')
        self.assertEqual(result.exit_code, 0)
        mock_client.cancel_order.assert_called_once()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_cancel_with_yes_flag(self, mock_get_client):
        """trade order cancel 12345 -y should skip confirmation."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.cancel_order.return_value = True
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'cancel', '12345', '-y'])
        self.assertEqual(result.exit_code, 0)
        mock_client.cancel_order.assert_called_once()


class TestTradePositionList(unittest.TestCase):
    """Tests for 'tigeropen trade position list'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_position_list_basic(self, mock_get_client):
        """trade position list should call get_positions and output results."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_contract = make_mock_obj(symbol='AAPL')
        mock_pos = make_mock_obj(
            contract=mock_contract,
            quantity=100, average_cost=145.0,
            market_price=150.0, unrealized_pnl=500.0,
            market_value=15000.0,
        )
        mock_client.get_positions.return_value = [mock_pos]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'position', 'list'])
        self.assertEqual(result.exit_code, 0)

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_position_list_with_sec_type(self, mock_get_client):
        """trade position list --sec-type OPT should filter by security type."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_positions.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'position', 'list', '--sec-type', 'OPT'])
        self.assertEqual(result.exit_code, 0)


class TestTradeOrderModify(unittest.TestCase):
    """Tests for 'tigeropen trade order modify'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_modify_with_limit_price(self, mock_get_client):
        """trade order modify 12345 --limit-price 155.0 should modify the order."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_order = MagicMock()
        mock_order.id = 12345
        mock_client.get_order.return_value = mock_order
        mock_client.modify_order.return_value = True
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'modify', '12345',
                                          '--limit-price', '155.0', '-y'])
        self.assertEqual(result.exit_code, 0)
        mock_client.modify_order.assert_called_once()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_modify_with_quantity(self, mock_get_client):
        """trade order modify 12345 --quantity 200 should update quantity."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_order = MagicMock()
        mock_order.id = 12345
        mock_client.get_order.return_value = mock_order
        mock_client.modify_order.return_value = True
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'modify', '12345',
                                          '--quantity', '200', '-y'])
        self.assertEqual(result.exit_code, 0)
        mock_client.modify_order.assert_called_once()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_modify_prompts_confirmation(self, mock_get_client):
        """trade order modify should prompt for confirmation without -y."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_order = MagicMock()
        mock_order.id = 12345
        mock_client.get_order.return_value = mock_order
        mock_client.modify_order.return_value = True
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'modify', '12345',
                                          '--limit-price', '155.0'], input='y\n')
        self.assertEqual(result.exit_code, 0)
        mock_client.modify_order.assert_called_once()


class TestTradeOrderPreview(unittest.TestCase):
    """Tests for 'tigeropen trade order preview'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_preview_basic(self, mock_get_client):
        """trade order preview should call preview_order with correct params."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client._account = 'DU123456'
        mock_client.get_contracts.return_value = [MagicMock()]
        mock_client.preview_order.return_value = make_mock_obj(
            order_id=99, init_margin=5000.0, maint_margin=2500.0
        )
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'preview',
                                          '--symbol', 'AAPL',
                                          '--action', 'BUY',
                                          '--quantity', '100',
                                          '--limit-price', '150.0'])
        self.assertEqual(result.exit_code, 0)
        mock_client.preview_order.assert_called_once()


class TestTradeOrderPlace(unittest.TestCase):
    """Tests for 'tigeropen trade order place'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_place_with_confirmation(self, mock_get_client):
        """trade order place should prompt for confirmation and place order."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client._account = 'DU123456'
        mock_client.get_contracts.return_value = [MagicMock()]
        mock_result = MagicMock()
        mock_result.id = 12345
        mock_client.place_order.return_value = mock_result
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'place',
                                          '--symbol', 'AAPL',
                                          '--action', 'BUY',
                                          '--quantity', '100',
                                          '--limit-price', '150.0',
                                          '-y'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Order placed', result.output)
        mock_client.place_order.assert_called_once()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_place_abort_on_no(self, mock_get_client):
        """trade order place should abort when user says no."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client._account = 'DU123456'
        mock_client.get_contracts.return_value = [MagicMock()]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'place',
                                          '--symbol', 'AAPL',
                                          '--action', 'BUY',
                                          '--quantity', '100',
                                          '--limit-price', '150.0'], input='n\n')
        # Should abort - place_order should NOT be called
        mock_client.place_order.assert_not_called()


class TestAccountInfo(unittest.TestCase):
    """Tests for 'tigeropen account info'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_info(self, mock_get_client):
        """account info should call get_managed_accounts."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_account = make_mock_obj(account='DU123456', capability='RegTMargin')
        mock_client.get_managed_accounts.return_value = [mock_account]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'info'])
        self.assertEqual(result.exit_code, 0)


class TestAccountAssets(unittest.TestCase):
    """Tests for 'tigeropen account assets'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_assets(self, mock_get_client):
        """account assets should call get_prime_assets."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_asset = make_mock_obj(
            account='DU123456',
            net_liquidation=100000.0,
            buying_power=50000.0,
        )
        mock_client.get_prime_assets.return_value = mock_asset
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'assets'])
        self.assertEqual(result.exit_code, 0)


class TestAccountAnalytics(unittest.TestCase):
    """Tests for 'tigeropen account analytics'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_analytics_basic(self, mock_get_client):
        """account analytics should call get_analytics_asset."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_analytics_asset.return_value = [
            make_mock_obj(date='2025-01-01', pnl=500.0, net_value=100500.0)
        ]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'analytics'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_analytics_asset.assert_called_once()

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_analytics_with_date_range(self, mock_get_client):
        """account analytics --start-date --end-date should pass date params."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_analytics_asset.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'analytics',
                                          '--start-date', '2025-01-01',
                                          '--end-date', '2025-03-01'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_analytics_asset.call_args[1]
        self.assertEqual(call_kwargs.get('start_date'), '2025-01-01')
        self.assertEqual(call_kwargs.get('end_date'), '2025-03-01')


class TestTransactionList(unittest.TestCase):
    """Tests for 'tigeropen trade transaction list'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_transaction_list_basic(self, mock_get_client):
        """trade transaction list should call get_transactions."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_txn = make_mock_obj(
            id=99999, symbol='AAPL', action='BUY',
            quantity=100, filled_price=150.0,
        )
        mock_client.get_transactions.return_value = [mock_txn]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'transaction', 'list'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('AAPL', result.output)
        mock_client.get_transactions.assert_called_once()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_transaction_list_with_symbol_filter(self, mock_get_client):
        """trade transaction list --symbol AAPL should filter by symbol."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_transactions.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'transaction', 'list', '--symbol', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_transactions.call_args[1]
        self.assertEqual(call_kwargs.get('symbol'), 'AAPL')


class TestTradeOrderListEmpty(unittest.TestCase):
    """Tests for order list with no results."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_list_empty_shows_message(self, mock_get_client):
        """trade order list with no orders should show 'No orders found'."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_orders.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'list'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No orders found', result.output)


class TestTradePositionListEmpty(unittest.TestCase):
    """Tests for position list with no results."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_position_list_empty_shows_message(self, mock_get_client):
        """trade position list with no positions should show message."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_positions.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'position', 'list'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No positions found', result.output)


class TestTradeTransactionListEmpty(unittest.TestCase):
    """Tests for transaction list with no results."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_transaction_list_empty_shows_message(self, mock_get_client):
        """trade transaction list with no transactions should show message."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_transactions.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'transaction', 'list'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No transactions found', result.output)


class TestTradeOrderCancelAbort(unittest.TestCase):
    """Tests for cancel abort when user says no."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_cancel_aborts_on_no(self, mock_get_client):
        """trade order cancel should abort when user says no."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'cancel', '12345'], input='n\n')
        mock_client.cancel_order.assert_not_called()


class TestAccountInfoEmpty(unittest.TestCase):
    """Tests for account info with no results."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_info_empty_shows_message(self, mock_get_client):
        """account info with no accounts should show message."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_managed_accounts.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'info'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No account info', result.output)

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_assets_empty_shows_message(self, mock_get_client):
        """account assets with no data should show message."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_prime_assets.return_value = None
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'assets'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No asset data', result.output)

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_analytics_empty_shows_message(self, mock_get_client):
        """account analytics with no data should show message."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_analytics_asset.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'analytics'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No analytics data', result.output)


class TestTradeOrderGetNotFound(unittest.TestCase):
    """Tests for order get when order doesn't exist."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_get_not_found(self, mock_get_client):
        """trade order get with non-existent ID should show not found message."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_order.return_value = None
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'get', '99999'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('not found', result.output)


class TestTradeOrderModifyNotFound(unittest.TestCase):
    """Tests for order modify when order doesn't exist."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_modify_not_found(self, mock_get_client):
        """trade order modify with non-existent ID should show not found."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_order.return_value = None
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'modify', '99999',
                                          '--limit-price', '155.0', '-y'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('not found', result.output)
        mock_client.modify_order.assert_not_called()


class TestTradeOrderListJsonFormat(unittest.TestCase):
    """Tests for JSON output format in trade commands."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_list_json(self, mock_get_client):
        """trade order list --format json should produce valid JSON."""
        import json
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_order = make_mock_obj(
            id=12345, symbol='AAPL', action='BUY',
            order_type='LMT', quantity=100, filled=0,
            status='Submitted', limit_price=150.0,
        )
        mock_client.get_orders.return_value = [mock_order]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['--format', 'json', 'trade', 'order', 'list'])
        self.assertEqual(result.exit_code, 0)
        parsed = json.loads(result.output)
        self.assertIsInstance(parsed, list)
        self.assertEqual(parsed[0]['symbol'], 'AAPL')


class TestMakeContractFallback(unittest.TestCase):
    """Tests for _make_contract fallback when get_contracts returns empty."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_order_place_with_empty_contracts(self, mock_get_client):
        """order place should work even when get_contracts returns empty list."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client._account = 'DU123456'
        mock_client.get_contracts.return_value = []  # empty - triggers fallback
        mock_client.place_order.return_value = 54321
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'place',
                                          '--symbol', 'UNKNOWN',
                                          '--action', 'BUY',
                                          '--quantity', '10',
                                          '--limit-price', '50.0',
                                          '-y'])
        self.assertEqual(result.exit_code, 0)
        mock_client.place_order.assert_called_once()


class TestPositionListNullContract(unittest.TestCase):
    """Tests for position list with contract=None."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_position_list_with_null_contract(self, mock_get_client):
        """position list should handle positions where contract is None."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_pos = make_mock_obj(
            contract=None,
            quantity=50, average_cost=100.0,
            market_price=105.0, unrealized_pnl=250.0,
            market_value=5250.0,
        )
        mock_client.get_positions.return_value = [mock_pos]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'position', 'list'])
        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
