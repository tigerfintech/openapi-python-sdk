
# Tiger Open API 期权 / Options Trading

> 中文 | English — 双语技能。Bilingual skill.
> 官方文档 Docs: https://docs.itigerup.com/docs/quote-option

## 初始化 / Initialize

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
quote_client = QuoteClient(client_config=client_config)
trade_client = TradeClient(client_config=client_config)
```

---

## 期权到期日 / Option Expirations

```python
expirations = quote_client.get_option_expirations(symbols=['AAPL'], market='US')
# 返回 DataFrame / Returns DataFrame
# 列: symbol, option_symbol, date, timestamp, period_tag
# period_tag: "m"=月度期权(monthly), "w"=周期权(weekly)
# 也支持 symbols=['AAPL', 'TSLA'] 批量查询
```

## 期权链 / Option Chain

```python
from tigeropen.quote.domain.filter import OptionFilter

# 基础期权链 / Basic chain
chain = quote_client.get_option_chain(symbol='AAPL', expiry='2025-08-29', market='US')
# 返回 DataFrame，包含 call/put 的行权价、价格、成交量、持仓量等

# 带筛选和希腊字母 / With filters and Greeks
option_filter = OptionFilter(
    implied_volatility_min=0.3,
    implied_volatility_max=0.8,
    delta_min=0.2,
    delta_max=0.8,
    gamma_min=0.005,
    theta_max=-0.05,
    open_interest_min=100,
    volume_min=50,
    in_the_money=True
)
chain = quote_client.get_option_chain(
    symbol='AAPL', expiry='2025-08-29',
    option_filter=option_filter,
    return_greek_value=True,  # 返回 delta/gamma/theta/vega/rho
    market='US')
```

### OptionFilter 筛选字段 / Filter Fields

| 字段 Field | 说明 Description |
|-----------|-----------------|
| `implied_volatility_min/max` | 隐含波动率范围 IV range |
| `delta_min/max` | Delta 范围 |
| `gamma_min/max` | Gamma 范围 |
| `theta_min/max` | Theta 范围 |
| `vega_min/max` | Vega 范围 |
| `open_interest_min/max` | 持仓量范围 Open interest |
| `volume_min/max` | 成交量范围 Volume |
| `in_the_money` | 是否实值 In the money (True/False) |

---

## 港股期权 / HK Options

港股期权标的代码与股票代码不同，需先映射。
HK option underlying symbols differ from stock codes; map first.

```python
# 获取映射 / Get mapping (e.g. 00700 -> TCH.HK)
hk_symbols = quote_client.get_option_symbols(market='HK')

# 使用映射后的代码 / Use mapped symbol
expirations = quote_client.get_option_expirations(symbols=['TCH.HK'], market='HK')
chain = quote_client.get_option_chain(symbol='TCH.HK', expiry='2025-06-18', market='HK')
```

---

## 期权行情 / Option Quotes

```python
# 实时行情 / Real-time quotes
briefs = quote_client.get_option_briefs(identifiers=['AAPL  250829C00150000'])
# 属性: symbol, latest_price, bid_price, ask_price, volume, open_interest, change, change_percent
# Greeks: delta, gamma, theta, vega, rho, implied_volatility
# 额外属性: mid_price, mark_price, pre_mark_price, rates_bonds

# K线 / K-lines (支持周期: day, 1min, 5min, 30min, 60min)
bars = quote_client.get_option_bars(identifiers=['AAPL  250829C00150000'], period='day')
# 可选参数: sort_dir (SortDirection.ASC/DESC), limit, begin_time, end_time

# 深度行情 / Depth quotes
depth = quote_client.get_option_depth(identifiers=['AAPL  250829C00150000'], market='US')

# 逐笔成交 / Trade ticks
ticks = quote_client.get_option_trade_ticks(identifiers=['AAPL  250829C00150000'])

# 分时 / Timeline (支持 US 和 HK 市场 / Supports US and HK markets)
timeline = quote_client.get_option_timeline(identifiers=['AAPL  250829C00150000'])
# HK 期权: quote_client.get_option_timeline(identifiers=['TCH.HK250828C00610000'], market='HK')
```

### 期权代码格式 / Option Symbol Format

- 美股 US: `'AAPL  250829C00150000'`
  - 格式: `标的` + 空格填充至6位 + `YYMMDD` + `C/P` + 行权价*1000(8位)
  - Format: symbol padded to 6 chars + YYMMDD + C/P + strike*1000 (8 digits)
- 港股 HK: `'TCH.HK 230616C00550000'`
  - 注意使用映射后的代码 / Use mapped symbol

---

## 期权分析 / Option Analysis

```python
from tigeropen.common.consts import OptionAnalysisPeriod

# 基础用法(默认52周) / Basic usage (default 52-week)
analysis = quote_client.get_option_analysis(symbols=['AAPL'])

# 指定分析周期 / Specify analysis period
analysis = quote_client.get_option_analysis(
    symbols=['AAPL'],
    period=OptionAnalysisPeriod.TWENTY_SIX_WEEK)

