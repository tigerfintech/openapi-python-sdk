# -*- coding: utf-8 -*-
"""Loopback callback receiver (RFC 8252).

Covers test-plan cases A-02..A-06, K-05, K-06.

The callback is where the authorization code lands, so most of these are security
assertions rather than functional ones.
"""
import re
import socket
import threading
import unittest
import urllib.error
import urllib.request

from tigeropen.auth.oauth2 import OAuth2Exception
from tigeropen.auth.oauth2.exceptions import Category
from tigeropen.auth.oauth2.loopback_receiver import CALLBACK_PATH, LoopbackReceiver


def get(url, timeout=5):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.status, response.read().decode()


class RedirectUriTest(unittest.TestCase):

    def test_uses_the_ip_literal_not_localhost(self):
        """K-06: RFC 8252 §8.3 — `localhost` depends on hosts resolution and can be
        pointed elsewhere."""
        with LoopbackReceiver(0) as receiver:
            self.assertTrue(receiver.redirect_uri.startswith('http://127.0.0.1:'))
            self.assertNotIn('localhost', receiver.redirect_uri)

    def test_path_is_the_agreed_one(self):
        with LoopbackReceiver(0) as receiver:
            self.assertTrue(receiver.redirect_uri.endswith(CALLBACK_PATH))

    def test_port_zero_gets_a_real_assigned_port(self):
        with LoopbackReceiver(0) as receiver:
            self.assertGreater(receiver.port, 0)
            self.assertIn(':%d/' % receiver.port, receiver.redirect_uri)

    def test_fixed_port_is_honoured(self):
        with LoopbackReceiver(0) as probe:
            free_port = probe.port
        with LoopbackReceiver(free_port) as receiver:
            self.assertEqual(free_port, receiver.port)


class BindingTest(unittest.TestCase):
    """K-05: the authorization code must not be exposed to the local network."""

    def test_binds_loopback_only(self):
        with LoopbackReceiver(0) as receiver:
            host, _ = receiver._server.server_address
            self.assertEqual('127.0.0.1', host)
            self.assertNotEqual('0.0.0.0', host)

    def test_taken_fixed_port_reports_the_port_and_what_to_do(self):
        blocker = socket.socket()
        blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        blocker.bind(('127.0.0.1', 0))
        blocker.listen(1)
        taken = blocker.getsockname()[1]
        try:
            with self.assertRaises(OAuth2Exception) as ctx:
                LoopbackReceiver(taken)
            message = ctx.exception.message
            self.assertEqual(Category.CALLBACK_FAILED, ctx.exception.category)
            self.assertIn(str(taken), message, 'the message must name the port')
            self.assertIn('callback_port', message, 'and say how to change it')
        finally:
            blocker.close()


class CallbackCaptureTest(unittest.TestCase):

    def test_listener_is_up_before_the_url_is_handed_out(self):
        """A-02: a fast user can finish approving before a late listener is ready."""
        with LoopbackReceiver(0) as receiver:
            # The constructor has returned; the port must already accept connections
            status, _ = get(receiver.redirect_uri + '?code=x&state=y')
            self.assertEqual(200, status)

    def test_query_parameters_are_captured(self):
        with LoopbackReceiver(0) as receiver:
            threading.Thread(
                target=get, args=(receiver.redirect_uri + '?code=the-code&state=the-state',),
                daemon=True).start()
            params = receiver.wait_for_callback(5)
        self.assertEqual('the-code', params['code'])
        self.assertEqual('the-state', params['state'])

    def test_url_encoded_values_are_decoded(self):
        with LoopbackReceiver(0) as receiver:
            threading.Thread(
                target=get, args=(receiver.redirect_uri + '?code=a%2Bb%2Fc&state=s',),
                daemon=True).start()
            params = receiver.wait_for_callback(5)
        self.assertEqual('a+b/c', params['code'])

    def test_error_callback_is_captured(self):
        """A-04: the user denying is a normal outcome, not a crash."""
        with LoopbackReceiver(0) as receiver:
            threading.Thread(
                target=get,
                args=(receiver.redirect_uri + '?error=access_denied&error_description=nope',),
                daemon=True).start()
            params = receiver.wait_for_callback(5)
        self.assertEqual('access_denied', params['error'])
        self.assertNotIn('code', params)

    def test_timeout_raises_callback_failed(self):
        """A-05."""
        with LoopbackReceiver(0) as receiver:
            with self.assertRaises(OAuth2Exception) as ctx:
                receiver.wait_for_callback(0.2)
            self.assertEqual(Category.CALLBACK_FAILED, ctx.exception.category)
            self.assertIn('timed out', ctx.exception.message)

    def test_other_paths_are_not_treated_as_the_callback(self):
        with LoopbackReceiver(0) as receiver:
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                get('http://127.0.0.1:%d/something-else' % receiver.port)
            self.assertEqual(404, ctx.exception.code)

    def test_port_is_released_after_close(self):
        receiver = LoopbackReceiver(0)
        port = receiver.port
        receiver.close()
        probe = socket.socket()
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(('127.0.0.1', port))    # raises if still held
        finally:
            probe.close()

    def test_close_is_idempotent(self):
        receiver = LoopbackReceiver(0)
        receiver.close()
        receiver.close()


