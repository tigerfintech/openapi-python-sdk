---
name: tigeropen-mcp
description: Tiger MCP Server setup and AI integration skill. Expose Tiger OpenAPI as MCP tools for Cursor, Claude Code, Trae and other AI editors. Supports market data queries, order trading, and account management MCP tools. Use this skill when users need to configure Tiger MCP Server, integrate with AI tools, or use AI for quantitative trading.
metadata:
  author: tigerbrokers
  version: "0.1.5"
  language: en_US
---

# Tiger MCP Server

Tiger MCP Server exposes Tiger OpenAPI as Model Context Protocol (MCP) tools, integrating directly with Cursor, Claude Code, Trae, and other AI editors.

## Installation

```bash
pip install tigermcp
# Or using uvx (recommended)
uvx tigermcp
```

### Prerequisite: Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Configuration

### Option 1: Config File

```bash
export TIGEROPEN_PROPS_PATH="/path/to/tiger_openapi_config.properties"
```

### Option 2: Individual Environment Variables

```bash
export TIGEROPEN_TIGER_ID="your_tiger_id"
export TIGEROPEN_PRIVATE_KEY="your_private_key"
export TIGEROPEN_ACCOUNT="your_account"
```

### Optional

```bash
export TIGERMCP_READONLY=true   # Read-only mode, disables trading
export TIGERMCP_DEBUG=true      # Debug mode
```

## Run

```bash
uvx tigermcp
```

## AI Editor Integration

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

### Read-only Mode (recommended for first-time use)

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

## Available MCP Tools

### Quote Tools

| Tool | Function |
|------|----------|
| `get_realtime_quote` | Stock/option/futures real-time quotes |
| `get_depth_quote` | Level 2 order book |
| `get_ticks` | Trade ticks |
| `get_bars` | K-line candlestick data |
| `get_timeline` | Intraday timeline |
| `get_capital_flow` | Capital flow |
| `get_capital_distribution` | Capital distribution |
| `get_stock_broker` | HK broker seat data |
| `get_option_expirations` | Option expiration dates |
| `get_option_chain` | Option chain |
| `get_hk_option_symbols` | HK option symbol mapping |
| `get_market_status` | Market status |

### Trade Tools

| Tool | Function |
|------|----------|
| `place_order` | Place order (disabled in read-only mode) |
| `cancel_order` | Cancel order (disabled in read-only mode) |
| `preview_order` | Preview order |
| `get_orders` | Query orders |
| `get_order` | Order details |
| `get_transactions` | Transaction records |
| `get_positions` | Position query |
| `get_assets` | Asset query |
| `get_analytics_asset` | Asset analytics |
| `get_contract` | Contract info |

## Troubleshooting

### macOS 12 and below: `realpath: command not found`

```bash
brew install coreutils
```

## Notes

- `TIGERMCP_READONLY=true` enables read-only mode, blocking `place_order` and `cancel_order`
- Start with read-only mode to get familiar
- MCP Server runs in stdio mode
- Requires `tigeropen>=3.4.8` and `mcp[cli]>=1.13.0`
