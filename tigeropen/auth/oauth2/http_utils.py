# -*- coding: utf-8 -*-
"""
HTTP calls used by the OAuth2 flow.

``tigeropen.common.util.web_utils`` is not reused for two reasons: the token endpoint
needs form-encoded bodies (that one only sends JSON), and here we must be able to read
4xx response bodies -- that is where the OAuth2 errors live, and that one raises on any
non-200, discarding the body.
"""
import json
import logging
from urllib.parse import urlencode

import urllib3

from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception

logger = logging.getLogger(__name__)

#: Calls in the authorization flow are interactive, so the timeouts are generous.
#: Same values as the Java SDK.
CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 30

_JSON_CONTENT_TYPE = 'application/json; charset=utf-8'
_FORM_CONTENT_TYPE = 'application/x-www-form-urlencoded; charset=utf-8'

_http_pool = urllib3.PoolManager()
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
    """Post a form and return only the HTTP status, tolerating an empty body.

    Needed for RFC 7009 revocation: that endpoint answers 200 with **no body** on success,
    which :func:`post_form` rejects as "empty response". The caller only needs to know
    whether the server accepted it, so nothing is parsed.

    :return: the HTTP status code
    :raise OAuth2Exception: only on a connection failure
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
