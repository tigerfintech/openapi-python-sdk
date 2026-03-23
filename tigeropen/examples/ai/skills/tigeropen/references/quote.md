
# Tiger Open API 行情数据 / Market Data

> 中文 | English — 双语技能，代码示例通用。Bilingual skill with shared code examples.
> 官方文档 Docs: https://docs.itigerup.com/docs/quote-stock

## 初始化 / Initialize

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.quote.quote_client import QuoteClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
quote_client = QuoteClient(client_config=client_config)
# is_grab_permission 默认 True，自动抢占行情权限 / auto-grabs quote permissions
# 多设备同账号仅最后抢占的设备收到行情 / last device to grab gets data
```

> 建议模块级创建一次并复用。Create QuoteClient once and reuse.

---

## 市场状态 / Market Status

```python
from tigeropen.common.consts import Market

status = quote_client.get_market_status(Market.US)  # US, HK, CN, ALL
for s in status:
    print(f"{s.market}: status={s.trading_status}, open={s.open_time}")
# MarketStatus 属性: market, trading_status, status, open_time
# trading_status: NOT_YET_OPEN, PRE_HOUR_TRADING, TRADING, MIDDLE_CLOSE, POST_HOUR_TRADING, CLOSING, EARLY_CLOSING
```

## 交易日历 / Trading Calendar

```python
cal = quote_client.get_trading_calendar(market=Market.US, begin_date='2025-01-01', end_date='2025-12-31')
# 返回 list[dict] / Returns list of dicts
# 每项: {'date': '2025-01-02', 'type': 'TRADING'}
# type: TRADING(交易日) / NON_TRADING(非交易日)
```

---

## 股票代码与信息 / Stock Symbols & Info

```python
# 获取所有代码 / Get all symbols
symbols = quote_client.get_symbols(market=Market.US)  # 返回 symbol 列表

# 获取代码和名称 / Get symbols with names
names = quote_client.get_symbol_names(market=Market.HK, lang=Language.zh_CN)
# 返回 DataFrame: symbol, name

# 股票详情 / Stock details
details = quote_client.get_stock_details(symbols=['AAPL'])
# 属性: symbol, market, exchange, sec_type, listing_date, float_shares, eps, adr_rate, etf
```

## 股票基本面 / Stock Fundamentals

```python
# 基本面指标 / Fundamental indicators
fundamentals = quote_client.get_stock_fundamental(symbols=['AAPL', 'TSLA'])
# 属性: symbol, roe, roa, pe_ttm, pe_lyr, pb, ps_ttm, market_value, 52week_high, 52week_low,
#       volume_ratio, turnover_rate, latest_earnings_date, next_earnings_date
```

---

## 实时行情 / Real-time Quotes

### 股票 / Stocks

```python
briefs = quote_client.get_stock_briefs(['AAPL', 'TSLA', '00700'])
for b in briefs:
    print(f"{b.symbol}: price={b.latest_price}, change={b.change}, "
          f"change%={b.change_percent}%, volume={b.volume}, "
          f"open={b.open}, high={b.high}, low={b.low}, pre_close={b.pre_close}")

# 含盘前盘后 / Include pre/after-hours
briefs = quote_client.get_stock_briefs(['AAPL'], include_hour_trading=True)
# 额外属性: hour_trading_latest_price, hour_trading_pre_close, hour_trading_latest_time, hour_trading_volume, hour_trading_change_percent

# 延迟行情(无权限时) / Delayed quotes (when no permission)
delayed = quote_client.get_stock_delay_briefs(symbols=['AAPL'])
```

### 夜盘行情 / Overnight Quotes

```python
overnight = quote_client.get_quote_overnight(symbols=['AAPL', 'TSLA'])
# 返回夜盘交易时段行情 / Returns overnight trading session quotes
```

### 交易元数据 / Trading Metadata

```python
metas = quote_client.get_trade_metas(symbols=['AAPL', '00700'])
# 属性: symbol, market, sec_type, lot_size(每手股数), min_tick(最小价格变动), spread_scale
```

---

## K线数据 / K-line (Candlestick) Data

```python
from tigeropen.common.consts import BarPeriod, QuoteRight, TradingSession

