# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import re
import enum
import delorean
import six

from tigeropen.common.consts import THREAD_LOCAL, SecurityType, CorporateActionType
from tigeropen.common.exceptions import ApiException
from tigeropen.fundamental.request.model import FinancialDailyParams, FinancialReportParams, CorporateActionParams
from tigeropen.fundamental.response.corporate_dividend_response import CorporateDividendResponse
from tigeropen.fundamental.response.corporate_split_response import CorporateSplitResponse
from tigeropen.fundamental.response.financial_report_response import FinancialReportResponse
from tigeropen.fundamental.response.financial_daily_response import FinancialDailyResponse
from tigeropen.quote.response.future_briefs_response import FutureBriefsResponse
from tigeropen.quote.response.future_exchange_response import FutureExchangeResponse
from tigeropen.quote.response.future_contract_response import FutureContractResponse
from tigeropen.quote.response.future_quote_bar_response import FutureQuoteBarResponse
from tigeropen.quote.response.future_quote_ticks_response import FutureTradeTickResponse
from tigeropen.quote.response.future_trading_times_response import FutureTradingTimesResponse
from tigeropen.quote.response.option_briefs_response import OptionBriefsResponse
from tigeropen.quote.response.option_chains_response import OptionChainsResponse
from tigeropen.quote.response.option_expirations_response import OptionExpirationsResponse
from tigeropen.quote.response.option_quote_bar_response import OptionQuoteBarResponse
from tigeropen.quote.response.option_quote_ticks_response import OptionTradeTickResponse
from tigeropen.quote.response.quote_bar_response import QuoteBarResponse
from tigeropen.quote.response.quote_timeline_response import QuoteTimelineResponse
from tigeropen.quote.response.quote_brief_response import QuoteBriefResponse
from tigeropen.quote.response.stock_briefs_response import StockBriefsResponse
from tigeropen.quote.response.stock_short_interest_response import ShortInterestResponse
from tigeropen.quote.response.stock_trade_meta_response import TradeMetaResponse
from tigeropen.quote.response.symbol_names_response import SymbolNamesResponse
from tigeropen.quote.response.symbols_response import SymbolsResponse
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.quote.request.model import MarketParams, MultipleQuoteParams, MultipleContractParams, \
    FutureQuoteParams, FutureExchangeParams, FutureTypeParams, FutureTradingTimeParams, SingleContractParams, \
    SingleOptionQuoteParams
from tigeropen.quote.request import OpenApiRequest
from tigeropen.quote.response.quote_ticks_response import TradeTickResponse
from tigeropen.quote.response.market_status_response import MarketStatusResponse
from tigeropen.common.consts.service_types import MARKET_STATE, ALL_SYMBOLS, ALL_SYMBOL_NAMES, BRIEF, \
    TIMELINE, KLINE, TRADE_TICK, OPTION_EXPIRATION, OPTION_CHAIN, FUTURE_EXCHANGE, OPTION_BRIEF, \
    OPTION_KLINE, OPTION_TRADE_TICK, FUTURE_KLINE, FUTURE_TICK, FUTURE_CONTRACT_BY_EXCHANGE_CODE, \
    FUTURE_TRADING_DATE, QUOTE_SHORTABLE_STOCKS, FUTURE_REAL_TIME_QUOTE, \
    FUTURE_CURRENT_CONTRACT, QUOTE_REAL_TIME, QUOTE_STOCK_TRADE, FINANCIAL_DAILY, FINANCIAL_REPORT, CORPORATE_ACTION
