---
name: tigeropen-trade
description: 老虎证券 OpenAPI 交易操作技能。股票/期货下单（市价单、限价单、止损单、跟踪止损单、算法单）、修改订单、撤销订单、预览订单、查询订单、查询账户资产和持仓。当用户需要下单交易、管理订单、查看账户资产或持仓信息时使用此技能。
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: zh_CN
---

# Tiger Open API 交易操作

## 初始化交易客户端

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
trade_client = TradeClient(client_config=client_config)
accounts = trade_client.get_managed_accounts()  # 获取管理的账户列表
```

## 合约

交易前必须获取合约对象。

```python
from tigeropen.common.util.contract_utils import (
    stock_contract, option_contract_by_symbol, future_contract
)

# 股票合约
contract = stock_contract(symbol='AAPL', currency='USD')

# 也可通过 TradeClient 获取
contract = trade_client.get_contract(symbol='AAPL', sec_type='STK')
contracts = trade_client.get_contracts(symbols=['AAPL', 'TSLA'], sec_type='STK')

# 期权合约
opt = option_contract_by_symbol(symbol='AAPL', expiry='20250829',
                                 strike=150.0, put_call='CALL', currency='USD')
opt = trade_client.get_contract(symbol='AAPL', sec_type='OPT',
                                 expiry='20250829', strike=150.0, put_call='CALL')

# 期货合约
fut = future_contract(symbol='CL2509', currency='USD')
```

## 下单

### 限价单 (LMT)

```python
from tigeropen.common.util.order_utils import limit_order

order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)
trade_client.place_order(order)
print(f"订单ID: {order.id}")
```

### 市价单 (MKT)

```python
from tigeropen.common.util.order_utils import market_order

order = market_order(account=client_config.account, contract=contract,
                     action='BUY', quantity=100)
trade_client.place_order(order)
```

### 止损单 (STP)

```python
from tigeropen.common.util.order_utils import stop_order

order = stop_order(account=client_config.account, contract=contract,
                   action='SELL', quantity=100, aux_price=140.0)
trade_client.place_order(order)
```

### 止损限价单 (STP_LMT)

```python
from tigeropen.common.util.order_utils import stop_limit_order

order = stop_limit_order(account=client_config.account, contract=contract,
                         action='SELL', quantity=100,
                         limit_price=139.0, aux_price=140.0)
trade_client.place_order(order)
```

### 跟踪止损单 (TRAIL)

```python
from tigeropen.common.util.order_utils import trail_order

order = trail_order(account=client_config.account, contract=contract,
                    action='SELL', quantity=100,
                    trailing_percent=5.0)  # 或用 aux_price 指定金额
trade_client.place_order(order)
```

### 算法订单 (TWAP/VWAP)

```python
from tigeropen.common.util.order_utils import algo_order, algo_order_params

params = algo_order_params(start_time=1625097600000, end_time=1625184000000)
order = algo_order(account=client_config.account, contract=contract,
                   action='BUY', quantity=1000, strategy='TWAP', algo_params=params)
trade_client.place_order(order)
```

### 下单参数说明

| 参数 | 说明 |
|------|------|
| `account` | 交易账户ID |
| `contract` | 合约对象 |
| `action` | `BUY`(买入) / `SELL`(卖出) |
| `quantity` | 下单数量 |
| `limit_price` | 限价（LMT/STP_LMT 必填） |
| `aux_price` | 触发价（STP/STP_LMT）或回撤金额（TRAIL） |
| `trailing_percent` | 跟踪止损百分比 |
| `time_in_force` | `DAY`(当日) / `GTC`(撤销前有效) / `GTD`(指定日期) |
| `outside_rth` | 是否允许盘前盘后（仅美股） |

## 附加订单（止盈止损）

```python
from tigeropen.common.util.order_utils import limit_order, order_leg

order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)

