#!/usr/bin/env python3
import functools
import os
import re
from datetime import datetime
from typing import Optional, Any, Union

import pandas as pd
from docutils.nodes import description
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from tigeropen.common.consts import Market, SecurityType, Currency, BarPeriod, QuoteRight, \
    OrderType
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
from tigeropen.quote.domain.filter import StockFilter, SortFilterData, ScannerResult
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient

_client_config = TigerOpenClientConfig()

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


class QuoteApi:
    quote_client = QuoteClient(_client_config)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_quote_permissions() -> Any:
        """
        Get quote permissions
        获取我的行情权限
        """
        return QuoteApi.quote_client.get_quote_permission()

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_market_status(market: str = Market.ALL.value,
                          lang: Optional[str] = None) -> Any:
        """
        Get market status
        获取市场的状态
        """
        status = QuoteApi.quote_client.get_market_status(market, lang=lang)
        return status

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_trading_calendar(
            market: Market = Field(..., description="Market. 市场. US/HK/CN"),
            begin_date: Optional[str] = Field(
                None,
                description="Start date in YYYY-MM-DD format, included. 开始日期",
                pattern=r"^\d{4}-\d{2}-\d{2}$"),
            end_date: Optional[str] = Field(
                None,
                description="End date in YYYY-MM-DD format, excluded, must later than begin_date. 结束日期",
                pattern=r"^\d{4}-\d{2}-\d{2}$")) -> Any:
        """
        Get trading calendar
        获取交易日历
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
    @server.tool(description='Market scanner 选股器')
    @ApiHelper.handle_result
    def market_scanner(market: str = Market.US.value,
                       filters: Optional[list[dict]] = None,
                       sort_field: Optional[dict] = None,
                       max_items: int = 1000) -> Any:
        """
        Market scanner -
        选股器

        :param market: Market. 市场. US/HK
        :param filters: List of filter conditions. 过滤条件列表。
            Example: [
              {
                "field_type": "StockField",
                "field_name": "current_ChangeRate",
                "filter_min": 0.01,
                "filter_max": 0.5,
                "is_no_filter": false
              },
              {
                "field_type": "AccumulateField",
                "field_name": "ChangeRate",
                "filter_min": 0.01,
                "filter_max": 1,
                "is_no_filter": false,
                "accumulate_period": "Last_Year"
              },
              {
                "field_type": "FinancialField",
                "field_name": "LYR_PE",
                "filter_min": 1,
                "filter_max": 100,
                "is_no_filter": false,
                "financial_period": "LTM"
              },
              {
                "field_type": "MultiTagField",
                "field_name": "Concept",
                "tag_list": ["BK4562", "BK4575"],
                "is_no_filter": false
              }
            ]
        :param sort_field: Sort field and direction. 排序字段和方向。
            Example: {
              "field_type": "StockField",
              "field_name": "FloatShare",
              "sort_dir": "ASC",
              "period": null
            }
        :param max_items: 最多返回的条目数
        :return: ScannerResult object containing result items and symbols from all pages

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
    @server.tool()
    @ApiHelper.handle_result
    def get_realtime_quote(
        symbols: list[str],
        sec_type: Union[SecurityType,
                        str] = Field(...,
                                     description="Security type. STK/OPT/FUT",
                                     pattern=r'^(STK|OPT|FUT)$'),
        include_hour_trading: bool = False,
        market: Optional[str] = Field(None, description="Market. US/HK"),
        timezone: Optional[str] = Field(
            None,
            description=
            "Timezone of Options expiry, US/Easter or Asia/Hone_Kong")
    ) -> Any:
        """
        Get realtime quotes
        获取实时行情
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
    @server.tool()
    @ApiHelper.handle_result
    def get_depth_quote(symbols: Union[str, list[str]],
                        sec_type: Union[SecurityType, str],
                        market: Union[Market, str],
                        timezone: Optional[str] = None) -> Any:
        """
        Get depth quotes (order book)
        获取深度行情
        """
        if SecurityType.OPT.value == sec_type.upper():
            return QuoteApi.quote_client.get_option_depth(identifiers=symbols,
                                                          market=market,
                                                          timezone=timezone)
        return QuoteApi.quote_client.get_depth_quote(symbols=symbols,
                                                     market=market)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_trade_ticks(symbols: Union[str, list[str]],
                        sec_type: Union[SecurityType, str],
                        trade_session: Optional[str] = None,
                        begin_index: Optional[int] = None,
                        end_index: Optional[int] = None,
                        limit: Optional[int] = None,
                        timezone: Optional[str] = None) -> Any:
        """
        Get trade ticks (detailed transaction data).
        获取逐笔成交数据
        """
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
    @server.tool()
    @ApiHelper.handle_result
    def get_bars(symbols: Union[str, list[str]],
                 sec_type: Union[SecurityType, str],
                 period: str = Field(None, description="Bar period. K线周期. Available values: day/week/month/year/1min/3min/5min/10min/15min/30min/60min",
                                     pattern= r'^(day|week|month|year|1min|3min|5min|10min|15min|30min|60min)$'),
                 limit: Optional[int] = 251,
                 right: str = QuoteRight.BR.value,
                 begin_time: Union[int, str] = -1,
                 end_time: Union[int, str] = -1,
                 trade_session: Optional[str] = None,
                 market: Optional[str] = None,
                 timezone: Optional[str] = None) -> Any:
        """
        Get k-line data
        获取K线数据

        :param period   DAY = 'day'  # 日K
                        WEEK = 'week'  # 周K
                        MONTH = 'month'  # 月K
                        YEAR = 'year'  # 年K
                        ONE_MINUTE = '1min'  # 1分钟
                        THREE_MINUTES = '3min'  # 3分钟
                        FIVE_MINUTES = '5min'  # 5分钟
                        TEN_MINUTES = '10min'  # 10分钟
                        FIFTEEN_MINUTES = '15min'  # 15分钟
                        HALF_HOUR = '30min'  # 30分钟
                        ONE_HOUR = '60min'  # 60分钟
        """
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
    @server.tool()
    @ApiHelper.handle_result
    def get_timeline(symbols: Union[str, list[str]],
                     sec_type: Union[SecurityType, str],
                     begin_time: Union[int, str] = -1,
                     trade_session: Optional[str] = None,
                     market: Optional[str] = None,
                     timezone: Optional[str] = None,
                     include_hour_trading: bool = False,
                     date: Optional[str] = None,
                     right: str = QuoteRight.BR.value) -> Any:
        """
        Get timeline data
        获取分时数据
        """
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
                                                                  date,
                                                                  right=right)
            else:
                return QuoteApi.quote_client.get_timeline(
                    symbols,
                    include_hour_trading=include_hour_trading,
                    begin_time=begin_time,
                    trade_session=trade_session)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_capital_flow(symbol: str,
                         market: str,
                         period: str,
                         begin_time: Union[int, str] = -1,
                         end_time: Union[int, str] = -1,
                         limit: int = 200) -> Any:
        """
        Get capital flow
        获取资金流向数据
        """
        return QuoteApi.quote_client.get_capital_flow(symbol,
                                                      market=market,
                                                      period=period,
                                                      begin_time=begin_time,
                                                      end_time=end_time,
                                                      limit=limit)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_capital_distribution(symbol: str, market: str) -> Any:
        """
        获取资金分布数据
        """
        return QuoteApi.quote_client.get_capital_distribution(symbol,
                                                              market=market)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_stock_broker(symbol: str,
                         limit: int = 40,
                         lang: Optional[str] = None) -> Any:
        """
        Get stock broker data
        获取股票经纪商数据
        """

        return QuoteApi.quote_client.get_stock_broker(symbol,
                                                      limit=limit,
                                                      lang=lang)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_broker_hold(market: str = Market.HK.value,
                        order_by: str = 'marketValue',
                        direction: str = SortDirection.DESC.value,
                        limit: int = 50,
                        page: int = 0,
                        lang: Optional[str] = None) -> Any:
        """
        Get broker hold data
        获取经纪商持仓数据
        """

        return QuoteApi.quote_client.get_broker_hold(market=market,
                                                     order_by=order_by,
                                                     direction=direction,
                                                     limit=limit,
                                                     page=page,
                                                     lang=lang)

    @staticmethod
    @server.tool(description='Get option expiration dates')
    @ApiHelper.handle_result
    def get_option_expirations(symbols: list[str],
                               market: Optional[str] = None) -> Any:
        """
        Get option expiration dates
        获取期权到期日列表
        
        Rule:
        if symbol in \d{5} then need to call get_hk_option_symbols first to
        convert format (e.g., 00700 = TCH.HK)
        """
        market_param = Market(market) if market else None
        return QuoteApi.quote_client.get_option_expirations(
            symbols, market=market_param)

    @staticmethod
    @server.tool(description='Get option chain data')
    @ApiHelper.handle_result
    def get_option_chain(
        symbol: str,
        expiry: Union[str, int] = Field(
            ...,
            description=
            "Expiration date in 'YYYY-MM-DD' format or timestamp in milliseconds. e.g. 2021-06-18 or 1560484800000"
        ),
        option_filter: Optional[dict] = None,
        return_greek_value: Optional[bool] = None,
        market: Optional[str] = None,
        timezone: Optional[str] = Field(
            ...,
            description=
            "Timezone for the option chain data, if symbol in \d{5} then timezone is Asia/Hong_Kong"
        )
    ) -> Any:
        """
        Get option chain data
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
            from tigeropen.quote.domain.filter import OptionFilter
            filter_obj = OptionFilter()
            if 'strike_price_range' in option_filter:
                filter_obj.strike_price_range = option_filter[
                    'strike_price_range']
            if 'expire_date_range' in option_filter:
                filter_obj.expire_date_range = option_filter[
                    'expire_date_range']
            if 'strike_type' in option_filter:
                filter_obj.strike_type = option_filter['strike_type']
            if 'sort_by' in option_filter:
                filter_obj.sort_by = option_filter['sort_by']
            if 'sort_dir' in option_filter:
                filter_obj.sort_dir = SortDirection(option_filter['sort_dir'])

        return QuoteApi.quote_client.get_option_chain(
            symbol,
            expiry,
            option_filter=filter_obj,
            return_greek_value=return_greek_value,
            market=market,
            timezone=timezone)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_hk_option_symbols(market: str = Market.HK.value) -> Any:
        """
        获取港股期权代码格式(e.g., 00700 = TCH.HK).
        """
        return QuoteApi.quote_client.get_option_symbols(market=market)


