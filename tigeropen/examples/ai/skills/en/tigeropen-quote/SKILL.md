---
name: tigeropen-quote
description: Tiger Brokers OpenAPI market data skill. Get real-time quotes for stocks/options/futures, K-line candlestick data, Level 2 depth quotes, trade ticks, timeline data, capital flow, fundamental data, and manage quote permissions. Use this skill when users need market quotes, historical K-lines, order book depth, or financial data.
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: en_US
---

# Tiger Open API Market Data

## Initialize Quote Client

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.quote.quote_client import QuoteClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
quote_client = QuoteClient(client_config=client_config)
# is_grab_permission defaults to True, auto-grabs quote permissions
# With multiple devices on same account, only last device to grab gets data
```

> Create QuoteClient once at module level and reuse to avoid repeated permission grabs.

## Market Status

```python
from tigeropen.common.consts import Market

status = quote_client.get_market_status(Market.US)
for s in status:
    print(f"Market: {s.market}, Status: {s.trading_status}, Open: {s.open_time}")
```

## Real-time Quotes

### Stocks

```python
briefs = quote_client.get_stock_briefs(['AAPL', 'TSLA', '00700'])
for b in briefs:
    print(f"{b.symbol}: price={b.latest_price}, change={b.change}, "
          f"change%={b.change_percent}%, volume={b.volume}")

# Include pre/after-hours
briefs = quote_client.get_stock_briefs(['AAPL'], include_hour_trading=True)
```

### Options

```python
# Symbol format: US 'AAPL  250829C00150000', HK 'TCH.HK 230616C00550000'
option_briefs = quote_client.get_option_briefs(identifiers=['AAPL  250829C00150000'])
```

### Futures

```python
future_brief = quote_client.get_future_brief(identifiers=['CL2509'])
```

## K-line (Candlestick) Data

```python
from tigeropen.common.consts import BarPeriod, QuoteRight

# Daily K-lines (returns DataFrame: symbol, time, open, high, low, close, volume)
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=60)

# Minute K-lines
bars_5m = quote_client.get_bars(['AAPL'], period=BarPeriod.FIVE_MINUTES, limit=100)

# Time range
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY,
                              begin_time='2025-01-01', end_time='2025-06-30')

# Adjustment: br (forward adjusted, default) / nr (unadjusted)
bars_nr = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, right=QuoteRight.NR)

# Paginated fetch for large datasets
bars = quote_client.get_bars_by_page(symbol='AAPL', period=BarPeriod.DAY,
                                      begin_time='2020-01-01', end_time='2025-01-01',
                                      total=2000)

# Futures K-lines
future_bars = quote_client.get_future_bars_by_page(
    identifier='CL2509', period=BarPeriod.DAY,
    begin_time='2025-01-01', end_time='2025-06-30')

# Options K-lines
option_bars = quote_client.get_option_bars(
    identifiers=['AAPL  250829C00150000'], period=BarPeriod.DAY)
```

**Bar periods**: `day/week/month/year/1min/3min/5min/10min/15min/30min/45min/60min/2hour/3hour/4hour/6hour`

## Depth Quote (Level 2)

```python
depth = quote_client.get_depth_quote(['AAPL'], market=Market.US)
depth = quote_client.get_depth_quote(['00700'], market=Market.HK)  # 10 levels
# Returns asks/bids with: price, volume, order_count

depth = quote_client.get_option_depth(identifiers=['AAPL  250829C00150000'], market='US')
```

> Requires Level 2 market data subscription.

## Trade Ticks

```python
ticks = quote_client.get_trade_ticks(symbols=['AAPL'], limit=50)
option_ticks = quote_client.get_option_trade_ticks(identifiers=['AAPL  250829C00150000'])
future_ticks = quote_client.get_future_trade_ticks(identifier='CL2509', limit=50)
```

## Timeline (Intraday)

```python
timeline = quote_client.get_timeline(['AAPL'], include_hour_trading=True)
timeline = quote_client.get_timeline_history(['AAPL'], date='2025-06-18')
```

## Capital Flow

```python
flow = quote_client.get_capital_flow(symbol='AAPL', market='US',
                                      period='day',  # intraday/day/week/month/year/quarter/6month
                                      begin_time='2025-01-01', end_time='2025-06-30')

distribution = quote_client.get_capital_distribution(symbol='AAPL', market='US')
```

## Fundamental Data

```python
# Daily financial metrics
financial = quote_client.get_financial_daily(
    symbols=['AAPL'], fields=['pe_ttm', 'pb', 'ps_ttm', 'market_value'],
    begin_date='2025-01-01', end_date='2025-06-30')

# Financial reports
report = quote_client.get_financial_report(
    symbols=['AAPL'], fields=['total_revenue', 'net_income', 'eps_diluted'],
    period_type='LTM')  # Annual/Quarterly/LTM

# Dividends
dividends = quote_client.get_corporate_dividend(
    symbols=['AAPL'], market='US',
    begin_date='2024-01-01', end_date='2025-12-31')

# Stock splits
splits = quote_client.get_corporate_split(symbols=['AAPL'], market='US',
                                           begin_date='2020-01-01', end_date='2025-12-31')

# Earnings calendar
earnings = quote_client.get_corporate_earnings_calendar(
    market='US', begin_date='2025-06-01', end_date='2025-06-30')
```

## Quote Permission Management

```python
permissions = quote_client.get_quote_permission()
for p in permissions:
    print(f"Permission: {p['name']}, Expires: {p['expire_at']}")  # -1 = no expiry

quote_client.grab_quote_permission()  # Grab permissions (multi-device)

quota = quote_client.get_kline_quota(with_details=True)
for q in quota:
    print(f"Type: {q['method']}, Used: {q['used']}, Remaining: {q['remain']}")
```

## Notes

- Quote permissions require separate purchase; API and App are independent
- Multi-device: only the last device to grab gets permissions
- K-line data has quota limits; check periodically
- Use `get_bars_by_page` for large historical datasets
- HK stock codes are 5-digit numbers, e.g. `00700` (Tencent)
