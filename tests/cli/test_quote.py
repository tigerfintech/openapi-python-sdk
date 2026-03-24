# -*- coding: utf-8 -*-
"""
Tests for CLI quote commands with mocked QuoteClient.
"""
import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
import pandas as pd


def make_mock_obj(**kwargs):
    """Create a simple object with given attributes as instance attrs."""
    obj = object.__new__(type('MockObj', (), {}))
    for k, v in kwargs.items():
        object.__setattr__(obj, k, v)
    return obj


class TestQuoteBriefs(unittest.TestCase):
    """Tests for 'tigeropen quote briefs' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_quote_briefs_basic(self, mock_get_client):
        """quote briefs AAPL GOOG should call get_stock_briefs and output results."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL', 'GOOG'],
            'latest_price': [150.0, 2800.0],
            'volume': [1000000, 500000],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'briefs', 'AAPL', 'GOOG'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('AAPL', result.output)
        self.assertIn('GOOG', result.output)
        mock_client.get_stock_briefs.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_quote_briefs_json_format(self, mock_get_client):
        """quote briefs --format json should output valid JSON."""
        from tigeropen.cli.main import cli
        import json
        mock_client = MagicMock()
        mock_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [150.0],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['--format', 'json', 'quote', 'briefs', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        parsed = json.loads(result.output)
        self.assertEqual(parsed[0]['symbol'], 'AAPL')

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_quote_briefs_requires_symbols(self, mock_get_client):
        """quote briefs without symbols should fail."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['quote', 'briefs'])
        self.assertNotEqual(result.exit_code, 0)


class TestQuoteBars(unittest.TestCase):
    """Tests for 'tigeropen quote bars' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_quote_bars_basic(self, mock_get_client):
        """quote bars AAPL should call get_bars with default period."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_bars.return_value = pd.DataFrame({
            'symbol': ['AAPL'] * 3,
            'time': [1000, 2000, 3000],
            'open': [148.0, 149.0, 150.0],
            'close': [149.0, 150.0, 151.0],
            'high': [150.0, 151.0, 152.0],
            'low': [147.0, 148.0, 149.0],
            'volume': [100, 200, 300],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'bars', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('AAPL', result.output)
        mock_client.get_bars.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_quote_bars_with_period(self, mock_get_client):
        """quote bars AAPL --period 5min should pass period to SDK."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_bars.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'bars', 'AAPL', '--period', '5min'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_bars.call_args
        self.assertEqual(call_kwargs[1].get('period') or call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1].get('period'), '5min')

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_quote_bars_with_limit(self, mock_get_client):
        """quote bars AAPL --limit 10 should pass limit to SDK."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_bars.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'bars', 'AAPL', '--limit', '10'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_bars.call_args
        self.assertEqual(call_kwargs[1].get('limit'), 10)


class TestQuoteMarketStatus(unittest.TestCase):
    """Tests for 'tigeropen quote market-status' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_market_status_basic(self, mock_get_client):
        """quote market-status should call get_market_status and output results."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_status = make_mock_obj(market='US', status='Trading', trading_status='TRADING')
        mock_client.get_market_status.return_value = [mock_status]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'market-status'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('US', result.output)
        mock_client.get_market_status.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_market_status_with_market_filter(self, mock_get_client):
        """quote market-status --market US should filter by market."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_market_status.return_value = []
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'market-status', '--market', 'US'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_market_status.call_args
        self.assertEqual(call_kwargs[1].get('market'), 'US')


class TestQuoteTimeline(unittest.TestCase):
    """Tests for 'tigeropen quote timeline' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_timeline_basic(self, mock_get_client):
        """quote timeline AAPL should call get_timeline."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_timeline.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'time': [1000],
            'price': [150.0],
            'avg_price': [149.5],
            'volume': [1000],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'timeline', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('AAPL', result.output)


class TestQuoteDepth(unittest.TestCase):
    """Tests for 'tigeropen quote depth' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_depth_basic(self, mock_get_client):
        """quote depth AAPL --market US should call get_depth_quote."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_depth_quote.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'ask': [[150.1, 150.2]],
            'bid': [[149.9, 149.8]],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'depth', 'AAPL', '--market', 'US'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_depth_quote.assert_called_once()


class TestQuoteOptionExpirations(unittest.TestCase):
    """Tests for 'tigeropen quote option expirations' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_option_expirations(self, mock_get_client):
        """quote option expirations AAPL should call get_option_expirations."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_option_expirations.return_value = [
            make_mock_obj(symbol='AAPL', dates=['2025-03-21', '2025-04-17'])
        ]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'option', 'expirations', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_option_expirations.assert_called_once()


