# -*- coding: utf-8 -*-
"""NewsClient 单元测试（news_stock_list / news_highlight_list）。

- 契约对齐 stock-openapi docs/news_api_design.md §3.1-§3.3：请求 wire key 为
  snake_case，响应出参为 camelCase，用真实 wire 形状验证反序列化。
- 路由回归：news 请求走主网关，对照组（QuoteClient）走行情域名。
"""
import json
import logging
import unittest
from unittest.mock import MagicMock

from tigeropen.common.exceptions import ApiException
from tigeropen.common.util import web_utils
from tigeropen.news.news_client import NewsClient
from tigeropen.quote.quote_client import QuoteClient

from tests.support import client_config, is_integ_run

logger = logging.getLogger(__name__)


class TestNewsClient(unittest.TestCase):

    def setUp(self):
        self.is_mock = not is_integ_run()
        logger.setLevel(logging.DEBUG if self.is_mock else logging.INFO)
        # 离线 config；行情域名设为与主网关可区分的假地址，路由断言才有区分度
        # （离线默认两者同值，见 tiger_open_config 缺省分支）
        self.client_config = client_config()
        self.client_config.quote_server_url = 'https://quote.example.test/gateway'
        self.client: NewsClient = NewsClient(self.client_config, logger=logger)
        self.origin_do_request = web_utils.do_request

    def tearDown(self):
        web_utils.do_request = self.origin_do_request

    def _mock_response(self, data, code=0, message='success'):
        wire = {'code': code, 'message': message, 'data': data, 'timestamp': 1700000000000}
        web_utils.do_request = MagicMock(return_value=json.dumps(wire).encode())

    def _biz_content(self):
        """取 do_request 最近一次调用请求体里的 biz_content（JSON 字符串 → dict）。"""
        body = web_utils.do_request.call_args.kwargs['params']
        return json.loads(body['biz_content'])

    def _request_url(self):
        return web_utils.do_request.call_args.kwargs['url']

    def test_get_stock_news(self):
        if self.is_mock:
            data = {
                'items': [{
                    'id': '123456',
                    'title': 'Apple Q2',
                    'summary': 'Earnings beat',
                    'pubTimestamp': 1729413600,
                    'url': 'https://example.com/news/123456'
                }],
                'pageCount': 1,
                'pageSize': 20,
                'totalPage': 10,
                'totalSize': 200,
            }
            self._mock_response(data)
            page = self.client.get_stock_news('AAPL', lang='zh_CN', page_count=1, page_size=20)
            self.assertIsNotNone(page)
            self.assertEqual(page.page_count, 1)
            self.assertEqual(page.page_size, 20)
            self.assertEqual(page.total_page, 10)
            self.assertEqual(page.total_size, 200)
            self.assertEqual(len(page.items), 1)
            item = page.items[0]
            self.assertEqual(item.id, '123456')
            self.assertEqual(item.title, 'Apple Q2')
            self.assertEqual(item.summary, 'Earnings beat')
            self.assertEqual(item.pub_timestamp, 1729413600)
            self.assertEqual(item.url, 'https://example.com/news/123456')
            # 请求 wire key 为 snake_case：symbol / page_count / page_size
            biz = self._biz_content()
            self.assertEqual(web_utils.do_request.call_args.kwargs['params']['method'],
                             'news_stock_list')
            self.assertEqual(biz.get('symbol'), 'AAPL')
            self.assertEqual(biz.get('page_count'), 1)
            self.assertEqual(biz.get('page_size'), 20)
            self.assertEqual(biz.get('lang'), 'zh_CN')
        else:
            page = self.client.get_stock_news('AAPL')
            logger.debug(f'get_stock_news result: {page}')
            self.assertIsNotNone(page)

    def test_get_stock_news_lang_empty_means_mixed(self):
        """显式传空串 = 中英混合内容（服务端空 lang 语义），不回落客户端默认语言。"""
        if self.is_mock:
            self._mock_response({'items': [], 'pageCount': 1, 'pageSize': 20,
                                 'totalPage': 0, 'totalSize': 0})
            self.client.get_stock_news('AAPL', lang='')
            self.assertNotIn('lang', self._biz_content())

    def test_get_stock_news_omits_optional_paging_when_absent(self):
        """page_count / page_size 不传时不进 wire，由服务端归一化为默认 1 / 20。"""
        if self.is_mock:
            self._mock_response({'items': [], 'pageCount': 1, 'pageSize': 20,
                                 'totalPage': 0, 'totalSize': 0})
            self.client.get_stock_news('AAPL')
            biz = self._biz_content()
            self.assertNotIn('page_count', biz)
            self.assertNotIn('page_size', biz)
            # 不传 lang 继承客户端语言配置（默认 en_US）
            self.assertEqual(biz.get('lang'), 'en_US')

    def test_get_market_news(self):
        if self.is_mock:
            data = {
                'items': [{
                    'id': '789',
                    'title': 'Fed cuts rates',
                    'summary': 'FOMC decision',
                    'pubTimestamp': 1761429600,
                    'url': 'https://example.com/highlight/detail?id=789'
                }],
                'pageCount': 2,
                'pageSize': 20,
                'totalPage': 5,
                'totalSize': 100,
            }
            self._mock_response(data)
            page = self.client.get_market_news(lang='en_US', last_id='789')
            self.assertIsNotNone(page)
            self.assertEqual(page.page_count, 2)
            self.assertEqual(page.total_page, 5)
            self.assertEqual(page.total_size, 100)
            self.assertEqual(len(page.items), 1)
            item = page.items[0]
            self.assertEqual(item.id, '789')
            self.assertEqual(item.title, 'Fed cuts rates')
            self.assertEqual(item.pub_timestamp, 1761429600)
            # 游标翻页：last_id 原样进 wire
            self.assertEqual(web_utils.do_request.call_args.kwargs['params']['method'],
                             'news_highlight_list')
            biz = self._biz_content()
            self.assertEqual(biz.get('last_id'), '789')
            self.assertEqual(biz.get('lang'), 'en_US')
            self.assertNotIn('page_count', biz)
        else:
            page = self.client.get_market_news()
            logger.debug(f'get_market_news result: {page}')
            self.assertIsNotNone(page)

    def test_get_market_news_default_starts_from_latest(self):
        """不传 last_id = 从最新开始（游标缺省不进 wire）。"""
        if self.is_mock:
            self._mock_response({'items': [], 'pageCount': 1, 'pageSize': 20,
                                 'totalPage': 0, 'totalSize': 0})
            self.client.get_market_news()
            self.assertNotIn('last_id', self._biz_content())

    def test_error_response_raises_api_exception(self):
        if self.is_mock:
            self._mock_response(None, code=1001, message='biz param error')
            with self.assertRaises(ApiException):
                self.client.get_stock_news('')

    def test_news_routes_to_main_gateway_not_quote(self):
        """news 请求走主网关；对照组：QuoteClient 走行情域名。"""
        if self.is_mock:
            # news 两个接口都走主网关
            self._mock_response({'items': [], 'pageCount': 1, 'pageSize': 20,
                                 'totalPage': 0, 'totalSize': 0})
            self.client.get_stock_news('AAPL')
            self.assertEqual(self._request_url(), self.client_config.server_url)
            self.assertNotEqual(self._request_url(), self.client_config.quote_server_url)

            self.client.get_market_news()
            self.assertEqual(self._request_url(), self.client_config.server_url)

            # 对照组：QUOTE 类型走行情域名，证明上面两个断言不是同值假阳性
            quote_client = QuoteClient(self.client_config, logger=logger, is_grab_permission=False)
            market_data = {
                'code': 0,
                'message': 'success',
                'timestamp': 1754978785570,
                'data': [{
                    'market': 'US',
                    'marketStatus': 'Not Yet Opened',
                    'status': 'NOT_YET_OPEN',
                    'openTime': '08-12 09:30:00 EDT'
                }]
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(market_data).encode())
            quote_client.get_market_status(market='US')
            self.assertEqual(self._request_url(), self.client_config.quote_server_url)


if __name__ == '__main__':
    unittest.main()
