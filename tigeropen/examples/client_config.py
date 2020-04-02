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
    client_config.account = 'your account'  # 环球账户.
    # 只使用一个账户时，不论是环球账户, 标准账户或是模拟账户, 都填在 client_config.account 下, 默认只会使用这里的账户.
    # standard_account 属性和 paper_account 属性只是为多账户时取用方便, 一般可忽略
    client_config.standard_account = None  # 标准账户
    client_config.paper_account = None  # 模拟账户
    client_config.language = Language.en_US
    return client_config
