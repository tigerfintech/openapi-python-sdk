# -*- coding: utf-8 -*-
"""NewsClient 集成测试 — 真实接口，只读（news_stock_list / news_highlight_list）。

- 契约：请求 wire key snake_case / 响应 camelCase，条目 url 为绝对路径；
- highlight 游标翻页按 last_id 定位，两页不重叠不遗漏。
"""
import logging
import time
import unittest

import pytest

from tigeropen.news.domain.news_item import NewsItem
from tigeropen.news.domain.news_page import NewsPage
from tigeropen.news.news_client import NewsClient
from tests.support import integ_client_config, is_integ_run

logger = logging.getLogger(__name__)


@pytest.mark.skipif(not is_integ_run(), reason="requires TIGER_RUN_INTEG=true")
class TestIntegNewsClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client_config = integ_client_config()
        cls.client = NewsClient(cls.client_config, logger=logger)

    def _assert_item_contract(self, item):
        """条目契约：id/title/summary/pub_timestamp(秒级)/url(绝对路径)。"""
        self.assertIsInstance(item, NewsItem)
        self.assertIsInstance(item.id, str)
        self.assertTrue(item.id)
        self.assertIsInstance(item.title, str)
        self.assertIsInstance(item.pub_timestamp, int)
        # 秒级时间戳：大于 2020 年、不超过当前时间 + 1 天
        self.assertGreater(item.pub_timestamp, 1577836800)
        self.assertLessEqual(item.pub_timestamp, time.time() + 86400)
        self.assertIsInstance(item.url, str)
        self.assertTrue(item.url.startswith('http'))

    def test_get_stock_news_contract(self):
        page = self.client.get_stock_news('AAPL', lang='zh_CN', page_count=1, page_size=5)
        self.assertIsInstance(page, NewsPage)
        self.assertIsInstance(page.page_count, int)
        self.assertIsInstance(page.page_size, int)
        self.assertIsInstance(page.total_page, int)
        self.assertIsInstance(page.total_size, int)
        self.assertGreaterEqual(page.total_size, 0)
        if not page.items:
            pytest.skip('no news items returned for AAPL')
        self.assertLessEqual(len(page.items), 5)
        for item in page.items:
            self._assert_item_contract(item)
        logger.debug(f'stock news (real): total={page.total_size}, first={page.items[0].title}')

    def test_get_stock_news_paging_params_echoed(self):
        """显式传 page_size=5 时服务端信封回显 pageSize=5。"""
        page = self.client.get_stock_news('AAPL', page_size=5)
        self.assertEqual(page.page_size, 5)

    def test_get_market_news_contract(self):
        page = self.client.get_market_news(lang='zh_CN')
        self.assertIsInstance(page, NewsPage)
        if not page.items:
            pytest.skip('no highlight items returned')
        for item in page.items:
            self._assert_item_contract(item)
        logger.debug(f'highlight news (real): total={page.total_size}, first={page.items[0].title}')

    def test_get_market_news_cursor_no_overlap(self):
        """游标翻页：last_id 取上一页最后一条 id，两页 id 集合不重叠（不漏不重）。"""
        page1 = self.client.get_market_news()
        if not page1.items:
            pytest.skip('no highlight items returned')
        last_id = page1.items[-1].id
        page2 = self.client.get_market_news(lang='zh_CN', last_id=last_id)
        if not page2.items:
            pytest.skip('no more highlight items after cursor')
        ids1 = {item.id for item in page1.items}
        ids2 = {item.id for item in page2.items}
        self.assertEqual(ids1 & ids2, set(),
                         'cursor pagination must not repeat items across pages')
        logger.debug(f'cursor paging: page1={len(ids1)} items, page2={len(ids2)} items, '
                     f'no overlap')


if __name__ == '__main__':
    unittest.main()
