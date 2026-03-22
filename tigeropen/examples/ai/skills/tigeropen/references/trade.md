
# Tiger Open API 交易 / Trading

> 中文 | English — 双语技能，代码通用。Bilingual skill with shared code examples.
> 官方文档 Docs: https://docs.itigerup.com/docs/place-order

## 初始化 / Initialize

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
trade_client = TradeClient(client_config=client_config)

# 获取管理的账户 / Get managed accounts
accounts = trade_client.get_managed_accounts()
# 返回 AccountProfile 列表: account, capability, status, account_type
```

---

## 合约 / Contracts

交易前必须获取合约对象。Contracts must be obtained before trading.

### 本地构造 / Local Construction

```python
from tigeropen.common.util.contract_utils import (
    stock_contract, option_contract, option_contract_by_symbol,
    future_contract, war_contract_by_symbol, iopt_contract_by_symbol,
    fund_contract, cc_contract
)

# 股票 / Stock
contract = stock_contract(symbol='AAPL', currency='USD')

# 港股 / HK Stock
contract = stock_contract(symbol='00700', currency='HKD')

# 期权 / Option
opt = option_contract_by_symbol(symbol='AAPL', expiry='20250829',
                                 strike=150.0, put_call='CALL', currency='USD')

# 期货 / Future
fut = future_contract(symbol='CL2509', currency='USD')

# 窝轮 / Warrant
war = war_contract_by_symbol(symbol='12345', currency='HKD')

# 牛熊证 / CBBC
iopt = iopt_contract_by_symbol(symbol='56789', currency='HKD')

# 基金 / Fund
fund = fund_contract(symbol='ARKK', currency='USD')

# 数字货币 / Crypto
cc = cc_contract(symbol='BTC/USD', currency='USD')
```

### 远程获取 / Remote Fetch

```python
# 单个合约 / Single contract
contract = trade_client.get_contract(symbol='AAPL', sec_type='STK')
contract = trade_client.get_contract(symbol='AAPL', sec_type='OPT',
                                      expiry='20250829', strike=150.0, put_call='CALL')

# 批量合约 / Multiple contracts
contracts = trade_client.get_contracts(symbols=['AAPL', 'TSLA'], sec_type='STK')

# 衍生品合约列表 / Derivative contracts
derivatives = trade_client.get_derivative_contracts(symbol='AAPL', sec_type='OPT')
```

### Contract 对象属性 / Contract Attributes

| 属性 Attribute | 说明 Description |
|---------------|-----------------|
| `symbol` | 代码 Symbol |
| `sec_type` | 证券类型 Security type (STK/OPT/FUT/WAR/IOPT) |
| `currency` | 货币 Currency |
| `exchange` | 交易所 Exchange |
| `name` | 名称 Name |
| `expiry` | 到期日 Expiry (options/futures) |
| `strike` | 行权价 Strike (options) |
| `put_call` | CALL/PUT (options) |
| `multiplier` | 乘数 Multiplier |
| `lot_size` | 每手股数 Lot size |
| `shortable` | 可否卖空 Shortable |
| `shortable_count` | 可卖空数量 Shortable count |
| `min_tick` | 最小价格变动 Min tick size |

---

## 下单 / Place Orders

### 限价单 LMT / Limit Order

```python
from tigeropen.common.util.order_utils import limit_order

order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)
trade_client.place_order(order)
print(f"Order ID: {order.id}")
```

### 市价单 MKT / Market Order

```python
from tigeropen.common.util.order_utils import market_order, market_order_by_amount

order = market_order(account=client_config.account, contract=contract,
                     action='BUY', quantity=100)
trade_client.place_order(order)

# 按金额下单(碎股) / By amount (fractional shares)
order = market_order_by_amount(account=client_config.account, contract=contract,
                               action='BUY', amount=5000)  # 买入 $5000 的股票