# 日K / Daily (返回 DataFrame: symbol, time, open, high, low, close, volume, amount)
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=60)

# 分钟K / Minute
bars_5m = quote_client.get_bars(['AAPL'], period=BarPeriod.FIVE_MINUTES, limit=100)

# 时间范围 / Time range
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY,
                              begin_time='2025-01-01', end_time='2025-06-30')

# 复权 / Adjustment: BR(前复权/forward, default), NR(不复权/none)
bars_nr = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, right=QuoteRight.NR)

# 多股票 / Multiple symbols
bars = quote_client.get_bars(['AAPL', 'TSLA', 'GOOG'], period=BarPeriod.DAY, limit=30)

# 指定日期的分钟K线 / Minute K-lines for specific date
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.ONE_MINUTE, date='20250618')

# 指定交易时段 / Specific trading session (夜盘 overnight)
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY,
                              trade_session=TradingSession.OverNight)

# 含基本面数据(PE/换手率) / With fundamental data (PE/turnover)
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, with_fundamental=True)

# 分页(单个标的，使用 page_token) / Pagination (single symbol, via page_token)
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=100)
next_token = bars['next_page_token'].iloc[0]
if next_token:
    bars_next = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=100, page_token=next_token)
```

### 分页获取大量K线 / Paginated K-line for Large Datasets

```python
# 自动分页获取(注意: symbol 为单个字符串) / Auto-paginated fetch (note: symbol is a single string)
bars = quote_client.get_bars_by_page(symbol='AAPL', period=BarPeriod.DAY,
                                      begin_time='2020-01-01', end_time='2025-01-01',
                                      total=2000)
# 也支持 trade_session 和 with_fundamental 参数
# Also supports trade_session and with_fundamental params
```

**K线周期 / Bar Periods**: `day/week/month/year/1min/3min/5min/10min/15min/30min/45min/60min/2hour/3hour/4hour/6hour`

---

## 深度行情 / Depth Quote (Level 2)

```python
# 美股深度 / US depth (需要 L2 权限 / requires L2 permission)
depth = quote_client.get_depth_quote(['AAPL'], market=Market.US)
# 返回 asks(卖盘) 和 bids(买盘)，每档: price, volume, order_count
# US: 最多40档 / up to 40 levels

# 港股深度 / HK depth
depth = quote_client.get_depth_quote(['00700'], market=Market.HK)
# HK: 最多10档 / up to 10 levels
```

## 逐笔成交 / Trade Ticks

```python
from tigeropen.common.consts import TradingSession

ticks = quote_client.get_trade_ticks(symbols=['AAPL'], limit=50)
# 返回 DataFrame: symbol, time, price, volume, direction(+/-), index

# 指定交易时段 / Specific trading session
ticks = quote_client.get_trade_ticks(symbols=['AAPL'], limit=100,
                                      trade_session=TradingSession.Regular)

# 分页(使用 begin_index/end_index) / Pagination via begin_index/end_index
ticks = quote_client.get_trade_ticks(symbols=['AAPL'], begin_index=0, end_index=100)
```

## 分时数据 / Timeline (Intraday)

```python
# 当日分时 / Today's timeline
timeline = quote_client.get_timeline(['AAPL'], include_hour_trading=True)
# 返回 DataFrame: symbol, time, price, avg_price, pre_close, volume, trade_session

# 指定交易时段 / Specific trading session
timeline = quote_client.get_timeline(['AAPL'], trade_session=TradingSession.OverNight)

# 历史某日分时 / Historical date
timeline = quote_client.get_timeline_history(['AAPL'], date='2025-06-18')
# 也支持 trade_session 参数 / Also supports trade_session param
```

---

## 资金流向 / Capital Flow

```python
from tigeropen.common.consts import CapitalPeriod

# 资金流向 / Capital flow (使用 CapitalPeriod 枚举)
flow = quote_client.get_capital_flow(symbol='AAPL', market='US',
                                      period=CapitalPeriod.DAY,
                                      begin_time='2025-01-01', end_time='2025-06-30')
