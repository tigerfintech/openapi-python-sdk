# -*- coding: utf-8 -*-
"""Single-use OAuth 2.0 loopback redirect receiver (RFC 8252).

The receiver binds only to ``127.0.0.1`` to prevent authorization code exposure on the
local network. Dynamic registration uses a system-assigned port as permitted by RFC 8252
§7.3; manual registration requires a port matching its redirect URI. The IP literal
avoids the name-resolution risks described by RFC 8252 §8.3.
"""
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse

from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception

logger = logging.getLogger(__name__)

CALLBACK_PATH = '/callback'

#: Inline SVG avoids external resources and font-dependent glyph rendering.
def _icon(color, path):
    return ("<svg width='64' height='64' viewBox='0 0 64 64' aria-hidden='true'>"
            "<circle cx='32' cy='32' r='29' fill='none' stroke='%s' stroke-width='4'/>"
            "<path d='%s' fill='none' stroke='%s' stroke-width='5'"
            " stroke-linecap='round' stroke-linejoin='round'/></svg>" % (color, path, color))


#: Green tick.
_ICON_SUCCESS = _icon('#22c55e', 'M19 33l9.5 9.5L45 22')
#: Grey dash for the normal ``access_denied`` outcome.
_ICON_CANCELLED = _icon('#9ca3af', 'M20 32h24')
#: Red cross, for outcomes that really are failures.
_ICON_FAILED = _icon('#ef4444', 'M22 22l20 20M42 22L22 42')

#: English callback text, kept consistent with the Java SDK.
_TEXT = {
    'title': 'Tiger OpenAPI',
    'success': ('Authorization successful',
                'You can close this page and return to the application.'),
    'cancelled': ('Authorization cancelled',
                  'You declined this authorization. You can close this page.'),
    'failed': ('Authorization failed',
               'Please return to the application and try again.'),
}


def _outcome_of(params):
    """Classify ``access_denied`` as cancellation and other errors as failures."""
    if 'code' in params:
        return 'success'
    if params.get('error') == 'access_denied':
        return 'cancelled'
    return 'failed'


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
                    params = receiver._record(parsed.query)
                    _respond(self, params)
                finally:
                    receiver._latch.set()

            def log_message(self, fmt, *args):
                # Suppress the default request log because its query string contains the
                # authorization code.
                logger.debug('loopback callback request received')

        try:
            self._server = HTTPServer(('127.0.0.1', port), _Handler)
        except OSError as e:
            # A fixed port can conflict with another listener; system-assigned ports do not.
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
        """Record the callback params (first one wins) and return a snapshot of them."""
        with self._lock:
            if not self._latch.is_set():
                for key, value in parse_qsl(raw_query, keep_blank_values=True):
                    self._params[key] = value
            return dict(self._params)


def _respond(handler, params):
    """Render a redacted callback outcome page.

    Callback parameters, including authorization codes and errors, are omitted because
    browser history, screenshots, and extensions may expose page content. Full parameters
    remain available to internal callback processing.
    """
    outcome = _outcome_of(params)
    icon = {'success': _ICON_SUCCESS,
            'cancelled': _ICON_CANCELLED,
            'failed': _ICON_FAILED}[outcome]
    heading, detail = _TEXT[outcome]

    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>%s</title></head>"
        "<body style=\"margin:0;min-height:100vh;display:flex;align-items:center;"
        "justify-content:center;"
        "font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',"
        "sans-serif;background:#fafafa;color:#1f2328\">"
        "<main style='text-align:center;padding:48px 24px;max-width:420px'>"
        "%s"
        "<h2 style='margin:24px 0 8px;font-size:20px;font-weight:600'>%s</h2>"
        "<p style='margin:0;font-size:14px;line-height:1.6;color:#6b7280'>%s</p>"
        "</main></body></html>" % (_TEXT['title'], icon, heading, detail))

    body = html.encode('utf-8')
    handler.send_response(200)
    handler.send_header('Content-Type', 'text/html; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
