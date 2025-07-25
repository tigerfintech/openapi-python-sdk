from mcp.server.fastmcp import FastMCP
from tigeropen.tiger_open_config import get_client_config, TigerOpenClientConfig
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.consts import Market, SecurityType, Currency, BarPeriod, SegmentType
from typing import List, Optional, Dict, Any, Union
import pandas as pd

# --- TigerOpen API Configuration ---
client_config = TigerOpenClientConfig(props_path='../../../../openapi_test/prod_20150899/')
quote_client = QuoteClient(client_config)
trade_client = TradeClient(client_config)

# Create an MCP server
mcp = FastMCP("TigerOpenSDK")

# 工具函数：用于序列化各种对象和处理 DataFrame
def serialize_object(obj):
    """通用对象序列化函数"""
    if obj is None:
        return None
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

def serialize_list(items):
    """序列化对象列表"""
    if items is None:
        return []
    return [serialize_object(item) for item in items]

def dataframe_to_dict_list(df):
    """将 pandas DataFrame 转换为字典列表"""
    if df is None:
        return []
    if isinstance(df, pd.DataFrame):
        if df.empty:
            return []
        return df.to_dict(orient='records')
    return df

def serialize_position(pos):
    """序列化仓位对象，特别处理嵌套的合约对象"""
    if not pos: 
        return None
    pos_dict = pos.__dict__.copy()
    if hasattr(pos, 'contract') and pos.contract:
        pos_dict['contract'] = pos.contract.__dict__
    return pos_dict

def handle_api_response(func, *args, **kwargs):
    """通用API调用处理函数"""
    try:
        result = func(*args, **kwargs)
        if isinstance(result, pd.DataFrame):
            return dataframe_to_dict_list(result)
        elif isinstance(result, list):
            return serialize_list(result)
        elif hasattr(result, '__dict__'):
            return serialize_object(result)
        return result
    except Exception as e:
        return {"error": str(e)}

#################################################
# 服务器状态与核心功能
#################################################
@mcp.resource("server://status")
def hello() -> Dict[str, str]:
    """检查服务器状态"""
    return {"message": "TigerOpen MCP Server is running!"}

@mcp.tool()
def get_quote_permissions() -> Any:
    """获取行情权限列表"""
    return handle_api_response(quote_client.get_quote_permission)

#################################################
# 行情接口 - 市场和符号
#################################################
@mcp.tool()
def get_market_status(market: str = Market.US.value) -> Any:
    """获取指定市场的状态"""
    try:
        status = quote_client.get_market_status(Market(market))
        return [s.__dict__ for s in status] if status else []
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_symbols(market: str = Market.US.value, include_otc: bool = False) -> Any:
    """获取市场的所有交易符号列表"""
    try:
        symbols = quote_client.get_symbols(Market(market), include_otc=include_otc)
        return symbols
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_symbol_names(market: str = Market.US.value, include_otc: bool = False) -> Any:
    """获取市场的所有交易符号及其名称"""
    return handle_api_response(quote_client.get_symbol_names, Market(market), include_otc=include_otc)

@mcp.tool()
def get_trading_calendar(market: str = Market.US.value, begin_date: Optional[str] = None, end_date: Optional[str] = None) -> Any:
    """获取交易日历"""
    return handle_api_response(quote_client.get_trading_calendar, Market(market), begin_date, end_date)

#################################################
# 行情接口 - 股票行情
#################################################
@mcp.tool()
def get_briefs(symbols: List[str], include_hour_trading: bool = False, include_ask_bid: bool = False) -> Any:
    """获取股票摘要信息"""
    if not symbols:
        return {"error": "symbols parameter is required"}
    try:
        briefs_df = quote_client.get_briefs(symbols, include_hour_trading=include_hour_trading, include_ask_bid=include_ask_bid)
        return briefs_df.to_dict(orient='records') if briefs_df is not None else []
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_stock_briefs(symbols: List[str], include_hour_trading: bool = False) -> Any:
    """获取股票实时行情"""
    return handle_api_response(quote_client.get_stock_briefs, symbols, include_hour_trading=include_hour_trading)

@mcp.tool()
def get_stock_details(symbols: List[str]) -> Any:
    """获取股票详情信息"""
    return handle_api_response(quote_client.get_stock_details, symbols)

@mcp.tool()
def get_bars(symbol: Union[str, List[str]], period: str = BarPeriod.DAY.value, 
             begin_time: int = -1, end_time: int = -1, limit: int = 251) -> Any:
    """获取K线数据"""
    return handle_api_response(quote_client.get_bars, symbol, BarPeriod(period), 
                              begin_time=begin_time, end_time=end_time, limit=limit)

