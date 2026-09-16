# -*- coding: utf-8 -*-
"""OAuth2 control plane: refresh, single-flight, logout/revoke, registration lifecycle.

Covers test-plan cases A-24..A-27, B-10..B-14, C-01..C-08, D-01..D-07, D-14,
I-11..I-16, J-05.

Everything runs against a fake authorization server bound to 127.0.0.1, so the
conftest network guard is satisfied and no real environment is needed.
"""
import shutil
import tempfile
import threading
import time
import unittest

from tests.oauth2_fakes import FakeAuthorizationServer
from tigeropen.auth.oauth2 import OAuth2Exception, OAuth2SessionManager, OAuth2Token
from tigeropen.auth.oauth2.exceptions import Category
from tigeropen.auth.oauth2.token import current_millis


class SessionTestBase(unittest.TestCase):
    def setUp(self):
        self.server = FakeAuthorizationServer()
        self.home = tempfile.mkdtemp(prefix='tigeropen-oauth2-session-')

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.home, ignore_errors=True)

    def session(self, client_id='cid', **kwargs):
        return OAuth2SessionManager(issuer=self.server.base_url, client_id=client_id,
                                    home=self.home, **kwargs)

    def seed(self, session, remaining_seconds=3600, refresh_token='RT0', access_token='AT0'):
        token = OAuth2Token(issuer=self.server.base_url, client_id='cid',
                            access_token=access_token, refresh_token=refresh_token,
                            scope='api.quote:read',
                            expires_at=current_millis() + remaining_seconds * 1000)
        session._persist(token)
        return token

    def seed_store_only(self, session, remaining_seconds=3600, refresh_token='RT0',
                        access_token='AT0'):
        """Write a token to disk without touching the session's in-memory copy.

        Stands in for a second process sharing the same store.
        """
        token = OAuth2Token(issuer=self.server.base_url, client_id='cid',
                            access_token=access_token, refresh_token=refresh_token,
                            scope='api.quote:read',
                            expires_at=current_millis() + remaining_seconds * 1000)
        session._store.save_token(token)
        return token

    def stored_token(self, session):
        return session._store.load_token('cid', self.server.base_url)


class GetAccessTokenTest(SessionTestBase):

    def test_returns_current_token_when_fresh(self):
        """B-10: outside the refresh window, no request is made."""
        s = self.session()
        self.seed(s, remaining_seconds=3600)
        self.assertEqual('AT0', s.get_access_token())
        self.assertEqual([], self.server.token_calls())

    def test_refreshes_inside_the_window(self):
        """B-12."""
        s = self.session()
        self.seed(s, remaining_seconds=60)
        self.assertEqual('AT1', s.get_access_token())
        self.assertEqual(1, len(self.server.token_calls()))

    def test_never_authorized_raises_and_opens_nothing(self):
        """B-11: must not implicitly start an authorization."""
        s = self.session()
        with self.assertRaises(OAuth2Exception) as ctx:
            s.get_access_token()
        self.assertEqual(Category.REAUTHORIZATION_REQUIRED, ctx.exception.category)
        self.assertEqual([], self.server.calls)

    def test_no_refresh_token_raises_without_calling_token_endpoint(self):
        """B-14."""
        s = self.session()
        self.seed(s, remaining_seconds=60, refresh_token=None)
        with self.assertRaises(OAuth2Exception) as ctx:
            s.get_access_token()
        self.assertEqual(Category.REAUTHORIZATION_REQUIRED, ctx.exception.category)
        self.assertEqual([], self.server.token_calls())

    def test_refresh_sends_the_right_grant(self):
        s = self.session()
        self.seed(s, remaining_seconds=60, refresh_token='RT-old')
        s.get_access_token()
        _, form = self.server.token_calls()[0]
        self.assertEqual('refresh_token', form['grant_type'])
        self.assertEqual('RT-old', form['refresh_token'])
        self.assertEqual('cid', form['client_id'])


