# -*- coding: utf-8 -*-
"""
OAuth2 support.

Typical use (dynamic registration, browser authorization)::

    from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2SessionManager
    from tigeropen.tiger_open_config import TigerOpenClientConfig

    sessions = OAuth2SessionManager()
    sessions.login_if_needed(lambda url: print('open in a browser:', url))

    config = TigerOpenClientConfig()
    config.authentication = OAuth2Authentication(sessions)

Port of ``com.tigerbrokers.stock.openapi.client.auth.oauth2``.
"""
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
