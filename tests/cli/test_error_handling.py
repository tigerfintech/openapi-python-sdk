# -*- coding: utf-8 -*-
"""
Tests for CLI error handling: ApiException, generic errors, verbose mode.
"""
import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from tigeropen.common.exceptions import ApiException


class TestApiExceptionHandling(unittest.TestCase):
    """Commands should catch ApiException and show user-friendly errors."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_api_error_shows_code_and_message(self, mock_get_client):
        """API errors should display error code and message in red."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.side_effect = ApiException(40001, 'Invalid symbol')
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'briefs', 'INVALID'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('40001', result.output)
        self.assertIn('Invalid symbol', result.output)

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_api_error_exits_with_code_1(self, mock_get_client):
        """API errors should cause exit code 1."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.side_effect = ApiException(40001, 'Invalid symbol')
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'briefs', 'INVALID'])
        self.assertEqual(result.exit_code, 1)


class TestGenericExceptionHandling(unittest.TestCase):
    """Commands should catch unexpected exceptions gracefully."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_generic_error_shows_message(self, mock_get_client):
        """Generic errors should display the error message."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.side_effect = ConnectionError('Network timeout')
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'briefs', 'AAPL'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Network timeout', result.output)

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_verbose_shows_traceback(self, mock_get_client):
        """With --verbose, errors should include the full traceback."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.side_effect = ApiException(40001, 'Bad request')
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['-v', 'quote', 'briefs', 'AAPL'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Traceback', result.output)

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_non_verbose_hides_traceback(self, mock_get_client):
        """Without --verbose, errors should NOT show full traceback."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.side_effect = ApiException(40001, 'Bad request')
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'briefs', 'AAPL'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertNotIn('Traceback', result.output)


class TestTradeErrorHandling(unittest.TestCase):
    """Trade commands should also handle errors gracefully."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_trade_api_error(self, mock_get_client):
        """Trade command API errors should be caught."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_orders.side_effect = ApiException(40002, 'Unauthorized')
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'list'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('40002', result.output)
        self.assertIn('Unauthorized', result.output)

    @patch('tigeropen.cli.account_cmd.get_trade_client')
    def test_account_api_error(self, mock_get_client):
        """Account command API errors should be caught."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_managed_accounts.side_effect = ApiException(40003, 'Token expired')
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['account', 'info'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('40003', result.output)
        self.assertIn('Token expired', result.output)


if __name__ == '__main__':
    unittest.main()