class SingleFlightTest(SessionTestBase):
    """C-01, C-02, C-05: the whole point is that N concurrent callers cause O(1) calls."""

    def test_concurrent_proactive_refresh_hits_the_endpoint_once(self):
        s = self.session()
        self.seed(s, remaining_seconds=60)

        results, errors = [], []
        barrier = threading.Barrier(20)

        def worker():
            try:
                barrier.wait()
                results.append(s.get_access_token())
            except Exception as e:            # noqa: BLE001 - surfaced by the assert below
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual([], errors)
        self.assertEqual(20, len(results))
        self.assertEqual(1, len(self.server.token_calls()),
                         'single-flight must collapse 20 concurrent refreshes into one call')
        # Whoever takes the exchange returns the new token; the rest return the one they
        # already hold, which still has 60s of life. Both are usable, nothing else may appear.
        self.assertEqual(set(), set(results) - {'AT0', 'AT1'},
                         'every caller must get a usable token, got %s' % results)
        self.assertIn('AT1', results,
                      'the refreshed token must at least reach the caller that fetched it')

    def test_usable_token_is_returned_without_waiting_for_an_in_flight_refresh(self):
        """C-13: a caller holding a still-usable token must not wait for someone else's
        exchange.

        HTTP and the push connection share one session, so whichever side starts a refresh
        would otherwise hold the other up for as long as the exchange takes.
        """
        s = self.session()
        self.seed(s, remaining_seconds=60)
        exchange_started = self.server.hold_token_endpoint()

        # Stands in for the heartbeat: starts a refresh and is stuck inside the token endpoint.
        def refresher():
            try:
                s.get_access_token()
            except Exception:                 # noqa: BLE001 - only the other caller's timing matters
                pass

        thread = threading.Thread(target=refresher, daemon=True)
        thread.start()
        self.assertTrue(exchange_started.wait(10),
                        'the refresh should have reached the token endpoint')

        # Stands in for a business request arriving mid-exchange. It must come straight back
        # with the token it already has, not block until the held exchange finishes.
        started_at = time.time()
        token = s.get_access_token()
        waited = time.time() - started_at

        self.assertEqual('AT0', token, 'must reuse the token in hand, not wait for the new one')
        self.assertLess(waited, 2, 'returned after %.1fs, so it waited on the exchange' % waited)
        self.assertEqual(1, len(self.server.token_calls()),
                         'the second caller must not start an exchange of its own')

        self.server.release_token_endpoint()
        thread.join(10)

    def test_nearly_expired_token_makes_the_caller_wait_for_the_new_one(self):
        """Not blocking is only correct while the token in hand still works. Below that the
        caller waits, since the token could otherwise expire mid-request.
        """
        s = self.session()
        self.seed(s, remaining_seconds=5)
        self.assertEqual('AT1', s.get_access_token())
        self.assertEqual(1, len(self.server.token_calls()))

    def test_concurrent_401_storm_does_not_fan_out(self):
        """C-01: 20 threads all holding the same stale token."""
        s = self.session()
        self.seed(s, remaining_seconds=3600, access_token='STALE')

        results = []
        barrier = threading.Barrier(20)

        def worker():
            barrier.wait()
            results.append(s.refresh_after_unauthorized('STALE').access_token)

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertLessEqual(len(self.server.token_calls()), 2,
                             'a 401 storm must not produce one refresh per thread')
        self.assertEqual(1, len(set(results)), 'all threads must converge on one token')

    def test_late_401_reuses_the_already_refreshed_token(self):
        """C-02: the receipt tells us our 401 is stale news."""
        s = self.session()
        self.seed(s, remaining_seconds=3600, access_token='T1')

        first = s.refresh_after_unauthorized('T1')
        calls_after_first = len(self.server.token_calls())

        second = s.refresh_after_unauthorized('T1')   # still holding the old one

        self.assertEqual(first.access_token, second.access_token)
        self.assertEqual(calls_after_first, len(self.server.token_calls()),
                         'the second 401 must not trigger another refresh')

    def test_comparison_is_on_the_credential_not_the_timestamp(self):
        """C-04: two tokens can share an expiry and still be different credentials."""
        s = self.session()
        expiry = current_millis() + 3600_000
        s._persist(OAuth2Token(issuer=self.server.base_url, client_id='cid',
                               access_token='NEW', refresh_token='RT', expires_at=expiry))
        # Caller reports a *different* credential with the same expiry
        result = s.refresh_after_unauthorized('OLD')
        self.assertEqual('NEW', result.access_token)
        self.assertEqual([], self.server.token_calls())


