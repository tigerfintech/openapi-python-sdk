
# Tiger Open API Python SDK

> 中文 | English — 本技能双语编写，代码示例通用。This skill is bilingual with shared code examples.

## 概述 / Overview

老虎量化开放平台 Python SDK (tigeropen) 为个人和机构用户提供交易与行情 API，支持美股、港股、A股、新加坡、澳洲市场的股票、期权、期货等品种。
The Tiger Open Platform Python SDK (tigeropen) provides trading and market data APIs for stocks, options, futures across US, HK, China A-shares, Singapore, and Australia markets.

- 官方文档 / Docs: https://docs.itigerup.com/docs/intro
- GitHub: https://github.com/tigerbrokers/openapi-python-sdk
- SDK Version: 3.5.4 | Python: 3.8 - 3.13

### 支持的市场和品种 / Supported Markets

| 市场 Market | 股票/ETF | 期权 Options | 期货 Futures | 窝轮/牛熊证 Warrants/CBBC |
|-------------|---------|-------------|-------------|--------------------------|
| 美国 US     | ✅      | ✅          | ✅          | -                        |
| 香港 HK     | ✅      | ✅          | ✅          | ✅                       |
| 新加坡 SG   | ✅      | -           | ✅          | -                        |
| 澳洲 AU    | ✅      | -           | -           | -                        |
| A股 CN      | ✅      | -           | -           | -                        |

### 支持的订单类型 / Supported Order Types

市价单 MKT, 限价单 LMT, 止损单 STP, 止损限价单 STP_LMT, 跟踪止损单 TRAIL, 附加订单(止盈止损), 算法单 TWAP/VWAP

## 安装 / Installation

```bash
pip install tigeropen

# 验证 / Verify
python -c "import tigeropen; print(tigeropen.__VERSION__)"
```

## 前置条件 / Prerequisites

1. 开通老虎证券账户并入金 / Open a Tiger Brokers account and fund it
2. 访问 https://developer.itigerup.com/ 激活 API 权限 / Activate API permissions
3. 获取 `tiger_id` 和 RSA 私钥文件 / Obtain `tiger_id` and RSA private key file

> 机构用户通过机构后台注册 / Institutional users register via institutional backend

## 账户类型 / Account Types

| 类型 Type | 说明 Description | 推荐 |
|-----------|-----------------|------|
| 综合账户 Comprehensive (Live) | 支持所有市场、保证金交易、全品种。**推荐** | ✅ |
| 全球账户 Global (Live) | 旧账户类型，不支持窝轮/牛熊证 | - |
| 模拟账户 Paper | 测试用，支持美股/港股/A股/期权，无需真实资金 | 测试推荐 |

## 配置 / Configuration

### 方式一：配置文件 / Config File

创建 `tiger_openapi_config.properties`:

```properties
tiger_id=your_tiger_id
private_key_path=/path/to/private_key.pem
account=your_account
```

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
```

### 方式二：环境变量 / Environment Variables

```bash
export TIGEROPEN_TIGER_ID="your_tiger_id"
export TIGEROPEN_PRIVATE_KEY="your_private_key_content"  # 私钥内容，非路径
export TIGEROPEN_ACCOUNT="your_account"
```

```python
client_config = TigerOpenClientConfig()  # 自动读取环境变量
```

### 方式三：代码赋值 / Code Assignment

```python
client_config = TigerOpenClientConfig()
client_config.tiger_id = 'your_tiger_id'
client_config.private_key = 'your_private_key_content'
client_config.account = 'your_account'
```

> 优先级 Priority: 代码参数 code > 环境变量 env > 配置文件 config > 默认值 defaults

### 机构用户 / Institutional Users

```python
client_config.secret_key = 'your_secret_key'
# 香港机构需额外设置 / HK institutional needs:
# client_config.token = 'tbhk_2fa_token'
```

## 创建客户端 / Create Clients

```python
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

# 行情客户端 / Quote client (建议模块级创建一次并复用 / create once and reuse)
quote_client = QuoteClient(client_config=client_config)
# is_grab_permission 默认 True，自动抢占行情权限
# 多设备同账号时仅最后抢占的设备收到行情

