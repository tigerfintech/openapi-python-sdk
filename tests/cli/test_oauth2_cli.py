# -*- coding: utf-8 -*-
"""
Tests for CLI OAuth2 support: config init --auth oauth2, auth commands, and the
OAuth2 branch of build_config / push connect.
"""
import os
import unittest
import tempfile
import shutil
from unittest import mock
from click.testing import CliRunner

import pytest


# 纯单测：永远不碰真实接口，contract / integ job 会跳过
pytestmark = pytest.mark.unit


class TestConfigInitOAuth2(unittest.TestCase):
    """Tests for 'tigeropen config init --auth oauth2'."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_init_oauth2_writes_issuer(self):
        """config init with global --auth oauth2 should write issuer/account and no private key."""
        from tigeropen.cli.main import cli
        result = self.runner.invoke(
            cli, ['--auth', 'oauth2', 'config', 'init'],
            input=f'https://test-issuer.example.com\n\naccount_123\n\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0, result.output)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertIn('auth_mode=oauth2', content)
        self.assertIn('test-issuer.example.com', content)
        self.assertIn('account_123', content)
        self.assertNotIn('private_key', content)

    def test_config_init_oauth2_requires_account(self):
        """config init --auth oauth2 should require account (trade depends on it)."""
        from tigeropen.cli.main import cli
        # Empty account line should re-prompt rather than silently writing config.
        result = self.runner.invoke(
            cli, ['--auth', 'oauth2', 'config', 'init'],
            input=f'https://test-issuer.example.com\n\n\naccount_456\n\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0, result.output)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertIn('account_456', content)


class TestConfigShowOAuth2(unittest.TestCase):
    """Tests for 'tigeropen config show' in OAuth2 mode."""

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_oauth2_props(self):
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        with open(props_file, 'w') as f:
            f.write('auth_mode=oauth2\n')
            f.write('issuer=https://test-issuer.example.com\n')
            f.write('client_id=0123456789abcdef\n')
            f.write('account=account_123\n')
            f.write('server_url=wss://gw.example.com\n')
        return props_file

    def test_config_show_oauth2_masks_client_id(self):
        """OAuth2 config show should show issuer and mask client_id."""
        from tigeropen.cli.main import cli
        self._write_oauth2_props()
        result = self.runner.invoke(cli, ['--config-path', self.temp_dir, 'config', 'show'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn('auth_mode=oauth2', result.output)
        self.assertIn('issuer=https://test-issuer.example.com', result.output)
        self.assertIn('0123****cdef', result.output)
        self.assertNotIn('0123456789abcdef', result.output)
        self.assertNotIn('private_key', result.output)


class TestAuthStatus(unittest.TestCase):
    """Tests for 'tigeropen auth status'."""

    def setUp(self):
        self.runner = CliRunner()

    def test_auth_status_not_authorized(self):
        """auth status with no token should say not authorized."""
        from tigeropen.cli.main import cli
        with mock.patch('tigeropen.cli.auth_cmd.build_session_manager') as m:
            mgr = mock.MagicMock()
            mgr.status.return_value = None
            m.return_value = mgr
            result = self.runner.invoke(cli, ['auth', 'status'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('未授权', result.output)


class TestAuthToken(unittest.TestCase):
    """Tests for 'tigeropen auth token'."""

    def setUp(self):
        self.runner = CliRunner()

    def test_auth_token_prints_token(self):
        """auth token should print the access token."""
        from tigeropen.cli.main import cli
        with mock.patch('tigeropen.cli.auth_cmd.build_session_manager') as m:
            mgr = mock.MagicMock()
            token = mock.MagicMock()
            token.access_token = 'abc123'
            mgr.status.return_value = token
            m.return_value = mgr
            result = self.runner.invoke(cli, ['auth', 'token'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('abc123', result.output)


class TestBuildConfigOAuth2(unittest.TestCase):
    """Tests for build_config in OAuth2 mode."""

    def test_build_config_oauth2_sets_authentication(self):
        """build_config with auth=oauth2 should attach OAuth2Authentication."""
        from tigeropen.cli.client_factory import build_config
        from tigeropen.auth.oauth2.authentication import OAuth2Authentication
        from tigeropen.auth.oauth2.session_manager import BUILTIN_ISSUER
        from tigeropen.cli.oauth2_config import _pair_test_gateway
        ctx_obj = {
            'auth': 'oauth2',
            'issuer': BUILTIN_ISSUER,
            'client_id': None,
            'config_path': '/tmp/nonexistent-cli-oauth2-test',
        }
        config = build_config(ctx_obj)
        self.assertIsInstance(config.authentication, OAuth2Authentication)
        # Pairing: test issuer -> test gateway
        self.assertEqual(config.server_url, _pair_test_gateway(BUILTIN_ISSUER))

    def test_build_config_oauth2_clears_signature_credentials(self):
        """OAuth2 mode must not depend on (or keep) the private key / tiger_id."""
        from tigeropen.cli.client_factory import build_config
        from tigeropen.auth.oauth2.session_manager import BUILTIN_ISSUER
        ctx_obj = {
            'auth': 'oauth2',
            'issuer': BUILTIN_ISSUER,
            'config_path': '/tmp/nonexistent-cli-oauth2-test',
        }
        config = build_config(ctx_obj)
        self.assertEqual(config.private_key, '')
        self.assertEqual(config.tiger_id, '')

    def test_build_config_signature_keeps_no_authentication(self):
        """build_config without auth should leave authentication None (default)."""
        from tigeropen.cli.client_factory import build_config
        ctx_obj = {
            'tiger_id': 'test_id',
            'private_key': 'test_key',
            'config_path': '/tmp/nonexistent-cli-sign-test',
        }
        config = build_config(ctx_obj)
        self.assertIsNone(config.authentication)
        self.assertEqual(config.tiger_id, 'test_id')


class TestGetQuoteClientGrab(unittest.TestCase):
    """QuoteClient from the CLI factory must grab permission by default."""

    def test_quote_client_grabs_permission_by_default(self):
        from tigeropen.cli.client_factory import get_quote_client
        with mock.patch('tigeropen.cli.client_factory.build_config') as bc, \
                mock.patch('tigeropen.quote.quote_client.QuoteClient') as Q:
            qc = mock.MagicMock()
            Q.return_value = qc
            bc.return_value = mock.MagicMock()
            ctx_obj = {}
            result = get_quote_client(ctx_obj)
            # is_grab_permission not passed -> defaults True
            self.assertNotIn('is_grab_permission', Q.call_args.kwargs)
            self.assertEqual(result, qc)


class TestPushConnectBranch(unittest.TestCase):
    """Tests for the auth-mode branch of the push connect helper."""

    def test_signature_connect_passes_credentials(self):
        from tigeropen.cli.push_cmd import _connect_push
        pc = mock.MagicMock()
        cfg = mock.MagicMock()
        cfg.authentication = None
        cfg.tiger_id = 'T1'
        cfg.private_key = 'K'
        _connect_push(pc, cfg)
        pc.connect.assert_called_once_with('T1', 'K')

    def test_oauth2_connect_passes_nothing(self):
        from tigeropen.cli.push_cmd import _connect_push
        pc = mock.MagicMock()
        cfg = mock.MagicMock()
        cfg.authentication = object()
        _connect_push(pc, cfg)
        pc.connect.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