# 每个标的不同周期 / Per-symbol periods
analysis = quote_client.get_option_analysis(
    symbols=[
        'AAPL',  # 使用默认周期
        {'symbol': 'TSLA', 'period': '26week'},  # 指定26周
    ])

# 返回 List[OptionAnalysis]，属性:
# - symbol: 标的代码
# - implied_vol_30_days: 30日隐含波动率
# - his_volatility: 历史波动率
# - iv_his_v_ratio: IV/HV 比率
# - call_put_ratio: 看涨/看跌比率
# - iv_metric: IVMetric 对象，包含:
#     - period: 分析周期
#     - percentile: IV 百分位
#     - rank: IV 排名
```

### OptionAnalysisPeriod 分析周期

| 周期 Period | 值 Value | 说明 Description |
|------------|---------|-----------------|
| `THREE_YEAR` | `3year` | 3年 / 3 years |
| `FIFTY_TWO_WEEK` | `52week` | 52周(1年，默认) / 52 weeks (default) |
| `TWENTY_SIX_WEEK` | `26week` | 26周(6个月) / 26 weeks |
| `THIRTEEN_WEEK` | `13week` | 13周(3个月) / 13 weeks |

---

## 期权合约 / Option Contracts

```python
from tigeropen.common.util.contract_utils import option_contract_by_symbol

# 本地构造 / Local construction
opt = option_contract_by_symbol(
    symbol='AAPL', expiry='20250829',
    strike=150.0, put_call='CALL', currency='USD')

# 远程获取 / Remote fetch
opt = trade_client.get_contract(
    symbol='AAPL', sec_type='OPT',
    expiry='20250829', strike=150.0, put_call='CALL')
```

---

## 单腿期权下单 / Single-leg Option Order

```python
from tigeropen.common.util.order_utils import limit_order

# 买入看涨期权 / Buy call
order = limit_order(account=client_config.account, contract=opt,
                    action='BUY', quantity=1, limit_price=5.0)
trade_client.place_order(order)

# 卖出看跌期权 / Sell put
put_contract = option_contract_by_symbol(
    symbol='AAPL', expiry='20250829', strike=140.0, put_call='PUT', currency='USD')
order = limit_order(account=client_config.account, contract=put_contract,
                    action='SELL', quantity=1, limit_price=3.0)
trade_client.place_order(order)
```

> 期权1张合约 = 100股标的。1 option contract = 100 shares of underlying.

---

## 多腿组合策略 / Multi-leg Combo Strategies

```python
from tigeropen.common.util.order_utils import combo_order, contract_leg
```

### 牛市看涨价差 / Bull Call Spread (VERTICAL)

```python
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

### 跨式策略 / Straddle (STRADDLE)

```python
legs = [
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=150.0, put_call='CALL', action='BUY', ratio=1),
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=150.0, put_call='PUT', action='BUY', ratio=1),
]
order = combo_order(account=client_config.account, legs=legs,
                    combo_type='STRADDLE', action='BUY',
                    quantity=1, order_type='LMT', limit_price=8.0)
trade_client.place_order(order)
```

### 宽跨式策略 / Strangle (STRANGLE)

```python
legs = [
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=160.0, put_call='CALL', action='BUY', ratio=1),
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=140.0, put_call='PUT', action='BUY', ratio=1),
]
order = combo_order(account=client_config.account, legs=legs,
                    combo_type='STRANGLE', action='BUY',
                    quantity=1, order_type='LMT', limit_price=5.0)
trade_client.place_order(order)
```

### 日历价差 / Calendar Spread (CALENDAR)

```python
legs = [
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=150.0, put_call='CALL', action='SELL', ratio=1),  # 近月卖
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20251219',
                 strike=150.0, put_call='CALL', action='BUY', ratio=1),   # 远月买
]
order = combo_order(account=client_config.account, legs=legs,
                    combo_type='CALENDAR', action='BUY',
                    quantity=1, order_type='LMT', limit_price=2.0)
trade_client.place_order(order)
```

### 对角线价差 / Diagonal Spread (DIAGONAL)

```python
legs = [
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=155.0, put_call='CALL', action='SELL', ratio=1),
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20251219',
                 strike=145.0, put_call='CALL', action='BUY', ratio=1),
]
order = combo_order(account=client_config.account, legs=legs,
                    combo_type='DIAGONAL', action='BUY',
                    quantity=1, order_type='LMT', limit_price=5.0)
trade_client.place_order(order)
```

### 备兑策略 / Covered Call (COVERED)

```python
legs = [
    contract_leg(symbol='AAPL', sec_type='STK', action='BUY', ratio=100),  # 买100股
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=160.0, put_call='CALL', action='SELL', ratio=1),     # 卖1张call
]
order = combo_order(account=client_config.account, legs=legs,
                    combo_type='COVERED', action='BUY',
                    quantity=1, order_type='LMT', limit_price=145.0)
trade_client.place_order(order)
```

