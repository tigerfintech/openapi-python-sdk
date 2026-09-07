# -*- coding: utf-8 -*-
"""
Authorization server metadata (RFC 8414).

Endpoints always come from metadata, never hardcoded, so switching environments only
means changing the issuer.
"""


class OAuth2Metadata:
    """Response of ``{issuer}/.well-known/oauth-authorization-server``."""

    def __init__(self, issuer=None, authorization_endpoint=None, token_endpoint=None,
                 registration_endpoint=None, device_authorization_endpoint=None,
                 scopes_supported=None):
        self.issuer = issuer
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        #: Absent means only a manually configured client_id can be used
        self.registration_endpoint = registration_endpoint
        #: Absent means this environment does not support the device flow
        self.device_authorization_endpoint = device_authorization_endpoint
        self.scopes_supported = scopes_supported or []

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            issuer=data.get('issuer'),
            authorization_endpoint=data.get('authorization_endpoint'),
            token_endpoint=data.get('token_endpoint'),
            registration_endpoint=data.get('registration_endpoint'),
            device_authorization_endpoint=data.get('device_authorization_endpoint'),
            scopes_supported=data.get('scopes_supported') or [],
        )

    def __repr__(self):
        return ('OAuth2Metadata{issuer=%s, authorization_endpoint=%s, token_endpoint=%s, '
                'registration_endpoint=%s, device_authorization_endpoint=%s, scopes_supported=%s}'
                % (self.issuer, self.authorization_endpoint, self.token_endpoint,
                   self.registration_endpoint, self.device_authorization_endpoint,
                   self.scopes_supported))
