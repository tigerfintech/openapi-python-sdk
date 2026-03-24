<h1 align="center">TigerOpen Python SDK</h1>

<p align="center">
  <a href="https://pypi.org/project/tigeropen/"><img src="https://img.shields.io/pypi/v/tigeropen.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/tigeropen/"><img src="https://img.shields.io/pypi/pyversions/tigeropen.svg" alt="Python"></a>
  <a href="https://github.com/tigerfintech/openapi-python-sdk/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License"></a>
</p>

<p align="center">
  老虎证券 OpenAPI Python SDK — 行情、交易、账户、推送一站式接入
  <br>
  Tiger Brokers OpenAPI Python SDK — Market data, trading, account & push in one package
</p>

<p align="center">
  <a href="#中文文档">中文</a> | <a href="#english-documentation">English</a>
</p>

---

# 中文文档

## 目录

- [简介](#简介)
- [支持市场](#支持市场)
- [安装](#安装)
- [快速开始](#快速开始)
- [CLI 命令行工具](#cli-命令行工具)
- [MCP Server (AI 集成)](#mcp-server-ai-集成)
- [AI Skills (智能编程助手)](#ai-skills-智能编程助手)
- [示例代码](#示例代码)
- [文档与支持](#文档与支持)

## 简介

TigerOpen 是老虎证券开放平台的官方 Python SDK，为个人开发者和机构客户提供完整的证券交易接口服务：

- **行情数据** — 股票/期权/期货实时行情、K 线、逐笔成交、盘口深度
- **交易服务** — 下单、改单、撤单，支持市价/限价/止损/跟踪止损/算法订单 (TWAP/VWAP)
- **账户管理** — 资产查询、持仓管理、成交记录
- **实时推送** — WebSocket 行情推送、订单状态、持仓与资产变动
- **AI 工具链** — CLI 命令行、MCP Server、AI Skills，支持 Cursor / Claude Code / Trae 等 AI 编程工具

> 开通老虎证券账户并入金后即可免费使用 OpenAPI。

## 支持市场

| 市场 | 股票/ETF | 期权 | 期货 | 窝轮/牛熊证 |
|------|:--------:|:----:|:----:|:----------:|
| 美国 | ✅ | ✅ | ✅ | — |
| 香港 | ✅ | ✅ | ✅ | ✅ |
| 新加坡 | ✅ | — | — | — |
| 澳大利亚 | ✅ | ✅ | — | — |

## 安装

**Python 3.8+**

```bash
# 一键安装（自动检测 uv/pipx/pip）
curl -fsSL https://raw.githubusercontent.com/tigerfintech/openapi-python-sdk/master/install.sh | sh

# 或手动安装：
# 推荐：使用 uv（高速 Python 包管理器）
uv pip install tigeropen

# 或使用 pip
pip install tigeropen

# 或使用 Conda
conda install -c conda-forge tigeropen

# 从源码安装
git clone https://github.com/tigerfintech/openapi-python-sdk.git
cd openapi-python-sdk
pip install -e .

# 卸载
tigeropen uninstall
```

## 快速开始

### 1. 注册开发者

前往 [开发者信息页](https://developer.itigerup.com/profile) 注册并获取：
- `tiger_id` — 开发者 ID
- `private_key` — RSA 私钥（Python SDK 使用 **PKCS#1** 格式）
- `account` — 交易账户号

### 2. 配置

**方式一：配置文件**

创建 `tiger_openapi_config.properties`：

```properties
tiger_id=your_tiger_id
private_key_pk1=your_pkcs1_private_key
account=your_account
```

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
```

**方式二：代码直接配置**

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig()
config.tiger_id = 'your_tiger_id'
config.account = 'your_account'
config.private_key = 'your_private_key_content'
```

### 3. 查询行情

```python
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.common.consts import Market

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
client = QuoteClient(config)

# 实时报价
briefs = client.get_stock_briefs(['AAPL', 'TSLA'])
print(briefs)

# K 线数据
bars = client.get_bars(['AAPL'], period='day', limit=10)
print(bars)

# 市场状态
status = client.get_market_status(Market.US)
print(status)
```

### 4. 下单交易

```python
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import limit_order

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
client = TradeClient(config)

# 创建合约和订单
contract = stock_contract('AAPL', 'USD')
order = limit_order(client._account, contract, 'BUY', 1, 150.0)

# 预览订单
preview = client.preview_order(order)
print(preview)

# 下单
order_id = client.place_order(order)
print(f'Order ID: {order_id}')
```

### 5. 实时推送

```python
from tigeropen.push.push_client import PushClient
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
protocol, host, port = config.socket_host_port

def on_quote_changed(symbol, items, hour_trading):
    print(f'{symbol}: {items}')

push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))
push_client.quote_changed = on_quote_changed
push_client.connect(config.tiger_id, config.private_key)
push_client.subscribe_quote(['AAPL', 'TSLA'])
```

## CLI 命令行工具

安装 SDK 后自动获得 `tigeropen` 命令行工具，无需编码即可查询行情、管理订单。

### 初始化配置

```bash
tigeropen config init    # 交互式配置 tiger_id / account / private_key
tigeropen config show    # 查看当前配置（私钥已脱敏）
```

### 行情查询

```bash
# 实时报价
tigeropen quote briefs AAPL TSLA

# K 线数据
tigeropen quote bars AAPL --period day --limit 10

# 分时数据
tigeropen quote timeline AAPL

# 市场状态
tigeropen quote market-status

# 期权链
tigeropen quote option expirations AAPL
tigeropen quote option chain AAPL 2026-06-19

# 期货
tigeropen quote future exchanges
tigeropen quote future contracts CME
```

### 交易操作

```bash
# 查看持仓
tigeropen trade position list

# 查看订单
tigeropen trade order list --status Filled

# 预览订单
tigeropen trade order preview --symbol AAPL --action BUY --quantity 100 --limit-price 150

# 下单（会提示确认）
tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150

# 撤单
tigeropen trade order cancel 12345678
```

### 账户信息

```bash
tigeropen account assets
tigeropen account info
```

### 输出格式

```bash
# 表格（默认）
tigeropen quote briefs AAPL

# JSON
tigeropen quote briefs AAPL --format json

# CSV
tigeropen quote briefs AAPL --format csv
```

### 命令总览

```
tigeropen
├── config    — init / show / set / path
├── quote     — briefs / bars / timeline / ticks / depth / market-status / symbols
│   ├── option      — expirations / chain / briefs / bars
│   ├── future      — exchanges / contracts / briefs / bars
│   ├── capital     — flow / distribution
│   └── fundamental — financial / dividend / earnings
├── trade
│   ├── order       — list / get / place / preview / modify / cancel
│   ├── position    — list
│   └── transaction — list
├── account   — info / assets / analytics
├── push      — quote / order / position / asset
└── version
```

## MCP Server (AI 集成)

TigerOpen 提供 MCP (Model Context Protocol) Server，可与 Cursor、Claude Code、Trae 等 AI 编程工具集成，通过自然语言查询行情和管理交易。

### 安装

```bash
# 需要先安装 uv
pip install uv
# 或
brew install uv
```

### 配置

在 AI 工具的 MCP 配置中添加：

**个人账户：**

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["tigermcp"],
      "env": {
        "TIGEROPEN_TIGER_ID": "your_tiger_id",
        "TIGEROPEN_PRIVATE_KEY": "your_private_key",
        "TIGEROPEN_ACCOUNT": "your_account"
      }
    }
  }
}
```

**机构账户：**

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["tigermcp"],
      "env": {
        "TIGEROPEN_TIGER_ID": "your_tiger_id",
        "TIGEROPEN_PRIVATE_KEY": "your_private_key",
        "TIGEROPEN_ACCOUNT": "your_account",
        "TIGEROPEN_SECRET_KEY": "your_secret_key",
        "TIGEROPEN_TOKEN": "your_token"
      }
    }
  }
}
```

**只读模式：** 添加 `"TIGERMCP_READONLY": "true"` 到 `env` 中，禁止下单操作。

**macOS 12 用户：** 若遇到 `realpath` 错误，需安装 coreutils：`brew install coreutils`

### 使用示例

在 AI 工具中直接用自然语言：

- "查询 AAPL 的实时报价"
- "帮我看看 TSLA 最近 5 天的 K 线"
- "查询我的持仓"
- "以 150 美元限价买入 100 股 AAPL"

## AI Skills (智能编程助手)

TigerOpen 提供 [Agent Skills](https://github.com/anthropics/claude-code/blob/main/docs/skills.md) 规范的技能包，为 Claude Code 等 AI 编程工具提供 Tiger OpenAPI 的专业知识。

### 技能模块

| 技能 | 说明 |
|------|------|
| `quickstart` | 环境搭建与 SDK 配置 |
| `quote` | 行情接口使用指导 |
| `trade` | 交易接口使用指导 |
| `option` | 期权接口使用指导 |
| `push` | 实时推送接口使用指导 |
| `mcp` | MCP Server 配置指导 |

### 安装方式

**方式一：Claude Code 插件市场**

```bash
claude install-plugin tigerfintech/openapi-python-sdk/tigeropen/examples/ai/skills
```

**方式二：全局安装**

```bash
cp -r tigeropen/examples/ai/skills/ ~/.claude/skills/tigeropen/
```

**方式三：项目级安装**

```bash
cp -r tigeropen/examples/ai/skills/ .claude/skills/tigeropen/
```

更多安装方式详见 [Skills README](tigeropen/examples/ai/skills/README.md)。

## 示例代码

更多示例代码位于 [tigeropen/examples/](tigeropen/examples/) 目录。

## 文档与支持

- [官方 API 文档](https://docs.itigerup.com/docs/)
- [开发者信息页](https://developer.itigerup.com/profile)
- [GitHub Issues](https://github.com/tigerfintech/openapi-python-sdk/issues)
- 老虎量化 QQ 群：869893807（团队或公司客户请联系群主）

## License

[Apache License 2.0](LICENSE)

---

# English Documentation

## Table of Contents

- [Introduction](#introduction)
- [Supported Markets](#supported-markets)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Tool](#cli-tool)
- [MCP Server (AI Integration)](#mcp-server-ai-integration)
- [AI Skills](#ai-skills)
- [Examples](#examples)
- [Documentation & Support](#documentation--support)

## Introduction

TigerOpen is the official Python SDK for Tiger Brokers' Open Platform, providing developers and institutional clients with comprehensive securities trading interfaces:

- **Market Data** — Real-time quotes, candlesticks, tick data, order book depth for stocks, options & futures
- **Trading** — Place, modify, cancel orders; supports market/limit/stop/trailing-stop/algo orders (TWAP/VWAP)
- **Account Management** — Asset queries, position tracking, transaction history
- **Real-time Push** — WebSocket streaming for quotes, order status, position & asset changes
- **AI Toolchain** — CLI, MCP Server, AI Skills; integrates with Cursor / Claude Code / Trae

> OpenAPI is free to use after opening and funding a Tiger Brokers account.

## Supported Markets

| Market | Stocks/ETFs | Options | Futures | Warrants/CBBCs |
|--------|:-----------:|:-------:|:-------:|:--------------:|
| US | ✅ | ✅ | ✅ | — |
| Hong Kong | ✅ | ✅ | ✅ | ✅ |
| Singapore | ✅ | — | — | — |
| Australia | ✅ | ✅ | — | — |

## Installation

**Python 3.8+**

```bash
# One-line install (auto-detects uv/pipx/pip)
curl -fsSL https://raw.githubusercontent.com/tigerfintech/openapi-python-sdk/master/install.sh | sh

# Or install manually:
# Recommended: use uv (fast Python package manager)
uv pip install tigeropen

# Or use pip
pip install tigeropen

# Or use Conda
conda install -c conda-forge tigeropen

# Install from source
git clone https://github.com/tigerfintech/openapi-python-sdk.git
cd openapi-python-sdk
pip install -e .

# Uninstall
tigeropen uninstall
```

## Quick Start

### 1. Register as a Developer

Go to the [Developer Portal](https://developer.itigerup.com/profile) to obtain:
- `tiger_id` — Developer ID
- `private_key` — RSA private key (Python SDK uses **PKCS#1** format)
- `account` — Trading account number

### 2. Configuration

**Option A: Properties file**

Create `tiger_openapi_config.properties`:

```properties
tiger_id=your_tiger_id
private_key_pk1=your_pkcs1_private_key
account=your_account
```

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
```

**Option B: Direct configuration**

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig()
config.tiger_id = 'your_tiger_id'
config.account = 'your_account'
config.private_key = 'your_private_key_content'
```

### 3. Query Market Data

```python
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.common.consts import Market

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
client = QuoteClient(config)

# Real-time quotes
briefs = client.get_stock_briefs(['AAPL', 'TSLA'])
print(briefs)

# Candlestick data
bars = client.get_bars(['AAPL'], period='day', limit=10)
print(bars)

# Market status
status = client.get_market_status(Market.US)
print(status)
```

### 4. Place Orders

```python
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import limit_order

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
client = TradeClient(config)

# Create contract and order
contract = stock_contract('AAPL', 'USD')
order = limit_order(client._account, contract, 'BUY', 1, 150.0)

# Preview order
preview = client.preview_order(order)
print(preview)

# Place order
order_id = client.place_order(order)
print(f'Order ID: {order_id}')
```

### 5. Real-time Push

```python
from tigeropen.push.push_client import PushClient
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig(props_path='~/.tigeropen/')
protocol, host, port = config.socket_host_port

def on_quote_changed(symbol, items, hour_trading):
    print(f'{symbol}: {items}')

push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))
push_client.quote_changed = on_quote_changed
push_client.connect(config.tiger_id, config.private_key)
push_client.subscribe_quote(['AAPL', 'TSLA'])
```

## CLI Tool

After installing the SDK, you get the `tigeropen` CLI — query market data and manage orders without writing code.

### Initialize Configuration

```bash
tigeropen config init    # Interactive setup for tiger_id / account / private_key
tigeropen config show    # Show current config (private key masked)
```

### Market Data

```bash
# Real-time quotes
tigeropen quote briefs AAPL TSLA

# Candlestick data
tigeropen quote bars AAPL --period day --limit 10

# Intraday timeline
tigeropen quote timeline AAPL

# Market status
tigeropen quote market-status

# Option chain
tigeropen quote option expirations AAPL
tigeropen quote option chain AAPL 2026-06-19

# Futures
tigeropen quote future exchanges
tigeropen quote future contracts CME
```

### Trading

```bash
# View positions
tigeropen trade position list

# View orders
tigeropen trade order list --status Filled

# Preview order
tigeropen trade order preview --symbol AAPL --action BUY --quantity 100 --limit-price 150

# Place order (confirmation required)
tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150

# Cancel order
tigeropen trade order cancel 12345678
```

### Account

```bash
tigeropen account assets
tigeropen account info
```

### Output Formats

```bash
# Table (default)
tigeropen quote briefs AAPL

# JSON
tigeropen quote briefs AAPL --format json

# CSV
tigeropen quote briefs AAPL --format csv
```

### Command Reference

```
tigeropen
├── config    — init / show / set / path
├── quote     — briefs / bars / timeline / ticks / depth / market-status / symbols
│   ├── option      — expirations / chain / briefs / bars
│   ├── future      — exchanges / contracts / briefs / bars
│   ├── capital     — flow / distribution
│   └── fundamental — financial / dividend / earnings
├── trade
│   ├── order       — list / get / place / preview / modify / cancel
│   ├── position    — list
│   └── transaction — list
├── account   — info / assets / analytics
├── push      — quote / order / position / asset
└── version
```

## MCP Server (AI Integration)

TigerOpen provides an MCP (Model Context Protocol) Server that integrates with AI coding tools like Cursor, Claude Code, and Trae, enabling market queries and trade management via natural language.

### Install

```bash
# Install uv first
pip install uv
# or
brew install uv
```

### Configuration

Add to your AI tool's MCP settings:

**Personal account:**

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["tigermcp"],
      "env": {
        "TIGEROPEN_TIGER_ID": "your_tiger_id",
        "TIGEROPEN_PRIVATE_KEY": "your_private_key",
        "TIGEROPEN_ACCOUNT": "your_account"
      }
    }
  }
}
```

**Institutional account:**

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["tigermcp"],
      "env": {
        "TIGEROPEN_TIGER_ID": "your_tiger_id",
        "TIGEROPEN_PRIVATE_KEY": "your_private_key",
        "TIGEROPEN_ACCOUNT": "your_account",
        "TIGEROPEN_SECRET_KEY": "your_secret_key",
        "TIGEROPEN_TOKEN": "your_token"
      }
    }
  }
}
```

**Read-only mode:** Add `"TIGERMCP_READONLY": "true"` to `env` to disable order placement.

**macOS 12 users:** If you encounter a `realpath` error, install coreutils: `brew install coreutils`

### Usage Examples

Use natural language in your AI tool:

- "Get real-time quote for AAPL"
- "Show me TSLA's daily candles for the last 5 days"
- "Check my positions"
- "Buy 100 shares of AAPL at $150 limit"

## AI Skills

TigerOpen provides skill packs following the [Agent Skills](https://github.com/anthropics/claude-code/blob/main/docs/skills.md) standard, giving AI coding tools like Claude Code expert knowledge of Tiger OpenAPI.

### Skill Modules

| Skill | Description |
|-------|-------------|
| `quickstart` | Environment setup & SDK configuration |
| `quote` | Market data API guidance |
| `trade` | Trading API guidance |
| `option` | Options API guidance |
| `push` | Real-time push API guidance |
| `mcp` | MCP Server configuration |

### Installation

**Option 1: Claude Code Plugin Marketplace**

```bash
claude install-plugin tigerfintech/openapi-python-sdk/tigeropen/examples/ai/skills
```

**Option 2: Global installation**

```bash
cp -r tigeropen/examples/ai/skills/ ~/.claude/skills/tigeropen/
```

**Option 3: Project-level installation**

```bash
cp -r tigeropen/examples/ai/skills/ .claude/skills/tigeropen/
```

See the [Skills README](tigeropen/examples/ai/skills/README.md) for more installation methods.

## Examples

More examples are available in the [tigeropen/examples/](tigeropen/examples/) directory.

## Documentation & Support

- [Official API Documentation](https://docs-en.itigerup.com/docs/)
- [Developer Portal](https://developer.itigerup.com/profile)
- [GitHub Issues](https://github.com/tigerfintech/openapi-python-sdk/issues)
- Tiger Quant QQ Group: 869893807

## License

[Apache License 2.0](LICENSE)
