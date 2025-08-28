#!/usr/bin/env python3
import functools
import os
import re
from datetime import datetime
from typing import Optional, Any, Union

import pandas as pd
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from tigeropen import __VERSION__ as TIGEROPEN_SDK_VERSION
from tigeropen.common.consts import Market, SecurityType, Currency, OrderType
from tigeropen.common.consts import SortDirection
from tigeropen.common.consts.filter_fields import (
    StockField, AccumulateField, FinancialField, MultiTagField,
    AccumulatePeriod, FinancialPeriod
)
from tigeropen.common.util.contract_utils import option_contract_by_symbol, future_contract, \
    stock_contract
from tigeropen.common.util.order_utils import (limit_order, market_order,
                                               stop_order, stop_limit_order,
                                               trail_order, algo_order,
                                               algo_order_params, combo_order,
                                               contract_leg)
from tigeropen.quote.domain.filter import StockFilter, SortFilterData, ScannerResult, OptionFilter
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient

from tigermcp.version import __VERSION__ as TIGERMCP_VERSION

_client_config = TigerOpenClientConfig()
_client_config._channel = f"tigermcp-{TIGERMCP_VERSION}"

# 通过环境变量配置只读模式，默认为 False
_read_only_mode = os.environ.get("TIGERMCP_READONLY", "").lower() in ("true", "1", "yes")

server = FastMCP("TigerMCP")


