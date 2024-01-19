# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import json

from tigeropen.common.consts import THREAD_LOCAL
from tigeropen.common.exceptions import RequestException, ResponseException
from urllib3 import PoolManager

http_pool = PoolManager()


def do_post(url, query_string=None, headers=None, params=None, timeout=15, charset=None):
    return do_request('POST', url=url, query_string=query_string, headers=headers, params=params, timeout=timeout,
                      charset=charset)


def do_get(url, query_string=None, headers=None, params=None, timeout=15, charset=None):
    return do_request('GET', url=url, query_string=query_string, headers=headers, params=params, timeout=timeout,
                      charset=charset)


def do_request(method, url, query_string=None, headers=None, params=None, timeout=15, charset=None):
    try:
        response = http_pool.request(method, url=url, fields=query_string, body=json.dumps(params), headers=headers,
                                     timeout=timeout,
                                     )
    except Exception as e:
        raise RequestException('[' + THREAD_LOCAL.uuid + ']' + method + ' request failed. url: ' + url
                               + ' headers: ' + str(headers)
                               + ' params: ' + str(params) + ' detail: ' + str(e))
    if response.status != 200:
        raise ResponseException('[' + THREAD_LOCAL.uuid + ']invalid http status ' + str(response.status) +
                                ' headers: ' + str(headers) +
                                ' detail body:' + str(response.data) + ' params: ' + str(params))
    return response.data
