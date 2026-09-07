# -*- coding: utf-8 -*-
"""
Local callback receiver (RFC 8252 loopback).

Binds a port on ``127.0.0.1`` and shuts down after receiving a single callback.

With dynamic registration the port is 0, so the system assigns one and it is not
persisted: registration sends ``http://127.0.0.1/callback`` as the redirect_uri, and per
RFC 8252 §7.3 the authorization server ignores the port when matching a loopback URI.
With a manual clientId the port must match the redirect_uri the user registered by hand,
which the SDK cannot know -- hence the agreed default of 18888.

It binds only ``127.0.0.1``, not ``0.0.0.0``: the authorization code must not be exposed
to the local network. It uses the IP literal rather than ``localhost`` (RFC 8252 §8.3),
which depends on hosts resolution and can be redirected elsewhere.

It must be started **before** the authorization URL is handed to the user, otherwise a
fast user can finish approving before the listener is up and the redirect arrives at a
port with nobody listening.
"""
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse

from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception

logger = logging.getLogger(__name__)

CALLBACK_PATH = '/callback'

#: Inline SVG rather than an image, an icon font or a unicode glyph: the page must
#: render the same everywhere with no network access, and the check glyph is missing or
#: ugly in plenty of default fonts.
_CHECK_MARK = (
    "<svg width='64' height='64' viewBox='0 0 64 64' aria-hidden='true'>"
    "<circle cx='32' cy='32' r='29' fill='none' stroke='#22c55e' stroke-width='4'/>"
    "<path d='M19 33l9.5 9.5L45 22' fill='none' stroke='#22c55e' stroke-width='5'"
    " stroke-linecap='round' stroke-linejoin='round'/></svg>"
)


class LoopbackReceiver:
    """Single-shot local callback server. Usable as a context manager."""

    def __init__(self, port=0):
        """:param port: port to bind; 0 lets the system assign a free one"""
        self._latch = threading.Event()
        self._lock = threading.Lock()
        self._params = {}

        receiver = self

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path != CALLBACK_PATH:
                    self.send_response(404)
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return
                try:
                    success = receiver._record(parsed.query)
                    _respond(self, success)
                finally:
                    receiver._latch.set()

            def log_message(self, fmt, *args):
                # The default implementation writes the request line to stderr, which
                # would include the callback query string and therefore the auth code
                logger.debug('loopback callback request received')

        try:
            self._server = HTTPServer(('127.0.0.1', port), _Handler)
        except OSError as e:
            # Only a fixed port can be taken, and then we must say which port and what
            # to do about it; a system-assigned port never collides
            hint = '' if port == 0 else (
                ' (port %d is in use; free it or set another callback_port'
                ' matching the redirect_uri registered for your client)' % port)
            raise OAuth2Exception(
                Category.CALLBACK_FAILED,
                'cannot bind loopback callback server on 127.0.0.1:%d%s' % (port, hint), e)

        self._thread = threading.Thread(target=self._server.serve_forever,
                                        name='tiger-oauth2-loopback', daemon=True)
        self._thread.start()

    @property
    def redirect_uri(self):
        return 'http://127.0.0.1:%d%s' % (self._server.server_address[1], CALLBACK_PATH)

    @property
    def port(self):
        return self._server.server_address[1]

    def wait_for_callback(self, timeout_seconds):
        """Wait for the browser callback.

        :return: the query parameters carried by the callback
        :raise OAuth2Exception: on timeout
        """
        if not self._latch.wait(timeout_seconds):
            raise OAuth2Exception(Category.CALLBACK_FAILED,
                                  'waiting for authorization callback timed out')
        with self._lock:
            return dict(self._params)

    def close(self):
        try:
            self._server.shutdown()
        except Exception as e:
            logger.debug('stop loopback server fail:%s', e)
        try:
            self._server.server_close()
        except Exception as e:
            logger.debug('close loopback server fail:%s', e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def _record(self, raw_query):
        with self._lock:
            if not self._latch.is_set():
                for key, value in parse_qsl(raw_query, keep_blank_values=True):
                    self._params[key] = value
            return 'code' in self._params


def _respond(handler, success):
    """The callback page states the outcome only and displays no parameters.

    The browser address bar and history keep a trace, and the page may be screenshotted
    or read by an extension. The authorization code is single-use, but leaking it before
    it is redeemed lets someone else exchange it for a token first.
    """
    if success:
        message = (_CHECK_MARK + '<h2>Authentication successful</h2>'
                   '<p>You can close this page and return to the application.</p>')
    else:
        message = ('<h2>Authentication failed</h2>'
                   '<p>Please return to the application and try again.</p>')
    html = ("<html><head><meta charset='utf-8'><title>Tiger OpenAPI</title></head>"
            "<body style=\"font-family:-apple-system,'PingFang SC',sans-serif;"
            "padding:64px;text-align:center\">" + message + "</body></html>")
    body = html.encode('utf-8')
    handler.send_response(200)
    handler.send_header('Content-Type', 'text/html; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
