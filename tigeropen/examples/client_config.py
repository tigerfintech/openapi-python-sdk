# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
from tigeropen.common.consts import Language
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key


def get_client_config():
    """
    https://www.itiger.com/openapi/info 开发者信息获取
    :return:
    """
    is_sandbox = False
    client_config = TigerOpenClientConfig(sandbox_debug=is_sandbox)
    client_config.private_key = read_private_key('your private key file path')
    client_config.tiger_id = 'your tiger id'
    client_config.account = 'your account'
    client_config.secret_key = None  # 机构交易员专有密钥 (机构用户需要填写, 个人开发者无需填写)
    client_config.language = Language.en_US
    # client_config.timezone = 'US/Eastern' # 设置全局时区
    return client_config