trade_client.place_order(order)
```

> 也有 `limit_order_by_amount` 用于按金额的限价单。
> There's also `limit_order_by_amount` for limit orders by amount.

### 止损单 STP / Stop Order

```python
from tigeropen.common.util.order_utils import stop_order

order = stop_order(account=client_config.account, contract=contract,
                   action='SELL', quantity=100, aux_price=140.0)
# aux_price = 触发价 / trigger price
trade_client.place_order(order)
```

### 止损限价单 STP_LMT / Stop Limit Order

```python
from tigeropen.common.util.order_utils import stop_limit_order

order = stop_limit_order(account=client_config.account, contract=contract,
                         action='SELL', quantity=100,
                         limit_price=139.0, aux_price=140.0)
# 价格到 aux_price 时触发，以 limit_price 限价委托
trade_client.place_order(order)
```

### 跟踪止损单 TRAIL / Trailing Stop

```python
from tigeropen.common.util.order_utils import trail_order

# 百分比跟踪 / Percentage trailing
order = trail_order(account=client_config.account, contract=contract,
                    action='SELL', quantity=100, trailing_percent=5.0)

# 金额跟踪 / Amount trailing
order = trail_order(account=client_config.account, contract=contract,
                    action='SELL', quantity=100, aux_price=3.0)
trade_client.place_order(order)
```

### 算法单 TWAP/VWAP / Algo Orders

```python
from tigeropen.common.util.order_utils import algo_order, algo_order_params

params = algo_order_params(start_time=1625097600000, end_time=1625184000000,
                            participation_rate=0.1)
order = algo_order(account=client_config.account, contract=contract,
                   action='BUY', quantity=1000, strategy='TWAP',  # 或 'VWAP'
                   algo_params=params)
trade_client.place_order(order)
```

### 附加订单(止盈止损) / Bracket Orders (Take Profit / Stop Loss)

```python
from tigeropen.common.util.order_utils import limit_order_with_legs, order_leg

# 推荐使用 limit_order_with_legs / Recommended: use limit_order_with_legs
legs = [
    order_leg(leg_type='PROFIT', price=170.0),              # 止盈 / Take profit
    order_leg(leg_type='LOSS', price=140.0),                 # 止损 / Stop loss
    # 也可用跟踪止损 / Or trailing stop loss:
    # order_leg(leg_type='LOSS', trailing_percent=5.0),
]
order = limit_order_with_legs(account=client_config.account, contract=contract,
                              action='BUY', quantity=100, limit_price=150.0,
                              order_legs=legs)