# 返回 DataFrame: time, timestamp, net_inflow, symbol, period
# CapitalPeriod 可选值: INTRADAY, DAY, WEEK, MONTH, YEAR, QUARTER, HALFAYEAR

# 资金分布 / Capital distribution
distribution = quote_client.get_capital_distribution(symbol='AAPL', market='US')
# 属性: net_inflow, super_large_net_inflow, large/middle/small_net_inflow
```

## 港股经纪商 / HK Broker Data

```python
# 经纪商席位 / Broker seats (返回 StockBroker 对象)
broker = quote_client.get_stock_broker('00700', limit=40)
# broker.bid_broker: 买方经纪商列表(LevelBroker: level, price, broker_count, broker)
# broker.ask_broker: 卖方经纪商列表

# 经纪商持仓(CCASS) / Broker holdings (CCASS) - 独立方法
hold = quote_client.get_broker_hold(symbol='00700', limit=40)
```

## 热门交易排行 / Hot Trading Rank

```python
rank = quote_client.get_trade_rank(market='US')
# 返回热门交易标的排行
```

---

## 基本面数据 / Fundamental Data

### 每日财务指标 / Daily Financial Metrics

```python
financial = quote_client.get_financial_daily(
    symbols=['AAPL'],
    fields=['pe_ttm', 'pb', 'ps_ttm', 'market_value', 'shares_outstanding', 'market_capitalization'],
    begin_date='2025-01-01', end_date='2025-06-30')
# 返回 DataFrame: symbol, date, 及所选字段
# 可选字段: market_value, pe_ttm, pb, ps_ttm, pcf_ttm, market_capitalization,
#          shares_outstanding, total_share, eps_ttm, dividend_ttm, dividend_rate_ttm
```

### 财务报告 / Financial Reports

```python
report = quote_client.get_financial_report(
    symbols=['AAPL'],
    fields=['total_revenue', 'net_income', 'eps_diluted', 'gross_profit'],
    period_type='LTM')  # Annual/Quarterly/LTM/CumulativeQuarterly
# 可选字段类别:
# Income: total_revenue, cost_of_revenue, gross_profit, operating_income, net_income, eps_diluted, ebitda...
# Balance: total_assets, total_liabilities, total_equity, cash_and_equivalents, total_debt...
# CashFlow: operating_cash_flow, capital_expenditure, free_cash_flow, dividends_paid...
```

### 分红 / Dividends

```python
dividends = quote_client.get_corporate_dividend(
    symbols=['AAPL'], market='US',
    begin_date='2024-01-01', end_date='2025-12-31')
# 属性: symbol, announce_date, record_date, pay_date, amount, currency
```

### 拆合股 / Stock Splits

```python
splits = quote_client.get_corporate_split(
    symbols=['AAPL'], market='US',
    begin_date='2020-01-01', end_date='2025-12-31')
# 属性: symbol, execute_date, from_factor, to_factor
```

### 财报日历 / Earnings Calendar

```python
earnings = quote_client.get_corporate_earnings_calendar(
    market='US', begin_date='2025-06-01', end_date='2025-06-30')
# 属性: symbol, name, market, earnings_date, timing(BMO/AMC)
```

---

## 期权行情 / Option Quotes

> 详细的期权交易功能见 tigeropen-option 技能 / See tigeropen-option skill for trading

```python
# 到期日 / Expirations (返回 DataFrame: symbol, option_symbol, date, timestamp, period_tag)
expirations = quote_client.get_option_expirations(symbols=['AAPL'], market='US')
# period_tag: "m"=月度期权(monthly), "w"=周期权(weekly)

# 期权链 / Option chain
from tigeropen.quote.domain.filter import OptionFilter
chain = quote_client.get_option_chain(symbol='AAPL', expiry='2025-08-29', market='US')
# 带筛选 / With filters
option_filter = OptionFilter(implied_volatility_min=0.3, delta_min=0.2, open_interest_min=100, in_the_money=True)
chain = quote_client.get_option_chain(symbol='AAPL', expiry='2025-08-29',
                                       option_filter=option_filter, return_greek_value=True, market='US')

# 实时行情 / Real-time quotes
briefs = quote_client.get_option_briefs(identifiers=['AAPL  250829C00150000'])

