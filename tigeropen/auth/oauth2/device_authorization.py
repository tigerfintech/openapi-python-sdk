# -*- coding: utf-8 -*-
"""Device authorization response (RFC 8628)."""

#: Default polling interval per RFC 8628 §3.5. Tiger's authorization server does not
#: return ``interval``, so this default applies in practice.
DEFAULT_INTERVAL_SECONDS = 5


class OAuth2DeviceAuthorization:

    def __init__(self, device_code=None, user_code=None, verification_uri=None,
                 verification_uri_complete=None, expires_in=0, interval=0):
        #: Credential used to redeem the token; it must not be displayed or logged.
        self.device_code = device_code
        #: Short code presented to the resource owner.
        self.user_code = user_code
        #: Verification URI presented to the resource owner.
        self.verification_uri = verification_uri
        #: Verification URI with the user code included.
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
