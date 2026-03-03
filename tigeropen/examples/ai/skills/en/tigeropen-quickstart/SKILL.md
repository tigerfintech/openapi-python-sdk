---
name: tigeropen-quickstart
description: Tiger Brokers OpenAPI Python SDK quickstart. Install SDK, configure authentication (tiger_id/private_key/account), create clients, connect to paper or live trading. Use this skill when users need to set up the Tiger API, initialize SDK configuration, or set up development environment.
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: en_US
---

# Tiger Open API Python SDK Quickstart

## Overview

The Tiger Open Platform Python SDK (tigeropen) provides trading and market data APIs for individual developers and institutional users. Supports stocks, options, futures, and more across US, HK, China A-shares, and Singapore markets.

- Documentation: https://docs.itigerup.com/docs/intro
- GitHub: https://github.com/tigerbrokers/openapi-python-sdk
- SDK Version: 3.5.4 | Python: 3.8 - 3.13

## Installation

```bash
pip install tigeropen

# Verify
python -c "import tigeropen; print(tigeropen.__VERSION__)"
```

## Prerequisites

1. Open a Tiger Brokers account and fund it
2. Visit https://developer.itigerup.com/ to activate API permissions
3. Obtain your `tiger_id` and RSA private key file

## Configuration

Create a config file `tiger_openapi_config.properties` with tiger_id, private_key, and account:

```properties
tiger_id=your_tiger_id
private_key_path=/path/to/private_key.pem
account=your_account
```

Load via `props_path`:

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
```

> Also supports environment variables (`TIGEROPEN_TIGER_ID` / `TIGEROPEN_PRIVATE_KEY` / `TIGEROPEN_ACCOUNT`) and direct code assignment. Priority: code params > env vars > config file > defaults.

## Create Clients

```python
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

quote_client = QuoteClient(client_config=client_config)  # Market data
trade_client = TradeClient(client_config=client_config)  # Trading
```

## Paper Trading

```python
client_config = TigerOpenClientConfig(sandbox_debug=True)
client_config.account = 'your_paper_account'
```

## Complete Quickstart Example

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.consts import Market, BarPeriod
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

# 1. Load config
client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')

# 2. Create clients
quote_client = QuoteClient(client_config=client_config)
trade_client = TradeClient(client_config=client_config)

# 3. Check market status
status = quote_client.get_market_status(Market.US)
for s in status:
    print(f"Market: {s.market}, Status: {s.trading_status}")

# 4. Get real-time quotes
briefs = quote_client.get_stock_briefs(['AAPL', 'TSLA'])
for b in briefs:
    print(f"{b.symbol}: price={b.latest_price}, change={b.change_percent}%")

# 5. Get K-line data
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=30)
print(bars.tail())

# 6. Check account
assets = trade_client.get_prime_assets(base_currency='USD')
print(f"Net Liquidation: {assets.net_liquidation}, Available: {assets.available_funds}")
```

## Core Modules

| Module | Purpose |
|--------|---------|
| `QuoteClient` | Market data (quotes, K-lines, depth, option chains, etc.) |
| `TradeClient` | Trading (orders, positions, assets, contracts, etc.) |
| `PushClient` | Real-time push (quote updates, order/position changes, etc.) |
| `TigerOpenClientConfig` | Configuration management |

## Common Enums

```python
from tigeropen.common.consts import (
    Market,        # ALL, US, HK, CN, SG
    SecurityType,  # STK, OPT, FUT, WAR, IOPT, CASH, FUND, MLEG
    Currency,      # USD, HKD, CNH, SGD
    OrderType,     # MKT, LMT, STP, STP_LMT, TRAIL, TWAP, VWAP
    BarPeriod,     # DAY, WEEK, MONTH, ONE_MINUTE, FIVE_MINUTES, ONE_HOUR...
    Language,      # zh_CN, zh_TW, en_US
)
```

## Notes

- Authentication uses RSA-2048 signatures; all requests are signed with private key
- Create `QuoteClient` once and reuse; avoid repeated permission grabs
- Quote permissions require separate purchase; API and App permissions are independent
- Institutional users need additional `secret_key` configuration