# K线 / K-lines (支持: day, 1min, 5min, 30min, 60min; 可选 sort_dir)
bars = quote_client.get_option_bars(identifiers=['AAPL  250829C00150000'], period='day')

# 深度 / Depth
depth = quote_client.get_option_depth(identifiers=['AAPL  250829C00150000'], market='US')

# 逐笔 / Ticks
ticks = quote_client.get_option_trade_ticks(identifiers=['AAPL  250829C00150000'])

# 分时 / Timeline
timeline = quote_client.get_option_timeline(identifiers=['AAPL  250829C00150000'])

# 港股期权代码映射 / HK option symbol mapping
hk_symbols = quote_client.get_option_symbols(market='HK')  # e.g. 00700 -> TCH.HK
```

### 期权分析 / Option Analysis

```python
from tigeropen.common.consts import OptionAnalysisPeriod

analysis = quote_client.get_option_analysis(symbols=['AAPL'],
                                             period=OptionAnalysisPeriod.FIFTY_TWO_WEEK)
# 返回 List[OptionAnalysis]
# 属性: symbol, implied_vol_30_days, his_volatility, iv_his_v_ratio, call_put_ratio
# iv_metric: IVMetric(period, percentile, rank)
```

**期权代码格式 / Option Symbol Format**:
- 美股 US: `'AAPL  250829C00150000'` (标的 + YYMMDD + C/P + 行权价*1000)
- 港股 HK: `'TCH.HK 230616C00550000'`

---

## 期货行情 / Futures Quotes

```python
# 期货交易所 / Exchanges
exchanges = quote_client.get_future_exchanges()
# CME, NYMEX, COMEX, CBOT, CBOE, HKFE, SGX, OSE

# 交易所合约 / Exchange contracts
contracts = quote_client.get_future_contracts(exchange='CME')

# 指定合约 / Specific contract
contract = quote_client.get_future_contract(symbol='CL2509')

# 主力合约 / Current/main contract
current = quote_client.get_current_future_contract(contract_type='CL')

# 连续合约 / Continuous contracts
continuous = quote_client.get_future_continuous_contracts(contract_type='CL')

# 所有合约(某品种) / All contracts for a type
all_contracts = quote_client.get_all_future_contracts(contract_type='CL')

# 交易时间 / Trading times
times = quote_client.get_future_trading_times(symbol='CL2509')

# 实时行情 / Real-time quotes
brief = quote_client.get_future_brief(identifiers=['CL2509'])

# 深度行情 / Depth
depth = quote_client.get_future_depth(identifiers=['CL2509'])

# 逐笔 / Ticks
ticks = quote_client.get_future_trade_ticks(identifier='CL2509', limit=50)

# K线 / K-lines
bars = quote_client.get_future_bars(identifier='CL2509', period=BarPeriod.DAY, limit=60)

# 分页K线 / Paginated K-lines
bars = quote_client.get_future_bars_by_page(identifier='CL2509', period=BarPeriod.DAY,
                                             begin_time='2025-01-01', end_time='2025-06-30')
```

---

## 基金行情 / Fund Quotes

```python
# 基金代码 / Fund symbols
symbols = quote_client.get_fund_symbols()

# 基金合约 / Fund contracts
contracts = quote_client.get_fund_contracts(symbols=['ARKK'])

# 最新行情 / Latest quote
quote = quote_client.get_fund_quote(symbols=['ARKK'])

# 历史行情 / Historical quotes
history = quote_client.get_fund_history_quote(symbols=['ARKK'],
                                               begin_date='2025-01-01', end_date='2025-06-30')
```

---

## 数字货币行情 / Cryptocurrency Quotes

```python
from tigeropen.common.consts import SecurityType

# 代码列表 / Symbols
symbols = quote_client.get_symbols(market=Market.US, sec_type=SecurityType.CC)

# 实时行情 / Real-time quotes
briefs = quote_client.get_cc_briefs(symbols=['BTC/USD', 'ETH/USD'])

# K线 / K-lines
bars = quote_client.get_bars(['BTC/USD'], period=BarPeriod.DAY, limit=30, sec_type=SecurityType.CC)

