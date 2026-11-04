# -*- coding: utf-8 -*-
"""
Tests for CLI OAuth2 support: config init --auth oauth2, auth commands, and the
OAuth2 branch of build_config / push connect.
"""
import json
import logging
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


class TestCliRegistrationIdentity(unittest.TestCase):
    """What the user sees on the authorization page, and revokes by."""

    def test_cli_registers_under_its_own_name_and_surface(self):
        from tigeropen.cli.oauth2_config import CLIENT_NAME, SURFACE, build_session_manager
        self.assertEqual('cli', SURFACE)
        self.assertEqual('Tiger OpenAPI CLI', CLIENT_NAME)
        sessions = build_session_manager()
        self.assertEqual(CLIENT_NAME, sessions._client_name)

    def test_cli_name_is_not_the_sdk_name(self):
        """They are separate applications to the user; one name for both makes the entry on
        the authorization page unrecognisable."""
        from tigeropen.auth.oauth2.session_manager import CLIENT_NAME as SDK_NAME
        from tigeropen.cli.oauth2_config import CLIENT_NAME as CLI_NAME
        self.assertNotEqual(SDK_NAME, CLI_NAME)


class TestRemoveStoredCredentials(unittest.TestCase):
    """The store root is shared with the SDKs, so deletion must be scoped by surface."""

    def setUp(self):
        self.home = os.environ['TIGEROPEN_HOME']
        os.makedirs(os.path.join(self.home, 'clients'), exist_ok=True)
        os.makedirs(os.path.join(self.home, 'tokens'), exist_ok=True)

    def _write(self, rel, payload):
        path = os.path.join(self.home, rel)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f)
        return path

    def _seed(self, surface, client_id, issuer_hash='h1'):
        reg = self._write('clients/%s-%s.json' % (issuer_hash, surface),
                          {'issuer': 'https://issuer', 'client_id': client_id,
                           'client_name': 'n', 'registered_scopes': 's'})
        tok = self._write('tokens/%s.json' % client_id,
                          {'schema_version': 1, 'client_id': client_id,
                           'issuer': 'https://issuer', 'access_token': 'AT',
                           'refresh_token': 'RT', 'expires_at': 0})
        return reg, tok

    def _remove(self, **kwargs):
        from tigeropen.cli.oauth2_config import remove_stored_credentials
        with mock.patch('tigeropen.cli.oauth2_config._revoke_quietly', return_value=True):
            return remove_stored_credentials(**kwargs)

    def test_other_surfaces_are_left_untouched(self):
        """A shared root means a careless delete takes the Java SDK's authorization with it."""
        cli_reg, cli_tok = self._seed('cli', 'cid-cli')
        java_reg, java_tok = self._seed('sdk-java', 'cid-java')
        py_reg, py_tok = self._seed('sdk-python', 'cid-py')

        self._remove()

        for path in (cli_reg, cli_tok):
            self.assertFalse(os.path.exists(path), path)
        for path in (java_reg, java_tok, py_reg, py_tok):
            self.assertTrue(os.path.exists(path), path)

    def test_the_store_root_is_never_removed(self):
        self._seed('cli', 'cid-cli')
        self._remove()
        self.assertTrue(os.path.isdir(self.home))
        self.assertTrue(os.path.isdir(os.path.join(self.home, 'tokens')))

    def test_every_issuer_registered_by_the_cli_is_cleared(self):
        """Switching issuers leaves one registration per issuer, all of them the CLI's."""
        first = self._seed('cli', 'cid-1', issuer_hash='h1')
        second = self._seed('cli', 'cid-2', issuer_hash='h2')
        _, removed = self._remove()
        for path in first + second:
            self.assertFalse(os.path.exists(path), path)
        self.assertEqual(4, len(removed))

    def test_a_manual_client_id_has_its_token_removed(self):
        """With a configured clientId there is no registration file to find the token by."""
        token = self._write('tokens/manual-cid.json',
                            {'schema_version': 1, 'client_id': 'manual-cid',
                             'issuer': 'https://issuer', 'access_token': 'AT',
                             'refresh_token': 'RT', 'expires_at': 0})
        self._remove(client_id='manual-cid')
        self.assertFalse(os.path.exists(token))

    def test_an_unreadable_registration_is_still_removed(self):
        path = os.path.join(self.home, 'clients', 'h1-cli.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('not json')
        self._remove()
        self.assertFalse(os.path.exists(path))

    def test_a_client_id_that_is_not_its_own_file_name_is_still_cleaned_up(self):
        """clientId comes from the server or from configuration, and is sanitised before it
        becomes a file name. Rebuilding the path from the raw value looks at a file that was
        never written, so the token survives while its registration is deleted."""
        from tigeropen.auth.oauth2.token_store import _safe_file_name
        for raw in ('a/b', '../../etc/passwd'):
            with self.subTest(client_id=raw):
                reg = self._write('clients/%s-cli.json' % _safe_file_name(raw),
                                  {'issuer': 'https://issuer', 'client_id': raw,
                                   'client_name': 'n', 'registered_scopes': 's'})
                token = self._write('tokens/%s.json' % _safe_file_name(raw),
                                    {'schema_version': 1, 'client_id': raw,
                                     'issuer': 'https://issuer', 'access_token': 'AT',
                                     'refresh_token': 'RT', 'expires_at': 0})
                self.assertNotEqual(os.path.basename(token), raw + '.json')

                _, removed = self._remove()

                self.assertFalse(os.path.exists(token), 'orphaned token left behind')
                self.assertFalse(os.path.exists(reg))
                self.assertIn(token, removed, 'the reported path must be the real one')

    def test_nothing_stored_reports_nothing_removed(self):
        _, removed = self._remove()
        self.assertEqual([], removed)

    def test_a_failed_revocation_does_not_stop_local_cleanup(self):
        """The package is coming off either way; leaving the token behind is the worse
        outcome."""
        from tigeropen.cli.oauth2_config import remove_stored_credentials
        _, token = self._seed('cli', 'cid-cli')
        with mock.patch('tigeropen.cli.oauth2_config.build_session_manager',
                        side_effect=RuntimeError('network down')):
            revoked, removed = remove_stored_credentials()
        self.assertFalse(revoked)
        self.assertFalse(os.path.exists(token))


class TestSdkLogging(unittest.TestCase):
    """The SDK logs through more than one tree, and silencing one leaves the rest on stderr."""

    def setUp(self):
        self._root_level = logging.getLogger().level

    def tearDown(self):
        from tigeropen.cli.main import SDK_LOGGERS
        for name in SDK_LOGGERS:
            logging.getLogger(name).setLevel(logging.NOTSET)
        logging.getLogger().setLevel(self._root_level)

    def test_every_sdk_logger_tree_is_silenced(self):
        """``tiger_openapi`` and ``tigeropen`` are siblings: neither covers the other."""
        from tigeropen.cli.main import _configure_sdk_logging
        _configure_sdk_logging(False)
        for name in ('tiger_openapi',
                     'tigeropen',
                     'tigeropen.auth.oauth2.session_manager',
                     'tigeropen.cli.settings'):
            self.assertEqual(logging.CRITICAL,
                             logging.getLogger(name).getEffectiveLevel(), name)

    def test_verbose_reaches_the_root_logger_too(self):
        """The push transport logs through the root logger, so a stream cannot be diagnosed
        without it."""
        from tigeropen.cli.main import _configure_sdk_logging
        _configure_sdk_logging(True)
        self.assertEqual(logging.DEBUG, logging.getLogger('tigeropen').getEffectiveLevel())
        self.assertEqual(logging.DEBUG, logging.getLogger().getEffectiveLevel())


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
