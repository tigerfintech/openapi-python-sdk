# -*- coding: utf-8 -*-
# 
# @Date    : 2022/6/24
# @Author  : sukai
import unittest

from tigeropen.push.push_client import PushClient


class TestPushClient(unittest.TestCase):

    def test_tick_convert(self):
        body = '{"symbol":"QQQ","tickType":"*****","serverTimestamp":1656062042242,"priceOffset":2,' \
               '"volumes":[99,10,10,10,800],"partCode":["t","p","p","p","t"],"cond":"IIIIT","type":"TradeTick",' \
               '"times":[1656062084833,11,0,0,31],"quoteLevel":"usStockQuote","priceBase":28770,"sn":878,' \
               '"prices":[6,3,2,2,0],"timestamp":1656062085570}'

        expected = 'QQQ', [{'tick_type': '*', 'price': 287.76, 'volume': 99, 'part_code': 'NSDQ',
                     'part_code_name': 'NASDAQ Stock Market, LLC (NASDAQ)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084833, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.73, 'volume': 10, 'part_code': 'ARCA',
                     'part_code_name': 'NYSE Arca, Inc. (NYSE Arca)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084844, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.72, 'volume': 10, 'part_code': 'ARCA',
                     'part_code_name': 'NYSE Arca, Inc. (NYSE Arca)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084844, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.72, 'volume': 10, 'part_code': 'ARCA',
                     'part_code_name': 'NYSE Arca, Inc. (NYSE Arca)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084844, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.7, 'volume': 800, 'part_code': 'NSDQ',
                     'part_code_name': 'NASDAQ Stock Market, LLC (NASDAQ)', 'cond': 'US_FORM_T',
                     'time': 1656062084875, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570}]
        self.assertEqual(expected, PushClient._convert_tick(body))