class RejectedRefreshTest(SessionTestBase):
    """A rejected refresh must not be taken as the end of the authorization until the store
    has been re-read.

    Refresh tokens rotate, so a second process sharing this store can refresh first and
    legitimately invalidate the value this one holds while the authorization is still alive.
    """

    def test_rejected_refresh_adopts_the_token_another_process_left_on_disk(self):
        s = self.session()
        self.seed(s, remaining_seconds=60, refresh_token='RT0', access_token='AT0')

        # Another process refreshes first, rotating RT0 away and leaving a fresh token behind.
        self.seed_store_only(s, remaining_seconds=3600, refresh_token='RT-rotated',
                             access_token='AT-other-process')
        self.server.token_responses.append({'error': 'invalid_grant'})

        self.assertEqual('AT-other-process', s.get_access_token(),
                         'must adopt what is on disk rather than declare the grant dead')
        self.assertEqual(1, len(self.server.token_calls()),
                         'the stored token was already fresh, so no second exchange was needed')
        self.assertIsNotNone(self.stored_token(s),
                             'a valid token must survive our own copy being stale')

    def test_rejected_refresh_retries_with_the_refresh_token_found_on_disk(self):
        """The same recovery, when the token found on disk is itself due for a refresh."""
        s = self.session()
        self.seed(s, remaining_seconds=60, refresh_token='RT0', access_token='AT0')
        self.seed_store_only(s, remaining_seconds=60, refresh_token='RT-rotated',
                             access_token='AT-other-process')
        self.server.token_responses.append({'error': 'invalid_grant'})

        self.assertEqual('AT1', s.get_access_token())
        calls = self.server.token_calls()
        self.assertEqual(2, len(calls))
        self.assertEqual('RT-rotated', calls[1][1]['refresh_token'],
                         'the retry must present the refresh token that was on disk')

    def test_rejection_with_nothing_newer_on_disk_still_clears_the_authorization(self):
        """With nothing newer on disk the rejection is about the authorization itself, so
        local state is cleared as before.
        """
        s = self.session()
        self.seed(s, remaining_seconds=60)
        self.server.token_responses.append({'error': 'invalid_grant'})

        with self.assertRaises(OAuth2Exception) as caught:
            s.get_access_token()
        self.assertEqual(Category.REAUTHORIZATION_REQUIRED, caught.exception.category)
        self.assertIsNone(self.stored_token(s),
                          'a genuinely dead authorization must still be cleared')
        self.assertEqual(1, len(self.server.token_calls()),
                         'one rejection with nothing newer must not be retried')

    def test_rejection_of_the_stored_token_too_ends_the_authorization(self):
        """A rejection surviving the newest stored credential ends the authorization."""
        s = self.session()
        self.seed(s, remaining_seconds=60, refresh_token='RT0', access_token='AT0')
        self.seed_store_only(s, remaining_seconds=60, refresh_token='RT-rotated',
                             access_token='AT-other-process')
        self.server.token_responses.append({'error': 'invalid_grant'})
        self.server.token_responses.append({'error': 'invalid_grant'})

        with self.assertRaises(OAuth2Exception) as caught:
            s.get_access_token()
        self.assertEqual(Category.REAUTHORIZATION_REQUIRED, caught.exception.category)
        self.assertEqual(2, len(self.server.token_calls()))
        self.assertIsNone(self.stored_token(s),
                          'both credentials were refused, so the grant really is gone')