trade_client.place_order(order)
```

> 附加订单仅支持限价单作为主订单，最多2个 leg。子订单在主订单全部成交后自动生效。
> Bracket orders only support limit as primary, max 2 legs. Legs activate after primary is fully filled.

### order_leg 参数 / order_leg Parameters

| 参数 Parameter | 说明 Description |
|---------------|-----------------|
| `leg_type` | `PROFIT`(止盈) 或 `LOSS`(止损) |
| `price` | 触发价格 Trigger price |
| `limit_price` | 限价(可选) Limit price (optional) |
| `trailing_percent` | 跟踪止损百分比 Trailing percent |
| `trailing_amount` | 跟踪止损金额 Trailing amount |
| `quantity` | 数量(默认同主单) Quantity (default: same as primary) |

---

### 下单参数总览 / Order Parameters Overview

| 参数 Parameter | 说明 Description | 必填 Required |
|---------------|-----------------|--------------|
| `account` | 交易账户 Trading account | ✅ |
| `contract` | 合约对象 Contract | ✅ |
| `action` | `BUY` / `SELL` | ✅ |
| `quantity` | 数量 Quantity | ✅ |
| `limit_price` | 限价 Limit price | LMT/STP_LMT |
| `aux_price` | 触发价/跟踪金额 Trigger/trailing amount | STP/STP_LMT/TRAIL |
| `trailing_percent` | 跟踪止损百分比 Trailing percent | TRAIL |
| `time_in_force` | `DAY`/`GTC`(撤销前有效)/`GTD`(指定日期) | - |
| `outside_rth` | 盘前盘后 Pre/after hours (仅美股 US only) | - |
| `trading_session_type` | 交易时段 `TradingSessionType` 枚举值(PRE_RTH_POST/OVERNIGHT/RTH/FULL/HK_AUC/HK_CTS/HK_AUC_CTS) | - |
| `order_id` | 自定义订单ID Custom order ID | - |
| `user_mark` | 自定义标记 Custom mark | - |
| `quantity_scale` | 数量精度(碎股) Quantity scale (fractional) | - |
| `total_cash_amount` | 按金额下单 Order by amount | - |
| `expire_time` | GTD到期时间 GTD expire time | GTD |

### 各市场支持的订单类型 / Order Types by Market

| 订单类型 | 美股 US | 港股 HK | 新加坡 SG | 期货 Futures | 期权 Options |
|---------|---------|---------|----------|-------------|-------------|
| MKT 市价 | ✅ | ✅ | ✅ | ✅ | ✅ |
| LMT 限价 | ✅ | ✅ | ✅ | ✅ | ✅ |
| STP 止损 | ✅ | - | - | ✅ | ✅ |
| STP_LMT 止损限价 | ✅ | - | - | ✅ | ✅ |
| TRAIL 跟踪止损 | ✅ | - | - | - | - |
| TWAP/VWAP 算法 | ✅ | - | - | - | - |
| AL 竞价限价 | - | ✅ | - | - | - |
| AM 竞价市价 | - | ✅ | - | - | - |
| OCA 一撤全撤 | ✅ | ✅ | - | - | - |

### 特殊下单场景 / Special Order Scenarios

```python
# 盘前盘后 / Pre/after-hours (美股 US only)
order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)
order.outside_rth = True
trade_client.place_order(order)

# 夜盘(通宵) / Overnight trading (使用 TradingSessionType 枚举)
from tigeropen.common.consts import TradingSessionType
order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)
order.trading_session_type = TradingSessionType.OVERNIGHT.value
trade_client.place_order(order)
# TradingSessionType 可选值: PRE_RTH_POST, OVERNIGHT, RTH, FULL, HK_AUC, HK_CTS, HK_AUC_CTS

# GTC 订单 / Good Till Cancelled
order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)
order.time_in_force = 'GTC'
trade_client.place_order(order)

# 港股下单 / HK stock order (注意: 数量须为 lot_size 的整数倍，可通过 get_trade_metas 查询)
hk_contract = stock_contract(symbol='00700', currency='HKD')
order = limit_order(account=client_config.account, contract=hk_contract,
                    action='BUY', quantity=100, limit_price=350.0)
trade_client.place_order(order)

# 期货下单 / Futures order
fut_contract = future_contract(symbol='CL2509', currency='USD')
order = limit_order(account=client_config.account, contract=fut_contract,
                    action='BUY', quantity=1, limit_price=70.0)
trade_client.place_order(order)

# 价格修正工具 / Price correction utility
from tigeropen.common.util.price_util import PriceUtil
price_util = PriceUtil(trade_client)
corrected = price_util.correct_price(symbol='AAPL', price=150.123)
```

### 港股竞价单 / HK Auction Orders

```python
from tigeropen.common.util.order_utils import auction_limit_order, auction_market_order

# 竞价限价单 AL / Auction Limit Order
order = auction_limit_order(account=client_config.account, contract=hk_contract,
                            action='BUY', quantity=100, limit_price=350.0)
trade_client.place_order(order)

# 竞价市价单 AM / Auction Market Order
order = auction_market_order(account=client_config.account, contract=hk_contract,
                             action='BUY', quantity=100)