class ApiHelper:

    @staticmethod
    def serialize_object(obj):
        if obj is None:
            return None
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)

    @staticmethod
    def serialize_list(items):
        if items is None:
            return []
        return [ApiHelper.serialize_object(item) for item in items]

    @staticmethod
    def dataframe_to_dict_list(df):
        if df is None:
            return []
        if isinstance(df, pd.DataFrame):
            if df.empty:
                return []
            return df.to_dict(orient='records')
        return df

    @staticmethod
    def handle_result(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                return ApiHelper.dataframe_to_dict_list(result)
            elif isinstance(result, list):
                return ApiHelper.serialize_list(result)
            elif hasattr(result, '__dict__'):
                return ApiHelper.serialize_object(result)
            return result

        return wrapper


@server.resource("server://status")
def hello() -> Any:
    return {"message": "TigerOpen MCP Server is running!"}


@server.tool(title="mcp server info",
             description=f"MCP Server Version: {TIGERMCP_VERSION}, Tigeropen Version: {TIGEROPEN_SDK_VERSION}, Read Only Mode: {_read_only_mode}")
def server_info() -> Any:
    return {
        "mcp_version": TIGERMCP_VERSION,
        "sdk_version": TIGEROPEN_SDK_VERSION,
        "read_only_mode": _read_only_mode
    }


class QuoteApi:
    quote_client = QuoteClient(_client_config)

    @staticmethod
    @server.tool(description='Query the market data permissions the user has.')
    @ApiHelper.handle_result
    def get_quote_permissions() -> Any:
        """
        查询用户所拥有的行情权限
        """
        return QuoteApi.quote_client.get_quote_permission()

    @staticmethod
    @server.tool(description="Get the status of a market and its latest opening time.")
    @ApiHelper.handle_result
    def get_market_status(market: str = Market.ALL.value,
                          lang: Optional[str] = None) -> Any:
        """
        获取指定市场的状态及最近开盘时间
        """
        status = QuoteApi.quote_client.get_market_status(market, lang=lang)
        return status

    @staticmethod
    @server.tool(description='Get the market trading calendar since 2015, excluding temporary market closures.')
    @ApiHelper.handle_result
    def get_trading_calendar(
            market: Market = Field(..., description="Market. 市场. US/HK/CN"),
            begin_date: Optional[str] = Field(
                None,
                description="Start date in YYYY-MM-DD format, included. the year must be later than 2015. 开始日期",
                pattern=r"^\d{4}-\d{2}-\d{2}$"),
            end_date: Optional[str] = Field(
                None,
                description="End date in YYYY-MM-DD format, excluded, must later than begin_date. 结束日期",
                pattern=r"^\d{4}-\d{2}-\d{2}$")) -> Any:
        """
        获取自 2015 年以来的市场交易日历（不含临时休市调整）
        """
        begin_dt = datetime.strptime(begin_date, '%Y-%m-%d') if begin_date else None
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        if begin_dt and end_dt and begin_dt >= end_dt:
            raise ValueError(
                "end_date must be later than begin_date, if provided both."
            )
        return QuoteApi.quote_client.get_trading_calendar(
            market, begin_date, end_date)

    @staticmethod
    @server.tool(description='Market scanner')
    @ApiHelper.handle_result
    def market_scanner(market: str = Field(..., description="Market. 市场. US/HK", pattern=r'^(US|HK)$'),
                       filters: Optional[list[dict]] = Field(None,
                                                             description="List of filter conditions. 过滤条件列表。Available field_type: StockField(tigeropen.common.consts.filter_fields.StockField), "
                                                                         "AccumulateField(tigeropen.common.consts.filter_fields.AccumulateField), "
                                                                         "FinancialField(tigeropen.common.consts.filter_fields.FinancialField), "
                                                                         "MultiTagField(tigeropen.common.consts.filter_fields.MultiTagField)."
                                                                         "Example: [{  \"field_type\": \"StockField\",  \"field_name\": \"current_ChangeRate\",  \"filter_min\": 0.01,  \"filter_max\": 0.5,  \"is_no_filter\": false},"
                                                                         " {  \"field_type\": \"AccumulateField\",  \"field_name\": \"ChangeRate\",  \"filter_min\": 0.01,  \"filter_max\": 1,  \"is_no_filter\": false,  \"accumulate_period\": \"Last_Year\"}, "
                                                                         "{  \"field_type\": \"FinancialField\",  \"field_name\": \"LYR_PE\",  \"filter_min\": 1,  \"filter_max\": 100,  \"is_no_filter\": false,  \"financial_period\": \"LTM\"},"
                                                                         " {  \"field_type\": \"MultiTagField\",  \"field_name\": \"Concept\",  \"tag_list\": [\"BK4562\", \"BK4575\"],  \"is_no_filter\": false}]"),
                       sort_field: Optional[dict] = Field(None,
                                                          description="Sort field and direction. 排序字段和方向。Example: {  \"field_type\": \"StockField\",  \"field_name\": \"FloatShare\",  \"sort_dir\": \"ASC\",  \"period\": null}"),
                       max_items: int = 1000) -> Any:
        """
        Market scanner
        选股器
        """
        sort_field_data = None
        if sort_field:
            field_type = sort_field.get('field_type')
            field_name = sort_field.get('field_name')
            sort_dir_str = sort_field.get('sort_dir', 'DESC')
            period_str = sort_field.get('period')

            field = None
            if field_type == 'StockField':
                field = getattr(StockField, field_name, None)
            elif field_type == 'AccumulateField':
                field = getattr(AccumulateField, field_name, None)
            elif field_type == 'FinancialField':
                field = getattr(FinancialField, field_name, None)
            elif field_type == 'MultiTagField':
                field = getattr(MultiTagField, field_name, None)
            sort_dir = getattr(SortDirection, sort_dir_str) if hasattr(
                SortDirection, sort_dir_str) else SortDirection.DESC

            period = None
            if period_str and field_type == 'AccumulateField':
                period = getattr(AccumulatePeriod, period_str) if hasattr(
                    AccumulatePeriod, period_str) else None

            if field:
                sort_field_data = SortFilterData(field, sort_dir, period)

        filter_list = []
        if filters:
            for filter_item in filters:
                field_type = filter_item.get('field_type')
                field_name = filter_item.get('field_name')
                field = None

                if field_type == 'StockField':
                    field = getattr(StockField, field_name, None)
                elif field_type == 'AccumulateField':
                    field = getattr(AccumulateField, field_name, None)
                elif field_type == 'FinancialField':
                    field = getattr(FinancialField, field_name, None)
                elif field_type == 'MultiTagField':
                    field = getattr(MultiTagField, field_name, None)

                if not field:
                    continue

                filter_min = filter_item.get('filter_min')
                filter_max = filter_item.get('filter_max')
                is_no_filter = filter_item.get('is_no_filter', False)

                accumulate_period = None
                financial_period = None
                tag_list = None

                if field_type == 'AccumulateField' and 'accumulate_period' in filter_item:
                    period_str = filter_item.get('accumulate_period')
                    accumulate_period = getattr(
                        AccumulatePeriod, period_str) if hasattr(
                        AccumulatePeriod, period_str) else None

                elif field_type == 'FinancialField' and 'financial_period' in filter_item:
                    period_str = filter_item.get('financial_period')
                    financial_period = getattr(
                        FinancialPeriod, period_str) if hasattr(
                        FinancialPeriod, period_str) else None

                elif field_type == 'MultiTagField' and 'tag_list' in filter_item:
                    tag_list = filter_item.get('tag_list')

                stock_filter = StockFilter(field=field,
                                           filter_min=filter_min,
                                           filter_max=filter_max,
                                           is_no_filter=is_no_filter,
                                           accumulate_period=accumulate_period,
                                           financial_period=financial_period,
                                           tag_list=tag_list)
                filter_list.append(stock_filter)

        all_items = []
        all_symbols = set()
        page_size = 100  # 每页请求的数量
        cursor_id = None
        items_fetched = 0

        unlimited = max_items == 0

        while True:
            result = QuoteApi.quote_client.market_scanner(
                market=market,
                filters=filter_list if filter_list else None,
                sort_field_data=sort_field_data,
                page_size=page_size,
                cursor_id=cursor_id)

            all_items.extend(result.items)
            all_symbols.update(result.symbols)
            items_fetched += len(result.items)

            if not result.cursor_id or (not unlimited
                                        and items_fetched >= max_items):
                break

            cursor_id = result.cursor_id

        final_items = all_items[:
                                max_items] if not unlimited and max_items > 0 else all_items
        final_result = ScannerResult(page=0,
                                     page_size=len(final_items),
                                     total_page=1,
                                     total_count=len(final_items),
                                     items=list(),
                                     cursor_id=None)
        final_result.items = final_items
        final_result.symbols = list(all_symbols)

        return final_result

    @staticmethod
    @server.tool(description='Get real-time market data for stocks or options.')
    @ApiHelper.handle_result
    def get_realtime_quote(
            symbols: list[str] = Field(...,
                                       description="List of symbols. e.g. Stock: 'AAPL', '00700'; Option: 'AAPL  250829C00150000', 'TCH.HK 230616C00550000'; Future: 'CL2509'"),
            sec_type: Union[SecurityType,
            str] = Field(...,
                         description="Security type. STK/OPT/FUT",
                         pattern=r'^(STK|OPT|FUT)$'),
            include_hour_trading: bool = False,
            market: Optional[str] = Field(None, description="Market. US/HK", pattern=r'^(US|HK)$'),
            timezone: Optional[str] = Field(
                None,
                description=
                "Timezone of Options expiry, US/Eastern or Asia/Hone_Kong")
    ) -> Any:
        """
        获取股票、期权实时行情
        """
        # check sec_type
        if sec_type.upper() not in [
            SecurityType.STK.value, SecurityType.OPT.value,
            SecurityType.FUT.value
        ]:
            raise ValueError(
                f"Invalid security type: {sec_type}, must be one of {SecurityType.STK.value}, {SecurityType.OPT.value}, {SecurityType.FUT.value}"
            )
        if market and market.upper() not in [Market.US.value, Market.HK.value, Market.CN.value]:
            raise ValueError(
                f"Invalid market: {market}, must be one of {Market.US.value}, {Market.HK.value}, {Market.CN.value}"
            )

        if sec_type.upper() == SecurityType.OPT.value:
            return QuoteApi.quote_client.get_option_briefs(identifiers=symbols,
                                                           market=market,
                                                           timezone=timezone)
        elif sec_type.upper() == SecurityType.FUT.value:
            return QuoteApi.quote_client.get_future_brief(identifiers=symbols)
        return QuoteApi.quote_client.get_stock_briefs(
            symbols, include_hour_trading=include_hour_trading)

    @staticmethod
    @server.tool(description='Get depth quotes for specified stocks or options.')
    @ApiHelper.handle_result
    def get_depth_quote(symbols: Union[str, list[str]] = Field(...,
                                                               description="List of symbols. e.g. Stock: 'AAPL', '00700'; US Option: 'AAPL  250829C00150000', HK Option: 'TCH.HK 230616C00550000'"),
                        sec_type: Union[SecurityType, str] = Field(...,
                                                                   description="Security type. STK/OPT. All symbols must be in the same sec_type",
                                                                   pattern=r'^(STK|OPT)$'),
                        market: Union[Market, str] = Field(...,
                                                           description="Market. US/HK, All symbols must be in the same market.",
                                                           pattern=r'^(US|HK)$'),
                        timezone: Optional[str] = Field(None, description="Timezone of Option expiry.")) -> Any:
        """
        获取深度行情
        """
        if sec_type.upper() not in [
            SecurityType.STK.value, SecurityType.OPT.value
        ]:
            raise ValueError(
                f"Invalid security type: {sec_type}, must be one of {SecurityType.STK.value}, {SecurityType.OPT.value}"
            )
        if SecurityType.OPT.value == sec_type.upper():
            return QuoteApi.quote_client.get_option_depth(identifiers=symbols,
                                                          market=market,
                                                          timezone=timezone)
        return QuoteApi.quote_client.get_depth_quote(symbols=symbols,
                                                     market=market)

    @staticmethod
    @server.tool(description='Get tick-by-tick trade data.')
    @ApiHelper.handle_result
    def get_trade_ticks(symbols: Union[str, list[str]] = Field(...,
                                                               description="List of symbols. e.g. Stock: 'AAPL', '00700'; US Option: 'AAPL  250829C00150000'; HK Option: 'TCH.HK 230616C00550000'; Future: 'CL2509'"),
                        sec_type: Union[SecurityType, str] = Field(...,
                                                                   description="Security type. STK/OPT/FUT, aAll symbols must be in the same sec_type",
                                                                   pattern=r'^(STK|OPT|FUT)$'),
                        trade_session: Optional[str] = Field(None,
                                                             description="Trade session. Available values: PreMarket/Regular/AfterHours/OverNight"),
                        begin_index: Optional[int] = None,
                        end_index: Optional[int] = None,
                        limit: Optional[int] = None,
                        timezone: Optional[str] = Field(None,
                                                        description="Timezone, US/Eastern or Asia/Hong_Kong, used by Option expiry")) -> Any:
        """
        获取逐笔成交数据
        """
        if sec_type.upper() not in [
            SecurityType.STK.value, SecurityType.OPT.value,
            SecurityType.FUT.value
        ]:
            raise ValueError(
                f"Invalid security type: {sec_type}, must be one of {SecurityType.STK.value}, {SecurityType.OPT.value}, {SecurityType.FUT.value}"
            )
        if SecurityType.OPT.value == sec_type.upper():
            return QuoteApi.quote_client.get_option_trade_ticks(
                identifiers=symbols, timezone=timezone)
        elif SecurityType.FUT.value == sec_type.upper():
            return QuoteApi.quote_client.get_future_trade_ticks(
                identifier=symbols,
                begin_index=begin_index,
                end_index=end_index,
                limit=limit)
        return QuoteApi.quote_client.get_trade_ticks(
            symbols=symbols,
            trade_session=trade_session,
            begin_index=begin_index,
            end_index=end_index,
            limit=limit)

    @staticmethod
    @server.tool(description='Get candlestick (K-line) data.')
    @ApiHelper.handle_result
    def get_bars(symbols: Union[str, list[str]] = Field(...,
                                                        description="List of symbols. e.g. Stock: 'AAPL', '00700'; US Option: 'AAPL  250829C00150000'; HK Option: 'TCH.HK 230616C00550000'; Future: 'CL2509'"),
                 sec_type: Union[SecurityType, str] = Field(...,
                                                            description="Security type. STK/OPT/FUT. All symbols must be in the same sec_type",
                                                            pattern=r'^(STK|OPT|FUT)$'),
                 period: str = Field(None,
                                     description="Bar period. K线周期. Available values: day/week/month/year/1min/3min/5min/10min/15min/30min/60min",
                                     pattern=r'^(day|week|month|year|1min|3min|5min|10min|15min|30min|60min)$'),
                 limit: Optional[int] = 251,
                 right: str = Field("br",
                                    description="k-line right. Available values: br/mr. br: before right, nr: no right"),
                 begin_time: Union[int, str] = Field(-1,
                                                     description="Begin time date string 'YYYY-MM-DD HH:MM:SS' or timestamp in milliseconds. 开始时间"),
                 end_time: Union[int, str] = Field(-1,
                                                   description="End time date string 'YYYY-MM-DD HH:MM:SS' or timestamp in milliseconds. 结束时间"),
                 trade_session: Optional[str] = Field(None,
                                                      description="Trade session. Available values: PreMarket/Regular/AfterHours/OverNight"),
                 market: Optional[str] = Field(None,
                                               description="Market. US/HK. All symbols must be in the same market."),
                 timezone: Optional[str] = None) -> Any:
        """
        获取K线数据
        """
        if sec_type.upper() not in [
            SecurityType.STK.value, SecurityType.OPT.value,
            SecurityType.FUT.value
        ]:
            raise ValueError(
                f"Invalid security type: {sec_type}, must be one of {SecurityType.STK.value}, {SecurityType.OPT.value}, {SecurityType.FUT.value}"
            )
        # check symbols
        symbols = symbols if isinstance(symbols, list) else [symbols]
        option_count = 0
        for symbol in symbols:
            if len(symbol) > 6 and re.match(r'(\w+(?:\.\w+)?)\s*(\d{6})([CP])(\d+)', symbol, re.M):
                option_count += 1
        if option_count == len(symbols):
            sec_type = SecurityType.OPT.value
        elif option_count > 0:
            return {
                "error":
                    "Mixing Options and Stocks in symbols is not supported. Please separate them."
            }

        if sec_type.upper() == "OPT":
            return QuoteApi.quote_client.get_option_bars(identifiers=symbols,
                                                         begin_time=begin_time,
                                                         end_time=end_time,
                                                         period=period,
                                                         limit=limit,
                                                         market=market,
                                                         timezone=timezone)
        elif sec_type.upper() == "FUT":
            results = []
            for symbol in symbols if isinstance(symbols, list) else [symbols]:
                result = QuoteApi.quote_client.get_future_bars_by_page(
                    identifier=symbol,
                    period=period,
                    begin_time=begin_time,
                    end_time=end_time,
                    total=limit)
                results.append(result)
            return pd.concat(results, ignore_index=True)
        else:
            results = []
            for symbol in symbols if isinstance(symbols, list) else [symbols]:
                result = QuoteApi.quote_client.get_bars_by_page(
                    symbol=symbol,
                    period=period,
                    begin_time=begin_time,
                    end_time=end_time,
                    total=limit,
                    right=right,
                    trade_session=trade_session)
                results.append(result)
            return pd.concat(results, ignore_index=True)

    @staticmethod
    @server.tool(description='Get intraday data.')
    @ApiHelper.handle_result
    def get_timeline(symbols: Union[str, list[str]] = Field(...,
                                                            description="List of symbols. e.g. Stock: 'AAPL', '00700'; US Option: 'AAPL  250829C00150000'; HK Option: 'TCH.HK 230616C00550000'; Future: 'CL2509'"),
                     sec_type: Union[SecurityType, str] = Field(..., description="Security type. STK/OPT/FUT",
                                                                pattern=r'^(STK|OPT|FUT)$'),
                     begin_time: Union[int, str] = Field(-1,
                                                         description="Begin time date string 'YYYY-MM-DD HH:MM:SS' or timestamp in milliseconds. 开始时间"),
                     trade_session: Optional[str] = Field(None,
                                                          description="Trade session. Available values: PreMarket/Regular/AfterHours/OverNight"),
                     market: Optional[str] = Field(None,
                                                   description="Market. Available US/HK. All symbols must be in the same market."),
                     timezone: Optional[str] = Field(None,
                                                     description="Timezone of Options expiry, US/Easter or Asia/Hone_Kong. All symbols must be in the same timezone."),
                     include_hour_trading: bool = False,
                     date: Optional[str] = Field(None,
                                                 description="Date in 'YYYY-MM-DD' format. Only support for STK sec_type. e.g. 2026-06-18")
                     ) -> Any:
        """
        获取分时数据
        """
        if sec_type.upper() not in [
            SecurityType.STK.value, SecurityType.OPT.value
        ]:
            raise ValueError(
                f"Invalid security type: {sec_type}, must be one of {SecurityType.STK.value}, {SecurityType.OPT.value}"
            )
        # 根据合约类型选择不同的API调用
        if sec_type.upper() == "OPT":
            return QuoteApi.quote_client.get_option_timeline(
                identifiers=symbols,
                market=market,
                begin_time=begin_time,
                timezone=timezone)
        else:
            if date:
                return QuoteApi.quote_client.get_timeline_history(symbols,
                                                                  date)
            else:
                return QuoteApi.quote_client.get_timeline(
                    symbols,
                    include_hour_trading=include_hour_trading,
                    begin_time=begin_time,
                    trade_session=trade_session)

    @staticmethod
    @server.tool(description='Get stock capital flow data.')
    @ApiHelper.handle_result
    def get_capital_flow(symbol: str = Field(..., description="Stock symbol. e.g. 'AAPL', '00700'"),
                         market: str = Field(..., description="Market. US/HK", pattern=r'^(US|HK)$'),
                         period: str = Field(...,
                                             description="Data period. Available values: intraday/day/week/month/year/quarter/6month",
                                             pattern=r'^(intraday|day|week|month|year|quarter|6month)$'),
                         begin_time: Union[int, str] = Field(-1,
                                                             description="Begin time date string 'YYYY-MM-DD HH:MM:SS' or timestamp in milliseconds. 开始时间"),
                         end_time: Union[int, str] = Field(-1,
                                                           description="End time date string 'YYYY-MM-DD HH:MM:SS' or timestamp in milliseconds, must be later than begin_time. 结束时间"),
                         limit: int = 200) -> Any:
        """
        获取资金流向数据
        """
        return QuoteApi.quote_client.get_capital_flow(symbol,
                                                      market=market,
                                                      period=period,
                                                      begin_time=begin_time,
                                                      end_time=end_time,
                                                      limit=limit)

    @staticmethod
    @server.tool(description='Get stock capital distribution.')
    @ApiHelper.handle_result
    def get_capital_distribution(symbol: str = Field(..., description="Stock symbol. e.g. 'AAPL', '00700'"),
                                 market: str = Field(..., description="Market. US/HK", pattern=r'^(US|HK)$')
                                 ) -> Any:
        """
        获取资金分布数据
        """
        return QuoteApi.quote_client.get_capital_distribution(symbol=symbol,
                                                              market=market)

    @staticmethod
    @server.tool(description='Get Hong Kong broker trading seat data.')
    @ApiHelper.handle_result
    def get_stock_broker(symbol: str = Field(..., description="Stock symbol. e.g. '00700', only support HK stock",
                                             pattern=r'^\d{5}$'),
                         limit: int = 40) -> Any:
        """
        获取股票经纪商数据
        """

        return QuoteApi.quote_client.get_stock_broker(symbol,
                                                      limit=limit)

    @staticmethod
    @server.tool(description='Get all available option expiration dates for a specified underlying symbol.')
    @ApiHelper.handle_result
    def get_option_expirations(symbols: list[str] = Field(...,
                                                          description="List of option underlying symbols. e.g. US Option: 'AAPL'; HK Option: 'TCH.HK'."
                                                                      "if symbol in \\d{5} format like '00700', then need to convert format (e.g., 00700 = TCH.HK),  call get_hk_option_symbols to get the mapping first."),
                               market: Optional[str] = Field(...,
                                                             description="Market, US/HK. All symbols must be in the same market.",
                                                             pattern=r'^(US|HK)$')
                               ) -> Any:
        """
        获取期权到期日列表
        
        Rule:
        if symbol in \d{5} then need to call get_hk_option_symbols first to
        convert format (e.g., 00700 = TCH.HK)
        """
        return QuoteApi.quote_client.get_option_expirations(symbols, market=market)

    @staticmethod
    @server.tool(
        description='Get option data for a specified underlying symbol, expiration date, and filter conditions.')
    @ApiHelper.handle_result
    def get_option_chain(
            symbol: str = Field(...,
                                description="Option underlying symbol. e.g. US Option: 'AAPL'; HK Option: 'TCH.HK'. if symbol in \\d{5} like 00700, then need to call get_hk_option_symbols first to convert format (e.g., 00700 = TCH.HK)"),
            expiry: Union[str, int] = Field(
                ...,
                description=
                "Expiration date in 'YYYY-MM-DD' format or timestamp in milliseconds. e.g. 2021-06-18 or 1560484800000"
            ),
            option_filter: Optional[dict] = Field(None,
                                                  description="Option filter conditions. 期权筛选条件. Example: {  \"implied_volatility_min\": 0.5,  \"implied_volatility_max\": 0.9,  \"delta_min\": 0,  \"delta_max\": 1,  \"open_interest_min\": 100,  \"open_interest_max\": null,  \"volume_min\": null,  \"volume_max\": 100,  \"gamma_min\": 0.005,  \"gamma_max\": 0.5,  \"theta_min\": null,  \"theta_max\": -0.05,  \"vega_min\": 0.01,  \"vega_max\": 0.5,  \"in_the_money\": true}"),
            return_greek_value: Optional[bool] = None,
            market: Optional[str] = Field(
                ...,
                description="Market, US/HK. All symbols must be in the same market.",
                pattern=r'^(US|HK)$'),
            timezone: Optional[str] = Field(
                ...,
                description=
                "Timezone for the option expiry"
            )
    ) -> Any:
        """
        获取期权链数据
        """
        if isinstance(expiry, str):
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', expiry):
                raise ValueError(
                    "expiry must be in YYYY-MM-DD format when provided as a string"
                )
        elif isinstance(expiry, int):
            if len(str(expiry)) != 13:
                raise ValueError(
                    "expiry must be a valid timestamp in milliseconds when provided as an integer"
                )

        # 转换期权筛选条件
        filter_obj = None
        if option_filter:
            filter_fields = {
                'implied_volatility_min': option_filter.get(
                    'implied_volatility_min'),
                'implied_volatility_max': option_filter.get(
                    'implied_volatility_max'),
                'delta_min': option_filter.get('delta_min'),
                'delta_max': option_filter.get('delta_max'),
                'open_interest_min': option_filter.get('open_interest_min'),
                'open_interest_max': option_filter.get('open_interest_max'),
                'volume_min': option_filter.get('volume_min'),
                'volume_max': option_filter.get('volume_max'),
                'gamma_min': option_filter.get('gamma_min'),
                'gamma_max': option_filter.get('gamma_max'),
                'theta_min': option_filter.get('theta_min'),
                'theta_max': option_filter.get('theta_max'),
                'vega_min': option_filter.get('vega_min'),
                'vega_max': option_filter.get('vega_max'),
                'in_the_money':
                    option_filter.get('in_the_money', None)
            }
            filter_obj = OptionFilter(**{k: v
                                         for k, v in filter_fields.items() if v is not None})

        return QuoteApi.quote_client.get_option_chain(
            symbol,
            expiry,
            option_filter=filter_obj,
            return_greek_value=return_greek_value,
            market=market,
            timezone=timezone)

    @staticmethod
    @server.tool(description='Get the code format for Hong Kong stock options (e.g., 00700 = TCH.HK)')
    @ApiHelper.handle_result
    def get_hk_option_symbols() -> Any:
        """
        获取港股期权代码格式(e.g., 00700 = TCH.HK).
        """
        return QuoteApi.quote_client.get_option_symbols(market=Market.HK)


class TradeApi:
    """交易API类
    """
    trade_client = TradeClient(_client_config)

    @staticmethod
    @server.tool(description='Get account position data.')
    def get_positions(sec_type: str = Field(SecurityType.STK.value,
                                            description="Security type. STK/OPT/FUT", pattern=r'^(STK|OPT|FUT)$'),
                      market: str = Field(Market.ALL.value,
                                          description="Market. US/HK/ALL", pattern=r'^(US|HK|ALL)$'),
                      symbol: Optional[str] = Field(None, description='Contract symbol. e.g. "AAPL", "00700"')
                      ) -> Any:
        """
        获取持仓信息
        """
        result = ApiHelper.serialize_list(
            TradeApi.trade_client.get_positions(sec_type=sec_type,
                                                market=market,
                                                symbol=symbol))
        if result:
            for item in result:
                item.pop('quantity', None)
                item.pop('position_scale', None)
        return result

    @staticmethod
    @server.tool(description='Get account asset information.')
    @ApiHelper.handle_result
    def get_assets(base_currency: Optional[str] = Field(None, description='Currency, e.g. USD, HKD'),
                   consolidated: bool = True) -> Any:
        """
        获取账户资产信息
        """
        return TradeApi.trade_client.get_prime_assets(
            base_currency=base_currency, consolidated=consolidated)

    @staticmethod
    @server.tool(description="Get historical account asset analysis")
    @ApiHelper.handle_result
    def get_analytics_asset(
            start_date: Optional[str] = Field(
                None,
                description="Start date in YYYY-MM-DD format. 开始日期",
                pattern=r"^\d{4}-\d{2}-\d{2}$"),
            end_date: Optional[str] = Field(
                None,
                description="End date in YYYY-MM-DD format. Must be later than start_date. 结束日期",
                pattern=r"^\d{4}-\d{2}-\d{2}$"),
            seg_type: Optional[str] = Field(
                None, description="Segment type. SEC/FUT/ALL"),
            currency: Optional[str] = None) -> Any:
        """
        Get analytics asset
        获取账户资产分析数据
        """
        if start_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', start_date):
            return {"error": "start_date must be in YYYY-MM-DD format"}
        if end_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', end_date):
            return {"error": "end_date must be in YYYY-MM-DD format"}
        return TradeApi.trade_client.get_analytics_asset(start_date=start_date,
                                                         end_date=end_date,
                                                         seg_type=seg_type,
                                                         currency=currency)

    @staticmethod
    @server.tool(description='Get contract information for a specified stock or option.')
    @ApiHelper.handle_result
    def get_contract(symbol: str = Field(...,
                                         description="Contract symbol. e.g. 'AAPL', '00700', 'CL2509'. If sec_type is OPT, expiry/strike/put_call also must be provided."),
                     sec_type: str = Field(..., description="Security type. STK/OPT/FUT", pattern=r'^(STK|OPT|FUT)$'),
                     expiry: Optional[str] = Field(None,
                                                   description="Option expiry date in 'YYYYMMDD' format, like '20250826'. If sec_type is OPT, this field must be provided.",
                                                   pattern=r'^\d{4}\d{2}\d{2}$'),
                     strike: Optional[float] = Field(None,
                                                     description="Option strike price. If sec_type is OPT, this field must be provided."),
                     put_call: Optional[str] = Field(None,
                                                     description="PUT/CALL. If sec_type is OPT, this field must be provided."),
                     currency: Optional[str] = None) -> Any:
        """
        获取合约信息
        """
        if sec_type.upper() == SecurityType.OPT.value:
            # 期权合约需要提供更多参数
            if not all([symbol, expiry, strike, put_call]):
                return {
                    "error":
                        'Missing required fields for option contract: symbol, expiry, strike, put_call'
                }
            if put_call.upper() in ['C', 'CALL']:
                put_call = 'CALL'
            elif put_call.upper() in ['P', 'PUT']:
                put_call = 'PUT'
            else:
                return {
                    "error": "Invalid put_call value, must be 'CALL' or 'PUT'"
                }
        return TradeApi.trade_client.get_contract(symbol=symbol,
                                                  sec_type=sec_type,
                                                  expiry=expiry,
                                                  strike=strike,
                                                  put_call=put_call,
                                                  currency=currency)

    @staticmethod
    @server.tool(description="Query the maximum tradable size of a stock or option in the account.")
    @ApiHelper.handle_result
    def get_estimate_tradable_quantity(
            action: str = Field(..., description="Order action. BUY/SELL", pattern=r'^(BUY|SELL)$'),
            order_type: str = Field(..., description="Order type. MKT/LMT/STP/STP_LMT",
                                    pattern=r'^(MKT|LMT|STP|STP_LMT)$'),
            quantity: int = Field(..., description="Order quantity. Must be a positive integer.", gt=0),
            sec_type: str = Field(..., description="Security type. STK/OPT/FUT", pattern=r'^(STK|OPT|FUT|MLEG|FUND)$'),
            symbol: Optional[str] = Field(None,
                                          description="Contract symbol. e.g. 'AAPL', '00700', 'CL2509'. If sec_type is OPT, expiry/strike/put_call also must be provided."),
            currency: Optional[str] = Field("USD", description="Currency, USD/HKD"),
            limit_price: Optional[float] = Field(None,
                                                 description="Limit price, required if order_type is LMT or STP_LMT"),
            time_in_force: Optional[str] = Field(None, description="Time in force. DAY/GTC/GTD"),
            outside_rth: Optional[bool] = Field(None, description="Outside regular trading hours, True/False"),
            aux_price: Optional[float] = Field(None,
                                               description="Auxiliary price, required if order_type is STP or STP_LMT"),
            trailing_percent: Optional[float] = None,
            expire_time: Optional[str] = Field(None,
                                               description="Order expiration time in 'YYYY-MM-DD HH:MM:SS' format, required if time_in_force is GTD"),
            user_mark: Optional[str] = None,
            combo_type: Optional[str] = None,
            contract_legs: Optional[list[dict]] = None,
            expiry: Optional[str] = Field(None,
                                          description="Option expiry date in 'YYYYMMDD' format, like '20250826'. If sec_type is OPT, this field must be provided.",
                                          pattern=r'^\d{4}\d{2}\d{2}$'),
            strike: Optional[float] = Field(None,
                                            description="Option strike price. If sec_type is OPT, this field must be provided."),
            put_call: Optional[str] = Field(None,
                                            description="PUT/CALL. If sec_type is OPT, this field must be provided."),
            trading_session_type: Optional[str] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            seg_type: Optional[str] = None

    ) -> Any:
        """
        Get estimate tradable quantity
        获取可交易数量. 参数构造与下单一致.
        """
        order = TradeApi._prepare_order(
            action=action,
            order_type=order_type,
            quantity=quantity,
            sec_type=sec_type,
            symbol=symbol,
            currency=currency,
            limit_price=limit_price,
            time_in_force=time_in_force,
            outside_rth=outside_rth,
            aux_price=aux_price,
            trailing_percent=trailing_percent,
            expire_time=expire_time,
            user_mark=user_mark,
            combo_type=combo_type,
            contract_legs=contract_legs,
            expiry=expiry,
            strike=strike,
            put_call=put_call,
            trading_session_type=trading_session_type,
            start_time=start_time,
            end_time=end_time
        )
        return TradeApi.trade_client.get_estimate_tradable_quantity(order=order, seg_type=seg_type)

    @staticmethod
    @server.tool(description="Place Order")
    @ApiHelper.handle_result
    def place_order(action: str = Field(..., description="Order action. BUY/SELL", pattern=r'^(BUY|SELL)$'),
                    order_type: str = Field(..., description="Order type. MKT/LMT/STP/STP_LMT",
                                            pattern=r'^(MKT|LMT|STP|STP_LMT)$'),
                    quantity: int = Field(..., description="Order quantity. Must be a positive integer.", gt=0),
                    sec_type: Union[SecurityType, str] = Field(..., description="Security type. STK/OPT/FUT",
                                                               pattern=r'^(STK|OPT|FUT)$'),
                    symbol: Optional[str] = Field(None,
                                                  description="Contract symbol. e.g. 'AAPL', '00700', 'CL2509'. If sec_type is OPT, expiry/strike/put_call also must be provided."),
                    currency: Optional[str] = Field("USD", description="Currency, USD/HKD"),
                    limit_price: Optional[float] = Field(None,
                                                         description="Limit price, required if order_type is LMT or STP_LMT"),
                    time_in_force: Optional[str] = Field(None, description="Time in force. DAY/GTC/GTD"),
                    outside_rth: Optional[bool] = Field(None, description="Outside regular trading hours, True/False"),
                    aux_price: Optional[float] = Field(None,
                                                       description="Auxiliary price, required if order_type is STP or STP_LMT"),
                    trailing_percent: Optional[float] = None,
                    expire_time: Optional[str] = Field(None,
                                                       description="Order expiration time in 'YYYY-MM-DD HH:MM:SS' format, required if time_in_force is GTD"),
                    user_mark: Optional[str] = None,
                    combo_type: Optional[str] = None,
                    contract_legs: Optional[list[dict]] = None,
                    expiry: Optional[str] = Field(None,
                                                  description="Option expiry date in 'YYYYMMDD' format, like '20250826'. If sec_type is OPT, this field must be provided.",
                                                  pattern=r'^\d{4}\d{2}\d{2}$'),
                    strike: Optional[float] = Field(None,
                                                    description="Option strike price. If sec_type is OPT, this field must be provided."),
                    put_call: Optional[str] = Field(None,
                                                    description="PUT/CALL. If sec_type is OPT, this field must be provided."),
                    trading_session_type: Optional[str] = None,
                    start_time: Optional[int] = None,
                    end_time: Optional[int] = None) -> Any:
        """
        Place order
        下单

        return：
        id: int, Order ID. 订单ID
        order_id: Order ID of account, not recommended to use this field.
        """
        # 检查是否处于只读模式
        if _read_only_mode:
            return {
                "error": "Order placement is not allowed in read-only mode"
            }

        order = TradeApi._prepare_order(
            action=action,
            order_type=order_type,
            quantity=quantity,
            sec_type=sec_type,
            symbol=symbol,
            currency=currency,
            limit_price=limit_price,
            time_in_force=time_in_force,
            outside_rth=outside_rth,
            aux_price=aux_price,
            trailing_percent=trailing_percent,
            expire_time=expire_time,
            user_mark=user_mark,
            combo_type=combo_type,
            contract_legs=contract_legs,
            expiry=expiry,
            strike=strike,
            put_call=put_call,
            trading_session_type=trading_session_type,
            start_time=start_time,
            end_time=end_time,
        )

        # 如果返回的是错误信息，直接返回
        if isinstance(order, dict) and "error" in order:
            return order
        TradeApi.trade_client.place_order(order)
        return order

    @staticmethod
    @server.tool(description="Modify Order")
    @ApiHelper.handle_result
    def modify_order(
            id: str = Field(..., description='Order.id, a multi bit number, like 38000878710423552'),
            quantity: Optional[int] = Field(None, description="Modified quantity"),
            limit_price: Optional[float] = Field(None, description="Modified limit price"),
            aux_price: Optional[float] = Field(None, description="Modified auxiliary price"),
            trailing_percent: Optional[float] = None,
            time_in_force: Optional[str] = Field(None, description="Modified time in force. DAY/GTC/GTD"),
            outside_rth: Optional[bool] = Field(None, description="Modified outside regular trading hours, True/False"),
            expire_time: Optional[str] = Field(None,
                                               description="Modified order expiration time in 'YYYY-MM-DD HH:MM:SS' format, required if time_in_force is GTD"),
            user_mark: Optional[str] = None,
    ) -> Any:
        """
        Modify order
        修改订单
        """
        if _read_only_mode:
            return {
                "error": "Order modification is not allowed in read-only mode"
            }

        # 将字符串转换为整数
        try:
            order_id = int(id)
        except (ValueError, TypeError):
            return {"error": f"Invalid order ID format: {id}"}

        order = TradeApi.trade_client.get_order(id=order_id)
        return TradeApi.trade_client.modify_order(
            order,
            id=order_id,
            quantity=quantity,
            limit_price=limit_price,
            aux_price=aux_price,
            trailing_percent=trailing_percent,
            time_in_force=time_in_force,
            outside_rth=outside_rth,
            expire_time=expire_time,
            user_mark=user_mark,
        )

    @staticmethod
    @server.tool(description="Preview Order")
    @ApiHelper.handle_result
    def preview_order(
            action: str = Field(..., description="Order action. BUY/SELL", pattern=r'^(BUY|SELL)$'),
            order_type: str = Field(..., description="Order type. MKT/LMT/STP/STP_LMT",
                                    pattern=r'^(MKT|LMT|STP|STP_LMT)$'),
            quantity: int = Field(..., description="Order quantity. Must be a positive integer.", gt=0),
            sec_type: str = Field(..., description="Security type. STK/OPT/FUT", pattern=r'^(STK|OPT|FUT|MLEG|FUND)$'),
            symbol: Optional[str] = Field(None,
                                          description="Contract symbol. e.g. 'AAPL', '00700', 'CL2509'. If sec_type is OPT, expiry/strike/put_call also must be provided."),
            currency: Optional[str] = Field("USD", description="Currency, USD/HKD"),
            limit_price: Optional[float] = Field(None,
                                                 description="Limit price, required if order_type is LMT or STP_LMT"),
            time_in_force: Optional[str] = Field(None, description="Time in force. DAY/GTC/GTD"),
            outside_rth: Optional[bool] = Field(None, description="Outside regular trading hours, True/False"),
            aux_price: Optional[float] = Field(None,
                                               description="Auxiliary price, required if order_type is STP or STP_LMT"),
            trailing_percent: Optional[float] = None,
            expire_time: Optional[str] = Field(None,
                                               description="Order expiration time in 'YYYY-MM-DD HH:MM:SS' format, required if time_in_force is GTD"),
            user_mark: Optional[str] = None,
            combo_type: Optional[str] = None,
            contract_legs: Optional[list[dict]] = None,
            expiry: Optional[str] = Field(None,
                                          description="Option expiry date in 'YYYYMMDD' format, like '20250826'. If sec_type is OPT, this field must be provided.",
                                          pattern=r'^\d{4}\d{2}\d{2}$'),
            strike: Optional[float] = Field(None,
                                            description="Option strike price. If sec_type is OPT, this field must be provided."),
            put_call: Optional[str] = Field(None,
                                            description="PUT/CALL. If sec_type is OPT, this field must be provided."),
            trading_session_type: Optional[str] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None
    ) -> Any:
        """
        Preview order
        预览订单
        """
        order = TradeApi._prepare_order(
            action=action,
            order_type=order_type,
            quantity=quantity,
            sec_type=sec_type,
            symbol=symbol,
            currency=currency,
            limit_price=limit_price,
            time_in_force=time_in_force,
            outside_rth=outside_rth,
            aux_price=aux_price,
            trailing_percent=trailing_percent,
            expire_time=expire_time,
            user_mark=user_mark,
            combo_type=combo_type,
            contract_legs=contract_legs,
            expiry=expiry,
            strike=strike,
            put_call=put_call,
            trading_session_type=trading_session_type,
            start_time=start_time,
            end_time=end_time,
        )

        # 如果返回的是错误信息，直接返回
        if isinstance(order, dict) and "error" in order:
            return order

        preview_result = TradeApi.trade_client.preview_order(order)
        return preview_result

    @staticmethod
    @server.tool(description="Get the full list of orders for the account.")
    @ApiHelper.handle_result
    def get_orders(symbol: Optional[str] = None,
                   sec_type: Optional[str] = Field(SecurityType.ALL.value,
                                                   description="Security type filter, available values are: ALL/STK/OPT/FUT"),
                   market: str = Field(Market.ALL.value,
                                       description="Market filter, available values are: US/HK/ALL"),
                   start_time: Optional[str] = Field(None,
                                                     description='Start time (inclusive). Either timestamp in milliseconds (13-digit integer) or date string (e.g., "2017-01-01", "2017-01-01 12:00:00" 开始时间(闭区间，包含).'),
                   end_time: Optional[str] = Field(None,
                                                   description='End time (exclusive). Either timestamp in milliseconds (13-digit integer) or date string (e.g., "2017-01-01", "2017-01-01 12:00:00" 结束时间(开区间，不包含).'),
                   limit: int = 100,
                   is_brief: bool = False,
                   states: Optional[list[str]] = Field(None,
                                                       description="Order status filter, available values are: Filled 已成交/Cancelled 已取消/Submitted 已提交,未成交")) -> Any:
        """
        Get orders
        获取订单列表
        """
        return TradeApi.trade_client.get_orders(symbol=symbol,
                                                sec_type=sec_type,
                                                market=market,
                                                start_time=start_time,
                                                end_time=end_time,
                                                limit=limit,
                                                is_brief=is_brief,
                                                states=states)

    @staticmethod
    @server.tool(description="Get detailed information for a specified order.")
    @ApiHelper.handle_result
    def get_order(id: str = Field(..., description='Order.id, a multi bit number, like 38000878710423552')) -> Any:
        """
        Get order
        获取订单详情
        
        :param id: Order ID, 订单ID
        """
        if len(id) < 10:
            return {"error": f"Invalid order ID: {id}, please use order.id field value"}
        try:
            order_id = int(id)
        except (ValueError, TypeError):
            return {"error": f"Invalid order ID format: {id}"}

        return TradeApi.trade_client.get_order(id=order_id)

    @staticmethod
    @server.tool(description="Cancel Order")
    @ApiHelper.handle_result
    def cancel_order(id: str = Field(..., description='Order.id, like 38000878710423552')) -> Any:
        """
        Cancel order
        撤销订单
        
        :param id: Order ID, 订单ID
        """
        if _read_only_mode:
            return {
                "error": "Order cancellation is not allowed in read-only mode"
            }
        if len(id) < 10:
            return {"error": f"Invalid order ID: {id}, please use order.id field value"}
        try:
            order_id = int(id)
        except (ValueError, TypeError):
            return {"error": f"Invalid order ID format: {id}"}

        return TradeApi.trade_client.cancel_order(id=order_id)

    @staticmethod
    @server.tool(description="Get transaction information for filled orders.")
    @ApiHelper.handle_result
    def get_transactions(
            order_id: Optional[str] = Field(None, description="Order ID to filter transactions. 订单ID过滤"),
            symbol: Optional[str] = Field(None, description="Symbol to filter transactions. 合约代码过滤"),
            sec_type: Optional[str] = Field(None, description="Security type to filter transactions. Available values STK/OPT/FUT/FUND, 合约类型过滤"),
            start_time: Optional[int] = Field(
                ..., description="Start time in milliseconds"),
            end_time: Optional[int] = Field(
                ..., description="End time in milliseconds, must be later than start_time"),
            expiry: Optional[str] = Field(None,
                                         description="Option expiry date in 'YYYYMMDD' format, like '20250830'. If sec_type is OPT, this field must be provided.",
                                         pattern=r'^\d{4}\d{2}\d{2}$'),
            strike: Optional[float] = Field(None,
                                           description="Option strike price. If sec_type is OPT, this field must be provided."),
            put_call: Optional[str] = Field(None,
                                           description="PUT/CALL. If sec_type is OPT, this field must be provided."),
            max_items: int = Field(
                1000,
                description=
                "Maximum number of items to return. 0 means all available items"),
    ) -> Any:
        """
        Get transactions
        获取成交记录
        """
        all_transactions = []
        page_token = ''
        unlimited = max_items == 0
        items_fetched = 0
        page_size = 100
        if max_items < page_size:
            page_size = max_items
        # 处理订单ID，将字符串转换为整数
        processed_order_id = None
        if order_id:
            try:
                processed_order_id = int(order_id)
            except (ValueError, TypeError):
                return {"error": f"Invalid order ID format: {order_id}"}

        while True:
            result = TradeApi.trade_client.get_transactions(
                order_id=processed_order_id,
                symbol=symbol,
                sec_type=sec_type,
                start_time=start_time,
                end_time=end_time,
                limit=page_size,
                expiry=expiry,
                strike=strike,
                put_call=put_call,
                page_token=page_token)

            # 检查返回结果的类型，trade_client.get_transactions返回的应该是TransactionsResponse对象
            if hasattr(result, 'result') and isinstance(result.result, list):
                current_page = result.result
                next_page_token = result.next_page_token if hasattr(
                    result, 'next_page_token') else None
            elif isinstance(result, list):
                current_page = result
                next_page_token = None
            else:
                current_page = []
                next_page_token = None

            # 如果没有结果，则退出循环
            if not current_page:
                break

            all_transactions.extend(current_page)
            items_fetched += len(current_page)

            # 如果没有下一页token或已达到要求的最大数量，则退出循环
            if not next_page_token or (not unlimited
                                       and items_fetched >= max_items):
                break

            # 使用next_page_token作为下一页的token
            page_token = next_page_token

        # 如果设置了最大项目数，则截断结果
        final_transactions = all_transactions[:
                                              max_items] if not unlimited and max_items > 0 else all_transactions
        return final_transactions

    @staticmethod
    def _prepare_order(action: str,
                       order_type: str,
                       quantity: int,
                       sec_type: Union[SecurityType, str],
                       symbol: Optional[str] = None,
                       currency: str = Currency.USD.value,
                       limit_price: Optional[float] = None,
                       time_in_force: Optional[str] = None,
                       outside_rth: Optional[bool] = None,
                       aux_price: Optional[float] = None,
                       trailing_percent: Optional[float] = None,
                       expire_time: Optional[str] = None,
                       user_mark: Optional[str] = None,
                       combo_type: Optional[str] = None,
                       contract_legs: Optional[list[dict]] = None,
                       order_id: Optional[str] = None,
                       id: Optional[str] = None,
                       expiry: Optional[str] = None,
                       strike: Optional[float] = None,
                       put_call: Optional[str] = None,
                       trading_session_type: Optional[str] = None,
                       **kwargs) -> Any:
        if sec_type.upper() == SecurityType.OPT.value:
            # 期权合约需要提供更多参数
            if not all([symbol, expiry, strike, put_call]):
                return {
                    "error":
                        'Missing required fields for option contract: symbol, expiry, strike, put_call'
                }
            if put_call.upper() in ['C', 'CALL']:
                put_call = 'CALL'
            elif put_call.upper() in ['P', 'PUT']:
                put_call = 'PUT'
            else:
                return {
                    "error": "Invalid put_call value, must be 'CALL' or 'PUT'"
                }
            contract = option_contract_by_symbol(symbol=symbol,
                                                 expiry=expiry,
                                                 strike=strike,
                                                 put_call=put_call,
                                                 currency=currency)
        elif sec_type.upper() == SecurityType.FUT.value:
            contract = future_contract(symbol=symbol, currency=currency)
        elif sec_type.upper() == SecurityType.STK.value:
            contract = stock_contract(symbol=symbol, currency=currency)
        elif sec_type.upper() == SecurityType.MLEG.value:
            if not contract_legs:
                return {
                    "error": "Missing contract_legs for MLEG security type"
                }
            legs = []
            for leg_param in contract_legs:
                leg = contract_leg(symbol=leg_param.get('symbol'),
                                   sec_type=leg_param.get(
                                       'sec_type', SecurityType.STK.value),
                                   expiry=leg_param.get('expiry'),
                                   strike=leg_param.get('strike'),
                                   put_call=leg_param.get('put_call'),
                                   action=leg_param.get('action'),
                                   ratio=leg_param.get('ratio', 1))
                legs.append(leg)

            order = combo_order(_client_config.account,
                                legs,
                                combo_type=combo_type,
                                action=action,
                                quantity=quantity,
                                order_type=order_type,
                                limit_price=limit_price,
                                aux_price=aux_price,
                                trailing_percent=trailing_percent)
            order.user_mark = user_mark
            order.time_in_force = time_in_force
            order.trading_session_type = trading_session_type
            order.id = id
            order.order_id = order_id
            order.expire_time = expire_time
            order.outside_rth = outside_rth
            return order
        else:
            return {"error": f"Unsupported security type: {sec_type}"}

        order_type = order_type.upper()
        if order_type == OrderType.LMT.value:
            order = limit_order(account=_client_config.account,
                                contract=contract,
                                action=action,
                                quantity=quantity,
                                limit_price=limit_price,
                                time_in_force=time_in_force)
        elif order_type == OrderType.MKT.value:
            order = market_order(account=_client_config.account,
                                 contract=contract,
                                 action=action,
                                 quantity=quantity,
                                 time_in_force=time_in_force)
        elif order_type == OrderType.STP.value:
            order = stop_order(account=_client_config.account,
                               contract=contract,
                               action=action,
                               quantity=quantity,
                               aux_price=aux_price,
                               time_in_force=time_in_force)
        elif order_type == OrderType.STP_LMT.value:
            order = stop_limit_order(account=_client_config.account,
                                     contract=contract,
                                     action=action,
                                     quantity=quantity,
                                     limit_price=limit_price,
                                     aux_price=aux_price,
                                     time_in_force=time_in_force)
        elif order_type == OrderType.TRAIL.value:
            order = trail_order(account=_client_config.account,
                                contract=contract,
                                action=action,
                                quantity=quantity,
                                trailing_percent=trailing_percent,
                                aux_price=aux_price,
                                time_in_force=time_in_force)
        elif order_type in (OrderType.TWAP.value, OrderType.VWAP.value):
            if 'start_time' not in kwargs or 'end_time' not in kwargs:
                return {
                    "error":
                        "TWAP and VWAP orders require start_time and end_time parameters"
                }

            algo_params = algo_order_params(
                start_time=kwargs.get('start_time'),
                end_time=kwargs.get('end_time'),
                no_take_liq=kwargs.get('no_take_liq', False),
                allow_past_end_time=kwargs.get('allow_past_end_time', False),
                participation_rate=kwargs.get('participation_rate', None))
            order = algo_order(account=_client_config.account,
                               contract=contract,
                               action=action,
                               quantity=quantity,
                               strategy=order_type,
                               algo_params=algo_params,
                               time_in_force=time_in_force)
        else:
            return {"error": f"Unsupported order type: {order_type}"}

        if outside_rth is not None:
            order.outside_rth = outside_rth
        if user_mark is not None:
            order.user_mark = user_mark
        if order.expire_time is not None:
            order.expire_time = expire_time
        if id is not None:
            # 将字符串转换为整数
            try:
                order.id = int(id)
            except (ValueError, TypeError):
                return {"error": f"Invalid order ID format: {id}"}
        if order_id is not None:
            # 将字符串转换为整数
            try:
                order.order_id = int(order_id)
            except (ValueError, TypeError):
                return {"error": f"Invalid order_id format: {order_id}"}
        if trading_session_type is not None:
            order.trading_session_type = trading_session_type

        return order


def main():
    """Main entry function for MCP server, used by CLI"""
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nStop Tiger MCP Server...")
        sys.exit(0)

    # Register SIGINT handler (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    print("Tiger MCP Server started in stdio mode")
    if _read_only_mode:
        print("Running in READ-ONLY mode - order placement is disabled")
    print("Press Ctrl+C to exit")

    try:
        server.run('stdio')
    except Exception as e:
        print(f"Server error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
