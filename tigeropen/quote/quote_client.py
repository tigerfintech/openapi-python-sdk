# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
from tigeropen.common.consts import THREAD_LOCAL
from tigeropen.common.exceptions import ApiException
from tigeropen.quote.response.quote_bar_response import QuoteBarResponse
from tigeropen.quote.response.quote_hour_trading_timeline_response import QuoteHourTradingTimelineResponse
from tigeropen.quote.response.quote_timeline_response import QuoteTimelineResponse
from tigeropen.quote.response.quote_brief_response import QuoteBriefResponse
from tigeropen.quote.response.symbol_names_response import SymbolNamesResponse
from tigeropen.quote.response.symbols_response import SymbolsResponse
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.quote.request.model import MarketParams, SingleQuoteParams, MultipleQuoteParams
from tigeropen.quote.request import OpenApiRequest
from tigeropen.quote.response.quote_ticks_response import TradeTickResponse
from tigeropen.quote.response.market_status_response import MarketStatusResponse
from tigeropen.common.consts.service_types import MARKET_STATE, ALL_SYMBOLS, ALL_SYMBOL_NAMES, BRIEF, STOCK_DETAIL, \
    TIMELINE, HOUR_TRADING_TIMELINE, KLINE, TRADE_TICK
from tigeropen.common.consts import Market, Language, QuoteRight, TimelinePeriod, BarPeriod
import logging


class QuoteClient(TigerOpenClient):
    def __init__(self, client_config, logger=None):
        if not logger:
            logger = logging.getLogger('tiger_openapi')
        super(QuoteClient, self).__init__(client_config, logger=logger)
        if client_config:
            self._lang = client_config.language
        else:
            self._lang = Language.zh_CN

    def get_market_status(self, market=Market.ALL, lang=None):
        """
        获取市场状态
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MarketParams()
        params.market = market.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(MARKET_STATE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = MarketStatusResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.markets
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_symbols(self, market=Market.ALL):
        """
        获取股票代号列表
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :return:
        """
        params = MarketParams()
        params.market = market.value

        request = OpenApiRequest(ALL_SYMBOLS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SymbolsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.symbols
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_symbol_names(self, market=Market.ALL, lang=None):
        """
        获取股票代号列表和名称
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MarketParams()
        params.market = market.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(ALL_SYMBOL_NAMES, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SymbolNamesResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.symbol_names
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_briefs(self, symbols, include_hour_trading=False, include_ask_bid=False, right=QuoteRight.BR, lang=None):
        """
        获取股票摘要
        :param symbols: 股票代号列表
        :param include_hour_trading: 是否包含盘前盘后
        :param include_ask_bid: 是否包含买卖盘
        :param right: 复权选项 ，br: 前复权，nr: 不复权
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.include_hour_trading = include_hour_trading
        params.include_ask_bid = include_ask_bid
        params.right = right.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(BRIEF, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteBriefResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_details(self, symbols, lang=None):
        """
        获取股票详情(废弃)
        :param symbols: 股票代号列表
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(STOCK_DETAIL, biz_model=params)
        response_content = self.__fetch_data(request)
        return response_content

    def get_timeline(self, symbol, include_hour_trading=False, begin_time=-1, period=TimelinePeriod.DAY, lang=None):
        """
        获取分时数据
        :param symbol: 股票代码
        :param include_hour_trading: 是否包含盘前盘后分时
        :param begin_time: 开始时间
        :param period: 分时 ：day，5日分时： 5day
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = SingleQuoteParams()
        params.symbol = symbol
        params.include_hour_trading = include_hour_trading
        params.begin_time = begin_time
        params.period = period.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(TIMELINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteTimelineResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                if include_hour_trading:
                    return response.pre_market, response.regular, response.after_hours
                else:
                    return response.regular
            else:
                raise ApiException(response.code, response.message)
        print(response_content)

    def get_hour_trading_timeline(self, symbol, begin_time=-1, lang=None):
        """
        获取盘前盘后分时数据
        :param symbol: 股票代码
        :param begin_time: 开始时间
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = SingleQuoteParams()
        params.symbol = symbol
        params.begin_time = begin_time
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(HOUR_TRADING_TIMELINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteHourTradingTimelineResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.hour_trading, response.timelines
            else:
                raise ApiException(response.code, response.message)

    def get_bars(self, symbol, period=BarPeriod.DAY, begin_time=-1, end_time=-1, right=QuoteRight.BR, limit=251,
                 lang=None):
        """
        获取K线数据
        :param symbol: 股票代码
        :param period: day: 日K,week: 周K,month:月K ,year:年K,1min:1分钟,5min:5分钟,15min:15分钟,30min:30分钟,60min:60分钟
        :param begin_time: 开始时间
        :param end_time: 结束时间
        :param right: 复权选项 ，br: 前复权，nr: 不复权
        :param limit: 数量限制
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = SingleQuoteParams()
        params.symbol = symbol
        if period:
            params.period = period.value
        params.begin_time = begin_time
        params.end_time = end_time
        params.right = right.value
        params.limit = limit
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)
        print(response_content)

    def get_trade_ticks(self, symbol, begin_index=0, end_index=30, limit=30, lang=None):
        """
        获取逐笔成交
        :param symbol: 股票代码
        :param begin_index: 开始索引
        :param end_index: 结束索引
        :param limit: 数量限制
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = SingleQuoteParams()
        params.symbol = symbol
        params.begin_index = begin_index
        params.end_index = end_index
        params.limit = limit
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(TRADE_TICK, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = TradeTickResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trade_ticks
            else:
                raise ApiException(response.code, response.message)

        return None

    def __fetch_data(self, request):
        try:
            response = super(QuoteClient, self).execute(request)
            return response
        except Exception as e:
            if THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e
