# -*- coding: utf-8 -*-
"""Device authorization grant (RFC 8628).

Covers test-plan cases A-13..A-18 and H-16.

The polling loop sleeps between attempts, so a fake clock replaces ``time`` -- this
keeps the interval assertions exact instead of timing-dependent, and the whole file
runs in milliseconds.
"""
import shutil
import tempfile
import unittest
import unittest.mock as mock

from tests.oauth2_fakes import FakeAuthorizationServer
from tigeropen.auth.oauth2 import OAuth2Exception, OAuth2SessionManager
from tigeropen.auth.oauth2.device_authorization import (
    DEFAULT_INTERVAL_SECONDS,
    OAuth2DeviceAuthorization,
)
from tigeropen.auth.oauth2.exceptions import Category
from tigeropen.auth.oauth2.session_manager import DEVICE_SLOW_DOWN_INCREMENT_SECONDS


class FakeClock:
    """Advances only when the code under test sleeps."""

    def __init__(self):
        self.now = 1_000.0
        self.sleeps = []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class DeviceFlowTestBase(unittest.TestCase):
    def setUp(self):
        self.server = FakeAuthorizationServer()
        self.home = tempfile.mkdtemp(prefix='tigeropen-oauth2-device-')
        self.clock = FakeClock()
        patcher = mock.patch.multiple('time', time=self.clock.time, sleep=self.clock.sleep)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.home, ignore_errors=True)

    def session(self, **kwargs):
        return OAuth2SessionManager(issuer=self.server.base_url, client_id='cid',
                                    home=self.home, **kwargs)

    def login(self, session=None):
        self.shown = []
        session = session or self.session()
        return session.login_with_device_code(self.shown.append)


class DeviceAuthorizationRequestTest(DeviceFlowTestBase):

    def test_happy_path_returns_and_persists_a_token(self):
        token = self.login()
        self.assertEqual('AT1', token.access_token)
        self.assertEqual('AT1', self.session().status().access_token)

    def test_request_carries_client_id_and_scope(self):
        self.login()
        _, form = self.server.calls_to('/device')[0]
        self.assertEqual('cid', form['client_id'])
        self.assertEqual('api.quote:read api.trade:read', form['scope'])

    def test_token_request_uses_the_device_code_grant(self):
        self.login()
        _, form = self.server.token_calls()[0]
        self.assertEqual('urn:ietf:params:oauth:grant-type:device_code', form['grant_type'])
        self.assertEqual('DEV-CODE', form['device_code'])
        self.assertEqual('cid', form['client_id'])

    def test_user_is_shown_the_code_before_polling_starts(self):
        """The user cannot approve a code they have not been given yet."""
        seen = []

        def on_device(device):
            seen.append((device.user_code, len(self.server.token_calls())))

        self.session().login_with_device_code(on_device)
        self.assertEqual([('ABCD-EFGH', 0)], seen)

    def test_missing_endpoint_is_reported_before_any_request(self):
        self.server.advertise_device = False
        with self.assertRaises(OAuth2Exception) as ctx:
            self.login()
        self.assertEqual(Category.METADATA_UNAVAILABLE, ctx.exception.category)
        self.assertEqual([], self.server.calls_to('/device'))

    def test_error_response_is_reported(self):
        self.server.device_responses.append(
            {'error': 'invalid_client', 'error_description': 'unknown client'})
        with self.assertRaises(OAuth2Exception) as ctx:
            self.login()
        self.assertEqual(Category.DEVICE_AUTHORIZATION_FAILED, ctx.exception.category)
        self.assertIn('invalid_client', ctx.exception.message)

    def test_incomplete_response_is_rejected(self):
        """Without a user_code there is nothing to show, so polling would be pointless."""
        self.server.device_responses.append({'device_code': 'DEV', 'expires_in': 600})
        with self.assertRaises(OAuth2Exception) as ctx:
            self.login()
        self.assertEqual(Category.DEVICE_AUTHORIZATION_FAILED, ctx.exception.category)
        self.assertEqual([], self.server.token_calls(), 'must not poll without a user code')


