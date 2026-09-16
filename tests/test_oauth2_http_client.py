# -*- coding: utf-8 -*-
"""OAuth2 data plane: how a business request carries the credential.

Covers test-plan cases E-04, G-02..G-06, H-02..H-09, K-01, K-02, L-01, L-02, L-09.

The most important cases here are the *regression* ones: signature mode must be
byte-for-byte unchanged by the OAuth2 work.
"""
import logging
import threading
import unittest

from tests.oauth2_fakes import FakeGateway, StubSessions
from tests.support import offline_client_config
from tigeropen.auth.authentication import (
    Authentication,
    AuthenticationAttempt,
    AuthenticationType,
    RequestAuthContext,
    RetryDecision,
)
from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2Token
from tigeropen.common.consts.service_types import ACCOUNTS, CANCEL_ORDER, MODIFY_ORDER, PLACE_ORDER
from tigeropen.common.exceptions import ResponseException
from tigeropen.common.request import OpenApiRequest
from tigeropen.common.util.web_utils import _safe_headers
from tigeropen.tiger_open_client import TigerOpenClient


class ClientTestBase(unittest.TestCase):
    def setUp(self):
        self.gateway = FakeGateway()
        self.logger = logging.getLogger('tigeropen-oauth2-test')
        self.logger.addHandler(logging.NullHandler())

    def tearDown(self):
        self.gateway.stop()

    def oauth2_client(self, sessions=None, **kwargs):
        config = offline_client_config()
        config.authentication = OAuth2Authentication(sessions or StubSessions())
        config.server_url = self.gateway.url
        for k, v in kwargs.items():
            setattr(config, k, v)
        return TigerOpenClient(config, logger=self.logger)

    def signature_client(self):
        config = offline_client_config()
        config.server_url = self.gateway.url
        return TigerOpenClient(config, logger=self.logger)

    def call(self, client, method=ACCOUNTS):
        return client.execute(OpenApiRequest(method=method, biz_model=None), url=self.gateway.url)


class RequestShapeTest(ClientTestBase):
    """G-02, H-02: the gateway branches on the presence of `sign`."""

    def test_oauth2_body_has_no_signature_fields(self):
        self.call(self.oauth2_client())
        _, body = self.gateway.requests[0]
        for forbidden in ('sign', 'tiger_id', 'sign_type'):
            self.assertNotIn(forbidden, body,
                             '%s in an OAuth2 body makes the gateway ignore the Bearer token'
                             % forbidden)

    def test_oauth2_body_keeps_the_business_fields(self):
        self.call(self.oauth2_client())
        _, body = self.gateway.requests[0]
        self.assertEqual({'method', 'version', 'timestamp', 'charset', 'device_id'}, set(body))

    def test_device_id_is_sent_in_oauth2_mode(self):
        """§9.5: it is a business parameter and drives market-data seat arbitration."""
        self.call(self.oauth2_client())
        _, body = self.gateway.requests[0]
        self.assertTrue(body.get('device_id'))

    def test_bearer_prefix(self):
        """G-03: unlike the HK license token, this one carries a scheme."""
        self.call(self.oauth2_client())
        self.assertEqual('Bearer tok-1', self.gateway.auth_headers()[0])

    def test_signature_body_still_has_the_signature_fields(self):
        """L-01: the regression side of the same coin."""
        self.call(self.signature_client())
        _, body = self.gateway.requests[0]
        for required in ('sign', 'tiger_id', 'sign_type'):
            self.assertIn(required, body)

    def test_signature_body_field_order_is_unchanged(self):
        """L-02: the body is serialised in insertion order, so order is part of the
        wire format. This is the guard against silently changing existing users'
        requests."""
        self.call(self.signature_client())
        _, body = self.gateway.requests[0]
        self.assertEqual(
            ['method', 'version', 'timestamp', 'tiger_id', 'charset', 'sign_type',
             'device_id', 'sign'],
            list(body))


