# -*- coding: utf-8 -*-
"""
OAuth2 session management -- the control plane.

Handles metadata discovery, dynamic registration, authorization (loopback + PKCE or
device code), token refresh and persistence. The data plane (how each request carries a
credential) lives in :class:`~tigeropen.auth.oauth2.authentication.OAuth2Authentication`,
which only needs :meth:`OAuth2SessionManager.get_access_token` and
:meth:`OAuth2SessionManager.refresh_after_unauthorized`.

Scopes are never hardcoded and never chosen by the application: authorization always
requests every ``scopes_supported`` entry from the metadata. Dynamic registration
declares no scope and records the granted set as ``registered_scopes``, so a later scope
expansion triggers re-registration instead of an ``invalid_scope``.

The constructor sends no requests, so building the object works offline.
"""
import base64
import hashlib
import logging
import os
import re
import threading
import time
from urllib.parse import urlencode

from tigeropen.auth.oauth2 import http_utils
from tigeropen.auth.oauth2.client_registration import OAuth2ClientRegistration
from tigeropen.auth.oauth2.device_authorization import OAuth2DeviceAuthorization
from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception
from tigeropen.auth.oauth2.loopback_receiver import LoopbackReceiver
from tigeropen.auth.oauth2.metadata import OAuth2Metadata
from tigeropen.auth.oauth2.token import OAuth2Token, current_millis
from tigeropen.auth.oauth2.token_store import OAuth2TokenStore

logger = logging.getLogger(__name__)

ENV_ISSUER = 'TIGEROPEN_OAUTH2_ISSUER'

# WARNING: still a placeholder, must be changed to the production address before launch
BUILTIN_ISSUER = 'https://openapi-oauth2-test.qa.tigerbrokers.net'

#: How early to refresh an access token
DEFAULT_REFRESH_AHEAD_MILLIS = 300 * 1000
#: How long to wait for the browser callback
DEFAULT_AUTHORIZE_TIMEOUT_SECONDS = 5 * 60
#: RFC 8628 §3.5 default. Tiger's server does not return ``interval``, so this applies.
DEFAULT_DEVICE_POLL_INTERVAL_SECONDS = 5
#: Added to the polling interval on each ``slow_down``
DEVICE_SLOW_DOWN_INCREMENT_SECONDS = 5
#: Fallback when the device authorization response omits ``expires_in``
DEFAULT_DEVICE_EXPIRES_IN_SECONDS = 600

#: Fixed callback port for a manually configured clientId. Chosen to stay clear of the
#: default Linux ephemeral range (from 32768) and of common dev ports.
DEFAULT_MANUAL_CALLBACK_PORT = 18888

GRANT_TYPE_AUTHORIZATION_CODE = 'authorization_code'
GRANT_TYPE_REFRESH_TOKEN = 'refresh_token'
GRANT_TYPE_DEVICE_CODE = 'urn:ietf:params:oauth:grant-type:device_code'

DEFAULT_CLIENT_NAME = 'Tiger Python SDK'

_WHITESPACE = re.compile(r'\s+')