class TradeApi:
    """交易API类
    """
    trade_client = TradeClient(_client_config)

    @staticmethod
    @server.tool()
    def get_positions(sec_type: str = SecurityType.STK.value,
                      currency: str = Currency.ALL.value,
                      market: str = Market.ALL.value,
                      symbol: Optional[str] = None) -> Any:
        """
        Get positions
        获取持仓信息
        """
        result = ApiHelper.serialize_list(
            TradeApi.trade_client.get_positions(sec_type=sec_type,
                                                currency=currency,
                                                market=market,
                                                symbol=symbol))
        if result:
            for item in result:
                item.pop('quantity', None)
                item.pop('position_scale', None)
        return result

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def get_assets(base_currency: Optional[str] = None,
                   consolidated: bool = True) -> Any:
        """
        Get assets
        获取账户资产信息
        """
        return TradeApi.trade_client.get_prime_assets(
            base_currency=base_currency, consolidated=consolidated)

    @staticmethod
    @server.tool(description="Get account assets analytics")
    @ApiHelper.handle_result
    def get_analytics_asset(
            start_date: Optional[str] = Field(
                None,
                description="Start date in YYYY-MM-DD format. 开始日期",
                pattern=r"^\d{4}-\d{2}-\d{2}$"),
            end_date: Optional[str] = Field(
                None,
                description="End date in YYYY-MM-DD format. 结束日期",
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
    @server.tool()
    @ApiHelper.handle_result
    def get_contract(symbol: str,
                     sec_type: str = SecurityType.STK.value,
                     expiry: Optional[str] = None,
                     strike: Optional[float] = None,
                     put_call: Optional[str] = None,
                     currency: Optional[str] = None) -> Any:
        """
        Get contract
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
    @server.tool(description="Get estimated tradable quantity")
    @ApiHelper.handle_result
    def get_estimate_tradable_quantity(action: str,
                    order_type: str,
                    quantity: int,
                    sec_type: Union[SecurityType, str],
                    symbol: Optional[str] = None,
                    currency: Optional[str] = Currency.USD.value,
                    limit_price: Optional[float] = None,
                    time_in_force: Optional[str] = None,
                    outside_rth: Optional[bool] = None,
                    aux_price: Optional[float] = None,
                    trailing_percent: Optional[float] = None,
                    expire_time: Optional[str] = None,
                    user_mark: Optional[str] = None,
                    combo_type: Optional[str] = None,
                    contract_legs: Optional[list[dict]] = None,
                    expiry: Optional[str] = None,
                    strike: Optional[float] = None,
                    put_call: Optional[str] = None,
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
    @server.tool()
    @ApiHelper.handle_result
    def place_order(action: str,
                    order_type: str,
                    quantity: int,
                    sec_type: Union[SecurityType, str],
                    symbol: Optional[str] = None,
                    currency: Optional[str] = Currency.USD.value,
                    limit_price: Optional[float] = None,
                    time_in_force: Optional[str] = None,
                    outside_rth: Optional[bool] = None,
                    aux_price: Optional[float] = None,
                    trailing_percent: Optional[float] = None,
                    expire_time: Optional[str] = None,
                    user_mark: Optional[str] = None,
                    combo_type: Optional[str] = None,
                    contract_legs: Optional[list[dict]] = None,
                    expiry: Optional[str] = None,
                    strike: Optional[float] = None,
                    put_call: Optional[str] = None,
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
    @server.tool()
    @ApiHelper.handle_result
    def modify_order(
        id: str,
        quantity: Optional[Union[int, float]] = None,
        limit_price: Optional[float] = None,
        aux_price: Optional[float] = None,
        trailing_percent: Optional[float] = None,
        time_in_force: Optional[str] = None,
        outside_rth: Optional[bool] = None,
        expire_time: Optional[str] = None,
        user_mark: Optional[str] = None,
    ) -> Any:
        """
        Modify order
        修改订单
        
        :param id: Order ID, 订单ID
        :param quantity: 修改的数量
        :param limit_price: 修改的限价
        :param aux_price: 修改的辅助价格
        :param trailing_percent: 修改的追踪百分比
        :param time_in_force: 修改的有效期类型
        :param outside_rth: 是否允许盘前盘后交易
        :param expire_time: 订单过期时间
        :param user_mark: 用户备注
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
    @server.tool()
    @ApiHelper.handle_result
    def preview_order(
        action: str,
        order_type: str,
        quantity: int,
        sec_type: Union[SecurityType, str],
        symbol: Optional[str] = None,
        currency: Optional[str] = Currency.USD.value,
        limit_price: Optional[float] = None,
        time_in_force: Optional[str] = None,
        outside_rth: Optional[bool] = None,
        aux_price: Optional[float] = None,
        trailing_percent: Optional[float] = None,
        expire_time: Optional[str] = None,
        user_mark: Optional[str] = None,
        combo_type: Optional[str] = None,
        contract_legs: Optional[list[dict]] = None,
        expiry: Optional[str] = None,
        strike: Optional[float] = None,
        put_call: Optional[str] = None,
        trading_session_type: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
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
    @server.tool()
    @ApiHelper.handle_result
    def get_orders(symbol: Optional[str] = None,
                   sec_type: Optional[str] = None,
                   market: str = Market.ALL.value,
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   limit: int = 100,
                   is_brief: bool = False,
                   states: Optional[list[str]] = Field(None, description="Order status filter, available values are: Filled 已成交/Cancelled 已取消/Submitted 已提交,未成交")) -> Any:
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
    @server.tool()
    @ApiHelper.handle_result
    def get_order(id: str) -> Any:
        """
        Get order
        获取订单详情
        
        :param id: Order ID, 订单ID
        """
        # 将字符串转换为整数
        try:
            order_id = int(id)
        except (ValueError, TypeError):
            return {"error": f"Invalid order ID format: {id}"}

        return TradeApi.trade_client.get_order(id=order_id)

    @staticmethod
    @server.tool()
    @ApiHelper.handle_result
    def cancel_order(id: str) -> Any:
        """
        Cancel order
        撤销订单
        
        :param id: Order ID, 订单ID
        """
        if _read_only_mode:
            return {
                "error": "Order cancellation is not allowed in read-only mode"
            }
        # 将字符串转换为整数
        try:
            order_id = int(id)
        except (ValueError, TypeError):
            return {"error": f"Invalid order ID format: {id}"}

        return TradeApi.trade_client.cancel_order(id=order_id)

    @staticmethod
    @server.tool(description="Get transactions 订单成交记录")
    @ApiHelper.handle_result
    def get_transactions(
        order_id: Optional[str] = None,
        symbol: Optional[str] = None,
        sec_type: Optional[Union[SecurityType, str]] = None,
        start_time: Optional[int] = Field(
            ..., description="Start time in milliseconds"),
        end_time: Optional[int] = Field(
            ..., description="End time in milliseconds"),
        expiry: Optional[str] = None,
        strike: Optional[float] = None,
        put_call: Optional[str] = None,
        max_items: int = Field(
            0,
            description=
            "Maximum number of items to return. 0 means all available items"),
    ) -> Any:
        """
        Get transactions
        获取成交记录
        
        当返回结果超过limit限制时，将自动进行分页获取，并合并结果返回。
        When results exceed the limit, this function will automatically paginate and return the combined results.
        
        :param order_id: Order ID to filter transactions. 订单ID过滤
        :param symbol: Symbol to filter transactions. 合约代码过滤
        :param sec_type: Security type to filter transactions. 合约类型过滤
        :param start_time: Start time in milliseconds. 开始时间（毫秒时间戳）
        :param end_time: End time in milliseconds. 结束时间（毫秒时间戳）
        :param expiry: Option expiry date (for option transactions). 期权到期日（用于期权成交记录）
        :param strike: Option strike price (for option transactions). 期权行权价（用于期权成交记录）
        :param put_call: Option right (PUT/CALL) (for option transactions). 期权类型（看跌/看涨）
        :param max_items: Maximum total items to return, 0 means return all items. 最大返回记录数，0表示返回所有记录
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
