# -*- coding: utf-8 -*-
# 
# @Date    : 2022/10/8
# @Author  : sukai
import unittest
from unittest.mock import MagicMock

from tigeropen.common.consts import License
from tigeropen.tiger_open_config import TigerOpenClientConfig, GATEWAY_SUFFIX


class TestClientConfig(unittest.TestCase):

    def test_refresh_server_info(self):
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
        config = TigerOpenClientConfig()
        config.query_domains = MagicMock(name='query_domains', return_value=domain_map)
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
        config.query_domains = MagicMock(name='query_domains', return_value=domain_map)
        config.domain_conf = config.query_domains()
        config.license = 'TBNZ'
        config.refresh_server_info()
        self.assertEqual('https://openapi.tigerfintech.com' + GATEWAY_SUFFIX, config.server_url)
        self.assertEqual(('ssl', 'openapi.tigerfintech.com', 9883), config.socket_host_port)