@mcp.tool()
def get_timeline(symbols: List[str], include_hour_trading: bool = False, begin_time: int = -1) -> Any:
    """获取分时数据"""
    return handle_api_response(quote_client.get_timeline, symbols, include_hour_trading=include_hour_trading, begin_time=begin_time)

@mcp.tool()
def get_trade_ticks(symbols: List[str], limit: Optional[int] = None) -> Any:
    """获取逐笔成交数据"""
    return handle_api_response(quote_client.get_trade_ticks, symbols, limit=limit)

@mcp.tool()
def get_depth_quote(symbols: List[str], market: str = Market.US.value) -> Any:
    """获取深度行情"""
    return handle_api_response(quote_client.get_depth_quote, symbols, Market(market))

@mcp.tool()
def get_short_interest(symbols: List[str]) -> Any:
    """获取美股做空数据"""
    return handle_api_response(quote_client.get_short_interest, symbols)

#################################################
# 行情接口 - 期权相关
#################################################
@mcp.tool()
def get_option_expirations(symbols: List[str], market: Optional[str] = None) -> Any:
    """获取期权到期日列表"""
    market_param = Market(market) if market else None
    return handle_api_response(quote_client.get_option_expirations, symbols, market=market_param)

@mcp.tool()
def get_option_chain(symbol: str, expiry: str, market: Optional[str] = None) -> Any:
    """获取期权链"""
    market_param = Market(market) if market else None
    return handle_api_response(quote_client.get_option_chain, symbol, expiry, market=market_param)

@mcp.tool()
def get_option_briefs(identifiers: List[str], market: Optional[str] = None) -> Any:
    """获取期权最新行情"""
    market_param = Market(market) if market else None
    return handle_api_response(quote_client.get_option_briefs, identifiers, market=market_param)

@mcp.tool()
def get_option_bars(identifiers: List[str], period: str = BarPeriod.DAY.value, 
                   begin_time: int = -1, end_time: int = -1, limit: Optional[int] = None) -> Any:
    """获取期权K线数据"""
    return handle_api_response(quote_client.get_option_bars, identifiers, 
                              begin_time=begin_time, end_time=end_time, 
                              period=BarPeriod(period), limit=limit)

#################################################
# 行情接口 - 期货相关
#################################################
@mcp.tool()
def get_future_exchanges(sec_type: str = SecurityType.FUT.value) -> Any:
    """获取期货交易所列表"""
    return handle_api_response(quote_client.get_future_exchanges, SecurityType(sec_type))

@mcp.tool()
def get_future_contracts(exchange: str) -> Any:
    """获取交易所下的可交易合约"""
    return handle_api_response(quote_client.get_future_contracts, exchange)

@mcp.tool()
def get_future_contract(contract_code: str) -> Any:
    """通过合约代码获取期货合约"""
    return handle_api_response(quote_client.get_future_contract, contract_code)

@mcp.tool()
def get_future_continuous_contracts(future_type: Optional[str] = None) -> Any:
    """获取期货连续合约"""
    return handle_api_response(quote_client.get_future_continuous_contracts, future_type)

@mcp.tool()
def get_future_bars(identifiers: List[str], period: str = BarPeriod.DAY.value, 
                   begin_time: int = -1, end_time: int = -1, limit: int = 1000) -> Any:
    """获取期货K线数据"""
    return handle_api_response(quote_client.get_future_bars, identifiers, 
                              BarPeriod(period), begin_time, end_time, limit)

@mcp.tool()
def get_future_brief(identifiers: List[str]) -> Any:
    """获取期货最新行情"""
    return handle_api_response(quote_client.get_future_brief, identifiers)

#################################################
# 行情接口 - 财务数据
#################################################
@mcp.tool()
def get_corporate_dividend(symbols: List[str], market: str, begin_date: str, end_date: str) -> Any:
    """获取公司派息数据"""
    return handle_api_response(quote_client.get_corporate_dividend, symbols, Market(market), begin_date, end_date)

@mcp.tool()
def get_corporate_split(symbols: List[str], market: str, begin_date: str, end_date: str) -> Any:
    """获取公司拆合股数据"""
    return handle_api_response(quote_client.get_corporate_split, symbols, Market(market), begin_date, end_date)

@mcp.tool()
def get_financial_daily(symbols: List[str], market: str, fields: List[str], begin_date: str, end_date: str) -> Any:
    """获取日级的财务数据"""
    return handle_api_response(quote_client.get_financial_daily, symbols, Market(market), fields, begin_date, end_date)

@mcp.tool()
def get_industry_list(industry_level: str = "GGROUP") -> Any:
    """获取行业列表"""
    return handle_api_response(quote_client.get_industry_list, industry_level)

