
# Tiger MCP Server

> 中文 | English — 双语技能。Bilingual skill.
> 官方文档 Docs: https://docs.itigerup.com/docs/mcp

Tiger MCP Server 将老虎 OpenAPI 暴露为 MCP (Model Context Protocol) 工具，集成到 Cursor、Claude Code、Kiro、Trae 等 AI 编辑器。
Tiger MCP Server exposes Tiger OpenAPI as MCP tools for AI editors like Cursor, Claude Code, Kiro, and Trae.

## 安装 / Installation

```bash
pip install tigermcp
# 或推荐使用 uvx / Or recommended:
uvx tigermcp
```

### 前置：安装 uv / Prerequisites: Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 配置 / Configuration

### 方式一：配置文件 / Config File

```bash
export TIGEROPEN_PROPS_PATH="/path/to/config/"  # 配置文件所在目录 / Directory containing config file
```

### 方式二：环境变量 / Environment Variables

```bash
export TIGEROPEN_TIGER_ID="your_tiger_id"
export TIGEROPEN_PRIVATE_KEY="your_private_key"  # 私钥内容或文件路径 / Key content or file path
export TIGEROPEN_ACCOUNT="your_account"
```

### 可选配置 / Optional

```bash
export TIGERMCP_READONLY=true   # 只读模式，禁止交易 / Read-only mode, disable trading
export TIGERMCP_DEBUG=true      # 调试模式 / Debug mode
```

## 运行 / Run

```bash
uvx tigermcp
```

## AI 编辑器集成 / AI Editor Integration

### 个人用户 / Individual Users

在编辑器的 MCP 配置中添加 / Add to editor's MCP config:

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["--python", "3.13", "tigermcp"],
      "env": {
        "TIGEROPEN_TIGER_ID": "your_tiger_id",
        "TIGEROPEN_PRIVATE_KEY": "your_private_key",
        "TIGEROPEN_ACCOUNT": "your_account",
        "TIGERMCP_READONLY": true
      }
    }
  }
}
```

> 也可使用 `TIGEROPEN_PROPS_PATH` 指定配置文件路径，代替 `TIGEROPEN_TIGER_ID` 等配置。
> You can also use `TIGEROPEN_PROPS_PATH` to specify config file path instead of individual env vars.

### 机构用户 / Institutional Users

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["--python", "3.13", "tigermcp"],
      "env": {
        "TIGEROPEN_TIGER_ID": "your_tiger_id",
        "TIGEROPEN_PRIVATE_KEY": "your_private_key",
        "TIGEROPEN_ACCOUNT": "your_account",
        "TIGEROPEN_SECRET_KEY": "your_secret_key",
        "TIGEROPEN_SIGN_TYPE": "TBHK",
        "TIGERMCP_TOKEN": "your_2fa_token"
      }
    }
  }
}
```

### 只读模式(推荐初次使用) / Read-only Mode (Recommended for First-time Use)

```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["--python", "3.13", "tigermcp"],
      "env": {
        "TIGEROPEN_PROPS_PATH": "/path/to/config/",
        "TIGERMCP_READONLY": true
      }
    }
  }
}
```

### 编辑器配置文件位置 / Editor Config File Locations

| 编辑器 Editor | 配置路径 Config Path |
|--------------|---------------------|
| Cursor | `.cursor/mcp.json` (项目级) 或 `~/.cursor/mcp.json` (全局) |
| Claude Code | `.claude/settings.local.json` 或 `~/.claude/settings.json` |
| Trae | `.trae/mcp.json` |
| Kiro | `.kiro/settings/mcp.json` (项目级) 或 `~/.kiro/settings/mcp.json` (全局) |

## 可用 MCP 工具 / Available MCP Tools

### 行情工具 / Quote Tools

| 工具 Tool | 功能 Function |
|----------|--------------|
| `get_realtime_quote` | 股票/期权/期货实时行情 Real-time stock/option/future quotes |
| `get_depth_quote` | 深度盘口 Level 2 order book |
| `get_ticks` | 逐笔成交 Trade ticks |
| `get_bars` | K线数据 K-line candlestick data |
| `get_timeline` | 分时数据 Intraday timeline |
| `get_capital_flow` | 资金流向 Capital flow |
| `get_capital_distribution` | 资金分布 Capital distribution |
| `get_stock_broker` | 港股经纪商数据 HK broker seat data |
| `get_option_expirations` | 期权到期日 Option expiration dates |
| `get_option_chain` | 期权链 Option chain with Greeks |
| `get_hk_option_symbols` | 港股期权代码映射 HK option symbol mapping |
| `get_market_status` | 市场状态 Market status |

### 交易工具 / Trade Tools

| 工具 Tool | 功能 Function |
|----------|--------------|
| `place_order` | 下单 Place order (只读模式禁用 disabled in read-only) |
| `cancel_order` | 撤单 Cancel order (只读模式禁用 disabled in read-only) |
| `preview_order` | 预览订单 Preview order |
| `get_orders` | 查询订单列表 Query orders |
| `get_order` | 订单详情 Order details |
| `get_transactions` | 成交记录 Transaction records |
| `get_positions` | 持仓查询 Position query |
| `get_assets` | 资产查询 Asset query |
| `get_analytics_asset` | 资产分析 Asset analytics |
| `get_contract` | 合约信息 Contract info |

## 常见问题 / Troubleshooting

### macOS 12 及以下 `realpath: command not found`

```bash
brew install coreutils
```

### Homebrew 未安装 / Homebrew Not Installed

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 连接问题 / Connection Issues

- 确保网络可访问 Tiger API 服务器 / Ensure network can reach Tiger API servers
- 检查 tiger_id/private_key/account 是否正确 / Verify credentials
- 检查私钥格式为 PKCS#1 / Ensure private key is PKCS#1 format

## 注意事项 / Notes

- `TIGERMCP_READONLY=true` 启用只读模式，禁止 `place_order` 和 `cancel_order`，初次使用建议开启
- MCP Server 通过 stdio 模式运行 / Runs in stdio mode
- 需要 `tigeropen>=3.4.8` 和 `mcp[cli]>=1.13.0`
- 也可使用 `TIGEROPEN_PROPS_PATH` 指定配置文件路径，代替单独配置各环境变量
- Tiger MCP 是 AI 连接 Tiger API 的工具，输出取决于 AI/LLM 能力
- 用户承担所有投资决策风险 / Users bear all investment decision risks
- 免责声明 / Disclaimer: https://docs.itigerup.com/docs/mcp
