# -*- coding: utf-8 -*-
"""OAuth 2.0 dynamic client registration state (RFC 7591).

Registration state is stored separately from tokens and retained across logout.
``registered_scopes`` records the granted scope set; scope expansion requires a new
registration to avoid ``invalid_scope``.
"""


class OAuth2ClientRegistration:

    def __init__(self, issuer=None, client_id=None, client_name=None,
                 registered_scopes=None, client_id_issued_at=0):
        self.issuer = issuer
        self.client_id = client_id
        self.client_name = client_name
        self.registered_scopes = registered_scopes
        self.client_id_issued_at = client_id_issued_at

    def to_dict(self):
        return {
            'issuer': self.issuer,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'registered_scopes': self.registered_scopes,
            'client_id_issued_at': self.client_id_issued_at,
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            issuer=data.get('issuer'),
            client_id=data.get('client_id'),
            client_name=data.get('client_name'),
            registered_scopes=data.get('registered_scopes'),
            client_id_issued_at=data.get('client_id_issued_at') or 0,
        )

    def __repr__(self):
        return ('OAuth2ClientRegistration{issuer=%s, client_id=%s, client_name=%s, '
                'registered_scopes=%s}'
                % (self.issuer, self.client_id, self.client_name, self.registered_scopes))