trade_client.place_order(order)
```

> 竞价单用于港股竞价时段(开盘竞价/收盘竞价)。`time_in_force` 支持 `DAY` 和 `OPG`。
> Auction orders for HK pre-opening/closing auction sessions. `time_in_force` supports `DAY` and `OPG`.

### OCA 订单(一撤全撤) / OCA Order (One-Cancels-All)

```python
from tigeropen.common.util.order_utils import oca_order, order_leg

# OCA 订单: 多个子订单中任一成交，其余自动撤销
# OCA order: when any leg fills, others are automatically cancelled
legs = [
    order_leg(leg_type='LMT', limit_price=160.0),   # 限价单
    order_leg(leg_type='STP', price=140.0),           # 止损单
]
order = oca_order(account=client_config.account, contract=contract,
                  action='SELL', order_legs=legs, quantity=100)
trade_client.place_order(order)
```

---

## 预览订单 / Preview Order

```python
preview = trade_client.preview_order(order)
# 返回保证金、佣金、验证信息 / Returns margin, commission, validation
# 属性: init_margin, maintain_margin, order_status, warning_text
```

## 修改订单 / Modify Order

```python
order = trade_client.get_order(id=123456789)
trade_client.modify_order(order,
                           quantity=200,
                           limit_price=155.0,
                           time_in_force='GTC',
                           outside_rth=True)
```

> 订单类型不可修改。仅 `Submitted` 或 `PartiallyFilled` 状态可改。
> Order type cannot be changed. Only Submitted/PartiallyFilled orders can be modified.

## 撤销订单 / Cancel Order

```python
trade_client.cancel_order(id=123456789)

# 批量撤销 / Batch cancel
for order in trade_client.get_open_orders():
    trade_client.cancel_order(id=order.id)
```

> 撤销为异步操作。使用 `id` (全局订单ID)。Cancellation is async. Use global order `id`.

---

## 查询订单 / Query Orders

```python
# 所有订单 / All orders
orders = trade_client.get_orders(limit=100)

# 待成交 / Open (pending) orders
open_orders = trade_client.get_open_orders()

# 已成交 / Filled orders (需指定时间，最多90天)
filled = trade_client.get_filled_orders(start_time='2025-01-01', end_time='2025-03-31')

# 已取消 / Cancelled orders
cancelled = trade_client.get_cancelled_orders()

# 指定订单 / Single order
order = trade_client.get_order(id=123456789)

# 条件筛选 / Filtered query
orders = trade_client.get_orders(
    symbol='AAPL', sec_type='STK', market='US',
    states=['Filled', 'Cancelled'],
    sort_by='latest_time',  # latest_time(默认) / limit_price
    limit=100,
    is_brief=False  # True: 精简模式 / brief mode
)

# 分页查询 / Pagination
orders = trade_client.get_orders(limit=20)
# 使用 page_token 翻页 / Use page_token for next page
if hasattr(orders, 'page_token') and orders.page_token:
    next_page = trade_client.get_orders(limit=20, page_token=orders.page_token)
