# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import logging
import re
import time

import pandas as pd

from tigeropen.common.consts import Market, QuoteRight, BarPeriod, OPEN_API_SERVICE_VERSION_V3, \
    OPEN_API_SERVICE_VERSION_V1, Language
from tigeropen.common.consts import THREAD_LOCAL, SecurityType, CorporateActionType, IndustryLevel
from tigeropen.common.consts.filter_fields import FieldBelongType
from tigeropen.common.consts.service_types import GRAB_QUOTE_PERMISSION, QUOTE_DELAY, GET_QUOTE_PERMISSION, \
    HISTORY_TIMELINE, FUTURE_CONTRACT_BY_CONTRACT_CODE, STOCK_FUNDAMENTAL, TRADE_RANK, TRADING_CALENDAR, FUTURE_CONTRACTS, MARKET_SCANNER, \
    STOCK_BROKER, CAPITAL_FLOW, CAPITAL_DISTRIBUTION, WARRANT_REAL_TIME_QUOTE, WARRANT_FILTER, MARKET_SCANNER_TAGS, \
    KLINE_QUOTA, FUND_ALL_SYMBOLS, FUND_CONTRACTS, FUND_QUOTE, FUND_HISTORY_QUOTE, FINANCIAL_CURRENCY, \
    FINANCIAL_EXCHANGE_RATE, ALL_HK_OPTION_SYMBOLS, OPTION_DEPTH
from tigeropen.common.consts.service_types import MARKET_STATE, ALL_SYMBOLS, ALL_SYMBOL_NAMES, BRIEF, \
    TIMELINE, KLINE, TRADE_TICK, OPTION_EXPIRATION, OPTION_CHAIN, FUTURE_EXCHANGE, OPTION_BRIEF, \
    OPTION_KLINE, OPTION_TRADE_TICK, FUTURE_KLINE, FUTURE_TICK, FUTURE_CONTRACT_BY_EXCHANGE_CODE, \
    FUTURE_TRADING_DATE, QUOTE_SHORTABLE_STOCKS, FUTURE_REAL_TIME_QUOTE, \
    FUTURE_CURRENT_CONTRACT, QUOTE_REAL_TIME, QUOTE_STOCK_TRADE, FINANCIAL_DAILY, FINANCIAL_REPORT, CORPORATE_ACTION, \
    QUOTE_DEPTH, INDUSTRY_LIST, INDUSTRY_STOCKS, STOCK_INDUSTRY, STOCK_DETAIL, FUTURE_CONTINUOUS_CONTRACTS
from tigeropen.common.exceptions import ApiException
from tigeropen.common.request import OpenApiRequest
from tigeropen.common.util.common_utils import eastern, get_enum_value, date_str_to_timestamp
from tigeropen.common.util.contract_utils import extract_option_info
from tigeropen.fundamental.request.model import FinancialDailyParams, FinancialReportParams, CorporateActionParams, \
    IndustryParams, FinancialExchangeRateParams
from tigeropen.fundamental.response.corporate_dividend_response import CorporateDividendResponse
from tigeropen.fundamental.response.corporate_earnings_calendar_response import EarningsCalendarResponse
from tigeropen.fundamental.response.corporate_split_response import CorporateSplitResponse
from tigeropen.fundamental.response.dataframe_response import DataframeResponse
from tigeropen.fundamental.response.financial_daily_response import FinancialDailyResponse
from tigeropen.fundamental.response.financial_exchange_rate_response import FinancialExchangeRateResponse
from tigeropen.fundamental.response.financial_report_response import FinancialReportResponse
from tigeropen.fundamental.response.industry_response import IndustryListResponse, IndustryStocksResponse, \
    StockIndustryResponse
from tigeropen.quote.domain.filter import OptionFilter
from tigeropen.quote.request.model import MarketParams, MultipleQuoteParams, MultipleContractParams, \
    FutureQuoteParams, FutureExchangeParams, FutureContractParams, FutureTradingTimeParams, SingleContractParams, \
    SingleOptionQuoteParams, DepthQuoteParams, OptionChainParams, TradingCalendarParams, MarketScannerParams, \
    StockBrokerParams, CapitalParams, WarrantFilterParams, KlineQuotaParams, SymbolsParams, OptionContractsParams
from tigeropen.quote.response.capital_distribution_response import CapitalDistributionResponse
from tigeropen.quote.response.capital_flow_response import CapitalFlowResponse
from tigeropen.quote.response.fund_contracts_response import FundContractsResponse
from tigeropen.quote.response.future_briefs_response import FutureBriefsResponse
from tigeropen.quote.response.future_contract_response import FutureContractResponse
from tigeropen.quote.response.future_exchange_response import FutureExchangeResponse
from tigeropen.quote.response.future_quote_bar_response import FutureQuoteBarResponse
from tigeropen.quote.response.future_quote_ticks_response import FutureTradeTickResponse
from tigeropen.quote.response.future_trading_times_response import FutureTradingTimesResponse
from tigeropen.quote.response.kline_quota_response import KlineQuotaResponse
from tigeropen.quote.response.market_scanner_response import MarketScannerResponse, MarketScannerTagsResponse
from tigeropen.quote.response.market_status_response import MarketStatusResponse
from tigeropen.quote.response.option_briefs_response import OptionBriefsResponse
from tigeropen.quote.response.option_chains_response import OptionChainsResponse
from tigeropen.quote.response.option_depth_response import OptionDepthQuoteResponse
from tigeropen.quote.response.option_expirations_response import OptionExpirationsResponse
from tigeropen.quote.response.option_quote_bar_response import OptionQuoteBarResponse
from tigeropen.quote.response.option_quote_ticks_response import OptionTradeTickResponse
from tigeropen.quote.response.option_symbols_response import OptionSymbolsResponse
from tigeropen.quote.response.quote_bar_response import QuoteBarResponse
from tigeropen.quote.response.quote_brief_response import QuoteBriefResponse
from tigeropen.quote.response.quote_delay_briefs_response import DelayBriefsResponse
from tigeropen.quote.response.quote_depth_response import DepthQuoteResponse
from tigeropen.quote.response.quote_grab_permission_response import QuoteGrabPermissionResponse
from tigeropen.quote.response.quote_ticks_response import TradeTickResponse
from tigeropen.quote.response.quote_dataframe_response import QuoteDataframeResponse
from tigeropen.quote.response.quote_timeline_response import QuoteTimelineResponse
from tigeropen.quote.response.stock_briefs_response import StockBriefsResponse
from tigeropen.quote.response.stock_broker_response import StockBrokerResponse
from tigeropen.quote.response.stock_details_response import StockDetailsResponse
from tigeropen.quote.response.stock_short_interest_response import ShortInterestResponse
from tigeropen.quote.response.stock_trade_meta_response import TradeMetaResponse
from tigeropen.quote.response.symbol_names_response import SymbolNamesResponse
from tigeropen.quote.response.symbols_response import SymbolsResponse
from tigeropen.quote.response.trade_rank_response import TradeRankResponse
from tigeropen.quote.response.trading_calendar_response import TradingCalendarResponse
from tigeropen.quote.response.warrant_briefs_response import WarrantBriefsResponse
from tigeropen.quote.response.warrant_filter_response import WarrantFilterResponse
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.tiger_open_config import LANGUAGE


