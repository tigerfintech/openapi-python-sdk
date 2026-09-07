# -*- coding: utf-8 -*-
"""
Authentication abstractions.

Port of ``com.tigerbrokers.stock.openapi.client.auth``. Purely additive: code that
does not use this package behaves exactly as before.
"""
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
