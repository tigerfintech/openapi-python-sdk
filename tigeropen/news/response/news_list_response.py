# -*- coding: utf-8 -*-
"""资讯列表响应解析 — news_stock_list 与 news_highlight_list 共用。

两接口服务端共用同一套 VO、wire 出参为 camelCase（决策 #13），
故 SDK 侧同样共用一个解析器：data → NewsPage(items: List[NewsItem])。
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.news.domain.news_item import NewsItem
from tigeropen.news.domain.news_page import NewsPage


class NewsListResponse(TigerResponse):
    """资讯列表响应（news_stock_list / news_highlight_list 共用）。"""

    def __init__(self):
        super().__init__()
        # 初始化为空结果而非 None（对齐 OptionAnalysisResponse.analysis_list 惯例），
        # data 缺失或解析前的空页语义成立
        self.result = NewsPage()

    def parse_response_content(self, response_content):
        super().parse_response_content(response_content)

        page = NewsPage()
        if self.data and isinstance(self.data, dict):
            page.page_count = self.data.get('pageCount')
            page.page_size = self.data.get('pageSize')
            page.total_page = self.data.get('totalPage')
            page.total_size = self.data.get('totalSize')
            for item in self.data.get('items') or []:
                news_item = NewsItem()
                for key, value in item.items():
                    attr = string_utils.camel_to_underline(key)
                    if hasattr(news_item, attr):
                        setattr(news_item, attr, value)
                page.items.append(news_item)
        self.result = page