# 分时 / Timeline
timeline = quote_client.get_timeline(['BTC/USD'], sec_type=SecurityType.CC)
```

---

## 窝轮/牛熊证行情 / Warrant & CBBC Quotes

```python
# 窝轮筛选器 / Warrant scanner
warrants = quote_client.get_warrant_filter(
    symbol='00700', filter_type='warrant',  # warrant/cbbc/inline
    sort_field='changeRate', sort_dir='DESC')

# 窝轮行情 / Warrant quotes
briefs = quote_client.get_warrant_briefs(symbols=['12345'])
```

---

## 选股器 / Market Scanner

```python
from tigeropen.common.consts import Market, StockField, AccumulateField, FinancialField, MultiTagField, SortDirection

# 基础选股 / Basic scanning
result = quote_client.market_scanner(
    market=Market.US,
    sort_field_name='changeRate',
    sort_dir=SortDirection.DESC,
    filter_fields=[
        {'fieldName': StockField.FloatMarketValue, 'filterMin': 1e9, 'filterMax': 1e12},  # 流通市值 1B-1T
        {'fieldName': StockField.ChangeRate, 'filterMin': 5, 'filterMax': 30},  # 涨跌幅 5%-30%
        {'fieldName': StockField.Volume, 'filterMin': 1000000},  # 成交量 > 1M
    ],
    limit=20
)

# 带财务指标 / With financial fields
result = quote_client.market_scanner(
    market=Market.US,
    sort_field_name='pe_ttm',
    sort_dir=SortDirection.ASC,
    filter_fields=[
        {'fieldName': FinancialField.PE_TTM, 'filterMin': 0, 'filterMax': 20},
        {'fieldName': StockField.FloatMarketValue, 'filterMin': 1e10},
    ],
    limit=50
)

# 多标签筛选 / Multi-tag filter (ETF, has options, industry)
result = quote_client.market_scanner(
    market=Market.US,
    filter_fields=[
        {'fieldName': MultiTagField.HasOption, 'filterValues': ['true']},
        {'fieldName': MultiTagField.IsETF, 'filterValues': ['false']},
    ]
)

# 获取筛选标签值 / Get scanner tag values
tags = quote_client.get_market_scanner_tags(market=Market.US, field_name=MultiTagField.IndustryCode)
```

### StockField 选股字段

| 字段 Field | 说明 Description |
|-----------|-----------------|
| `Change` | 涨跌额 Price change |
| `ChangeRate` | 涨跌幅% Change rate |
| `LatestPrice` | 最新价 Latest price |
| `Volume` | 成交量 Volume |
| `Amount` | 成交额 Turnover |
| `TurnoverRate` | 换手率 Turnover rate |
| `FloatShare` | 流通股本 Float shares |
| `FloatMarketValue` | 流通市值 Float market cap |
| `MarketValue` | 总市值 Total market cap |

---

## 行情权限管理 / Quote Permission Management

```python
# 查询权限 / Query permissions
permissions = quote_client.get_quote_permission()
for p in permissions:
    print(f"{p['name']}: expires={p['expire_at']}")  # -1 = 永不过期 never expires

# 抢占权限 / Grab permissions (多设备切换时 / multi-device)
quote_client.grab_quote_permission()

# K线配额 / K-line quota
quota = quote_client.get_kline_quota(with_details=True)
for q in quota:
    print(f"{q['method']}: used={q['used']}, remain={q['remain']}")
```

**权限类型**: `usQuoteBasic`, `usStockQuoteLv2Totalview`, `hkStockQuoteLv2`, `usOptionQuote`, `hkFutureQuoteLv2`, `CBOEFuturesQuoteLv2`

---

## 注意事项 / Notes

- 行情权限需单独购买，API 与 App 独立 / Quote permissions require separate purchase
- 多设备同账号：最后抢占的设备获取权限 / Last device to grab gets permissions
- K线有配额限制，大量数据用 `get_bars_by_page` / Use paginated fetch for large datasets
- 港股代码5位数 `00700`(腾讯) / HK codes are 5-digit like `00700`
- 深度行情需 L2 权限 / Depth quotes require Level 2 permission
- 更多详情见 / More details: https://docs.itigerup.com/docs/quote-stock