# 交易客户端 / Trade client
trade_client = TradeClient(client_config=client_config)
```

## 模拟交易 / Paper Trading

```python
client_config = TigerOpenClientConfig(sandbox_debug=True)
client_config.account = 'your_paper_account'
# 模拟账户支持美股/港股/A股/期权
```

## 完整入门示例 / Complete Quickstart

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.consts import Market, BarPeriod
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

# 1. 加载配置 / Load config
client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')

# 2. 创建客户端 / Create clients
quote_client = QuoteClient(client_config=client_config)
trade_client = TradeClient(client_config=client_config)

# 3. 查看市场状态 / Check market status
status = quote_client.get_market_status(Market.US)
for s in status:
    print(f"Market: {s.market}, Status: {s.trading_status}, Open: {s.open_time}")

# 4. 获取实时行情 / Get real-time quotes
briefs = quote_client.get_stock_briefs(['AAPL', 'TSLA'])
for b in briefs:
    print(f"{b.symbol}: price={b.latest_price}, change={b.change_percent}%")

# 5. 获取K线 / Get K-line data
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=30)
print(bars.tail())

# 6. 查看账户 / Check account
assets = trade_client.get_prime_assets(base_currency='USD')
print(f"Net Liquidation: {assets.net_liquidation}, Available: {assets.available_funds}")

# 7. 查看持仓 / Check positions
positions = trade_client.get_positions()
for p in positions:
    print(f"{p.contract.symbol}: qty={p.qty}, pnl={p.unrealized_pnl}")
```

## 核心模块 / Core Modules

| 模块 Module | 用途 Purpose | 导入路径 Import |
|-------------|-------------|----------------|
| `TigerOpenClientConfig` | 配置管理 / Config | `tigeropen.tiger_open_config` |
| `QuoteClient` | 行情数据 / Market data | `tigeropen.quote.quote_client` |
| `TradeClient` | 交易操作 / Trading | `tigeropen.trade.trade_client` |
| `PushClient` | 实时推送 / Real-time push | `tigeropen.push.push_client` |

## 枚举参考 / Enum Reference

```python
from tigeropen.common.consts import (
    Market,        # ALL, US, HK, CN, SG, AU
    SecurityType,  # STK, OPT, FUT, WAR, IOPT, CASH, FUND, MLEG, CC
    Currency,      # USD, HKD, CNH, SGD, AUD
    Language,      # zh_CN, zh_TW, en_US
    OrderType,     # MKT, LMT, STP, STP_LMT, TRAIL, TWAP, VWAP
    OrderStatus,   # Initial, PendingSubmit, Submitted, PartiallyFilled, Filled, Cancelled, Inactive, PendingCancel
    BarPeriod,     # DAY, WEEK, MONTH, YEAR, ONE_MINUTE, THREE_MINUTES, FIVE_MINUTES, TEN_MINUTES,
                   # FIFTEEN_MINUTES, HALF_HOUR, FORTY_FIVE_MINUTES, ONE_HOUR, TWO_HOURS, THREE_HOURS, FOUR_HOURS, SIX_HOURS
    QuoteRight,    # BR(前复权/forward), NR(不复权/none)
    TradingSession,  # PreMarket, Regular, AfterHours
    TimeInForce,   # DAY, GTC, GTD
)
```

### SecurityType 证券类型

| 值 Value | 说明 Description |
|----------|-----------------|
| `STK` | 股票/ETF Stock |
| `OPT` | 期权 Option |
| `FUT` | 期货 Future |
| `WAR` | 窝轮 Warrant |
| `IOPT` | 牛熊证 CBBC/Inline Warrant |
| `FUND` | 基金 Fund |
| `CASH` | 外汇 Forex |
| `CC` | 数字货币 Cryptocurrency |
| `MLEG` | 组合 Multi-leg Combo |

### OrderStatus 订单状态