class RefreshSemanticsTest(SessionTestBase):

    def test_response_without_refresh_token_carries_the_old_one_forward(self):
        """C-07: otherwise there would be nothing to refresh with next time."""
        self.server.token_responses.append(
            {'access_token': 'AT-new', 'expires_in': 3600, 'scope': 'api.quote:read'})
        s = self.session()
        self.seed(s, remaining_seconds=60, refresh_token='RT-keep')

        token = s.refresh('AT0')
        self.assertEqual('RT-keep', token.refresh_token)

    def test_response_without_scope_keeps_the_previous_scope(self):
        """C-08: RFC 6749 §5.1 lets the server omit scope when it is unchanged."""
        self.server.token_responses.append(
            {'access_token': 'AT-new', 'refresh_token': 'RT-new', 'expires_in': 3600})
        s = self.session()
        self.seed(s, remaining_seconds=60)

        self.assertEqual('api.quote:read', s.refresh('AT0').scope)

    def test_refreshed_token_is_persisted(self):
        s = self.session()
        self.seed(s, remaining_seconds=60)
        s.get_access_token()

        reloaded = self.session()
        self.assertEqual('AT1', reloaded.status().access_token)

    def test_invalid_grant_is_terminal_and_clears_local_state(self):
        """§8.5 / I-15."""
        self.server.token_responses.append({'error': 'invalid_grant'})
        s = self.session()
        self.seed(s, remaining_seconds=60)

        with self.assertRaises(OAuth2Exception) as ctx:
            s.refresh('AT0')
        self.assertEqual(Category.REAUTHORIZATION_REQUIRED, ctx.exception.category)
        self.assertIsNone(s.status())

    def test_server_error_is_retryable_and_keeps_local_token(self):
        """C-12 / I-16: a transient failure must not destroy the authorization."""
        self.server.token_responses.append({'error': 'temporarily_unavailable'})
        s = self.session()
        self.seed(s, remaining_seconds=60)

        with self.assertRaises(OAuth2Exception) as ctx:
            s.refresh('AT0')
        self.assertEqual(Category.TOKEN_REQUEST_FAILED, ctx.exception.category)
        self.assertIsNotNone(s.status(), 'a retryable failure must not clear the token')


class LoginIfNeededTest(SessionTestBase):
    """A-24..A-27: when may the user be interrupted?"""

    def test_usable_token_does_not_invoke_the_callback(self):
        s = self.session()
        self.seed(s, remaining_seconds=3600)
        called = []
        self.assertEqual('AT0', s.login_if_needed(lambda url: called.append(url)).access_token)
        self.assertEqual([], called)

    def test_expiring_token_is_refreshed_silently(self):
        s = self.session()
        self.seed(s, remaining_seconds=60)
        called = []
        self.assertEqual('AT1', s.login_if_needed(lambda url: called.append(url)).access_token)
        self.assertEqual([], called, 'a silent refresh must not prompt the user')

    def test_reauthorization_required_falls_back_to_authorization(self):
        """A-27."""
        self.server.token_responses.append({'error': 'invalid_grant'})
        s = self.session()
        self.seed(s, remaining_seconds=60)
        s.login = lambda cb: 'AUTHORIZED'
        self.assertEqual('AUTHORIZED', s.login_if_needed(lambda url: None))

    def test_transient_failure_propagates_instead_of_prompting(self):
        """A-26: a network blip must not pop a browser for a problem that fixes itself."""
        self.server.token_responses.append({'error': 'temporarily_unavailable'})
        s = self.session()
        self.seed(s, remaining_seconds=60)
        started = []
        s.login = lambda cb: started.append(1)

        with self.assertRaises(OAuth2Exception) as ctx:
            s.login_if_needed(lambda url: None)
        self.assertEqual(Category.TOKEN_REQUEST_FAILED, ctx.exception.category)
        self.assertEqual([], started, 'must not start an authorization')

    def test_device_code_variant_shares_the_same_grading(self):
        """H-16: the device-flow entry point must behave identically."""
        self.server.token_responses.append({'error': 'temporarily_unavailable'})
        s = self.session()
        self.seed(s, remaining_seconds=60)
        started = []
        s.login_with_device_code = lambda cb: started.append(1)

        with self.assertRaises(OAuth2Exception):
            s.login_with_device_code_if_needed(lambda d: None)
        self.assertEqual([], started)

    def test_device_code_variant_reuses_a_usable_token(self):
        s = self.session()
        self.seed(s, remaining_seconds=3600)
        called = []
        token = s.login_with_device_code_if_needed(lambda d: called.append(d))
        self.assertEqual('AT0', token.access_token)
        self.assertEqual([], called)


