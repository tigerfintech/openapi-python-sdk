# -*- coding: utf-8 -*-
"""资讯接口请求参数（wire key 为 snake_case，对齐服务端入参约定）。"""
from tigeropen.common.model import BaseParams


class NewsStockListParams(BaseParams):
    """news_stock_list 请求参数。

    - symbol: 必填，单标的非空 —— 下游资讯服务实际不支持批量查询（传多个仅单个标的生效），
      显式传空由服务端校验报参数错误
    - page_count / page_size: 可选，缺省由服务端归一化为 1 / 20；
      显式传值须满足 page_count >= 1、1 <= page_size <= 50（服务端校验）
    - lang: 公共参数见 BaseParams（zh_CN/zh_TW/en_US，空 = 中英混合内容，
      非法值服务端回退 en_US 不报错）
    """

    def __init__(self):
        super().__init__()
        self._symbol = None
        self._page_count = None
        self._page_size = None

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def page_count(self):
        return self._page_count

    @page_count.setter
    def page_count(self, value):
        self._page_count = value

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        self._page_size = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self._symbol:
            params['symbol'] = self._symbol
        if self._page_count is not None:
            params['page_count'] = self._page_count
        if self._page_size is not None:
            params['page_size'] = self._page_size
        return params


class NewsHighlightListParams(BaseParams):
    """news_highlight_list 请求参数。

    - last_id: 可选游标 —— 唯一翻页方式，取上一页 items 最后一条的 id；
      不传从最新开始
    - lang: 公共参数见 BaseParams
    """

    def __init__(self):
        super().__init__()
        self._last_id = None

    @property
    def last_id(self):
        return self._last_id

    @last_id.setter
    def last_id(self, value):
        self._last_id = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self._last_id:
            params['last_id'] = self._last_id
        return params
