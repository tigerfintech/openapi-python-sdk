# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import json

from tigeropen.common.consts import THREAD_LOCAL
from tigeropen.common.exceptions import RequestException, ResponseException

try:
    import httplib
except ImportError:
    import http.client as httplib
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus


def url_encode(params, charset):
    query_string = ""
    for (k, v) in params.items():
        value = v
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        value = quote_plus(value, encoding=charset)
        query_string += ("&" + k + "=" + value)
    query_string = query_string[1:]
    return query_string


def get_http_connection(url, query_string, timeout):
    url_parse_result = urlparse.urlparse(url)
    host = url_parse_result.hostname
    port = 80
    connection = httplib.HTTPConnection(host=host, port=port, timeout=timeout)
    if url.find("https") == 0:
        port = 443
        connection = httplib.HTTPSConnection(host=host, port=port, timeout=timeout)
    url = url_parse_result.scheme + "://" + url_parse_result.hostname
    if url_parse_result.port:
        url += url_parse_result.port
    url += url_parse_result.path
    if query_string:
        url += ('?' + query_string)
    return url, connection


def do_post(url, query_string=None, headers=None, params=None, timeout=15, charset=None):
    return do_request('POST', url=url, query_string=query_string, headers=headers, params=params, timeout=timeout,
                      charset=charset)


def do_get(url, query_string=None, headers=None, params=None, timeout=15, charset=None):
    return do_request('GET', url=url, query_string=query_string, headers=headers, params=params, timeout=timeout,
                      charset=charset)


def do_request(method, url, query_string=None, headers=None, params=None, timeout=15, charset=None):
    url, connection = get_http_connection(url, query_string, timeout)

    try:
        connection.connect()
    except Exception as e:
        raise RequestException('[' + THREAD_LOCAL.uuid + ']' + method + ' connect failed. url: ' + url
                               + ' params: ' + str(params) + ' detail: ' + str(e))
    try:
        connection.request(method, url, body=json.dumps(params), headers=headers)
    except Exception as e:
        raise RequestException('[' + THREAD_LOCAL.uuid + ']' + method + ' request failed. url: ' + url
                               + ' params: ' + str(params) + ' detail: ' + str(e))
    response = connection.getresponse()
    result = response.read()

    if response.status != 200:
        if charset:
            result = result.decode(charset)
        raise ResponseException('[' + THREAD_LOCAL.uuid + ']invalid http status ' + str(response.status) +
                                ',detail body:' + result + ' params: ' + str(params))
    try:
        response.close()
        connection.close()
    except Exception as e:
        pass
    return result
