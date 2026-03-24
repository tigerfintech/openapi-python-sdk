
# Tiger Open API CLI 命令行工具 / CLI Tool

> 中文 | English — 双语技能，代码通用。Bilingual skill with shared code examples.
> 官方 CLI 入口: `tigeropen` (安装 SDK 后自动可用 / Available after SDK install)

## 概述 / Overview

TigerOpen CLI 是基于 click 框架的命令行工具，安装 `tigeropen` SDK 后自动获得 `tigeropen` 命令。
无需编写 Python 代码即可查询行情、管理订单、查看账户信息。
The TigerOpen CLI is a click-based command-line tool, available automatically after installing the `tigeropen` SDK.
Query market data, manage orders, and view account info without writing Python code.

- 入口命令 Entry point: `tigeropen`
- 安装 Install: `pip install tigeropen`
- Python: 3.8 - 3.14

---

## 配置 / Configuration

### 初始化配置 / Initialize Config

```bash
# 交互式配置（会引导输入 tiger_id, account, private_key）
# Interactive setup (prompts for tiger_id, account, private_key)
tigeropen config init
```

配置文件默认保存到 `~/.tigeropen/tiger_openapi_config.properties`。
Config file is saved to `~/.tigeropen/tiger_openapi_config.properties` by default.

### 查看配置 / Show Config

```bash
# 查看当前配置（私钥已脱敏）/ Show config (private key masked)
tigeropen config show
```

### 修改配置 / Set Config Value

```bash
# 设置单个配置项 / Set a single config value
tigeropen config set tiger_id your_tiger_id
tigeropen config set account your_account
```

### 查看配置路径 / Show Config Path

```bash
tigeropen config path
```

### 指定配置目录 / Specify Config Directory

```bash
# 使用 --config-path 或 -c 指定配置文件路径（全局选项）
# Use --config-path or -c to specify config path (global option)
tigeropen -c /path/to/config/ quote briefs AAPL
```

---

## 全局选项 / Global Options

所有命令均支持以下全局选项。These global options apply to all commands.

| 选项 Option | 短写 Short | 说明 Description | 默认 Default |
|-------------|-----------|-----------------|-------------|
| `--config-path` | `-c` | 配置文件路径 Config file path | `~/.tigeropen/` |
| `--format` | `-f` | 输出格式 Output format: `table` / `json` / `csv` | `table` |
| `--language` | `-l` | 语言 Language: `en_US` / `zh_CN` / `zh_TW` | `en_US` |
| `--verbose` | `-v` | 调试日志 Enable debug logging | `false` |

### 输出格式示例 / Output Format Examples

```bash
# 表格输出（默认）/ Table output (default)
tigeropen quote briefs AAPL

# JSON 输出 / JSON output
tigeropen -f json quote briefs AAPL

# CSV 输出 / CSV output
tigeropen --format csv quote bars AAPL --limit 5
```

---

## 版本 / Version

```bash
tigeropen version
```

---

## 行情命令 / Quote Commands

### 实时报价 / Real-time Quotes

```bash
# 获取一个或多个股票的实时行情 / Get real-time quotes for one or more symbols
tigeropen quote briefs AAPL TSLA GOOG

# 包含盘前盘后数据 / Include pre/after market data
tigeropen quote briefs AAPL --hour-trading
```

### K 线数据 / Candlestick (Bars) Data

```bash
# 日 K 线 / Daily bars
tigeropen quote bars AAPL

# 指定周期和数量 / Specify period and limit
tigeropen quote bars AAPL --period 5min --limit 20

# 指定时间范围 / Specify time range
tigeropen quote bars AAPL --begin-time 2026-01-01 --end-time 2026-03-01

# 可选周期 / Available periods:
# day, week, month, year, 1min, 3min, 5min, 10min, 15min, 30min, 60min
```

### 分时数据 / Intraday Timeline

```bash
# 今日分时 / Today's timeline
tigeropen quote timeline AAPL

# 指定日期 / Specific date
tigeropen quote timeline AAPL --date 2026-03-20
```

### 逐笔成交 / Tick Data

```bash
tigeropen quote ticks AAPL

# 限制条数 / Limit results
tigeropen quote ticks AAPL --limit 50

# 指定范围 / Specify range
tigeropen quote ticks AAPL --begin-index 0 --end-index 100
```

### 盘口深度 / Order Book Depth

```bash
# --market 为必选参数 / --market is required
tigeropen quote depth AAPL --market US
tigeropen quote depth 00700 --market HK
```

