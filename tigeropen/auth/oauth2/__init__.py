# -*- coding: utf-8 -*-
"""OAuth 2.0 authentication, authorization flows, and token persistence."""
from tigeropen.auth.oauth2.authentication import OAuth2Authentication
from tigeropen.auth.oauth2.client_registration import OAuth2ClientRegistration
from tigeropen.auth.oauth2.device_authorization import OAuth2DeviceAuthorization
from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception
from tigeropen.auth.oauth2.metadata import OAuth2Metadata
from tigeropen.auth.oauth2.session_manager import OAuth2SessionManager
from tigeropen.auth.oauth2.token import OAuth2Token
from tigeropen.auth.oauth2.token_store import OAuth2TokenStore

__all__ = [
    'Category',
    'OAuth2Authentication',
    'OAuth2ClientRegistration',
    'OAuth2DeviceAuthorization',
    'OAuth2Exception',
    'OAuth2Metadata',
    'OAuth2SessionManager',
    'OAuth2Token',
    'OAuth2TokenStore',
]
