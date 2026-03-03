---
name: tigeropen-quote
description: 老虎证券 OpenAPI 行情数据技能。获取股票/期权/期货实时行情、K线数据、深度盘口、逐笔成交、分时数据、资金流向、基本面数据、行情权限管理。当用户需要查询市场行情、获取历史K线、查看盘口深度、获取财务数据时使用此技能。
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: zh_CN
---

# Tiger Open API 行情数据

## 初始化行情客户端

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.quote.quote_client import QuoteClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
quote_client = QuoteClient(client_config=client_config)
# is_grab_permission 默认 True，自动抢占行情权限
# 多设备同账号时，仅最后抢占的设备能收到行情
```

> 建议在模块级别创建 QuoteClient 一次并复用，避免重复抢占触发频率限制。

## 市场状态

```python
from tigeropen.common.consts import Market

status = quote_client.get_market_status(Market.US)
for s in status:
    print(f"市场: {s.market}, 状态: {s.trading_status}, 开盘: {s.open_time}")
```

## 实时行情

### 股票行情

```python
briefs = quote_client.get_stock_briefs(['AAPL', 'TSLA', '00700'])
for b in briefs:
    print(f"{b.symbol}: 最新价={b.latest_price}, 涨跌={b.change}, "
          f"涨跌幅={b.change_percent}%, 成交量={b.volume}")

# 含盘前盘后
briefs = quote_client.get_stock_briefs(['AAPL'], include_hour_trading=True)
```

### 期权行情

```python
# 期权代码格式: 美股 'AAPL  250829C00150000', 港股 'TCH.HK 230616C00550000'
option_briefs = quote_client.get_option_briefs(identifiers=['AAPL  250829C00150000'])
```

### 期货行情

```python
future_brief = quote_client.get_future_brief(identifiers=['CL2509'])
```

## K线数据

```python
from tigeropen.common.consts import BarPeriod, QuoteRight

# 日K（返回 DataFrame: symbol, time, open, high, low, close, volume）
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=60)

# 分钟K
bars_5m = quote_client.get_bars(['AAPL'], period=BarPeriod.FIVE_MINUTES, limit=100)

# 指定时间范围
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY,
                              begin_time='2025-01-01', end_time='2025-06-30')

# 复权: br(前复权,默认) / nr(不复权)
bars_nr = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, right=QuoteRight.NR)

# 大量数据分页获取
bars = quote_client.get_bars_by_page(symbol='AAPL', period=BarPeriod.DAY,
                                      begin_time='2020-01-01', end_time='2025-01-01',
                                      total=2000)

# 期货K线
future_bars = quote_client.get_future_bars_by_page(
    identifier='CL2509', period=BarPeriod.DAY,
    begin_time='2025-01-01', end_time='2025-06-30')

# 期权K线
option_bars = quote_client.get_option_bars(
    identifiers=['AAPL  250829C00150000'], period=BarPeriod.DAY)
```

**K线周期**: `day/week/month/year/1min/3min/5min/10min/15min/30min/45min/60min/2hour/3hour/4hour/6hour`

## 深度行情 (Level 2)

```python
# 美股深度行情
depth = quote_client.get_depth_quote(['AAPL'], market=Market.US)

# 港股深度行情 (十档)
depth = quote_client.get_depth_quote(['00700'], market=Market.HK)
# 返回 asks(卖盘) 和 bids(买盘)，每档: price, volume, order_count

# 期权深度行情
depth = quote_client.get_option_depth(identifiers=['AAPL  250829C00150000'], market='US')
```

> 深度行情需要 Level 2 行情权限

## 逐笔成交

```python
ticks = quote_client.get_trade_ticks(symbols=['AAPL'], limit=50)

# 期权逐笔
option_ticks = quote_client.get_option_trade_ticks(identifiers=['AAPL  250829C00150000'])

# 期货逐笔
future_ticks = quote_client.get_future_trade_ticks(identifier='CL2509', limit=50)
```

## 分时数据

```python
# 当日分时
timeline = quote_client.get_timeline(['AAPL'], include_hour_trading=True)

# 历史某日分时
timeline = quote_client.get_timeline_history(['AAPL'], date='2025-06-18')
```

## 期权链

详见 [期权技能](../tigeropen-option/SKILL.md)。

## 资金流向

```python
# 资金流向
flow = quote_client.get_capital_flow(symbol='AAPL', market='US',
                                      period='day',  # intraday/day/week/month/year/quarter/6month
                                      begin_time='2025-01-01', end_time='2025-06-30')

# 资金分布
distribution = quote_client.get_capital_distribution(symbol='AAPL', market='US')
```

## 基本面数据

```python
# 每日财务指标
financial = quote_client.get_financial_daily(
    symbols=['AAPL'], fields=['pe_ttm', 'pb', 'ps_ttm', 'market_value'],
    begin_date='2025-01-01', end_date='2025-06-30')

# 财务报告
report = quote_client.get_financial_report(
    symbols=['AAPL'], fields=['total_revenue', 'net_income', 'eps_diluted'],
    period_type='LTM')  # Annual/Quarterly/LTM

# 分红
dividends = quote_client.get_corporate_dividend(
    symbols=['AAPL'], market='US',
    begin_date='2024-01-01', end_date='2025-12-31')

# 拆合股
splits = quote_client.get_corporate_split(symbols=['AAPL'], market='US',
                                           begin_date='2020-01-01', end_date='2025-12-31')

# 财报日历
earnings = quote_client.get_corporate_earnings_calendar(
    market='US', begin_date='2025-06-01', end_date='2025-06-30')
```

## 行情权限管理

```python
# 查询行情权限
permissions = quote_client.get_quote_permission()
for p in permissions:
    print(f"权限: {p['name']}, 到期: {p['expire_at']}")  # -1 表示永不过期

# 抢占行情权限
quote_client.grab_quote_permission()

# K线配额查询
quota = quote_client.get_kline_quota(with_details=True)
for q in quota:
    print(f"类型: {q['method']}, 已用: {q['used']}, 剩余: {q['remain']}")
```

**权限类型**: usQuoteBasic, usStockQuoteLv2Totalview, hkStockQuoteLv2, usOptionQuote, CBOEFuturesQuoteLv2 等

## 港股经纪商数据

```python
broker_data = quote_client.get_stock_broker('00700', limit=40)
```

## 注意事项

- 行情权限需单独购买，API 与 App 独立
- 多设备同账号时权限被最后抢占的设备获取
- K线数据有配额限制，建议定期检查
- 大量历史数据推荐用 `get_bars_by_page` 自动分页
- 港股代码为5位数字如 `00700`(腾讯)
