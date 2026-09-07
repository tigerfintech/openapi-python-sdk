# -*- coding: utf-8 -*-
"""
Client obtained by dynamic registration (RFC 7591).

Stored separately from the token and **kept across logout**: the registered client_id
is this application's identity on this machine, while logging out only clears the
authorization. Deleting it would pile up a new client on the authorization server every
time the user logs back in.

``registered_scopes`` records the scope set granted at registration time. If the SDK
later needs a wider set, the stored registration no longer covers it and a new
registration is made, instead of reusing a client_id that would get ``invalid_scope``.
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
