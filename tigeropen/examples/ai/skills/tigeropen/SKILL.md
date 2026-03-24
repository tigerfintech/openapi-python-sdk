---
name: tigeropen
description: |
  Tiger Brokers OpenAPI Python SDK — complete skills for AI coding tools. Covers SDK setup, market data queries, stock/futures/options trading, real-time push subscriptions, CLI command-line tool, and MCP server integration. Use when building trading applications, querying market data, placing orders, using the tigeropen CLI, or integrating Tiger Brokers API with AI editors.
  老虎证券 OpenAPI Python SDK 完整技能集。涵盖 SDK 配置、行情查询、股票/期货/期权交易、实时推送订阅、CLI 命令行工具、MCP Server 集成。适用于构建交易应用、查询行情数据、下单交易、使用 tigeropen CLI、或将老虎 API 集成到 AI 编辑器。
license: Apache-2.0
compatibility: Requires Python 3.8+, pip, and a Tiger Brokers developer account
metadata:
  author: tigerbrokers
  version: "3.5.6"
  language: zh_CN, en_US
  openclaw:
    requires:
      env:
        - TIGEROPEN_TIGER_ID
        - TIGEROPEN_PRIVATE_KEY
        - TIGEROPEN_ACCOUNT
      bins:
        - pip
        - python
    primaryEnv: TIGEROPEN_TIGER_ID
---

# Tiger Open API Python SDK

> 老虎量化开放平台 Python SDK 完整技能集 / Complete AI skill set for Tiger Brokers OpenAPI

- Docs: https://docs.itigerup.com/docs/prepare
- GitHub: https://github.com/tigerfintech/openapi-python-sdk
- SDK: `pip install tigeropen` | Python 3.8 - 3.14

## Reference Guides

This skill is organized into focused reference files. Load the relevant guide based on your task:

- **[Quickstart](references/quickstart.md)** — SDK install, authentication, client setup, enums/objects, error codes, FAQ
- **[Market Data](references/quote.md)** — Real-time quotes, K-lines, depth, ticks, capital flow, fundamentals, scanner
- **[Trading](references/trade.md)** — Place orders (market/limit/stop/algo), order management, assets, positions, fund transfers
- **[Options](references/option.md)** — Option chains, Greeks, single-leg/multi-leg combos, option calculator
- **[Real-time Push](references/push.md)** — Subscribe to quote/depth/tick/K-line/order/position/asset changes via PushClient
- **[CLI Tool](references/cli.md)** — Command-line interface: config, quote, trade, account, push commands with table/json/csv output
- **[MCP Server](references/mcp.md)** — Expose Tiger API as MCP tools for Cursor, Claude Code, Kiro, Trae

## Quick Start

```python
from tigeropen.common.consts import Language, Market
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

# 1. Configure / 配置
# 方式一：配置文件(推荐) / Method 1: Config file (recommended)
config = TigerOpenClientConfig(props_path='/path/to/your/config/')

# 方式二：代码赋值 / Method 2: Code assignment
# config = TigerOpenClientConfig()
# config.tiger_id = 'your_tiger_id'
# config.private_key = read_private_key('/path/to/your_private_key.pem')
# config.account = 'your_account'
# config.language = Language.en_US

# 2. Query quotes / 查询行情
quote_client = QuoteClient(config)
quote = quote_client.get_market_status(Market.US)

# 3. Place order / 下单
trade_client = TradeClient(config)
# See references/trade.md for order examples
```

## When to Use Each Reference

| Task | Reference |
|------|-----------|
| First time setup, SDK install, auth config | [quickstart.md](references/quickstart.md) |
| Get stock/option/future quotes, K-lines, screener | [quote.md](references/quote.md) |
| Place/modify/cancel orders, check positions/assets | [trade.md](references/trade.md) |
| Option chains, Greeks, combo strategies | [option.md](references/option.md) |
| Real-time streaming data via WebSocket | [push.md](references/push.md) |
| CLI commands: query data, manage orders from terminal | [cli.md](references/cli.md) |
| Set up MCP Server for AI editor integration | [mcp.md](references/mcp.md) |
