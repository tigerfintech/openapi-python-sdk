# -*- coding: utf-8 -*-
"""
Shared OAuth2 helpers for the CLI.

Pulls together the pieces a CLI command needs to run in OAuth2 mode: building a
session manager and attaching it to a client config.
"""
from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2SessionManager

#: Environment variable for a manually registered clientId (dynamic registration otherwise)
TIGEROPEN_CLIENT_ID = 'TIGEROPEN_CLIENT_ID'

#: Entry point that owns the CLI's dynamic client registration.
#:
#: The CLI is a separate application from the SDK as far as the user is concerned: it gets
#: its own entry on the authorization page and can be revoked on its own. Leaving this at the
#: SDK default would file both under one registration, so one clientId and one token would be
#: shared and revoking either would take down both.
SURFACE = 'cli'


def build_session_manager(issuer=None, client_id=None):
    """Build an OAuth2SessionManager. Sends no requests, so it works offline."""
    return OAuth2SessionManager(
        issuer=issuer,
        client_id=client_id,
        surface=SURFACE,
    )


def attach_oauth2(config, sessions):
    """Attach OAuth2 authentication to a client config.

    In OAuth2 mode the private key plays no part at all. It is cleared here so a
    pre-existing signature config (props with ``private_key_pk8``) cannot leak a
    key into a session that never signs; nothing in the request path reads it, and
    leaving it in place would only mislead anyone inspecting the config.
    """
    config.authentication = OAuth2Authentication(sessions)
    config.private_key = ''
    config.tiger_id = ''
    return config
