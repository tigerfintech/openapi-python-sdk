# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import logging
import re
import time
from typing import Optional, Union, List

import pandas as pd

from tigeropen.common.consts import Market, QuoteRight, BarPeriod, OPEN_API_SERVICE_VERSION_V3, \
    OPEN_API_SERVICE_VERSION_V1, Language, SortDirection, TradingSession, Income, Balance, CashFlow, BalanceSheetRatio, \
    Growth, Leverage, Profitability, \
    FinancialReportPeriodType, CapitalPeriod
from tigeropen.common.consts import THREAD_LOCAL, SecurityType, CorporateActionType, IndustryLevel
from tigeropen.common.consts.filter_fields import FieldBelongType
from tigeropen.common.consts.fundamental_fields import Field
from tigeropen.common.consts.service_types import GRAB_QUOTE_PERMISSION, QUOTE_DELAY, GET_QUOTE_PERMISSION, \
    HISTORY_TIMELINE, FUTURE_CONTRACT_BY_CONTRACT_CODE, STOCK_FUNDAMENTAL, TRADE_RANK, TRADING_CALENDAR, \
    FUTURE_CONTRACTS, MARKET_SCANNER, \
    STOCK_BROKER, CAPITAL_FLOW, CAPITAL_DISTRIBUTION, WARRANT_REAL_TIME_QUOTE, WARRANT_FILTER, MARKET_SCANNER_TAGS, \
    KLINE_QUOTA, FUND_ALL_SYMBOLS, FUND_CONTRACTS, FUND_QUOTE, FUND_HISTORY_QUOTE, FINANCIAL_CURRENCY, \
    FINANCIAL_EXCHANGE_RATE, ALL_HK_OPTION_SYMBOLS, OPTION_DEPTH, BROKER_HOLD, OPTION_TIMELINE, FUTURE_DEPTH
from tigeropen.common.consts.service_types import MARKET_STATE, ALL_SYMBOLS, ALL_SYMBOL_NAMES, BRIEF, \
    TIMELINE, KLINE, TRADE_TICK, OPTION_EXPIRATION, OPTION_CHAIN, FUTURE_EXCHANGE, OPTION_BRIEF, \
    OPTION_KLINE, OPTION_TRADE_TICK, FUTURE_KLINE, FUTURE_TICK, FUTURE_CONTRACT_BY_EXCHANGE_CODE, \
    FUTURE_TRADING_DATE, QUOTE_SHORTABLE_STOCKS, FUTURE_REAL_TIME_QUOTE, \
    FUTURE_CURRENT_CONTRACT, QUOTE_REAL_TIME, QUOTE_STOCK_TRADE, FINANCIAL_DAILY, FINANCIAL_REPORT, CORPORATE_ACTION, \
    QUOTE_DEPTH, INDUSTRY_LIST, INDUSTRY_STOCKS, STOCK_INDUSTRY, STOCK_DETAIL, FUTURE_CONTINUOUS_CONTRACTS, \
    QUOTE_OVERNIGHT
from tigeropen.common.exceptions import ApiException
from tigeropen.common.request import OpenApiRequest
from tigeropen.common.util.common_utils import eastern, get_enum_value, date_str_to_timestamp
from tigeropen.common.util.contract_utils import extract_option_info, is_hk_option_underlying_symbol
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
from tigeropen.quote.domain.capital_distribution import CapitalDistribution
from tigeropen.quote.domain.filter import SortFilterData, StockFilter, OptionFilter, ScannerResult
from tigeropen.quote.domain.market_status import MarketStatus
from tigeropen.quote.domain.quote_brief import QuoteBrief
from tigeropen.quote.domain.stock_broker import StockBroker
from tigeropen.quote.request.model import MarketParams, MultipleQuoteParams, MultipleContractParams, \
    FutureQuoteParams, FutureExchangeParams, FutureContractParams, FutureTradingTimeParams, SingleContractParams, \
    SingleOptionQuoteParams, DepthQuoteParams, OptionChainParams, TradingCalendarParams, MarketScannerParams, \
    StockBrokerParams, CapitalParams, WarrantFilterParams, KlineQuotaParams, SymbolsParams, OptionContractsParams, \
    BrokerHoldParams
