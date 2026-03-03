---
name: tigeropen-option
description: Tiger Brokers OpenAPI options trading skill. Get option chains, expiration dates, option quotes, Greeks values. Place single-leg and multi-leg combo orders (vertical spreads, straddles, strangles, etc.). Use this skill when users need option data, Greeks analysis, option strategies, or placing option orders.
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: en_US
---

# Tiger Open API Options Trading

> The `quote_client` and `trade_client` in this skill are initialized as follows:
> ```python
> from tigeropen.tiger_open_config import TigerOpenClientConfig
> from tigeropen.quote.quote_client import QuoteClient
> from tigeropen.trade.trade_client import TradeClient
> client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
> quote_client = QuoteClient(client_config=client_config)
> trade_client = TradeClient(client_config=client_config)
> ```

## Get Option Expirations

```python
expirations = quote_client.get_option_expirations(symbols=['AAPL'], market='US')
print(expirations)  # List of expiration dates
```

## Get Option Chain

```python
from tigeropen.quote.domain.filter import OptionFilter

# Basic
chain = quote_client.get_option_chain(symbol='AAPL', expiry='2025-08-29', market='US')

# With filters and Greeks
option_filter = OptionFilter(
    implied_volatility_min=0.3, implied_volatility_max=0.8,
    delta_min=0.2, delta_max=0.8,
    open_interest_min=100,
    in_the_money=True
)
chain = quote_client.get_option_chain(
    symbol='AAPL', expiry='2025-08-29',
    option_filter=option_filter,
    return_greek_value=True,  # delta/gamma/theta/vega/rho
    market='US')
```

**Filter fields**: implied_volatility, delta, gamma, theta, vega, open_interest, volume, in_the_money

## HK Options

HK option underlying symbols differ from stock codes; get mapping first:

```python
hk_symbols = quote_client.get_option_symbols(market='HK')  # e.g. 00700 -> TCH.HK
chain = quote_client.get_option_chain(symbol='TCH.HK', expiry='2025-06-18', market='HK')
```

## Option Quotes

```python
# Real-time
briefs = quote_client.get_option_briefs(identifiers=['AAPL  250829C00150000'])

# K-lines
bars = quote_client.get_option_bars(identifiers=['AAPL  250829C00150000'], period='day')

# Depth
depth = quote_client.get_option_depth(identifiers=['AAPL  250829C00150000'], market='US')

# Trade ticks
ticks = quote_client.get_option_trade_ticks(identifiers=['AAPL  250829C00150000'])

# Timeline
timeline = quote_client.get_option_timeline(identifiers=['AAPL  250829C00150000'])
```

**Option symbol format**:
- US: `'AAPL  250829C00150000'` (underlying + YYMMDD + C/P + strike*1000)
- HK: `'TCH.HK 230616C00550000'`

## Option Contracts

```python
from tigeropen.common.util.contract_utils import option_contract_by_symbol

opt = option_contract_by_symbol(symbol='AAPL', expiry='20250829',
                                 strike=150.0, put_call='CALL', currency='USD')

opt = trade_client.get_contract(symbol='AAPL', sec_type='OPT',
                                 expiry='20250829', strike=150.0, put_call='CALL')
```

## Single-leg Option Order

```python
from tigeropen.common.util.order_utils import limit_order

order = limit_order(account=client_config.account, contract=opt,
                    action='BUY', quantity=1, limit_price=5.0)
trade_client.place_order(order)
```

> 1 option contract = 100 shares of underlying

## Multi-leg Combo Strategies

```python
from tigeropen.common.util.order_utils import combo_order, contract_leg

# Bull Call Spread
legs = [
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=145.0, put_call='CALL', action='BUY', ratio=1),
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=155.0, put_call='CALL', action='SELL', ratio=1),
]
order = combo_order(account=client_config.account, legs=legs,
                    combo_type='VERTICAL', action='BUY',
                    quantity=1, order_type='LMT', limit_price=3.0)
trade_client.place_order(order)
```

### Combo Strategy Types

| ComboType | Strategy | Description |
|-----------|----------|-------------|
| `VERTICAL` | Vertical spread | Same expiry, different strikes |
| `STRADDLE` | Straddle | Same strike, same expiry, call + put |
| `STRANGLE` | Strangle | Different strikes, same expiry, call + put |
| `CALENDAR` | Calendar spread | Same strike, different expiries |
| `DIAGONAL` | Diagonal spread | Different strikes, different expiries |
| `COVERED` | Covered call | Long stock + short call |
| `PROTECTIVE` | Protective put | Long stock + long put |
| `SYNTHETIC` | Synthetic | Synthetic long/short |
| `CUSTOM` | Custom | Custom combination |

## Query Option Positions

```python
from tigeropen.common.consts import SecurityType

opt_positions = trade_client.get_positions(sec_type=SecurityType.OPT)
for p in opt_positions:
    print(f"{p.contract.symbol}: qty={p.qty}, cost={p.average_cost}, "
          f"value={p.market_value}, pnl={p.unrealized_pnl}")
```

## Notes

- HK options require symbol mapping via `get_option_symbols`
- Each option contract typically represents 100 shares
- Greeks available via `return_greek_value=True`
- All legs in a combo must share the same underlying
