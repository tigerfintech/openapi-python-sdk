# -*- coding: utf-8 -*-
"""Authentication interfaces shared by signature and OAuth 2.0 implementations."""
from tigeropen.auth.authentication import (
    Authentication,
    AuthenticationAttempt,
    AuthenticationType,
    RequestAuthContext,
    RetryDecision,
)

__all__ = [
    'Authentication',
    'AuthenticationAttempt',
    'AuthenticationType',
    'RequestAuthContext',
    'RetryDecision',
]