class OAuth2SessionManager:
    """An OAuth2 session. Thread-safe.

    Java uses ``builder()``; Python takes keyword arguments::

        sessions = OAuth2SessionManager()                   # dynamic registration
        sessions = OAuth2SessionManager(client_id='xxx')    # manual clientId
    """

    def __init__(self, issuer=None, client_id=None, client_name=DEFAULT_CLIENT_NAME,
                 callback_port=0, home=None,
                 refresh_ahead_millis=DEFAULT_REFRESH_AHEAD_MILLIS,
                 authorize_timeout_seconds=DEFAULT_AUTHORIZE_TIMEOUT_SECONDS):
        """
        :param issuer: authorization server; falls back to ``TIGEROPEN_OAUTH2_ISSUER``
            then to the built-in default
        :param client_id: manually issued clientId; omit to use dynamic registration
        :param callback_port: 0 lets the system assign one (dynamic registration only)
        :param home: storage root; falls back to ``TIGEROPEN_HOME`` then
            ``~/.tiger/openapi``
        """
        self._issuer = _trim_trailing_slash(issuer or self.default_issuer())
        self._client_name = client_name or DEFAULT_CLIENT_NAME
        self._callback_port = callback_port or 0
        #: Deliberately immutable: it determines the token filename and whether dynamic
        #: registration is used, so changing it mid-flight desynchronises memory and disk
        self._explicit_client_id = client_id or None
        self._refresh_ahead_millis = refresh_ahead_millis
        self._authorize_timeout_seconds = authorize_timeout_seconds

        self._store = OAuth2TokenStore(home)
        self._registered_client_id = None   # always None in manual mode
        self._metadata = None
        self._token = None
        self._resolved_scopes = None

        self._refresh_lock = threading.RLock()
        self._metadata_lock = threading.RLock()

    # ------------------------------------------------------------- properties

    @staticmethod
    def default_issuer():
        return _trim_trailing_slash(os.environ.get(ENV_ISSUER) or BUILTIN_ISSUER)

    @property
    def issuer(self):
        return self._issuer

    @property
    def client_id(self):
        """Currently known clientId; None before registration in dynamic mode."""
        return self._known_client_id()

    @property
    def has_explicit_client_id(self):
        return self._explicit_client_id is not None

    @property
    def callback_port(self):
        return self._callback_port

    @property
    def scopes(self):
        """Scopes requested by this session, space-separated. Fetches metadata."""
        return self._scopes()

    # ---------------------------------------------------------- authorization

    @classmethod
    def login_with_defaults(cls, on_authorization_url):
        """Authorize with default settings and return the session."""
        sessions = cls()
        sessions.login(on_authorization_url)
        return sessions

    @classmethod
    def login_with_device_code_defaults(cls, on_device_authorization):
        """Authorize by device code with default settings and return the session."""
        sessions = cls()
        sessions.login_with_device_code(on_device_authorization)
        return sessions

    def login(self, on_authorization_url):
        """Browser authorization (loopback + PKCE).

        :param on_authorization_url: called with the URL the user must open
        :return: :class:`OAuth2Token`
        """
        metadata = self._metadata_of()
        client_id = self._resolve_client_id()
        scopes = self._scopes()

        # Started before the URL is handed out, or a fast user hits a dead port
        receiver = LoopbackReceiver(self._effective_callback_port())
        try:
            verifier = _random_url_safe(64)
            challenge = _s256(verifier)
            state = _random_url_safe(24)
            url = metadata.authorization_endpoint + '?' + _query({
                'response_type': 'code',
                'client_id': client_id,
                'redirect_uri': receiver.redirect_uri,
                'scope': scopes,
                'state': state,
                'code_challenge': challenge,
                'code_challenge_method': 'S256',
            })
            on_authorization_url(url)

            params = receiver.wait_for_callback(self._authorize_timeout_seconds)
        finally:
            receiver.close()

        error = params.get('error')
        if error:
            raise OAuth2Exception(Category.CALLBACK_FAILED,
                                  'authorization denied: %s %s'
                                  % (error, params.get('error_description') or ''))
        if params.get('state') != state:
            # A state mismatch means this callback is not from the flow we started
            raise OAuth2Exception(Category.CALLBACK_FAILED, 'state mismatch in authorization callback')
        code = params.get('code')
        if not code:
            raise OAuth2Exception(Category.CALLBACK_FAILED, 'authorization callback has no code')

        token = self._exchange({
            'grant_type': GRANT_TYPE_AUTHORIZATION_CODE,
            'code': code,
            'redirect_uri': receiver.redirect_uri,
            'client_id': client_id,
            'code_verifier': verifier,
        }, scopes, client_id)
        self._persist(token)
        logger.info('oauth2 authorized. issuer:%s, client_id:%s, scope:%s',
                    self._issuer, client_id, token.scope)
        return token

    def login_if_needed(self, on_authorization_url):
        """Reuse a usable token, else refresh silently, else authorize."""
        token = self._reusable_token()
        if token is not None:
            return token
        existing = self._current_token()
        if existing is not None and existing.has_refresh_token():
            try:
                return self.refresh()
            except OAuth2Exception as e:
                logger.info('oauth2 silent refresh failed (%s), falling back to authorization', e)
        return self.login(on_authorization_url)

    def login_with_device_code(self, on_device_authorization):
        """Device code authorization (RFC 8628), for environments with no local browser.

        Less secure than loopback + PKCE: the user approves on another device, so the SDK
        cannot confirm the approver is the person operating this machine. Prefer
        :meth:`login` wherever a browser exists.

        :param on_device_authorization: called with an
            :class:`OAuth2DeviceAuthorization` to show the user code and verification URI
        """
        metadata = self._metadata_of()
        if not metadata.device_authorization_endpoint:
            raise OAuth2Exception(Category.METADATA_UNAVAILABLE,
                                  'authorization server does not advertise a device_authorization_endpoint')
        client_id = self._resolve_client_id()
        scopes = self._scopes()

        device = self._request_device_authorization(metadata, client_id, scopes)
        on_device_authorization(device)

        token = self._poll_for_device_token(metadata, device, client_id, scopes)
        self._persist(token)
        logger.info('oauth2 authorized by device code. issuer:%s, client_id:%s, scope:%s',
                    self._issuer, client_id, token.scope)
        return token

    def logout(self):
        """Clear the stored authorization. The registered client_id is kept: it is this
        machine's identity, not an authorization."""
        client_id = self._known_client_id()
        if client_id:
            self._store.delete_token(client_id)
        self._token = None
        logger.info('oauth2 logged out. client_id:%s', client_id)

    # ----------------------------------------------------------------- usage

    def get_access_token(self):
        """Return a currently usable access token, refreshing synchronously if it is
        close to expiry.

        Raises ``REAUTHORIZATION_REQUIRED`` if authorization never happened; it never
        opens a browser implicitly, since a background process suddenly launching one is
        harder to diagnose than a clear error.
        """
        token = self._current_token()
        if token is None or not token.access_token:
            raise OAuth2Exception(Category.REAUTHORIZATION_REQUIRED,
                                  'not authorized yet, call login() first')
        if not token.needs_refresh(self._refresh_ahead_millis):
            return token.access_token
        return self.refresh(token.access_token).access_token

    def status(self):
        """The current token, or None. Sends no requests and triggers no authorization."""
        return self._current_token()

    def is_authorized(self):
        return self._current_token() is not None

    def refresh(self, failed_access_token=None):
        """Refresh because the token is close to expiry."""
        return self._do_refresh(failed_access_token, force=False)

    def refresh_after_unauthorized(self, failed_access_token):
        """Refresh because of a 401, even if the token still looks fresh.

        :param failed_access_token: the access token that got the 401. If another thread
            already rotated it, the new one is returned without hitting the token
            endpoint -- this is what suppresses 401 storms.
        """
        return self._do_refresh(failed_access_token, force=True)

    def _do_refresh(self, failed_access_token, force):
        # Single-flight: concurrent refreshes queue up, the first one does the work
        with self._refresh_lock:
            current = self._current_token()
            if current is None:
                raise OAuth2Exception(Category.REAUTHORIZATION_REQUIRED,
                                      'not authorized yet, call login() first')
            if failed_access_token is not None and current.access_token != failed_access_token:
                # Already rotated by another thread. Compares token values rather than
                # timestamps: equal timestamps do not imply the same token.
                return current
            if not force and not current.needs_refresh(self._refresh_ahead_millis):
                return current
            if not current.has_refresh_token():
                raise OAuth2Exception(Category.REAUTHORIZATION_REQUIRED,
                                      'no refresh_token available, re-authorization required')

            client_id = self._known_client_id()
            token = self._exchange({
                'grant_type': GRANT_TYPE_REFRESH_TOKEN,
                'refresh_token': current.refresh_token,
                'client_id': client_id,
            }, current.scope, client_id)
            if not token.refresh_token:
                # Carry the old one forward, or there is nothing to refresh with next time
                token.refresh_token = current.refresh_token
            self._persist(token)
            logger.info('oauth2 access token refreshed. client_id:%s', client_id)
            return token

    # --------------------------------------------------------------- internal

    def _reusable_token(self):
        token = self._current_token()
        if token is not None and token.access_token \
                and not token.needs_refresh(self._refresh_ahead_millis):
            return token
        return None

    def _current_token(self):
        token = self._token
        if token is not None:
            return token
        client_id = self._known_client_id()
        if not client_id:
            return None
        token = self._store.load_token(client_id, self._issuer)
        if token is not None:
            self._token = token
        return token

    def _known_client_id(self):
        """The known clientId, without triggering registration. Manual mode never reads
        ``clients/``."""
        if self._explicit_client_id:
            return self._explicit_client_id
        if self._registered_client_id:
            return self._registered_client_id
        client_id = self._store.load_client_id(self._issuer)
        if client_id:
            self._registered_client_id = client_id
        return client_id

    def _persist(self, token):
        self._token = token
        self._store.save_token(token)

    def _effective_callback_port(self):
        if self._callback_port > 0:
            return self._callback_port
        # A manual clientId has a fixed redirect_uri registered in the console, so the
        # port must match; dynamic registration lets the system assign one
        return DEFAULT_MANUAL_CALLBACK_PORT if self._explicit_client_id else 0

    def _scopes(self):
        scopes = self._resolved_scopes
        if scopes is not None:
            return scopes
        metadata = self._metadata_of()
        if not metadata.scopes_supported:
            # Do not guess. Requesting too few scopes surfaces as a 403 from some
            # endpoint much later, which is far harder to trace than failing here.
            raise OAuth2Exception(Category.METADATA_UNAVAILABLE,
                                  'authorization server metadata has no scopes_supported')
        scopes = _normalize_scopes(' '.join(metadata.scopes_supported))
        self._resolved_scopes = scopes
        return scopes

    def _metadata_of(self):
        metadata = self._metadata
        if metadata is not None:
            return metadata
        with self._metadata_lock:
            if self._metadata is not None:
                return self._metadata
            url = self._issuer + '/.well-known/oauth-authorization-server'
            data = http_utils.get_json(url)
            metadata = OAuth2Metadata.from_dict(data)
            if metadata is None or not metadata.authorization_endpoint or not metadata.token_endpoint:
                raise OAuth2Exception(Category.METADATA_UNAVAILABLE,
                                      'incomplete authorization server metadata from ' + url)
            self._metadata = metadata
            return metadata

    def _resolve_client_id(self):
        """Manual clientId > saved registration whose scopes still cover > register."""
        if self._explicit_client_id:
            return self._explicit_client_id
        required = self._scopes()
        registration = self._store.load_client_registration(self._issuer)
        if registration is not None and registration.client_id \
                and _scopes_cover(registration.registered_scopes, required):
            self._registered_client_id = registration.client_id
            return registration.client_id
        if registration is not None and registration.client_id:
            logger.info('registered scopes no longer cover required scopes, re-registering client')
        return self._register(required)

    def _register(self, scopes):
        """Dynamic registration (RFC 7591).

        Deliberately declares no scope: if the declared set were ever narrower than what
        is later needed, authorization would fail with ``invalid_scope`` while the
        registration is already persisted, which is a dead end. Instead the granted set
        is recorded and a wider requirement triggers re-registration.
        """
        metadata = self._metadata_of()
        if not metadata.registration_endpoint:
            raise OAuth2Exception(
                Category.CLIENT_REGISTRATION_REQUIRED,
                'authorization server does not support dynamic registration; '
                'pass client_id explicitly')
        port = self._callback_port
        redirect_uri = ('http://127.0.0.1:%d/callback' % port) if port > 0 \
            else 'http://127.0.0.1/callback'
        payload = {
            'client_name': self._client_name,
            'redirect_uris': [redirect_uri],
            'grant_types': [GRANT_TYPE_AUTHORIZATION_CODE, GRANT_TYPE_REFRESH_TOKEN,
                            GRANT_TYPE_DEVICE_CODE],
            'response_types': ['code'],
            # Public client: there is no client_secret to hide, PKCE is the protection
            'token_endpoint_auth_method': 'none',
        }
        response = http_utils.post_json(metadata.registration_endpoint, payload)
        error = response.get('error')
        if error:
            raise OAuth2Exception(Category.CLIENT_REGISTRATION_REQUIRED,
                                  'dynamic registration failed: %s %s'
                                  % (error, response.get('error_description') or ''))
        client_id = response.get('client_id')
        if not client_id:
            raise OAuth2Exception(Category.CLIENT_REGISTRATION_REQUIRED,
                                  'dynamic registration response has no client_id')

        registration = OAuth2ClientRegistration(
            issuer=self._issuer,
            client_id=client_id,
            client_name=self._client_name,
            registered_scopes=_normalize_scopes(response.get('scope')) or scopes,
            client_id_issued_at=response.get('client_id_issued_at') or int(time.time()),
        )
        self._store.save_client_registration(registration)
        self._registered_client_id = client_id
        logger.info('oauth2 client registered. issuer:%s, client_id:%s', self._issuer, client_id)
        return client_id

    def _request_device_authorization(self, metadata, client_id, scopes):
        response = http_utils.post_form(metadata.device_authorization_endpoint, {
            'client_id': client_id,
            'scope': scopes,
        })
        error = response.get('error')
        if error:
            raise OAuth2Exception(Category.DEVICE_AUTHORIZATION_FAILED,
                                  'device authorization failed: %s %s'
                                  % (error, response.get('error_description') or ''))
        device = OAuth2DeviceAuthorization.from_dict(response)
        if device is None or not device.device_code or not device.user_code:
            raise OAuth2Exception(Category.DEVICE_AUTHORIZATION_FAILED,
                                  'incomplete device authorization response')
        return device

    def _poll_for_device_token(self, metadata, device, client_id, scopes):
        """Poll the token endpoint until the user approves.

        Deliberately not reusing :meth:`_exchange`: ``invalid_grant`` means something
        different here, and ``authorization_pending`` / ``slow_down`` do not exist there.
        """
        interval = device.effective_interval()
        expires_in = device.expires_in or DEFAULT_DEVICE_EXPIRES_IN_SECONDS
        deadline = time.time() + expires_in

        while True:
            if time.time() >= deadline:
                raise OAuth2Exception(Category.DEVICE_AUTHORIZATION_FAILED,
                                      'device authorization was not approved in time')
            time.sleep(interval)
            response = http_utils.post_form(metadata.token_endpoint, {
                'grant_type': GRANT_TYPE_DEVICE_CODE,
                'device_code': device.device_code,
                'client_id': client_id,
            })
            error = response.get('error')
            if not error:
                return self._to_token(response, scopes, client_id)
            if error == 'authorization_pending':
                continue
            if error == 'slow_down':
                interval += DEVICE_SLOW_DOWN_INCREMENT_SECONDS
                logger.debug('device polling slowed down to %ss', interval)
                continue
            if error == 'access_denied':
                raise OAuth2Exception(Category.DEVICE_AUTHORIZATION_FAILED,
                                      'device authorization was denied by the user')
            if error == 'expired_token':
                raise OAuth2Exception(Category.DEVICE_AUTHORIZATION_FAILED,
                                      'device code expired before it was approved')
            raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED,
                                  'device token request failed: %s %s'
                                  % (error, response.get('error_description') or ''))

    def _exchange(self, form, requested_scopes, client_id):
        metadata = self._metadata_of()
        response = http_utils.post_form(metadata.token_endpoint, form)
        error = response.get('error')
        if error:
            description = response.get('error_description') or ''
            if error in ('invalid_grant', 'invalid_client'):
                # Terminal: the stored authorization is dead, keeping it only makes every
                # later call retry and fail again
                self._store.delete_token(client_id)
                self._token = None
                if error == 'invalid_client' and self._explicit_client_id is None:
                    # The server no longer knows this dynamically registered client, so
                    # the registration is void too
                    self._store.delete_client_registration(self._issuer)
                    self._registered_client_id = None
                raise OAuth2Exception(Category.REAUTHORIZATION_REQUIRED,
                                      'token request rejected: %s %s' % (error, description))
            raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED,
                                  'token request failed: %s %s' % (error, description))
        return self._to_token(response, requested_scopes, client_id)

    def _to_token(self, response, requested_scopes, client_id):
        access_token = response.get('access_token')
        if not access_token:
            raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED,
                                  'token response has no access_token')
        expires_in = response.get('expires_in') or 3600
        return OAuth2Token(
            issuer=self._issuer,
            client_id=client_id,
            access_token=access_token,
            refresh_token=response.get('refresh_token'),
            token_type=response.get('token_type') or 'Bearer',
            # The response scope wins: what was granted may be narrower than requested
            scope=_normalize_scopes(response.get('scope')) or requested_scopes,
            expires_at=current_millis() + int(expires_in) * 1000,
        )


def _scopes_cover(granted, required):
    if not granted or not required:
        return False
    granted_set = set(granted.split(' '))
    return all(scope in granted_set for scope in required.split(' '))


def _normalize_scopes(raw):
    """Split on whitespace, dedupe, sort, join with spaces.

    Sorting keeps :func:`_scopes_cover` and the stored value order-independent: the
    authorization server does not guarantee a stable order, and without normalization
    that would spuriously trigger re-registration.
    """
    if not raw:
        return None
    parts = [p for p in _WHITESPACE.split(raw.strip()) if p]
    if not parts:
        return None
    return ' '.join(sorted(set(parts)))


def _trim_trailing_slash(value):
    if not value:
        return value
    return value[:-1] if value.endswith('/') else value


def _query(params):
    return urlencode([(k, v) for k, v in params.items() if v is not None])


def _random_url_safe(num_bytes):
    return base64.urlsafe_b64encode(os.urandom(num_bytes)).decode('ascii').rstrip('=')


def _s256(verifier):
    digest = hashlib.sha256(verifier.encode('ascii')).digest()
    return base64.urlsafe_b64encode(digest).decode('ascii').rstrip('=')
