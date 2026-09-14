# -*- coding: utf-8 -*-
"""File-backed OAuth 2.0 authorization state.

Storage layout::

    ~/.tiger/openapi/
      tokens/{clientId}.json                authorization state, mode 0600, removed on logout
      clients/{issuerHash}-{surface}.json   dynamic registration, retained across logout

Registration files are keyed by issuer because the client ID is not yet available during
lookup, and by surface so that each entry point registers its own client. Without the
surface, whichever entry point ran first would own the registration and every other one
would silently inherit its identity: one name on the user's authorization page, one
revocation switch for all of them, and one shared token file whose refresh-token rotation
they would race over.

Token files need no surface: each surface registers a distinct client ID, so their token
files are already distinct. A manually configured client ID is shared on purpose -- one
client ID means one application.

Storage root precedence is: explicit argument, ``TIGEROPEN_HOME``, then
``~/.tiger/openapi``. The format is compatible with the Java SDK.
"""
import hashlib
import json
import logging
import os
import re
import tempfile

from tigeropen.auth.oauth2.client_registration import OAuth2ClientRegistration
from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception
from tigeropen.auth.oauth2.token import SCHEMA_VERSION, OAuth2Token

logger = logging.getLogger(__name__)

ENV_HOME = 'TIGEROPEN_HOME'
DEFAULT_HOME = os.path.join('~', '.tiger', 'openapi')

#: Entry point owning a registration. The CLI and the MCP server are built on this SDK and
#: must pass their own value, otherwise they would be filed as the Python SDK and share its
#: client. Keep in step with the Java SDK's ``sdk-java``.
DEFAULT_SURFACE = 'sdk-python'

_SAFE_CHARS = re.compile(r'[^a-zA-Z0-9\-_.]')
#: Surfaces become part of a file name, so they are restricted rather than sanitised: a
#: silently rewritten surface would file two entry points under one name.
_SURFACE_PATTERN = re.compile(r'^[a-z0-9][a-z0-9-]*$')


class OAuth2TokenStore:

    def __init__(self, home=None, surface=DEFAULT_SURFACE):
        """
        :param home: storage root; defaults to ``TIGEROPEN_HOME`` then ``~/.tiger/openapi``
        :param surface: entry point owning the registration, e.g. ``sdk-python``, ``cli``,
            ``mcp``. Lowercase alphanumerics and hyphens only
        """
        if home:
            base = home
        else:
            base = os.environ.get(ENV_HOME) or DEFAULT_HOME
        self.home = os.path.abspath(os.path.expanduser(base))
        self.surface = _validate_surface(surface)

    def load_token(self, client_id, expected_issuer=None):
        """Load a token, treating a missing file or issuer mismatch as a cache miss."""
        path = self._token_file(client_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            token = OAuth2Token.from_dict(data)
            if token is None:
                return None
            if token.schema_version != SCHEMA_VERSION:
                # Unknown schema versions are not interpreted.
                raise OAuth2Exception(Category.STORAGE_FAILED,
                                      'unsupported token schema_version: %s' % token.schema_version)
            if expected_issuer is not None and expected_issuer != token.issuer:
                logger.info('token issuer mismatch, treat as cache miss. client_id:%s', client_id)
                return None
            return token
        except OAuth2Exception:
            raise
        except Exception:
            logger.error('read token file fail:%s', path, exc_info=True)
            return None

    def save_token(self, token):
        if token is None or not token.client_id:
            raise OAuth2Exception(Category.STORAGE_FAILED, 'token or client_id is empty, cannot save')
        path = self._token_file(token.client_id)
        self._write_atomic(path, json.dumps(token.to_dict(), ensure_ascii=False, indent=2))

    def delete_token(self, client_id):
        """Delete authorization state while retaining client registration."""
        if not client_id:
            return
        self._delete(self._token_file(client_id))

    def load_client_id(self, issuer):
        registration = self.load_client_registration(issuer)
        return registration.client_id if registration else None

    def load_client_registration(self, issuer):
        path = self._client_file(issuer)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return OAuth2ClientRegistration.from_dict(json.load(f))
        except Exception:
            logger.error('read client registration file fail:%s', path, exc_info=True)
            return None

    def save_client_registration(self, registration):
        if registration is None or not registration.issuer:
            raise OAuth2Exception(Category.STORAGE_FAILED, 'registration or issuer is empty, cannot save')
        path = self._client_file(registration.issuer)
        self._write_atomic(path, json.dumps(registration.to_dict(), ensure_ascii=False, indent=2))

    def delete_client_registration(self, issuer):
        """Delete registration state after an ``invalid_client`` response."""
        if not issuer:
            return
        self._delete(self._client_file(issuer))

    def _token_file(self, client_id):
        return os.path.join(self.home, 'tokens', _safe_file_name(client_id) + '.json')

    def _client_file(self, issuer):
        return os.path.join(self.home, 'clients',
                            '%s-%s.json' % (hash_issuer(issuer), self.surface))

    @staticmethod
    def _delete(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            logger.error('delete file fail:%s', path, exc_info=True)

    @staticmethod
    def _write_atomic(path, content):
        """Atomically replace a file through a same-directory temporary file.

        Same-filesystem replacement prevents partial JSON writes. Directories and files
        are restricted to modes 0700 and 0600 where supported.
        """
        directory = os.path.dirname(path)
        try:
            os.makedirs(directory, exist_ok=True)
            _restrict_directory(directory)
            fd, tmp_path = tempfile.mkstemp(dir=directory, prefix='.tmp-', suffix='.json')
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(content)
                _restrict_file(tmp_path)
                os.replace(tmp_path, path)
            except Exception:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
                raise
            _restrict_file(path)
        except Exception as e:
            raise OAuth2Exception(Category.STORAGE_FAILED, 'write file fail: ' + path, e)


def _safe_file_name(raw):
    """Sanitize an untrusted client ID for use as a file name."""
    name = _SAFE_CHARS.sub('_', raw or '')
    while '..' in name:
        name = name.replace('..', '__')
    return name or '_'


def _validate_surface(surface):
    """Reject a surface that cannot be used verbatim as part of a file name."""
    if not surface or not _SURFACE_PATTERN.match(surface):
        raise OAuth2Exception(
            Category.STORAGE_FAILED,
            "invalid surface %r: expected lowercase alphanumerics and hyphens, e.g. 'cli'"
            % (surface,))
    return surface


def hash_issuer(issuer):
    """Return the Java-compatible 32-character SHA-256 issuer file key."""
    return hashlib.sha256((issuer or '').encode('utf-8')).hexdigest()[:32]


def _restrict_file(path):
    """Restrict a credential file to mode 0600 where supported."""
    try:
        os.chmod(path, 0o600)
    except Exception:
        logger.debug('restrict file permission skipped:%s', path)


def _restrict_directory(path):
    """Restrict a credential directory to mode 0700 where supported."""
    try:
        os.chmod(path, 0o700)
    except Exception:
        logger.debug('restrict directory permission skipped:%s', path)
