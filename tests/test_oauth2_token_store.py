# -*- coding: utf-8 -*-
"""OAuth2 local persistence.

Covers test-plan cases I-01..I-08, I-10, I-11, I-15, I-16, L-13.
Filesystem only — no network.
"""
import json
import os
import shutil
import stat
import tempfile
import unittest

from tigeropen.auth.oauth2 import OAuth2ClientRegistration, OAuth2Exception, OAuth2Token, OAuth2TokenStore
from tigeropen.auth.oauth2.exceptions import Category
from tigeropen.auth.oauth2.token import current_millis

ISSUER = 'https://as.example.com'
CLIENT_ID = 'client-abc'


def a_token(client_id=CLIENT_ID, issuer=ISSUER, **kwargs):
    kwargs.setdefault('access_token', 'AT')
    kwargs.setdefault('refresh_token', 'RT')
    kwargs.setdefault('scope', 'api.quote:read')
    kwargs.setdefault('expires_at', current_millis() + 3600_000)
    return OAuth2Token(issuer=issuer, client_id=client_id, **kwargs)


class StoreTestBase(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix='tigeropen-oauth2-store-')
        self.store = OAuth2TokenStore(self.home)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def token_path(self, client_id=CLIENT_ID):
        return os.path.join(self.home, 'tokens', client_id + '.json')


class RoundTripTest(StoreTestBase):

    def test_save_then_load(self):
        self.store.save_token(a_token())
        loaded = self.store.load_token(CLIENT_ID, ISSUER)
        self.assertEqual('AT', loaded.access_token)
        self.assertEqual('RT', loaded.refresh_token)
        self.assertEqual('api.quote:read', loaded.scope)

    def test_missing_file_is_not_an_error(self):
        self.assertIsNone(self.store.load_token('nobody', ISSUER))

    def test_on_disk_format(self):
        """I-03: the field set is a cross-language contract."""
        self.store.save_token(a_token())
        with open(self.token_path()) as f:
            data = json.load(f)
        self.assertEqual(
            {'schema_version', 'issuer', 'client_id', 'access_token',
             'refresh_token', 'token_type', 'scope', 'expires_at'},
            set(data))
        self.assertEqual(1, data['schema_version'])
        self.assertEqual('Bearer', data['token_type'])

    def test_expires_at_is_epoch_millis(self):
        """B-09: an absolute millisecond timestamp, not expires_in."""
        self.store.save_token(a_token())
        with open(self.token_path()) as f:
            expires_at = json.load(f)['expires_at']
        self.assertGreater(expires_at, 1_600_000_000_000)  # clearly millis, not seconds

    def test_delete(self):
        self.store.save_token(a_token())
        self.store.delete_token(CLIENT_ID)
        self.assertIsNone(self.store.load_token(CLIENT_ID, ISSUER))

    def test_delete_is_idempotent(self):
        self.store.delete_token(CLIENT_ID)
        self.store.delete_token(None)  # must not raise

    def test_save_without_client_id_is_rejected(self):
        with self.assertRaises(OAuth2Exception) as ctx:
            self.store.save_token(OAuth2Token(issuer=ISSUER, access_token='AT'))
        self.assertEqual(Category.STORAGE_FAILED, ctx.exception.category)


class PermissionTest(StoreTestBase):
    """I-01: the token file is a credential at rest."""

    @unittest.skipIf(os.name == 'nt', 'POSIX permissions only')
    def test_token_file_is_0600(self):
        self.store.save_token(a_token())
        self.assertEqual(0o600, stat.S_IMODE(os.stat(self.token_path()).st_mode))

    @unittest.skipIf(os.name == 'nt', 'POSIX permissions only')
    def test_directories_are_0700(self):
        self.store.save_token(a_token())
        self.store.save_client_registration(
            OAuth2ClientRegistration(issuer=ISSUER, client_id=CLIENT_ID))
        for sub in ('tokens', 'clients'):
            mode = stat.S_IMODE(os.stat(os.path.join(self.home, sub)).st_mode)
            self.assertEqual(0o700, mode, sub)

    @unittest.skipIf(os.name == 'nt', 'POSIX permissions only')
    def test_permissions_survive_overwrite(self):
        self.store.save_token(a_token())
        self.store.save_token(a_token(access_token='AT2'))
        self.assertEqual(0o600, stat.S_IMODE(os.stat(self.token_path()).st_mode))