class QuoteClient(TigerOpenClient):

    def __init__(self, client_config, logger=None, is_grab_permission=True):
        if not logger:
            logger = logging.getLogger('tiger_openapi')
        self.logger = logger
        super(QuoteClient, self).__init__(client_config, logger=logger)
        self._lang = LANGUAGE
        self._timezone = eastern
        self._url = None
        if client_config:
            self._url = client_config.quote_server_url
            self._lang = client_config.language
            if client_config.timezone:
                self._timezone = client_config.timezone
        self.permissions = None
        if is_grab_permission and self.permissions is None:
            self.permissions = self.grab_quote_permission()
            self.logger.info('Grab quote permission. Permissions:' + str(self.permissions))

    def __fetch_data(self, request):
        try:
            response = super(QuoteClient, self).execute(request, url=self._url)
            return response
        except Exception as e:
            if hasattr(THREAD_LOCAL, 'logger') and THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e

    def get_market_status(self, market=Market.ALL, lang=None):
        """
        获取市场状态
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return: MarketStatus 对象构成的列表. MarketStatus 对象有如下属性：
            market: 字符串，市场名称
            status: 字符串，当前市场所处的状态
            open_time: 带 tzinfo 的 datetime 对象，表示最近的开盘、交易时间
        """
        params = MarketParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

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

    def get_symbols(self, market=Market.ALL, include_otc=False):
        """
        获取股票代号列表
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :param include_otc: 是否包含 OTC
        :return: 所有 symbol 的列表，包含退市和不可交易的部分代码. 其中以.开头的代码为指数， 如 .DJI 表示道琼斯指数
        """
        params = SymbolsParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(self._lang)
        params.include_otc = include_otc
        request = OpenApiRequest(ALL_SYMBOLS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SymbolsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_symbol_names(self, market=Market.ALL, lang=None, include_otc=False):
        """
        获取股票代号列表和名称
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :param include_otc: 是否包含 OTC
        :return: list, list 中的每个对象是一个 tuple. tuple 的第一个元素是 symbol，第二个是 name
        """
        params = SymbolsParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        params.include_otc = include_otc

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

    def get_trade_metas(self, symbols):
        """
        获取股票交易需要的信息(最新数量和报价单位等)
        :param symbols: 股票代号列表
        :return: pandas.DataFrame, 各 column 的含义如下:
            symbol: 证券代码
            lot_size: 每手股数
            min_tick: 价格最小变动单位
            spread_scale: 报价精度
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(QUOTE_STOCK_TRADE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = TradeMetaResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.metas
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
        params.right = get_enum_value(right)
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

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

    def get_stock_briefs(self, symbols, include_hour_trading=False, lang=None):
        """
        获取股票实时行情
        :param symbols: 股票代号列表
        :param lang: 语言支持: tigeropen.common.consts.Language:  zh_CN,zh_TW,en_US
        :param include_hour_trading: 是否包含盘前盘后
        :return: pandas.DataFrame.  各 column 含义如下：
            symbol: 证券代码
            ask_price: 卖一价
            ask_size: 卖一量
            bid_price: 买一价
            bid_size: 买一量
            pre_close: 前收价
            latest_price: 最新价
            latest_time: 最新成交时间
            volume: 成交量
            open: 开盘价
            high: 最高价
            low: 最低价
            status: 交易状态:
                "UNKNOWN": 未知
                "NORMAL": 正常
                "HALTED": 停牌
                "DELIST": 退市
                "NEW": 新股
                "ALTER": 变更
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.include_hour_trading = include_hour_trading
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(QUOTE_REAL_TIME, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = StockBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_stock_delay_briefs(self, symbols, lang=None):
        """
        query delay quote
        :param symbols: stock symbol list, like ['AAPL', 'GOOG']
        :param lang: language: tigeropen.common.consts.Language:  zh_CN,zh_TW,en_US
        :return: pandas.DataFrame. the columns are as follows：
            symbol:
            pre_close:
            time: last quote change time
            volume:
            open:
            high:
            low:
            close:
            halted: stock status(0: normal 3: suspended  4: delist 7: ipo 8: changed)
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(QUOTE_DELAY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = DelayBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_stock_details(self, symbols, lang=None):
        """
        获取股票详情
        :param symbols: 股票代号列表
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return: pandas.DataFrame.  各 column 含义如下：
            symbol: 代码
            market: 市场
            sec_type: 证券类型
            exchange: 交易所
            name: 名称
            shortable: 做空信息
            ask_price: 卖一价
            ask_size: 卖一量
            bid_price: 买一价
            bid_size: 买一量
            pre_close: 前收价
            latest_price: 最新价
            adj_pre_close: 复权后前收价
            latest_time: 最新成交时间
            volume: 成交量
            open: 开盘价
            high: 最高价
            low: 最低价
            change: 涨跌额
            amount: 成交额
            amplitude: 振幅
            market_status: 市场状态 （未开盘，交易中，休市等）
            trading_status:   0: 非交易状态 1: 盘前交易（盘前竞价） 2: 交易中 3: 盘后交易（收市竞价）
            float_shares: 流通股本
            shares: 总股本
            eps: 每股收益
            adr_rate: ADR的比例数据，非ADR的股票为None
            etf: 非0表示该股票是ETF,1表示不带杠杆的etf,2表示2倍杠杆etf,3表示3倍etf杠杆
            listing_date: 上市日期时间戳（该市场当地时间零点），该key可能不存在
            更多字段见 tigeropen.quote.response.stock_details_response.StockDetailsResponse
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(STOCK_DETAIL, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = StockDetailsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.details
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_timeline(self, symbols, include_hour_trading=False, begin_time=-1, lang=None, trade_session=None, **kwargs):
        """
        获取当日分时数据
        :param symbols: 股票代号列表
        :param include_hour_trading: 是否包含盘前盘后分时
        :param begin_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return: pandas.DataFrame, DataFrame 的 column 及含义如下：
            symbol: 证券代码
            time: 精确到毫秒的时间戳
            price: 当前分钟的收盘价
            avg_price: 截至到当前时间的成交量加权均价
            pre_close: 昨日收盘价
            volume: 这一分钟的成交量
            trading_session: 字符串， "pre_market" 表示盘前交易, "regular" 表示盘中交易, "after_hours"表示盘后交易
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.include_hour_trading = include_hour_trading
        params.begin_time = begin_time
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        params.trade_session = get_enum_value(trade_session)
        if 'version' in kwargs:
            params.version = kwargs.get('version')
        else:
            params.version = OPEN_API_SERVICE_VERSION_V3

        request = OpenApiRequest(TIMELINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteTimelineResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.timelines
            else:
                raise ApiException(response.code, response.message)

    def get_timeline_history(self, symbols, date, right=QuoteRight.BR):
        """
        get timeline history data
        :param symbols: security symbol list. like ['AAPL', 'BABA']
        :param date: date of timeline. yyyy-MM-dd format, like "2022-04-12"
        :param right: quote right. QuoteRight.BR: before right，QuoteRight.NR: no right
        :return: pandas.DataFrame, columns explanations：
            symbol: security symbol
            time: time in milliseconds
            price: close price of current minute
            avg_price: volume weighted average price up to now.
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.date = date
        params.right = get_enum_value(right)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(HISTORY_TIMELINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteDataframeResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_bars(self, symbols, period=BarPeriod.DAY, begin_time=-1, end_time=-1, right=QuoteRight.BR, limit=251,
                 lang=None, page_token=None, trade_session=None):
        """
        获取K线数据
        :param symbols: 股票代号列表
        :param period: day: 日K,week: 周K,month:月K ,year:年K,1min:1分钟,5min:5分钟,15min:15分钟,30min:30分钟,60min:60分钟
        :param begin_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: 结束时间. 格式同 begin_time
        :param right: 复权选项 ，QuoteRight.BR: 前复权，nQuoteRight.NR: 不复权
        :param limit: 数量限制
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :param page_token: the token of next page. only supported when exactly one symbol
        :return: pandas.DataFrame 对象，各 column 的含义如下；
            time: 毫秒时间戳
            open: Bar 的开盘价
            close: Bar 的收盘价
            high: Bar 的最高价
            low: Bar 的最低价
            volume: Bar 的成交量
            next_page_token: token of next page
        """
        params = MultipleQuoteParams()
        params.symbols = symbols if isinstance(symbols, list) else [symbols]
        params.period = get_enum_value(period)
        params.begin_time = begin_time
        params.end_time = end_time
        params.right = get_enum_value(right)
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        params.page_token = page_token if len(params.symbols) == 1 else None
        params.trade_session = get_enum_value(trade_session)
        request = OpenApiRequest(KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

    def get_bars_by_page(self, symbol, period=BarPeriod.DAY, begin_time=-1, end_time=-1, total=10000, page_size=1000,
                         right=QuoteRight.BR, time_interval=2, lang=None, trade_session=None):
        """
        request bats by page
        :param symbol: symbol of stock.
        :param period:
        :param begin_time:
        :param end_time: time of the latest bar, excluded
        :param total: Total bars number
        :param page_size: Bars number of each request
        :param right:
        :param time_interval: Time interval between requests
        :param lang:
        :return:
        """
        if begin_time == -1 and end_time == -1:
            raise ApiException(400, 'One of the begin_time or end_time must be specified')
        if isinstance(symbol, list) and len(symbol) != 1:
            raise ApiException(400, 'Paging queries support only one symbol at each request')
        current = 0
        next_page_token = None
        result = list()
        result_df = None
        while current < total:
            if current + page_size >= total:
                page_size = total - current
            current += page_size
            bars = self.get_bars(symbols=symbol, period=period, begin_time=begin_time, end_time=end_time, right=right,
                                 limit=page_size, lang=lang, trade_session=trade_session, page_token=next_page_token)
            if bars.empty:
                result_df = bars
                break
            next_page_token = bars['next_page_token'].iloc[0]
            result.append(bars)
            if not next_page_token:
                break
            time.sleep(time_interval)
        return pd.concat(result).sort_values('time').reset_index(drop=True) if result else result_df

    def get_trade_ticks(self, symbols, trade_session=None, begin_index=None, end_index=None, limit=None, lang=None,
                        **kwargs):
        """
        获取逐笔成交
        :param symbols: 股票代号列表
        :param trade_session: tigeropen.common.consts.TradingSession, like TradingSession.PreMarket
        :param begin_index: 开始索引
        :param end_index: 结束索引
        :param limit: 数量限制
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return: pandas.DataFrame 对象， column 有如下属性：
            index: 索引值
            time: 毫秒时间戳
            price: 成交价
            volume: 成交量
            direction: 价格变动方向，"-"表示向下变动， "+" 表示向上变动
        """
        params = MultipleQuoteParams()
        params.symbols = [symbols] if isinstance(symbols, str) else symbols
        # compatible with version 1.0
        params.symbol = symbols if isinstance(symbols, str) else symbols[0]
        params.trade_session = get_enum_value(trade_session)
        params.begin_index = begin_index
        params.end_index = end_index
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        if 'version' in kwargs:
            params.version = kwargs.get('version')

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

    def get_short_interest(self, symbols, lang=None):
        """
        获取美股的做空数据
        :param symbols: 股票代号列表
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return: pandas.DataFrame 对象，各 column 含义如下：
            symbol: 证券代码
            settlement_date: 收集信息的时间
            short_interest: 未平仓做空股数
            avg_daily_volume: 过去一年的日均成交量
            days_to_cover: 回补天数。使用最近一次获取的未平仓做空股数/日均成交量得到
            percent_of_float: 未平仓股数占流通股本的比重
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(QUOTE_SHORTABLE_STOCKS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ShortInterestResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.short_interests
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_depth_quote(self, symbols, market):
        """
        获取深度行情
        :param symbols:
        :param market: tigeropen.common.consts.Market
        :return:
        数据结构:
            若返回单个 symbol:
            {'symbol': '02833',
             'asks': [(27.4, 300, 2), (27.45, 500, 1), (27.5, 4400, 1), (27.55, 0, 0), (27.6, 5700, 3), (27.65, 0, 0),
                      (27.7, 500, 1), (27.75, 0, 0), (27.8, 0, 0), (27.85, 0, 0)],
             'bids': [(27, 4000, 3), (26.95, 200, 1), (26.9, 0, 0), (26.85, 400, 1), (26.8, 0, 0), (26.75, 0, 0),
                      (26.7, 0, 0), (26.65, 0, 0), (26.6, 0, 0), (26.55, 0, 0)]
            }

            若返回多个 symbol:
            {'02833':
                {'symbol': '02833',
                 'asks': [(27.35, 200, 1), (27.4, 2100, 2), (27.45, 500, 1), (27.5, 4400, 1), (27.55, 0, 0),
                         (27.6, 5700, 3), (27.65, 0, 0), (27.7, 500, 1), (27.75, 0, 0), (27.8, 0, 0)],
                 'bids': [(27.05, 100, 1), (27, 5000, 4), (26.95, 200, 1), (26.9, 0, 0), (26.85, 400, 1), (26.8, 0, 0),
                        (26.75, 0, 0), (26.7, 0, 0), (26.65, 0, 0), (26.6, 0, 0)]
                },
            '02828':
                {'symbol': '02828',
                 'asks': [(106.6, 6800, 7), (106.7, 110200, 10), (106.8, 64400, 8), (106.9, 80600, 8), (107, 9440, 16),
                        (107.1, 31800, 5), (107.2, 11800, 4), (107.3, 9800, 2), (107.4, 9400, 1), (107.5, 21000, 9)],
                 'bids': [(106.5, 62800, 17), (106.4, 68200, 9), (106.3, 78400, 6), (106.2, 52400, 4), (106.1, 3060, 4),
                         (106, 33400, 4), (105.9, 29600, 3), (105.8, 9600, 2), (105.7, 15200, 2), (105.6, 0, 0)]}
                }

        asks 和 bids 列表项数据含义为 (委托价格，委托数量，委托订单数) :
            [(ask_price1, ask_volume1, order_count), (ask_price2, ask_volume2, order_count), ...]
            [(bid_price1, bid_volume2, order_count), (bid_price2, bid_volume2, order_count), ...]

        """
        params = DepthQuoteParams()
        params.symbols = symbols if isinstance(symbols, list) else [symbols]
        params.market = get_enum_value(market)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(QUOTE_DEPTH, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = DepthQuoteResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.order_book
            else:
                raise ApiException(response.code, response.message)

    def get_option_expirations(self, symbols, market=None):
        """
        返回美股期权的过期日
        :param symbols: 股票代码列表
        :return: pandas.DataFrame， 各 column 的含义如下：
            symbol: 证券代码
            date: 到日期 YYYY-MM-DD 格式的字符串
            timestamp: 到期日，精确到毫秒的时间戳
        """
        params = OptionContractsParams()
        params.symbols = symbols
        params.lang = get_enum_value(self._lang)
        params.market = get_enum_value(market)
        request = OpenApiRequest(OPTION_EXPIRATION, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionExpirationsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.expirations
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_chain(self, symbol, expiry, option_filter=None, return_greek_value=None, market=None, **kwargs):
        """
        query option chain with filter
        :param symbol: underlying stock symbol
        :param expiry: expiration date ( like '2021-06-18' or 1560484800000 )
        :param option_filter: option filter conditions, tigeropen.quote.domain.filter.OptionFilter
        :param return_greek_value: return greek value or not, bool
        :param kwargs: optional. specify option_filter parameters directly without option_filer,
                        like: open_interest_min=100, delta_min=0.1
        :return: pandas.DataFrame，the columns are as follows：
            identifier: option identifier
            symbol: underlying stock symbol
            expiry: option expiration date. timestamp in millisecond, like 1560484800000
            strike: strike price
            put_call: option direction. 'CALL' or 'PUT'
            multiplier: option multiplier
            ask_price:
            ask_size:
            bid_price:
            bid_size:
            pre_close:
            latest_price:
            volume:
            open_interest:
        """
        params = OptionChainParams()
        param = SingleContractParams()
        param.symbol = symbol
        if isinstance(expiry, str) and re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', expiry):
            param.expiry = date_str_to_timestamp(expiry, self._timezone)
        else:
            param.expiry = expiry
        params.contracts = [param]
        if option_filter:
            params.option_filter = option_filter
        elif kwargs:
            params.option_filter = OptionFilter(**kwargs)
        if market:
            params.market = get_enum_value(market)
        params.return_greek_value = return_greek_value
        params.lang = get_enum_value(self._lang)
        params.version = OPEN_API_SERVICE_VERSION_V3
        request = OpenApiRequest(OPTION_CHAIN, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionChainsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.chain
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_briefs(self, identifiers, market = None):
        """
        获取期权最新行情
        :param identifiers: 期权代码列表
        :return: pandas.DataFrame， 各 column 的含义如下：
            identifier: 期权代码
            symbol: 期权对应的正股代码
            expiry: 到期日，毫秒级时间戳
            strike: 行权价
            put_call: 期权方向
            multiplier: 乘数
            ask_price: 卖价
            ask_size: 卖量
            bid_price: 买价
            bid_size: 买量
            pre_close: 前收价
            latest_price: 最新价
            latest_time: 最新交易时间
            volume: 成交量
            open_interest: 未平仓数量
            open: 开盘价
            high: 最高价
            low: 最低价
            rates_bonds: 无风险利率
            volatility: 历史波动率
        """
        params = OptionContractsParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = date_str_to_timestamp(expiry, self._timezone)
            param.put_call = put_call
            param.strike = strike
            contracts.append(param)
        params.option_basics = contracts
        if market:
            params.market = get_enum_value(market)
        # params.version = OPEN_API_SERVICE_VERSION_V3
        request = OpenApiRequest(OPTION_BRIEF, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_bars(self, identifiers, begin_time=-1, end_time=4070880000000, period=BarPeriod.DAY, limit=None,
                        sort_dir=None, market=None):
        """
        获取期权日K数据
        :param identifiers: 期权代码列表
        :param begin_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: 结束时间. 格式同 begin_time
        :param period: 时间间隔. 可选值: DAY("day"), ONE_MINUTE("1min"), FIVE_MINUTES("5min"), HALF_HOUR("30min"),
            ONE_HOUR("60min");
        :param limit: 每个期权的返回k线数量
        :param sort_dir: tigeropen.common.consts.SortDirection, e.g. SortDirection.DESC
        :return: pandas.DataFrame, 各 column 含义如下：
            time: 毫秒级时间戳
            open: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            volume: 成交量
            open_interest: 未平仓数量
            expiry: 期权到期时间
            strike: 行权价
            put_call: 期权方向
        """
        params = OptionContractsParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleOptionQuoteParams()
            param.symbol = symbol
            param.expiry = date_str_to_timestamp(expiry, self._timezone)
            param.put_call = put_call
            param.strike = strike
            param.period = get_enum_value(period)
            param.begin_time = date_str_to_timestamp(begin_time, self._timezone)
            param.end_time = date_str_to_timestamp(end_time, self._timezone)
            param.limit = limit
            param.sort_dir = get_enum_value(sort_dir)
            contracts.append(param)
        params.option_query = contracts
        if market:
            params.market = get_enum_value(market)
        request = OpenApiRequest(OPTION_KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionQuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

    def get_option_trade_ticks(self, identifiers):
        """
        获取期权逐笔成交
        :param identifiers: 期权代码列表
        :return: pandas.DataFrame, 各 column 的含义如下：
            symbol: 期权对应的正股代码
            expiry: 期权到期时间， YYYY-MM-DD 格式的字符串
            put_call: 期权方向
            strike: 行权价
            time: 成交时间
            price: 成交价格
            volume: 成交量
        """
        params = MultipleContractParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = date_str_to_timestamp(expiry, timezone=self._timezone)
            param.put_call = put_call
            param.strike = strike
            contracts.append(param)
        params.contracts = contracts
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(OPTION_TRADE_TICK, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionTradeTickResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trade_ticks
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_symbols(self, market: Market = Market.HK, lang: Language = Language.en_US):
        """
        获取港股期权合约代码
        :param market: Market
        :param lang: Language
        :return: list
        """
        params = MarketParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang)
        request = OpenApiRequest(ALL_HK_OPTION_SYMBOLS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionSymbolsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_option_depth(self, identifiers, market: Market = Market.US):
        """
        获取期权深度
        :param market:
        :param identifiers: 期权代码列表
        """
        params = OptionContractsParams()
        contracts = []
        if isinstance(identifiers, str):
            identifiers = [identifiers]
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = date_str_to_timestamp(expiry, timezone=self._timezone)
            param.put_call = put_call
            param.strike = strike
            contracts.append(param)
        params.option_basics = contracts
        params.market = get_enum_value(market)
        request = OpenApiRequest(OPTION_DEPTH, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionDepthQuoteResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_future_exchanges(self, sec_type=SecurityType.FUT, lang=None):
        """
        获取期货交易所列表
        :param sec_type: FUT: 期货;  FOP: 期货期权
        :param lang:
        :return: pandas.DataFrame ， 各 column 的含义如下：
            code: 交易所代码
            name: 交易所名称
            zone: 交易所所在时区
        """
        params = MarketParams()
        params.sec_type = get_enum_value(sec_type)
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(FUTURE_EXCHANGE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureExchangeResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.exchanges
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_contracts(self, exchange, lang=None):
        """
        获取交易所下的可交易合约
        :param exchange:
        :param lang:
        :return: pandas.DataFrame, 各 column 含义如下：
            contract_code: 合约代码
            type: 期货合约对应的交易品种， 如 CL
            name: 期货合约的名称
            contract_month: 合约交割月份
            currency: 交易的货币
            first_notice_date: 第一通知日，合约在第一通知日后无法开多仓。已有的多仓会在第一通知日之前（通常为前三个交易日）被强制平仓。
            last_bidding_close_time: 竞价截止时间
            last_trading_date: 最后交易日
            trade: 是否可交易
            continuous: 是否为连续合约
        """
        params = FutureExchangeParams()
        params.exchange_code = exchange
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(FUTURE_CONTRACT_BY_EXCHANGE_CODE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_current_future_contract(self, future_type, lang=None):
        """
        查询指定品种的当前合约
        :param future_type: 期货合约对应的交易品种， 如 CL
        :param lang:
        :return: pandas.DataFrame, 各 column 的含义如下：
            contract_code: 合约代码
            type: 期货合约对应的交易品种， 如 CL
            name: 期货合约的名称
            contract_month: 合约交割月份
            currency: 交易的货币
            first_notice_date: 第一通知日，合约在第一通知日后无法开多仓。已有的多仓会在第一通知日之前（通常为前三个交易日）被强制平仓。
            last_bidding_close_time: 竞价截止时间
            last_trading_date: 最后交易日
            trade: 是否可交易
            continuous: 是否为连续合约
        """
        params = FutureContractParams()
        params.type = future_type
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(FUTURE_CURRENT_CONTRACT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_all_future_contracts(self, future_type, lang=None):
        """
        Query all option_basics of a given type
        :param future_type: like CL, VIX
        :param lang: language
        :return: same as "get_current_future_contract"
        """
        params = FutureContractParams()
        params.type = future_type
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(FUTURE_CONTRACTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_contract(self, contract_code, lang=None):
        """
        get future contract by contract_code
        :param contract_code: code of future contract, like VIX2206, CL2203
        :param lang:
        :return: pandas.DataFrame
        """
        params = FutureContractParams()
        params.contract_code = contract_code
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

        request = OpenApiRequest(FUTURE_CONTRACT_BY_CONTRACT_CODE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_continuous_contracts(self, future_type=None, lang=None):
        """
        Get Future Continuous Contracts
        :param future_type:  'CL'
        :param lang: zh_CN,zh_TW,en_US
        :return: pandas.DataFrame
        contract_code  continuous contract_month currency  display_multiplier exchange exchange_code first_notice_date  last_bidding_close_time last_trading_date  min_tick  multiplier     name symbol  trade type
0        CLmain       False                     USD                   1    NYMEX         NYMEX                                          0                        0.01      1000.0  WTI原油主连     CL   True   CL

        """
        params = FutureContractParams()
        params.type = future_type
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        
        request = OpenApiRequest(FUTURE_CONTINUOUS_CONTRACTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content, skip_main=False)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_trading_times(self, identifier, trading_date=None):
        """
        查询指定期货合约的交易时间
        :param identifier: 合约代码
        :param trading_date: 指定交易日的时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                             或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :return: pandas.DataFrame， 各column含义如下：
            start: 交易开始时间
            end: 交易结束时间
            trading: 是否为连续交易
            bidding: 是否为竞价交易
            zone: 时区
        """
        params = FutureTradingTimeParams()
        params.contract_code = identifier
        params.trading_date = trading_date
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FUTURE_TRADING_DATE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureTradingTimesResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trading_times
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_bars(self, identifiers, period=BarPeriod.DAY, begin_time=-1, end_time=-1, limit=1000,
                        page_token=None):
        """
        获取期货K线数据
        :param identifiers: 期货代码列表
        :param period: day: 日K,week: 周K,month:月K ,year:年K,1min:1分钟,5min:5分钟,15min:15分钟,30min:30分钟,60min:60分钟
        :param begin_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数;
        :param end_time: 结束时间. 格式同 begin_time
        :param limit: 数量限制
        :param page_token: the token of next page. only supported when there exactly one identifier
        :return: pandas.DataFrame, 各column 含义如下：
            identifier: 期货合约代码
            time: Bar对应的时间戳, 即Bar的结束时间。Bar的切割方式与交易所一致，以CN1901举例，T日的17:00至T+1日的16:30的数据会被合成一个日级Bar。
            latest_time: Bar 最后的更新时间
            open: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            settlement: 结算价，在未生成结算价时返回0
            volume: 成交量
            open_interest: 未平仓合约数量
            next_page_token: token of next page
        """
        params = FutureQuoteParams()
        params.contract_codes = identifiers if isinstance(identifiers, list) else [identifiers]
        params.period = get_enum_value(period)
        params.begin_time = date_str_to_timestamp(begin_time, self._timezone)
        params.end_time = end_time
        params.limit = limit
        params.page_token = page_token if len(params.contract_codes) == 1 else None
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FUTURE_KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureQuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

    def get_future_bars_by_page(self, identifier, period=BarPeriod.DAY, begin_time=-1, end_time=-1, total=10000,
                                page_size=1000, time_interval=2):
        """
        request bats by page
        :param identifier: identifier of future
        :param period:
        :param begin_time:
        :param end_time: time of the latest bar, excluded
        :param total: Total bars number
        :param page_size: Bars number of each request
        :param time_interval: Time interval between requests
        :return:
        """
        if begin_time == -1 and end_time == -1:
            raise ApiException(400, 'One of the begin_time or end_time must be specified')
        if isinstance(identifier, list) and len(identifier) != 1:
            raise ApiException(400, 'Paging queries support only one identifier at each request')
        current = 0
        next_page_token = None
        result = list()
        result_df = None
        while current < total:
            if current + page_size >= total:
                page_size = total - current
            current += page_size
            bars = self.get_future_bars(identifiers=identifier, period=period, begin_time=begin_time, end_time=end_time,
                                        limit=page_size, page_token=next_page_token)
            if bars.empty:
                result_df = bars
                break
            next_page_token = bars['next_page_token'].iloc[0]
            result.append(bars)
            if not next_page_token:
                break
            time.sleep(time_interval)
        return pd.concat(result).sort_values('time').reset_index(drop=True) if result else result_df

    def get_future_trade_ticks(self, identifier, begin_index=0, end_index=30, limit=1000):
        """
        获取期货逐笔成交
        :param identifier: future identifier. Only supports one identifier
        :param begin_index: 开始索引
        :param end_index: 结束索引
        :param limit: 数量限制
        :return: pandas.DataFrame, 各 column 含义如下
            index: 索引值
            time: 成交时间，精确到毫秒的时间戳
            price: 成交价格
            volume: 成交量
        """
        params = FutureQuoteParams()
        # Compatible with previous version (previous version 'identifiers' argument is a list)
        params.contract_code = identifier
        if isinstance(identifier, list):
            self.logger.warning("the 'identifier' argument should be a string")
            params.contract_code = identifier[0]
        params.begin_index = begin_index
        params.end_index = end_index
        params.limit = limit
        params.lang = get_enum_value(self._lang)
        params.version = OPEN_API_SERVICE_VERSION_V3
        request = OpenApiRequest(FUTURE_TICK, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureTradeTickResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trade_ticks
            else:
                raise ApiException(response.code, response.message)

    def get_future_brief(self, identifiers):
        """
        获取期货最新行情
        :param identifiers: 期货代码列表
        :return: pandas.DataFrame，各 column 含义如下
            identifier: 期货代码
            ask_price: 卖价
            ask_size: 卖量
            bid_price: 买价
            bid_size: 买量
            pre_close: 前收价
            latest_price: 最新价
            latest_size: 最新成交量
            latest_time: 最新价成交时间
            volume: 当日累计成交手数
            open_interest: 未平仓合约数量
            open: 开盘价
            high: 最高价
            low: 最低价
            limit_up: 涨停价
            limit_down: 跌停价
        """
        params = FutureQuoteParams()
        params.contract_codes = identifiers if isinstance(identifiers, list) else [identifiers]
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FUTURE_REAL_TIME_QUOTE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

    def get_corporate_split(self, symbols, market, begin_date, end_date):
        """
        获取公司拆合股数据
        :param symbols: 证券代码列表
        :param market: 查询的市场. 可选的值为 common.consts.Market 枚举类型, 如 Market.US
        :param begin_date: 起始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_date: 截止时间. 格式同 begin_date
        :return: pandas.DataFrame, 各 column 的含义如下:
            symbol: 证券代码
            action_type: 固定为 "SPLIT"
            from_factor: 公司行动前的因子
            to_factor: 公司行动后的因子
            ratio: 拆合股比例
            excute_date: 除权除息日
            market: 所属市场
            exchange: 所属交易所
        """
        params = CorporateActionParams()
        params.action_type = CorporateActionType.SPLIT.value
        params.symbols = symbols
        params.market = get_enum_value(market)
        params.begin_date = date_str_to_timestamp(begin_date, self._timezone)
        params.end_date = date_str_to_timestamp(end_date, self._timezone)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(CORPORATE_ACTION, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = CorporateSplitResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.corporate_split
            else:
                raise ApiException(response.code, response.message)

    def get_corporate_dividend(self, symbols, market, begin_date, end_date):
        """
        获取公司派息数据
        :param symbols: 证券代码列表
        :param market: 查询的市场. 可选的值为 common.consts.Market 枚举类型, 如 Market.US
        :param begin_date: 起始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_date: 截止时间. 格式同 begin_date
        :return: pandas.DataFrame, 各 column 的含义如下:
            symbol: 证券代码
            action_type: 固定为 "DIVIDEND"
            amount: 分红金额
            currency: 分红货币类型
            announced_date: 公告日期
            excute_date: 除权除息日
            record_date: 股权登记日
            pay_date: 现金到账日
            market: 所属市场
            exchange: 所属交易所
        """
        params = CorporateActionParams()
        params.action_type = CorporateActionType.DIVIDEND.value
        params.symbols = symbols
        params.market = get_enum_value(market)
        params.begin_date = date_str_to_timestamp(begin_date, self._timezone)
        params.end_date = date_str_to_timestamp(end_date, self._timezone)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(CORPORATE_ACTION, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = CorporateDividendResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.corporate_dividend
            else:
                raise ApiException(response.code, response.message)

    def get_corporate_earnings_calendar(self, market, begin_date, end_date):
        """
        获取公司财报日历
        :param market:
        :param begin_date: 起始时间
        :param end_date: 截止时间
        :return:
        """
        params = CorporateActionParams()
        params.action_type = CorporateActionType.EARNINGS_CALENDAR.value
        params.market = get_enum_value(market)
        params.begin_date = date_str_to_timestamp(begin_date, self._timezone)
        params.end_date = date_str_to_timestamp(end_date, self._timezone)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(CORPORATE_ACTION, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = EarningsCalendarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.earnings_calendar
            else:
                raise ApiException(response.code, response.message)

    def get_financial_daily(self, symbols, market, fields, begin_date, end_date):
        """
        获取日级的财务数据
        :param symbols: 证券代码列表
        :param market: 查询的市场. 可选的值为 common.consts.Market 枚举类型, 如 Market.US
        :param fields: 查询的字段列表, 可选的项为 common.consts.Valuation 枚举类型, 如 Valuation.shares_outstanding
        :param begin_date: 开始时间.  如: '2019-01-01'
        :param end_date: 结束时间. 格式同 begin_date
        :return: pandas.DataFrame, 各 column 的含义如下:
            symbol: 证券代码
            field: 查询的字段名称
            date: 查询的日期
            value: 字段对应的值
        """
        params = FinancialDailyParams()
        params.symbols = symbols
        params.market = get_enum_value(market)
        params.fields = [get_enum_value(field) for field in fields]
        params.begin_date = date_str_to_timestamp(begin_date, self._timezone)
        params.end_date = date_str_to_timestamp(end_date, self._timezone)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FINANCIAL_DAILY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FinancialDailyResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.financial_daily
            else:
                raise ApiException(response.code, response.message)

    def get_financial_report(self, symbols, market, fields, period_type, begin_date=None, end_date=None):
        """
        获取财报数据
        :param symbols:
        :param market: 查询的市场. 可选的值为 common.consts.Market 枚举类型, 如 Market.US
        :param fields: 查询的字段列表. 可选的项为 common.consts 下的 Income, Balance, CashFlow, BalanceSheetRatio,
                        Growth, Leverage, Profitability 枚举类型. 如 Income.total_revenue
        :param period_type: 查询的周期类型. 可选的值为 common.consts.FinancialReportPeriodType 枚举类型
        :param begin_date: specify range begin of period_end_date
        :param end_date: specify range end of period_end_date
        :return: pandas.DataFrame, 各 column 的含义如下:
            symbol: 证券代码
            currency: 财报使用的币种
            field: 查询的字段名称
            value: 字段对应的值
            period_end_date: 这条记录对应财报的所属自然季度日期
            filing_date: 财报的发布日期
        """
        params = FinancialReportParams()
        params.symbols = symbols
        params.market = get_enum_value(market)
        params.fields = [get_enum_value(field) for field in fields]
        params.period_type = get_enum_value(period_type)
        params.lang = get_enum_value(self._lang)
        params.begin_date = date_str_to_timestamp(begin_date, self._timezone)
        params.end_date = date_str_to_timestamp(end_date, self._timezone)
        request = OpenApiRequest(FINANCIAL_REPORT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FinancialReportResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.financial_report
            else:
                raise ApiException(response.code, response.message)

    def get_financial_currency(self, symbols, market):
        """
        获取财务币种
        :param symbols: 证券代码列表
        :param market: 查询的市场. 可选的值为 common.consts.Market 枚举类型, 如 Market.US
        :return: pandas.DataFrame
              symbol currency company_currency
            0   AAPL      USD              USD
            1   GOOG      USD              USD
        """
        params = FinancialReportParams()
        params.symbols = symbols
        params.market = get_enum_value(market)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FINANCIAL_CURRENCY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = DataframeResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_financial_exchange_rate(self, currency_list, begin_date, end_date=None, timezone=None):
        """
        获取货币和美元兑换的汇率（1美元换多少单位其他货币）
        :param currency_list: 财务币种列表
        :param begin_date: 起始时间
        :param end_date: 截止时间
        :param timezone: 时区
        :return: pandas.DataFrame
          currency           date    value
        0      HKD  1691942400000  7.81728
        1      USD  1691942400000  1.00000
        """
        tz = timezone if timezone else self._timezone
        params = FinancialExchangeRateParams()
        params.currency_list = currency_list
        params.begin_date = date_str_to_timestamp(begin_date, tz)
        if end_date is None:
            end_date = begin_date
        params.end_date = date_str_to_timestamp(end_date, tz)
        params.timezone = str(tz)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FINANCIAL_EXCHANGE_RATE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FinancialExchangeRateResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result

    def get_industry_list(self, industry_level=IndustryLevel.GGROUP):
        """
        获取行业列表
        :param industry_level: 行业级别. 可选值为 common.consts.IndustryLevel 枚举类型. 默认一级行业
        :return: 由行业信息 dict 构成的列表. industry_level 为行业级别, id 为行业 id
          如 [{'industry_level': 'GGROUP', 'id': '5020', 'name_cn': '媒体与娱乐', 'name_en': 'Media & Entertainment'},
             {'industry_level': 'GGROUP', 'id': '2550', 'name_cn': '零售业', 'name_en': 'Retailing'},
             ...]
        """
        params = IndustryParams()
        params.industry_level = get_enum_value(industry_level)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(INDUSTRY_LIST, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = IndustryListResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.industry_list
            else:
                raise ApiException(response.code, response.message)

    def get_industry_stocks(self, industry, market=Market.US):
        """
        获取某行业下的股票列表
        :param industry: 行业 id
        :param market: 市场枚举类型
        :return: 公司信息列表.
            如 [{'symbol': 'A', 'company_name': 'A', 'market': 'US', 'industry_list': [{...}, {...},..]},
               {'symbol': 'B', 'company_name': 'B', 'market': 'US', 'industry_list': [{...}, {...},..]},
               ...]
        """
        params = IndustryParams()
        params.market = get_enum_value(market)
        params.industry_id = industry
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(INDUSTRY_STOCKS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = IndustryStocksResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.industry_stocks
            else:
                raise ApiException(response.code, response.message)

    def get_stock_industry(self, symbol, market=Market.US):
        """
        获取股票的行业
        :param symbol: 股票 symbol
        :param market: 市场枚举类型
        :return: 所属多级行业的列表
            如 [{'industry_level': 'GSECTOR', 'id': '45', 'name_cn': '信息技术', 'name_en': 'Information Technology'},
              {'industry_level': 'GGROUP', 'id': '4520', 'name_cn': '技术硬件与设备', 'name_en': 'Technology Hardware & Equipment'},
              {'industry_level': 'GIND', 'id': '452020', 'name_cn': '电脑与外围设备', 'name_en': 'Technology Hardware, Storage & Peripherals'},
              {'industry_level': 'GSUBIND', 'id': '45202030', 'name_cn': '电脑硬件、储存设备及电脑周边', 'name_en': 'Technology Hardware, Storage & Peripherals'}]
        """
        params = IndustryParams()
        params.symbol = symbol
        params.market = get_enum_value(market)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(STOCK_INDUSTRY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = StockIndustryResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.stock_industry
            else:
                raise ApiException(response.code, response.message)

    def market_scanner(self, market=Market.US, filters=None, sort_field_data=None, page=0, page_size=100):
        """
        screen stocks
        :param market: tigeropen.common.consts.Market
        :param filters: list of tigeropen.quote.domain.filter.StockFilter
        :param sort_field_data: tigeropen.quote.domain.filter.FilterSortData
        :param page: page begin number
        :param page_size: page size limit
        :return:
        """
        params = MarketScannerParams()
        params.version = OPEN_API_SERVICE_VERSION_V1
        params.market = get_enum_value(market)
        if filters is not None:
            params.base_filter_list = list()
            params.accumulate_filter_list = list()
            params.financial_filter_list = list()
            params.multi_tags_filter_list = list()
            for f in filters:
                if f.field_belong_type == FieldBelongType.BASE:
                    params.base_filter_list.append(f.to_dict())
                elif f.field_belong_type == FieldBelongType.ACCUMULATE:
                    params.accumulate_filter_list.append(f.to_dict())
                elif f.field_belong_type == FieldBelongType.FINANCIAL:
                    params.financial_filter_list.append(f.to_dict())
                elif f.field_belong_type == FieldBelongType.MULTI_TAG:
                    params.multi_tags_filter_list.append(f.to_dict())
        if sort_field_data is not None:
            params.sort_field_data = sort_field_data
        params.page = page
        params.page_size = page_size
        request = OpenApiRequest(MARKET_SCANNER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = MarketScannerResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_market_scanner_tags(self, market=Market.US, tag_fields=None):
        """
        :param market: tigeropen.common.consts.Market
        :param tag_fields: tigeropen.common.consts.filter_fields.MultiTagField
        """
        params = MarketScannerParams()
        params.market = get_enum_value(market)
        params.multi_tags_fields = tag_fields
        request = OpenApiRequest(MARKET_SCANNER_TAGS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = MarketScannerTagsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
    def grab_quote_permission(self):
        """
        抢占行情权限
        :return: 权限列表。expire_at 为-1时表示长期有效
        示例: [{'name': 'usQuoteBasic', 'expire_at': 1621931026000},
              {'name': 'usStockQuoteLv2Totalview', 'expire_at': 1621931026000},
              {'name': 'usOptionQuote', 'expire_at': 1621931026000},
              {'name': 'hkStockQuoteLv2', 'expire_at': -1}]
        """
        request = OpenApiRequest(GRAB_QUOTE_PERMISSION)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteGrabPermissionResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.permissions
            else:
                raise ApiException(response.code, response.message)

    def get_quote_permission(self):
        """
        查询行情权限。query quote permissions
        :return: 权限列表。expire_at 为-1时表示长期有效
        示例: [{'name': 'usQuoteBasic', 'expire_at': 1621931026000},
              {'name': 'usStockQuoteLv2Totalview', 'expire_at': 1621931026000},
              {'name': 'usOptionQuote', 'expire_at': 1621931026000},
              {'name': 'hkStockQuoteLv2', 'expire_at': -1}]
        """
        request = OpenApiRequest(GET_QUOTE_PERMISSION)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteGrabPermissionResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.permissions
            else:
                raise ApiException(response.code, response.message)

    def get_trading_calendar(self, market, begin_date=None, end_date=None):
        """
        get trading calendar
        :param market:  common.consts.Market, like Market.US
        :param begin_date:
        :param end_date:
        :return:
        """
        params = TradingCalendarParams()
        params.market = get_enum_value(market)
        params.begin_date = begin_date
        params.end_date = end_date
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(TRADING_CALENDAR, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = TradingCalendarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.calendar
            else:
                raise ApiException(response.code, response.message)

    def get_stock_broker(self, symbol, limit=40, lang=None):
        """Get stock broker information
        :param symbol:
        :param limit: The maximum number of items returned. Default value is 40.
        :param lang: tigeropen.common.consts.Language
        return: tigeropen.quote.domain.stock_broker.StockBroker
        example:
        StockBroker({'symbol': '01810',
            'bid_broker': [
                LevelBroker({'level': 1, 'price': 11.46, 'broker_count': 5,
                    'broker': [Broker({'id': '5999', 'name': '中国创盈'}), Broker({'id': '4374', 'name': '巴克莱亚洲'}),
                            Broker({'id': '1438', 'name': 'Susquehanna'}), Broker({'id': '4821', 'name': '华盛'}),
                             Broker({'id': '6998', 'name': '中国投资'})]})],
            'ask_broker': [
                LevelBroker({'level': 1, 'price': 11.48, 'broker_count': 5,
                    'broker': [Broker({'id': '4374', 'name': '巴克莱亚洲'}), Broker({'id': '9056', 'name': '瑞银'}),
                            Broker({'id': '2027', 'name': '东亚'}), Broker({'id': '4821', 'name': '华盛'}),
                            Broker({'id': '4374', 'name': '巴克莱亚洲'})]})]})
        """
        params = StockBrokerParams()
        params.symbol = symbol
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        request = OpenApiRequest(STOCK_BROKER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = StockBrokerResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_capital_flow(self, symbol, market, period, begin_time=-1, end_time=-1, limit=200, lang=None):
        """Get capital net inflow Data, including different time periods, such as daily, weekly, monthly, etc.
        :param symbol: 股票代号
        :param market: tigeropen.common.consts.Market
        :param period: period, possible values are: intraday, day, week, month, year, quarter, 6month
        :param begin_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: 结束时间. 格式同 begin_time
        :param limit: 数量限制
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return pandas.DataFrame, example:
                   time      timestamp    net_inflow symbol period
        0    2022-02-24  1645678800000 -5.889058e+08   AAPL    day
        1    2022-02-25  1645765200000 -1.229127e+08   AAPL    day
        2    2022-02-28  1646024400000  1.763644e+08   AAPL    day
        """
        params = CapitalParams()
        params.symbol = symbol
        params.market = get_enum_value(market)
        params.period = get_enum_value(period)
        params.begin_time = begin_time
        params.end_time = end_time
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        request = OpenApiRequest(CAPITAL_FLOW, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = CapitalFlowResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_capital_distribution(self, symbol, market, lang=None):
        """Get capital distribution.
        :param symbol: 股票代号
        :param market: tigeropen.common.consts.Market
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        return: tigeropen.quote.domain.capital_distribution.CapitalDistribution
        """
        params = CapitalParams()
        params.symbol = symbol
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)
        request = OpenApiRequest(CAPITAL_DISTRIBUTION, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = CapitalDistributionResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_warrant_briefs(self, symbols):
        """
        get warrant/iopt quote
        :param symbols:
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols if isinstance(symbols, list) else [symbols]
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(WARRANT_REAL_TIME_QUOTE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = WarrantBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_warrant_filter(self, symbol, page=None, page_size=None, sort_field_name=None, sort_dir=None,
                           filter_params=None):
        """
        :param sort_dir: tigeropen.common.consts.SortDirection, e.g. SortDirection.DESC
        :param filter_params: tigeropen.quote.request.model.WarrantFilterParams
        :return:
        """
        params = WarrantFilterParams()
        params.lang = get_enum_value(self._lang)
        params.symbol = symbol or (filter_params.symbol if filter_params else None)
        params.page = page or (filter_params.page if filter_params else None)
        params.page_size = page_size or (filter_params.page_size if filter_params else None)
        params.sort_field_name = sort_field_name or (filter_params.sort_field_name if filter_params else None)
        params.sort_dir = get_enum_value(sort_dir or (filter_params.sort_dir if filter_params else None))
        if filter_params:
            params.warrant_type = filter_params.warrant_type
            params.in_out_price = filter_params.in_out_price
            params.issuer_name = filter_params.issuer_name
            params.expire_ym = filter_params.expire_ym
            params.lot_size = filter_params.lot_size
            params.entitlement_ratio = filter_params.entitlement_ratio
            params.leverage_ratio = filter_params.leverage_ratio
            params.strike = filter_params.strike
            params.premium = filter_params.premium
            params.outstanding_ratio = filter_params.outstanding_ratio
            params.implied_volatility = filter_params.implied_volatility
            params.effective_leverage = filter_params.effective_leverage
            params.call_price = filter_params.call_price
            params.state = filter_params.state

        request = OpenApiRequest(WARRANT_FILTER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = WarrantFilterResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_kline_quota(self, with_details=False):
        params = KlineQuotaParams()
        params.lang = get_enum_value(self._lang)
        params.with_details = with_details
        request = OpenApiRequest(KLINE_QUOTA, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = KlineQuotaResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_fund_symbols(self):
        params = SymbolsParams()
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FUND_ALL_SYMBOLS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SymbolsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_fund_contracts(self, symbols):
        params = MultipleQuoteParams()
        params.symbols = symbols if isinstance(symbols, list) else [symbols]
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FUND_CONTRACTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FundContractsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_fund_quote(self, symbols):
        params = MultipleQuoteParams()
        params.symbols = symbols if isinstance(symbols, list) else [symbols]
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FUND_QUOTE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = StockBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

    def get_fund_history_quote(self, symbols, begin_time, end_time, limit=None):
        params = MultipleQuoteParams()
        params.symbols = symbols if isinstance(symbols, list) else [symbols]
        params.begin_time = begin_time
        params.end_time = end_time
        params.limit = limit
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(FUND_HISTORY_QUOTE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteDataframeResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
            
    def get_stock_fundamental(self, symbols, market):
        params = MultipleQuoteParams()
        params.symbols = symbols if isinstance(symbols, list) else [symbols]
        params.market = get_enum_value(market)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(STOCK_FUNDAMENTAL, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteDataframeResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_trade_rank(self, market, lang=Language.en_US):
        params = MarketParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang)
        request = OpenApiRequest(TRADE_RANK, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = TradeRankResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    