class PollingTest(DeviceFlowTestBase):

    def test_authorization_pending_keeps_polling(self):
        """A-13: pending is the normal state while the user walks to their phone."""
        self.server.token_responses.extend([{'error': 'authorization_pending'}] * 3)
        token = self.login()
        self.assertEqual('AT1', token.access_token)
        self.assertEqual(4, len(self.server.token_calls()))

    def test_default_interval_is_used_when_the_server_sends_none(self):
        """RFC 8628 §3.5; Tiger's server does not send one."""
        self.server.token_responses.append({'error': 'authorization_pending'})
        self.login()
        self.assertEqual([DEFAULT_INTERVAL_SECONDS] * 2, self.clock.sleeps)

    def test_server_interval_is_honoured(self):
        self.server.device_responses.append({
            'device_code': 'DEV-CODE', 'user_code': 'UC', 'verification_uri': 'https://x',
            'expires_in': 600, 'interval': 2})
        self.login()
        self.assertEqual([2], self.clock.sleeps)

    def test_slow_down_backs_off_and_keeps_polling(self):
        """A-14: the increment is permanent, not just for the next attempt."""
        self.server.token_responses.extend([
            {'error': 'authorization_pending'},
            {'error': 'slow_down'},
            {'error': 'authorization_pending'},
        ])
        self.login()
        base = DEFAULT_INTERVAL_SECONDS
        raised = base + DEVICE_SLOW_DOWN_INCREMENT_SECONDS
        self.assertEqual([base, base, raised, raised], self.clock.sleeps)

    def test_repeated_slow_down_compounds(self):
        self.server.token_responses.extend([{'error': 'slow_down'}, {'error': 'slow_down'}])
        self.login()
        base = DEFAULT_INTERVAL_SECONDS
        step = DEVICE_SLOW_DOWN_INCREMENT_SECONDS
        self.assertEqual([base, base + step, base + 2 * step], self.clock.sleeps)

    def test_access_denied_stops_immediately(self):
        """A-15: the user said no; polling on would be harassment."""
        self.server.token_responses.append({'error': 'access_denied'})
        with self.assertRaises(OAuth2Exception) as ctx:
            self.login()
        self.assertEqual(Category.DEVICE_AUTHORIZATION_FAILED, ctx.exception.category)
        self.assertIn('denied', ctx.exception.message)
        self.assertEqual(1, len(self.server.token_calls()))

    def test_expired_token_stops_immediately(self):
        """A-16."""
        self.server.token_responses.append({'error': 'expired_token'})
        with self.assertRaises(OAuth2Exception) as ctx:
            self.login()
        self.assertEqual(Category.DEVICE_AUTHORIZATION_FAILED, ctx.exception.category)
        self.assertIn('expired', ctx.exception.message)

    def test_deadline_is_enforced_locally(self):
        """A-17: a server that answers `authorization_pending` forever must not hang
        the caller forever."""
        self.server.device_responses.append({
            'device_code': 'DEV-CODE', 'user_code': 'UC', 'verification_uri': 'https://x',
            'expires_in': 12, 'interval': 5})
        self.server.token_responses.extend([{'error': 'authorization_pending'}] * 10)

        with self.assertRaises(OAuth2Exception) as ctx:
            self.login()
        self.assertEqual(Category.DEVICE_AUTHORIZATION_FAILED, ctx.exception.category)
        self.assertIn('not approved in time', ctx.exception.message)
        # The deadline is checked before sleeping, so the sleep that crosses it is
        # followed by one last poll (12s budget, 5s interval -> polls at 5s, 10s, 15s).
        self.assertEqual(3, len(self.server.token_calls()))

    def test_unexpected_error_is_reported_as_a_token_failure(self):
        self.server.token_responses.append({'error': 'invalid_scope',
                                            'error_description': 'nope'})
        with self.assertRaises(OAuth2Exception) as ctx:
            self.login()
        self.assertEqual(Category.TOKEN_REQUEST_FAILED, ctx.exception.category)
        self.assertIn('invalid_scope', ctx.exception.message)

    def test_a_failed_device_flow_leaves_an_existing_authorization_alone(self):
        """A-18: `invalid_grant` here refers to the device code, not to the stored
        refresh token, so the stored authorization must survive."""
        from tigeropen.auth.oauth2 import OAuth2Token
        from tigeropen.auth.oauth2.token import current_millis

        s = self.session()
        s._persist(OAuth2Token(issuer=self.server.base_url, client_id='cid',
                               access_token='KEEP', refresh_token='RT',
                               expires_at=current_millis() + 3600_000))

        self.server.token_responses.append({'error': 'invalid_grant'})
        with self.assertRaises(OAuth2Exception):
            s.login_with_device_code(lambda d: None)

        self.assertEqual('KEEP', self.session().status().access_token)


class DeviceAuthorizationModelTest(unittest.TestCase):

    def test_effective_interval_falls_back_to_the_default(self):
        for value in (0, None, -1):
            self.assertEqual(DEFAULT_INTERVAL_SECONDS,
                             OAuth2DeviceAuthorization(interval=value).effective_interval())

    def test_effective_interval_uses_the_server_value(self):
        self.assertEqual(7, OAuth2DeviceAuthorization(interval=7).effective_interval())

    def test_repr_never_prints_the_device_code(self):
        """A-18 / K-02: holding the device_code is equivalent to holding the result of
        the authorization."""
        device = OAuth2DeviceAuthorization(device_code='SECRET-DEVICE-CODE',
                                           user_code='ABCD-EFGH',
                                           verification_uri='https://example.com/activate')
        text = repr(device)
        self.assertNotIn('SECRET-DEVICE-CODE', text)
        self.assertIn('ABCD-EFGH', text, 'the user code is meant to be displayed')

    def test_from_dict_of_nothing(self):
        self.assertIsNone(OAuth2DeviceAuthorization.from_dict(None))
        self.assertIsNone(OAuth2DeviceAuthorization.from_dict({}))

    def test_from_dict_keeps_the_pre_filled_uri(self):
        device = OAuth2DeviceAuthorization.from_dict({
            'device_code': 'd', 'user_code': 'u',
            'verification_uri': 'https://x/activate',
            'verification_uri_complete': 'https://x/activate?code=u'})
        self.assertEqual('https://x/activate?code=u', device.verification_uri_complete)


if __name__ == '__main__':
    unittest.main()
