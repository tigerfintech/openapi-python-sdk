# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""

import base64
import json
from functools import lru_cache

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

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


@lru_cache(maxsize=10)
def load_private_key(private_key):
    return serialization.load_pem_private_key(
        fill_private_key_marker(private_key).encode(),
        password=None,
        backend=default_backend()
    )


@lru_cache(maxsize=10)
def load_public_key(public_key):
    return serialization.load_pem_public_key(
        fill_public_key_marker(public_key).encode(),
        backend=default_backend()
    )


def sign_with_rsa(private_key_str, sign_content, charset):
    sign_content = sign_content.encode(charset)
    private_key = load_private_key(private_key_str)

    algorithm = hashes.SHA1()
    padding_data = padding.PKCS1v15()

    signature = private_key.sign(sign_content, padding_data, algorithm)
    sign = str(base64.b64encode(signature), encoding=charset)
    return sign


def verify_with_rsa(public_key, message, sign):
    public_key = load_public_key(public_key)
    sign = base64.b64decode(sign)
    padding_data = padding.PKCS1v15()
    algorithm = hashes.SHA1()
    try:
        public_key.verify(sign, message, padding=padding_data, algorithm=algorithm)
    except Exception as e:
        raise e
    return True
