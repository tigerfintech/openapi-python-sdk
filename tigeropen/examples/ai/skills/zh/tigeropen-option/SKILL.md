---
name: tigeropen-option
description: 老虎证券 OpenAPI 期权交易技能。获取期权链、期权到期日、期权行情、希腊字母值，下期权单腿和多腿组合订单（牛市价差、跨式、宽跨式等策略）。当用户需要查询期权数据、分析期权Greeks、构建期权策略、下期权订单时使用此技能。
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: zh_CN
---

# Tiger Open API 期权交易

> 本技能中的 `quote_client` 和 `trade_client` 通过以下方式初始化：
> ```python
> from tigeropen.tiger_open_config import TigerOpenClientConfig
> from tigeropen.quote.quote_client import QuoteClient
> from tigeropen.trade.trade_client import TradeClient
> client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
> quote_client = QuoteClient(client_config=client_config)
> trade_client = TradeClient(client_config=client_config)
> ```

## 获取期权到期日

```python
expirations = quote_client.get_option_expirations(symbols=['AAPL'], market='US')
print(expirations)  # 返回到期日列表
```

## 获取期权链

```python
from tigeropen.quote.domain.filter import OptionFilter

# 基础期权链
chain = quote_client.get_option_chain(symbol='AAPL', expiry='2025-08-29', market='US')

# 带筛选和希腊字母
option_filter = OptionFilter(
    implied_volatility_min=0.3, implied_volatility_max=0.8,
    delta_min=0.2, delta_max=0.8,
    open_interest_min=100,
    in_the_money=True
)
chain = quote_client.get_option_chain(
    symbol='AAPL', expiry='2025-08-29',
    option_filter=option_filter,
    return_greek_value=True,  # 返回 delta/gamma/theta/vega/rho
    market='US')
```

**筛选条件**: implied_volatility, delta, gamma, theta, vega, open_interest, volume, in_the_money

## 港股期权

港股期权标的代码与股票代码不同，需先获取映射：

```python
# 获取映射 (如 00700 -> TCH.HK)
hk_symbols = quote_client.get_option_symbols(market='HK')

# 使用映射后的代码
chain = quote_client.get_option_chain(symbol='TCH.HK', expiry='2025-06-18', market='HK')
```

## 期权行情

```python
# 实时行情
briefs = quote_client.get_option_briefs(identifiers=['AAPL  250829C00150000'])

# K线
bars = quote_client.get_option_bars(identifiers=['AAPL  250829C00150000'], period='day')

# 深度行情
depth = quote_client.get_option_depth(identifiers=['AAPL  250829C00150000'], market='US')

# 逐笔成交
ticks = quote_client.get_option_trade_ticks(identifiers=['AAPL  250829C00150000'])

# 分时
timeline = quote_client.get_option_timeline(identifiers=['AAPL  250829C00150000'])
```

**期权代码格式**:
- 美股: `'AAPL  250829C00150000'` (标的 + 到期日YYMMDD + C/P + 行权价*1000)
- 港股: `'TCH.HK 230616C00550000'`

## 期权合约

```python
from tigeropen.common.util.contract_utils import option_contract_by_symbol

opt = option_contract_by_symbol(
    symbol='AAPL', expiry='20250829',
    strike=150.0, put_call='CALL', currency='USD')

# 或通过 TradeClient
opt = trade_client.get_contract(symbol='AAPL', sec_type='OPT',
                                 expiry='20250829', strike=150.0, put_call='CALL')
```

## 单腿期权下单

```python
from tigeropen.common.util.order_utils import limit_order

order = limit_order(account=client_config.account, contract=opt,
                    action='BUY', quantity=1, limit_price=5.0)
trade_client.place_order(order)
```

> 期权1张合约 = 100股标的

## 多腿组合策略

```python
from tigeropen.common.util.order_utils import combo_order, contract_leg

# 牛市看涨价差 (Bull Call Spread)
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

### 组合策略类型

| ComboType | 策略 | 说明 |
|-----------|------|------|
| `VERTICAL` | 垂直价差 | 同到期日不同行权价 |
| `STRADDLE` | 跨式 | 同行权价同到期日的看涨+看跌 |
| `STRANGLE` | 宽跨式 | 不同行权价同到期日的看涨+看跌 |
| `CALENDAR` | 日历价差 | 同行权价不同到期日 |
| `DIAGONAL` | 对角线价差 | 不同行权价不同到期日 |
| `COVERED` | 备兑 | 持有标的+卖出看涨 |
| `PROTECTIVE` | 保护性 | 持有标的+买入看跌 |
| `SYNTHETIC` | 合成 | 合成多/空头 |
| `CUSTOM` | 自定义 | 自定义组合 |

## 查询期权持仓

```python
from tigeropen.common.consts import SecurityType

opt_positions = trade_client.get_positions(sec_type=SecurityType.OPT)
for p in opt_positions:
    print(f"{p.contract.symbol}: 数量={p.qty}, 均价={p.average_cost}, "
          f"市值={p.market_value}, 盈亏={p.unrealized_pnl}")
```

## 注意事项

- 港股期权需通过 `get_option_symbols` 获取代码映射
- 期权每张合约通常代表100股标的股票
- 希腊字母通过 `return_greek_value=True` 获取
- 组合策略下单时需确保所有 leg 的标的一致
