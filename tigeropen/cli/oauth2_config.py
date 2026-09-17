# -*- coding: utf-8 -*-
"""
Shared OAuth2 helpers for the CLI.

Pulls together the pieces a CLI command needs to run in OAuth2 mode: building a
session manager and attaching it to a client config.
"""
import glob
import json
import logging
import os

from tigeropen.auth.oauth2 import OAuth2Authentication, OAuth2SessionManager
from tigeropen.auth.oauth2.token_store import OAuth2TokenStore

logger = logging.getLogger(__name__)

#: Entry point that owns the CLI's dynamic client registration.
#:
#: The CLI is a separate application from the SDK as far as the user is concerned: it gets
#: its own entry on the authorization page and can be revoked on its own. Leaving this at the
#: SDK default would file both under one registration, so one clientId and one token would be
#: shared and revoking either would take down both.
SURFACE = 'cli'

#: Application name shown on the user's authorization page. The CLI is what the user
#: authorized, so this is the name they must see there and recognise when revoking.
CLIENT_NAME = 'Tiger OpenAPI CLI'


def build_session_manager(issuer=None, client_id=None):
    """Build an OAuth2SessionManager. Sends no requests, so it works offline."""
    return OAuth2SessionManager(
        issuer=issuer,
        client_id=client_id,
        surface=SURFACE,
        client_name=CLIENT_NAME,
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


def remove_stored_credentials(issuer=None, client_id=None):
    """Delete the CLI's stored OAuth2 credentials, and only the CLI's.

    The store root is shared by every entry point: ``clients/`` holds one registration per
    surface and ``tokens/`` is keyed by clientId alone, so the Java SDK's and the Python
    SDK's authorizations sit in the same two directories. Deleting the root would take
    those with it, so files are selected by surface and the root is never removed.

    Server-side revocation is attempted first. A token that is only deleted locally stays
    valid until it expires, so revoking is the part that actually ends the authorization;
    it needs the network, and failing it must not stop the local cleanup.

    :param issuer: authorization server to revoke against; defaults to the built-in one
    :param client_id: manually configured clientId, which has no registration file to be
        found through
    :return: tuple of (revoked on the server, list of removed paths)
    """
    revoked = _revoke_quietly(issuer, client_id)

    store = OAuth2TokenStore(surface=SURFACE)
    registrations = _cli_registrations(store.home)

    client_ids = {reg['client_id'] for reg in registrations if reg['client_id']}
    if client_id:
        client_ids.add(client_id)

    removed = []
    for cid in sorted(client_ids):
        path = os.path.join(store.home, 'tokens', cid + '.json')
        if os.path.exists(path):
            store.delete_token(cid)
            removed.append(path)
    for reg in registrations:
        os.remove(reg['path'])
        removed.append(reg['path'])
    return revoked, removed


def _cli_registrations(home):
    """Every registration filed under this surface, with its clientId.

    The clientId is read before anything is deleted: it is the only link from a
    registration to its token file.
    """
    found = []
    for path in sorted(glob.glob(os.path.join(home, 'clients', '*-%s.json' % SURFACE))):
        entry = {'path': path, 'client_id': None}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                entry['client_id'] = json.load(f).get('client_id')
        except Exception as e:
            # An unreadable registration is still ours to delete; only its token cannot be
            # located through it.
            logger.debug('cannot read client registration %s: %s', path, e, exc_info=True)
        found.append(entry)
    return found


def _revoke_quietly(issuer, client_id):
    """Revoke on the server, reporting failure instead of raising.

    :return: True when the server confirmed revocation
    """
    try:
        return build_session_manager(issuer=issuer, client_id=client_id).logout()
    except Exception as e:
        logger.debug('server-side revocation failed: %s', e, exc_info=True)
        return False
