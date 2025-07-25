# TigerOpen MCP 服务器快速入门指南

此 MCP（Model Context Protocol）服务器封装了 TigerOpen SDK 的行情和交易 API，使您能够通过简单的接口调用轻松访问 Tiger API 的功能。

## 安装和配置

### 前提条件

- Python 3.10 或更高版本
- 已安装 TigerOpen Python SDK
- 有效的 Tiger 账户和 API 凭证

### 安装依赖

```bash
pip install "mcp[cli]" tigeropen
```

### 配置

在使用之前，您需要在 `server.py` 文件中更新您的 Tiger API 凭证：

```python
client_config = get_client_config(
    private_key_path='your_private_key_path',  # 私钥文件路径
    tiger_id='your_tiger_id',                 # Tiger ID
    account='your_account'                    # 交易账户
)
```

您可以参考项目根目录下的 `client_config.py.template` 文件了解如何配置。

## 启动 MCP 服务器

使用以下命令启动 MCP 服务器：

```bash
mcp dev server.py
```

服务器成功启动后，您将看到类似以下输出：

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:5000
```

## 服务器功能

MCP 服务器提供了以下主要功能：

### 行情接口

- **市场和符号**
  - `get_market_status`: 获取指定市场的状态
  - `get_symbols`: 获取市场的所有交易符号列表
  - `get_symbol_names`: 获取市场的所有交易符号及其名称
  - `get_trading_calendar`: 获取交易日历

- **股票行情**
  - `get_briefs`: 获取股票摘要信息
  - `get_stock_details`: 获取股票详情信息
  - `get_bars`: 获取K线数据
  - `get_timeline`: 获取分时数据
  - `get_trade_ticks`: 获取逐笔成交数据
  - `get_depth_quote`: 获取深度行情

- **期权相关**
  - `get_option_expirations`: 获取期权到期日列表
  - `get_option_chain`: 获取期权链
  - `get_option_briefs`: 获取期权最新行情
  - `get_option_bars`: 获取期权K线数据

- **期货相关**
  - `get_future_exchanges`: 获取期货交易所列表
  - `get_future_contracts`: 获取交易所下的可交易合约
  - `get_future_bars`: 获取期货K线数据
  - `get_future_brief`: 获取期货最新行情

- **财务数据**
  - `get_corporate_dividend`: 获取公司派息数据
  - `get_corporate_split`: 获取公司拆合股数据
  - `get_financial_daily`: 获取日级的财务数据
  - `get_industry_list`: 获取行业列表
  - `get_stock_industry`: 获取股票的行业

### 交易接口

- **账户信息**
  - `get_managed_accounts`: 获取管理的账号列表
  - `get_assets`: 获取账户资产信息
  - `get_positions`: 获取账户持仓情况
  - `get_prime_assets`: 获取Prime账户资产信息

- **订单管理**
  - `get_contracts`: 获取合约信息
  - `place_order`: 下单
  - `preview_order`: 预览订单（不实际下单）
  - `cancel_order`: 取消订单
  - `get_orders`: 获取所有订单列表
  - `get_open_orders`: 获取未成交订单列表
  - `get_filled_orders`: 获取已成交订单列表

- **资金管理**
  - `get_segment_fund_available`: 获取可用的分段资金
  - `get_segment_fund_history`: 获取分段资金历史
  - `transfer_segment_fund`: 转移分段资金

## 调用示例

### 从 MCP CLI 调用

您可以使用 MCP CLI 工具直接与服务器交互：

```bash
# 检查服务器状态
mcp call --url http://localhost:5000 server://status

# 获取美股市场状态
mcp call --url http://localhost:5000 get_market_status market=US

# 获取特定股票的行情
mcp call --url http://localhost:5000 get_briefs symbols=["AAPL","MSFT"]
```

### 从 Python 代码调用

```python
from mcp.client import McpClient

# 创建 MCP 客户端
client = McpClient("http://localhost:5000")

# 获取市场状态
status = client.call("get_market_status", market="US")
print(status)

# 获取股票行情
briefs = client.call("get_briefs", symbols=["AAPL", "MSFT"])
print(briefs)

# 下单
order = client.call("place_order", 
                   symbol="AAPL", 
                   action="BUY", 
                   order_type="LMT", 
                   quantity=1, 
                   limit_price=150.0)
print(order)
```

## 常见问题解答

### Q: 如何查看所有可用的 API?
**A**: 在服务器启动后，访问 http://localhost:5000/docs 查看完整的 API 文档。

### Q: 如何处理错误?
**A**: 所有 API 调用返回的结果中，如果包含 `"error"` 键，则表示发生错误。错误信息将在该键的值中提供。

### Q: 如何修改服务器端口?
**A**: 启动时指定端口：`mcp dev server.py --port 8000`

### Q: 如何使用不同的配置文件?
**A**: 修改 `server.py` 中的配置加载代码，指向您自己的配置文件。

## 更多资源

- [TigerOpen API 文档](https://quant.itigerup.com/openapi/zh/python/overview/intro.html)
- [MCP 框架文档](https://microsoft.github.io/mcp/)