| 状态 Status | 说明 Description |
|------------|-----------------|
| `Initial` | 初始化 / Created |
| `PendingSubmit` | 待提交 / Pending submit |
| `Submitted` | 已提交 / Submitted, awaiting fill |
| `PartiallyFilled` | 部分成交 / Partially filled |
| `Filled` | 全部成交 / Fully filled |
| `Cancelled` | 已取消 / Cancelled |
| `Inactive` | 已失效 / Rejected by system |
| `PendingCancel` | 待取消 / Pending cancel |

### BarPeriod K线周期

`day`, `week`, `month`, `year`, `1min`, `3min`, `5min`, `10min`, `15min`, `30min`, `45min`, `60min`, `2hour`, `3hour`, `4hour`, `6hour`

### Market Scanner 相关枚举

```python
from tigeropen.common.consts import (
    StockField,       # stockField: Change, ChangeRate, LatestPrice, Volume, Amount, TurnoverRate, FloatShare, FloatMarketValue...
    AccumulateField,  # accumulateField: ChangeRate, Amount, Volume
    FinancialField,   # financialField: TotalRevenue, NetIncome, EpsDiluted, ROE, PE_TTM, PB...
    MultiTagField,    # multiTagField: HasOption, IsETF, IndustryCode, ExchangeCode
    SortDirection,    # ASC, DESC
)
```

## 核心对象参考 / Key Object Reference

### PortfolioAccount 资产对象 (get_prime_assets)

| 属性 Attribute | 说明 Description |
|---------------|-----------------|
| `net_liquidation` | 总资产/净清算值 Net liquidation value |
| `available_funds` | 可用资金 Available funds |
| `buying_power` | 购买力 Buying power |
| `cash` | 现金 Cash balance |
| `excess_liquidity` | 剩余流动性 Excess liquidity |
| `cushion` | 缓冲比率 Cushion ratio |
| `init_margin` | 初始保证金 Initial margin |
| `maintain_margin` | 维持保证金 Maintenance margin |
| `unrealized_pnl` | 未实现盈亏 Unrealized P&L |
| `realized_pnl` | 已实现盈亏 Realized P&L |
| `gross_position_value` | 总持仓价值 Gross position value |

### Position 持仓对象

| 属性 Attribute | 说明 Description |
|---------------|-----------------|
| `contract` | 合约对象 Contract object |
| `qty` / `quantity` | 持仓数量 Position quantity |
| `average_cost` | 持仓均价 Average cost |
| `market_price` | 市场价 Market price |
| `market_value` | 市值 Market value |
| `unrealized_pnl` | 未实现盈亏 Unrealized P&L |
| `realized_pnl` | 已实现盈亏 Realized P&L |
| `salable_qty` | 可卖数量 Salable quantity |

### Order 订单对象

| 属性 Attribute | 说明 Description |
|---------------|-----------------|
| `id` | 全局订单ID Global order ID |
| `order_id` | 用户订单ID User order ID |
| `symbol` | 标的代码 Symbol |
| `action` | BUY/SELL |
| `order_type` | 订单类型 Order type |
| `status` | 订单状态 Order status |
| `quantity` | 下单数量 Order quantity |
| `filled_quantity` | 成交数量 Filled quantity |
| `limit_price` | 限价 Limit price |
| `aux_price` | 触发价/回撤价 Aux price |
| `avg_fill_price` | 均价 Average fill price |
| `trade_time` | 交易时间 Trade time |
| `time_in_force` | 有效期 Time in force |
| `outside_rth` | 是否盘前盘后 Outside RTH |
| `order_legs` | 附加订单 Attached orders |

### Contract 合约对象

| 属性 Attribute | 说明 Description |
|---------------|-----------------|
| `symbol` | 代码 Symbol |
| `sec_type` | 证券类型 Security type |
| `currency` | 货币 Currency |
| `exchange` | 交易所 Exchange |
| `name` | 名称 Name |
| `expiry` | 到期日(期权/期货) Expiry |
| `strike` | 行权价(期权) Strike |
| `put_call` | 看涨/看跌(期权) Put/Call |
| `multiplier` | 乘数 Multiplier |
| `lot_size` | 每手股数 Lot size |
| `shortable` | 可否卖空 Shortable |
| `shortable_count` | 可卖空数量 Shortable count |
| `min_tick` | 最小价格变动 Min tick size |

## 行情权限与限制 / Quote Permissions & Limits

