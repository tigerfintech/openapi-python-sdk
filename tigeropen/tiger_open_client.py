# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import datetime
import json
import uuid

from tigeropen import __VERSION__
from tigeropen.common.consts import OPEN_API_SERVICE_VERSION, THREAD_LOCAL
from tigeropen.common.consts.params import P_TIMESTAMP, P_TIGER_ID, P_METHOD, P_CHARSET, P_VERSION, P_SIGN_TYPE, \
    P_DEVICE_ID, P_NOTIFY_URL, COMMON_PARAM_KEYS, P_SIGN
from tigeropen.common.exceptions import ResponseException, RequestException
from tigeropen.common.util.common_utils import has_value
from tigeropen.common.util.signature_utils import get_sign_content, sign_with_rsa, verify_with_rsa
from tigeropen.common.util.web_utils import do_post

try:
    from getmac import get_mac_address
except ImportError:
    def get_mac_address():
        return ':'.join(("%012x" % uuid.getnode())[i:i + 2] for i in range(0, 12, 2))


class TigerOpenClient:
    """
    client_config：客户端配置，包含tiger_id、应用私钥、老虎公钥等
    logger：日志对象，客户端执行信息会通过此日志对象输出
    """

    def __init__(self, client_config, logger=None):
        self.__config = client_config
        self.__logger = logger
        self.__headers = {
            'Content-type': 'application/json;charset=' + self.__config.charset,
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive",
            "User-Agent": 'openapi-python-sdk-' + __VERSION__
        }
        self.__device_id = self.__get_device_id()

    """
    内部方法，从params中抽取公共参数
    """

    def __get_common_params(self, params):
        common_params = dict()
        common_params[P_TIMESTAMP] = params[P_TIMESTAMP]
        common_params[P_TIGER_ID] = self.__config.tiger_id
        common_params[P_METHOD] = params[P_METHOD]
        common_params[P_CHARSET] = self.__config.charset
        common_params[P_VERSION] = params[P_VERSION] if params.get(P_VERSION) is not None else OPEN_API_SERVICE_VERSION
        common_params[P_SIGN_TYPE] = self.__config.sign_type
        common_params[P_DEVICE_ID] = self.__device_id
        if has_value(params, P_NOTIFY_URL):
            common_params[P_NOTIFY_URL] = params[P_NOTIFY_URL]
        return common_params

    @staticmethod
    def __get_device_id():
        """
        获取mac地址作为device_id
        :return:
        """
        try:
            return get_mac_address()
        except:
            return None

    """
    内部方法，从params中移除公共参数
    """
    def __remove_common_params(self, params):
        if not params:
            return
        for k in COMMON_PARAM_KEYS:
            if k in params:
                params.pop(k)

    """
    内部方法，通过请求request对象构造请求查询字符串和业务参数
    """
    def __prepare_request(self, request):
        THREAD_LOCAL.logger = self.__logger
        params = request.get_params()
        params[P_TIMESTAMP] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        common_params = self.__get_common_params(params)
        all_params = dict()
        all_params.update(params)
        all_params.update(common_params)
        sign_content = get_sign_content(all_params)
        try:
            sign = sign_with_rsa(self.__config.private_key, sign_content, self.__config.charset)
        except Exception as e:
            raise RequestException('[' + THREAD_LOCAL.uuid + ']request sign failed. ' + str(e))
        all_params[P_SIGN] = sign

        log_url = self.__config.server_url + '?' + sign_content + "&sign=" + sign
        if THREAD_LOCAL.logger:
            THREAD_LOCAL.logger.debug('[' + THREAD_LOCAL.uuid + ']request:' + log_url)

        return all_params

    """
    内部方法，解析请求返回结果并做验签
    """

    def __parse_response(self, response_str, timestamp=None):
        response_str = response_str.decode(self.__config.charset)
        if THREAD_LOCAL.logger:
            THREAD_LOCAL.logger.debug('[' + THREAD_LOCAL.uuid + ']response:' + response_str)

        response_content = json.loads(response_str)

        if not self.__config.tiger_public_key or 'sign' not in response_content or not timestamp:
            return response_content

        sign = response_content.get('sign')

        try:
            verify_res = verify_with_rsa(self.__config.tiger_public_key, timestamp.encode('utf-8'),
                                         sign.encode('utf-8'))
        except Exception as e:
            raise ResponseException('[' + THREAD_LOCAL.uuid + ']response sign verify failed. ' + str(e) + ' '
                                    + response_str)
        if not verify_res:
            raise ResponseException('[' + THREAD_LOCAL.uuid + ']response sign verify failed. ' + response_str)

        return response_content

    """
    执行接口请求
    """

    def execute(self, request):
        THREAD_LOCAL.uuid = str(uuid.uuid1())
        query_string = None
        params = self.__prepare_request(request)

        response = do_post(self.__config.server_url, query_string, self.__headers, params, self.__config.timeout,
                           self.__config.charset)

        return self.__parse_response(response, params.get('timestamp'))
