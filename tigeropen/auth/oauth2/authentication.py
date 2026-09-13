# -*- coding: utf-8 -*-
"""Request authentication backed by an OAuth 2.0 session manager."""
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
        """Attach a Bearer token to the request context.

        Near-expiry refreshes use the session manager's single-flight synchronization.
        Missing authorization raises ``REAUTHORIZATION_REQUIRED`` without starting an
        implicit browser flow.
        """
        access_token = self._sessions.get_access_token()
        context.authorization_header = BEARER_PREFIX + access_token
        return AuthenticationAttempt(AuthenticationType.OAUTH2, access_token)

    def on_unauthorized(self, attempt, status_code):
        """Process HTTP 401 responses.

        HTTP 403 indicates insufficient permission and cannot be resolved by refreshing
        a token with the same scope. Server errors and timeouts are not credential
        failures.
        """
        if status_code != UNAUTHORIZED_STATUS:
            return RetryDecision.no_retry()
        credential = attempt.credential if attempt is not None else None
        try:
            # Reuse a token already rotated by another thread without another token request.
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
