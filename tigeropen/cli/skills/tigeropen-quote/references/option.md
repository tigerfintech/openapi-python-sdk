# 期权命令进阶 / Option Reference

> CLI 期权命令的补充知识：代码格式、HK 映射、链字段解读、单腿下单。
> 多腿组合、期权计算器、Wheel 策略是 Python API 能力，CLI 不直接支持，需用 SDK 编写代码（见 tigeropen-skill 项目）。

## 期权代码格式 / Option Symbol Format

CLI 的 `quote option briefs` / `bars` 需要完整期权标识符：

| 市场 | 格式 | 示例 |
|---|---|---|
| 美股 US | `标的`(左填充至6位) + `YYMMDD` + `C/P` + 行权价×1000(8位) | `'AAPL  250829C00150000'` |
| 港股 HK | `映射代码` + `YYMMDD` + `C/P` + 行权价×1000 | `'TCH.HK 230616C00550000'` |

`C`=Call 看涨，`P`=Put 看跌。行权价 ×1000 补零到 8 位。

## 港股期权映射 / HK Option Mapping

港股期权标的代码与正股代码不同，**必须先映射**：

```bash
# CLI 无映射命令，需通过 SDK get_option_symbols(market='HK') 查询
# 例如 00700 -> TCH.HK，然后才能用 TCH.HK 查期权链
tigeropen quote option expirations TCH.HK
tigeropen quote option chain TCH.HK 2026-06-18
```

> 直接用 `00700` 查港股期权会失败，必须先拿到映射后的期权代码。

## 期权链字段解读 / Option Chain Fields

`quote option chain <SYMBOL> <EXPIRY>` 返回每行一个合约，关键字段：

| 字段 | 说明 |
|---|---|
| `identifier` | 期权完整代码（用于 briefs/bars） |
| `strike` | 行权价 |
| `put_call` | `CALL` / `PUT` |
| `expiry` | 到期日（毫秒时间戳） |
| `multiplier` | 合约乘数（美股通常 100） |
| `bid/ask_price`、`bid/ask_size` | 买卖价与量 |
| `last_price` | 最新价 |
| `volume`、`open_interest` | 成交量、持仓量 |
| `delta/gamma/theta/vega/rho` | 希腊字母（chain 默认不含，需 SDK 带 `return_greek_value=True`） |
| `implied_volatility` | 隐含波动率 |

**筛选提示**：CLI 的 chain 命令不支持筛选参数；带 Greeks / IV / 持仓量筛选需用 SDK 的 `get_option_chain(option_filter=...)`。

## 单腿期权下单 / Single-leg Option Order

CLI 的 `trade order place` / `preview` 支持 `--sec-type OPT`：

```bash
# 买看涨（先查链拿到 identifier，构造合约）
tigeropen trade order preview --symbol "AAPL  250829C00150000" --sec-type OPT --action BUY --quantity 1 --limit-price 1.5

# 确认后下单
tigeropen trade order place --symbol "AAPL  250829C00150000" --sec-type OPT --action BUY --quantity 1 --limit-price 1.5
```

> ⚠️ 期权下单是**高风险写操作**，需用户确认。多腿组合（价差/跨式/铁鹰等）CLI 不支持，需用 SDK 的 `Order` + `contract_legs`。