class UnauthorizedRetryTest(ClientTestBase):
    """G-04..G-06, H-09: at most one retry, never for order operations."""

    def test_401_refreshes_and_retries_once(self):
        sessions = StubSessions()
        self.gateway.responses.append((401, {'code': 401}))
        client = self.oauth2_client(sessions)

        self.call(client)

        self.assertEqual(['Bearer tok-1', 'Bearer tok-refreshed'], self.gateway.auth_headers())
        self.assertEqual(1, sessions.refreshes)

    def test_place_order_is_never_retried(self):
        """A 401 does not prove the order was not placed."""
        self.gateway.responses.append((401, {'code': 401}))
        client = self.oauth2_client()

        with self.assertRaises(ResponseException) as ctx:
            self.call(client, PLACE_ORDER)
        self.assertEqual(401, ctx.exception.status)
        self.assertEqual(1, len(self.gateway.requests), 'the order must be sent exactly once')

    def test_cancel_order_is_never_retried(self):
        self.gateway.responses.append((401, {'code': 401}))
        with self.assertRaises(ResponseException):
            self.call(self.oauth2_client(), CANCEL_ORDER)
        self.assertEqual(1, len(self.gateway.requests))

    def test_modify_order_is_never_retried(self):
        self.gateway.responses.append((401, {'code': 401}))
        with self.assertRaises(ResponseException):
            self.call(self.oauth2_client(), MODIFY_ORDER)
        self.assertEqual(1, len(self.gateway.requests))

    def test_403_does_not_trigger_a_refresh(self):
        """E-04: a refresh returns the same scope, so the retry is guaranteed to fail."""
        sessions = StubSessions()
        self.gateway.responses.append((403, {'code': 403}))
        client = self.oauth2_client(sessions, retry_max_tries=0)

        with self.assertRaises(ResponseException):
            self.call(client)
        self.assertEqual(0, sessions.refreshes)

    def test_retry_stops_after_one_attempt(self):
        """Two consecutive 401s must not loop."""
        sessions = StubSessions()
        self.gateway.responses.extend([(401, {'code': 401}), (401, {'code': 401})])
        client = self.oauth2_client(sessions)

        with self.assertRaises(ResponseException):
            self.call(client)
        self.assertEqual(2, len(self.gateway.requests))
        self.assertEqual(1, sessions.refreshes)

    def test_unchanged_token_after_refresh_means_no_retry(self):
        """C-03: retrying with the same credential just collects the same 401."""

        class StuckSessions(StubSessions):
            def refresh_after_unauthorized(self, failed):
                self.refreshes += 1
                return OAuth2Token(access_token=self.token)   # unchanged

        sessions = StuckSessions()
        self.gateway.responses.append((401, {'code': 401}))
        with self.assertRaises(ResponseException):
            self.call(self.oauth2_client(sessions))
        self.assertEqual(1, len(self.gateway.requests))


class StatusPropagationTest(ClientTestBase):
    """H-03, L-09: the 401 branch needs a status code to key off."""

    def test_status_is_attached(self):
        # retries off, so the single queued 500 is what the caller sees
        self.gateway.responses.append((500, {'code': 500}))
        with self.assertRaises(ResponseException) as ctx:
            self.call(self.oauth2_client(retry_max_tries=0), ACCOUNTS)
        self.assertEqual(500, ctx.exception.status)

    def test_5xx_is_retried_unlike_401(self):
        """A server error is transient; only 401 short-circuits the retry."""
        self.gateway.responses.append((500, {'code': 500}))
        self.call(self.oauth2_client())          # second attempt succeeds
        self.assertEqual(2, len(self.gateway.requests))

    def test_positional_construction_still_works(self):
        """L-09: existing callers pass only a message."""
        error = ResponseException('boom')
        self.assertIsNone(error.status)
        self.assertIn('boom', str(error))


