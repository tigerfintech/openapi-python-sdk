---
name: tigeropen-quickstart
description: 老虎证券 OpenAPI Python SDK 快速入门。安装 SDK、配置认证信息（tiger_id/private_key/account）、创建客户端、连接模拟或真实交易环境。当用户需要接入老虎 API、初始化 SDK 配置、设置开发环境时使用此技能。
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: zh_CN
---

# Tiger Open API Python SDK 快速入门

## 概述

老虎量化开放平台 Python SDK（tigeropen）为个人开发者和机构用户提供交易和行情数据接口，支持美股、港股、A股、新加坡市场的股票、期权、期货等品种的行情查询和交易操作。

- 官方文档: https://docs.itigerup.com/docs/intro
- GitHub: https://github.com/tigerbrokers/openapi-python-sdk
- SDK 版本: 3.5.4 | Python 支持: 3.8 - 3.13

## 安装

```bash
pip install tigeropen

# 验证安装
python -c "import tigeropen; print(tigeropen.__VERSION__)"
```

## 前置条件

1. 在老虎证券完成开户并入金
2. 访问 https://developer.itigerup.com/ 激活 API 权限
3. 获取 `tiger_id` 和 RSA 私钥文件

## 配置客户端

创建配置文件 `tiger_openapi_config.properties`，包含 tiger_id、private_key、account 等信息：

```properties
tiger_id=your_tiger_id
private_key_path=/path/to/private_key.pem
account=your_account
```

通过 `props_path` 加载配置：

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
```

> 也支持环境变量（`TIGEROPEN_TIGER_ID` / `TIGEROPEN_PRIVATE_KEY` / `TIGEROPEN_ACCOUNT`）和代码直接赋值，优先级：代码参数 > 环境变量 > 配置文件 > 默认值。

## 创建客户端

```python
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

# 行情客户端（建议模块级别创建一次并复用）
quote_client = QuoteClient(client_config=client_config)

# 交易客户端
trade_client = TradeClient(client_config=client_config)
```

## 模拟交易环境

```python
client_config = TigerOpenClientConfig(sandbox_debug=True)
client_config.account = 'your_paper_account'
```

## 完整入门示例

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.consts import Market, BarPeriod
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

# 1. 加载配置
client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')

# 2. 创建客户端
quote_client = QuoteClient(client_config=client_config)
trade_client = TradeClient(client_config=client_config)

# 3. 查看市场状态
status = quote_client.get_market_status(Market.US)
for s in status:
    print(f"市场: {s.market}, 状态: {s.trading_status}")

# 4. 获取实时行情
briefs = quote_client.get_stock_briefs(['AAPL', 'TSLA'])
for b in briefs:
    print(f"{b.symbol}: 最新价={b.latest_price}, 涨跌幅={b.change_percent}%")

# 5. 获取K线
bars = quote_client.get_bars(['AAPL'], period=BarPeriod.DAY, limit=30)
print(bars.tail())

# 6. 查看账户
assets = trade_client.get_prime_assets(base_currency='USD')
print(f"总资产: {assets.net_liquidation}, 可用资金: {assets.available_funds}")
```

## 核心模块

| 模块 | 用途 |
|------|------|
| `QuoteClient` | 行情数据（实时行情、K线、深度、期权链等） |
| `TradeClient` | 交易操作（下单、撤单、查持仓、查资产等） |
| `PushClient` | 实时推送（行情推送、订单变动、持仓变动等） |
| `TigerOpenClientConfig` | 配置管理 |

## 常用枚举

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

## 注意事项

- 认证方式为 RSA-2048 签名，所有请求用私钥签名
- `QuoteClient` 应创建一次并复用，避免重复抢占行情权限
- 行情权限需单独购买，API 与 App 行情权限独立
- 机构用户需额外设置 `secret_key`
