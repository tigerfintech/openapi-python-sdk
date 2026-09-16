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

    def test_config_init_oauth2_writes_only_what_it_asked_for(self):
        """The issuer and the gateway are not written.

        Both are meant to follow the built-in defaults. A value accepted here outlives the
        default it was copied from, and an issuer left behind that way is how a login stores
        its token where the business commands do not look for it.
        """
        from tigeropen.cli.main import cli
        # client_id (skip) / account / config dir
        result = self.runner.invoke(
            cli, ['--auth', 'oauth2', 'config', 'init'],
            input=f'\naccount_123\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0, result.output)
        props_file = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        content = open(props_file, 'r').read()
        self.assertIn('auth_mode=oauth2', content)
        self.assertIn('account_123', content)
        self.assertNotIn('issuer', content)
        self.assertNotIn('server_url', content)
        self.assertNotIn('private_key', content)

    def test_config_init_oauth2_names_the_authorization_server(self):
        """Not asking for it must not mean hiding it: the user still has to be able to see
        which environment the login will go to."""
        from tigeropen.auth.oauth2.session_manager import OAuth2SessionManager
        from tigeropen.cli.main import cli
        result = self.runner.invoke(
            cli, ['--auth', 'oauth2', 'config', 'init'],
            input=f'\naccount_123\n{self.temp_dir}\n')
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn(OAuth2SessionManager.default_issuer(), result.output)

    def test_config_init_oauth2_requires_account(self):
        """config init --auth oauth2 should require account (trade depends on it)."""
        from tigeropen.cli.main import cli
        # Empty account line should re-prompt rather than silently writing config.
        result = self.runner.invoke(
            cli, ['--auth', 'oauth2', 'config', 'init'],
            input=f'\n\naccount_456\n{self.temp_dir}\n')
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


class TestAuthLoginFlow(unittest.TestCase):
    """Which authorization flow ``auth login`` picks.

    A command line runs in a remote shell as often as on a desktop, and the device flow is the
    one that behaves the same in both. The browser redirect flow binds the authorization to
    this process instead of to a code, so it stays available for where that matters.
    """

    def setUp(self):
        self.runner = CliRunner()

    def _sessions(self):
        mgr = mock.MagicMock()
        mgr.issuer = 'https://issuer.example.com'
        mgr.client_id = 'cid'
        return mgr

    def test_login_uses_the_device_flow_by_default(self):
        from tigeropen.cli.main import cli
        mgr = self._sessions()
        with mock.patch('tigeropen.cli.auth_cmd.build_session_manager', return_value=mgr):
            self.runner.invoke(cli, ['auth', 'login'])
        mgr.login_with_device_code_if_needed.assert_called_once()
        mgr.login_if_needed.assert_not_called()

    def test_loopback_flag_switches_to_the_browser_flow(self):
        from tigeropen.cli.main import cli
        mgr = self._sessions()
        with mock.patch('tigeropen.cli.auth_cmd.build_session_manager', return_value=mgr), \
                mock.patch('tigeropen.cli.auth_cmd.webbrowser.open'):
            self.runner.invoke(cli, ['auth', 'login', '--loopback'])
        mgr.login_if_needed.assert_called_once()
        mgr.login_with_device_code_if_needed.assert_not_called()

    def test_login_device_stays_available_as_an_explicit_name(self):
        from tigeropen.cli.main import cli
        mgr = self._sessions()
        with mock.patch('tigeropen.cli.auth_cmd.build_session_manager', return_value=mgr):
            self.runner.invoke(cli, ['auth', 'login-device'])
        mgr.login_with_device_code_if_needed.assert_called_once()


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
        ctx_obj = {
            'auth': 'oauth2',
            'issuer': BUILTIN_ISSUER,
            'client_id': None,
            'config_path': '/tmp/nonexistent-cli-oauth2',
        }
        config = build_config(ctx_obj)
        self.assertIsInstance(config.authentication, OAuth2Authentication)
        # The gateway is whatever the client config defaults to; OAuth2 changes how the
        # request is authenticated, not where it is sent.
        self.assertIsNotNone(config.server_url)

    def test_build_config_oauth2_clears_signature_credentials(self):
        """OAuth2 mode must not depend on (or keep) the private key / tiger_id."""
        from tigeropen.cli.client_factory import build_config
        from tigeropen.auth.oauth2.session_manager import BUILTIN_ISSUER
        ctx_obj = {
            'auth': 'oauth2',
            'issuer': BUILTIN_ISSUER,
            'config_path': '/tmp/nonexistent-cli-oauth2',
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


class TestSettingsResolution(unittest.TestCase):
    """Every command must resolve a setting the same way.

    Resolving it twice let ``auth login`` store its token under one issuer while every later
    command looked for it under another, and the only symptom was "not authorized" straight
    after a successful login.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_props(self, **entries):
        path = os.path.join(self.temp_dir, 'tiger_openapi_config.properties')
        with open(path, 'w') as f:
            for k, v in entries.items():
                f.write('%s=%s\n' % (k, v))
        return path

    def test_auth_login_and_business_commands_agree_on_the_issuer(self):
        from tigeropen.cli.auth_cmd import _sessions_from_ctx
        from tigeropen.cli.client_factory import build_config
        self._write_props(auth_mode='oauth2', issuer='https://issuer.example.com',
                          account='acc-1')
        ctx_obj = {'config_path': self.temp_dir}

        login_sessions = _sessions_from_ctx(mock.Mock(obj=dict(ctx_obj)))
        business_config = build_config(dict(ctx_obj))

        self.assertEqual('https://issuer.example.com', login_sessions.issuer)
        self.assertEqual(login_sessions.issuer,
                         business_config.authentication.session_manager.issuer,
                         'both paths must land on the same authorization server')

    def test_auth_mode_from_the_config_file_takes_effect(self):
        """A concrete click default would shadow the file, leaving auth_mode unusable."""
        from tigeropen.cli.client_factory import build_config
        from tigeropen.auth.oauth2.authentication import OAuth2Authentication
        self._write_props(auth_mode='oauth2', account='acc-1')
        config = build_config({'config_path': self.temp_dir})
        self.assertIsInstance(config.authentication, OAuth2Authentication,
                              'auth_mode=oauth2 in the config file must select OAuth2')

    def test_oauth2_is_preferred_when_nothing_is_configured(self):
        """OAuth2 needs no key on disk and can be set up from the command line, so it is the
        better answer for a machine that says nothing about which mode to use. Its failure
        also names the command that fixes it."""
        from tigeropen.cli.settings import resolve_settings
        with mock.patch.dict(os.environ, {'TIGEROPEN_HOME': self.temp_dir}):
            self.assertEqual('oauth2',
                             resolve_settings({'config_path': self.temp_dir})['auth'])

    def test_signature_setup_is_left_alone(self):
        """Every installation predating OAuth2 support looks like this, and must keep
        working exactly as before.

        All three private-key spellings the SDK accepts are covered: config init writes
        private_key_pk8, but a hand-written file uses the documented private_key, and reading
        only one of them would take that installation for an unconfigured one.
        """
        from tigeropen.cli.settings import resolve_settings
        for key in ('private_key', 'private_key_pk8', 'private_key_pk1'):
            self._write_props(**{'tiger_id': '123456', key: 'KEY', 'account': 'acc-1'})
            with mock.patch.dict(os.environ, {'TIGEROPEN_HOME': self.temp_dir}):
                self.assertEqual('signature',
                                 resolve_settings({'config_path': self.temp_dir})['auth'], key)

    def test_an_existing_authorization_selects_oauth2(self):
        """Once the user has authorized, later commands should use it without being told."""
        from tigeropen.auth.oauth2 import OAuth2Token, OAuth2TokenStore
        from tigeropen.auth.oauth2.client_registration import OAuth2ClientRegistration
        from tigeropen.auth.oauth2.token import current_millis
        from tigeropen.cli.settings import resolve_settings
        issuer = 'https://issuer.example.com'
        home = os.path.join(self.temp_dir, 'home')
        store = OAuth2TokenStore(home, 'cli')
        registration = OAuth2ClientRegistration(issuer=issuer, client_id='cid',
                                                registered_scopes='api.quote:read')
        store.save_client_registration(registration)
        store.save_token(OAuth2Token(issuer=issuer, client_id='cid', access_token='AT',
                                     refresh_token='RT', scope='api.quote:read',
                                     expires_at=current_millis() + 3600_000))
        # Signature credentials are present too: the stored authorization still wins.
        self._write_props(tiger_id='123456', private_key_pk8='KEY', issuer=issuer)

        with mock.patch.dict(os.environ, {'TIGEROPEN_HOME': home}):
            self.assertEqual('oauth2',
                             resolve_settings({'config_path': self.temp_dir})['auth'])

    def test_explicit_option_wins_over_the_config_file(self):
        from tigeropen.cli.client_factory import build_config
        self._write_props(auth_mode='oauth2', account='from-file')
        config = build_config({'config_path': self.temp_dir, 'account': 'from-option'})
        self.assertEqual('from-option', config.account)

    def test_account_comes_from_the_config_file_when_no_option_is_given(self):
        from tigeropen.cli.client_factory import build_config
        self._write_props(auth_mode='oauth2', account='from-file')
        config = build_config({'config_path': self.temp_dir})
        self.assertEqual('from-file', config.account)


class TestCliSurface(unittest.TestCase):
    """The CLI must not share its client registration with the SDK.

    Sharing one would mean a single clientId and a single token for both, one entry on the
    authorization page with no way to tell which is which, and revoking either taking the
    other down with it.
    """

    ISSUER = 'https://issuer.example.com'

    def test_cli_session_manager_files_itself_as_cli(self):
        from tigeropen.auth.oauth2.token_store import DEFAULT_SURFACE
        from tigeropen.cli.oauth2_config import build_session_manager
        sessions = build_session_manager(issuer=self.ISSUER)
        self.assertEqual('cli', sessions._store.surface)
        self.assertNotEqual(DEFAULT_SURFACE, sessions._store.surface,
                            'the CLI must not be filed as the Python SDK')

    def test_cli_and_sdk_registrations_land_in_different_files(self):
        """What the surface is actually for. Dropping the argument would leave the assertion
        above as the only thing standing between the two entry points."""
        from tigeropen.auth.oauth2.session_manager import OAuth2SessionManager
        from tigeropen.cli.oauth2_config import build_session_manager
        home = tempfile.mkdtemp()
        try:
            with mock.patch.dict(os.environ, {'TIGEROPEN_HOME': home}):
                cli = build_session_manager(issuer=self.ISSUER)
                sdk = OAuth2SessionManager(issuer=self.ISSUER)
            cli_file = cli._store._client_file(self.ISSUER)
            sdk_file = sdk._store._client_file(self.ISSUER)
            self.assertNotEqual(cli_file, sdk_file)
            self.assertTrue(cli_file.endswith('-cli.json'), cli_file)
        finally:
            shutil.rmtree(home, ignore_errors=True)


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
