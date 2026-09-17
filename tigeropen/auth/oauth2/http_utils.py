# -*- coding: utf-8 -*-
"""HTTP helpers for OAuth 2.0 JSON and form-encoded requests.

OAuth error responses retain 4xx response bodies for protocol-level error handling.
"""
import json
import logging
from urllib.parse import urlencode

import urllib3

from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception

logger = logging.getLogger(__name__)

#: Every call here is a small JSON exchange with the authorization server, so a request that
#: has not answered in this long is not going to. Same values as the Java SDK.
CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 10

_JSON_CONTENT_TYPE = 'application/json; charset=utf-8'
_FORM_CONTENT_TYPE = 'application/x-www-form-urlencoded; charset=utf-8'

#: Certificate verification is stated rather than inherited. These calls carry the refresh
#: token, which stays valid for weeks, so the posture must not depend on which urllib3
#: version happens to be installed.
_http_pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
_timeout = urllib3.Timeout(connect=CONNECT_TIMEOUT_SECONDS, read=READ_TIMEOUT_SECONDS)


def get_json(url):
    return _execute('GET', url, body=None, content_type=None)


def post_json(url, payload):
    body = json.dumps(payload).encode('utf-8')
    return _execute('POST', url, body=body, content_type=_JSON_CONTENT_TYPE)


def post_form(url, form):
    """Send a form-encoded body. Fields whose value is None are skipped."""
    fields = [(k, v) for k, v in form.items() if v is not None]
    body = urlencode(fields).encode('utf-8')
    return _execute('POST', url, body=body, content_type=_FORM_CONTENT_TYPE)


def post_form_for_status(url, form):
    """Post a form and return the HTTP status without requiring a response body.

    RFC 7009 revocation returns an empty success body, so no parsing is performed.

    :return: the HTTP status code
    :raise OAuth2Exception: on connection failure
    """
    fields = [(k, v) for k, v in form.items() if v is not None]
    body = urlencode(fields).encode('utf-8')
    headers = {'Accept': 'application/json', 'Content-Type': _FORM_CONTENT_TYPE}
    try:
        response = _http_pool.request('POST', url, body=body, headers=headers, timeout=_timeout)
    except Exception as e:
        raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED, 'request fail: ' + url, e)
    return response.status


def _execute(method, url, body, content_type):
    """Send the request and parse the response body as a dict.

    A 4xx returns its body instead of raising: OAuth2 errors (``invalid_grant``,
    ``authorization_pending`` and friends) live in the 4xx body, and the caller needs the
    ``error`` field to tell "wait and retry" from "re-authorize". Only a connection
    failure or a non-JSON response raises.
    """
    headers = {'Accept': 'application/json'}
    if content_type:
        headers['Content-Type'] = content_type
    try:
        response = _http_pool.request(method, url, body=body, headers=headers, timeout=_timeout)
    except Exception as e:
        raise OAuth2Exception(Category.METADATA_UNAVAILABLE, 'request fail: ' + url, e)

    try:
        text = response.data.decode('utf-8') if response.data else ''
    except Exception as e:
        raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED,
                              'cannot decode response from %s, http status %s' % (url, response.status), e)
    if not text:
        raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED,
                              'empty response from %s, http status %s' % (url, response.status))
    try:
        parsed = json.loads(text)
    except Exception as e:
        raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED,
                              'non-JSON response from %s, http status %s' % (url, response.status), e)
    if not isinstance(parsed, dict):
        raise OAuth2Exception(Category.TOKEN_REQUEST_FAILED,
                              'unexpected response from %s, http status %s' % (url, response.status))
    return parsed