class CredentialMaskingTest(ClientTestBase):
    """K-01, K-02, H-06, H-07."""

    def test_bearer_is_masked_in_exception_messages(self):
        self.gateway.responses.append((500, {'code': 500}))
        with self.assertRaises(ResponseException) as ctx:
            self.call(self.oauth2_client(retry_max_tries=0))
        message = str(ctx.exception)
        self.assertNotIn('tok-1', message)
        self.assertIn('Bearer ***', message)

    def test_license_token_is_not_masked(self):
        """H-07: signature users' logs must stay byte-identical, so the same dict
        object is returned untouched."""
        headers = {'Authorization': 'eyJhbGciOi.license.token', 'X': '1'}
        self.assertIs(headers, _safe_headers(headers))

    def test_masking_is_case_insensitive_about_the_scheme(self):
        """RFC 6750 makes the Authorization scheme case-insensitive.

        A custom Authentication implementation sending a lowercase scheme would otherwise put
        the token straight into exception messages, which is the one thing this function is
        for.
        """
        for header in ('bearer secret', 'BEARER secret', 'BeArEr secret'):
            masked = _safe_headers({'Authorization': header})
            self.assertEqual('Bearer ***', masked['Authorization'], header)

    def test_masking_does_not_mutate_the_caller_dict(self):
        headers = {'Authorization': 'Bearer secret'}
        masked = _safe_headers(headers)
        self.assertEqual('Bearer secret', headers['Authorization'])
        self.assertEqual('Bearer ***', masked['Authorization'])

    def test_missing_or_empty_headers(self):
        self.assertIsNone(_safe_headers(None))
        self.assertEqual({}, _safe_headers({}))


class HeaderIsolationTest(ClientTestBase):
    """H-08: Authorization is request-scoped."""

    def test_concurrent_requests_do_not_share_a_header(self):
        class RotatingSessions(StubSessions):
            def __init__(self):
                super().__init__()
                self.counter = 0
                self.lock = threading.Lock()

            def get_access_token(self):
                with self.lock:
                    self.counter += 1
                    return 'tok-%d' % self.counter

        client = self.oauth2_client(RotatingSessions())
        threads = [threading.Thread(target=self.call, args=(client,)) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        headers = self.gateway.auth_headers()
        self.assertEqual(10, len(headers))
        self.assertEqual(10, len(set(headers)), 'each request must carry its own token')


class AuthenticationContractTest(unittest.TestCase):
    """A third-party Authentication implementation must be usable."""

    def test_custom_implementation_is_accepted(self):
        class Custom(Authentication):
            @property
            def auth_type(self):
                return AuthenticationType.OAUTH2

            def apply(self, context):
                context.authorization_header = 'Bearer custom'
                return AuthenticationAttempt(AuthenticationType.OAUTH2, 'custom')

            def on_unauthorized(self, attempt, status_code):
                return RetryDecision.no_retry()

            def close(self):
                pass

        config = offline_client_config()
        config.authentication = Custom()
        # Must not raise about a missing private key / tiger id
        TigerOpenClient(config, logger=logging.getLogger('x'))

    def test_incomplete_implementation_is_rejected(self):
        with self.assertRaises(TypeError):
            class Incomplete(Authentication):
                @property
                def auth_type(self):
                    return AuthenticationType.OAUTH2

            Incomplete()

    def test_oauth2_authentication_requires_a_session(self):
        with self.assertRaises(ValueError):
            OAuth2Authentication(None)

    def test_on_unauthorized_ignores_non_401(self):
        auth = OAuth2Authentication(StubSessions())
        attempt = AuthenticationAttempt(AuthenticationType.OAUTH2, 'tok-1')
        for status in (200, 403, 500, 503):
            self.assertFalse(auth.on_unauthorized(attempt, status).should_retry, status)

    def test_apply_sets_the_bearer_header(self):
        auth = OAuth2Authentication(StubSessions())
        ctx = RequestAuthContext({})
        attempt = auth.apply(ctx)
        self.assertEqual('Bearer tok-1', ctx.authorization_header)
        self.assertEqual('tok-1', attempt.credential)


if __name__ == '__main__':
    unittest.main()