class CallbackPageTest(unittest.TestCase):
    """A-06: the page is rendered in the user's browser -- it must leak nothing.

    It also has to report the *right* outcome: `access_denied` is the user pressing
    "decline", not a failure.
    """

    def _page(self, query, accept_language='en-US,en;q=0.9'):
        with LoopbackReceiver(0) as receiver:
            request = urllib.request.Request(
                receiver.redirect_uri + query,
                headers={'Accept-Language': accept_language} if accept_language else {})
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.read().decode()

    # ---------------------------------------------------------------- outcome

    def test_success_page(self):
        body = self._page('?code=SECRET-CODE&state=SECRET-STATE')
        self.assertIn('Authorization successful', body)
        self.assertIn('#22c55e', body, 'green tick')

    def test_declined_page_is_not_reported_as_a_failure(self):
        """The user chose to decline; calling that a failure describes the wrong thing
        and nudges them to redo something they meant to refuse."""
        body = self._page('?error=access_denied&state=s')

        self.assertIn('Authorization cancelled', body)
        self.assertNotIn('failed', body.lower())
        self.assertNotIn('try again', body.lower(), 'must not push a retry')

    def test_declined_page_uses_a_neutral_icon(self):
        """Grey dash, not a red cross -- declining is a normal outcome."""
        body = self._page('?error=access_denied&state=s')

        self.assertIn('#9ca3af', body, 'neutral grey')
        self.assertNotIn('#ef4444', body, 'must not be coloured as an error')

    def test_real_error_page(self):
        body = self._page('?error=server_error&state=s')

        self.assertIn('Authorization failed', body)
        self.assertIn('#ef4444', body, 'red cross')

    def test_missing_code_without_an_error_is_a_failure(self):
        """A callback with neither `code` nor `error` is malformed, not a decline."""
        body = self._page('?state=s')

        self.assertIn('Authorization failed', body)
        self.assertIn('#ef4444', body)

    # --------------------------------------------------------------- language

    def test_page_is_english_regardless_of_browser_language(self):
        """**Fixed English, on purpose.** The SDK's exceptions, logs and error messages are
        all English; a callback page that followed the browser would be the one localised
        surface in an otherwise English toolkit. It is also what gets screenshotted into
        bug reports, where a fixed wording is easier to search for and quote.
        """
        for header in ('zh-CN,zh;q=0.9', 'zh-TW', 'zh-HK', 'ja', 'fr-FR', '', None):
            body = self._page('?error=access_denied&state=s', header)
            self.assertIn('Authorization cancelled', body, repr(header))

    def test_no_page_contains_non_ascii_copy(self):
        """Catches a stray localised string being reintroduced into any of the three."""
        for query in ('?code=x&state=y', '?error=access_denied', '?error=server_error'):
            body = self._page(query, 'zh-CN')
            heading = re.search(r'<h2[^>]*>([^<]*)</h2>', body).group(1)
            detail = re.search(r'<p [^>]*>([^<]*)</p>', body).group(1)
            self.assertTrue(heading.isascii(), '%s -> %s' % (query, heading))
            self.assertTrue(detail.isascii(), '%s -> %s' % (query, detail))

    # ----------------------------------------------------------------- safety

    def test_no_page_leaks_any_parameter(self):
        secrets = ('SECRET-CODE', 'SECRET-STATE', 'server_error', 'access_denied')
        pages = (self._page('?code=SECRET-CODE&state=SECRET-STATE'),
                 self._page('?error=access_denied&state=SECRET-STATE'),
                 self._page('?error=server_error&state=SECRET-STATE'))

        for body in pages:
            for secret in secrets:
                self.assertNotIn(secret, body)

    def test_page_loads_no_external_resources(self):
        """It must render identically with no network; the icons are inline SVG."""
        for query in ('?code=x&state=y', '?error=access_denied', '?error=server_error'):
            body = self._page(query)
            self.assertIn('<svg', body)
            for tag in ('<img', '<script', '<link', 'http://', 'https://'):
                self.assertNotIn(tag, body, '%s in %s' % (tag, query))

    def test_page_declares_utf8(self):
        self.assertIn("charset='utf-8'", self._page('?code=x&state=y'))

    def test_pages_share_one_layout(self):
        """The three outcomes differ only in icon and copy -- same geometry, same shell."""
        pages = [self._page(q) for q in
                 ('?code=x&state=y', '?error=access_denied', '?error=server_error')]
        for body in pages:
            self.assertIn("viewBox='0 0 64 64'", body, 'same icon geometry')
            self.assertIn("max-width:420px", body, 'same content shell')
            self.assertIn('<h2', body)
            self.assertIn('<p ', body)


class SingleShotTest(unittest.TestCase):

    def test_first_callback_wins(self):
        """A-07-ish: a second request must not overwrite a completed result."""
        with LoopbackReceiver(0) as receiver:
            get(receiver.redirect_uri + '?code=first&state=s')
            first = receiver.wait_for_callback(5)
            get(receiver.redirect_uri + '?code=second&state=s')
            self.assertEqual('first', first['code'])
            self.assertEqual('first', receiver.wait_for_callback(5)['code'])

    def test_wait_returns_a_copy(self):
        with LoopbackReceiver(0) as receiver:
            get(receiver.redirect_uri + '?code=x&state=y')
            params = receiver.wait_for_callback(5)
            params['code'] = 'mutated'
            self.assertEqual('x', receiver.wait_for_callback(5)['code'])


if __name__ == '__main__':
    unittest.main()