```

### Order 对象属性 / Order Attributes

| 属性 Attribute | 说明 Description |
|---------------|-----------------|
| `id` | 全局订单ID Global order ID |
| `order_id` | 用户订单ID User order ID |
| `symbol` | 标的代码 Symbol |
| `sec_type` | 证券类型 Security type |
| `action` | BUY/SELL |
| `order_type` | MKT/LMT/STP/STP_LMT/TRAIL |
| `status` | 订单状态 Order status |
| `quantity` | 下单数量 Order quantity |
| `filled_quantity` | 成交数量 Filled quantity |
| `remaining_quantity` | 剩余数量 Remaining quantity |
| `limit_price` | 限价 Limit price |
| `aux_price` | 触发价 Aux price |
| `avg_fill_price` | 平均成交价 Average fill price |
| `trade_time` | 交易时间 Trade time |
| `time_in_force` | DAY/GTC/GTD |
| `outside_rth` | 是否盘前盘后 Outside RTH |
| `order_legs` | 附加订单列表 Attached orders |
| `algo_params` | 算法参数 Algo parameters |
| `user_mark` | 自定义标记 User mark |

### 订单状态 / Order Status

| 状态 Status | 说明 Description |
|------------|-----------------|
| `Initial` | 初始化 Created |
| `PendingSubmit` | 待提交 Pending submit |
| `Submitted` | 已提交 Submitted |
| `PartiallyFilled` | 部分成交 Partially filled |
| `Filled` | 全部成交 Fully filled |
| `Cancelled` | 已取消 Cancelled |
| `Inactive` | 已失效/拒绝 Rejected |
| `PendingCancel` | 待取消 Pending cancel |

---

## 成交记录 / Transaction Records

```python
# 按标的查询 / By symbol
transactions = trade_client.get_transactions(
    symbol='AAPL', sec_type='STK',
    start_time=1625097600000, end_time=1625184000000)

# 按订单查询 / By order ID
transactions = trade_client.get_transactions(order_id='123456789',
                                              start_time=1625097600000,
                                              end_time=1625184000000)
# 分页 / Pagination with page_token
```

---

## 账户资产 / Account Assets

### 综合资产(推荐) / Prime Assets (Recommended)

```python
assets = trade_client.get_prime_assets(base_currency='USD', consolidated=True)
print(f"总资产 Net: {assets.net_liquidation}")
print(f"可用资金 Available: {assets.available_funds}")
print(f"购买力 Buying Power: {assets.buying_power}")
print(f"现金 Cash: {assets.cash}")
print(f"保证金 Margin: {assets.maintain_margin}")
print(f"未实现盈亏 Unrealized PnL: {assets.unrealized_pnl}")
print(f"已实现盈亏 Realized PnL: {assets.realized_pnl}")
print(f"缓冲比率 Cushion: {assets.cushion}")

# 按板块 / By segment
# assets.segments 包含 S(证券), C(商品/期货), F(基金), D(数字货币) 板块
# 每个 Segment 有 cash_balance, cash_available_for_trade, net_liquidation 等
# 每个 Segment.currency_assets 包含各币种明细
```

### 全球资产 / Global Assets

```python
assets_list = trade_client.get_assets()
for a in assets_list:
    print(f"Buying Power: {a.buying_power}")
    print(f"Maintenance Margin: {a.maintenance_margin_requirement}")
    print(f"Unrealized PnL: {a.unrealized_pnl}")
```

### 资产分析 / Asset Analytics

```python
analytics = trade_client.get_analytics_asset(
    start_date='2025-01-01', end_date='2025-06-30',
    seg_type='SEC',  # SEC(证券)/FUT(期货)/ALL
    currency='USD')
# 返回 summary(pnl, pnl_percentage, annualized_return) 和 history(每日资产/盈亏)
```

---

## 持仓 / Positions

```python
from tigeropen.common.consts import SecurityType, Market

# 所有持仓 / All positions
positions = trade_client.get_positions()

# 按类型 / By security type
positions = trade_client.get_positions(sec_type=SecurityType.STK)
for p in positions:
    print(f"{p.contract.symbol}: qty={p.qty}, cost={p.average_cost}, "
          f"price={p.market_price}, value={p.market_value}, "
          f"pnl={p.unrealized_pnl}, salable={p.salable_qty}")

# 按市场 / By market
us_pos = trade_client.get_positions(sec_type=SecurityType.STK, market=Market.US)
hk_pos = trade_client.get_positions(sec_type=SecurityType.STK, market=Market.HK)

# 按代码 / By symbol
aapl_pos = trade_client.get_positions(sec_type=SecurityType.STK, symbol='AAPL')

# 期权持仓 / Option positions
opt_pos = trade_client.get_positions(sec_type=SecurityType.OPT)

