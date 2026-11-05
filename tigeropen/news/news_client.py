# -*- coding: utf-8 -*-
"""
资讯客户端。
"""
import logging
from typing import Optional, Union

from tigeropen.common.consts import THREAD_LOCAL, Language
from tigeropen.common.consts.service_types import NEWS_STOCK_LIST, NEWS_HIGHLIGHT_LIST
from tigeropen.common.exceptions import ApiException
from tigeropen.common.request import OpenApiRequest
from tigeropen.common.util.common_utils import get_enum_value
from tigeropen.news.domain.news_page import NewsPage
from tigeropen.news.request.model import NewsStockListParams, NewsHighlightListParams
from tigeropen.news.response.news_list_response import NewsListResponse
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.tiger_open_config import LANGUAGE


class NewsClient(TigerOpenClient):

    def __init__(self, client_config, logger=None):
        if not logger:
            logger = logging.getLogger('tiger_openapi')
        super(NewsClient, self).__init__(client_config, logger=logger)
        if client_config:
            self._lang = client_config.language
        else:
            self._lang = LANGUAGE

    def __fetch_data(self, request):
        try:
            response = super(NewsClient, self).execute(request)
            return response
        except Exception as e:
            if hasattr(THREAD_LOCAL, 'logger') and THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e

    def get_stock_news(self, symbol: str, lang: Optional[Union[Language, str]] = None,
                       page_count: Optional[int] = None, page_size: Optional[int] = None) -> NewsPage:
        """
        查询个股新闻列表（method=news_stock_list）。Query the news list of a stock symbol.

        :param symbol: 股票代码，单标的必填。下游资讯服务实际不支持批量查询（传多个仅单个标的生效），
            故本接口只收一个；空值由服务端校验报参数错误
        :param lang: 语言（zh_CN/zh_TW/en_US），不传继承客户端语言配置（默认 en_US）；
            显式传空串 = 中英混合内容（服务端将空 lang 视为混合），
            非法非空值服务端回退 en_US 不报错
        :param page_count: 页码，缺省 = 1；显式传值须 >= 1（越界由服务端校验报参数错误）
        :param page_size: 每页条数，缺省 = 20；显式传值须 1-50（闭区间）
        :return: NewsPage 对象，有如下属性：
            - items: List[NewsItem]，每条含 id / title / summary / pub_timestamp（秒级时间戳）/ url
            - page_count / page_size / total_page / total_size: 分页信封字段
        """
        params = NewsStockListParams()
        params.symbol = symbol
        params.lang = get_enum_value(lang) if lang is not None else get_enum_value(self._lang)
        params.page_count = page_count
        params.page_size = page_size

        request = OpenApiRequest(NEWS_STOCK_LIST, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = NewsListResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return NewsPage()

    def get_market_news(self, lang: Optional[Union[Language, str]] = None,
                        last_id: Optional[str] = None) -> NewsPage:
        """
        查询市场要闻列表（method=news_highlight_list）。Query the market highlight news list.

        翻页只走 last_id 游标：取上一页 items 最后一条的 id 作为 last_id；
        不传从最新开始。

        :param lang: 语言（zh_CN/zh_TW/en_US），不传继承客户端语言配置（默认 en_US）；
            显式传空串 = 中英混合内容（服务端将空 lang 视为混合），
            非法非空值服务端回退 en_US 不报错
        :param last_id: 游标翻页参数，取上一页 items 最后一条的 id；不传 = 从最新开始
        :return: NewsPage 对象，属性同 get_stock_news；highlight 接口的 page_count 恒为 1
        """
        params = NewsHighlightListParams()
        params.lang = get_enum_value(lang) if lang is not None else get_enum_value(self._lang)
        params.last_id = last_id

        request = OpenApiRequest(NEWS_HIGHLIGHT_LIST, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = NewsListResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return NewsPage()
