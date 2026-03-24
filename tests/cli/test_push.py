# -*- coding: utf-8 -*-
"""
Tests for CLI push commands with mocked PushClient.
"""
import unittest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner


class TestPushQuote(unittest.TestCase):
    """Tests for 'tigeropen push quote'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_quote_connects_and_subscribes(self, MockPushClient, mock_build_config):
        """push quote AAPL should connect and subscribe to quote updates."""
        from tigeropen.cli.main import cli
        mock_config = MagicMock()
        mock_config.tiger_id = 'test_id'
        mock_config.private_key = 'test_key'
        mock_config.socket_host_port = ('ssl', 'openapi.test.com', 9883)
        mock_config.account = 'test_account'
        mock_build_config.return_value = mock_config

        mock_client = MagicMock()
        MockPushClient.return_value = mock_client
        # Simulate KeyboardInterrupt to stop the push loop
        mock_client.connect.side_effect = KeyboardInterrupt()

        result = self.runner.invoke(cli, ['push', 'quote', 'AAPL', 'GOOG'])
        # Should attempt to create PushClient with host/port
        MockPushClient.assert_called_once()
        self.assertEqual(result.exit_code, 0)

    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_quote_requires_symbols(self, MockPushClient, mock_build_config):
        """push quote without symbols should fail."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(cli, ['push', 'quote'])
        self.assertNotEqual(result.exit_code, 0)


class TestPushOrder(unittest.TestCase):
    """Tests for 'tigeropen push order'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_order_connects(self, MockPushClient, mock_build_config):
        """push order should connect and subscribe to order updates."""
        from tigeropen.cli.main import cli
        mock_config = MagicMock()
        mock_config.tiger_id = 'test_id'
        mock_config.private_key = 'test_key'
        mock_config.socket_host_port = ('ssl', 'openapi.test.com', 9883)
        mock_config.account = 'test_account'
        mock_build_config.return_value = mock_config

        mock_client = MagicMock()
        MockPushClient.return_value = mock_client
        mock_client.connect.side_effect = KeyboardInterrupt()

        result = self.runner.invoke(cli, ['push', 'order'])
        MockPushClient.assert_called_once()
        self.assertEqual(result.exit_code, 0)


class TestPushPosition(unittest.TestCase):
    """Tests for 'tigeropen push position'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_position_connects(self, MockPushClient, mock_build_config):
        """push position should connect and subscribe to position updates."""
        from tigeropen.cli.main import cli
        mock_config = MagicMock()
        mock_config.tiger_id = 'test_id'
        mock_config.private_key = 'test_key'
        mock_config.socket_host_port = ('ssl', 'openapi.test.com', 9883)
        mock_config.account = 'test_account'
        mock_build_config.return_value = mock_config

        mock_client = MagicMock()
        MockPushClient.return_value = mock_client
        mock_client.connect.side_effect = KeyboardInterrupt()

        result = self.runner.invoke(cli, ['push', 'position'])
        MockPushClient.assert_called_once()
        self.assertEqual(result.exit_code, 0)


class TestPushAsset(unittest.TestCase):
    """Tests for 'tigeropen push asset'."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_asset_connects(self, MockPushClient, mock_build_config):
        """push asset should connect and subscribe to asset updates."""
        from tigeropen.cli.main import cli
        mock_config = MagicMock()
        mock_config.tiger_id = 'test_id'
        mock_config.private_key = 'test_key'
        mock_config.socket_host_port = ('ssl', 'openapi.test.com', 9883)
        mock_config.account = 'test_account'
        mock_build_config.return_value = mock_config

        mock_client = MagicMock()
        MockPushClient.return_value = mock_client
        mock_client.connect.side_effect = KeyboardInterrupt()

        result = self.runner.invoke(cli, ['push', 'asset'])
        MockPushClient.assert_called_once()
        self.assertEqual(result.exit_code, 0)


class TestPushDisconnectsOnExit(unittest.TestCase):
    """Push commands should always disconnect in the finally block."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.push_cmd._wait_for_interrupt')
    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_quote_disconnects_after_streaming(self, MockPushClient, mock_build_config, mock_wait):
        """push quote should call disconnect even after normal exit."""
        from tigeropen.cli.main import cli
        mock_config = MagicMock()
        mock_config.tiger_id = 'test_id'
        mock_config.private_key = 'test_key'
        mock_config.socket_host_port = ('ssl', 'openapi.test.com', 9883)
        mock_config.account = 'test_account'
        mock_build_config.return_value = mock_config

        mock_client = MagicMock()
        MockPushClient.return_value = mock_client
        # _wait_for_interrupt returns normally (simulates Ctrl+C handled)
        mock_wait.return_value = None

        result = self.runner.invoke(cli, ['push', 'quote', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        mock_client.disconnect.assert_called_once()
        self.assertIn('Disconnected', result.output)

    @patch('tigeropen.cli.push_cmd._wait_for_interrupt')
    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_order_disconnects_after_streaming(self, MockPushClient, mock_build_config, mock_wait):
        """push order should call disconnect even after normal exit."""
        from tigeropen.cli.main import cli
        mock_config = MagicMock()
        mock_config.tiger_id = 'test_id'
        mock_config.private_key = 'test_key'
        mock_config.socket_host_port = ('ssl', 'openapi.test.com', 9883)
        mock_config.account = 'test_account'
        mock_build_config.return_value = mock_config

        mock_client = MagicMock()
        MockPushClient.return_value = mock_client
        mock_wait.return_value = None

        result = self.runner.invoke(cli, ['push', 'order'])
        self.assertEqual(result.exit_code, 0)
        mock_client.disconnect.assert_called_once()
        self.assertIn('Disconnected', result.output)


class TestPushDisconnectFailure(unittest.TestCase):
    """Push commands should handle disconnect errors gracefully."""

    def setUp(self):
        self.runner = CliRunner()

    @patch('tigeropen.cli.push_cmd._wait_for_interrupt')
    @patch('tigeropen.cli.push_cmd.build_config')
    @patch('tigeropen.cli.push_cmd.PushClient')
    def test_push_quote_survives_disconnect_error(self, MockPushClient, mock_build_config, mock_wait):
        """push quote should still print 'Disconnected' even if disconnect() raises."""
        from tigeropen.cli.main import cli
        mock_config = MagicMock()
        mock_config.tiger_id = 'test_id'
        mock_config.private_key = 'test_key'
        mock_config.socket_host_port = ('ssl', 'openapi.test.com', 9883)
        mock_config.account = 'test_account'
        mock_build_config.return_value = mock_config

        mock_client = MagicMock()
        MockPushClient.return_value = mock_client
        mock_client.disconnect.side_effect = Exception('socket error')
        mock_wait.return_value = None

        result = self.runner.invoke(cli, ['push', 'quote', 'AAPL'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Disconnected', result.output)


if __name__ == '__main__':
    unittest.main()