class TestQuoteOptionChain(unittest.TestCase):
    """Tests for 'tigeropen quote option chain' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_option_chain(self, mock_get_client):
        """quote option chain AAPL 2025-03-21 should call get_option_chain."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_option_chain.return_value = pd.DataFrame({
            'identifier': ['AAPL  250321C00150000'],
            'strike': [150.0],
            'put_call': ['CALL'],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'option', 'chain', 'AAPL', '2025-03-21'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_option_chain.assert_called_once()


class TestQuoteSymbols(unittest.TestCase):
    """Tests for 'tigeropen quote symbols' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_symbols_default_market(self, mock_get_client):
        """quote symbols should call get_symbol_names with default US market."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_symbol_names.return_value = pd.DataFrame({
            'symbol': ['AAPL', 'GOOG', 'TSLA'],
            'name': ['Apple Inc', 'Alphabet Inc', 'Tesla Inc'],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'symbols'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('AAPL', result.output)
        mock_client.get_symbol_names.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_symbols_with_market(self, mock_get_client):
        """quote symbols --market HK should pass market parameter."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_symbol_names.return_value = pd.DataFrame({
            'symbol': ['00700'],
            'name': ['Tencent Holdings'],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'symbols', '--market', 'HK'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_symbol_names.call_args
        self.assertEqual(call_kwargs[1].get('market'), 'HK')


class TestQuoteTicks(unittest.TestCase):
    """Tests for 'tigeropen quote ticks' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_ticks_basic(self, mock_get_client):
        """quote ticks AAPL should call get_trade_ticks."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_trade_ticks.return_value = pd.DataFrame({
            'symbol': ['AAPL'] * 3,
            'time': [1000, 2000, 3000],
            'price': [150.0, 150.1, 150.2],
            'volume': [10, 20, 30],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'ticks', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('AAPL', result.output)
        mock_client.get_trade_ticks.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_ticks_with_limit(self, mock_get_client):
        """quote ticks AAPL --limit 50 should pass limit to SDK."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_trade_ticks.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'ticks', 'AAPL', '--limit', '50'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_trade_ticks.call_args[1]
        self.assertEqual(call_kwargs.get('limit'), 50)


class TestQuoteCapitalFlow(unittest.TestCase):
    """Tests for 'tigeropen quote capital flow' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_capital_flow_basic(self, mock_get_client):
        """quote capital flow AAPL should call get_capital_flow."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_capital_flow.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'net_inflow': [5000000.0],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'capital', 'flow', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_capital_flow.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_capital_flow_with_market(self, mock_get_client):
        """quote capital flow AAPL --market HK should pass market."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_capital_flow.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'capital', 'flow', '00700', '--market', 'HK'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_capital_flow.call_args[1]
        self.assertEqual(call_kwargs.get('market'), 'HK')


class TestQuoteCapitalDistribution(unittest.TestCase):
    """Tests for 'tigeropen quote capital distribution' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_capital_distribution_basic(self, mock_get_client):
        """quote capital distribution AAPL should call get_capital_distribution."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_capital_distribution.return_value = make_mock_obj(
            symbol='AAPL', net_inflow=1000000.0, in_all=5000000.0, out_all=4000000.0
        )
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'capital', 'distribution', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_capital_distribution.assert_called_once()


class TestQuoteFundamental(unittest.TestCase):
    """Tests for 'tigeropen quote fundamental' subcommands."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_financial_report(self, mock_get_client):
        """quote fundamental financial AAPL should call get_financial_report."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_financial_report.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'revenue': [100000000.0],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'fundamental', 'financial', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_financial_report.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_dividend(self, mock_get_client):
        """quote fundamental dividend AAPL should call get_corporate_dividend."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_corporate_dividend.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'amount': [0.82],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'fundamental', 'dividend', 'AAPL',
                                          '--begin-date', '2025-01-01', '--end-date', '2025-12-31'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_corporate_dividend.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_earnings(self, mock_get_client):
        """quote fundamental earnings should call get_corporate_earnings_calendar."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_corporate_earnings_calendar.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'date': ['2025-01-30'],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'fundamental', 'earnings',
                                          '--begin-date', '2025-01-01', '--end-date', '2025-12-31'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_corporate_earnings_calendar.assert_called_once()


class TestQuoteOptionBriefs(unittest.TestCase):
    """Tests for 'tigeropen quote option briefs' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_option_briefs(self, mock_get_client):
        """quote option briefs should call get_option_briefs."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_option_briefs.return_value = [
            make_mock_obj(identifier='AAPL  250321C00150000', latest_price=5.0, volume=1000)
        ]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'option', 'briefs', 'AAPL  250321C00150000'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_option_briefs.assert_called_once()


class TestQuoteOptionBars(unittest.TestCase):
    """Tests for 'tigeropen quote option bars' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_option_bars(self, mock_get_client):
        """quote option bars should call get_option_bars."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_option_bars.return_value = pd.DataFrame({
            'identifier': ['AAPL  250321C00150000'],
            'open': [5.0],
            'close': [5.5],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'option', 'bars', 'AAPL  250321C00150000'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_option_bars.assert_called_once()


class TestQuoteFutureContracts(unittest.TestCase):
    """Tests for 'tigeropen quote future contracts' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_future_contracts(self, mock_get_client):
        """quote future contracts CME should call get_future_contracts."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_future_contracts.return_value = [
            make_mock_obj(code='CL2509', name='Crude Oil Sep 2025')
        ]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'future', 'contracts', 'CME'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_future_contracts.assert_called_once()


class TestQuoteFutureBriefs(unittest.TestCase):
    """Tests for 'tigeropen quote future briefs' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_future_briefs(self, mock_get_client):
        """quote future briefs CL2509 should call get_future_brief."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_future_brief.return_value = [
            make_mock_obj(identifier='CL2509', latest_price=75.5, volume=50000)
        ]
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'future', 'briefs', 'CL2509'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_future_brief.assert_called_once()


class TestQuoteFutureBars(unittest.TestCase):
    """Tests for 'tigeropen quote future bars' command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_future_bars(self, mock_get_client):
        """quote future bars CL2509 should call get_future_bars."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_future_bars.return_value = pd.DataFrame({
            'identifier': ['CL2509'],
            'open': [75.0],
            'close': [75.5],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'future', 'bars', 'CL2509'])
        self.assertEqual(result.exit_code, 0)
        mock_client.get_future_bars.assert_called_once()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_future_bars_with_period(self, mock_get_client):
        """quote future bars CL2509 --period 5min should pass period."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_future_bars.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'future', 'bars', 'CL2509', '--period', '5min'])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_client.get_future_bars.call_args[1]
        self.assertEqual(call_kwargs.get('period'), '5min')


