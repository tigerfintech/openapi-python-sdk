# -*- coding: utf-8 -*-
"""Authorization-code flow: the `state` check and callback handling.

Covers test-plan cases A-01..A-06, A-09, A-28..A-32.

`state` is the CSRF defence of the whole browser flow: it is the only thing tying the
callback back to the authorization *this process* started. The check was implemented in
both SDKs but had **no test on either side** -- these fill that gap.

The flow is driven end to end: `login()` runs on a worker thread, the authorization URL
is intercepted, and the callback is delivered by hand to the real loopback port.
"""
import shutil
import tempfile
import threading
import unittest
import urllib.request
from urllib.parse import parse_qs, urlparse

from tests.oauth2_fakes import FakeAuthorizationServer
from tigeropen.auth.oauth2 import OAuth2Exception, OAuth2SessionManager
from tigeropen.auth.oauth2.exceptions import Category


class AuthorizationFlowTestBase(unittest.TestCase):
    def setUp(self):
        self.server = FakeAuthorizationServer()
        self.home = tempfile.mkdtemp(prefix='tigeropen-oauth2-authflow-')

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.home, ignore_errors=True)

    def session(self):
        return OAuth2SessionManager(issuer=self.server.base_url, client_id='cid',
                                    home=self.home, authorize_timeout_seconds=5)

    def run_login(self, respond):
        """Run login() on a worker thread; `respond(params)` delivers the callback.

        :param respond: called with the authorization request's query params; must return
            the query string to deliver to the loopback port
        :return: (token, error) -- exactly one is None
        """
        outcome = {}
        seen = {}

        def worker():
            try:
                outcome['token'] = self.session().login(on_url)
            except Exception as e:                     # noqa: BLE001 - asserted by caller
                outcome['error'] = e

        def on_url(url):
            query = parse_qs(urlparse(url).query)
            seen['params'] = {k: v[0] for k, v in query.items()}
            redirect_uri = seen['params']['redirect_uri']
            threading.Thread(
                target=self._deliver,
                args=(redirect_uri, respond(seen['params'])),
                daemon=True).start()

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(15)
        self.assertFalse(thread.is_alive(), 'login() did not finish')
        self.seen_params = seen.get('params', {})
        return outcome.get('token'), outcome.get('error')

    @staticmethod
    def _deliver(redirect_uri, query):
        try:
            with urllib.request.urlopen(redirect_uri + '?' + query, timeout=5) as response:
                response.read()
        except Exception:                              # noqa: BLE001 - best effort
            pass