@mcp.tool()
def get_industry_stocks(industry: str, market: str = Market.US.value) -> Any:
    """获取某行业下的股票列表"""
    return handle_api_response(quote_client.get_industry_stocks, industry, Market(market))

@mcp.tool()
def get_stock_industry(symbol: str, market: str = Market.US.value) -> Any:
    """获取股票的行业"""
    return handle_api_response(quote_client.get_stock_industry, symbol, Market(market))

#################################################
# 交易接口 - 账户信息
#################################################
@mcp.tool()
def get_managed_accounts() -> Any:
    """获取管理的账号列表"""
    try:
        accounts = trade_client.get_managed_accounts()
        return [acc.__dict__ for acc in accounts] if accounts else []
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_assets(account: Optional[str] = None, segment: bool = False, market_value: bool = False) -> Any:
    """获取账户资产信息"""
    try:
        active_account = account if account else client_config.account
        assets = trade_client.get_assets(account=active_account, segment=segment, market_value=market_value)
        if assets:
            asset_summary = assets.summary.__dict__ if hasattr(assets, 'summary') and assets.summary else None
            segments = {k: v.__dict__ for k, v in assets.segments.items()} if hasattr(assets, 'segments') and assets.segments else None
            return {'summary': asset_summary, 'segments': segments}
        return None
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_positions(account: Optional[str] = None, sec_type: str = SecurityType.STK.value, 
                  currency: str = Currency.ALL.value, market: str = Market.ALL.value, 
                  symbol: Optional[str] = None) -> Any:
    """获取账户持仓情况"""
    try:
        active_account = account if account else client_config.account
        positions = trade_client.get_positions(account=active_account,
                                               sec_type=SecurityType(sec_type),
                                               currency=Currency(currency),
                                               market=Market(market),
                                               symbol=symbol)
        return [serialize_position(pos) for pos in positions] if positions else []
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_prime_assets(account: Optional[str] = None, base_currency: Optional[str] = None, consolidated: bool = True) -> Any:
    """获取Prime账户资产信息"""
    base_currency_param = Currency(base_currency) if base_currency else None
    return handle_api_response(trade_client.get_prime_assets, account, base_currency_param, consolidated)

@mcp.tool()
def get_aggregate_assets(account: Optional[str] = None, seg_type: str = SegmentType.SEC.value, base_currency: Optional[str] = None) -> Any:
    """获取账户聚合资产信息"""
    base_currency_param = Currency(base_currency) if base_currency else None
    return handle_api_response(trade_client.get_aggregate_assets, account, SegmentType(seg_type), base_currency_param)