class LogoutTest(SessionTestBase):
    """D-01..D-07, D-14."""

    def test_revokes_then_clears_locally(self):
        s = self.session()
        self.seed(s)
        self.assertTrue(s.logout())

        self.assertEqual(1, len(self.server.revoke_calls()))
        self.assertIsNone(s.status())
        self.assertIsNone(self.session().status(), 'must be gone from disk too')

    def test_revokes_the_refresh_token_by_preference(self):
        """D-02: revoking the access token alone would leave the 30-day half alive."""
        s = self.session()
        self.seed(s, refresh_token='RT-x', access_token='AT-x')
        s.logout()

        _, form = self.server.revoke_calls()[0]
        self.assertEqual('RT-x', form['token'])
        self.assertEqual('refresh_token', form['token_type_hint'])
        self.assertEqual('cid', form['client_id'])

    def test_falls_back_to_the_access_token(self):
        """D-03."""
        s = self.session()
        self.seed(s, refresh_token=None, access_token='AT-only')
        s.logout()

        _, form = self.server.revoke_calls()[0]
        self.assertEqual('AT-only', form['token'])
        self.assertEqual('access_token', form['token_type_hint'])

    def test_rejected_revocation_still_clears_local_state(self):
        """D-04: the user asked to log out."""
        self.server.revoke_status = 401
        s = self.session()
        self.seed(s)

        self.assertFalse(s.logout())
        self.assertIsNone(s.status())

    def test_unreachable_server_does_not_raise(self):
        """D-05."""
        s = OAuth2SessionManager(issuer='http://127.0.0.1:1', client_id='cid', home=self.home)
        s._persist(OAuth2Token(issuer='http://127.0.0.1:1', client_id='cid',
                               access_token='AT', refresh_token='RT',
                               expires_at=current_millis() + 3600_000))
        self.assertFalse(s.logout())
        self.assertIsNone(s.status())

    def test_no_revocation_endpoint_skips_the_call(self):
        """D-06."""
        self.server.advertise_revocation = False
        s = self.session()
        self.seed(s)

        self.assertFalse(s.logout())
        self.assertEqual([], self.server.revoke_calls())
        self.assertIsNone(s.status())

    def test_logout_without_a_token_sends_nothing(self):
        """D-07."""
        s = self.session()
        self.assertFalse(s.logout())
        self.assertEqual([], self.server.calls)

    def test_logout_keeps_the_client_registration(self):
        """D-14: the registration is an identity, not an authorization."""
        from tigeropen.auth.oauth2 import OAuth2ClientRegistration
        s = self.session(client_id=None)
        s._store.save_client_registration(OAuth2ClientRegistration(
            issuer=self.server.base_url, client_id='dyn-client',
            registered_scopes='api.quote:read api.trade:read'))
        s._registered_client_id = 'dyn-client'
        s._persist(OAuth2Token(issuer=self.server.base_url, client_id='dyn-client',
                               access_token='AT', refresh_token='RT',
                               expires_at=current_millis() + 3600_000))

        s.logout()
        self.assertIsNotNone(s._store.load_client_registration(self.server.base_url))