from tigeropen.quote.response.broker_hold_response import BrokerHoldResponse
from tigeropen.quote.response.capital_distribution_response import CapitalDistributionResponse
from tigeropen.quote.response.capital_flow_response import CapitalFlowResponse
from tigeropen.quote.response.fund_contracts_response import FundContractsResponse
from tigeropen.quote.response.future_briefs_response import FutureBriefsResponse
from tigeropen.quote.response.future_contract_response import FutureContractResponse
from tigeropen.quote.response.future_depth_response import FutureDepthResponse
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
from tigeropen.quote.response.option_timeline_response import OptionTimelineResponse
from tigeropen.quote.response.quote_bar_response import QuoteBarResponse
from tigeropen.quote.response.quote_brief_response import QuoteBriefResponse
from tigeropen.quote.response.quote_dataframe_response import QuoteDataframeResponse
from tigeropen.quote.response.quote_delay_briefs_response import DelayBriefsResponse
from tigeropen.quote.response.quote_depth_response import DepthQuoteResponse
from tigeropen.quote.response.quote_grab_permission_response import QuoteGrabPermissionResponse
from tigeropen.quote.response.quote_overnight_response import QuoteOvernightResponse
from tigeropen.quote.response.quote_ticks_response import TradeTickResponse
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
            self.logger.info('Grab quote permission. Permissions:' +
                             str(self.permissions))

    def __fetch_data(self, request):
        try:
            response = super(QuoteClient, self).execute(request, url=self._url)
            return response
        except Exception as e:
            if hasattr(THREAD_LOCAL, 'logger') and THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e

    def get_market_status(
            self,
            market: Optional[Union[Market, str]] = Market.ALL,
            lang: Optional[Union[Language, str]] = None) -> list[MarketStatus]:
        """
        Get market status. 获取市场状态. 

        :param market: Stock market. 市场. Available values: US/HK/CN/ALL
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: list of MarketStatus. MarketStatus fields:
            market: Market name. 市场名称.
            status: Current market status name. 当前市场所处的状态名称.
            trading_status: Current market status. 当前市场所处的状态枚举值.
            open_time: `datetime.datetime` object with tzinfo, indicating the next opening time. 带 tzinfo 的 datetime 对象，表示下次开盘时间.
        
        :return example:
            [MarketStatus({'market': 'US', 'status': 'Not Yet Opened', 'open_time': datetime.datetime(2025, 8, 12, 9, 30, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>),'trading_status': 'NOT_YET_OPEN'}),
            MarketStatus({'market': 'HK', 'status': 'Trading', 'open_time': datetime.datetime(2025, 8, 13, 9, 30, tzinfo=<DstTzInfo 'Asia/Hong_Kong' HKT+8:00:00 STD>),'trading_status': 'TRADING'}),
            MarketStatus({'market': 'CN', 'status': 'Trading', 'open_time': datetime.datetime(2025, 8, 13, 9, 30, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>), 'trading_status': 'TRADING'})]
        """
        params = MarketParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(MARKET_STATE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = MarketStatusResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.markets
            else:
                raise ApiException(response.code, response.message)
        return list()

    def get_symbols(self,
                    market: Optional[Union[Market, str]] = Market.ALL,
                    include_otc: bool = False) -> list[str]:
        """
        Get symbols of market. 获取市场下的股票代码列表

        :param market: Stock market. 市场. Available values: US/HK/CN/ALL
        :param include_otc: Is include OTC. 是否包含 OTC 股票
        :return: List of symbols, include delisted stocks. 所有 symbol 的列表，包含退市和不可交易的部分代码.
            If start with '.' , it is an index, such as .DJI represents the Dow Jones Index. 如果以 '.' 开头，则表示指数代码，如 .DJI 表示道琼斯指数.
        
        :return example:
            [".DJI", "AAPL", "SPY"]
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

        return list()

    def get_symbol_names(self,
                         market: Optional[Union[Market, str]] = Market.ALL,
                         lang: Optional[Union[Language, str]] = None,
                         include_otc: bool = False) -> list[tuple[str, str]]:
        """
        Get stock symbols and names. 获取股票代码列表和名称

        :param market: Stock market. 市场. Available values: US/HK/CN/ALL
        :param lang: Language. 语言. Available values: zh_CN,zh_TW,en_US. Default value is the `lang` setting in the client config. 默认使用配置中的语言.
        :param include_otc: 是否包含 OTC
        :return: list of tuples, like [(symbol, name), ...]. 返回值为 `(代码, 名称)` 的元组列表.

        :return example:
            [('.DJI', 'Dow Jones'), ('.IXIC', 'NASDAQ'), ('AAPL', 'Apple')]
        """
        params = SymbolsParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
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

        return list()

    def get_trade_metas(self, symbols: list[str]) -> pd.DataFrame:
        """
        Get trade meta information for stocks. 获取股票交易需要的信息

        :param symbols: Stock symbols list. 股票代号列表
        :return: pandas.DataFrame, columns are as follows:
            symbol: Stock symbol. 股票代码
            lot_size: Lot size. 每手股数
            min_tick: Minimum price fluctuation unit. 价格最小变动单位
            spread_scale: Quotation precision. 报价精度

        :return example:
           symbol  lot_size  min_tick  spread_scale
        0   AAPL         1      0.01             1
        1   MSFT         1      0.01             1
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
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

        return pd.DataFrame()

    def get_briefs(
            self,
            symbols: list[str],
            include_hour_trading: Optional[bool] = False,
            include_ask_bid: Optional[bool] = False,
            right: Optional[Union[QuoteRight, str]] = QuoteRight.BR,
            lang: Optional[Union[Language, str]] = None) -> list[QuoteBrief]:
        """
        Get stock brief information. 获取股票摘要信息. (Not Recommended, use get_stock_briefs instead)

        :param symbols: Stock symbols list. 股票代码列表
        :param include_hour_trading: Is include hour trading. 是否包含盘前盘后
        :param include_ask_bid: Is include ask bid. 是否包含买卖盘
        :param right: Quote right. 复权. Available values: br/nr
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: List of QuoteBrief objects. The fields of QuoteBrief as follows:
            symbol: Stock symbol. 股票代码
            market: Market. 市场
            sec_type: Security type. 证券类型
            name: Name. 名称
            ask_price: Ask price. 卖一价
            ask_size: Ask size. 卖一量
            bid_price: Bid price. 买一价
            bid_size: Bid size. 买一量
            latest_price: Latest price. 最新价
            latest_time: Latest trade time. 最新成交时间
            volume: Volume. 成交量
            open_price: Open price. 开盘价
            high_price: High price. 最高价
            low_price: Low price. 最低价
            pre_close: Previous close price. 前收盘价
            halted: Halted. 停牌信息. 0: Normal 正常, 3: Halted 停牌, 4: Delisted 退市
            delay: Delay in minutes. 延时分钟
            auction: Auction info, HK stock only. 是否竞价时段（仅港股）
            expiry: Expiry time, HK stock only. 到期时间（仅港股）
            hour_trading: Hour trading info, includes pre-market and after-hours trading. 盘前盘后交易信息
                hour_trading.trading_session: Trading session, like "pre_market", "regular", "after_hours". 交易时段，如 "pre_market" 盘前交易, "regular" 盘中交易, "after_hours" 盘后交易
                hour_trading.latest_price: Latest price in the trading session. 该交易时段的最新价
                hour_trading.prev_close: Previous close price in the trading session. 该交易时段的前收盘价
                hour_trading.latest_time: Latest trade time in the trading session. 该交易时段的最新成交时间
                hour_trading.volume: Volume in the trading session. 该交易时段的成交量
                hour_trading.open_price: Open price in the trading session. 该交易时段的开盘价
                hour_trading.high_price: High price in the trading session. 该交易时段的最高价
                hour_trading.low_price: Low price in the trading session. 该交易时段的最低价
                hour_trading.change: Change in the trading session. 该交易时段的涨跌额


        :return example:
        [QuoteBrief({'symbol': 'AAPL', 'market': 'US', 'name': 'Apple', 'sec_type': 'STK', 'latest_price': 227.18,
         'prev_close': 229.09, 'latest_time': 1754942400000,
         'volume': None, 'open_price': None, 'high_price': None, 'low_price': None, 'change': None, 
         'bid_price': None, 'bid_size': None, 'ask_price': None, 'ask_size': None, 'halted': 0.0, 'delay': 0, 'auction': None, 'expiry': None, 
          'hour_trading': HourTrading({'trading_session': <TradingSession.AfterHours: 'AfterHours'>, 'latest_price': 226.3225, 'prev_close': 227.18, 'latest_time': 1754956795127, 'volume': 2431140, 'open_price': None, 'high_price': None, 'low_price': None, 'change': None})})]
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.include_hour_trading = include_hour_trading
        params.include_ask_bid = include_ask_bid
        params.right = get_enum_value(right)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(BRIEF, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteBriefResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return list()

    def get_stock_briefs(
            self,
            symbols: list[str],
            include_hour_trading: Optional[bool] = False,
            lang: Optional[Union[str, Language]] = None) -> pd.DataFrame:
        """
        Get stock realtime quote. 获取股票实时行情

        :param symbols: Stock symbols list. 股票代码列表
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :param include_hour_trading: Is include hour trading. 是否包含盘前盘后
        :return: pandas.DataFrame. The columns are as follows:
            symbol: Stock symbol. 股票代码
            ask_price: Ask price. 卖一价
            ask_size: Ask size. 卖一量
            bid_price: Bid price. 买一价
            bid_size: Bid size. 买一量
            pre_close: Previous close. 前收价
            latest_price: Latest price. 最新价
            latest_time: Latest time. 最新成交时间
            volume: Volume. 成交量
            open: Open price. 开盘价
            high: High price. 最高价
            low: Low price. 最低价
            close: Close price. 收盘价
            adj_pre_close: Adjusted previous close. 复权过的前收价
            hour_trading_tag: Hour trading tag. 盘前盘后交易标记
            hour_trading_latest_price: Hour trading latest price. 盘前盘后交易的最新价
            hour_trading_pre_close: Hour trading previous close. 盘前盘后交易的前收价
            hour_trading_latest_time: Hour trading latest time. 盘前盘后交易的最新成交时间
            hour_trading_volume: Hour trading volume. 盘前盘后交易的成交量
            hour_trading_timestamp: Hour trading timestamp. 盘前盘后交易的时间戳
            status: Trading status. 交易状态:
                UNKNOWN: 未知
                NORMAL: 正常
                HALTED: 停牌
                DELIST: 退市
                NEW: 新股
                ALTER: 变更

        :return example:
       symbol    open    high     low   close  pre_close  latest_price    latest_time  ask_price  ask_size  bid_price  bid_size    volume  status  adj_pre_close hour_trading_tag  hour_trading_latest_price  hour_trading_pre_close hour_trading_latest_time  hour_trading_volume  hour_trading_timestamp
     0   AAPL  227.92  229.56  224.76  227.18     229.09        227.18  1754942400000     226.38       363      226.3       227  61806132  NORMAL         227.18          Pre-Mkt                     226.37                  227.18                04:31 EDT                 5841           1754987488932
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.include_hour_trading = include_hour_trading
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(QUOTE_REAL_TIME, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = StockBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return pd.DataFrame()

    def get_stock_delay_briefs(
            self,
            symbols: list[str],
            lang: Optional[Union[str, Language]] = None) -> pd.DataFrame:
        """
        Get delay quote. 获取股票延时行情

        :param symbols: stock symbol list, like ['AAPL', 'GOOG']
        :param lang: language. Available options: zh_CN,zh_TW,en_US
        :return: pandas.DataFrame. The columns are as follows：
            symbol: Stock symbol. 股票代码
            pre_close: Previous close price. 前收价
            time: Last quote change time. 最后报价变动时间
            volume: Trading volume. 成交量
            open: Opening price. 开盘价
            high: Highest price. 最高价
            low: Lowest price. 最低价
            close: Closing price. 收盘价
            halted: Halted. 停牌信息. 0: Normal 正常, 3: Halted 停牌, 4: Delisted 退市
        
        :return example:
        symbol  pre_close  halted           time    open    high     low   close    volume
      0   AAPL     229.09     0.0  1754942400000  227.92  229.56  224.76  227.18  61806132
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(QUOTE_DELAY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = DelayBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return pd.DataFrame()

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
        params.symbols = self._format_to_list(symbols)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

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

    def get_timeline(self,
                     symbols: list[str],
                     include_hour_trading: bool = False,
                     begin_time: Optional[Union[int, str]] = -1,
                     lang: Optional[Union[str, Language]] = None,
                     trade_session: Optional[Union[str, TradingSession]] = None,
                     **kwargs) -> pd.DataFrame:
        """
        Get intraday timeline data. 获取当日分时数据，支持盘前盘后

        :param symbols: List of stock symbols, e.g. ["AAPL", "TSLA"]
                        股票代码列表
        :param include_hour_trading: Whether to include pre/after market timeline. 是否包含盘前盘后分时，默认 False
        :param begin_time: Start time, 13-digit timestamp (int) or datetime string (str), default -1 for all today.
                          开始时间, 13位时间戳或日期字符串, -1 表示当天全部
        :param lang: Language, zh_CN/zh_TW/en_US. Default from config. 语言
        :param trade_session: Trading session, e.g. TradingSession.Regular, TradingSession.OverNight. 交易时段，可选
        :param kwargs: Other optional params, e.g. version. 其他可选参数
        :return: pandas.DataFrame with columns:
            - symbol: stock symbol 股票代码
            - time: timestamp in ms 毫秒时间戳
            - price: close price of the minute 当前分钟收盘价
            - avg_price: volume weighted avg price up to now 加权均价
            - pre_close: previous close 昨日收盘价
            - volume: volume of the minute 该分钟成交量
            - trading_session: trading session 交易时段

        :return example:
            symbol           time     price  avg_price  pre_close   volume trading_session
        0     AAPL  1754919000000  226.7500  227.75438     229.09  1656620         regular
        1     AAPL  1754919060000  226.6000  227.51157     229.09   426781         regular
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.include_hour_trading = include_hour_trading
        params.begin_time = begin_time
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
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

    def get_timeline_history(
        self,
        symbols: list[str],
        date: str,
        right: Optional[Union[QuoteRight, str]] = QuoteRight.BR,
        trade_session: Optional[Union[TradingSession, str]] = None) -> pd.DataFrame:
        """
        Get historical timeline data. 获取历史分时数据

        :param symbols: List of stock symbols, e.g. ["AAPL", "BABA"]. 股票代码列表
        :param date: Date of timeline in yyyy-MM-dd format, like "2022-04-12". 日期，格式为 yyyy-MM-dd
        :param right: Quote right. QuoteRight.BR: before right, QuoteRight.NR: no right. 复权方式
        :param trade_session: Trading session, e.g. TradingSession.Regular, TradingSession.OverNight. 交易时段，可选
        :return: pandas.DataFrame with columns:
            - symbol: stock symbol 股票代码
            - time: timestamp in ms 毫秒时间戳
            - price: close price of the minute 当前分钟收盘价
            - avg_price: volume weighted avg price up to now 加权均价
            
        Example:
             symbol           time   volume     price  avg_price
        0     AAPL  1698845400000   654691  171.1000  171.04840
        1     AAPL  1698845460000   175598  170.5950  171.01788
        2     AAPL  1698845520000   186093  170.5350  170.95750
        3     AAPL  1698845580000   145550  170.2719  170.90828
        4     AAPL  1698845640000   221063  170.4100  170.82759
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.date = date
        params.right = get_enum_value(right)
        params.trade_session = get_enum_value(trade_session)
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

    def get_bars(self,
                 symbols: Union[str, list[str]],
                 period: Optional[Union[BarPeriod, str]] = BarPeriod.DAY,
                 begin_time: Optional[Union[int, str]] = -1,
                 end_time: Optional[Union[int, str]] = -1,
                 right: Optional[Union[QuoteRight, str]] = QuoteRight.BR,
                 limit: Optional[int] = 251,
                 lang: Optional[Union[Language, str]] = None,
                 page_token: Optional[str] = None,
                 trade_session: Optional[Union[TradingSession, str]] = None,
                 date: Optional[str] = None) -> pd.DataFrame:
        """
        Get K-line (OHLC) data. 获取K线数据

        :param symbols: Stock symbols list. 股票代号列表
        :param period: Bar period. 周期. Available values:
            - day: daily bar. 日K
            - week: weekly bar. 周K
            - month: monthly bar. 月K
            - year: yearly bar. 年K
            - 1min: 1-minute bar. 1分钟
            - 5min: 5-minute bar. 5分钟
            - 15min: 15-minute bar. 15分钟
            - 30min: 30-minute bar. 30分钟
            - 60min: 60-minute bar. 60分钟
        :param begin_time: Start time. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01" or "2019-01-01 12:00:00".
                         开始时间. 可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: End time. Same format as begin_time. 结束时间，格式同 begin_time
        :param right: Quote right. 复权选项. QuoteRight.BR: before right (前复权), QuoteRight.NR: no right (不复权)
        :param limit: Number limit. 数量限制
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :param page_token: The token of next page. Only supported when exactly one symbol. 下一页的令牌，仅当请求一个股票时支持
        :param trade_session: Trading session. 交易时段. 夜盘传 TradingSession.OverNight
        :param date: Date in format yyyyMMdd. 日期，格式为 yyyyMMdd
        :return: pandas.DataFrame with columns:
            - symbol: stock symbol. 股票代码
            - time: timestamp in milliseconds. 毫秒时间戳
            - open: opening price of the bar. 开盘价
            - high: highest price of the bar. 最高价
            - low: lowest price of the bar. 最低价
            - close: closing price of the bar. 收盘价
            - volume: trading volume of the bar. 成交量
            - amount: trading amount of the bar. 成交额
            - next_page_token: token for the next page. 下一页的令牌

        :return example:
          symbol           time     open    high     low   close     volume        amount next_page_token
        0   AAPL  1754366400000  203.400  205.34  202.16  202.92   44155079  8.987659e+09            None
        1   AAPL  1754452800000  205.630  215.38  205.59  213.25  108483103  2.315469e+10            None
        2   AAPL  1754539200000  218.875  220.85  216.58  220.03   90224834  1.979849e+10            None
        3   AAPL  1754625600000  220.830  231.00  219.25  229.35  113853967  2.589128e+10            None
        4   AAPL  1754884800000  227.920  229.56  224.76  227.18   61806132  1.416425e+10            None
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.period = get_enum_value(period)
        params.begin_time = begin_time
        params.end_time = end_time
        params.right = get_enum_value(right)
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.page_token = page_token if len(params.symbols) == 1 else None
        params.trade_session = get_enum_value(trade_session)
        params.date = str(date).replace('-', '').replace('/',
                                                         '') if date else None
        request = OpenApiRequest(KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

        return pd.DataFrame()

    def get_bars_by_page(self,
                         symbol: str,
                         period: Union[BarPeriod, str] = BarPeriod.DAY,
                         begin_time: Union[int, str] = -1,
                         end_time: Union[int, str] = -1,
                         total: int = 10000,
                         page_size: int = 100,
                         right: Union[QuoteRight, str] = QuoteRight.BR,
                         time_interval: int = 2,
                         lang: Optional[Union[str, Language]] = None,
                         trade_session: Optional[TradingSession] = None):
        """
        Get bars by page. 分页获取K线数据.

        :param symbol: symbol of stock.
        :param period: Bar period. 周期. 
        :param begin_time: time of the earliest bar, included. k线数据的开始时间，包含
        :param end_time: time of the latest bar, excluded. k线数据的结束时间，不包含
        :param total: Total bars number. K线数据的总条数
        :param page_size: Bars number of each request. 每次请求的K线数据条数
        :param right: Quote right. 复权方式. Available values: `QuoteRight.BR` (前复权), `QuoteRight.NR` (不复权)
        :param time_interval: Time interval between requests. 请求之间的时间间隔
        :param lang: 语言
        :param trade_session: Trading session, e.g., TradingSession.PreMarket, TradingSession.Regular, TradingSession.AfterHours.
                          交易时段，例如 TradingSession.PreMarket（盘前），TradingSession.Regular（盘中），TradingSession.AfterHours（盘后）
        :return: pandas.DataFrame with columns:
            - symbol: Stock symbol. 股票代码
            - time: Timestamp. 毫秒时间戳
            - open: Open price. 开盘价
            - high: High price. 最高价
            - low: Low price. 最低价
            - close: Close price. 收盘价
            - volume: Volume. 成交量
            - amount: Amount. 成交额

        :return example:
          symbol           time     open    high     low   close     volume        amount
        0   AAPL  1754366400000  203.400  205.34  202.16  202.92   44155079  8.987659e+09
        1   AAPL  1754452800000  205.630  215.38  205.59  213.25  108483103  2.315469e+10
        """
        if begin_time == -1 and end_time == -1:
            raise ApiException(
                400, 'One of the begin_time or end_time must be specified')
        if isinstance(symbol, list) and len(symbol) != 1:
            raise ApiException(
                400, 'Paging queries support only one symbol at each request')
        current = 0
        next_page_token = None
        result = list()
        result_df = None
        while current < total:
            if current + page_size >= total:
                page_size = total - current
            current += page_size
            bars = self.get_bars(symbols=symbol,
                                 period=period,
                                 begin_time=begin_time,
                                 end_time=end_time,
                                 right=right,
                                 limit=page_size,
                                 lang=lang,
                                 trade_session=trade_session,
                                 page_token=next_page_token)
            if bars.empty:
                result_df = bars
                break
            next_page_token = bars['next_page_token'].iloc[0]
            result.append(bars)
            if not next_page_token:
                break
            time.sleep(time_interval)
        return pd.concat(result).sort_values('time').reset_index(
            drop=True) if result else result_df

    def get_trade_ticks(self,
                        symbols: Union[str, list[str]],
                        trade_session: Optional[Union[TradingSession,
                                                      str]] = None,
                        begin_index: Optional[int] = None,
                        end_index: Optional[int] = None,
                        limit: Optional[int] = None,
                        lang: Optional[Union[Language, str]] = None,
                        **kwargs) -> pd.DataFrame:
        """
        Get trade ticks data. 获取逐笔成交数据

        :param symbols: Stock symbols list or a single symbol string. 股票代号列表或单个股票代码
        :param trade_session: Trading session, e.g., TradingSession.PreMarket, TradingSession.Regular, TradingSession.AfterHours.
                            交易时段，例如 TradingSession.PreMarket（盘前），TradingSession.Regular（盘中），TradingSession.OverNight（夜盘）
        :param begin_index: Start index. 开始索引
        :param end_index: End index. 结束索引
        :param limit: Number limit. 数量限制
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :param kwargs: Other optional parameters. 其他可选参数，如 'version'
        :return: pandas.DataFrame with columns:
            - symbol: stock symbol. 股票代码
            - time: timestamp in milliseconds. 毫秒时间戳
            - price: trade price. 成交价
            - volume: trade volume. 成交量
            - direction: price direction, "-" for down, "+" for up. 价格变动方向，"-"表示向下变动，"+"表示向上变动
            - index: tick index. 逐笔成交索引

        :return example:
            symbol           time  volume   price direction   index
        0     AAPL  1754942403109     406  227.18         -  482299
        1     AAPL  1754942403109   26215  227.18         -  482300
        2     AAPL  1754942403109     884  227.18         -  482301
        3     AAPL  1754942403109     200  227.18         -  482302
        4     AAPL  1754942403109    4094  227.18         -  482303
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        # compatible with version 1.0
        params.symbol = symbols if isinstance(symbols, str) else symbols[0]
        params.trade_session = get_enum_value(trade_session)
        params.begin_index = begin_index
        params.end_index = end_index
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
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

        return pd.DataFrame()

    def get_short_interest(self, symbols, lang=None):
        """
        Get short interest data for US stocks. 获取美国股票的做空数据
        
        :param symbols: List of symbols. 股票代号列表
        :param lang: Language. Available values: zh_CN,zh_TW,en_US
        :return: pandas.DataFrame 对象，各 column 含义如下：
            symbol: Stock symbol. 股票代码
            settlement_date: 收集信息的时间
            short_interest: 未平仓做空股数
            avg_daily_volume: 过去一年的日均成交量
            days_to_cover: 回补天数。使用最近一次获取的未平仓做空股数/日均成交量得到
            percent_of_float: 未平仓股数占流通股本的比重
        """
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

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

    def get_depth_quote(self, symbols: Union[str, list[str]],
                        market: Union[Market, str], trade_session: Optional[Union[TradingSession, str]] = None) -> dict:
        """
        Get market depth (order book). 获取深度行情数据（订单簿）
        
        :param symbols: Stock symbols list or a single symbol string. 股票代码列表或单个股票代码
        :param market: Market. 市场类型. Available values: US/HK/CN, from tigeropen.common.consts.Market
        :param trade_session: Trading session. 交易时段. e.g., TradingSession.PreMarket, TradingSession.Regular, TradingSession.AfterHours.
        :return: Dictionary with symbols as keys and order book data as values. 以股票代码为键，订单簿数据为值的字典
            Each item in asks and bids list means (price, volume, order count):
            asks 和 bids 列表中的每项数据含义为 (委托价格, 委托数量, 委托订单数):
                asks: [(ask_price1, ask_volume1, order_count1), (ask_price2, ask_volume2, order_count2), ...]
                bids: [(bid_price1, bid_volume1, order_count1), (bid_price2, bid_volume2, order_count2), ...]

        :return example:
            When returning a single symbol (返回单个股票的情况):
            ```
            {
                'symbol': '02833',
                'asks': [(27.4, 300, 2), (27.45, 500, 1), (27.5, 4400, 1), ...],
                'bids': [(27, 4000, 3), (26.95, 200, 1), (26.9, 0, 0), ...]
            }
            ```
            
            When returning multiple symbols (返回多个股票的情况):
            ```
            {
                '02833': {
                    'symbol': '02833',
                    'asks': [(27.35, 200, 1), (27.4, 2100, 2), ...],
                    'bids': [(27.05, 100, 1), (27, 5000, 4), ...]
                },
                '02828': {
                    'symbol': '02828',
                    'asks': [(106.6, 6800, 7), (106.7, 110200, 10), ...],
                    'bids': [(106.5, 62800, 17), (106.4, 68200, 9), ...]
                }
            }
            ```
            
 
        """
        params = DepthQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.market = get_enum_value(market)
        params.trade_session = get_enum_value(trade_session)
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

    def get_option_expirations(
            self,
            symbols: Union[list[str], str],
            market: Optional[Union[Market, str]] = None) -> pd.DataFrame:
        """
        Get option expiration dates. 获取期权到期日

        :param symbols: Stock symbols list. 股票代码列表
        :param market: Stock market. 市场. Available values: US/HK/CN/ALL
        :return: pandas.DataFrame with columns:
            symbol: Stock symbol. 股票代码
            option_symbol: Option symbol. 期权代码
            date: Expiration date in YYYY-MM-DD format. 到期日，YYYY-MM-DD 格式的字符串
            timestamp: Expiration timestamp in milliseconds. 到期日的毫秒时间戳
            period_tag: Period tag, like "m" for monthly, "w" for weekly. 周期标签，如"m"代表月度期权，"w"代表周期权

        :return example:
            symbol option_symbol        date      timestamp period_tag
        0    AAPL          AAPL  2025-08-15  1755230400000          m
        1    AAPL          AAPL  2025-08-22  1755835200000          w
        2    AAPL          AAPL  2025-08-29  1756440000000          w

        """
        params = OptionContractsParams()
        params.symbols = self._format_to_list(symbols)
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

        return pd.DataFrame()

    def get_option_chain(self,
                         symbol: str,
                         expiry: Union[str, int],
                         option_filter: Optional[OptionFilter] = None,
                         return_greek_value: Optional[bool] = None,
                         market: Optional[Union[Market, str]] = None,
                         timezone: Optional[str] = None,
                         **kwargs) -> pd.DataFrame:
        """
        Query option chain with filter. 查询期权链数据，支持过滤条件

        :param symbol: Underlying stock symbol. 标的股票代码
        :param expiry: Expiration date (like '2021-06-18' or 1560484800000). 到期日（如 '2021-06-18' 或 1560484800000）
        :param option_filter: Option filter conditions, tigeropen.quote.domain.filter.OptionFilter. 期权过滤条件.
                              e.g. OptionFilter(implied_volatility_min=0.05, implied_volatility_max=1, delta_min=0,
                                         delta_max=1, open_interest_min=10, open_interest_max=20000, in_the_money=True)
        :param return_greek_value: Return greek value or not, bool. 是否返回希腊字母值
        :param market: Stock market. 市场. Available values: US/HK/CN
        :param timezone: Default US/Eastern, when querying non-U.S. stock options, you need to specify the time zone. 
                         默认为美东时间，查询非美股期权时需要指定时区
        :param kwargs: Optional. Specify option_filter parameters directly without option_filter,
                       like: open_interest_min=100, delta_min=0.1.
                       可选参数。可以直接指定过滤条件参数而不使用option_filter对象，如：open_interest_min=100, delta_min=0.1
        :return: pandas.DataFrame with columns:
            identifier: Option identifier. 期权标识符
            symbol: Underlying stock symbol. 标的股票代码
            expiry: Option expiration date, timestamp in milliseconds. 期权到期日，毫秒时间戳
            strike: Strike price. 行权价
            put_call: Option direction, 'CALL' or 'PUT'. 期权方向，'CALL'(看涨)或'PUT'(看跌)
            multiplier: Option multiplier. 期权乘数
            ask_price: Ask price. 卖价
            ask_size: Ask size. 卖量
            bid_price: Bid price. 买价
            bid_size: Bid size. 买量
            pre_close: Previous close price. 前收盘价
            latest_price: Latest price. 最新价
            volume: Trading volume. 成交量
            open_interest: Open interest. 未平仓合约数
            last_timestamp: Last trade timestamp. 最后交易时间戳
            implied_vol: Implied volatility. 隐含波动率
            delta: Delta. Delta值
            gamma: Gamma. Gamma值
            theta: Theta. Theta值
            vega: Vega. Vega值
            rho: Rho. Rho值

        :return example:
             symbol         expiry             identifier strike put_call  ask_price  ask_size  volume  latest_price  pre_close  open_interest  multiplier  last_timestamp  implied_vol     delta     gamma     theta      vega       rho  bid_price  bid_size
        0     AAPL  1755230400000  AAPL  250815P00090000   90.0      PUT       0.01     750.0       4          0.01       0.01           1984         100   1754927160721     2.816660 -0.000514  0.000027 -0.016986  0.000482 -0.000014        NaN       NaN
        1     AAPL  1755230400000  AAPL  250815C00090000   90.0     CALL     137.90      86.0      10        137.62     140.35              2         100   1754940397131     3.652140  0.995457  0.000151 -0.157473  0.003590  0.009734     136.85      67.0
        2     AAPL  1755230400000  AAPL  250815P00095000   95.0      PUT       0.01    1000.0       1          0.01       0.01            542         100   1754921987495     2.657900 -0.000545  0.000030 -0.016739  0.000480 -0.000015        NaN       NaN
        3     AAPL  1755230400000  AAPL  250815C00095000   95.0     CALL     133.05     100.0       5        131.38     135.65              3         100   1754920925656     3.286350  0.996532  0.000132 -0.115157  0.002413  0.010314     131.60     100.0
        4     AAPL  1755230400000  AAPL  250815P00100000  100.0      PUT       0.01    1000.0       0          0.01       0.01           8636         100   1754065604281     2.508310 -0.000577  0.000034 -0.016648  0.000477 -0.000016        NaN       NaN
        """
        params = OptionChainParams()
        param = SingleContractParams()
        param.symbol = symbol
        if market is None and is_hk_option_underlying_symbol(symbol):
            market = Market.HK
        if isinstance(expiry, str) and re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}',
                                                expiry):
            param.expiry = date_str_to_timestamp(
                expiry, self._parse_timezone(timezone, market))
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

        return pd.DataFrame()

    def get_option_briefs(self,
                          identifiers: Union[str, list[str]],
                          market: Optional[Union[Market, str]] = None,
                          timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get option quotes. 获取期权最新行情

        :param identifiers: Option identifiers list. 期权代码列表. e.g. ["AAPL 250815C00125000", "AAPL 250815P00090000"]
        :param market: Stock market. 市场. Available values: US/HK/CN
        :param timezone: Timezone when process Option expiry. 处理期权到期时的时区
        :return: pandas.DataFrame with columns:
            identifier: Option identifier. 期权代码
            symbol: Underlying stock symbol. 期权对应的正股代码
            expiry: Expiration date, timestamp in milliseconds. 到期日，毫秒级时间戳
            strike: Strike price. 行权价
            put_call: Option direction, 'CALL' or 'PUT'. 期权方向，'CALL'(看涨)或'PUT'(看跌)
            multiplier: Option multiplier. 乘数
            ask_price: Ask price. 卖价
            ask_size: Ask size. 卖量
            bid_price: Bid price. 买价
            bid_size: Bid size. 买量
            pre_close: Previous close price. 前收价
            latest_price: Latest price. 最新价
            latest_time: Latest trade time. 最新交易时间
            volume: Trading volume. 成交量
            open_interest: Open interest. 未平仓数量
            open: Open price. 开盘价
            high: High price. 最高价
            low: Low price. 最低价
            rates_bonds: Risk-free interest rate. 无风险利率
            volatility: Historical volatility. 历史波动率
            change: Price change. 价格变动

        :return example:
                    identifier symbol         expiry strike put_call  multiplier ask_price ask_size bid_price bid_size pre_close latest_price latest_time  volume open_interest  open  high   low  rates_bonds volatility change
        0  PDD   260121C00090000    PDD  1768971600000   90.0     CALL         100      None     None      None     None      None         None        None       0          None  None  None  None     0.039494     26.29%   None

        """
        params = OptionContractsParams()
        identifiers = self._format_to_list(identifiers)
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            if market is None and is_hk_option_underlying_symbol(symbol):
                market = Market.HK
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = date_str_to_timestamp(
                expiry, self._parse_timezone(timezone, market))
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

        return pd.DataFrame()

    def get_option_bars(self,
                        identifiers: Union[str, list[str]],
                        begin_time: Union[int, str] = -1,
                        end_time: Union[int, str] = 4070880000000,
                        period: Union[BarPeriod, str] = BarPeriod.DAY,
                        limit: Optional[int] = None,
                        sort_dir: Optional[Union[SortDirection, str]] = None,
                        market: Optional[Union[Market, str]] = None,
                        timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get option K-line (OHLC) data. 获取期权K线数据

        :param identifiers: Option identifiers list. 期权代码列表
        :param begin_time: Start time. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01" or "2019-01-01 12:00:00".
                          开始时间. 可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: End time. Same format as begin_time. 结束时间，格式同 begin_time
        :param period: Bar period. 周期. Available values:
            - day: daily bar. 日K
            - 1min: 1-minute bar. 1分钟
            - 5min: 5-minute bar. 5分钟
            - 30min: 30-minute bar. 30分钟
            - 60min: 60-minute bar. 60分钟
        :param limit: Maximum number of bars for each option. 每个期权返回的K线最大数量
        :param sort_dir: Sort direction, tigeropen.common.consts.SortDirection. 排序方向，如 SortDirection.DESC（降序）
        :param market: Stock market. 市场. Available values: US/HK/CN
        :param timezone: Default US/Eastern, when querying non-U.S. options, you need to specify the time zone.
                         默认为美东时间，查询非美股期权时需要指定时区
        :return: pandas.DataFrame with columns:
            identifier: Option identifier. 期权代码
            symbol: Underlying stock symbol. 标的股票代码
            expiry: Option expiration date, timestamp in milliseconds. 期权到期日，毫秒时间戳
            put_call: Option direction, 'CALL' or 'PUT'. 期权方向，'CALL'(看涨)或'PUT'(看跌)
            strike: Strike price. 行权价
            time: Timestamp in milliseconds for the bar. K线对应的毫秒时间戳
            open: Opening price of the bar. 开盘价
            high: Highest price of the bar. 最高价
            low: Lowest price of the bar. 最低价
            close: Closing price of the bar. 收盘价
            volume: Trading volume of the bar. 成交量
            open_interest: Open interest. 未平仓合约数

        :return example:
                         identifier symbol         expiry put_call  strike           time   open   high    low  close  volume  open_interest
        0    AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1722830400000  33.00  33.00  29.50  29.50       9              0
        1    AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1722916800000  27.95  31.60  27.88  31.60      18              9
        2    AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1723003200000  33.75  33.75  33.75  33.75       2             27
        3    AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1723089600000  34.20  34.20  34.20  34.20       5             29
        4    AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1723176000000  34.50  35.94  34.50  35.94       4             34
        """
        params = OptionContractsParams()
        identifiers = self._format_to_list(identifiers)
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleOptionQuoteParams()
            param.symbol = symbol
            if market is None and is_hk_option_underlying_symbol(symbol):
                market = Market.HK
            param.expiry = date_str_to_timestamp(
                expiry, self._parse_timezone(timezone, market))
            param.put_call = put_call
            param.strike = strike
            param.period = get_enum_value(period)
            param.begin_time = date_str_to_timestamp(
                begin_time, self._parse_timezone(timezone, market))
            param.end_time = date_str_to_timestamp(
                end_time, self._parse_timezone(timezone, market))
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

    def get_option_trade_ticks(self,
                               identifiers: Union[str, list[str]],
                               timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get option trade ticks data. 获取期权逐笔成交数据

        :param identifiers: Option identifiers list. 期权代码列表
        :param timezone: Default US/Eastern, when querying non-U.S. options, you need to specify the time zone.
                         默认为美东时间，查询非美股期权时需要指定时区
        :return: pandas.DataFrame with columns:
            identifier: Option identifier. 期权代码
            symbol: Underlying stock symbol. 期权对应的正股代码
            expiry: Option expiration date, timestamp in milliseconds. 期权到期日，毫秒时间戳
            put_call: Option direction, 'CALL' or 'PUT'. 期权方向，'CALL'(看涨)或'PUT'(看跌)
            strike: Strike price. 行权价
            time: Trade timestamp in milliseconds. 成交时间，毫秒时间戳
            price: Trade price. 成交价格
            volume: Trade volume. 成交量

        :return example:
                        identifier symbol         expiry put_call  strike           time  price  volume
        0   AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1755005504417  30.00       2
        1   AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1755005504417  30.00       2
        2   AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1755005515034  30.20       3
        3   AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1755005668898  29.50       2
        4   AAPL  250815C00200000   AAPL  1755230400000     CALL   200.0  1755005735775  29.20       2
        """
        params = MultipleContractParams()
        identifiers = self._format_to_list(identifiers)
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleContractParams()
            param.symbol = symbol
            if is_hk_option_underlying_symbol(symbol):
                market = Market.HK
            else:
                market = None
            param.expiry = date_str_to_timestamp(
                expiry, self._parse_timezone(timezone, market))
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

        return pd.DataFrame()

    def get_option_symbols(
            self,
            market: Optional[Union[Market, str]] = Market.HK,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get option symbols. 获取期权合约代码

        :param market: Stock market. 市场. Default is HK market. 默认为港股市场
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame with columns:
            symbol: Option symbol code. 期权代码
            name: Option name. 期权名称
            underlying_symbol: Underlying stock symbol. 对应的正股代码

        :return example:
              symbol name underlying_symbol
        0    ALC.HK  ALC             02600
        1    CRG.HK  CRG             00390
        2    PAI.HK  PAI             02318
        3    XCC.HK  XCC             00939
        4    XTW.HK  XTW             00788
        """
        params = MarketParams()
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(ALL_HK_OPTION_SYMBOLS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionSymbolsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_option_depth(self,
                         identifiers: Union[str, list[str]],
                         market: Optional[Union[Market, str]] = Market.US,
                         timezone: Optional[str] = None) -> Union[dict, list]:
        """
        Get option depth quotes. 获取期权深度行情

        :param identifiers: Option identifier(s) list or a single identifier string. 期权代码列表或单个期权代码字符串
        :param market: Stock market. 市场. Available values: US/HK/CN. Default is US market. 默认为美股市场
        :param timezone: Timezone for processing option expiry dates. 处理期权到期日的时区
        :return: Option depth data. The return type depends on the number of identifiers.
                 期权深度数据。返回类型取决于请求的期权代码数量。
                 
                 Each item in asks and bids list means (price, volume, timestamp, exchange):
                 asks 和 bids 列表中的每项数据含义为 (价格, 数量, 时间戳, 交易所):
                 asks: [(price1, volume1, timestamp1, exchange1), (price2, volume2, timestamp2, exchange2), ...]
                 bids: [(price1, volume1, timestamp1, exchange1), (price2, volume2, timestamp2, exchange2), ...]
        
        :return example:
        when returning a single identifier (返回单个期权代码的情况):
        {'identifier': 'AAPL  250815C00210000',
        'asks': [(20.0, 26, 1755028800000, 'AMEX'), (20.0, 25, 1755028799000, 'BOX'), (20.0, 19, 1755028799000, 'CBOE'), ...],
        'bids': [(19.75, 23, 1755028800000, 'AMEX'), (19.75, 19, 1755028799000, 'CBOE'), (19.75, 18, 1755028799000, 'BZX'), ...]}

        when returning multiple identifiers (返回多个期权代码的情况):
        {'AAPL  250815C00210000':
            {'identifier': 'AAPL  250815C00210000',
             'asks': [(20.0, 26, 1755028800000, 'AMEX'), (20.0, 25, 1755028799000, 'BOX'), ...],
             'bids': [(19.75, 23, 1755028800000, 'AMEX'), (19.75, 19, 1755028799000, 'CBOE'), ...]},
        'AAPL  250815P00200000':
            {'identifier': 'AAPL  250815P00200000',
             'asks': [(0.04, 127, 1755028798000, 'NSDQ'), (0.04, 62, 1755028799000, 'EMLD'), ...],
             'bids': [(0.03, 432, 1755028798000, 'ARCA'), (0.03, 137, 1755028798000, 'NSDQ'), ...]}}
        """
        params = OptionContractsParams()
        identifiers = self._format_to_list(identifiers)
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            if market is None and is_hk_option_underlying_symbol(symbol):
                market = Market.HK
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = date_str_to_timestamp(
                expiry, self._parse_timezone(timezone, market))
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

    def get_option_timeline(self,
                            identifiers: Union[str, list[str]],
                            market: Optional[Union[Market, str]] = None,
                            begin_time: Optional[Union[str, int]] = None,
                            timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get option timeline (time and sales). 获取期权分时数据

        :param identifiers: Option identifier(s). 期权合约标识符，可以是单个字符串或字符串列表
        :param market: Market. 市场. Available values: US/HK
        :param begin_time: Begin time. 开始时间. Format: 'yyyy-MM-dd' or timestamp in milliseconds
        :param timezone: Timezone. 时区. Default: NY time for US market, HK time for HK market
        :return: pandas.DataFrame. The columns are as follows:
            identifier: Option identifier. 期权合约标识符
            symbol: Underlying symbol. 标的股票代码
            expiry: Option expiry date (timestamp in milliseconds). 期权到期日（毫秒时间戳）
            put_call: Option type. 期权类型. CALL or PUT
            strike: Strike price. 行权价
            pre_close: Previous close price. 前收盘价
            price: Latest price. 最新价
            avg_price: Average price. 均价
            time: Trade time (timestamp in milliseconds). 交易时间（毫秒时间戳）
            volume: Volume. 成交量

        :return example:
                         identifier  symbol         expiry put_call  strike  pre_close  price  avg_price           time  volume
        0    TCH.HK250828C00610000  TCH.HK  1756310400000     CALL  610.00       1.87   1.87   1.870000  1755048600000       0
        1    TCH.HK250828C00610000  TCH.HK  1756310400000     CALL  610.00       1.87   3.00   3.000000  1755048660000       3
        2    TCH.HK250828C00610000  TCH.HK  1756310400000     CALL  610.00       1.87   3.00   3.000000  1755048720000       0
        3    TCH.HK250828C00610000  TCH.HK  1756310400000     CALL  610.00       1.87   2.90   2.901818  1755048780000     162
        4    TCH.HK250828C00610000  TCH.HK  1756310400000     CALL  610.00       1.87   3.00   2.948896  1755048840000     152
        """
        params = OptionContractsParams()
        identifiers = self._format_to_list(identifiers)
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleOptionQuoteParams()
            param.symbol = symbol
            param.expiry = date_str_to_timestamp(
                expiry, self._parse_timezone(timezone, market))
            param.put_call = put_call
            param.strike = strike
            param.begin_time = date_str_to_timestamp(
                begin_time, self._parse_timezone(timezone, market))
            contracts.append(param)
        params.option_query = contracts
        if market:
            params.market = get_enum_value(market)
        request = OpenApiRequest(OPTION_TIMELINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionTimelineResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_future_exchanges(
            self,
            sec_type: Optional[Union[SecurityType, str]] = SecurityType.FUT,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get future exchanges list. 获取期货交易所列表

        :param sec_type: Security type. 证券类型. Available values:
            - FUT: Futures. 期货
            - FOP: Future Options. 期货期权
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            code: Exchange code. 交易所代码
            name: Exchange name. 交易所名称
            zone: Exchange timezone. 交易所所在时区

        :return example:
             code   name              zone
        0    CME    CME   America/Chicago
        1  NYMEX  NYMEX  America/New_York
        2  COMEX  COMEX  America/New_York
        3    SGX    SGX         Singapore
        4   HKEX   HKEX    Asia/Hong_Kong
        5   CBOT   CBOT   America/Chicago
        6    OSE    OSE        Asia/Tokyo
        7   CBOE   CBOE   America/Chicago
        8  EUREX  EUREX     Europe/Berlin
        """
        params = MarketParams()
        params.sec_type = get_enum_value(sec_type)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(FUTURE_EXCHANGE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureExchangeResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.exchanges
            else:
                raise ApiException(response.code, response.message)
        return pd.DataFrame()

    def get_future_contracts(
            self,
            exchange: str,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get tradable future contracts of an exchange. 获取交易所下的可交易合约

        :param exchange: Exchange code. 交易所代码. For example: CME, NYMEX, COMEX, etc.
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            contract_code: Contract code. 合约代码
            type: Future type, like CL. 期货合约对应的交易品种，如 CL
            name: Contract name. 期货合约的名称
            contract_month: Contract delivery month. 合约交割月份
            currency: Trading currency. 交易的货币
            first_notice_date: First notice date, after which long positions cannot be opened. Existing long positions will be forced to close before the first notice date (usually three trading days before).
                              第一通知日，合约在第一通知日后无法开多仓。已有的多仓会在第一通知日之前（通常为前三个交易日）被强制平仓。
            last_bidding_close_time: Last bidding close time. 竞价截止时间
            last_trading_date: Last trading date. 最后交易日
            trade: Whether it can be traded. 是否可交易
            continuous: Whether it is a continuous contract. 是否为连续合约
            multiplier: Contract multiplier. 合约乘数
            min_tick: Minimum price fluctuation. 最小价格波动
            symbol: Symbol. 交易代码
            exchange: Exchange name. 交易所名称
            exchange_code: Exchange code. 交易所代码
            delivery_mode: Delivery mode. 交割方式
            product_type: Product type. 产品类型
            product_worth: Product worth. 产品价值

        :return example:
             contract_code  continuous contract_month currency delivery_mode  display_multiplier exchange exchange_code first_notice_date  last_bidding_close_time last_trading_date  min_tick  multiplier                                  name      product_type                         product_worth symbol  trade  type
        0        MEUR2509       False         202509      USD      Physical                 1.0      CME        GLOBEX                                          0          20250915  0.000100     12500.0            E-Micro EUR/USD - Sep 2025                FX          12,500 x futures price (USD)    M6E   True  MEUR
        1        MEUR2512       False         202512      USD      Physical                 1.0      CME        GLOBEX                                          0          20251215  0.000100     12500.0            E-Micro EUR/USD - Dec 2025                FX          12,500 x futures price (USD)    M6E   True  MEUR
        2        MEURmain       False                     USD      Physical                 1.0      CME        GLOBEX                                          0                    0.000100     12500.0                E-Micro EUR/USD - main                FX          12,500 x futures price (USD)    M6E   True  MEUR
        3         CHF2512       False         202512      USD      Physical                 1.0      CME        GLOBEX                                          0          20251215  0.000050    125000.0                Swiss Franc - Dec 2025                FX          125,000x futures price (USD)    CHF   True   CHF
        4         CHF2509       False         202509      USD      Physical                 1.0      CME        GLOBEX                                          0          20250915  0.000050    125000.0                Swiss Franc - Sep 2025                FX          125,000x futures price (USD)    CHF   True   CHF
        """
        params = FutureExchangeParams()
        params.exchange_code = exchange
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(FUTURE_CONTRACT_BY_EXCHANGE_CODE,
                                 biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return pd.DataFrame()

    def get_current_future_contract(
            self,
            future_type: str,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get current contract of a future type. 获取期货品种的当前合约

        :param future_type: Future type code, like 'CL' for crude oil, 'ES' for S&P 500 E-mini. 期货品种代码，如原油的'CL'、标普500微型期货的'ES'
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            contract_code: Contract code. 合约代码
            continuous: Whether it is a continuous contract. 是否为连续合约
            contract_month: Contract delivery month. 合约交割月份
            currency: Trading currency. 交易的货币
            delivery_mode: Delivery mode. 交割方式
            display_multiplier: Display multiplier. 显示乘数
            exchange: Exchange name. 交易所名称
            exchange_code: Exchange code. 交易所代码
            first_notice_date: First notice date, after which long positions cannot be opened. 第一通知日，合约在此日后无法开多仓
            last_bidding_close_time: Last bidding close time. 竞价截止时间
            last_trading_date: Last trading date. 最后交易日
            min_tick: Minimum price fluctuation. 最小价格波动
            multiplier: Contract multiplier. 合约乘数
            name: Contract name. 合约名称
            product_type: Product type. 产品类型
            product_worth: Product worth. 产品价值
            symbol: Symbol. 交易代码
            trade: Whether it can be traded. 是否可交易
            type: Future type. 期货品种代码

        :return example:
           contract_code  continuous contract_month currency delivery_mode  display_multiplier exchange exchange_code first_notice_date  last_bidding_close_time last_trading_date  min_tick  multiplier                       name  product_type              product_worth symbol  trade type
        0        ES2509       False         202509      USD          Cash                   1      CME        GLOBEX                                          0          20250919      0.25        50.0  E-mini S&P 500 - Sep 2025  Equity Index  US$50 USD per index point     ES   True   ES

        """
        params = FutureContractParams()
        params.type = future_type
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(FUTURE_CURRENT_CONTRACT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return pd.DataFrame()

    def get_all_future_contracts(
            self,
            future_type: str,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get all future contracts of a given type. 获取指定类型的所有期货合约

        :param future_type: Future type code, like 'CL' for crude oil, 'ES' for S&P 500 E-mini. 期货品种代码，如原油的'CL'、标普500微型期货的'ES'
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            contract_code: Contract code. 合约代码
            continuous: Whether it is a continuous contract. 是否为连续合约
            contract_month: Contract delivery month. 合约交割月份
            currency: Trading currency. 交易的货币
            delivery_mode: Delivery mode. 交割方式
            display_multiplier: Display multiplier. 显示乘数
            exchange: Exchange name. 交易所名称
            exchange_code: Exchange code. 交易所代码
            first_notice_date: First notice date, after which long positions cannot be opened. 第一通知日，合约在此日后无法开多仓
            last_bidding_close_time: Last bidding close time. 竞价截止时间
            last_trading_date: Last trading date. 最后交易日
            min_tick: Minimum price fluctuation. 最小价格波动
            multiplier: Contract multiplier. 合约乘数
            name: Contract name. 合约名称
            product_type: Product type. 产品类型
            product_worth: Product worth. 产品价值
            symbol: Symbol. 交易代码
            trade: Whether it can be traded. 是否可交易
            type: Future type. 期货品种代码

        :return example:
           contract_code  continuous contract_month currency delivery_mode  display_multiplier exchange exchange_code first_notice_date  last_bidding_close_time last_trading_date  min_tick  multiplier                       name  product_type              product_worth symbol  trade type
        0        ES2509       False         202509      USD          Cash                   1      CME        GLOBEX                                          0          20250919      0.25        50.0  E-mini S&P 500 - Sep 2025  Equity Index  US$50 USD per index point     ES   True   ES
        1        ES2512       False         202512      USD          Cash                   1      CME        GLOBEX                                          0          20251219      0.25        50.0  E-mini S&P 500 - Dec 2025  Equity Index  US$50 USD per index point     ES   True   ES
        2        ES2603       False         202603      USD          Cash                   1      CME        GLOBEX                                          0          20260320      0.25        50.0  E-mini S&P 500 - Mar 2026  Equity Index  US$50 USD per index point     ES   True   ES
        """
        params = FutureContractParams()
        params.type = future_type
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(FUTURE_CONTRACTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return pd.DataFrame()

    def get_future_contract(
            self,
            contract_code: str,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get future contract by contract code. 根据合约代码获取期货合约信息

        :param contract_code: Code of future contract, like VIX2206, CL2203, CLmain. 期货合约代码，如 VIX2206、CL2203、CLmain
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            contract_code: Contract code. 合约代码
            continuous: Whether it is a continuous contract. 是否为连续合约
            contract_month: Contract delivery month. 合约交割月份
            currency: Trading currency. 交易的货币
            delivery_mode: Delivery mode. 交割方式
            display_multiplier: Display multiplier. 显示乘数
            exchange: Exchange name. 交易所名称
            exchange_code: Exchange code. 交易所代码
            first_notice_date: First notice date, after which long positions cannot be opened. 第一通知日，合约在此日后无法开多仓
            last_bidding_close_time: Last bidding close time. 竞价截止时间
            last_trading_date: Last trading date. 最后交易日
            min_tick: Minimum price fluctuation. 最小价格波动
            multiplier: Contract multiplier. 合约乘数
            name: Contract name. 合约名称
            product_type: Product type. 产品类型
            product_worth: Product worth. 产品价值
            symbol: Symbol. 交易代码
            trade: Whether it can be traded. 是否可交易
            type: Future type, like CL. 期货合约对应的交易品种，如 CL

        :return example:
          contract_code  continuous contract_month currency delivery_mode  display_multiplier exchange exchange_code first_notice_date  last_bidding_close_time last_trading_date  min_tick  multiplier                  name product_type             product_worth symbol  trade type
        0        CLmain       False                     USD      Physical                   1    NYMEX         NYMEX                                          0                        0.01      1000.0  WTI Crude Oil - main       Energy  US$1,000 x futures price     CL   True   CL

        """
        params = FutureContractParams()
        params.contract_code = contract_code
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(FUTURE_CONTRACT_BY_CONTRACT_CODE,
                                 biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return pd.DataFrame()

    def get_future_continuous_contracts(
            self,
            future_type: str,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get future continuous contracts. 获取期货连续合约

        :param future_type: Future type code, like 'CL' for crude oil. 期货品种代码，如原油的'CL'
        :param lang: Language. 语言. Available values: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            contract_code: Contract code. 合约代码
            continuous: Whether it is a continuous contract. 是否为连续合约
            contract_month: Contract delivery month. 合约交割月份
            currency: Trading currency. 交易的货币
            delivery_mode: Delivery mode. 交割方式
            display_multiplier: Display multiplier. 显示乘数
            exchange: Exchange name. 交易所名称
            exchange_code: Exchange code. 交易所代码
            first_notice_date: First notice date, after which long positions cannot be opened. 第一通知日，合约在此日后无法开多仓
            last_bidding_close_time: Last bidding close time. 竞价截止时间
            last_trading_date: Last trading date. 最后交易日
            min_tick: Minimum price fluctuation. 最小价格波动
            multiplier: Contract multiplier. 合约乘数
            name: Contract name. 合约名称
            product_type: Product type. 产品类型
            product_worth: Product worth. 产品价值
            symbol: Symbol. 交易代码
            trade: Whether it can be traded. 是否可交易
            type: Future type, like CL. 期货合约对应的交易品种，如 CL

        :return example:
           contract_code  continuous contract_month currency delivery_mode  display_multiplier exchange exchange_code first_notice_date  last_bidding_close_time last_trading_date  min_tick  multiplier                  name product_type             product_worth symbol  trade type
        0        CLmain       False                     USD      Physical                   1    NYMEX         NYMEX                                          0                        0.01      1000.0  WTI Crude Oil - main       Energy  US$1,000 x futures price     CL   True   CL

        """
        params = FutureContractParams()
        params.type = future_type
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(FUTURE_CONTINUOUS_CONTRACTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content, skip_main=False)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return pd.DataFrame()

    def get_future_trading_times(
            self,
            identifier: str,
            trading_date: Optional[Union[int, str]] = None) -> pd.DataFrame:
        """
        Get future contract trading times. 查询指定期货合约的交易时间

        :param identifier: Future contract code. 期货合约代码
        :param trading_date: Trading date. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01" or "2019-01-01 12:00:00".
                           指定交易日的时间. 可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :return: pandas.DataFrame. The columns are as follows:
            start: Trading start time (timestamp in milliseconds). 交易开始时间（毫秒时间戳）
            end: Trading end time (timestamp in milliseconds). 交易结束时间（毫秒时间戳）
            trading: Whether it is continuous trading. 是否为连续交易
            bidding: Whether it is bidding trading. 是否为竞价交易
            zone: Timezone. 时区

        :return example:
                    start            end  trading  bidding              zone
        0  1755035100000  1755036000000    False     True  America/New_York
        1  1755036000000  1755118800000     True    False  America/New_York

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
        return pd.DataFrame()

    def get_future_bars(self,
                        identifiers: Union[str, list[str]],
                        period: Union[BarPeriod, str] = BarPeriod.DAY,
                        begin_time: Union[int, str] = -1,
                        end_time: Union[int, str] = -1,
                        limit: int = 1000,
                        page_token: Optional[str] = None,
                        timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get future contract K-line (OHLC) data. 获取期货K线数据

        :param identifiers: Future contract code list or single contract code. 期货合约代码列表或单个合约代码
        :param period: Bar period. 周期. Available values:
            - day: daily bar. 日K
            - week: weekly bar. 周K
            - month: monthly bar. 月K
            - year: yearly bar. 年K
            - 1min: 1-minute bar. 1分钟
            - 5min: 5-minute bar. 5分钟
            - 15min: 15-minute bar. 15分钟
            - 30min: 30-minute bar. 30分钟
            - 60min: 60-minute bar. 60分钟
        :param begin_time: Start time. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01" or "2019-01-01 12:00:00".
                          开始时间. 可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: End time. Same format as begin_time. 结束时间，格式同 begin_time
        :param limit: Maximum number of bars to return. 返回的K线最大数量
        :param page_token: The token for pagination. Only supported when there's exactly one identifier.
                          分页标记。仅当只有一个合约标识符时支持
        :param timezone: Timezone for processing dates. 处理日期的时区
        :return: pandas.DataFrame. The columns are as follows:
            identifier: Future contract code. 期货合约代码
            time: Timestamp in milliseconds for the bar (end time). Bar cutting follows exchange rules. For example, for CN1901, data from T day 17:00 to T+1 day 16:30 will be combined into one daily bar.
                  K线对应的时间戳，即K线的结束时间。K线的切割方式与交易所一致，以CN1901举例，T日的17:00至T+1日的16:30的数据会被合成一个日级K线
            latest_time: Last update time of the bar. K线最后的更新时间
            open: Opening price. 开盘价
            high: Highest price. 最高价
            low: Lowest price. 最低价
            close: Closing price. 收盘价
            settlement: Settlement price. Returns 0 if not generated. 结算价，在未生成结算价时返回0
            volume: Trading volume. 成交量
            open_interest: Open interest (number of open contracts). 未平仓合约数量
            next_page_token: Token for next page query. 下一页查询标记

        :return example:
          identifier           time    latest_time   open   high    low  close  settlement  volume  open_interest                                    next_page_token
        0     CL2609  1755032400000  1755032400000  61.25  61.25  61.13  61.25       61.25    2459          47604  ZnV0dXJlX2tsaW5lfENMMjYwOXxkYXl8MTc1NTA2NjI0Nz...
        1     CL2609  1754946000000  1754904392000  61.19  61.19  61.19  61.19       61.47     707          47604  ZnV0dXJlX2tsaW5lfENMMjYwOXxkYXl8MTc1NTA2NjI0Nz...
        2     CL2609  1754686800000  1754669837000  61.35  61.59  61.21  61.21       61.20    1340          47375  ZnV0dXJlX2tsaW5lfENMMjYwOXxkYXl8MTc1NTA2NjI0Nz...
        3     CL2609  1754600400000  1754600400000  61.37  61.37  61.37  61.37       61.37       0          46496  ZnV0dXJlX2tsaW5lfENMMjYwOXxkYXl8MTc1NTA2NjI0Nz...
        4     CL2609  1754514000000  1754498885000  61.88  62.28  61.88  62.26       61.36     762          46535  ZnV0dXJlX2tsaW5lfENMMjYwOXxkYXl8MTc1NTA2NjI0Nz...

        """
        params = FutureQuoteParams()
        params.contract_codes = self._format_to_list(identifiers)
        params.period = get_enum_value(period)
        params.begin_time = date_str_to_timestamp(
            begin_time, self._parse_timezone(timezone))
        params.end_time = end_time
        params.limit = limit
        params.page_token = page_token if len(
            params.contract_codes) == 1 else None
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

    def get_future_bars_by_page(self,
                                identifier: str,
                                period: Union[BarPeriod, str] = BarPeriod.DAY,
                                begin_time: Union[int, str] = -1,
                                end_time: Union[int, str] = -1,
                                total: Optional[int] = 10000,
                                page_size: Optional[int] = 500,
                                time_interval: Optional[int] = 2):
        """
        Get Future bars by page. 分页获取期货K线数据

        :param identifier: identifier of Future contract. 期货合约标识符
        :param period: Bar period. 周期. Available values:
            - day: daily bar. 日K
            - week: weekly bar. 周K 
            - month: monthly bar. 月K
            - year: yearly bar. 年K
            - 1min: 1-minute bar. 1分钟
            - 5min: 5-minute bar. 5分钟
            - 15min: 15-minute bar. 15分钟
            - 30min: 30-minute bar. 30分钟
            - 60min: 60-minute bar. 60分钟
        :param begin_time: Start time. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01" or "2019-01-01 12:00:00".
                          开始时间. 可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: End time. Same format as begin_time. 结束时间，格式同 begin_time
        :param total: Total number of K-lines. 总K线数量
        :param page_size: Page size. 每次请求的K线数量
        :param time_interval: Time interval between requests. 请求之间的时间间隔，单位为秒
        :return:
        """
        if begin_time == -1 and end_time == -1:
            raise ApiException(
                400, 'One of the begin_time or end_time must be specified')
        if isinstance(identifier, list) and len(identifier) != 1:
            raise ApiException(
                400,
                'Paging queries support only one identifier at each request')
        current = 0
        next_page_token = None
        result = list()
        result_df = None
        while current < total:
            if current + page_size >= total:
                page_size = total - current
            current += page_size
            bars = self.get_future_bars(identifiers=identifier,
                                        period=period,
                                        begin_time=begin_time,
                                        end_time=end_time,
                                        limit=page_size,
                                        page_token=next_page_token)
            if bars.empty:
                result_df = bars
                break
            next_page_token = bars['next_page_token'].iloc[0]
            result.append(bars)
            if not next_page_token:
                break
            time.sleep(time_interval)
        return pd.concat(result).sort_values('time').reset_index(
            drop=True) if result else result_df

    def get_future_trade_ticks(self,
                               identifier: str,
                               begin_index: int = 0,
                               end_index: int = 30,
                               limit: int = 1000) -> pd.DataFrame:
        """
        Get future trade ticks data. 获取期货逐笔成交数据

        :param identifier: Future contract code. Only supports one identifier.
                          期货合约代码。仅支持一个标识符
        :param begin_index: Begin index for trade ticks. 
                           逐笔成交的开始索引
        :param end_index: End index for trade ticks. 
                         逐笔成交的结束索引
        :param limit: Maximum number of trade ticks to return. 
                     返回的逐笔成交最大数量限制
        :return: pandas.DataFrame. The columns are as follows:
            identifier: Future contract code. 期货合约代码
            index: Trade index. 成交索引值
            price: Trade price. 成交价格
            volume: Trade volume. 成交量
            time: Trade time (timestamp in milliseconds). 成交时间，精确到毫秒的时间戳

        :return example:
            identifier  index  price  volume           time
        0      CL2509      0  63.07      10  1755036000000
        1      CL2509      1  63.07       7  1755036000000
        2      CL2509      2  63.07       9  1755036000000
        3      CL2509      3  63.06       4  1755036000000
        4      CL2509      4  63.05       6  1755036000000
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

    def get_future_brief(
            self,
            identifiers: Union[str, list[str]],
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get future realtime quote. 获取期货最新行情

        :param identifiers: Future contract code list or a single contract code. 期货合约代码列表或单个合约代码
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            identifier: Future contract code. 期货合约代码
            ask_price: Ask price. 卖价
            ask_size: Ask size. 卖量
            bid_price: Bid price. 买价
            bid_size: Bid size. 买量
            pre_close: Previous close price. 前收价
            latest_price: Latest price. 最新价
            latest_size: Latest trade volume. 最新成交量
            latest_time: Latest trade time (timestamp in milliseconds). 最新价成交时间（毫秒时间戳）
            volume: Total volume for the current trading day. 当日累计成交手数
            open_interest: Number of open contracts. 未平仓合约数量
            open_interest_change: Change in open interest. 未平仓合约变化量
            open: Open price. 开盘价
            high: Highest price. 最高价
            low: Lowest price. 最低价
            settlement: Settlement price. 结算价
            limit_up: Upper price limit. 涨停价
            limit_down: Lower price limit. 跌停价

        :return example:
           identifier  latest_price  latest_size    latest_time  bid_price  ask_price  bid_size  ask_size  open_interest  open_interest_change  volume    open     high     low  settlement  limit_up  limit_down
        0     ES2509        6469.5            5  1755067657000     6469.5    6469.75        11        14        1938507                 26858   46493  6468.0  6474.75  6461.0      6468.5    6919.5      6017.5

        """
        params = FutureQuoteParams()
        params.contract_codes = self._format_to_list(identifiers)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(FUTURE_REAL_TIME_QUOTE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_future_depth(self, identifiers: Union[str, list[str]],
                         lang: Optional[Union[Language, str]] = None) -> dict:
        """
        Get future depth data. 获取期货深度数据

        :param identifiers: Future contract code list or a single contract code. 期货合约代码列表或单个合约代码
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return:
        if single identifier:
        {
            "identifier": "CL2509",
            "asks": [
                {"price": 63.07, "size": 10},
                {"price": 63.08, "size": 5},
                ...
            ],
            "bids": [
                {"price": 63.06, "size": 7},
                {"price": 63.05, "size": 12},
                ...
            ]
        }

        if multiple identifiers:
        {
            "CL2509": {
                "asks": [
                    {"price": 63.07, "size": 10},
                    {"price": 63.08, "size": 5},
                    ...
                ],
                "bids": [
                    {"price": 63.06, "size": 7},
                    {"price": 63.05, "size": 12},
                    ...
                ]
            },
            "ES2509": {
                "asks": [
                    {"price": 6469.5, "size": 11},
                    {"price": 6469.75, "size": 14},
                    ...
                ],
                "bids": [
                    {"price": 6469.25, "size": 8},
                    {"price": 6469.0, "size": 10},
                    ...
                ]
            }
        }

        """
        params = FutureQuoteParams()
        params.contract_codes = self._format_to_list(identifiers)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(FUTURE_DEPTH, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureDepthResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)


    def get_corporate_split(self,
                            symbols: Union[str, list[str]],
                            market: Union[Market, str],
                            begin_date: Union[int, str],
                            end_date: Union[int, str],
                            timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get stock split data. 获取公司拆合股数据

        :param symbols: Stock symbols list or a single symbol. 证券代码列表或单个代码
        :param market: Market to query. 查询的市场. Available values: US/HK/CN, from tigeropen.common.consts.Market
        :param begin_date: Begin date. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01" or "2019-01-01 12:00:00".
                         起始时间. 可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_date: End date. Same format as begin_date. 结束时间，格式同 begin_date
        :param timezone: Timezone for processing dates. 处理日期的时区
        :return: pandas.DataFrame. The columns are as follows:
            symbol: Stock symbol. 证券代码
            action_type: Fixed as "SPLIT". 固定为 "SPLIT"
            from_factor: Factor before corporate action. 公司行动前的因子
            to_factor: Factor after corporate action. 公司行动后的因子
            ratio: Split ratio. 拆合股比例
            execute_date: Ex-dividend date. 除权除息日
            market: Market. 所属市场
            exchange: Exchange. 所属交易所

        :return example:
           symbol action_type  from_factor  to_factor  ratio execute_date market exchange
         0   UVXY       SPLIT          5.0        1.0    5.0   2024-04-11     US     CBOE
        """
        params = CorporateActionParams()
        params.action_type = CorporateActionType.SPLIT.value
        params.symbols = self._format_to_list(symbols)
        params.market = get_enum_value(market)
        params.begin_date = date_str_to_timestamp(
            begin_date, self._parse_timezone(timezone))
        params.end_date = date_str_to_timestamp(end_date,
                                                self._parse_timezone(timezone))
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

    def get_corporate_dividend(self,
                               symbols,
                               market,
                               begin_date,
                               end_date,
                               timezone=None):
        """
        获取公司派息数据
        :param symbols: 证券代码列表
        :param market: 查询的市场. 可选的值为 common.consts.Market 枚举类型, 如 Market.US
        :param begin_date: 起始时间. 若是时间戳需要精确到毫秒, 为13位整数;
                                    或是日期时间格式的字符串, 如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_date: 截止时间. 格式同 begin_date
        :param timezone: 时区
        :return: pandas.DataFrame, 各 column 的含义如下:
            symbol: 证券代码
            action_type: 固定为 "DIVIDEND"
            amount: 分红金额
            currency: 分红货币类型
            announced_date: 公告日期
            execute_date: 除权除息日
            record_date: 股权登记日
            pay_date: 现金到账日
            market: 所属市场
            exchange: 所属交易所
        """
        params = CorporateActionParams()
        params.action_type = CorporateActionType.DIVIDEND.value
        params.symbols = self._format_to_list(symbols)
        params.market = get_enum_value(market)
        params.begin_date = date_str_to_timestamp(
            begin_date, self._parse_timezone(timezone))
        params.end_date = date_str_to_timestamp(end_date,
                                                self._parse_timezone(timezone))
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

    def get_corporate_earnings_calendar(self,
                                        market,
                                        begin_date,
                                        end_date,
                                        timezone=None):
        """
        获取公司财报日历
        :param market:
        :param begin_date: 起始时间
        :param end_date: 截止时间
        :param timezone: 时区
        :return:
        """
        params = CorporateActionParams()
        params.action_type = CorporateActionType.EARNINGS_CALENDAR.value
        params.market = get_enum_value(market)
        params.begin_date = date_str_to_timestamp(
            begin_date, self._parse_timezone(timezone))
        params.end_date = date_str_to_timestamp(end_date,
                                                self._parse_timezone(timezone))
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

    def get_financial_daily(self,
                            symbols: Union[str, list[str]],
                            market: Union[Market, str],
                            fields: list[Union[Field, str]],
                            begin_date: Union[int, str],
                            end_date: Union[int, str],
                            timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get daily financial data. 获取日级的财务数据

        :param symbols: Stock symbols list or a single symbol. 证券代码列表或单个代码
        :param market: Market to query. 查询的市场. Available values: US/HK/CN, from tigeropen.common.consts.Market
        :param fields: Fields list to query. 查询的字段列表. From tigeropen.common.consts.Valuation, e.g., Valuation.shares_outstanding
        :param begin_date: Begin date. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01".
                          开始时间. 可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01"
        :param end_date: End date. Same format as begin_date. 结束时间，格式同 begin_date
        :param timezone: Timezone for processing dates. 处理日期的时区
        :return: pandas.DataFrame. The columns are as follows:
            symbol: Stock symbol. 证券代码
            field: Field name. 查询的字段名称
            date: Date of the data (timestamp in milliseconds). 数据日期（毫秒时间戳）
            value: Field value. 字段对应的值

        :return example:
             symbol               field           date         value
        0     AAPL  shares_outstanding  1672502400000  1.590812e+10
        1     AAPL  shares_outstanding  1672588800000  1.590812e+10
        2     AAPL  shares_outstanding  1672675200000  1.590812e+10
        3     AAPL  shares_outstanding  1672761600000  1.590812e+10
        4     AAPL  shares_outstanding  1672848000000  1.590812e+10

        """
        params = FinancialDailyParams()
        params.symbols = self._format_to_list(symbols)
        params.market = get_enum_value(market)
        params.fields = [get_enum_value(field) for field in fields]
        params.begin_date = date_str_to_timestamp(
            begin_date, self._parse_timezone(timezone))
        params.end_date = date_str_to_timestamp(end_date,
                                                self._parse_timezone(timezone))
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

    def get_financial_report(self,
                             symbols: Union[str, list[str]],
                             market: Union[Market, str],
                             fields: list[Union[Income, Balance, CashFlow,
                                                BalanceSheetRatio, Growth,
                                                Leverage, Profitability, str]],
                             period_type: Union[FinancialReportPeriodType,
                                                str],
                             begin_date: Optional[Union[int, str]] = None,
                             end_date: Optional[Union[int, str]] = None,
                             timezone: Optional[str] = None) -> pd.DataFrame:
        """
        Get financial report data. 获取财报数据

        :param symbols: Stock symbols list or a single symbol. 证券代码列表或单个代码
        :param market: Market to query. 查询的市场. Available values: US/HK/CN, from tigeropen.common.consts.Market
        :param fields: Fields list to query. 查询的字段列表. From tigeropen.common.consts modules:
                      - Income: e.g., Income.total_revenue, Income.net_income
                      - Balance: e.g., Balance.total_assets, Balance.total_liabilities
                      - CashFlow: e.g., CashFlow.operating_cash_flow
                      - BalanceSheetRatio: Various balance sheet ratios
                      - Growth: Growth metrics
                      - Leverage: Leverage ratios
                      - Profitability: Profitability ratios
        :param period_type: Period type for financial data. 查询的财报周期类型.
                           From tigeropen.common.consts.FinancialReportPeriodType:
                           - ANNUAL: Annual report. 年报
                           - QUARTERLY: Quarterly report. 季报
                           - LTM: Last Twelve Months. 过去十二个月
                           - TTM: Trailing Twelve Months. 滚动十二个月
                           - YTD: Year To Date. 年初至今
        :param begin_date: Start date of period_end_date range. 财报周期结束日期的开始范围.
                          Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01".
        :param end_date: End date of period_end_date range. 财报周期结束日期的结束范围.
                        Same format as begin_date.
        :param timezone: Timezone for processing dates. 处理日期的时区
        :return: pandas.DataFrame. The columns are as follows:
            symbol: Stock symbol. 证券代码
            currency: Currency used in the report. 财报使用的币种
            field: Field name. 查询的字段名称
            value: Field value. 字段对应的值
            period_end_date: Natural quarter date of the report. 这条记录对应财报的所属自然季度日期
            filing_date: Report release date. 财报的发布日期

        :return example:
           symbol currency       field       value period_end_date filing_date
        0   AAPL      USD  net_income   9.4321E10      2023-04-01  2024-05-03
        1   AAPL      USD  net_income    9.476E10      2023-07-01  2024-08-02
        2   AAPL      USD  net_income   9.6995E10      2023-09-30  2024-11-01
        3   AAPL      USD  net_income  1.00913E11      2023-12-30  2025-01-31
        """
        params = FinancialReportParams()
        params.symbols = self._format_to_list(symbols)
        params.market = get_enum_value(market)
        params.fields = [get_enum_value(field) for field in fields]
        params.period_type = get_enum_value(period_type)
        params.lang = get_enum_value(self._lang)
        params.begin_date = date_str_to_timestamp(
            begin_date, self._parse_timezone(timezone))
        params.end_date = date_str_to_timestamp(end_date,
                                                self._parse_timezone(timezone))
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
        params.symbols = self._format_to_list(symbols)
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

    def get_financial_exchange_rate(self,
                                    currency_list,
                                    begin_date,
                                    end_date=None,
                                    timezone=None):
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
        tz = self._parse_timezone(timezone)
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

    def get_industry_list(
        self,
        industry_level: Union[IndustryLevel, str] = IndustryLevel.GGROUP
    ) -> list[dict]:
        """
        Get industry list. 获取行业列表
        
        :param industry_level: Industry level. 行业级别. Available values from common.consts.IndustryLevel:
                              - GSECTOR: Top level sectors. 顶级行业部门
                              - GGROUP: Industry groups. 行业组
                              - GIND: Industries. 行业
                              - GSUBIND: Sub-industries. 子行业
                              Default is GGROUP.
        :return: List of industry information dictionaries. 由行业信息字典构成的列表
                Each dictionary contains:
                - industry_level: Industry level code. 行业级别代码
                - id: Industry ID. 行业ID
                - name_cn: Industry name in Chinese. 行业中文名称
                - name_en: Industry name in English. 行业英文名称

        :return example:
        [
            {
                'industry_level': 'GGROUP', 
                'id': '5020', 
                'name_cn': '媒体与娱乐', 
                'name_en': 'Media & Entertainment'
            }, 
            {
                'industry_level': 'GGROUP', 
                'id': '2550', 
                'name_cn': '零售业', 
                'name_en': 'Consumer Discretionary Distribution & Retail'
            }, 
            {
                'industry_level': 'GGROUP', 
                'id': '3510', 
                'name_cn': '医疗保健设备与服务', 
                'name_en': 'Health Care Equipment & Services'
            }
        ]
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
            如 [{'symbol': 'A', 'company_name': 'A', 'market': 'US', 'industry_list': [{...}, {...},...]},
               {'symbol': 'B', 'company_name': 'B', 'market': 'US', 'industry_list': [{...}, {...},...]},
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

    def market_scanner(self,
                       market: Optional[Union[Market, str]] = Market.US,
                       filters: Optional[List[StockFilter]] = None,
                       sort_field_data: Optional[SortFilterData] = None,
                       page: Optional[int] = 0,
                       page_size: Optional[int] = 100,
                       cursor_id: Optional[str] = None) -> ScannerResult:
        """
        Screen stocks with filtering conditions and sort options. 按条件筛选和排序股票

        :param market: Stock market. 市场. Available values: US/HK/CN, from tigeropen.common.consts.Market
        :param filters: List of stock filters. 筛选条件列表. List of tigeropen.quote.domain.filter.StockFilter objects
        :param sort_field_data: Sort field data. 排序字段数据. tigeropen.quote.domain.filter.SortFilterData object
        :param page: Page number, starting from 0. 页码，从0开始
        :param page_size: Number of items per page. 每页记录数
        :param cursor_id: Cursor ID for pagination. 分页的游标ID
        :return: ScannerResult object containing page info, result items and symbols
        
        The returned ScannerResult contains these fields:
        - page: Current page number (当前页码)
        - total_page: Total number of pages (总页数)
        - total_count: Total number of records (记录总数) 
        - page_size: Number of items per page (每页记录数)
        - items: List of ScannerResultItem objects (扫描结果项列表)
        - symbols: List of stock symbols (股票代码列表)
        
        Each ScannerResultItem contains:
        - symbol: Stock symbol (股票代码)
        - market: Market (市场)
        - field_data: Dictionary of field values (字段值的字典)
        - symbols: List of stock symbols in the current page. 当前页的股票代码列表

        :return example:
        ScannerResult({
            'page': 0, 
            'total_page': 1466, 
            'total_count': 7329, 
            'page_size': 5,
            'items': [
                ScannerResultItem({'symbol': 'AAPL', 'market': 'US', 'field_data': {
                    <StockField.current_ChangeRate: 59>: 0.5, 
                    <MultiTagField.StockCode: 4>: 'AAPL', 
                    <MultiTagField.Market_Name: 21>: 'US'
                }}),
                ScannerResultItem({'symbol': 'MSFT', 'market': 'US', 'field_data': {
                    <StockField.current_ChangeRate: 59>: 0.4, 
                    <MultiTagField.StockCode: 4>: 'MSFT', 
                    <MultiTagField.Market_Name: 21>: 'US'
                }})
            ], 
            'symbols': ['AAPL', 'MSFT']
        })
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
        params.cursor_id = cursor_id
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

    def get_trading_calendar(
            self,
            market: Union[Market, str],
            begin_date: Optional[Union[str, int]] = None,
            end_date: Optional[Union[str, int]] = None) -> list[dict]:
        """
        Get trading calendar for a specific market. 获取特定市场的交易日历

        :param market: Market. 市场. common.consts.Market, like Market.US
        :param begin_date: Begin date, included. 开始日期, 包含. Format: 'yyyy-MM-dd' or timestamp in milliseconds
                         格式：'yyyy-MM-dd' 或毫秒时间戳
        :param end_date: End date, not included. 结束日期, 不包含. Format: 'yyyy-MM-dd' or timestamp in milliseconds
                       格式：'yyyy-MM-dd' 或毫秒时间戳
        :return: List of trading calendar days. Each day is a dictionary with the following keys:
                交易日历日期列表，每个日期是具有以下键的字典：
            date: Trading date string (format: 'yyyy-MM-dd'). 交易日期字符串（格式：'yyyy-MM-dd'）
            type: Trading type. 交易类型. 'TRADING' for trading day, 'NON_TRADING' for non-trading day
                 'TRADING' 表示交易日，'NON_TRADING'表示非交易日

        :return example:
        [
            {'date': '2025-08-13', 'type': 'TRADING'}, 
            {'date': '2025-08-14', 'type': 'TRADING'}, 
            {'date': '2025-08-15', 'type': 'TRADING'},
            {'date': '2025-08-16', 'type': 'NON_TRADING'},
            {'date': '2025-08-17', 'type': 'NON_TRADING'}
        ]
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

    def get_stock_broker(
            self,
            symbol: str,
            limit: int = 40,
            lang: Optional[Union[Language, str]] = None) -> StockBroker:
        """
        Get stockbroker information. 获取股票经纪商信息

        :param symbol: Stock symbol. 股票代码
        :param limit: The maximum number of brokers to return at each price level. Default is 40.
                     每个价格档位返回的最大经纪商数量。默认值为40
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: StockBroker object with the following structure:
                 StockBroker对象，包含以下结构：
            symbol: Stock symbol. 股票代码
            bid_broker: List of LevelBroker objects for bid side. 买方的经纪商信息列表，每个元素是一个LevelBroker对象
                LevelBroker:
                    level: Price level (1 is best bid). 价格档位（1表示最优买价）
                    price: Price at this level. 此档位的价格
                    broker_count: Number of brokers at this price level. 此价格档位的经纪商数量
                    broker: List of Broker objects. 经纪商对象列表
                        Broker:
                            id: Broker ID. 经纪商ID
                            name: Broker name. 经纪商名称
            ask_broker: List of LevelBroker objects for ask side. 卖方的经纪商信息列表，结构同bid_broker
        
        :return example:
        StockBroker({
            'symbol': '01810',
            'bid_broker': [
                LevelBroker({
                    'level': 1, 
                    'price': 11.46, 
                    'broker_count': 5,
                    'broker': [
                        Broker({'id': '5999', 'name': '中国创盈'}), 
                        Broker({'id': '4374', 'name': '巴克莱亚洲'}),
                        Broker({'id': '1438', 'name': 'Susquehanna'}), 
                        Broker({'id': '4821', 'name': '华盛'}),
                        Broker({'id': '6998', 'name': '中国投资'})
                    ]
                })
            ],
            'ask_broker': [
                LevelBroker({
                    'level': 1, 
                    'price': 11.48, 
                    'broker_count': 5,
                    'broker': [
                        Broker({'id': '4374', 'name': '巴克莱亚洲'}), 
                        Broker({'id': '9056', 'name': '瑞银'}),
                        Broker({'id': '2027', 'name': '东亚'}), 
                        Broker({'id': '4821', 'name': '华盛'}),
                        Broker({'id': '4374', 'name': '巴克莱亚洲'})
                    ]
                })
            ]
        })
        """
        params = StockBrokerParams()
        params.symbol = symbol
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(STOCK_BROKER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = StockBrokerResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_broker_hold(
            self,
            market: Union[Market, str] = Market.HK,
            order_by: str = 'marketValue',
            direction: Union[SortDirection, str] = SortDirection.DESC,
            limit: int = 50,
            page: int = 0,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get Hong Kong stock brokers' holding information. 获取港股实时经纪队列数据
        
        :param market: Market to query. 查询的市场. Default is Market.HK
        :param order_by: Field to sort by. 排序字段. Default is 'marketValue'
                        Available values: 'marketValue', 'sharesHold', 'buyAmount', etc.
        :param direction: Sort direction. 排序方向. From tigeropen.common.consts.SortDirection:
                         - ASC: Ascending order. 升序
                         - DESC: Descending order. 降序
        :param limit: Maximum number of records to return per page. 每页返回的最大记录数
        :param page: Page number, starting from 0. 页码，从0开始
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            org_id: Broker organization ID. 经纪商机构ID
            org_name: Broker organization name. 经纪商机构名称
            date: Date of the data. 数据日期
            shares_hold: Number of shares held. 持有股数
            market_value: Market value of shares. 持股市值
            buy_amount: Today's buying amount. 今日买入金额
            buy_amount5: 5-day buying amount. 5日买入金额
            buy_amount20: 20-day buying amount. 20日买入金额
            buy_amount60: 60-day buying amount. 60日买入金额
            market: Market. 市场
            page: Current page number. 当前页码
            total_page: Total number of pages. 总页数
            total_count: Total number of records. 记录总数

        :return example:
             org_id                             org_name        date   shares_hold  market_value  buy_amount  buy_amount5  buy_amount20  buy_amount60 market  page  total_page  total_count
        0   C00019            HONGKONG SHANGHAI BANKING  2025-08-12  679751035124  1.084098e+13    25783546  -1398518479   -1925856646  -11992723448     HK     0          14          675
        1   A00003                (SH)-HK Stock Connect  2025-08-12  322858531788  3.387372e+12   165112466    326626308    8036108049   23431084282     HK     0          14          675
        2   C00010                        CITIBANK N.A.  2025-08-12  204243273603  2.531753e+12   381710217   1517103569    3507932105   -8726829068     HK     0          14          675
        3   A00004                (SZ)-HK Stock Connect  2025-08-12  209368051775  2.323152e+12   293848216   1142638582    4064309306   10201521740     HK     0          14          675
        4   B01161                                  UBS  2025-08-12  152410314229  1.344047e+12    63675556    -96248826   -1764660015   -1817547800     HK     0          14          675
        """
        params = BrokerHoldParams()
        params.market = get_enum_value(market)
        params.order_by = order_by
        params.direction = get_enum_value(direction)
        params.limit = limit
        params.page = page
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(BROKER_HOLD, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = BrokerHoldResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_capital_flow(
            self,
            symbol: str,
            market: Union[Market, str],
            period: Union[CapitalPeriod, str],
            begin_time: Union[int, str] = -1,
            end_time: Union[int, str] = -1,
            limit: int = 200,
            lang: Optional[Union[Language, str]] = None) -> pd.DataFrame:
        """
        Get capital net inflow data for a stock. 获取股票资金流向数据
        
        :param symbol: Stock symbol. 股票代码
        :param market: Market. 市场. Available values: US/HK/CN, from tigeropen.common.consts.Market
        :param period: Time period for capital flow data. 资金流向数据的时间周期. From tigeropen.common.consts.CapitalPeriod:
                      - INTRADAY: Intraday data. 日内数据
                      - DAY: Daily data. 日级数据
                      - WEEK: Weekly data. 周级数据
                      - MONTH: Monthly data. 月级数据
                      - YEAR: Yearly data. 年级数据
                      - QUARTER: Quarterly data. 季度数据
                      - HALFAYEAR: Half-yearly data. 半年数据
        :param begin_time: Begin time. 开始时间. Can be 13-digit timestamp (milliseconds) or datetime string like "2019-01-01" or "2019-01-01 12:00:00".
                          可以是13位毫秒时间戳或日期时间格式的字符串，如 "2019-01-01" 或 "2019-01-01 12:00:00"
        :param end_time: End time. 结束时间. Same format as begin_time. 格式同 begin_time
        :param limit: Maximum number of records to return. 返回的最大记录数量
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: pandas.DataFrame. The columns are as follows:
            time: Date or time string. 日期或时间字符串
            timestamp: Timestamp in milliseconds. 毫秒时间戳
            net_inflow: Net capital inflow. 净资金流入量
            symbol: Stock symbol. 股票代码
            period: Time period. 时间周期
            
        :return example:
                   time      timestamp    net_inflow symbol period
        0    2024-10-23  1729656000000 -3.051296e+08   AAPL    day
        1    2024-10-24  1729742400000 -3.889794e+08   AAPL    day
        2    2024-10-25  1729828800000 -3.011353e+08   AAPL    day
        3    2024-10-28  1730088000000 -1.662333e+07   AAPL    day
        4    2024-10-29  1730174400000 -7.020035e+07   AAPL    day
        """
        params = CapitalParams()
        params.symbol = symbol
        params.market = get_enum_value(market)
        params.period = get_enum_value(period)
        params.begin_time = begin_time
        params.end_time = end_time
        params.limit = limit
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(CAPITAL_FLOW, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = CapitalFlowResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_capital_distribution(
            self,
            symbol: str,
            market: Union[Market, str],
            lang: Optional[Union[Language,
                                 str]] = None) -> 'CapitalDistribution':
        """
        Get capital distribution data for a stock. 获取股票资金分布数据
        
        :param symbol: Stock symbol. 股票代码
        :param market: Market. 市场. Available values: US/HK/CN, from tigeropen.common.consts.Market
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: CapitalDistribution object with the following fields:
                 包含以下字段的CapitalDistribution对象:
            symbol: Stock symbol. 股票代码
            net_inflow: Net capital inflow. 净资金流入
            in_all: Total inflow amount. 总流入金额
            in_big: Large order inflow amount. 大单流入金额
            in_mid: Medium order inflow amount. 中单流入金额
            in_small: Small order inflow amount. 小单流入金额
            out_all: Total outflow amount. 总流出金额
            out_big: Large order outflow amount. 大单流出金额
            out_mid: Medium order outflow amount. 中单流出金额
            out_small: Small order outflow amount. 小单流出金额
            
        :return example:
        CapitalDistribution({
            'symbol': 'AAPL', 
            'net_inflow': -284440760.35, 
            'in_all': 3501504236.05, 
            'in_big': 363021158.16980004, 
            'in_mid': 325198563.3328, 
            'in_small': 2813284514.5437512, 
            'out_all': 3785944996.4, 
            'out_big': 552875033.2554, 
            'out_mid': 332693992.8277004, 
            'out_small': 2900375970.3170733
        })
        """
        params = CapitalParams()
        params.symbol = symbol
        params.market = get_enum_value(market)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
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
        params.symbols = self._format_to_list(symbols)
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

    def get_warrant_filter(self,
                           symbol,
                           page=None,
                           page_size=None,
                           sort_field_name=None,
                           sort_dir=None,
                           filter_params=None):
        """
        :param symbol:
        :param page:
        :param page_size:
        :param sort_field_name:
        :param sort_dir: tigeropen.common.consts.SortDirection, e.g. SortDirection.DESC
        :param filter_params: tigeropen.quote.request.model.WarrantFilterParams
        :return:
        """
        params: WarrantFilterParams = WarrantFilterParams()
        params.lang = get_enum_value(self._lang)
        params.symbol = symbol or (filter_params.symbol
                                   if filter_params else None)
        params.page = page or (filter_params.page if filter_params else None)
        params.page_size = page_size or (filter_params.page_size
                                         if filter_params else None)
        params.sort_field_name = sort_field_name or (
            filter_params.sort_field_name if filter_params else None)
        params.sort_dir = get_enum_value(
            sort_dir or (filter_params.sort_dir if filter_params else None))
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

    def get_kline_quota(self, with_details: bool = False) -> list[dict]:
        """
        Get K-line quota information. 获取K线数据查询配额信息

        :param with_details: Whether to include detailed quota information. 是否包含详细配额信息
        :return: List of dictionaries containing quota information for different K-line types:
                包含不同类型K线数据配额信息的字典列表:
            remain: Remaining quota count. 剩余配额数量
            used: Used quota count. 已使用配额数量
            method: Method type. 方法类型 ('kline', 'future_kline', 'option_kline')
            details: Detailed usage information. 使用详情
            symbol_details: Symbol-specific usage details. 按股票代码的使用详情

        :return example:
        [
            {'remain': 5000, 'used': 0, 'method': 'kline', 'details': [], 'symbol_details': []}, 
            {'remain': 5000, 'used': 0, 'method': 'future_kline', 'details': [], 'symbol_details': []}, 
            {'remain': 5000, 'used': 0, 'method': 'option_kline', 'details': [], 'symbol_details': []}
        ]
        """
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
        params.symbols = self._format_to_list(symbols)
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
        params.symbols = self._format_to_list(symbols)
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

    def get_fund_history_quote(self,
                               symbols,
                               begin_time,
                               end_time,
                               limit=None):
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
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
        params.symbols = self._format_to_list(symbols)
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

    def get_quote_overnight(self, symbols, lang=Language.en_US):
        params = MultipleQuoteParams()
        params.symbols = self._format_to_list(symbols)
        params.lang = get_enum_value(lang)
        request = OpenApiRequest(QUOTE_OVERNIGHT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteOvernightResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def _parse_timezone(self, timezone=None, market=None):
        if timezone:
            return timezone
        if market:
            if Market.HK.name == get_enum_value(market):
                return 'Asia/Hong_Kong'
            if Market.US.name == get_enum_value(market):
                return 'US/Eastern'
            if Market.CN.name == get_enum_value(market):
                return 'Asia/Shanghai'
        return self._timezone

    @classmethod
    def _format_to_list(cls, data: Union[str, list]):
        if isinstance(data, str):
            return [data]
        return data
