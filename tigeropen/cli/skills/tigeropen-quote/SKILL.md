---
name: tigeropen-quote
version: 0.1.0
description: >
  TigerOpen CLI 行情命令：实时报价、K线、分时、逐笔、盘口、市场状态、选股器、
  期权、期货、资金流向、基本面。当用户要查询行情数据时使用。
  不负责下单（tigeropen-trade）、推送订阅（tigeropen-push）。
metadata:
  requires:
    bins: ["tigeropen"]
  cliHelp: "tigeropen quote --help; tigeropen quote <subgroup> --help"
---

**CRITICAL — 使用前 MUST 先读 [`../tigeropen-shared/SKILL.md`](../tigeropen-shared/SKILL.md)**（行情权限 grab、认证模式）。

## 路由规则

只要目标是**查询行情数据**（价格、K线、盘口、深度、成交量、基本面、选股），归本 skill。交易/下单走 `tigeropen-trade`，实时推送走 `tigeropen-push`。

## 命令速查

| 想做什么 | 命令 | 示例 |
|---|---|---|
| 实时报价 | `quote briefs <SYMBOLS...>` | `tigeropen quote briefs AAPL TSLA` |
| K线 | `quote bars <SYMBOLS...>` | `tigeropen quote bars AAPL --period 5min --limit 20` |
| 分时 | `quote timeline <SYMBOLS...>` | `tigeropen quote timeline AAPL --date 2026-03-20` |
| 逐笔 | `quote ticks <SYMBOLS...>` | `tigeropen quote ticks AAPL --limit 50` |
| 盘口深度 | `quote depth <SYMBOLS...> --market US` | `--market` 必选 |
| 市场状态 | `quote market-status [--market]` | `tigeropen quote market-status --market HK` |
| 股票列表 | `quote symbols [--market]` | `tigeropen quote symbols --market HK` |
| 选股器 | `quote scanner --filter <SPEC>` | 见下 |
| 期权到期日 | `quote option expirations <SYMBOL>` | `tigeropen quote option expirations AAPL` |
| 期权链 | `quote option chain <SYMBOL> <EXPIRY>` | `tigeropen quote option chain AAPL 2026-06-19` |
| 期权报价 | `quote option briefs <IDENTIFIERS...>` | `tigeropen quote option briefs "AAPL  260619C00150000"` |
| 期权K线 | `quote option bars <IDENTIFIERS...>` | `tigeropen quote option bars "AAPL  260619C00150000"` |
| 期货交易所 | `quote future exchanges` | |
| 期货合约 | `quote future contracts <EXCHANGE>` | `tigeropen quote future contracts CME` |
| 期货报价 | `quote future briefs <IDENTIFIERS...>` | `tigeropen quote future briefs ES2606` |
| 期货K线 | `quote future bars <IDENTIFIER>` | |
| 资金流向 | `quote capital flow <SYMBOL>` | `--market --period` |
| 资金分布 | `quote capital distribution <SYMBOL>` | |
| 财务报告 | `quote fundamental financial <SYMBOLS...>` | `--fields --period-type` |
| 分红 | `quote fundamental dividend <SYMBOLS...>` | `--begin-date --end-date` |
| 财报日历 | `quote fundamental earnings` | `--market --begin-date --end-date` |

### 期权进阶

港股期权需先用映射代码（如 `00700` → `TCH.HK`）；期权代码格式、链字段解读、单腿期权下单见 [`references/option.md`](references/option.md)。多腿组合/期权计算器是 SDK 能力，CLI 不支持。

## 关键参数

- `bars` 周期：`day/week/month/year/1min/3min/5min/10min/15min/30min/60min`
- `market-status` 市场：`US/HK/CN/ALL`（默认 ALL）
- `depth` 市场：`US/HK/CN`（必选）
- 期权标识符格式：`SYMBOL  YYMMDDCSSSSSSSS`（C=Call, P=Put, S=Strike*1000）
- `bars` 时间范围：`--begin-time --end-time`（`YYYY-MM-DD`）

## 选股器 scanner

`--filter` 可重复，格式：

| 格式 | 说明 | 示例 |
|---|---|---|
| `FIELD` | 仅取值 | `--filter MarketValue` |
| `FIELD:min:max` | 数值区间 | `--filter PeTTM:5:20` |
| `FIELD:min:` / `FIELD::max` | 单边界 | `--filter MarketValue:1e10:` |
| `acc.FIELD:min:max:PERIOD` | 累计字段 | `--filter acc.ROE:0.15::ANNUAL` |
| `fin.FIELD:min:max` | 财务字段(LTM) | `--filter fin.TotalRevenue:1e9:` |
| `tag.FIELD:tag1,tag2` | 标签 | `--filter tag.Industry:Technology` |
| `gainers` / `losers` | 预设涨/跌幅±5% | `--filter gainers` |

其他：`--market US|HK`（默认 US）、`--sort`、`--sort-dir ASC|DESC`、`--limit`、`--page-size`

示例：
```bash
tigeropen quote scanner --filter gainers --sort acc.ChangeRate --sort-dir DESC
tigeropen quote scanner --filter MarketValue:1e10: --filter PeTTM::20 --sort MarketValue
tigeropen quote scanner --market HK --filter gainers --limit 10
```

> 字段名大小写敏感，取自 `tigeropen.common.consts.filter_fields`。

## 注意事项

- **行情权限**：查询实时行情需权限；CLI 默认 grab，同机幂等
- 无权限时可能返回延迟行情（`--format json` 可见 `delayed` 标记）
- 输出均支持 `-f json/csv/table`
