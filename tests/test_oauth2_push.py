# -*- coding: utf-8 -*-
"""Socket push: connect credential and in-place token rotation.

Covers test-plan cases C-13..C-16, H-10..H-13, H-17.

No socket is opened: the connection is replaced by a recorder, so the assertions are
about which frames the client decides to send.
"""
import threading
import time
import unittest
import unittest.mock as mock

from tests.support import offline_client_config
from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2Token
from tigeropen.auth.oauth2.token import current_millis
from tigeropen.push.network.exception import ConnectFailedException
from tigeropen.auth.oauth2.session_manager import DEFAULT_REFRESH_AHEAD_MILLIS
from tigeropen.push.protobuf_push_client import (
    TOKEN_REFRESH_REPLY_TIMEOUT_MILLIS,
    ProtobufPushClient,
    _REFRESH_IN_PROGRESS,
)
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
from tigeropen.push.push_client import PushClient


class RecordingConnection:
    """Stands in for PushConnection; records the frames the client sends."""

    def __init__(self, *args, **kwargs):
        self.frames = []
        self.connect_requests = []
        self.transport = mock.Mock()

    def set_listener(self, *args):
        pass

    def remove_listener(self, *args):
        pass

    def set_ssl(self, *args):
        pass

    def connect(self, request, wait=True):
        self.connect_requests.append(request)

    def send_frame(self, frame):
        self.frames.append(frame)

    def disconnect(self):
        pass


class Frame:
    def __init__(self, code, msg=''):
        self.code = code
        self.msg = msg


class SessionsStub:
    """Minimal OAuth2SessionManager stand-in for the push client."""

    def __init__(self, token='AT-1', remaining_millis=3600_000):
        self.token = token
        self.remaining_millis = remaining_millis
        self.exchanges = 0
        self.exchange_started = threading.Event()
        self.release = None          # set to an Event to hold the exchange open

    def status(self):
        return OAuth2Token(access_token=self.token,
                           expires_at=current_millis() + self.remaining_millis)

    def should_refresh_soon(self):
        # The push client asks rather than keeping a refresh window of its own.
        return self.status().needs_refresh(DEFAULT_REFRESH_AHEAD_MILLIS)

    def get_access_token(self):
        self.exchanges += 1
        self.exchange_started.set()
        if self.release is not None:
            self.release.wait(5)
        return self.token


