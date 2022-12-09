# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""

ORDER_NO = "order_no"
PREVIEW_ORDER = "preview_order"
PLACE_ORDER = "place_order"
CANCEL_ORDER = "cancel_order"
MODIFY_ORDER = "modify_order"

"""
账户/资产
"""
ACCOUNTS = "accounts"
ASSETS = "assets"
PRIME_ASSETS = "prime_assets"
POSITIONS = "positions"
ORDERS = "orders"
ACTIVE_ORDERS = "active_orders"  # 待成交订单
INACTIVE_ORDERS = "inactive_orders"  # 已撤销订单
FILLED_ORDERS = "filled_orders"  # 已成交订单
ORDER_TRANSACTIONS = "order_transactions"  # 订单成交记录
ANALYTICS_ASSET = "analytics_asset"

USER_LICENSE = "user_license"

"""
合约
"""
CONTRACT = "contract"
CONTRACTS = "contracts"
QUOTE_CONTRACT = "quote_contract"

"""
行情
"""
MARKET_STATE = "market_state"
ALL_SYMBOLS = "all_symbols"
ALL_SYMBOL_NAMES = "all_symbol_names"
BRIEF = "brief"
STOCK_DETAIL = "stock_detail"
TIMELINE = "timeline"
HISTORY_TIMELINE = "history_timeline"
KLINE = "kline"
TRADE_TICK = "trade_tick"
QUOTE_REAL_TIME = "quote_real_time"
QUOTE_DELAY = "quote_delay"
QUOTE_SHORTABLE_STOCKS = "quote_shortable_stocks"
QUOTE_STOCK_TRADE = "quote_stock_trade"
QUOTE_DEPTH = "quote_depth"  # level2 深度行情
GRAB_QUOTE_PERMISSION = "grab_quote_permission"  # 抢占行情
MARKET_SCANNER = "market_scanner"  # 选股器
GET_QUOTE_PERMISSION = "get_quote_permission"
TRADING_CALENDAR = "trading_calendar"
STOCK_BROKER = "stock_broker"  # 港股股票实时经纪队列
CAPITAL_DISTRIBUTION = "capital_distribution"  # 股票当日资金分布
CAPITAL_FLOW = "capital_flow"  # 股票资金流向

# 期权行情
OPTION_EXPIRATION = "option_expiration"
OPTION_CHAIN = "option_chain"
OPTION_BRIEF = "option_brief"
OPTION_KLINE = "option_kline"
OPTION_TRADE_TICK = "option_trade_tick"

# 期货行情
FUTURE_EXCHANGE = "future_exchange"
FUTURE_CONTRACT_BY_CONTRACT_CODE = "future_contract_by_contract_code"
FUTURE_CONTRACT_BY_EXCHANGE_CODE = "future_contract_by_exchange_code"
FUTURE_CONTRACTS = "future_contracts"
FUTURE_CONTINUOUS_CONTRACTS = "future_continuous_contracts"
FUTURE_CURRENT_CONTRACT = "future_current_contract"
FUTURE_KLINE = "future_kline"
FUTURE_REAL_TIME_QUOTE = "future_real_time_quote"
FUTURE_TICK = "future_tick"
FUTURE_TRADING_DATE = "future_trading_date"

# 公司行动, 财务数据
FINANCIAL_DAILY = 'financial_daily'
FINANCIAL_REPORT = 'financial_report'
CORPORATE_ACTION = 'corporate_action'

# 行业数据
INDUSTRY_LIST = 'industry_list'
INDUSTRY_STOCKS = 'industry_stocks'
STOCK_INDUSTRY = 'stock_industry'