class AtomicWriteTest(StoreTestBase):
    """I-02: a crash mid-write must not leave a truncated JSON file."""

    def test_no_temp_files_left_behind(self):
        self.store.save_token(a_token())
        leftovers = [n for n in os.listdir(os.path.join(self.home, 'tokens'))
                     if n.startswith('.tmp-')]
        self.assertEqual([], leftovers)

    def test_rename_failure_leaves_previous_content_intact(self):
        """The rename is the commit point: if it fails, the old file must survive."""
        self.store.save_token(a_token(access_token='OLD'))
        original = open(self.token_path()).read()

        import unittest.mock as mock
        with mock.patch('os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OAuth2Exception) as ctx:
                self.store.save_token(a_token(access_token='NEW'))
        self.assertEqual(Category.STORAGE_FAILED, ctx.exception.category)

        self.assertEqual(original, open(self.token_path()).read())

    def test_rename_failure_cleans_up_the_temp_file(self):
        """A failed write must not leave debris behind for the next run to trip on."""
        import unittest.mock as mock
        with mock.patch('os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OAuth2Exception):
                self.store.save_token(a_token())

        leftovers = [n for n in os.listdir(os.path.join(self.home, 'tokens'))
                     if n.startswith('.tmp-')]
        self.assertEqual([], leftovers)

    def test_temp_file_is_created_in_the_same_directory(self):
        """A cross-filesystem rename is not atomic, so the temp file must be a sibling."""
        import unittest.mock as mock
        seen = {}
        real_mkstemp = tempfile.mkstemp

        def spy(*args, **kwargs):
            seen['dir'] = kwargs.get('dir')
            return real_mkstemp(*args, **kwargs)

        with mock.patch('tempfile.mkstemp', side_effect=spy):
            self.store.save_token(a_token())
        self.assertEqual(os.path.dirname(self.token_path()), seen['dir'])


class IssuerBindingTest(StoreTestBase):
    """I-04: prevents sending a staging token to production."""

    def test_mismatched_issuer_is_a_silent_cache_miss(self):
        self.store.save_token(a_token())
        self.assertIsNone(self.store.load_token(CLIENT_ID, 'https://other.example.com'))

    def test_matching_issuer_loads(self):
        self.store.save_token(a_token())
        self.assertIsNotNone(self.store.load_token(CLIENT_ID, ISSUER))

    def test_no_expected_issuer_skips_the_check(self):
        self.store.save_token(a_token())
        self.assertIsNotNone(self.store.load_token(CLIENT_ID, None))


class CorruptionTest(StoreTestBase):
    """I-05..I-07: bad local state must never crash the caller."""

    def _write_raw(self, text):
        path = self.token_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(text)

    def test_unknown_schema_version_fails_loudly(self):
        """I-05: guessing at an unknown format is worse than refusing."""
        self.store.save_token(a_token())
        data = json.load(open(self.token_path()))
        data['schema_version'] = 99
        json.dump(data, open(self.token_path(), 'w'))

        with self.assertRaises(OAuth2Exception) as ctx:
            self.store.load_token(CLIENT_ID, ISSUER)
        self.assertEqual(Category.STORAGE_FAILED, ctx.exception.category)

    def test_malformed_json_is_treated_as_absent(self):
        """I-06: re-authorising beats crashing."""
        self._write_raw('{not json at all')
        self.assertIsNone(self.store.load_token(CLIENT_ID, ISSUER))

    def test_empty_file_is_treated_as_absent(self):
        self._write_raw('')
        self.assertIsNone(self.store.load_token(CLIENT_ID, ISSUER))

    def test_json_null_is_treated_as_absent(self):
        self._write_raw('null')
        self.assertIsNone(self.store.load_token(CLIENT_ID, ISSUER))

    def test_missing_refresh_token_field(self):
        """I-07: readable, but the caller must see there is nothing to refresh with."""
        self.store.save_token(a_token())
        data = json.load(open(self.token_path()))
        del data['refresh_token']
        json.dump(data, open(self.token_path(), 'w'))

        loaded = self.store.load_token(CLIENT_ID, ISSUER)
        self.assertIsNotNone(loaded)
        self.assertFalse(loaded.has_refresh_token())

    def test_missing_expires_at_defaults_to_expired(self):
        self.store.save_token(a_token())
        data = json.load(open(self.token_path()))
        del data['expires_at']
        json.dump(data, open(self.token_path(), 'w'))

        loaded = self.store.load_token(CLIENT_ID, ISSUER)
        self.assertEqual(0, loaded.expires_at)
        self.assertTrue(loaded.needs_refresh(0))


class ClientRegistrationTest(StoreTestBase):
    """I-11, I-15: the registration is an identity, not an authorization."""

    def _reg(self, **kwargs):
        kwargs.setdefault('issuer', ISSUER)
        kwargs.setdefault('client_id', CLIENT_ID)
        kwargs.setdefault('registered_scopes', 'api.quote:read')
        return OAuth2ClientRegistration(**kwargs)

    def test_roundtrip(self):
        self.store.save_client_registration(self._reg())
        loaded = self.store.load_client_registration(ISSUER)
        self.assertEqual(CLIENT_ID, loaded.client_id)
        self.assertEqual('api.quote:read', loaded.registered_scopes)

    def test_load_client_id_shortcut(self):
        self.store.save_client_registration(self._reg())
        self.assertEqual(CLIENT_ID, self.store.load_client_id(ISSUER))

    def test_keyed_by_issuer_not_client_id(self):
        """It is looked up before any client_id is known."""
        self.store.save_client_registration(self._reg())
        self.assertIsNone(self.store.load_client_registration('https://other.example.com'))

    def test_filename_is_the_issuer_hash_and_surface(self):
        from tigeropen.auth.oauth2.token_store import DEFAULT_SURFACE, hash_issuer
        self.store.save_client_registration(self._reg())
        self.assertEqual(['%s-%s.json' % (hash_issuer(ISSUER), DEFAULT_SURFACE)],
                         os.listdir(os.path.join(self.home, 'clients')))

    def test_deleting_the_token_keeps_the_registration(self):
        """I-15 / D-14: otherwise every logout piles up a new client on the server."""
        self.store.save_token(a_token())
        self.store.save_client_registration(self._reg())

        self.store.delete_token(CLIENT_ID)

        self.assertIsNone(self.store.load_token(CLIENT_ID, ISSUER))
        self.assertIsNotNone(self.store.load_client_registration(ISSUER))

    def test_delete_registration(self):
        self.store.save_client_registration(self._reg())
        self.store.delete_client_registration(ISSUER)
        self.assertIsNone(self.store.load_client_registration(ISSUER))

    def test_malformed_registration_is_treated_as_absent(self):
        self.store.save_client_registration(self._reg())
        path = self.store._client_file(ISSUER)
        with open(path, 'w') as f:
            f.write('{broken')
        self.assertIsNone(self.store.load_client_registration(ISSUER))


class SurfaceIsolationTest(StoreTestBase):
    """Each entry point owns its own registration.

    Without this, whichever entry point ran first would own the registration and every
    other one would silently inherit its identity -- one name on the authorization page,
    one revocation switch for all of them, and one shared token file whose refresh-token
    rotation they would race over.
    """

    def _store_for(self, surface):
        return OAuth2TokenStore(self.home, surface)

    def _reg_for(self, client_id):
        return OAuth2ClientRegistration(issuer=ISSUER, client_id=client_id,
                                        registered_scopes='api.quote:read')

    def test_each_surface_registers_its_own_client(self):
        for surface, client_id in (('sdk-python', 'py-1'), ('sdk-java', 'java-1'),
                                   ('cli', 'cli-1'), ('mcp', 'mcp-1')):
            self._store_for(surface).save_client_registration(self._reg_for(client_id))

        for surface, client_id in (('sdk-python', 'py-1'), ('sdk-java', 'java-1'),
                                   ('cli', 'cli-1'), ('mcp', 'mcp-1')):
            self.assertEqual(client_id, self._store_for(surface).load_client_id(ISSUER), surface)

    def test_one_surface_does_not_see_anothers_registration(self):
        self._store_for('cli').save_client_registration(self._reg_for('cli-1'))

        self.assertIsNone(self._store_for('mcp').load_client_id(ISSUER))
        self.assertIsNone(self._store_for('sdk-python').load_client_id(ISSUER))

    def test_deleting_one_surface_leaves_the_others(self):
        """An ``invalid_client`` on one entry point must not unregister the rest."""
        self._store_for('cli').save_client_registration(self._reg_for('cli-1'))
        self._store_for('mcp').save_client_registration(self._reg_for('mcp-1'))

        self._store_for('cli').delete_client_registration(ISSUER)

        self.assertIsNone(self._store_for('cli').load_client_id(ISSUER))
        self.assertEqual('mcp-1', self._store_for('mcp').load_client_id(ISSUER))

    def test_default_surface_is_the_python_sdk(self):
        from tigeropen.auth.oauth2.token_store import DEFAULT_SURFACE
        self.assertEqual('sdk-python', DEFAULT_SURFACE)
        self.assertEqual(DEFAULT_SURFACE, OAuth2TokenStore(self.home).surface)

    def test_surface_must_be_usable_verbatim_as_a_file_name(self):
        """Rejected rather than sanitised: silently rewriting would file two entry points
        under one name, which is exactly what the surface exists to prevent."""
        for bad in ('SDK-Java', 'sdk_python', '../etc', '', None, 'a b', '-leading'):
            with self.assertRaises(OAuth2Exception, msg=repr(bad)):
                OAuth2TokenStore(self.home, bad)

    def test_token_files_are_not_keyed_by_surface(self):
        """They need no surface -- distinct clients already mean distinct file names."""
        self._store_for('cli').save_token(a_token(client_id='shared-manual-id'))

        self.assertIsNotNone(
            self._store_for('mcp').load_token('shared-manual-id', ISSUER),
            'a manually configured client ID is shared on purpose: one ID, one application')


class HomeResolutionTest(unittest.TestCase):
    """§7.1: deliberately not the current working directory."""

    def test_explicit_home_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(os.path.abspath(tmp), OAuth2TokenStore(tmp).home)

    def test_env_var_is_used_when_no_explicit_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = os.environ.get('TIGEROPEN_HOME')
            os.environ['TIGEROPEN_HOME'] = tmp
            try:
                self.assertEqual(os.path.abspath(tmp), OAuth2TokenStore().home)
            finally:
                if old is None:
                    os.environ.pop('TIGEROPEN_HOME', None)
                else:
                    os.environ['TIGEROPEN_HOME'] = old

    def test_default_is_under_user_home(self):
        old = os.environ.pop('TIGEROPEN_HOME', None)
        try:
            expected = os.path.abspath(os.path.expanduser('~/.tiger/openapi'))
            self.assertEqual(expected, OAuth2TokenStore().home)
        finally:
            if old is not None:
                os.environ['TIGEROPEN_HOME'] = old

    def test_home_is_absolute(self):
        """L-13: a relative path would follow the process's cwd, which is exactly
        what the legacy license-token store does — the two must not collide."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(os.path.isabs(OAuth2TokenStore(tmp).home))


class TokenModelTest(unittest.TestCase):
    """B-10: the refresh window boundary."""

    def test_needs_refresh_boundary(self):
        token = a_token(expires_at=current_millis() + 301_000)
        self.assertFalse(token.needs_refresh(300_000))

        token = a_token(expires_at=current_millis() + 299_000)
        self.assertTrue(token.needs_refresh(300_000))

    def test_expired_token_needs_refresh(self):
        self.assertTrue(a_token(expires_at=current_millis() - 1).needs_refresh(0))

    def test_remaining_millis_is_negative_once_expired(self):
        self.assertLess(a_token(expires_at=current_millis() - 5000).remaining_millis(), 0)

    def test_has_refresh_token(self):
        self.assertTrue(a_token().has_refresh_token())
        self.assertFalse(a_token(refresh_token=None).has_refresh_token())
        self.assertFalse(a_token(refresh_token='').has_refresh_token())

    def test_repr_leaks_no_credential(self):
        """K-02."""
        token = a_token(access_token='secret-access', refresh_token='secret-refresh')
        text = repr(token)
        self.assertNotIn('secret-access', text)
        self.assertNotIn('secret-refresh', text)
        self.assertIn(CLIENT_ID, text)


if __name__ == '__main__':
    unittest.main()
