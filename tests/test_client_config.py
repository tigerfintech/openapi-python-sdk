# -*- coding: utf-8 -*-
#
# @Date    : 2022/10/8
# @Author  : sukai
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pytz import timezone as pytz_timezone

from tigeropen.common.consts import Language, License
from tigeropen.tiger_open_config import (
    TigerOpenClientConfig, GATEWAY_SUFFIX,
    SERVER_URL, US_SERVER_URL, SOCKET_HOST_PORT, US_SOCKET_HOST_PORT,
    TIMEOUT, TOKEN_REFRESH_DURATION, LANGUAGE,
    SANDBOX_TIGER_PUBLIC_KEY, TIGER_PUBLIC_KEY,
)


def make_config(**kwargs) -> TigerOpenClientConfig:
    """构造一个不触发 query_domains 的 config 实例"""
    cfg = TigerOpenClientConfig(enable_dynamic_domain=False, **kwargs)
    return cfg


def write_props(path: str, content: str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


class TestDefaults(unittest.TestCase):
    def setUp(self):
        self.cfg = make_config()

    def test_server_url_default(self):
        self.assertEqual(SERVER_URL, self.cfg.server_url)

    def test_quote_server_url_default(self):
        self.assertEqual(SERVER_URL, self.cfg.quote_server_url)

    def test_socket_host_port_default(self):
        self.assertEqual(SOCKET_HOST_PORT, self.cfg.socket_host_port)

    def test_timeout_default(self):
        self.assertEqual(TIMEOUT, self.cfg.timeout)

    def test_token_refresh_duration_default(self):
        self.assertEqual(TOKEN_REFRESH_DURATION, self.cfg.token_refresh_duration)

    def test_language_default(self):
        self.assertEqual(LANGUAGE, self.cfg.language)

    def test_use_full_tick_default(self):
        self.assertFalse(self.cfg.use_full_tick)

    def test_timezone_default(self):
        self.assertIsNone(self.cfg.timezone)

    def test_tiger_public_key_default(self):
        self.assertEqual(TIGER_PUBLIC_KEY, self.cfg.tiger_public_key)


class TestIsUs(unittest.TestCase):
    def test_us_license_overrides_endpoints(self):
        # is_us 在 _apply_defaults 里判断，但构造时 license 尚未从 props/env 以外的方式注入
        # 通过设好 license 后手动调用 _apply_defaults 来验证覆盖逻辑
        cfg = make_config()
        cfg._license = License.TBUS
        cfg._server_url = None
        cfg._quote_server_url = None
        cfg._socket_host_port = None
        cfg._apply_defaults()
        self.assertEqual(US_SERVER_URL, cfg._server_url)
        self.assertEqual(US_SERVER_URL, cfg._quote_server_url)
        self.assertEqual(US_SOCKET_HOST_PORT, cfg._socket_host_port)


class TestEnvVars(unittest.TestCase):
    def setUp(self):
        # 清理所有 TIGEROPEN_ 环境变量，避免测试间污染
        self._saved = {k: v for k, v in os.environ.items() if k.startswith('TIGEROPEN_')}
        for k in self._saved:
            del os.environ[k]

    def tearDown(self):
        for k in list(os.environ):
            if k.startswith('TIGEROPEN_'):
                del os.environ[k]
        os.environ.update(self._saved)

    def test_server_url_from_env(self):
        os.environ['TIGEROPEN_SERVER_URL'] = 'https://custom.example.com/gateway'
        cfg = make_config()
        self.assertEqual('https://custom.example.com/gateway', cfg.server_url)
        self.assertEqual('https://custom.example.com/gateway', cfg.quote_server_url)

    def test_timeout_from_env(self):
        os.environ['TIGEROPEN_TIMEOUT'] = '30'
        cfg = make_config()
        self.assertEqual(30, cfg.timeout)

    def test_timeout_invalid_env_falls_back_to_default(self):
        os.environ['TIGEROPEN_TIMEOUT'] = 'not_a_number'
        cfg = make_config()
        self.assertEqual(TIMEOUT, cfg.timeout)

    def test_token_refresh_duration_from_env(self):
        os.environ['TIGEROPEN_TOKEN_REFRESH_DURATION'] = '3600'
        cfg = make_config()
        self.assertEqual(3600, cfg.token_refresh_duration)

    def test_token_refresh_duration_zero_is_valid(self):
        os.environ['TIGEROPEN_TOKEN_REFRESH_DURATION'] = '0'
        # 0 是有效值，不应被 if not 误判
        cfg = make_config()
        self.assertEqual(0, cfg.token_refresh_duration)

    def test_socket_host_port_from_env(self):
        os.environ['TIGEROPEN_SOCKET_HOST_PORT'] = 'ssl,custom.host.com,9999'
        cfg = make_config()
        self.assertEqual(('ssl', 'custom.host.com', 9999), cfg.socket_host_port)

    def test_socket_host_port_invalid_env_falls_back_to_default(self):
        os.environ['TIGEROPEN_SOCKET_HOST_PORT'] = 'bad_format'
        cfg = make_config()
        self.assertEqual(SOCKET_HOST_PORT, cfg.socket_host_port)

    def test_use_full_tick_true_from_env(self):
        for val in ('true', 'True', 'TRUE', '1', 'yes'):
            os.environ['TIGEROPEN_USE_FULL_TICK'] = val
            cfg = make_config()
            self.assertTrue(cfg.use_full_tick, msg=f'Expected True for env value {val!r}')

    def test_use_full_tick_false_from_env(self):
        os.environ['TIGEROPEN_USE_FULL_TICK'] = 'false'
        cfg = make_config()
        self.assertFalse(cfg.use_full_tick)

    def test_timezone_from_env(self):
        os.environ['TIGEROPEN_TIMEZONE'] = 'Asia/Shanghai'
        cfg = make_config()
        self.assertEqual(pytz_timezone('Asia/Shanghai'), cfg.timezone)

    def test_language_from_env(self):
        os.environ['TIGEROPEN_LANGUAGE'] = 'zh_CN'
        cfg = make_config()
        self.assertEqual(Language.zh_CN, cfg.language)

    def test_language_invalid_env_falls_back_to_default(self):
        os.environ['TIGEROPEN_LANGUAGE'] = 'invalid_lang'
        cfg = make_config()
        self.assertEqual(LANGUAGE, cfg.language)


class TestPropsFile(unittest.TestCase):
    def setUp(self):
        self._saved = {k: v for k, v in os.environ.items() if k.startswith('TIGEROPEN_')}
        for k in self._saved:
            del os.environ[k]
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        for k in list(os.environ):
            if k.startswith('TIGEROPEN_'):
                del os.environ[k]
        os.environ.update(self._saved)

    def _cfg(self, props_content: str) -> TigerOpenClientConfig:
        write_props(os.path.join(self.tmpdir, 'tiger_openapi_config.properties'), props_content)
        return make_config(props_path=self.tmpdir)

    def test_server_url_from_props(self):
        cfg = self._cfg('server_url=https://props.example.com/gateway\n')
        self.assertEqual('https://props.example.com/gateway', cfg.server_url)
        self.assertEqual('https://props.example.com/gateway', cfg.quote_server_url)

    def test_timeout_from_props(self):
        cfg = self._cfg('timeout=60\n')
        self.assertEqual(60, cfg.timeout)

    def test_token_refresh_duration_from_props(self):
        cfg = self._cfg('token_refresh_duration=1800\n')
        self.assertEqual(1800, cfg.token_refresh_duration)

    def test_socket_host_port_from_props(self):
        cfg = self._cfg('socket_host_port=ssl,props.host.com,9001\n')
        self.assertEqual(('ssl', 'props.host.com', 9001), cfg.socket_host_port)

    def test_use_full_tick_from_props(self):
        cfg = self._cfg('use_full_tick=true\n')
        self.assertTrue(cfg.use_full_tick)

    def test_timezone_from_props(self):
        cfg = self._cfg('timezone=America/New_York\n')
        self.assertEqual(pytz_timezone('America/New_York'), cfg.timezone)

    def test_language_from_props(self):
        cfg = self._cfg('language=zh_TW\n')
        self.assertEqual(Language.zh_TW, cfg.language)

    def test_private_key_priority_plain_over_pk8(self):
        cfg = self._cfg('private_key=PLAIN_KEY\nprivate_key_pk8=PK8_KEY\nprivate_key_pk1=PK1_KEY\n')
        self.assertEqual('PLAIN_KEY', cfg.private_key)

    def test_private_key_priority_pk8_over_pk1(self):
        cfg = self._cfg('private_key_pk8=PK8_KEY\nprivate_key_pk1=PK1_KEY\n')
        self.assertEqual('PK8_KEY', cfg.private_key)

    def test_private_key_fallback_to_pk1(self):
        cfg = self._cfg('private_key_pk1=PK1_KEY\n')
        self.assertEqual('PK1_KEY', cfg.private_key)


class TestPriority(unittest.TestCase):
    """代码赋值 > env var > props 文件 > 内置默认值"""

    def setUp(self):
        self._saved = {k: v for k, v in os.environ.items() if k.startswith('TIGEROPEN_')}
        for k in self._saved:
            del os.environ[k]
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        for k in list(os.environ):
            if k.startswith('TIGEROPEN_'):
                del os.environ[k]
        os.environ.update(self._saved)

    def test_env_beats_props(self):
        write_props(os.path.join(self.tmpdir, 'tiger_openapi_config.properties'),
                    'timeout=99\n')
        os.environ['TIGEROPEN_TIMEOUT'] = '42'
        cfg = make_config(props_path=self.tmpdir)
        self.assertEqual(42, cfg.timeout)

    def test_code_assignment_beats_env(self):
        os.environ['TIGEROPEN_TIMEOUT'] = '42'
        cfg = make_config()
        cfg.timeout = 5
        self.assertEqual(5, cfg.timeout)


class TestSandboxDebug(unittest.TestCase):
    def setUp(self):
        self._saved = {k: v for k, v in os.environ.items() if k.startswith('TIGEROPEN_')}
        for k in self._saved:
            del os.environ[k]

    def tearDown(self):
        for k in list(os.environ):
            if k.startswith('TIGEROPEN_'):
                del os.environ[k]
        os.environ.update(self._saved)

    def test_sandbox_debug_without_dynamic_domain_sets_public_key(self):
        cfg = TigerOpenClientConfig(sandbox_debug=True, enable_dynamic_domain=False)
        self.assertEqual(SANDBOX_TIGER_PUBLIC_KEY, cfg.tiger_public_key)

    def test_sandbox_debug_with_dynamic_domain_raises(self):
        with self.assertRaises(NotImplementedError):
            TigerOpenClientConfig(sandbox_debug=True, enable_dynamic_domain=True)

    def test_no_sandbox_debug_keeps_production_public_key(self):
        cfg = make_config()
        self.assertEqual(TIGER_PUBLIC_KEY, cfg.tiger_public_key)

    def test_env_sandbox_sets_sandbox_public_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_props(os.path.join(tmpdir, 'tiger_openapi_config.properties'), 'env=SANDBOX\n')
            cfg = TigerOpenClientConfig(enable_dynamic_domain=False, props_path=tmpdir)
            self.assertEqual(SANDBOX_TIGER_PUBLIC_KEY, cfg.tiger_public_key)

    def test_env_test_sets_sandbox_public_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_props(os.path.join(tmpdir, 'tiger_openapi_config.properties'), 'env=TEST\n')
            cfg = TigerOpenClientConfig(enable_dynamic_domain=False, props_path=tmpdir)
            self.assertEqual(SANDBOX_TIGER_PUBLIC_KEY, cfg.tiger_public_key)


class TestRefreshServerInfo(unittest.TestCase):
    domain_map = {
        'socket_port': 9883,
        'port': 9887,
        'TBSG-QUOTE': 'https://openapi.tigerfintech.com/sgp-quote',
        'TBNZ-QUOTE': 'https://openapi.tigerfintech.com/hkg-quote',
        'TBSG-PAPER': 'https://openapi-sandbox.tigerfintech.com/sgp',
        'TBNZ-PAPER': 'https://openapi-sandbox.tigerfintech.com/hkg',
        'TBSG': 'https://openapi.tigerfintech.com/sgp',
        'TBNZ': 'https://openapi.tigerfintech.com/hkg',
        'COMMON': 'https://openapi.tigerfintech.com',
    }

    def test_refresh_server_info(self):
        config = TigerOpenClientConfig()
        config.query_domains = MagicMock(name='query_domains', return_value=self.domain_map)
        config.domain_conf = config.query_domains()

        self.assertEqual('https://openapi.tigerfintech.com' + GATEWAY_SUFFIX, config.server_url)
        self.assertEqual(('ssl', 'openapi.tigerfintech.com', 9883), config.socket_host_port)

        config.license = License.TBNZ
        config.refresh_server_info()
        self.assertEqual('https://openapi.tigerfintech.com/hkg' + GATEWAY_SUFFIX, config.server_url)
        self.assertEqual('https://openapi.tigerfintech.com/hkg-quote' + GATEWAY_SUFFIX, config.quote_server_url)

        config.license = 'TBSG'
        config.refresh_server_info()
        self.assertEqual('https://openapi.tigerfintech.com/sgp' + GATEWAY_SUFFIX, config.server_url)
        self.assertEqual('https://openapi.tigerfintech.com/sgp-quote' + GATEWAY_SUFFIX, config.quote_server_url)

        config.is_paper = True
        config.license = 'TBNZ'
        config.refresh_server_info()
        self.assertEqual('https://openapi-sandbox.tigerfintech.com/hkg' + GATEWAY_SUFFIX, config.server_url)
        self.assertEqual('https://openapi.tigerfintech.com/hkg-quote' + GATEWAY_SUFFIX, config.quote_server_url)

        config = TigerOpenClientConfig(enable_dynamic_domain=False)
        config.query_domains = MagicMock(name='query_domains', return_value=self.domain_map)
        config.domain_conf = config.query_domains()
        config.license = 'TBNZ'
        config.refresh_server_info()
        self.assertEqual('https://openapi.tigerfintech.com' + GATEWAY_SUFFIX, config.server_url)
        self.assertEqual(('ssl', 'openapi.tigerfintech.com', 9883), config.socket_host_port)


if __name__ == '__main__':
    unittest.main()