### 权限类型 / Permission Types

- 美股L1 `usQuoteBasic` (Nasdaq Basic), 美股L2 `usStockQuoteLv2Totalview` (40档深度)
- 港股BMP (手动刷新), 港股L2 `hkStockQuoteLv2` (10档深度, 自动推送)
- 美期权 `usOptionQuote`, 港期权L2 (随港期货L2)
- 期货L2: CBOE, HKFE, SGX, OSE

### 配额限制 / Quota Limits (取决于资产/交易量等级)

| 等级 | 历史行情(股票/期货/期权) | 订阅(标准/深度) |
|------|------------------------|----------------|
| 基础 | 20/10/10 次 | 20/10 个 |
| 高级($50K+) | 100/50/100 | 100/50 |
| 顶级($1M+) | 2000/200/2000 | 2000/500 |

> 行情权限需单独购买，API 与 App 独立。详见 https://docs.itigerup.com/docs/permission

## 请求频率限制 / Rate Limits

60秒滚动窗口 / 60-second rolling window:

| 限制 Limit | 接口 APIs |
|-----------|----------|
| 120/min (高频) | 下单/撤单/改单/查询订单, 实时行情, 分时, 逐笔, 期权行情, 期货行情 |
| 60/min (中频) | 期权链, 深度行情, 合约, K线, 资产, 持仓, 成交 |
| 10/min (低频) | 行情权限, 市场状态, 代码列表, 股票详情, 期货交易所 |

> 超频返回 code=4/5。持续超频可能导致账户限制。Rate limit exceeded returns code=4/5.

## 错误代码 / Error Codes

| 代码 Code | 说明 Description |
|-----------|-----------------|
| 0 | 成功 Success |
| 1 | 服务器错误 Server error |
| 2 | 网络超时 Network timeout |
| 4 | 访问拒绝 Access forbidden (IP白名单/签名失败/订阅超限) |
| 5 | 频率限制 Rate limit (HTTP 429) |
| 1000 | 通用参数错误 Common param error |
| 1010 | 业务参数错误 Business param error |
| 1100 | 全球账户交易错误 Global account trade error |
| 1200 | 综合账户交易错误 Comprehensive account trade error |
| 1300 | 模拟账户交易错误 Paper account trade error |
| 2100-2300 | 行情数据错误 Market data error |
| 4000 | 权限不足 Permission denied |
| 4001 | 被新连接踢出 Kicked out by new connection |

### 频率限制恢复 / Rate Limit Recovery

```python
import time

def safe_api_call(func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if 'rate limit' in str(e).lower() or '429' in str(e):
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

## 常见问题 / FAQ

### 私钥格式 / Private Key Format

Python SDK 使用 **PKCS#1** 格式 (以 `-----BEGIN RSA PRIVATE KEY-----` 开头)。
如果是 PKCS#8 格式（`BEGIN PRIVATE KEY`），需转换：

```bash
openssl rsa -in pkcs8_key.pem -out pkcs1_key.pem
```

### SSL/证书问题 / SSL Issues

```python
# macOS 运行 / Run on macOS:
# /Applications/Python\ 3.x/Install\ Certificates.command

# 或设置环境变量 / Or set env:
import ssl
ssl._create_default_https_context = ssl._create_unverified_context  # 仅调试 / debug only
```

### 推送连接问题 / Push Connection Issues

- 同一 tiger_id 只能有一个推送连接，新连接会踢掉旧连接
- Only one push connection per tiger_id; new connection kicks the old one
- 断线后 PushClient 自动重连 / Auto-reconnects after disconnection

### Windows 编码问题 / Windows Encoding

```python
# Windows 终端中文乱码
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

## 注意事项 / Notes

- 认证使用 RSA-2048 签名 / Authentication uses RSA-2048 signatures
- `QuoteClient` 应创建一次并复用 / Create once and reuse
- 行情权限需单独购买 / Quote permissions require separate purchase
- 交易佣金与 App 一致，无额外 API 费用 / Trading fees same as app
- 官方 QQ/Telegram 支持群 / Official support groups: https://t.me/TigerBrokersAPISupport