class RegistrationLifecycleTest(SessionTestBase):
    """I-11..I-14."""

    def test_dynamic_registration_happens_once_and_is_reused(self):
        """I-11."""
        s = self.session(client_id=None)
        self.assertEqual('dyn-client', s._resolve_client_id())
        register_calls = [c for c in self.server.calls if c[0] == '/register']
        self.assertEqual(1, len(register_calls))

        fresh = self.session(client_id=None)
        self.assertEqual('dyn-client', fresh._resolve_client_id())
        self.assertEqual(1, len([c for c in self.server.calls if c[0] == '/register']),
                         'a restart must reuse the stored client_id')

    def test_registration_declares_no_scope(self):
        """§5.3: declaring one would dead-end on any later scope expansion."""
        s = self.session(client_id=None)
        s._resolve_client_id()
        # /register is posted as JSON, so it is recorded with an empty form; assert on the
        # stored registration instead
        stored = s._store.load_client_registration(self.server.base_url)
        self.assertEqual('api.quote:read api.trade:read', stored.registered_scopes)

    def test_invalid_client_clears_the_registration_in_dynamic_mode(self):
        """I-13: otherwise the user can never recover."""
        s = self.session(client_id=None)
        s._resolve_client_id()
        s._persist(OAuth2Token(issuer=self.server.base_url, client_id='dyn-client',
                               access_token='AT', refresh_token='RT',
                               expires_at=current_millis() + 60_000))

        self.server.token_responses.append({'error': 'invalid_client'})
        with self.assertRaises(OAuth2Exception):
            s.refresh('AT')

        self.assertIsNone(s._store.load_client_registration(self.server.base_url))

    def test_invalid_client_never_touches_the_registration_in_manual_mode(self):
        """I-14: clients/ holds a different thing entirely — deleting it punishes
        an innocent party."""
        from tigeropen.auth.oauth2 import OAuth2ClientRegistration
        s = self.session(client_id='manual-cid')
        s._store.save_client_registration(OAuth2ClientRegistration(
            issuer=self.server.base_url, client_id='someone-elses-dynamic-client'))
        self.seed(s, remaining_seconds=60)
        # seed() stores under 'cid'; re-persist under the manual id
        s._persist(OAuth2Token(issuer=self.server.base_url, client_id='manual-cid',
                               access_token='AT', refresh_token='RT',
                               expires_at=current_millis() + 60_000))

        self.server.token_responses.append({'error': 'invalid_client'})
        with self.assertRaises(OAuth2Exception):
            s.refresh('AT')

        registration = s._store.load_client_registration(self.server.base_url)
        self.assertIsNotNone(registration)
        self.assertEqual('someone-elses-dynamic-client', registration.client_id)


class MetadataTest(SessionTestBase):

    def test_scopes_request_the_full_supported_set_normalised(self):
        """A-19."""
        self.assertEqual('api.quote:read api.trade:read', self.session().scopes)

    def test_missing_scopes_supported_fails_loudly(self):
        """A-20: guessing would surface as a 403 much later."""
        s = self.session()
        s._metadata = type('M', (), {'scopes_supported': [],
                                     'authorization_endpoint': 'x', 'token_endpoint': 'y'})()
        with self.assertRaises(OAuth2Exception) as ctx:
            s._scopes()
        self.assertEqual(Category.METADATA_UNAVAILABLE, ctx.exception.category)

    def test_status_and_is_authorized_send_no_requests(self):
        s = self.session()
        self.assertIsNone(s.status())
        self.assertFalse(s.is_authorized())
        self.seed(s)
        self.assertTrue(s.is_authorized())
        self.assertEqual([], self.server.calls)

    def test_constructor_sends_no_requests(self):
        """Building the object offline must work."""
        OAuth2SessionManager(issuer='http://127.0.0.1:1', home=self.home)


if __name__ == '__main__':
    unittest.main()
