---
name: tigeropen-mcp
description: Tiger MCP Server 配置与 AI 集成技能。将老虎 OpenAPI 暴露为 MCP 工具，集成到 Cursor、Claude Code、Trae 等 AI 编辑器。支持行情查询、下单交易、账户管理等 MCP 工具。当用户需要配置 Tiger MCP Server、集成到 AI 工具、或使用 AI 进行量化交易时使用此技能。
metadata:
  author: tigerbrokers
  version: "0.1.5"
  language: zh_CN
---

# Tiger MCP Server

Tiger MCP Server 将老虎 OpenAPI 暴露为 Model Context Protocol (MCP) 工具，可直接集成到 Cursor、Claude Code、Trae 等 AI 编辑器中。

## 安装

```bash
pip install tigermcp
# 或使用 uvx（推荐）
uvx tigermcp
```

### 前置：安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 配置

### 方式一：配置文件

```bash
export TIGEROPEN_PROPS_PATH="/path/to/tiger_openapi_config.properties"
```

### 方式二：单独环境变量

```bash
export TIGEROPEN_TIGER_ID="your_tiger_id"
export TIGEROPEN_PRIVATE_KEY="your_private_key"
export TIGEROPEN_ACCOUNT="your_account"
```

### 可选配置

```bash
export TIGERMCP_READONLY=true   # 只读模式，禁止交易操作
export TIGERMCP_DEBUG=true      # 调试模式
```

## 运行

```bash
uvx tigermcp
```

## 集成到 AI 编辑器

在编辑器的 MCP 配置文件中添加：

### Cursor / Claude Code / Trae

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["tigermcp"],
      "env": {
        "TIGEROPEN_PROPS_PATH": "/path/to/tiger_openapi_config.properties"
      }
    }
  }
}
```

### 只读模式（推荐初次使用）

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["tigermcp"],
      "env": {
        "TIGEROPEN_PROPS_PATH": "/path/to/config.properties",
        "TIGERMCP_READONLY": "true"
      }
    }
  }
}
```

## 可用 MCP 工具

### 行情工具

| 工具 | 功能 |
|------|------|
| `get_realtime_quote` | 股票/期权/期货实时行情 |
| `get_depth_quote` | 深度盘口数据 |
| `get_ticks` | 逐笔成交 |
| `get_bars` | K线数据 |
| `get_timeline` | 分时数据 |
| `get_capital_flow` | 资金流向 |
| `get_capital_distribution` | 资金分布 |
| `get_stock_broker` | 港股经纪商数据 |
| `get_option_expirations` | 期权到期日 |
| `get_option_chain` | 期权链 |
| `get_hk_option_symbols` | 港股期权代码映射 |
| `get_market_status` | 市场状态 |

### 交易工具

| 工具 | 功能 |
|------|------|
| `place_order` | 下单（只读模式下禁用） |
| `cancel_order` | 撤单（只读模式下禁用） |
| `preview_order` | 预览订单 |
| `get_orders` | 查询订单 |
| `get_order` | 订单详情 |
| `get_transactions` | 成交记录 |
| `get_positions` | 持仓查询 |
| `get_assets` | 资产查询 |
| `get_analytics_asset` | 资产分析 |
| `get_contract` | 合约信息 |

## 常见问题

### macOS 12 及以下 `realpath: command not found`

```bash
brew install coreutils
```

### Homebrew 未安装

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## 注意事项

- `TIGERMCP_READONLY=true` 启用只读模式，禁止 `place_order` 和 `cancel_order`
- 初次使用建议先用只读模式熟悉
- MCP Server 通过 stdio 模式运行
- 需要 `tigeropen>=3.4.8` 和 `mcp[cli]>=1.13.0`