def wait_until(predicate, timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return predicate()


class PushTestBase(unittest.TestCase):
    def setUp(self):
        self.sessions = SessionsStub()
        self.connection = RecordingConnection()

    def client(self, oauth2=True):
        config = offline_client_config()
        if oauth2:
            config.authentication = OAuth2Authentication(self.sessions)
        client = ProtobufPushClient('127.0.0.1', 1, use_ssl=False, client_config=config)
        client._connection = self.connection
        return client

    def refresh_frames(self):
        return [f for f in self.connection.frames
                if f.command == SocketCommon.REFRESH_TOKEN]


class ConnectTest(PushTestBase):
    """H-12, H-13: what the connect message carries."""

    def _connect(self, client, **kwargs):
        with mock.patch('tigeropen.push.protobuf_push_client.PushConnection',
                        return_value=self.connection):
            client.connect(**kwargs)
        return self.connection.connect_requests[-1].connect

    def test_oauth2_connect_carries_the_bearer_token_only(self):
        connect = self._connect(self.client())
        self.assertEqual('AT-1', connect.accessToken)
        self.assertEqual('', connect.tigerId)
        self.assertEqual('', connect.sign)

    def test_tiger_id_and_private_key_are_ignored_in_oauth2_mode(self):
        """They play no part; passing them must not change the frame or raise."""
        connect = self._connect(self.client(), tiger_id='123456', private_key='not-a-key')
        self.assertEqual('', connect.tigerId)
        self.assertEqual('', connect.sign)

    def test_no_token_fails_with_a_clear_message(self):
        """H-13: connecting anyway would be rejected, and by then the real reason
        (never authorized / refresh failed) is lost."""
        self.sessions.token = ''
        with mock.patch('tigeropen.push.protobuf_push_client.PushConnection',
                        return_value=self.connection):
            with self.assertRaises(ConnectFailedException) as ctx:
                self.client().connect()
        self.assertIn('no oauth2 access token', str(ctx.exception))
        self.assertEqual([], self.connection.connect_requests)

    def test_reconnect_clears_any_pending_rotation(self):
        """C-16: the pinned token is per-connection, so a reconnect starts clean."""
        client = self.client()
        client._refresh_pending = 'stale'
        client._refresh_sent_at = 1
        self._connect(client)
        self.assertIsNone(client._refresh_pending)
        self.assertEqual('AT-1', client._access_token)

    def test_signature_connect_is_unchanged(self):
        """H-11 regression: no accessToken field, tigerId and sign as before."""
        client = self.client(oauth2=False)
        with mock.patch('tigeropen.push.protobuf_push_client.PushConnection',
                        return_value=self.connection), \
                mock.patch('tigeropen.push.protobuf_push_client.sign_with_rsa',
                           return_value='SIGNATURE'):
            client.connect(tiger_id='123456', private_key='key')
        connect = self.connection.connect_requests[-1].connect
        self.assertEqual('123456', connect.tigerId)
        self.assertEqual('SIGNATURE', connect.sign)
        self.assertEqual('', connect.accessToken, 'unset proto3 field reads as empty')


class ProtocolChoiceTest(unittest.TestCase):
    """H-10, H-11: STOMP has nowhere to carry a token and no REFRESH_TOKEN."""

    def test_oauth2_over_stomp_is_rejected_at_construction(self):
        config = offline_client_config()
        config.authentication = OAuth2Authentication(SessionsStub())
        with self.assertRaises(ValueError) as ctx:
            PushClient('127.0.0.1', 1, use_protobuf=False, client_config=config)
        self.assertIn('protobuf', str(ctx.exception))

    def test_oauth2_over_protobuf_is_accepted(self):
        config = offline_client_config()
        config.authentication = OAuth2Authentication(SessionsStub())
        self.assertIsInstance(
            PushClient('127.0.0.1', 1, client_config=config).client, ProtobufPushClient)

    def test_signature_over_stomp_still_works(self):
        """L-regression: the existing STOMP path must stay available."""
        from tigeropen.push.stomp_push_client import StompPushClient
        client = PushClient('127.0.0.1', 1, use_protobuf=False,
                            client_config=offline_client_config())
        self.assertIsInstance(client.client, StompPushClient)


class RotationTriggerTest(PushTestBase):
    """C-13: the heartbeat is what drives rotation."""

    def test_fresh_token_sends_nothing(self):
        client = self.client()
        client._access_token = 'AT-1'
        client.on_heartbeat(Frame(0))
        self.assertEqual([], self.refresh_frames())
        self.assertEqual(0, self.sessions.exchanges)

    def test_token_advanced_elsewhere_is_pushed_to_the_connection(self):
        """A token advanced elsewhere must reach this connection, even though the session's
        own token now looks fresh.

        The server validates the token pinned on this connection, so a session advanced by
        anything else leaves this connection on a token that is about to be rejected.
        """
        client = self.client()
        # This connection still presents the token it connected with.
        client._access_token = 'AT-pinned-at-connect'
        # The session's token is nowhere near expiry, as after an HTTP request refreshed it.
        self.sessions.remaining_millis = 3600_000
        self.sessions.token = 'AT-refreshed-by-http'

        client.on_heartbeat(Frame(0))

        self.assertTrue(wait_until(lambda: self.refresh_frames()),
                        'the connection must be told about the token the session already holds')
        self.assertEqual('AT-refreshed-by-http',
                         self.refresh_frames()[0].refreshToken.accessToken)

    def test_connection_without_a_pinned_token_falls_back_to_the_refresh_window(self):
        """A connection that never pinned a token falls back to the session's refresh window
        instead of rotating on every heartbeat."""
        client = self.client()
        client._access_token = None
        self.sessions.remaining_millis = 3600_000

        client.on_heartbeat(Frame(0))

        self.assertEqual([], self.refresh_frames())
        self.assertEqual(0, self.sessions.exchanges)

    def test_expiring_token_is_rotated_in_place(self):
        client = self.client()
        client._access_token = 'AT-1'
        self.sessions.remaining_millis = DEFAULT_REFRESH_AHEAD_MILLIS - 1_000
        self.sessions.token = 'AT-2'

        client.on_heartbeat(Frame(0))

        self.assertTrue(wait_until(lambda: self.refresh_frames()))
        self.assertEqual('AT-2', self.refresh_frames()[0].refreshToken.accessToken)
        self.assertEqual(SocketCommon.REFRESH_TOKEN, self.refresh_frames()[0].command)

    def test_unchanged_token_is_not_sent(self):
        """The session manager hands back the current token until its own window opens."""
        client = self.client()
        client._access_token = 'AT-1'
        self.sessions.remaining_millis = DEFAULT_REFRESH_AHEAD_MILLIS - 1_000

        client.on_heartbeat(Frame(0))

        self.assertTrue(wait_until(lambda: self.sessions.exchanges == 1))
        self.assertTrue(wait_until(lambda: client._refresh_pending is None))
        self.assertEqual([], self.refresh_frames())

    def test_signature_mode_heartbeat_does_nothing(self):
        """H-17 regression."""
        client = self.client(oauth2=False)
        client.on_heartbeat(Frame(0))
        self.assertEqual([], self.connection.frames)

    def test_heartbeat_callback_still_fires(self):
        client = self.client()
        seen = []
        client.heartbeat_callback = seen.append
        client.on_heartbeat(Frame(0))
        self.assertEqual(1, len(seen))

    def test_failed_exchange_keeps_the_connection_and_clears_the_claim(self):
        """A failed refresh is no reason to drop a working connection."""
        client = self.client()
        client._access_token = 'AT-1'
        self.sessions.remaining_millis = DEFAULT_REFRESH_AHEAD_MILLIS - 1_000
        self.sessions.get_access_token = mock.Mock(side_effect=RuntimeError('network down'))

        client.on_heartbeat(Frame(0))

        self.assertTrue(wait_until(lambda: client._refresh_pending is None))
        self.assertEqual([], self.refresh_frames())
        self.assertEqual('AT-1', client._access_token, 'the pinned token is untouched')


class RotationConcurrencyTest(PushTestBase):
    """C-14, C-15: at most one rotation in flight, and it must not wedge."""

    def setUp(self):
        super().setUp()
        self.sessions.remaining_millis = DEFAULT_REFRESH_AHEAD_MILLIS - 1_000

    def test_second_heartbeat_does_not_start_a_second_exchange(self):
        """C-15: the marker is claimed before the exchange starts."""
        self.sessions.release = threading.Event()
        client = self.client()
        client._access_token = 'AT-1'
        self.sessions.token = 'AT-2'

        client.on_heartbeat(Frame(0))
        self.assertTrue(self.sessions.exchange_started.wait(5))
        self.assertEqual(_REFRESH_IN_PROGRESS, client._refresh_pending)

        client.on_heartbeat(Frame(0))          # while the first is still running
        self.sessions.release.set()

        self.assertTrue(wait_until(lambda: self.refresh_frames()))
        self.assertEqual(1, self.sessions.exchanges)
        self.assertEqual(1, len(self.refresh_frames()))

    def test_pending_reply_blocks_a_second_send_within_the_window(self):
        client = self.client()
        client._access_token = 'AT-1'
        client._refresh_pending = 'AT-2'
        client._refresh_sent_at = current_millis()

        client.on_heartbeat(Frame(0))

        self.assertEqual(0, self.sessions.exchanges)
        self.assertEqual([], self.refresh_frames())

    def test_no_reply_within_the_window_frees_the_next_attempt(self):
        """C-14: an older server ignores REFRESH_TOKEN and never replies; without the
        timeout no later rotation could ever happen."""
        client = self.client()
        client._access_token = 'AT-1'
        self.sessions.token = 'AT-2'
        client._refresh_pending = 'AT-old'
        client._refresh_sent_at = current_millis() - TOKEN_REFRESH_REPLY_TIMEOUT_MILLIS - 1

        client.on_heartbeat(Frame(0))

        self.assertTrue(wait_until(lambda: self.refresh_frames()))
        self.assertEqual('AT-2', self.refresh_frames()[0].refreshToken.accessToken)

    def test_rotation_is_abandoned_when_the_connection_was_replaced(self):
        """A rotation in flight must not be delivered to a connection that replaced the one
        it was claimed for: the replacement has its own token, which can be the newer of
        the two.
        """
        self.sessions.release = threading.Event()
        client = self.client()
        client._access_token = 'AT-old'
        self.sessions.token = 'AT-old'          # what the exchange will hand back

        client.on_heartbeat(Frame(0))
        self.assertTrue(self.sessions.exchange_started.wait(5))

        # Reconnect: a new connection, already holding a newer token.
        replacement = RecordingConnection()
        client._connection = replacement
        client._access_token = 'AT-new'
        client._refresh_pending = None
        client._refresh_sent_at = 0

        self.sessions.release.set()

        self.assertTrue(wait_until(lambda: self.sessions.exchanges == 1))
        # Allow time for a frame to arrive if one is going to.
        self.assertFalse(wait_until(lambda: replacement.frames, timeout=1),
                         'the stale rotation must not be sent to the new connection')
        self.assertEqual('AT-new', client._access_token,
                         'the new connection must keep its own token')
        self.assertIsNone(client._refresh_pending,
                          'the claim belongs to the new connection and must be left alone')

    def test_send_failure_clears_the_claim(self):
        client = self.client()
        client._access_token = 'AT-1'
        self.sessions.token = 'AT-2'
        self.connection.send_frame = mock.Mock(side_effect=RuntimeError('socket closed'))

        client.on_heartbeat(Frame(0))

        self.assertTrue(wait_until(lambda: client._refresh_pending is None))
        self.assertEqual('AT-1', client._access_token)


class RotationReplyTest(PushTestBase):
    """C-16: the pinned token follows the server, not our intent."""

    def test_success_pins_the_new_token(self):
        client = self.client()
        client._access_token = 'AT-1'
        client._refresh_pending = 'AT-2'
        client._refresh_sent_at = current_millis()

        client.on_refresh_token(Frame(0, 'ok'))

        self.assertEqual('AT-2', client._access_token)
        self.assertIsNone(client._refresh_pending)

    def test_rejection_keeps_the_previous_token(self):
        """The server leaves its own connection attributes untouched when it rejects."""
        client = self.client()
        client._access_token = 'AT-1'
        client._refresh_pending = 'AT-2'
        client._refresh_sent_at = current_millis()

        client.on_refresh_token(Frame(4001, 'invalid token'))

        self.assertEqual('AT-1', client._access_token)
        self.assertIsNone(client._refresh_pending, 'a rejection must still free the slot')

    def test_reply_while_the_placeholder_is_held_pins_nothing(self):
        """Such a reply cannot correspond to a message we sent."""
        client = self.client()
        client._access_token = 'AT-1'
        client._refresh_pending = _REFRESH_IN_PROGRESS
        client._refresh_sent_at = current_millis()

        client.on_refresh_token(Frame(0, 'ok'))

        self.assertEqual('AT-1', client._access_token)
        self.assertIsNone(client._refresh_pending)

    def test_unsolicited_reply_is_harmless(self):
        client = self.client()
        client._access_token = 'AT-1'
        client.on_refresh_token(Frame(0, 'ok'))
        self.assertEqual('AT-1', client._access_token)

    def test_rotation_completes_end_to_end(self):
        client = self.client()
        client._access_token = 'AT-1'
        self.sessions.remaining_millis = DEFAULT_REFRESH_AHEAD_MILLIS - 1_000
        self.sessions.token = 'AT-2'

        client.on_heartbeat(Frame(0))
        self.assertTrue(wait_until(lambda: self.refresh_frames()))
        client.on_refresh_token(Frame(0, 'ok'))

        self.assertEqual('AT-2', client._access_token)
        # A later heartbeat now finds the token unchanged and sends nothing more
        client.on_heartbeat(Frame(0))
        self.assertTrue(wait_until(lambda: client._refresh_pending is None))
        self.assertEqual(1, len(self.refresh_frames()))


if __name__ == '__main__':
    unittest.main()
