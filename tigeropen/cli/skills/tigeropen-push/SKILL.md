---
name: tigeropen-push
version: 0.1.0
description: >
  TigerOpen CLI 推送命令：通过 WebSocket 实时订阅行情/订单/持仓/资产变动。
  当用户要实时监控数据流、订阅推送时使用。不负责查询类命令（tigeropen-quote/tigeropen-trade）。
metadata:
  requires:
    bins: ["tigeropen"]
  cliHelp: "tigeropen push --help"
---

**CRITICAL — 使用前 MUST 先读 [`../tigeropen-shared/SKILL.md`](../tigeropen-shared/SKILL.md)**（认证模式、scope 限制）。

## 路由规则

- 实时流式推送（行情/订单/持仓/资产变动）→ 本 skill
- 一次性查询 → `tigeropen-quote`（行情）/ `tigeropen-trade`（订单/资产）

## 命令速查

```bash
tigeropen push quote AAPL TSLA          # 实时行情推送（Ctrl+C 停止）
tigeropen push order                    # 订单状态推送
tigeropen push position                 # 持仓变动推送
tigeropen push asset                    # 资产变动推送
```

## 行为特征

- **WebSocket 长连接**：持续输出直到 `Ctrl+C`
- 输出格式：`--format json` 时每行一条 JSON（可管道处理）
- 推送地址来自 `config.socket_host_port`（`TIGEROPEN_SOCKET_URL` 或 props）

## 认证

```bash
# 签名模式
tigeropen push quote AAPL

# OAuth2 模式（protobuf only）
tigeropen --auth oauth2 push quote AAPL
```

**关键约束**：
- OAuth2 推送**仅支持 protobuf 协议**（STOMP 不支持）
- OAuth2 token 由心跳驱动就地轮换（不重连），服务端不支持时连接继续可用
- scope 无 `api.quote:read` 时行情订阅会被拒

## 注意事项

- **同一 tiger_id 只能有一个推送连接**，新连接踢旧连接
- 推送命令会持续占用终端，agent 场景注意超时
- 行情推送需行情权限（CLI 默认 grab）
