# -*- coding: utf-8 -*-
"""
OAuth2 errors.

Carries a :class:`Category` rather than an error-code string because the only
distinctions a caller acts on are "retry", "re-authorize" and "fix your config". The
raw error returned by the authorization server goes in the message for diagnosis.
"""
from enum import Enum


class Category(Enum):
    """Error category. Each one implies a different action."""

    #: Cannot fetch authorization server metadata: wrong address, service down, no network
    METADATA_UNAVAILABLE = 'METADATA_UNAVAILABLE'
    #: No usable client_id, and automatic registration is not possible
    CLIENT_REGISTRATION_REQUIRED = 'CLIENT_REGISTRATION_REQUIRED'
    #: Callback stage failed: timeout, user denial, or state mismatch
    CALLBACK_FAILED = 'CALLBACK_FAILED'
    #: Device flow not approved in time, or explicitly denied. Kept separate from
    #: REAUTHORIZATION_REQUIRED because only a new device authorization is needed --
    #: the stored token was not touched
    DEVICE_AUTHORIZATION_FAILED = 'DEVICE_AUTHORIZATION_FAILED'
    #: refresh_token expired, revoked, or never obtained. Retrying is pointless
    REAUTHORIZATION_REQUIRED = 'REAUTHORIZATION_REQUIRED'
    #: Token endpoint call failed, and not in the terminal way above
    TOKEN_REQUEST_FAILED = 'TOKEN_REQUEST_FAILED'
    #: Reading or writing the local token file failed
    STORAGE_FAILED = 'STORAGE_FAILED'


class OAuth2Exception(Exception):
    """Raised by any stage of the OAuth2 flow."""

    #: Mirrors the Java ``OAuth2Exception.Category`` spelling
    Category = Category

    def __init__(self, category, message, cause=None):
        super(OAuth2Exception, self).__init__(message)
        self.category = category
        self.message = message
        self.cause = cause

    @property
    def reauthorization_required(self):
        return self.category == Category.REAUTHORIZATION_REQUIRED

    def __str__(self):
        return 'OAuth2Exception{%s: %s}' % (self.category.name, self.message)
