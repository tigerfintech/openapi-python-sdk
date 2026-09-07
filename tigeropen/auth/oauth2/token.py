# -*- coding: utf-8 -*-
"""
Stored authorization state.

``issuer`` and ``client_id`` are recorded because the filename only carries the
clientId: after switching environments a missing issuer check would send a staging
token to production, showing up as an inexplicable 401.

Field names match the Java SDK's on-disk format, so both can read the same file.
"""
import time

#: On-disk format version. An unrecognised version is an error, not a guess.
SCHEMA_VERSION = 1


def current_millis():
    return int(time.time() * 1000)


class OAuth2Token:
    """An access token and its metadata."""

    def __init__(self, issuer=None, client_id=None, access_token=None, refresh_token=None,
                 token_type='Bearer', scope=None, expires_at=0, schema_version=SCHEMA_VERSION):
        self.schema_version = schema_version
        self.issuer = issuer
        self.client_id = client_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.scope = scope
        #: Absolute expiry as epoch millis, not expires_in
        self.expires_at = expires_at

    def remaining_millis(self):
        """Time until expiry; negative once already expired."""
        return self.expires_at - current_millis()

    def needs_refresh(self, ahead_millis):
        """
        :param ahead_millis: how early to refresh. The window exists because time passes
            between sending a request and the server validating it, so using a token
            right up to its expiry produces intermittent 401s
        """
        return self.remaining_millis() <= ahead_millis

    def has_refresh_token(self):
        return bool(self.refresh_token)

    def to_dict(self):
        return {
            'schema_version': self.schema_version,
            'issuer': self.issuer,
            'client_id': self.client_id,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'scope': self.scope,
            'expires_at': self.expires_at,
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            schema_version=data.get('schema_version', SCHEMA_VERSION),
            issuer=data.get('issuer'),
            client_id=data.get('client_id'),
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_type=data.get('token_type') or 'Bearer',
            scope=data.get('scope'),
            expires_at=data.get('expires_at') or 0,
        )

    def __repr__(self):
        """Prints no token values."""
        return ('OAuth2Token{client_id=%s, issuer=%s, scope=%s, expires_at=%s, has_refresh_token=%s}'
                % (self.client_id, self.issuer, self.scope, self.expires_at, self.has_refresh_token()))
