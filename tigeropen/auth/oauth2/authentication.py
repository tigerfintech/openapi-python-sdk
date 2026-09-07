# -*- coding: utf-8 -*-
"""
Adapter connecting an OAuth2 session to the data plane.

A thin layer: the real work lives in
:class:`~tigeropen.auth.oauth2.session_manager.OAuth2SessionManager`. This only decides
how each request carries the credential and what to do after a 401.
"""
import logging

from tigeropen.auth.authentication import (
    Authentication,
    AuthenticationAttempt,
    AuthenticationType,
    RetryDecision,
)
from tigeropen.auth.oauth2.exceptions import OAuth2Exception

logger = logging.getLogger(__name__)

BEARER_PREFIX = 'Bearer '

UNAUTHORIZED_STATUS = 401


class OAuth2Authentication(Authentication):
    """Authenticate with an OAuth2 access token.

    Thread-safe: all state lives in the session manager, which has its own locking.
    """

    def __init__(self, session_manager):
        if session_manager is None:
            raise ValueError('OAuth2SessionManager is required')
        self._sessions = session_manager

    @property
    def auth_type(self):
        return AuthenticationType.OAUTH2

    @property
    def session_manager(self):
        return self._sessions

    def apply(self, context):
        """Set ``Authorization: Bearer <token>`` on the context.

        Refreshes synchronously if the token is close to expiry (single-flight, so
        concurrent requests do not hammer the token endpoint). Raises
        ``REAUTHORIZATION_REQUIRED`` if authorization never happened; it never opens a
        browser implicitly.
        """
        access_token = self._sessions.get_access_token()
        context.authorization_header = BEARER_PREFIX + access_token
        return AuthenticationAttempt(AuthenticationType.OAUTH2, access_token)

    def on_unauthorized(self, attempt, status_code):
        """Handle 401 only.

        A 403 means insufficient permission (scope too narrow, account not granted, or
        the endpoint is closed to OAuth2 entirely); a refresh returns the same scope, so
        the retry is guaranteed to be another 403 and is pure waste. 5xx and timeouts
        have nothing to do with the credential.
        """
        if status_code != UNAUTHORIZED_STATUS:
            return RetryDecision.no_retry()
        credential = attempt.credential if attempt is not None else None
        try:
            # Pass the token we just used: if another thread already rotated it, this
            # returns the new one without hitting the token endpoint again
            refreshed = self._sessions.refresh_after_unauthorized(credential)
            if refreshed is None or not refreshed.access_token:
                return RetryDecision.no_retry()
            if credential is not None and refreshed.access_token == credential:
                # Credential unchanged, so a retry would get the same 401
                logger.warning('oauth2 got 401 but access token unchanged after refresh, no retry')
                return RetryDecision.no_retry()
            logger.info('oauth2 access token refreshed after 401, retrying once')
            return RetryDecision.retry(BEARER_PREFIX + refreshed.access_token)
        except OAuth2Exception as e:
            logger.warning('oauth2 refresh after 401 failed:%s, re-authorization required', e.message)
            return RetryDecision.no_retry()
        except Exception as e:
            logger.warning('oauth2 refresh after 401 error:%s', e)
            return RetryDecision.no_retry()

    def close(self):
        """The session is owned by the application and may still be in use, so it is
        not closed here."""
        pass