@mcp.tool()
def get_analytics_asset(account: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Any:
    """获取历史资产分析"""
    return handle_api_response(trade_client.get_analytics_asset, account, start_date, end_date)

#################################################
# 交易接口 - 订单管理
#################################################
@mcp.tool()
def get_contracts(symbol: Union[str, List[str]], sec_type: str = SecurityType.STK.value, 
                 currency: Optional[str] = None, exchange: Optional[str] = None) -> Any:
    """获取合约信息"""
    currency_param = Currency(currency) if currency else None
    return handle_api_response(trade_client.get_contracts, symbol, SecurityType(sec_type), currency_param, exchange)

@mcp.tool()
def get_contract(symbol: str, sec_type: str = SecurityType.STK.value, 
                currency: Optional[str] = None, exchange: Optional[str] = None,
                expiry: Optional[str] = None, strike: Optional[float] = None, 
                put_call: Optional[str] = None) -> Any:
    """获取单个合约详情"""
    currency_param = Currency(currency) if currency else None
    return handle_api_response(trade_client.get_contract, symbol, SecurityType(sec_type), 
                              currency_param, exchange, expiry, strike, put_call)

@mcp.tool()
def place_order(symbol: str, action: str, order_type: str, quantity: int, 
                account: Optional[str] = None, 
                sec_type: str = SecurityType.STK.value, 
                currency: str = Currency.USD.value, 
                limit_price: Optional[float] = None,
                time_in_force: Optional[str] = None,
                outside_rth: Optional[bool] = None) -> Any:
    """下单"""
    if not all([symbol, action, order_type, quantity]):
        return {"error": 'Missing required fields: symbol, action, order_type, quantity'}

    try:
        active_account = account if account else client_config.account
        contract = trade_client.get_contract(symbol, sec_type=SecurityType(sec_type), currency=Currency(currency))
        if not contract:
            return {"error": f'Contract not found for {symbol}'}

        order = trade_client.create_order(
            active_account, contract, action, order_type, quantity, 
            limit_price=limit_price, 
            time_in_force=time_in_force,
            outside_rth=outside_rth
        )
        trade_client.place_order(order)
        
        # 序列化订单对象
        order_details = order.__dict__.copy()
        if hasattr(order, 'status') and order.status:
             order_details['status'] = order.status.value 
        if hasattr(order, 'contract') and order.contract:
            order_details['contract'] = order.contract.__dict__
        return order_details

    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def preview_order(symbol: str, action: str, order_type: str, quantity: int,
                  account: Optional[str] = None,
                  sec_type: str = SecurityType.STK.value,
                  currency: str = Currency.USD.value,
                  limit_price: Optional[float] = None) -> Any:
    """预览订单（不实际下单，用于查看订单佣金和保证金信息）"""
    try:
        active_account = account if account else client_config.account
        contract = trade_client.get_contract(symbol, sec_type=SecurityType(sec_type), currency=Currency(currency))
        if not contract:
            return {"error": f'Contract not found for {symbol}'}
        
        order = trade_client.create_order(
            active_account, contract, action, order_type, quantity, 
            limit_price=limit_price
        )
        preview = trade_client.preview_order(order)
        return preview
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def cancel_order(id: Optional[str] = None, order_id: Optional[str] = None, account: Optional[str] = None) -> Any:
    """取消订单"""
    return handle_api_response(trade_client.cancel_order, account, id, order_id)

@mcp.tool()
def get_orders(account: Optional[str] = None, symbol: Optional[str] = None, 
               sec_type: Optional[str] = None, market: str = Market.ALL.value, 
               start_time: Optional[str] = None, end_time: Optional[str] = None,
               limit: int = 100, is_brief: bool = False) -> Any:
    """获取所有订单列表"""
    sec_type_param = SecurityType(sec_type) if sec_type else None
    return handle_api_response(trade_client.get_orders, account, sec_type_param, Market(market),
                              symbol, start_time, end_time, limit, is_brief)

@mcp.tool()
def get_open_orders(account: Optional[str] = None, symbol: Optional[str] = None, 
                   sec_type: Optional[str] = None, market: str = Market.ALL.value) -> Any:
    """获取未成交订单列表"""
    sec_type_param = SecurityType(sec_type) if sec_type else None
    return handle_api_response(trade_client.get_open_orders, account, sec_type_param, Market(market), symbol)

@mcp.tool()
def get_filled_orders(account: Optional[str] = None, symbol: Optional[str] = None, 
                     sec_type: Optional[str] = None, market: str = Market.ALL.value,
                     start_time: Optional[str] = None, end_time: Optional[str] = None) -> Any:
    """获取已成交订单列表"""
    sec_type_param = SecurityType(sec_type) if sec_type else None
    return handle_api_response(trade_client.get_filled_orders, account, sec_type_param, Market(market),
                              symbol, start_time, end_time)

@mcp.tool()
def get_order(id: Optional[str] = None, order_id: Optional[str] = None, account: Optional[str] = None) -> Any:
    """获取单个订单详情"""
    return handle_api_response(trade_client.get_order, account, id, order_id)

#################################################
# 交易接口 - 资金管理
#################################################
@mcp.tool()
def get_segment_fund_available(from_segment: Optional[str] = None, currency: Optional[str] = None) -> Any:
    """获取可用的分段资金"""
    from_segment_param = SegmentType(from_segment) if from_segment else None
    currency_param = Currency(currency) if currency else None
    return handle_api_response(trade_client.get_segment_fund_available, from_segment_param, currency_param)

@mcp.tool()
def get_segment_fund_history(limit: Optional[int] = None) -> Any:
    """获取分段资金历史"""
    return handle_api_response(trade_client.get_segment_fund_history, limit)

@mcp.tool()
def transfer_segment_fund(from_segment: str, to_segment: str, amount: float, currency: str) -> Any:
    """转移分段资金"""
    return handle_api_response(trade_client.transfer_segment_fund, 
                              SegmentType(from_segment), SegmentType(to_segment), 
                              amount, Currency(currency))

@mcp.tool()
def get_funding_history(seg_type: Optional[str] = None) -> Any:
    """获取资金历史"""
    seg_type_param = SegmentType(seg_type) if seg_type else None
    return handle_api_response(trade_client.get_funding_history, seg_type_param)

# To run this MCP server:
# 1. Make sure you have mcp installed: pip install "mcp[cli]"
# 2. Configure your TigerOpen API credentials in this file (client_config variable).
# 3. Run from your terminal in this directory: mcp dev server.py
#
# if __name__ == '__main__':
#     # This part is typically handled by `mcp dev` or `mcp run`
#     # For direct execution if needed, though `mcp` CLI is preferred:
#     # from mcp.server.runner import run_server
#     # run_server(mcp, host="127.0.0.1", port=5000)
#     print("To run this MCP server, use the command: mcp dev server.py")
#     print("Ensure your TigerOpen API credentials are configured in server.py")