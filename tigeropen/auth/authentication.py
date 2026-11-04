# -*- coding: utf-8 -*-
"""Thread-safe request authentication interfaces.

Implementations attach credentials, handle authentication retries, and release resources.
OAuth 2.0 authorization flows remain in ``OAuth2SessionManager``.
"""
from abc import ABCMeta, abstractmethod
from enum import Enum


class AuthenticationType(Enum):
    """Which kind of authentication."""

    #: tigerId + RSA private key signature
    SIGNATURE = 'SIGNATURE'
    #: ``Authorization: Bearer <access_token>``
    OAUTH2 = 'OAUTH2'


class RequestAuthContext:
    """Per-request authentication context.

    Business parameters (``method``, ``version``, ``biz_content``, ``timestamp``) are
    filled in by the client and must not be modified by an authentication implementation.
    """

    __slots__ = ('_params', '_retryable', '_authorization_header')

    def __init__(self, params, retryable=True):
        self._params = params
        self._retryable = retryable
        self._authorization_header = None

    @property
    def params(self):
        """Request body parameters. Read-only as far as authentication is concerned."""
        return self._params

    @property
    def retryable(self):
        """Whether a request may be retried with a new credential after a 401.

        Order placement, modification, and cancellation are not retryable because a 401
        does not prove that the operation was not executed.
        """
        return self._retryable

    @property
    def authorization_header(self):
        """Full ``Authorization`` header value; None means do not send the header."""
        return self._authorization_header

    @authorization_header.setter
    def authorization_header(self, value):
        self._authorization_header = value


class AuthenticationAttempt:
    """Credential snapshot used to coordinate authentication retries.

    Comparing the failed credential with current state detects rotation completed by
    another thread and avoids duplicate refresh requests.
    """

    __slots__ = ('_auth_type', '_credential')

    def __init__(self, auth_type, credential):
        self._auth_type = auth_type
        self._credential = credential

    @property
    def auth_type(self):
        return self._auth_type

    @property
    def credential(self):
        """Credential used by the request, including a raw OAuth 2.0 access token.

        This value is restricted to equality comparisons and must not be logged or
        exposed.
        """
        return self._credential

    def __repr__(self):
        """Never prints the credential value."""
        return 'AuthenticationAttempt{type=%s, credential=%s}' % (
            self._auth_type, '<none>' if self._credential is None else '***')


class RetryDecision:
    """Authentication retry decision.

    A retry always supplies a new full ``Authorization`` header value, including the
    ``Bearer `` prefix.
    """

    __slots__ = ('_should_retry', '_authorization_header')

    def __init__(self, should_retry, authorization_header):
        self._should_retry = should_retry
        self._authorization_header = authorization_header

    @staticmethod
    def no_retry():
        return _NO_RETRY

    @staticmethod
    def retry(authorization_header):
        """:param authorization_header: full new header value, including ``Bearer ``"""
        return RetryDecision(True, authorization_header)

    @property
    def should_retry(self):
        return self._should_retry

    @property
    def authorization_header(self):
        return self._authorization_header

    def __repr__(self):
        """Never prints the header value."""
        return 'RetryDecision{should_retry=%s}' % self._should_retry


_NO_RETRY = RetryDecision(False, None)


class Authentication(metaclass=ABCMeta):
    """Authentication interface. Implementations must be thread-safe."""

    @property
    @abstractmethod
    def auth_type(self):
        """Which kind of authentication. For logging and assertions; business logic
        should not branch on it."""

    @abstractmethod
    def apply(self, context):
        """Write the credential into the request and return a snapshot of which
        credential was used.

        The OAuth2 implementation may refresh synchronously here, so it may raise
        :class:`~tigeropen.auth.oauth2.exceptions.OAuth2Exception`.

        :param context: :class:`RequestAuthContext`
        :return: :class:`AuthenticationAttempt`, passed back to :meth:`on_unauthorized`
        """

    @abstractmethod
    def on_unauthorized(self, attempt, status_code):
        """Return the retry decision for an unauthorized response.

        Refresh applies only to HTTP 401 credential failures, never to HTTP 403, server
        errors, or timeouts. Authentication retries occur at most once per request and
        require a different credential.

        :param attempt: credential snapshot returned by :meth:`apply`
        :param status_code: HTTP response status
        :return: :class:`RetryDecision`
        """

    @abstractmethod
    def close(self):
        """Release resources. Must be called when switching authentication method."""