class TestQuoteCsvFormat(unittest.TestCase):
    """Tests for CSV output format."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_quote_briefs_csv(self, mock_get_client):
        """quote briefs --format csv should output CSV data."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [150.0],
        })
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['--format', 'csv', 'quote', 'briefs', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('symbol', result.output)
        self.assertIn('AAPL', result.output)
        # CSV should have comma-separated header
        lines = result.output.strip().split('\n')
        self.assertIn(',', lines[0])


class TestQuoteEmptyResults(unittest.TestCase):
    """Commands should show user-friendly messages when results are empty/None."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_briefs_none_shows_message(self, mock_get_client):
        """quote briefs returning None should show 'No data'."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_stock_briefs.return_value = None
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'briefs', 'INVALID'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No', result.output)

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_bars_empty_shows_message(self, mock_get_client):
        """quote bars returning empty DataFrame should show 'No data'."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_bars.return_value = pd.DataFrame()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'bars', 'INVALID'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No', result.output)

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_timeline_none_shows_message(self, mock_get_client):
        """quote timeline returning None should show 'No data'."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_timeline.return_value = None
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'timeline', 'INVALID'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No', result.output)

    @patch('tigeropen.cli.quote_cmd.get_quote_client')
    def test_capital_distribution_none_shows_message(self, mock_get_client):
        """quote capital distribution returning None should show 'No data'."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client.get_capital_distribution.return_value = None
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['quote', 'capital', 'distribution', 'INVALID'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No', result.output)


class TestTradeReturnValueHandling(unittest.TestCase):
    """Trade commands should handle return values correctly."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.trade_cmd.get_trade_client')
    def test_place_order_none_return_shows_failure(self, mock_get_client):
        """place_order returning None should not falsely claim success."""
        from tigeropen.cli.main import cli
        mock_client = MagicMock()
        mock_client._account = 'DU123456'
        mock_client.get_contracts.return_value = [MagicMock()]
        mock_client.place_order.return_value = None
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(cli, ['trade', 'order', 'place',
                                          '--symbol', 'AAPL',
                                          '--action', 'BUY',
                                          '--quantity', '100',
                                          '--limit-price', '150.0',
                                          '-y'])
        self.assertEqual(result.exit_code, 0)
        # Should NOT say "Order placed" with ID: None
        self.assertNotIn('ID: None', result.output)


if __name__ == '__main__':
    unittest.main()
