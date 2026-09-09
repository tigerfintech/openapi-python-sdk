---
name: tigeropen-cli
version: 0.1.0
description: >
  TigerOpen CLI 基础用法：命令总览、全局选项、配置管理、OAuth2 接入。
  当用户要用 tigeropen 命令行工具查询数据、管理订单或配置认证时使用。
  行情走 tigeropen-quote、交易走 tigeropen-trade、推送走 tigeropen-push。
metadata:
  requires:
    bins: ["tigeropen"]
  cliHelp: "tigeropen --help; tigeropen <command> --help"
---

**CRITICAL — 使用前 MUST 先读 [`../tigeropen-shared/SKILL.md`](../tigeropen-shared/SKILL.md)**（认证、配置、权限约定）。

> `tigeropen` 命令随 SDK 安装自动可用（`pip install tigeropen` 或官方 install.sh）。

## 命令总览

```
tigeropen [全局选项] COMMAND
├── version                 # SDK 版本
├── uninstall               # 卸载（--remove-config 删除凭证）
├── config                  # 配置管理：init/show/set/path
├── auth                    # OAuth2 认证：login/login-device/logout/status/token
├── quote                   # 行情：briefs/bars/timeline/ticks/depth/scanner/option/future/capital/fundamental
├── trade                   # 交易：order/position/transaction
├── account                 # 账户：info/assets/analytics
├── push                    # 推送：quote/order/position/asset（WebSocket）
└── skills                  # 内置 agent 知识：list/read
```

## 全局选项

| 选项 | 短写 | 说明 | 默认 |
|---|---|---|---|
| `--config-path` | `-c` | 配置文件路径 | `~/.tigeropen/` |
| `--format` | `-f` | 输出格式 table/json/csv | `json` |
| `--language` | `-l` | en_US/zh_CN/zh_TW | `en_US` |
| `--auth` | | 认证模式 signature/oauth2 | `signature` |
| `--issuer` | | OAuth2 授权服务器 | 内置默认 |
| `--client-id` | | 手动注册的 clientId | 动态注册 |
| `--verbose` | `-v` | 调试日志 | `false` |

全局选项可放在命令任意位置：`tigeropen quote briefs AAPL -f json` 与 `tigeropen -f json quote briefs AAPL` 等价。

## 配置管理

```bash
tigeropen config init                    # 签名模式交互配置（tiger_id/私钥）
tigeropen --auth oauth2 config init      # OAuth2 配置（issuer，不收集私钥）
tigeropen config show                    # 查看配置（私钥脱敏）
tigeropen config set <KEY> <VALUE>       # 设置配置项
tigeropen config path                    # 配置路径
```

配置写入 `~/.tigeropen/tiger_openapi_config.properties`。

## 版本与卸载

```bash
tigeropen version                        # SDK 版本
tigeropen uninstall                      # 交互确认后执行 pip uninstall
tigeropen uninstall --remove-config      # 同时删除 ~/.tigeropen/ 配置目录
tigeropen uninstall -y                   # 跳过确认（慎用）
```

> ⚠️ `--remove-config` 会**不可恢复地删除** `~/.tigeropen/`（含 tiger_id、私钥、token 等凭证），且删除发生在 `pip uninstall` 之前。与 `-y` 组合会跳过全部确认——除非确定要清空凭证，不要一起用。

## OAuth2 接入（本次新增）

详见 [`references/oauth2.md`](references/oauth2.md)。

快速上手：

```bash
# 1. 授权（浏览器）
tigeropen auth login

# 2. 用 OAuth2 查行情（默认 grab 权限）
tigeropen --auth oauth2 quote briefs AAPL

# 3. 查账户
tigeropen --auth oauth2 account info

# 4. 会话管理
tigeropen auth status
tigeropen auth logout
```

## 输出格式

```bash
tigeropen -f json quote briefs AAPL      # JSON（脚本友好）
tigeropen -f csv quote bars AAPL --limit 5
tigeropen -f table trade position list   # 表格
```

## 常见场景

```bash
# 快速看行情
tigeropen quote briefs AAPL TSLA -f json

# 看持仓和资产
tigeropen trade position list
tigeropen account assets

# 完整下单流程（preview 先行）
tigeropen quote briefs AAPL
tigeropen trade order preview --symbol AAPL --action BUY --quantity 100 --limit-price 150
tigeropen trade order place --symbol AAPL --action BUY --quantity 100 --limit-price 150
tigeropen trade order list --symbol AAPL --status Submitted
```

### 导出数据

```bash
# 导出 K 线到 CSV / Export bars to CSV
tigeropen -f csv quote bars AAPL --period day --limit 100 > aapl_bars.csv

# 导出持仓为 JSON / Export positions as JSON
tigeropen -f json trade position list > positions.json

# 导出成交记录 / Export transactions
tigeropen -f csv trade transaction list --symbol AAPL > aapl_transactions.csv
```

## 注意事项

- 下单/改单/撤单默认需交互确认，`-y` 跳过（**高风险写操作**）
- 推送命令 WebSocket 长连接，Ctrl+C 断开
- 行情权限需单独购买，API 与 App 独立
- 输出支持 `--format json` 管道处理