from tigeropen.common.consts import Market, Language, QuoteRight, BarPeriod
from tigeropen.common.util.contract_utils import extract_option_info
from tigeropen.common.util.common_utils import eastern
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

    def __fetch_data(self, request):
        try:
            response = super(QuoteClient, self).execute(request)
            return response
        except Exception as e:
            if THREAD_LOCAL.logger:
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
        :return: 所有 symbol 的列表，包含退市和不可交易的部分代码. 其中以.开头的代码为指数， 如 .DJI 表示道琼斯指数
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
        :return: list, list 中的每个对象是一个 tuple. tuple 的第一个元素是 symbol，第二个是 name
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

    def get_trade_metas(self, symbols):
        """
        获取股票交易需要的信息(最新数量和报价单位等)
        :param symbols: 股票代号列表
        :return: pandas.DataFrame, 各 column 的含义如下:
            symbol: 证券代码
            lot_size: 每股手数
            min_tick: 价格最小变动单位
            spread_scale: 报价精度
        """
        params = MultipleQuoteParams()
        params.symbols = symbols

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

    def get_stock_briefs(self, symbols, lang=None):
        """
        获取股票实时行情
        :param symbols: 股票代号列表
        :param lang: 语言支持: zh_CN,zh_TW,en_US
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
        params.lang = lang.value if lang else self._lang.value

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

    def get_timeline(self, symbols, include_hour_trading=False, begin_time=-1, lang=None):
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
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(TIMELINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteTimelineResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.timelines
            else:
                raise ApiException(response.code, response.message)

    def get_bars(self, symbols, period=BarPeriod.DAY, begin_time=-1, end_time=-1, right=QuoteRight.BR, limit=251,
                 lang=None):
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
        :return: pandas.DataFrame 对象，各 column 的含义如下；
            time: 毫秒时间戳
            open: Bar 的开盘价
            close: Bar 的收盘价
            high: Bar 的最高价
            low: Bar 的最低价
            volume: Bar 的成交量
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
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

    def get_trade_ticks(self, symbols, begin_index=0, end_index=30, limit=30, lang=None):
        """
        获取逐笔成交
        :param symbols: 股票代号列表
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
        params.symbols = symbols
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
        params.lang = lang.value if lang else self._lang.value

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

    def get_option_expirations(self, symbols):
        """
        返回美股期权的过期日
        :param symbols: 股票代码列表
        :return: pandas.DataFrame， 各 column 的含义如下：
            symbol: 证券代码
            date: 到日期 YYYY-MM-DD 格式的字符串
            timestamp: 到期日，精确到毫秒的时间戳
        """
        params = MultipleQuoteParams()
        params.symbols = symbols

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

    def get_option_chain(self, symbol, expiry):
        """
        获取美股期权链
        :param symbol: 股票代码
        :param expiry: 过期日 ( 类似 '2021-06-18' 或者 1560484800000 )
        :return: pandas.DataFrame，各 column 含义如下：
            identifier: 期权代码
            symbol: 期权对应的正股代码
            expiry: 期权到期日，毫秒级别的时间戳
            strike: 行权价
            put_call: 期权的方向
            multiplier: 乘数
            ask_price: 卖价
            ask_size: 卖量
            bid_price: 买价
            bid_size: 买量
            pre_close: 前收价
            latest_price: 最新价
            volume: 成交量
            open_interest: 未平仓数量
        """
        params = MultipleContractParams()
        param = SingleContractParams()
        param.symbol = symbol
        if isinstance(expiry, six.string_types) and re.match('[0-9]{4}\-[0-9]{2}\-[0-9]{2}', expiry):
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
        else:
            param.expiry = expiry
        params.contracts = [param]
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

    def get_option_briefs(self, identifiers):
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
        params = MultipleContractParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
            param.put_call = put_call
            param.strike = strike
            contracts.append(param)
        params.contracts = contracts

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

    def get_option_bars(self, identifiers, begin_time=-1, end_time=4070880000000):
        """
        获取期权日K数据
        :param identifiers: 期权代码列表
        :param begin_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: 结束时间. 格式同 begin_time
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
        params = MultipleContractParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleOptionQuoteParams()
            param.symbol = symbol
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
            param.put_call = put_call
            param.strike = strike
            param.period = BarPeriod.DAY.value
            param.begin_time = begin_time
            param.end_time = end_time
            contracts.append(param)
        params.contracts = contracts

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
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
            param.put_call = put_call
            param.strike = strike
            contracts.append(param)
        params.contracts = contracts

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
        params.sec_type = sec_type.value
        params.lang = lang.value if lang else self._lang.value

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
        params.lang = lang.value if lang else self._lang.value

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
        params = FutureTypeParams()
        params.type = future_type
        params.lang = lang.value if lang else self._lang.value

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

    def get_future_bars(self, identifiers, period=BarPeriod.DAY, begin_time=-1, end_time=-1, limit=1000):
        """
        获取期货K线数据
        :param identifiers: 期货代码列表
        :param period: day: 日K,week: 周K,month:月K ,year:年K,1min:1分钟,5min:5分钟,15min:15分钟,30min:30分钟,60min:60分钟
        :param begin_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: 结束时间. 格式同 begin_time
        :param limit: 数量限制
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
        """
        params = FutureQuoteParams()
        params.contract_codes = identifiers
        if period:
            params.period = period.value
        params.begin_time = begin_time
        params.end_time = end_time
        params.limit = limit

        request = OpenApiRequest(FUTURE_KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureQuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

    def get_future_trade_ticks(self, identifiers, begin_index=0, end_index=30, limit=1000):
        """
        获取期货逐笔成交
        :param identifiers: 期货代码列表
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
        params.contract_codes = identifiers
        params.begin_index = begin_index
        params.end_index = end_index
        params.limit = limit

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
        params.contract_codes = identifiers

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
        params.market = market.value
        params.begin_date = begin_date
        params.end_date = end_date

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
        params.market = market.value
        params.begin_date = begin_date
        params.end_date = end_date

        request = OpenApiRequest(CORPORATE_ACTION, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = CorporateDividendResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.corporate_dividend
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
        params.market = market.value
        params.fields = [field.value if isinstance(field, enum.Enum) else field for field in fields]
        params.begin_date = begin_date
        params.end_date = end_date

        request = OpenApiRequest(FINANCIAL_DAILY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FinancialDailyResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.financial_daily
            else:
                raise ApiException(response.code, response.message)

    def get_financial_report(self, symbols, market, fields, period_type):
        """
        获取财报数据
        :param symbols:
        :param market: 查询的市场. 可选的值为 common.consts.Market 枚举类型, 如 Market.US
        :param fields: 查询的字段列表. 可选的项为 common.consts 下的 Income, Balance, CashFlow, BalanceSheetRatio,
                        Growth, Leverage, Profitability 枚举类型. 如 Income.total_revenue
        :param period_type: 查询的周期类型. 可选的值为 common.consts.FinancialReportPeriodType 枚举类型
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
        params.market = market.value
        params.fields = [field.value if isinstance(field, enum.Enum) else field for field in fields]
        params.period_type = period_type.value

        request = OpenApiRequest(FINANCIAL_REPORT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FinancialReportResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.financial_report
            else:
                raise ApiException(response.code, response.message)
