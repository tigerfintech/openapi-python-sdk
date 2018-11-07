# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.consts import Language


class TigerOpenClientConfig(object):
    def __init__(self, sandbox_debug=False):
        # 开发者应用id
        self._tiger_id = ''
        # 授权账户
        self._account = ''
        # 请求签名类型，推荐RSA2
        self._sign_type = 'RSA'
        # 开发者应用私钥
        self._private_key = ''
        
        # 老虎证券开放平台网关地址
        self._server_url = "https://openapi.itiger.com/gateway"
        self._socket_host_port = ('ssl', 'openapi.itiger.com', 8883)
        # 老虎证券开放平台公钥
        self._tiger_public_key = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDNF3G8SoEcCZh2rshUbayDgLLrj6rKgzNMxDL2HS' \
                                 'nKcB0+GPOsndqSv+a4IBu9+I3fyBp5hkyMMG2+AXugd9pMpy6VxJxlNjhX1MYbNTZJUT4nudki4uh+LM' \
                                 'OkIBHOceGNXjgB+cXqmlUnjlqha/HgboeHSnSgpM3dKSJQlIOsDwIDAQAB'

        if sandbox_debug:
            self._server_url = "https://openapi-sandbox.itiger.com/gateway"
            self._socket_host_port = ('ssl', 'openapi-sandbox.itiger.com', 8885)
            self._tiger_public_key = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbm21i11hgAENGd3/f280PSe4g9YGkS3TEXBY' \
                                     'MidihTvHHf+tJ0PYD0o3PruI0hl3qhEjHTAxb75T5YD3SGK4IBhHn/Rk6mhqlGgI+bBrBVYaXixm' \
                                     'HfRo75RpUUuWACyeqQkZckgR0McxuW9xRMIa2cXZOoL1E4SL4lXKGhKoWbwIDAQAB'
            # 请求字符集，默认utf-8
        self._charset = 'UTF-8'
        # 语言
        self._language = Language.zh_CN
        
        ## 以下为可选参数
        # 请求读取超时，单位秒，默认15s
        self._timeout = 15
    
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