### 市场状态 / Market Status

```bash
# 所有市场 / All markets
tigeropen quote market-status

# 指定市场 / Specific market
tigeropen quote market-status --market US
tigeropen quote market-status --market HK

# 可选: US, HK, CN, ALL
```

### 股票列表 / Symbol List

```bash
# 美股列表 / US stock list
tigeropen quote symbols

# 港股列表 / HK stock list
tigeropen quote symbols --market HK
```

---

## 期权命令 / Option Commands

```bash
# 期权到期日列表 / Option expiration dates
tigeropen quote option expirations AAPL

# 期权链（需指定标的和到期日）/ Option chain (symbol + expiry)
tigeropen quote option chain AAPL 2026-06-19

# 期权报价（需期权标识符）/ Option quotes (by identifier)
tigeropen quote option briefs "AAPL  260619C00150000"

# 期权 K 线 / Option bars
tigeropen quote option bars "AAPL  260619C00150000" --period day --limit 10
```

> 期权标识符格式 / Option identifier format: `SYMBOL  YYMMDDCSSSSSSSS` (C=Call, P=Put, S=Strike*1000)

---

## 期货命令 / Futures Commands

```bash
# 期货交易所列表 / Futures exchanges
tigeropen quote future exchanges

# 交易所合约列表 / Contracts for an exchange
tigeropen quote future contracts CME

# 期货报价 / Futures quotes
tigeropen quote future briefs ES2606 CL2509

# 期货 K 线 / Futures bars
tigeropen quote future bars CL2509 --period day --limit 20
```

---

## 资金流向 / Capital Flow

```bash
# 资金流向数据 / Capital flow
tigeropen quote capital flow AAPL --market US --period day

# 可选 period: intraday, day, week, month
```

### 资金分布 / Capital Distribution

```bash
tigeropen quote capital distribution AAPL --market US
```

---

## 基本面数据 / Fundamental Data

### 财务报告 / Financial Reports

```bash
# 年度营收和净利润 / Annual revenue and net income
tigeropen quote fundamental financial AAPL --fields total_revenue,net_income

# 季度数据 / Quarterly data
tigeropen quote fundamental financial AAPL --period-type QUARTERLY

# 指定时间范围 / Specify date range
tigeropen quote fundamental financial AAPL --begin-date 2024-01-01 --end-date 2026-01-01

# 可选 period-type: ANNUAL, QUARTERLY, LTM
```

### 分红数据 / Dividend Data

```bash
tigeropen quote fundamental dividend AAPL --begin-date 2024-01-01 --end-date 2026-01-01
```

### 财报日历 / Earnings Calendar

```bash
tigeropen quote fundamental earnings --begin-date 2026-03-01 --end-date 2026-03-31
tigeropen quote fundamental earnings --market HK --begin-date 2026-03-01 --end-date 2026-03-31
```

---

## 交易命令 / Trade Commands

### 订单管理 / Order Management

```bash
# 订单列表 / List orders
tigeropen trade order list

# 按状态筛选 / Filter by status
tigeropen trade order list --status Filled
tigeropen trade order list --status Submitted

# 按标的筛选 / Filter by symbol
tigeropen trade order list --symbol AAPL

# 按市场筛选 / Filter by market
tigeropen trade order list --market US

# 限制数量 / Limit results
tigeropen trade order list --limit 20

# 查看订单详情 / Order details
tigeropen trade order get 12345678
```

### 预览订单 / Preview Order

```bash
# 预览限价买单 / Preview a limit buy order
tigeropen trade order preview --symbol AAPL --action BUY --quantity 100 --limit-price 150

# 预览市价卖单 / Preview a market sell order
tigeropen trade order preview --symbol AAPL --action SELL --quantity 50 --order-type MKT

# 可选参数 / Options:
#   --symbol       标的代码 Symbol (required)
#   --action       BUY/SELL (required)
#   --quantity     数量 Quantity (required)
#   --order-type   LMT/MKT/STP/STP_LMT (default: LMT)
#   --limit-price  限价 Limit price (LMT/STP_LMT)
#   --sec-type     STK/OPT/FUT (default: STK)
```

### 下单 / Place Order

```bash
# 下单（默认需要确认）/ Place order (confirmation required by default)
tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150

# 跳过确认 / Skip confirmation
tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150 -y
```

> 下单前建议先 preview 预览订单。Preview order before placing.

### 修改订单 / Modify Order

