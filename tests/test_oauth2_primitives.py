# -*- coding: utf-8 -*-
"""OAuth2 primitives: PKCE, scope normalisation, filename sanitising, proto contract.

Covers test-plan cases A-07, A-19, E-12, I-08, I-09, L-06, L-07.
All pure functions or serialisation — no I/O, no network.
"""
import unittest

from tigeropen.auth.authentication import (
    AuthenticationAttempt,
    AuthenticationType,
    RequestAuthContext,
    RetryDecision,
)
from tigeropen.auth.oauth2.session_manager import (
    DEFAULT_MANUAL_CALLBACK_PORT,
    _normalize_scopes,
    _random_url_safe,
    _s256,
    _scopes_cover,
    _trim_trailing_slash,
)
from tigeropen.auth.oauth2.token_store import _safe_file_name, hash_issuer


class PkceTest(unittest.TestCase):
    """A-07: the verifier/challenge pair must match RFC 7636 Appendix B."""

    def test_rfc7636_appendix_b_vector(self):
        verifier = 'dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk'
        self.assertEqual('E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM', _s256(verifier))

    def test_verifier_length_within_rfc_range(self):
        # 64 raw bytes -> 86 base64url chars, inside RFC 7636's 43..128
        verifier = _random_url_safe(64)
        self.assertEqual(86, len(verifier))
        self.assertTrue(43 <= len(verifier) <= 128)

    def test_state_length(self):
        self.assertEqual(32, len(_random_url_safe(24)))

    def test_no_base64_padding(self):
        """Padding would have to be percent-encoded in a query string."""
        for size in (16, 24, 32, 64):
            self.assertNotIn('=', _random_url_safe(size))

    def test_values_are_random(self):
        self.assertNotEqual(_random_url_safe(24), _random_url_safe(24))


class ScopeTest(unittest.TestCase):
    """A-19, E-12: normalisation is dedupe + sort, so order never matters."""

    def test_dedupe_and_sort(self):
        self.assertEqual('a b', _normalize_scopes('  b   a  b '))

    def test_order_independent(self):
        self.assertEqual(
            _normalize_scopes('api.trade:write api.quote:read'),
            _normalize_scopes('api.quote:read api.trade:write'))

    def test_blank_returns_none(self):
        for raw in (None, '', '   ', '\t\n'):
            self.assertIsNone(_normalize_scopes(raw))

    def test_cover(self):
        self.assertTrue(_scopes_cover('a b c', 'a c'))
        self.assertTrue(_scopes_cover('a b', 'a b'))
        self.assertFalse(_scopes_cover('a b', 'a c'))

    def test_cover_is_false_on_empty(self):
        """Empty must never be treated as "covers everything"."""
        self.assertFalse(_scopes_cover('', 'a'))
        self.assertFalse(_scopes_cover(None, 'a'))
        self.assertFalse(_scopes_cover('a', ''))


class IssuerTest(unittest.TestCase):
    """I-09: the hash must match the Java SDK so both can share one directory."""

    def test_hash_is_32_hex_chars(self):
        h = hash_issuer('https://example.com')
        self.assertEqual(32, len(h))
        int(h, 16)  # raises if not hex

    def test_hash_is_stable(self):
        self.assertEqual(hash_issuer('https://a.com'), hash_issuer('https://a.com'))

    def test_hash_differs_per_issuer(self):
        self.assertNotEqual(hash_issuer('https://a.com'), hash_issuer('https://b.com'))

    def test_known_vector(self):
        """Locked down so a change here is visible: it would orphan every stored
        registration and silently force re-registration on every machine."""
        import hashlib
        issuer = 'https://openapi-oauth2-test.qa.tigerbrokers.net'
        expected = hashlib.sha256(issuer.encode('utf-8')).hexdigest()[:32]
        self.assertEqual(expected, hash_issuer(issuer))

    def test_trailing_slash_trimmed(self):
        self.assertEqual('https://a.com', _trim_trailing_slash('https://a.com/'))
        self.assertEqual('https://a.com', _trim_trailing_slash('https://a.com'))


class SafeFileNameTest(unittest.TestCase):
    """I-08: client_id comes from the server and is used as a filename."""

    def test_path_traversal_is_neutralised(self):
        name = _safe_file_name('../../etc/passwd')
        self.assertNotIn('/', name)
        self.assertNotIn('..', name)

    def test_separators_replaced(self):
        self.assertNotIn('/', _safe_file_name('a/b'))
        self.assertNotIn('\\', _safe_file_name('a\\b'))

    def test_ordinary_client_id_untouched(self):
        self.assertEqual('dbd5dccf3a35418aa6eb9aa12545f214',
                         _safe_file_name('dbd5dccf3a35418aa6eb9aa12545f214'))

    def test_allowed_characters_kept(self):
        self.assertEqual('a-b_c.d', _safe_file_name('a-b_c.d'))

    def test_empty_never_yields_empty_filename(self):
        self.assertTrue(_safe_file_name(''))
        self.assertTrue(_safe_file_name(None))