# 附加止盈止损
order.order_legs = [
    order_leg(leg_type='PROFIT', price=170.0),  # 止盈
    order_leg(leg_type='LOSS', price=140.0),     # 止损
]
trade_client.place_order(order)
```

> 附加订单仅支持限价单作为主订单，子订单在主订单全部成交后自动生效。

## 预览订单

```python
preview = trade_client.preview_order(order)
# 返回保证金计算、预估佣金、验证结果
```

## 修改订单

```python
order = trade_client.get_order(id=123456789)
trade_client.modify_order(order, quantity=200, limit_price=155.0,
                          time_in_force='GTC', outside_rth=True)
```

> 订单类型不可修改，仅 `Submitted` 或 `PartiallyFilled` 状态可修改。

## 撤销订单

```python
trade_client.cancel_order(id=123456789)

# 批量撤销
for order in trade_client.get_open_orders():
    trade_client.cancel_order(id=order.id)
```

> 撤销为异步操作，建议使用 `id`（全局订单ID）。

## 查询订单

```python
# 所有订单
orders = trade_client.get_orders(limit=100)

# 待成交
open_orders = trade_client.get_open_orders()

# 已成交（需指定时间范围，最多90天）
filled = trade_client.get_filled_orders(start_time='2025-01-01', end_time='2025-06-30')

# 已取消
cancelled = trade_client.get_cancelled_orders()

# 指定订单
order = trade_client.get_order(id=123456789)

# 条件筛选
orders = trade_client.get_orders(symbol='AAPL', sec_type='STK', market='US',
                                  states=['Filled', 'Cancelled'], limit=100)

# 成交明细
transactions = trade_client.get_transactions(symbol='AAPL',
                                              start_time=1625097600000,
                                              end_time=1625184000000)
```

## 查询账户资产

```python
# 综合资产（推荐）
assets = trade_client.get_prime_assets(base_currency='USD', consolidated=True)
print(f"总资产: {assets.net_liquidation}")
print(f"可用资金: {assets.available_funds}")
print(f"现金: {assets.cash}")

# 基础资产
assets = trade_client.get_assets()
for a in assets:
    print(f"购买力: {a.buying_power}, 保证金: {a.maintenance_margin_requirement}")
    print(f"未实现盈亏: {a.unrealized_pnl}, 已实现盈亏: {a.realized_pnl}")

# 资产分析
analytics = trade_client.get_analytics_asset(
    start_date='2025-01-01', end_date='2025-06-30',
    seg_type='SEC', currency='USD')  # SEC/FUT/ALL
```

**资产核心字段**:
- `net_liquidation` - 总资产(净清算值) = 现金 + 股票 + 期权
- `available_funds` - 可用资金 = equity_with_loan - 初始保证金
- `buying_power` - 购买力（保证金账户日内最多4倍）
- `excess_liquidity` - 剩余流动性
- `cushion` - 缓冲比率 = excess_liquidity / net_liquidation

## 查询持仓

```python
from tigeropen.common.consts import SecurityType, Market

positions = trade_client.get_positions(sec_type=SecurityType.STK)
for p in positions:
    print(f"{p.contract.symbol}: 数量={p.qty}, 均价={p.average_cost}, "
          f"市值={p.market_value}, 盈亏={p.unrealized_pnl}")

# 按市场
us_pos = trade_client.get_positions(sec_type=SecurityType.STK, market=Market.US)

# 按代码
aapl_pos = trade_client.get_positions(sec_type=SecurityType.STK, symbol='AAPL')

# 期权持仓
opt_pos = trade_client.get_positions(sec_type=SecurityType.OPT)
```

## 订单状态对照

| 状态 | 值 | 说明 |
|------|------|------|
| 初始 | `Initial` | 订单已创建 |
| 已提交 | `Submitted` | 已提交等待成交 |
| 部分成交 | `PartiallyFilled` | 部分数量已成交 |
| 全部成交 | `Filled` | 全部成交 |
| 已取消 | `Cancelled` | 已撤销 |
| 已失效 | `Inactive` | 被系统拒绝 |

## 注意事项

- `place_order` 返回成功仅表示提交成功，需查询确认成交状态
- 市价单(MKT)和止损单(STP)不支持盘前盘后
- 同一证券不能同时持有多头和空头
- 下单前建议先 `preview_order` 验证
- 交易佣金与 App 一致，无额外 API 费用
