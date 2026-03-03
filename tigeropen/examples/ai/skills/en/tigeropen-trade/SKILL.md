---
name: tigeropen-trade
description: Tiger Brokers OpenAPI trading skill. Place stock/futures orders (market, limit, stop, trailing stop, algo orders), modify orders, cancel orders, preview orders, query orders, account assets, and positions. Use this skill when users need to place trades, manage orders, or view account assets and positions.
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: en_US
---

# Tiger Open API Trading

## Initialize Trade Client

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
trade_client = TradeClient(client_config=client_config)
accounts = trade_client.get_managed_accounts()
```

## Contracts

Contracts must be obtained before placing orders.

```python
from tigeropen.common.util.contract_utils import (
    stock_contract, option_contract_by_symbol, future_contract
)

# Stock contract
contract = stock_contract(symbol='AAPL', currency='USD')
contract = trade_client.get_contract(symbol='AAPL', sec_type='STK')

# Option contract
opt = option_contract_by_symbol(symbol='AAPL', expiry='20250829',
                                 strike=150.0, put_call='CALL', currency='USD')

# Futures contract
fut = future_contract(symbol='CL2509', currency='USD')
```

## Place Orders

### Limit Order (LMT)

```python
from tigeropen.common.util.order_utils import limit_order

order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)
trade_client.place_order(order)
print(f"Order ID: {order.id}")
```

### Market Order (MKT)

```python
from tigeropen.common.util.order_utils import market_order

order = market_order(account=client_config.account, contract=contract,
                     action='BUY', quantity=100)
trade_client.place_order(order)
```

### Stop Order (STP)

```python
from tigeropen.common.util.order_utils import stop_order

order = stop_order(account=client_config.account, contract=contract,
                   action='SELL', quantity=100, aux_price=140.0)
trade_client.place_order(order)
```

### Stop Limit Order (STP_LMT)

```python
from tigeropen.common.util.order_utils import stop_limit_order

order = stop_limit_order(account=client_config.account, contract=contract,
                         action='SELL', quantity=100,
                         limit_price=139.0, aux_price=140.0)
trade_client.place_order(order)
```

### Trailing Stop (TRAIL)

```python
from tigeropen.common.util.order_utils import trail_order

order = trail_order(account=client_config.account, contract=contract,
                    action='SELL', quantity=100,
                    trailing_percent=5.0)  # or use aux_price for amount
trade_client.place_order(order)
```

### Algo Orders (TWAP/VWAP)

```python
from tigeropen.common.util.order_utils import algo_order, algo_order_params

params = algo_order_params(start_time=1625097600000, end_time=1625184000000)
order = algo_order(account=client_config.account, contract=contract,
                   action='BUY', quantity=1000, strategy='TWAP', algo_params=params)
trade_client.place_order(order)
```

### Order Parameters

| Parameter | Description |
|-----------|-------------|
| `account` | Trading account ID |
| `contract` | Contract object |
| `action` | `BUY` or `SELL` |
| `quantity` | Order quantity |
| `limit_price` | Limit price (required for LMT/STP_LMT) |
| `aux_price` | Trigger price (STP/STP_LMT) or trailing amount (TRAIL) |
| `trailing_percent` | Trailing stop percentage |
| `time_in_force` | `DAY` / `GTC` (good till cancelled) / `GTD` (good till date) |
| `outside_rth` | Allow pre/after-hours trading (US stocks only) |

## Bracket Orders (Take Profit / Stop Loss)

```python
from tigeropen.common.util.order_utils import limit_order, order_leg

order = limit_order(account=client_config.account, contract=contract,
                    action='BUY', quantity=100, limit_price=150.0)
order.order_legs = [
    order_leg(leg_type='PROFIT', price=170.0),  # Take profit
    order_leg(leg_type='LOSS', price=140.0),     # Stop loss
]
trade_client.place_order(order)
```

> Bracket orders only support limit orders as the primary order.

## Preview Order

```python
preview = trade_client.preview_order(order)
# Returns margin calculations, estimated commission, validation results
```

## Modify Order

```python
order = trade_client.get_order(id=123456789)
trade_client.modify_order(order, quantity=200, limit_price=155.0,
                          time_in_force='GTC', outside_rth=True)
```

> Order type cannot be changed. Only Submitted or PartiallyFilled orders can be modified.

## Cancel Order

```python
trade_client.cancel_order(id=123456789)

# Batch cancel
for order in trade_client.get_open_orders():
    trade_client.cancel_order(id=order.id)
```

> Cancellation is asynchronous. Use `id` (global order ID).

## Query Orders

```python
orders = trade_client.get_orders(limit=100)
open_orders = trade_client.get_open_orders()
filled = trade_client.get_filled_orders(start_time='2025-01-01', end_time='2025-06-30')
cancelled = trade_client.get_cancelled_orders()
order = trade_client.get_order(id=123456789)

# Filtered
orders = trade_client.get_orders(symbol='AAPL', sec_type='STK', market='US',
                                  states=['Filled', 'Cancelled'], limit=100)

# Transaction details
transactions = trade_client.get_transactions(symbol='AAPL',
                                              start_time=1625097600000,
                                              end_time=1625184000000)
```

## Account Assets

```python
# Comprehensive (recommended)
assets = trade_client.get_prime_assets(base_currency='USD', consolidated=True)
print(f"Net Liquidation: {assets.net_liquidation}")
print(f"Available Funds: {assets.available_funds}")

# Basic
assets = trade_client.get_assets()
for a in assets:
    print(f"Buying Power: {a.buying_power}, Margin: {a.maintenance_margin_requirement}")

# Analytics
analytics = trade_client.get_analytics_asset(
    start_date='2025-01-01', end_date='2025-06-30',
    seg_type='SEC', currency='USD')  # SEC/FUT/ALL
```

**Key fields**: net_liquidation (total assets), available_funds, buying_power (up to 4x intraday), excess_liquidity, cushion

## Positions

```python
from tigeropen.common.consts import SecurityType, Market

positions = trade_client.get_positions(sec_type=SecurityType.STK)
for p in positions:
    print(f"{p.contract.symbol}: qty={p.qty}, cost={p.average_cost}, "
          f"value={p.market_value}, pnl={p.unrealized_pnl}")

us_pos = trade_client.get_positions(sec_type=SecurityType.STK, market=Market.US)
opt_pos = trade_client.get_positions(sec_type=SecurityType.OPT)
```

## Order Status Reference

| Status | Value | Description |
|--------|-------|-------------|
| Initial | `Initial` | Order created |
| Submitted | `Submitted` | Awaiting execution |
| Partially Filled | `PartiallyFilled` | Partial fill |
| Filled | `Filled` | Fully executed |
| Cancelled | `Cancelled` | Cancelled |
| Inactive | `Inactive` | Rejected by system |

## Notes

- `place_order` success only means submission; query to confirm execution
- Market (MKT) and stop (STP) orders do not support pre/after-hours
- Cannot hold long and short positions simultaneously in same security
- Use `preview_order` before placing real orders
- Trading commissions match the app; no additional API fees
