# -*- coding: utf-8 -*-
"""Thread-safe OAuth 2.0 authorization session management.

The manager performs metadata discovery, dynamic registration, loopback or device
authorization, token refresh, and persistence. Requested scopes are derived from
``scopes_supported`` metadata. Construction performs no network requests.
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

# Production authorization server. The environment variable or constructor argument
# overrides this value.
BUILTIN_ISSUER = 'https://openapi-oauth2.tigerfintech.com'

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

#: Stable application name used for persisted dynamic registration metadata.
CLIENT_NAME = 'Tiger Python SDK'

_WHITESPACE = re.compile(r'\s+')


class OAuth2SessionManager:
    """Thread-safe OAuth 2.0 authorization session manager."""

    def __init__(self, issuer=None, client_id=None, callback_port=0, home=None,
                 store=None,
                 authorize_timeout_seconds=DEFAULT_AUTHORIZE_TIMEOUT_SECONDS):
        """Initialize a session without performing network requests.

        :param issuer: authorization server; defaults to ``TIGEROPEN_OAUTH2_ISSUER`` or
            the built-in issuer
        :param client_id: manually issued client ID; omit for dynamic registration
        :param callback_port: loopback port; 0 selects a system-assigned port for dynamic
            registration
        :param home: storage root; defaults to ``TIGEROPEN_HOME`` or
            ``~/.tiger/openapi``; ignored when ``store`` is provided
        :param store: persistence provider implementing the ``OAuth2TokenStore`` methods
        :param authorize_timeout_seconds: loopback callback timeout in seconds
        """
        self._issuer = _trim_trailing_slash(issuer or self.default_issuer())
        self._callback_port = callback_port or 0
        #: Fixed for the session because it determines storage keys and registration mode.
        self._explicit_client_id = client_id or None
        self._authorize_timeout_seconds = authorize_timeout_seconds

        self._store = store if store is not None else OAuth2TokenStore(home)
        self._registered_client_id = None   # always None in manual mode
        self._metadata = None
        self._token = None
        self._resolved_scopes = None

        self._refresh_lock = threading.RLock()
        self._metadata_lock = threading.RLock()

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

    @classmethod
    def login_with_defaults(cls, on_authorization_url):
        """Create a default session and perform browser authorization when required.

        The callback receives the authorization URL; the SDK does not open a browser.
        """
        sessions = cls()
        sessions.login_if_needed(on_authorization_url)
        return sessions

    @classmethod
    def login_with_device_code_defaults(cls, on_device_authorization):
        """Create a default session and perform device authorization when required."""
        sessions = cls()
        sessions.login_with_device_code_if_needed(on_device_authorization)
        return sessions

    def login(self, on_authorization_url):
        """Perform browser authorization with a loopback redirect and PKCE.

        :param on_authorization_url: callback receiving the authorization URL
        :return: :class:`OAuth2Token`
        """
        metadata = self._metadata_of()
        client_id = self._resolve_client_id()
        scopes = self._scopes()

        # The receiver must be listening before the authorization request is issued.
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
            # A mismatch indicates that the callback does not belong to the active flow.
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
        """Use the existing local authorization if usable, otherwise run a full
        loopback + PKCE authorization.

        Blocks until authorization completes or times out.
        """
        reusable = self._reusable_token()
        if reusable is not None:
            return reusable
        return self.login(on_authorization_url)

    def login_with_device_code_if_needed(self, on_device_authorization):
        """Reuse local authorization or perform device authorization (RFC 8628).

        Device authorization supports environments without a local browser. Unlike
        loopback authorization with PKCE, it has no redirect binding or proof that the
        initiating and redeeming clients are the same party, increasing phishing risk.
        Loopback authorization is preferred when a local browser is available.
        """
        reusable = self._reusable_token()
        if reusable is not None:
            return reusable
        return self.login_with_device_code(on_device_authorization)

    def login_with_device_code(self, on_device_authorization):
        """Perform device authorization as defined by RFC 8628.

        This flow is intended for environments without a local browser and has the
        security limitations documented by :meth:`login_with_device_code_if_needed`.

        :param on_device_authorization: callback receiving an
            :class:`OAuth2DeviceAuthorization`
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
        """Revoke authorization under RFC 7009 and delete the local token.

        Dynamic client registration is retained across logout. The local token is
        deleted even if server-side revocation fails.

        :return: True when server-side revocation succeeds; False when only local state
            is cleared and the server credential may remain valid
        """
        client_id = self._known_client_id()
        revoked = self._revoke(self._current_token(), client_id)
        if client_id:
            self._store.delete_token(client_id)
        self._token = None
        logger.info('oauth2 logged out. client_id:%s, server_revoked:%s', client_id, revoked)
        return revoked

    def _revoke(self, current, client_id):
        """Attempt server-side revocation without raising.

        The refresh token is preferred because RFC 7009 §2.1 permits revocation of its
        associated access tokens. RFC 7009 §2.2 also returns success for unknown or
        previously revoked tokens.
        """
        if current is None or not client_id:
            return False
        value = current.refresh_token or current.access_token
        hint = 'refresh_token' if current.refresh_token else 'access_token'
        if not value:
            return False
        try:
            endpoint = self._metadata_of().revocation_endpoint
            if not endpoint:
                # Revocation is optional under RFC 8414.
                logger.warning('authorization server advertises no revocation_endpoint, '
                               'logging out locally only')
                return False
            status = http_utils.post_form_for_status(endpoint, {
                'token': value,
                'token_type_hint': hint,
                'client_id': client_id,
            })
            if 200 <= status < 300:
                return True
            # HTTP 400 and 401 indicate that the server rejected the client.
            logger.warning('oauth2 revoke rejected, http status:%s, logging out locally only',
                           status)
            return False
        except OAuth2Exception as e:
            logger.warning('oauth2 revoke failed:%s, logging out locally only', e.message)
            return False
        except Exception as e:
            logger.warning('oauth2 revoke error:%s, logging out locally only', e)
            return False

    def get_access_token(self):
        """Return a usable access token, refreshing synchronously near expiry.

        Raises ``REAUTHORIZATION_REQUIRED`` when no authorization is available. Browser
        authorization is never started implicitly.
        """
        token = self._current_token()
        if token is None or not token.access_token:
            raise OAuth2Exception(Category.REAUTHORIZATION_REQUIRED,
                                  'not authorized yet, call login() first')
        if not token.needs_refresh(DEFAULT_REFRESH_AHEAD_MILLIS):
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
        """Refresh after a 401 even when the token is not near expiry.

        :param failed_access_token: token used by the failed request; comparison with the
            current token detects rotation completed by another thread and preserves
            single-flight refresh behavior
        """
        return self._do_refresh(failed_access_token, force=True)

    def _do_refresh(self, failed_access_token, force):
        # Single-flight refresh: the first caller performs rotation while others wait.
        with self._refresh_lock:
            current = self._current_token()
            if current is None:
                raise OAuth2Exception(Category.REAUTHORIZATION_REQUIRED,
                                      'not authorized yet, call login() first')
            if failed_access_token is not None and current.access_token != failed_access_token:
                # Already rotated by another thread. Compares token values rather than
                # timestamps: equal timestamps do not imply the same token.
                return current
            if not force and not current.needs_refresh(DEFAULT_REFRESH_AHEAD_MILLIS):
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
                # Preserve the existing refresh token when rotation omits a replacement.
                token.refresh_token = current.refresh_token
            self._persist(token)
            logger.info('oauth2 access token refreshed. client_id:%s', client_id)
            return token

    def _reusable_token(self):
        """Return a reusable local token, refreshing it when required.

        Returns None when interactive authorization is required.
        """
        existing = self._current_token()
        if existing is None or not existing.access_token:
            return None
        if not existing.needs_refresh(DEFAULT_REFRESH_AHEAD_MILLIS):
            return existing
        if existing.has_refresh_token():
            try:
                return self.refresh(existing.access_token)
            except OAuth2Exception as e:
                # Only terminal authorization errors require interactive authorization;
                # transient network and server errors remain retryable.
                if e.category != Category.REAUTHORIZATION_REQUIRED:
                    raise
                logger.info('refresh token no longer valid, re-authorizing')
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
        # A manual clientId was registered by hand with a concrete redirect_uri the SDK
        # cannot see, so both sides agree on this port; dynamic registration sends a
        # portless redirect_uri and can let the system assign one
        return DEFAULT_MANUAL_CALLBACK_PORT if self._explicit_client_id else 0

    def _scopes(self):
        scopes = self._resolved_scopes
        if scopes is not None:
            return scopes
        metadata = self._metadata_of()
        if not metadata.scopes_supported:
            # Missing scope metadata is rejected instead of inferring incomplete scopes.
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
        """Register a public client under RFC 7591.

        Registration omits scope. The granted scope set is stored separately so a wider
        requirement triggers re-registration instead of ``invalid_scope``.
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
            'client_name': CLIENT_NAME,
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
            client_name=CLIENT_NAME,
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
        """Poll the token endpoint according to RFC 8628 response semantics."""
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
