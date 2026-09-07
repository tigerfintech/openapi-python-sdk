# -*- coding: utf-8 -*-
"""
How a request carries its credential.

The only data-plane abstraction, and it does three things: attach the credential
before sending, decide whether to swap credentials and retry after a 401, and release
resources. Authorization flows (login, dynamic registration, opening a browser) belong
to the control plane (``OAuth2SessionManager``), not here.

Implementations must be thread-safe.
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
        """Whether this request may be retried with a new credential after a 401.

        Named after the constraint rather than the business operation on purpose: an
        authentication implementation has no business knowing what an order is, it only
        needs to know whether it may send the request a second time.

        False for order placement, modification and cancellation -- a 401 does not prove
        the request was not executed, so a retry risks a duplicate order.
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
    """Snapshot of which credential a request used.

    Suppresses 401 storms. With N in-flight requests sharing a token that just expired,
    N 401s come back; without the snapshot each one triggers another refresh and the
    sequence never converges. With it, later 401s see the credential has already been
    rotated and retry with the new one directly.
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
        """The credential this request used (the raw access token in OAuth2 mode).

        For equality comparison only. Never log it, never expose it.
        """
        return self._credential

    def __repr__(self):
        """Never prints the credential value."""
        return 'AuthenticationAttempt{type=%s, credential=%s}' % (
            self._auth_type, '<none>' if self._credential is None else '***')


class RetryDecision:
    """Whether to retry after a 401.

    There is deliberately no "retry with the same credential" option: :meth:`retry`
    always carries a new full ``Authorization`` header value, including the ``Bearer ``
    prefix.
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
        """Decide what to do after a 401.

        Rules shared across language SDKs: refresh only for a 401 meaning "credential is
        invalid", never for 403, 5xx or a timeout; retry at most once per request for
        authentication reasons; retry only once a genuinely different credential is held.

        :param attempt: the snapshot returned by :meth:`apply`
        :param status_code: HTTP status received (Java passes an ``HttpResult``;
            Python has no equivalent type, so the status code is passed directly)
        :return: :class:`RetryDecision`
        """

    @abstractmethod
    def close(self):
        """Release resources. Must be called when switching authentication method."""
