# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""

import base64
import binascii
import json
import logging
import sys

import rsa

from tigeropen.common.util.string_utils import add_start_end


def get_sign_content(all_params):
    sign_content = ""
    for (k, v) in sorted(all_params.items()):
        value = v
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        sign_content += ("&" + k + "=" + value)
    sign_content = sign_content[1:]
    return sign_content


def read_private_key(key_file):
    """
    Pem key
    :param key_file:
    :return:
    """
    key_str = open(key_file, 'r').read()
    return key_str.replace('-----BEGIN RSA PRIVATE KEY-----\n', '').replace(
        '\n-----END RSA PRIVATE KEY-----', '').strip()


def read_public_key(key_file):
    """
    Pem key
    :param key_file:
    :return:
    """
    key_str = open(key_file, 'r').read()
    return key_str.replace('-----BEGIN PUBLIC KEY-----\n', '').replace('\n-----END PUBLIC KEY-----', '').strip()


def fill_private_key_marker(private_key):
    return add_start_end(private_key, "-----BEGIN RSA PRIVATE KEY-----\n", "\n-----END RSA PRIVATE KEY-----")


def fill_public_key_marker(public_key):
    return add_start_end(public_key, "-----BEGIN PUBLIC KEY-----\n", "\n-----END PUBLIC KEY-----")


def sign_with_rsa(private_key, sign_content, charset):
    sign_content = sign_content.encode(charset)
    try:
        private_key = rsa.PrivateKey.load_pkcs1(fill_private_key_marker(private_key), format='PEM')
    except binascii.Error:
        logging.error("私钥格式错误, 请参考文档进行修改. https://quant.itiger.com/openapi/py-docs/zh-cn/docs/intro/quickstart.html ")
        sys.exit(1)

    signature = rsa.sign(sign_content, private_key, 'SHA-1')

    sign = str(base64.b64encode(signature), encoding=charset)
    return sign


def verify_with_rsa(public_key, message, sign):
    public_key = fill_public_key_marker(public_key)
    sign = base64.b64decode(sign)
    return rsa.verify(message, sign, rsa.PublicKey.load_pkcs1_openssl_pem(public_key))
