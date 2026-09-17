# -*- coding: utf-8 -*-
"""Fakes shared by the OAuth2 test modules.

Everything binds 127.0.0.1 so the conftest network guard is satisfied and no real
environment is needed.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from tigeropen.auth.oauth2 import OAuth2Token

# HTTPServer.shutdown() waits for one poll interval; the 0.5s default would cost
# half a second per test case.
POLL_INTERVAL = 0.01


class _ThreadedServer:
    def _start(self, handler):
        self._http = HTTPServer(('127.0.0.1', 0), handler)
        self.port = self._http.server_address[1]
        self.base_url = 'http://127.0.0.1:%d' % self.port
        self._thread = threading.Thread(
            target=self._http.serve_forever, kwargs={'poll_interval': POLL_INTERVAL}, daemon=True)
        self._thread.start()

    def stop(self):
        self._http.shutdown()
        self._http.server_close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stop()
        return False


class FakeAuthorizationServer(_ThreadedServer):
    """Discovery, registration, token, device authorization and revocation.

    Every call is recorded as ``(path, form)``. Responses can be queued to drive a
    specific branch; anything not queued falls back to a success.
    """

    def __init__(self):
        self.calls = []
        #: JSON request bodies keyed by path. Registration is posted as JSON, so it lands in
        #: :attr:`calls` with an empty form and cannot be asserted on from there.
        self.json_bodies = {}
        self.token_responses = []
        self.device_responses = []
        self.revoke_status = 200
        self.advertise_revocation = True
        self.advertise_device = True
        self.serial = 0
        self.lock = threading.Lock()
        #: Set by :meth:`hold_token_endpoint` to stall a token request in flight.
        self._token_gate = None
        self.token_request_arrived = threading.Event()
        server = self

        class Handler(BaseHTTPRequestHandler):
            def _send(self, code, payload=None):
                body = b'' if payload is None else json.dumps(payload).encode()
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                base = server.base_url
                meta = {
                    'issuer': base,
                    'authorization_endpoint': base + '/authorize',
                    'token_endpoint': base + '/token',
                    'registration_endpoint': base + '/register',
                    'scopes_supported': ['api.quote:read', 'api.trade:read'],
                }
                if server.advertise_device:
                    meta['device_authorization_endpoint'] = base + '/device'
                if server.advertise_revocation:
                    meta['revocation_endpoint'] = base + '/revoke'
                self._send(200, meta)

            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get('Content-Length') or 0)).decode()
                form = {k: v[0] for k, v in parse_qs(raw).items()} if raw else {}
                with server.lock:
                    server.calls.append((self.path, form))
                if self.path == '/revoke':
                    return self._send(server.revoke_status)
                if self.path == '/register':
                    with server.lock:
                        server.json_bodies[self.path] = json.loads(raw)
                    return self._send(200, {'client_id': 'dyn-client',
                                            'scope': 'api.quote:read api.trade:read'})
                if self.path == '/device':
                    return self._send(200, server.next_device())
                server.await_token_gate()
                self._send(200, server.next_token())

            def log_message(self, *args):
                pass

        self._start(Handler)

    def hold_token_endpoint(self):
        """Make the next token request block until :meth:`release_token_endpoint` is called.

        :return: an Event set once a token request has arrived and is waiting
        """
        self.token_request_arrived = threading.Event()
        self._token_gate = threading.Event()
        return self.token_request_arrived

    def release_token_endpoint(self):
        """Let a held token request complete."""
        gate = self._token_gate
        self._token_gate = None
        if gate is not None:
            gate.set()

    def await_token_gate(self):
        gate = self._token_gate
        if gate is None:
            return
        self.token_request_arrived.set()
        # Bounded so a mistake in a test fails as a test rather than hanging the run.
        gate.wait(30)

    def next_token(self):
        with self.lock:
            if self.token_responses:
                return self.token_responses.pop(0)
            self.serial += 1
            return {
                'access_token': 'AT%d' % self.serial,
                'refresh_token': 'RT%d' % self.serial,
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': 'api.quote:read',
            }

    def next_device(self):
        with self.lock:
            if self.device_responses:
                return self.device_responses.pop(0)
            return {
                'device_code': 'DEV-CODE',
                'user_code': 'ABCD-EFGH',
                'verification_uri': self.base_url + '/activate',
                'expires_in': 600,
            }

    def calls_to(self, path):
        return [c for c in self.calls if c[0] == path]

    def token_calls(self):
        return self.calls_to('/token')

    def revoke_calls(self):
        return self.calls_to('/revoke')


class FakeGateway(_ThreadedServer):
    """Business gateway. Records the Authorization header and body of each request."""

    def __init__(self):
        self.requests = []
        self.responses = []
        gateway = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get('Content-Length') or 0)).decode()
                gateway.requests.append((self.headers.get('Authorization'), json.loads(raw)))
                status, payload = gateway.next_response()
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self._start(Handler)
        self.url = self.base_url + '/gateway'

    def next_response(self):
        if self.responses:
            return self.responses.pop(0)
        return 200, {'code': 0, 'message': 'success', 'data': {}}

    def auth_headers(self):
        return [h for h, _ in self.requests]


class StubSessions:
    """Stands in for OAuth2SessionManager on the data-plane side; counts refreshes."""

    def __init__(self, token='tok-1'):
        self.token = token
        self.refreshes = 0

    def get_access_token(self):
        return self.token

    def refresh_after_unauthorized(self, failed):
        self.refreshes += 1
        if failed == self.token:
            self.token = 'tok-refreshed'
        return OAuth2Token(access_token=self.token)
