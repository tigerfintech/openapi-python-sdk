# -*- coding: utf-8 -*-
"""测试基础设施：client config 构造与运行模式判断。."""
import base64
import os
import tempfile
from contextlib import contextmanager

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tigeropen.common.consts import License
from tigeropen.tiger_open_config import ENV_PREFIX, TigerOpenClientConfig

FAKE_TIGER_ID = '00000000'
FAKE_ACCOUNT = '00000000000000000'


def _generate_private_key():
    """Generate test RSA private key in DER base64 format."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    der = key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return base64.b64encode(der).decode()


# Cached at module level to avoid repeated key generation.
TEST_PRIVATE_KEY = _generate_private_key()

# tiger_openapi_config.properties；指向一个确定为空的目录，保证结果不随运行目录变化。
_EMPTY_PROPS_DIR = tempfile.mkdtemp(prefix='tigeropen-test-props-')


def is_integ_run():
    """Check if running in integration mode."""
    return os.environ.get('TIGER_RUN_INTEG', '').lower() == 'true'


@contextmanager
def _without_tigeropen_env():
    """Temporarily unset TIGEROPEN_* env vars."""
    saved = {k: v for k, v in os.environ.items() if k.startswith(ENV_PREFIX)}
    for key in saved:
        del os.environ[key]
    try:
        yield
    finally:
        os.environ.update(saved)


def offline_client_config():
    """Create offline client config (in-memory key, no network)."""
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
    """Return offline or real config based on TIGER_RUN_INTEG."""
    return integ_client_config() if is_integ_run() else offline_client_config()
