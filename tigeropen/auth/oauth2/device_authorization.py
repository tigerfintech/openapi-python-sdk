# -*- coding: utf-8 -*-
"""Device authorization response (RFC 8628)."""

#: Default polling interval per RFC 8628 §3.5. Tiger's authorization server does not
#: return ``interval``, so this default applies in practice.
DEFAULT_INTERVAL_SECONDS = 5


class OAuth2DeviceAuthorization:

    def __init__(self, device_code=None, user_code=None, verification_uri=None,
                 verification_uri_complete=None, expires_in=0, interval=0):
        #: Credential used to redeem the token. Never display it, never log it --
        #: holding it is equivalent to holding the result of this authorization.
        #: Show the user ``user_code`` instead.
        self.device_code = device_code
        #: Short code for the user to enter
        self.user_code = user_code
        #: Verification page for the user to open
        self.verification_uri = verification_uri
        #: Verification page with the code pre-filled; prefer it when present
        self.verification_uri_complete = verification_uri_complete
        self.expires_in = expires_in
        #: Polling interval in seconds; 0 means the server sent none
        self.interval = interval

    def effective_interval(self):
        return self.interval if self.interval and self.interval > 0 else DEFAULT_INTERVAL_SECONDS

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            device_code=data.get('device_code'),
            user_code=data.get('user_code'),
            verification_uri=data.get('verification_uri'),
            verification_uri_complete=data.get('verification_uri_complete'),
            expires_in=data.get('expires_in') or 0,
            interval=data.get('interval') or 0,
        )

    def __repr__(self):
        """Prints no device_code."""
        return ('OAuth2DeviceAuthorization{user_code=%s, verification_uri=%s, expires_in=%s, '
                'interval=%s}'
                % (self.user_code, self.verification_uri, self.expires_in, self.interval))