class ValueTypeTest(unittest.TestCase):
    """K-02: no value type may leak a credential through its repr."""

    def test_attempt_repr_masks_credential(self):
        attempt = AuthenticationAttempt(AuthenticationType.OAUTH2, 'super-secret-token')
        text = repr(attempt)
        self.assertNotIn('super-secret-token', text)
        self.assertIn('***', text)

    def test_attempt_repr_marks_absent_credential(self):
        self.assertIn('<none>', repr(AuthenticationAttempt(AuthenticationType.OAUTH2, None)))

    def test_retry_decision_repr_hides_header(self):
        decision = RetryDecision.retry('Bearer super-secret-token')
        self.assertNotIn('super-secret-token', repr(decision))

    def test_no_retry_is_a_singleton_and_carries_no_header(self):
        self.assertIs(RetryDecision.no_retry(), RetryDecision.no_retry())
        self.assertFalse(RetryDecision.no_retry().should_retry)
        self.assertIsNone(RetryDecision.no_retry().authorization_header)

    def test_retry_carries_the_full_header(self):
        decision = RetryDecision.retry('Bearer abc')
        self.assertTrue(decision.should_retry)
        self.assertEqual('Bearer abc', decision.authorization_header)

    def test_request_context_defaults_to_retryable(self):
        """Inverted semantics: the default must be "may retry"."""
        self.assertTrue(RequestAuthContext({}).retryable)
        self.assertFalse(RequestAuthContext({}, retryable=False).retryable)

    def test_request_context_header_roundtrip(self):
        ctx = RequestAuthContext({'a': 1})
        self.assertIsNone(ctx.authorization_header)
        ctx.authorization_header = 'Bearer x'
        self.assertEqual('Bearer x', ctx.authorization_header)
        self.assertEqual({'a': 1}, ctx.params)


class CallbackPortTest(unittest.TestCase):
    """§5.2: the port rule must stay identical to the Java SDK."""

    def _port(self, **kwargs):
        from tigeropen.auth.oauth2 import OAuth2SessionManager
        return OAuth2SessionManager(issuer='https://x', **kwargs)._effective_callback_port()

    def test_dynamic_registration_uses_system_assigned_port(self):
        self.assertEqual(0, self._port())

    def test_manual_client_id_uses_agreed_port(self):
        self.assertEqual(DEFAULT_MANUAL_CALLBACK_PORT, self._port(client_id='cid'))
        self.assertEqual(18888, DEFAULT_MANUAL_CALLBACK_PORT)

    def test_explicit_port_wins(self):
        self.assertEqual(9000, self._port(callback_port=9000))
        self.assertEqual(9000, self._port(client_id='cid', callback_port=9000))


class ProtoContractTest(unittest.TestCase):
    """L-06, L-07: the socket wire contract shared with the server and the Java SDK."""

    def setUp(self):
        from tigeropen.push.pb.util import ProtoMessageUtil
        self.util = ProtoMessageUtil
        ProtoMessageUtil.increment_count = 0

    def _connect(self, **kwargs):
        from tigeropen.push.pb.util import ProtoMessageUtil
        ProtoMessageUtil.increment_count = 0
        return ProtoMessageUtil.build_connect_message(
            'tiger-1', 'sig-1', send_interval=10, receive_interval=20,
            use_full_tick=True, **kwargs)

    def test_access_token_none_is_byte_identical_to_omitting_it(self):
        """L-06: signature mode must serialise exactly as before the OAuth2 change."""
        without = self._connect()
        with_none = self._connect(access_token=None)
        self.assertEqual(without.SerializeToString(), with_none.SerializeToString())

    def test_access_token_field_not_set_in_signature_mode(self):
        self.assertFalse(self._connect().connect.HasField('accessToken'))

    def test_access_token_set_in_oauth2_mode(self):
        message = self._connect(access_token='tok-abc')
        self.assertTrue(message.connect.HasField('accessToken'))
        self.assertEqual('tok-abc', message.connect.accessToken)

    def test_field_numbers_are_the_contract(self):
        """L-07: these numbers are agreed with the server and the Java SDK."""
        from tigeropen.push.pb import Request_pb2, SocketCommon_pb2
        self.assertEqual(10, Request_pb2.Request.Connect.ACCESSTOKEN_FIELD_NUMBER)
        self.assertEqual(5, Request_pb2.Request.REFRESHTOKEN_FIELD_NUMBER)
        self.assertEqual(10, SocketCommon_pb2.SocketCommon.REFRESH_TOKEN)

    def test_reserved_field_numbers_are_not_reused(self):
        fields = {f.number for f in
                  __import__('tigeropen.push.pb.Request_pb2', fromlist=['x'])
                  .Request.Connect.DESCRIPTOR.fields}
        self.assertNotIn(8, fields)
        self.assertNotIn(9, fields)

    def test_refresh_token_message(self):
        from tigeropen.push.pb import SocketCommon_pb2
        message = self.util.build_refresh_token_message('tok-new')
        self.assertEqual(SocketCommon_pb2.SocketCommon.REFRESH_TOKEN, message.command)
        self.assertEqual('tok-new', message.refreshToken.accessToken)

    def test_refresh_token_command_dispatches_to_on_refresh_token(self):
        """A listener without the method is fine, but the name must be right."""
        from tigeropen.push.network.utils import get_command_name
        from tigeropen.push.pb import SocketCommon_pb2
        self.assertEqual('refresh_token',
                         get_command_name(SocketCommon_pb2.SocketCommon.REFRESH_TOKEN))


if __name__ == '__main__':
    unittest.main()
