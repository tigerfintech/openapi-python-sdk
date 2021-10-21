# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.consts import Language
from tigeropen.common.util.signature_utils import read_private_key

# 老虎证券开放平台网关地址
SERVER_URL = 'https://openapi.itiger.com/gateway'
# 老虎证券开放平台 socket 连接域名端口
SOCKET_HOST_PORT = ('ssl', 'openapi.itiger.com', 8883)
# 老虎证券开放平台公钥
TIGER_PUBLIC_KEY = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDNF3G8SoEcCZh2rshUbayDgLLrj6rKgzNMxDL2HS' \
                   'nKcB0+GPOsndqSv+a4IBu9+I3fyBp5hkyMMG2+AXugd9pMpy6VxJxlNjhX1MYbNTZJUT4nudki4uh+LM' \
                   'OkIBHOceGNXjgB+cXqmlUnjlqha/HgboeHSnSgpM3dKSJQlIOsDwIDAQAB'
# 请求签名类型
SIGN_TYPE = 'RSA'
# 请求字符集
CHARSET = 'UTF-8'
# 语言
LANGUAGE = Language.zh_CN
# 请求超时时间, 单位秒, 默认15s
TIMEOUT = 15

# sandbox 环境配置
SANDBOX_SERVER_URL = 'https://openapi-sandbox.itiger.com/gateway'
SANDBOX_SOCKET_HOST_PORT = ('ssl', 'openapi-sandbox.itiger.com', 8885)
SANDBOX_TIGER_PUBLIC_KEY = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbm21i11hgAENGd3/f280PSe4g9YGkS3TEXBY' \
                           'MidihTvHHf+tJ0PYD0o3PruI0hl3qhEjHTAxb75T5YD3SGK4IBhHn/Rk6mhqlGgI+bBrBVYaXixm' \
                           'HfRo75RpUUuWACyeqQkZckgR0McxuW9xRMIa2cXZOoL1E4SL4lXKGhKoWbwIDAQAB'


class TigerOpenClientConfig:
    def __init__(self, sandbox_debug=False):
        # 开发者应用id
        self._tiger_id = ''
        # 授权账户
        self._account = ''
        # 开发者应用私钥
        self._private_key = ''
        # 请求签名类型，推荐RSA2
        self._sign_type = SIGN_TYPE
        # 机构交易员专有密钥
        self._secret_key = ''

        # 老虎证券开放平台网关地址
        self._server_url = SERVER_URL
        self._socket_host_port = SOCKET_HOST_PORT
        # 老虎证券开放平台公钥
        self._tiger_public_key = TIGER_PUBLIC_KEY

        if sandbox_debug:
            self._server_url = SANDBOX_SERVER_URL
            self._socket_host_port = SANDBOX_SOCKET_HOST_PORT
            self._tiger_public_key = SANDBOX_TIGER_PUBLIC_KEY
        # 请求字符集，默认utf-8
        self._charset = CHARSET
        # 语言
        self._language = LANGUAGE
        
        # 以下为可选参数
        # 请求读取超时，单位秒，默认15s
        self._timeout = TIMEOUT
    
    @property
    def tiger_id(self):
        return self._tiger_id
    
    @tiger_id.setter
    def tiger_id(self, value):
        self._tiger_id = value
    
    @property
    def account(self):
        return self._account
    
    @account.setter
    def account(self, value):
        self._account = value
    
    @property
    def sign_type(self):
        return self._sign_type
    
    @sign_type.setter
    def sign_type(self, value):
        self._sign_type = value
    
    @property
    def private_key(self):
        return self._private_key
    
    @private_key.setter
    def private_key(self, value):
        self._private_key = value
    
    @property
    def tiger_public_key(self):
        return self._tiger_public_key
    
    @tiger_public_key.setter
    def tiger_public_key(self, value):
        self._tiger_public_key = value
    
    @property
    def server_url(self):
        return self._server_url
    
    @server_url.setter
    def server_url(self, value):
        self._server_url = value
    
    @property
    def socket_host_port(self):
        return self._socket_host_port
    
    @socket_host_port.setter
    def socket_host_port(self, value):
        self._socket_host_port = value
    
    @property
    def charset(self):
        return self._charset
    
    @charset.setter
    def charset(self, value):
        self._charset = value
    
    @property
    def language(self):
        return self._language
    
    @language.setter
    def language(self, value):
        self._language = value
    
    @property
    def timeout(self):
        return self._timeout
    
    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value


def get_client_config(private_key_path, tiger_id, account, sandbox_debug=False, sign_type=None, timeout=None,
                      language=None, charset=None, server_url=None, socket_host_port=None, secret_key=None):
    """
    生成客户端配置
    :param private_key_path: 私钥文件路径, 如 '/Users/tiger/.ssh/rsa_private_key.pem'
    :param tiger_id: 开发者应用 id
    :param account: 授权账户 (必填. 作为发送请求时的默认账户. 不论是环球账户, 综合账户或是模拟账户, 都使用此参数)
    :param sandbox_debug: 是否请求 sandbox 环境
    :param sign_type: 签名类型
    :param timeout: 请求超时时间, 单位秒
    :param language: 语言, 取值为 tigeropen.common.consts.Language 中的枚举类型
    :param charset: 字符集编码
    :param server_url: 网关地址
    :param socket_host_port: 推送长连接的域名端口, 值为协议, 域名, 端口构成的三元组
    :param secret_key: 机构交易员专有密钥 (个人开发者无需指定)
    :return:
    """
    config = TigerOpenClientConfig(sandbox_debug=sandbox_debug)
    config.private_key = read_private_key(private_key_path)
    config.tiger_id = tiger_id
    config.account = account
    if sign_type:
        config.sign_type = sign_type
    if timeout:
        config.timeout = timeout
    if language:
        config.language = language
    if charset:
        config.charset = charset
    if server_url:
        config.server_url = server_url
    if socket_host_port:
        config.socket_host_port = socket_host_port
    if secret_key:
        config.secret_key = secret_key
    return config