```bash
# 修改限价 / Modify limit price
tigeropen trade order modify 12345678 --limit-price 155

# 修改数量 / Modify quantity
tigeropen trade order modify 12345678 --quantity 200

# 修改辅助价 / Modify aux price
tigeropen trade order modify 12345678 --aux-price 140

# 跳过确认 / Skip confirmation
tigeropen trade order modify 12345678 --limit-price 155 -y
```

### 撤销订单 / Cancel Order

```bash
# 撤销订单（需确认）/ Cancel order (confirmation required)
tigeropen trade order cancel 12345678

# 跳过确认 / Skip confirmation
tigeropen trade order cancel 12345678 -y
```

---

## 持仓命令 / Position Commands

```bash
# 所有股票持仓 / All stock positions
tigeropen trade position list

# 按证券类型 / By security type
tigeropen trade position list --sec-type OPT
tigeropen trade position list --sec-type FUT

# 按市场 / By market
tigeropen trade position list --market US
tigeropen trade position list --market HK

# 按标的 / By symbol
tigeropen trade position list --symbol AAPL

# 可选 sec-type: STK, OPT, FUT, WAR
# 可选 market: US, HK, ALL
```

---

## 成交记录 / Transaction Records

```bash
# 所有成交记录 / All transactions
tigeropen trade transaction list

# 按标的筛选 / Filter by symbol
tigeropen trade transaction list --symbol AAPL

# 按时间范围 / Filter by time range
tigeropen trade transaction list --start-time 2026-01-01 --end-time 2026-03-31

# 限制条数 / Limit results
tigeropen trade transaction list --limit 50
```

---

## 账户命令 / Account Commands

```bash
# 账户信息 / Account info
tigeropen account info

# 资产概览 / Asset summary
tigeropen account assets

# 按币种 / By currency
tigeropen account assets --currency USD

# 资产分析 / Asset analytics
tigeropen account analytics
tigeropen account analytics --start-date 2026-01-01 --end-date 2026-03-31
```

---

## 推送命令 / Push Commands (Real-time Streaming)

推送命令使用 WebSocket 连接，持续输出直到 Ctrl+C。
Push commands use WebSocket connections, streaming until Ctrl+C.

```bash
# 实时行情推送 / Real-time quote streaming
tigeropen push quote AAPL TSLA

# 订单状态推送 / Order status updates
tigeropen push order

# 持仓变动推送 / Position updates
tigeropen push position

# 资产变动推送 / Asset updates
tigeropen push asset
```

> 同一 `tiger_id` 只能有一个推送连接，新连接会踢掉旧连接。
> Only one push connection per `tiger_id`; new connection kicks the old one.

---

## 命令总览 / Command Reference

```
tigeropen [全局选项 Global Options]
├── version                             # SDK 版本 Version
├── config                              # 配置管理 Configuration
│   ├── init                            # 交互式配置 Interactive setup
│   ├── show                            # 查看配置（脱敏）Show config (masked)
│   ├── set <KEY> <VALUE>               # 设置配置项 Set config value
│   └── path                            # 配置路径 Config path
├── quote                               # 行情数据 Market Data
│   ├── briefs <SYMBOLS...>             # 实时报价 Real-time quotes
│   ├── bars <SYMBOLS...>               # K 线 Candlestick
│   ├── timeline <SYMBOLS...>           # 分时 Intraday timeline
│   ├── ticks <SYMBOLS...>              # 逐笔 Tick data
│   ├── depth <SYMBOLS...>              # 盘口 Order book depth
│   ├── market-status                   # 市场状态 Market status
│   ├── symbols                         # 股票列表 Symbol list
│   ├── option                          # 期权 Options
│   │   ├── expirations <SYMBOL>        # 到期日 Expiration dates
│   │   ├── chain <SYMBOL> <EXPIRY>     # 期权链 Option chain
│   │   ├── briefs <IDENTIFIERS...>     # 期权报价 Option quotes
│   │   └── bars <IDENTIFIERS...>       # 期权 K 线 Option bars
│   ├── future                          # 期货 Futures
│   │   ├── exchanges                   # 交易所 Exchanges
│   │   ├── contracts <EXCHANGE>        # 合约列表 Contract list
│   │   ├── briefs <IDENTIFIERS...>     # 期货报价 Futures quotes
│   │   └── bars <IDENTIFIER>           # 期货 K 线 Futures bars
│   ├── capital                         # 资金 Capital
│   │   ├── flow <SYMBOL>               # 资金流向 Capital flow
│   │   └── distribution <SYMBOL>       # 资金分布 Capital distribution
│   └── fundamental                     # 基本面 Fundamental
│       ├── financial <SYMBOLS...>      # 财务报告 Financial reports
│       ├── dividend <SYMBOLS...>       # 分红 Dividends
│       └── earnings                    # 财报日历 Earnings calendar
├── trade                               # 交易 Trading
│   ├── order                           # 订单 Orders
│   │   ├── list                        # 订单列表 Order list
│   │   ├── get <ORDER_ID>              # 订单详情 Order details
│   │   ├── preview                     # 预览 Preview
│   │   ├── place                       # 下单 Place order
│   │   ├── modify <ORDER_ID>           # 改单 Modify order
│   │   └── cancel <ORDER_ID>           # 撤单 Cancel order
│   ├── position                        # 持仓 Positions
│   │   └── list                        # 持仓列表 Position list
│   └── transaction                     # 成交 Transactions
│       └── list                        # 成交记录 Transaction list
├── account                             # 账户 Account
│   ├── info                            # 账户信息 Account info
│   ├── assets                          # 资产 Assets
│   └── analytics                       # 分析 Analytics
└── push                                # 推送 Push (Streaming)
    ├── quote <SYMBOLS...>              # 行情推送 Quote streaming
    ├── order                           # 订单推送 Order streaming
    ├── position                        # 持仓推送 Position streaming
    └── asset                           # 资产推送 Asset streaming
```

