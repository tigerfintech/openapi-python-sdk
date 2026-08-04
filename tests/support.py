# -*- coding: utf-8 -*-
"""测试基础设施：client config 构造与运行模式判断。

两种 config：

- ``offline_client_config()`` —— L1 单测用。私钥在内存中生成，配置目录是临时空目录，
  动态域名关闭，license 显式赋值，因此从构造到使用全程零凭据、零网络。
- ``integ_client_config()`` —— L2 契约测试和 L3 集成测试用。配置路径只从
  ``TIGER_CONFIG_PATH`` 环境变量取，不硬编码本机路径或 tiger_id。

运行模式由 ``TIGER_RUN_INTEG`` 环境变量决定，见 ``is_integ_run()``。
"""
import base64
import os
import tempfile
from contextlib import contextmanager

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tigeropen.common.consts import License
from tigeropen.tiger_open_config import ENV_PREFIX, TigerOpenClientConfig

# 仅用于通过 SDK 的非空校验，不对应任何真实账户
FAKE_TIGER_ID = '00000000'
FAKE_ACCOUNT = '00000000000000000'


def _generate_private_key():
    """生成 SDK 期望的私钥格式：DER 的 base64 文本，不带 PEM 头尾和换行。

    signature_utils.load_private_key() 直接对字符串做 base64 解码再 load DER，
    read_private_key() 读文件时也是把 PEM 头尾剥掉后返回 base64 正文。
    传完整 PEM 会在签名时报 binascii.Error: Incorrect padding。
    """
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    der = key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return base64.b64encode(der).decode()


# 模块级缓存。2048 位 RSA 生成有可观开销，每个 case 生成一次会让单测退化成秒级。
TEST_PRIVATE_KEY = _generate_private_key()

# 模块级临时目录。TigerOpenClientConfig 的 props_path 默认是 '.'，会读到 cwd 下的
# tiger_openapi_config.properties；指向一个确定为空的目录，保证结果不随运行目录变化。
_EMPTY_PROPS_DIR = tempfile.mkdtemp(prefix='tigeropen-test-props-')


def is_integ_run():
    """是否连真实接口运行（L2 / L3）。"""
    return os.environ.get('TIGER_RUN_INTEG', '').lower() == 'true'


@contextmanager
def _without_tigeropen_env():
    """构造期间临时移除 TIGEROPEN_* 环境变量。

    TigerOpenClientConfig 优先读环境变量，本机或 CI 上残留的 TIGEROPEN_PROPS_PATH /
    TIGEROPEN_PRIVATE_KEY 会让「离线」config 意外加载真实配置，单测结果随机器而变。
    """
    saved = {k: v for k, v in os.environ.items() if k.startswith(ENV_PREFIX)}
    for key in saved:
        del os.environ[key]
    try:
        yield
    finally:
        os.environ.update(saved)


def offline_client_config():
    """构造完全离线的 client config。

    三个关键点，缺一个就会产生真实网络请求：

    1. ``enable_dynamic_domain=False`` —— 否则构造时会 GET 域名花园拉取网关地址。
    2. ``license`` 显式赋值 —— 否则 TigerOpenClient 初始化会调 query_license() 发请求。
       该分支同时受 enable_dynamic_domain 约束，两者都关才稳妥。
    3. ``props_path`` 指向临时空目录 —— 避免读到运行目录下的真实配置。
    """
    with _without_tigeropen_env():
        config = TigerOpenClientConfig(enable_dynamic_domain=False,
                                       props_path=_EMPTY_PROPS_DIR)
    config.tiger_id = FAKE_TIGER_ID
    config.private_key = TEST_PRIVATE_KEY
    config.account = FAKE_ACCOUNT
    config.license = License.TBNZ
    return config


def integ_client_config():
    """构造连真实接口的 client config。

    凭据来源：runner 上的配置目录，通过 ``TIGEROPEN_PROPS_PATH`` 环境变量指定。
    文件里的 tiger_id / private_key / account 会被 TigerOpenClientConfig._load_props() 自动加载。
    这与 Java SDK 用同一个环境变量名指向同一目录是等价的。

    ``enable_dynamic_domain=False`` 是必须的：QA 配置多带 ``env=TEST``，
    与动态域名同时开启会命中已废弃分支抛 NotImplementedError。
    """
    props_path = os.environ.get('TIGEROPEN_PROPS_PATH', os.path.expanduser('~/.tigeropen/'))
    return TigerOpenClientConfig(props_path=props_path, enable_dynamic_domain=False)


def client_config():
    """按当前运行模式返回对应的 config。"""
    return integ_client_config() if is_integ_run() else offline_client_config()