### 保护性看跌 / Protective Put (PROTECTIVE)

```python
legs = [
    contract_leg(symbol='AAPL', sec_type='STK', action='BUY', ratio=100),
    contract_leg(symbol='AAPL', sec_type='OPT', expiry='20250829',
                 strike=140.0, put_call='PUT', action='BUY', ratio=1),
]
order = combo_order(account=client_config.account, legs=legs,
                    combo_type='PROTECTIVE', action='BUY',
                    quantity=1, order_type='LMT', limit_price=152.0)
trade_client.place_order(order)
```

### 组合策略类型总览 / Combo Strategy Types

| ComboType | 策略 Strategy | 说明 Description |
|-----------|--------------|-----------------|
| `VERTICAL` | 垂直价差 | 同到期日不同行权价 Same expiry, different strikes |
| `STRADDLE` | 跨式 | 同行权价同到期日 Call+Put Same strike & expiry |
| `STRANGLE` | 宽跨式 | 不同行权价同到期日 Call+Put Different strikes, same expiry |
| `CALENDAR` | 日历价差 | 同行权价不同到期日 Same strike, different expiries |
| `DIAGONAL` | 对角线价差 | 不同行权价不同到期日 Different strikes & expiries |
| `COVERED` | 备兑 | 持有股票+卖Call Long stock + short call |
| `PROTECTIVE` | 保护性 | 持有股票+买Put Long stock + long put |
| `SYNTHETIC` | 合成 | 合成多/空头 Synthetic long/short |
| `CUSTOM` | 自定义 | 自定义组合 Custom combination |

### contract_leg 参数 / contract_leg Parameters

| 参数 Parameter | 说明 Description | 必填 |
|---------------|-----------------|------|
| `symbol` | 标的代码 Symbol | ✅ |
| `sec_type` | `OPT` / `STK` | ✅ |
| `expiry` | 到期日 YYYYMMDD (期权) | OPT |
| `strike` | 行权价 Strike (期权) | OPT |
| `put_call` | `CALL` / `PUT` (期权) | OPT |
| `action` | `BUY` / `SELL` | ✅ |
| `ratio` | 比率 Ratio (STK用100, OPT用1) | ✅ |

---

## 查询期权持仓 / Query Option Positions

```python
from tigeropen.common.consts import SecurityType

opt_positions = trade_client.get_positions(sec_type=SecurityType.OPT)
for p in opt_positions:
    c = p.contract
    print(f"{c.symbol} {c.expiry} {c.strike} {c.put_call}: "
          f"qty={p.qty}, cost={p.average_cost}, value={p.market_value}, pnl={p.unrealized_pnl}")
```

---

## 期权计算工具 / Option Calculator Tools

> 需安装 `pip install quantlib==1.40`

### 期权定价与希腊字母 / Option Pricing & Greeks

```python
from tigeropen.examples.option_helpers.helpers import (
    FDAmericanDividendOptionHelper,   # 美式期权(美股/港股/ETF) American options
    FDEuropeanDividendOptionHelper,   # 欧式期权(指数期权) European options
)

# 计算期权价格 / Calculate option price
helper = FDAmericanDividendOptionHelper(
    option_type='CALL',    # CALL/PUT
    expiry='2025-08-29',   # 到期日
    settlement='2025-03-18',  # 结算日
    strike=150.0,          # 行权价
    underlying=155.0,      # 标的价格
    rate=0.05,             # 无风险利率
    volatility=0.25,       # 波动率
)
result = helper.calculate()
# result: npv(期权价格), delta, gamma, theta, vega, rho

# 从期权价格反算隐含波动率 / Calculate implied volatility from price
helper = FDAmericanDividendOptionHelper(
    option_type='CALL', expiry='2025-08-29', settlement='2025-03-18',
    strike=150.0, underlying=155.0, rate=0.05,
    option_price=8.5,  # 期权市场价格
)
iv = helper.implied_volatility()
```

### 期权指标计算器 / Option Metrics Calculator

```python
from tigeropen.examples.option_helpers.util import OptionUtil

option_util = OptionUtil(client_config=client_config)

# 计算期权指标 / Calculate option metrics
# 输入期权代码，自动查询市场数据计算
metrics = option_util.calculate('TSLA 260220C00385000')
# 返回: Greeks, profit_probability(盈利概率), annualized_return_for_selling(卖出年化收益率), leverage_ratio(杠杆比率)
```

---

## 注意事项 / Notes

- 港股期权需 `get_option_symbols` 获取代码映射 / HK options need symbol mapping
- 期权每张合约通常代表100股标的 / Each contract = 100 shares
- 希腊字母通过 `return_greek_value=True` 获取 / Greeks via `return_greek_value=True`
- 组合策略下单时所有 leg 标的必须一致 / All legs must share same underlying
- 期权行情需要期权行情权限 / Option quotes require option quote permission
- 期权计算工具需安装 quantlib / Calculator tools require `pip install quantlib==1.40`
- 更多期权知识见 / More: https://docs.itigerup.com/docs/quote-option