---

## 常用场景 / Common Workflows

### 快速查看行情 / Quick Quote Check

```bash
tigeropen quote briefs AAPL TSLA GOOG --format json
```

### 查看持仓盈亏 / Check Position P&L

```bash
tigeropen trade position list --format table
tigeropen account assets
```

### 下单完整流程 / Full Order Workflow

```bash
# 1. 查看实时行情 / Check current price
tigeropen quote briefs AAPL

# 2. 预览订单 / Preview order
tigeropen trade order preview --symbol AAPL --action BUY --quantity 100 --limit-price 150

# 3. 下单 / Place order
tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150

# 4. 查看订单状态 / Check order status
tigeropen trade order list --symbol AAPL --status Submitted

# 5. 如需撤单 / Cancel if needed
tigeropen trade order cancel <ORDER_ID>
```

### 导出数据 / Export Data

```bash
# 导出 K 线到 CSV 文件 / Export bars to CSV file
tigeropen -f csv quote bars AAPL --period day --limit 100 > aapl_bars.csv

# 导出持仓为 JSON / Export positions as JSON
tigeropen -f json trade position list > positions.json

# 导出成交记录 / Export transactions
tigeropen -f csv trade transaction list --symbol AAPL > aapl_transactions.csv
```

### 实时监控 / Real-time Monitoring

```bash
# 监控行情（Ctrl+C 停止）/ Monitor quotes (Ctrl+C to stop)
tigeropen push quote AAPL TSLA

# 监控订单状态 / Monitor order updates
tigeropen push order
```

---

## 错误处理 / Error Handling

CLI 自动捕获 API 异常并显示错误代码和消息。
The CLI automatically catches API exceptions and displays error codes and messages.

```bash
# 启用详细日志查看完整调用栈 / Enable verbose for full stack trace
tigeropen -v quote briefs INVALID_SYMBOL
```

常见错误 / Common errors:

| 错误 Error | 说明 Description |
|-----------|-----------------|
| `API Error [4]` | 访问被拒绝（检查凭证/权限）Access forbidden (check credentials) |
| `API Error [5]` | 频率限制（稍后重试）Rate limited (retry later) |
| `Config file not found` | 运行 `tigeropen config init` 初始化配置 / Run config init |
| `No quote data found` | 无数据（检查标的代码/市场状态）No data (check symbol/market status) |

---

## 注意事项 / Notes

- CLI 复用 SDK 的 `TigerOpenClientConfig` 配置体系，支持配置文件、环境变量、`--config-path` 参数
  CLI reuses SDK's `TigerOpenClientConfig`, supports config file, env vars, and `--config-path`
- 下单/改单/撤单操作默认需要交互确认，`-y` 跳过
  Place/modify/cancel require confirmation by default; use `-y` to skip
- 推送命令使用 WebSocket 长连接，Ctrl+C 断开
  Push commands use WebSocket; Ctrl+C to disconnect
- 行情权限需单独购买，API 与 App 独立
  Quote permissions require separate purchase; API and App are independent
- 全部输出支持 `--format json` 用于管道和脚本处理
  All output supports `--format json` for piping and scripting