class StateValidationTest(AuthorizationFlowTestBase):
    """A-03: the callback must prove it belongs to the flow we started."""

    def test_matching_state_completes_the_flow(self):
        token, error = self.run_login(lambda p: 'code=the-code&state=' + p['state'])

        self.assertIsNone(error)
        self.assertEqual('AT1', token.access_token)

    def test_mismatched_state_is_rejected(self):
        """The core CSRF check: an attacker-initiated flow lands a callback we never started."""
        token, error = self.run_login(lambda p: 'code=attacker-code&state=not-our-state')

        self.assertIsNone(token)
        self.assertIsInstance(error, OAuth2Exception)
        self.assertEqual(Category.CALLBACK_FAILED, error.category)
        self.assertIn('state mismatch', error.message)

    def test_mismatched_state_never_redeems_the_code(self):
        """Rejecting after redeeming would defeat the point."""
        self.run_login(lambda p: 'code=attacker-code&state=not-our-state')

        self.assertEqual([], self.server.token_calls(),
                         'a rejected callback must not reach the token endpoint')

    def test_missing_state_is_rejected(self):
        """An omitted state is not "no opinion" -- it is a failed check."""
        token, error = self.run_login(lambda p: 'code=the-code')

        self.assertIsNone(token)
        self.assertEqual(Category.CALLBACK_FAILED, error.category)
        self.assertIn('state mismatch', error.message)

    def test_empty_state_is_rejected(self):
        token, error = self.run_login(lambda p: 'code=the-code&state=')

        self.assertIsNone(token)
        self.assertEqual(Category.CALLBACK_FAILED, error.category)

    def test_state_is_compared_exactly(self):
        """No trimming, no case folding, no prefix matching, no truncation."""
        from urllib.parse import quote

        mutations = {
            'trailing space': lambda s: s + ' ',
            'truncated': lambda s: s[:-1],
            'extended': lambda s: s + 'x',
            'case flipped': lambda s: s.swapcase(),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                token, error = self.run_login(
                    lambda p: 'code=the-code&state=' + quote(mutate(p['state']), safe=''))
                self.assertIsNone(token, name)
                self.assertEqual(Category.CALLBACK_FAILED, error.category)

    def test_missing_code_is_rejected_even_with_a_valid_state(self):
        token, error = self.run_login(lambda p: 'state=' + p['state'])

        self.assertIsNone(token)
        self.assertIn('no code', error.message)


class DuplicateStateParameterTest(AuthorizationFlowTestBase):
    """Parameter pollution: `?state=ours&state=theirs`.

    Both SDKs let the **last** occurrence win. That choice is pinned here because the
    danger is divergence: if one side took the first and another took the last, an
    attacker could make the checking side and the redeeming side disagree.
    """

    def test_last_state_wins_and_a_polluted_callback_is_rejected(self):
        token, error = self.run_login(
            lambda p: 'code=the-code&state=' + p['state'] + '&state=attacker')

        self.assertIsNone(token, 'the trailing state must be the one checked')
        self.assertEqual(Category.CALLBACK_FAILED, error.category)

    def test_trailing_valid_state_is_accepted(self):
        """The mirror image, proving the rule is "last wins" rather than "any match"."""
        token, error = self.run_login(
            lambda p: 'code=the-code&state=attacker&state=' + p['state'])

        self.assertIsNone(error)
        self.assertEqual('AT1', token.access_token)

    def test_duplicate_code_also_takes_the_last(self):
        token, error = self.run_login(
            lambda p: 'code=first&code=second&state=' + p['state'])

        self.assertIsNone(error)
        _, form = self.server.token_calls()[0]
        self.assertEqual('second', form['code'])


class StateGenerationTest(AuthorizationFlowTestBase):
    """A-09: a reused state would let an old callback be replayed into a new flow."""

    def test_each_authorization_uses_a_fresh_state(self):
        states = []

        def capture(params):
            states.append(params['state'])
            return 'code=the-code&state=' + params['state']

        for _ in range(3):
            self.run_login(capture)

        self.assertEqual(3, len(set(states)), 'state must not repeat across authorizations')

    def test_verifier_is_also_fresh_and_never_leaves_the_process(self):
        """The verifier is sent only to the token endpoint, never in the browser URL."""
        challenges = []

        def capture(params):
            challenges.append(params['code_challenge'])
            self.assertNotIn('code_verifier', params,
                             'the verifier must never appear in the authorization URL')
            return 'code=the-code&state=' + params['state']

        for _ in range(3):
            self.run_login(capture)

        self.assertEqual(3, len(set(challenges)))

    def test_authorization_request_shape(self):
        """A-01: what the browser is sent."""
        self.run_login(lambda p: 'code=the-code&state=' + p['state'])

        params = self.seen_params
        self.assertEqual('code', params['response_type'])
        self.assertEqual('cid', params['client_id'])
        self.assertEqual('S256', params['code_challenge_method'])
        self.assertTrue(params['redirect_uri'].startswith('http://127.0.0.1:'))
        self.assertEqual('api.quote:read api.trade:read', params['scope'])


class CallbackErrorTest(AuthorizationFlowTestBase):
    """A-04: the user denying is a normal outcome."""

    def test_error_callback_is_reported_and_no_code_is_redeemed(self):
        token, error = self.run_login(
            lambda p: 'error=access_denied&error_description=user+said+no&state=' + p['state'])

        self.assertIsNone(token)
        self.assertEqual(Category.CALLBACK_FAILED, error.category)
        self.assertIn('access_denied', error.message)
        self.assertEqual([], self.server.token_calls())

    def test_error_is_checked_before_state(self):
        """A denial with a mismatched state should still read as a denial."""
        _, error = self.run_login(lambda p: 'error=access_denied&state=whatever')

        self.assertIn('access_denied', error.message)


class CodeRedemptionTest(AuthorizationFlowTestBase):
    """A-11: what the token request carries."""

    def test_authorization_code_grant_shape(self):
        self.run_login(lambda p: 'code=the-code&state=' + p['state'])

        _, form = self.server.token_calls()[0]
        self.assertEqual('authorization_code', form['grant_type'])
        self.assertEqual('the-code', form['code'])
        self.assertEqual('cid', form['client_id'])
        self.assertIn('code_verifier', form)
        self.assertEqual(self.seen_params['redirect_uri'], form['redirect_uri'])

    def test_verifier_matches_the_challenge_that_was_sent(self):
        """S256(verifier) must equal the challenge in the authorization URL."""
        import base64
        import hashlib

        self.run_login(lambda p: 'code=the-code&state=' + p['state'])

        _, form = self.server.token_calls()[0]
        digest = hashlib.sha256(form['code_verifier'].encode()).digest()
        expected = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
        self.assertEqual(self.seen_params['code_challenge'], expected)


if __name__ == '__main__':
    unittest.main()
