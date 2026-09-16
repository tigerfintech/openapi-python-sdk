---
name: tigeropen-trade
version: 0.1.0
description: >
  TigerOpen CLI 交易命令：订单（查询/预览/下单/改单/撤单）、持仓、成交、账户资产。
  当用户要下单、管理订单、查看持仓或资产时使用。
  高风险写操作：下单/改单/撤单会真实影响账户，必须确认。行情走 tigeropen-quote。
metadata:
  requires:
    bins: ["tigeropen"]
  cliHelp: "tigeropen trade --help; tigeropen account --help"
---

**CRITICAL — 使用前 MUST 先读 [`../tigeropen-shared/SKILL.md`](../tigeropen-shared/SKILL.md)**（认证模式、scope 限制）。

## ⚠️ 安全警告（交易涉及真实资金）

- 交易命令操作**真实账户**。默认 Paper Trading 更安全，实盘下单必须用户明确确认。
- **下单/改单/撤单是高风险写操作**：CLI 默认要求交互确认（`-y` 跳过）。agent 不应自动加 `-y`。
- 下单前**必须**先 `preview` 预览订单，展示预估信息。
- OAuth2 模式：scope 无 `api.trade:write` 时**无法下单**（下单命令会失败）。

## 路由规则

- 订单/持仓/成交/账户资产 → 本 skill
- 实时推送订单/持仓/资产变动 → `tigeropen-push`
- 行情数据 → `tigeropen-quote`

## 命令速查

### 订单查询（只读，安全）

```bash
tigeropen trade order list                        # 订单列表
tigeropen trade order list --status Filled        # 按状态
tigeropen trade order list --symbol AAPL          # 按标的
tigeropen trade order list --market US --limit 20
tigeropen trade order get <ORDER_ID>              # 订单详情
```

### 订单预览（只读，安全）

```bash
tigeropen trade order preview --symbol AAPL --action BUY --quantity 100 --limit-price 150
tigeropen trade order preview --symbol AAPL --action SELL --quantity 50 --order-type MKT
```

参数：`--symbol`（必）、`--action BUY/SELL`（必）、`--quantity`（必）、
`--order-type LMT/MKT/STP/STP_LMT`（默认 LMT）、`--limit-price`、`--sec-type STK/OPT/FUT`

### ⚠️ 下单（高风险写）

```bash
tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150
```

默认需确认；`-y` 跳过。**agent 应让用户确认后再执行**。

### ⚠️ 改单（高风险写）

```bash
tigeropen trade order modify <ORDER_ID> --limit-price 155
tigeropen trade order modify <ORDER_ID> --quantity 200
tigeropen trade order modify <ORDER_ID> --aux-price 140
```

### ⚠️ 撤单（高风险写）

```bash
tigeropen trade order cancel <ORDER_ID>
```

### 持仓（只读）

```bash
tigeropen trade position list
tigeropen trade position list --sec-type OPT
tigeropen trade position list --market US --symbol AAPL
```

`--sec-type STK/OPT/FUT/WAR`、`--market US/HK/ALL`

### 成交（只读）

```bash
tigeropen trade transaction list
tigeropen trade transaction list --symbol AAPL
tigeropen trade transaction list --start-time 2026-01-01 --end-time 2026-03-31
```

### 账户（只读）

```bash
tigeropen account info                 # 账户信息
tigeropen account assets               # 资产概览
tigeropen account assets --currency USD
tigeropen account analytics --start-date ... --end-date ...
```

## 完整下单流程

```
1. 查行情     tigeropen quote briefs AAPL
2. 预览订单   tigeropen trade order preview --symbol AAPL --action BUY --quantity 100 --limit-price 150
3. 确认后下单 tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150
4. 查状态     tigeropen trade order list --symbol AAPL --status Submitted
5. 需撤单     tigeropen trade order cancel <ORDER_ID>
```

## 风险标注总览

| 命令 | 风险 | 默认确认 |
|---|---|---|
| `order place` | 高风险写 | ✅ 需 `-y` 跳过 |
| `order modify` | 高风险写 | ✅ |
| `order cancel` | 高风险写 | ✅ |
| `order list/get` | 只读 | 无 |
| `order preview` | 只读 | 无 |
| `position list` | 只读 | 无 |
| `transaction list` | 只读 | 无 |
| `account *` | 只读 | 无 |
