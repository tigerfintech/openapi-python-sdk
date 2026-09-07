# -*- coding: utf-8 -*-
"""
On-disk authorization state.

Layout::

    ~/.tiger/openapi/
      tokens/{clientId}.json      authorization state, 0600, cleared on logout
      clients/{issuerHash}.json   dynamically registered client_id, kept across logout

The two directories are keyed differently because ``clients/`` is looked up before a
clientId is known: find the clientId by issuer, then find the token by clientId.

Root directory precedence: explicit argument > ``TIGEROPEN_HOME`` > ``~/.tiger/openapi``.
Deliberately not the current working directory.

The file format matches the Java SDK, so both can share one directory.
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

_SAFE_CHARS = re.compile(r'[^a-zA-Z0-9\-_.]')


class OAuth2TokenStore:

    def __init__(self, home=None):
        if home:
            base = home
        else:
            base = os.environ.get(ENV_HOME) or DEFAULT_HOME
        self.home = os.path.abspath(os.path.expanduser(base))

    # ------------------------------------------------------------------ token

    def load_token(self, client_id, expected_issuer=None):
        """Load a token. A missing file or an issuer mismatch is a cache miss."""
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
                # Fail loudly rather than guess at the format
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
        """For logout: clears the authorization only, keeps the client_id."""
        if not client_id:
            return
        self._delete(self._token_file(client_id))

    # ----------------------------------------------------------- registration

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
        """Only when the authorization server says ``invalid_client``. Deleting it
        otherwise means registering a new client next time and leaving garbage behind."""
        if not issuer:
            return
        self._delete(self._client_file(issuer))

    # --------------------------------------------------------------- internal

    def _token_file(self, client_id):
        return os.path.join(self.home, 'tokens', _safe_file_name(client_id) + '.json')

    def _client_file(self, issuer):
        return os.path.join(self.home, 'clients', hash_issuer(issuer) + '.json')

    @staticmethod
    def _delete(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            logger.error('delete file fail:%s', path, exc_info=True)

    @staticmethod
    def _write_atomic(path, content):
        """Temp file in the same directory, then rename.

        Overwriting in place would leave a truncated JSON file if the process died
        mid-write. The temp file must share the directory: a cross-filesystem rename is
        not atomic.
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
    """The clientId comes from the server and may contain ``/`` or ``..``."""
    name = _SAFE_CHARS.sub('_', raw or '')
    while '..' in name:
        name = name.replace('..', '__')
    return name or '_'


def hash_issuer(issuer):
    """The issuer is a URL containing ``://`` and ``/``, so it is hashed for use as a
    filename. First 16 bytes of SHA-256 as hex, 32 characters -- same as the Java SDK,
    so both can share one directory."""
    return hashlib.sha256((issuer or '').encode('utf-8')).hexdigest()[:32]


def _restrict_file(path):
    """0600. Silently skipped on non-POSIX platforms."""
    try:
        os.chmod(path, 0o600)
    except Exception:
        logger.debug('restrict file permission skipped:%s', path)


def _restrict_directory(path):
    """0700. Silently skipped on non-POSIX platforms."""
    try:
        os.chmod(path, 0o700)
    except Exception:
        logger.debug('restrict directory permission skipped:%s', path)