# 期货持仓 / Futures positions
fut_pos = trade_client.get_positions(sec_type=SecurityType.FUT)
```

### Position 对象属性 / Position Attributes

| 属性 Attribute | 说明 Description |
|---------------|-----------------|
| `contract` | 合约对象 Contract |
| `qty` / `quantity` | 持仓数量 Quantity |
| `average_cost` | 持仓均价 Average cost |
| `market_price` | 最新市场价 Market price |
| `market_value` | 市值 Market value |
| `unrealized_pnl` | 未实现盈亏 Unrealized P&L |
| `realized_pnl` | 已实现盈亏 Realized P&L |
| `salable_qty` | 可卖数量 Salable quantity |

---

## 预估可交易数量 / Estimate Tradable Quantity

```python
result = trade_client.get_estimate_tradable_quantity(
    symbol='AAPL', sec_type='STK', order_type='LMT',
    action='BUY', limit_price=150.0)
# 返回: tradable_quantity(可交易), financing_quantity(融资可交易), position_quantity(持仓数量)
```

## 资金划转 / Fund Transfer (Between Segments)

```python
# 查询可划转金额 / Query transferable amount
available = trade_client.get_segment_fund_available(
    from_segment='SEC', to_segment='FUT', currency='USD')

# 划转 / Transfer
trade_client.transfer_segment_fund(
    from_segment='SEC', to_segment='FUT', amount=10000.0, currency='USD')

# 取消划转 / Cancel transfer
trade_client.cancel_segment_fund(id='transfer_id')

# 划转历史 / Transfer history
history = trade_client.get_segment_fund_history()
```

## 出入金记录 / Deposit/Withdrawal Records

```python
records = trade_client.get_funding_history(
    start_time='2025-01-01', end_time='2025-06-30', currency='USD')
```

## 外汇下单 / Forex Order

```python
from tigeropen.common.consts import SegmentType

trade_client.place_forex_order(
    seg_type=SegmentType.SEC,  # SEC(证券板块) 或 FUT(期货板块)
    source_currency='USD', target_currency='HKD', source_amount=10000.0)
```

---

## 交易时间参考 / Trading Hours Reference

| 市场 Market | 时段 Session | 时间 Time (当地/Local) |
|-------------|-------------|----------------------|
| 美股 US | 盘前 Pre-market | 04:00-09:30 ET |
| | 常规 Regular | 09:30-16:00 ET |
| | 盘后 After-hours | 16:00-20:00 ET |
| | 夜盘 Overnight | 20:00-04:00 ET |
| 港股 HK | 竞价 Pre-opening | 09:00-09:30 |
| | 上午 Morning | 09:30-12:00 |
| | 下午 Afternoon | 13:00-16:00 |
| | 收盘竞价 Closing | 16:00-16:10 |
| 新加坡 SG | 全天 Full | 09:00-17:16 |

> 更多交易规则见 / More: https://docs.itigerup.com/docs/trade-rules

---

## 注意事项 / Notes

- `place_order` 返回成功仅表示提交成功，需查询确认成交。可检查 `order.id` 和 `order.status` / Success only means submitted; check `order.id` and `order.status`
- 市价单(MKT)和止损单(STP)不支持盘前盘后 / MKT and STP don't support pre/after-hours
- 同一证券不能同时持有多头和空头 / Cannot hold long and short simultaneously
- 下单前建议 `preview_order` / Use preview before placing real orders
- 交易佣金与 App 一致，无额外费用 / Trading fees same as app
- 已成交订单查询需指定时间范围，最多90天 / Filled orders require time range, max 90 days
- 港股下单数量须为 `lot_size` 的整数倍，可通过 `get_trade_metas` 查询 / HK orders must be multiples of `lot_size`
- `quantity_scale` 用于碎股精度控制 / `quantity_scale` controls fractional share precision
- `adjust_limit` 参数可用于价格自动修正 / `adjust_limit` for automatic price adjustment
