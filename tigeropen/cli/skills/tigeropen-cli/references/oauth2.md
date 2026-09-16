# OAuth2 接入指南

> 从签名模式切换到 OAuth2 的唯一变化是认证方式；业务命令语法不变。

## 环境变量

```bash
export TIGEROPEN_OAUTH2_ISSUER=https://...   # 授权服务器（不设则用内置默认）
export TIGEROPEN_CLIENT_ID=xxx               # 手动 clientId（不设则动态注册）
```

## 授权

### 浏览器授权（推荐）

```bash
tigeropen auth login
```

- 打印授权 URL 并尝试自动打开浏览器
- loopback + PKCE（S256），state 校验
- token 存 `~/.tiger/openapi/tokens/`（0600）
- **二次运行自动复用 token，不重复授权**

### 浏览器重定向（可选，安全性更高）

```bash
tigeropen auth login --loopback
```

- 绑定到当前进程，不依赖用户把验证码输到正确的地方
- 适合服务器/容器/SSH 场景
- 需要本机浏览器与可用的 loopback 端口；桌面环境优先用它

## 会话管理

```bash
tigeropen auth status        # issuer/client_id/scope/剩余秒数
tigeropen auth token         # 打印 access token（脚本/调试）
tigeropen auth logout        # 服务端 revoke + 清除本地 token
```

## 用 OAuth2 跑业务命令

```bash
tigeropen --auth oauth2 quote briefs AAPL
tigeropen --auth oauth2 trade order list
tigeropen --auth oauth2 account assets
tigeropen --auth oauth2 push quote AAPL     # 推送（protobuf only）
```

> 推送的 socket 地址不随 issuer 变化。指向非默认网关时需显式指定，如
> `TIGEROPEN_SOCKET_HOST_PORT="ssl,<gateway-host>,9883"`。

## 关键行为

1. **授权与查询分离**：业务命令不隐式弹浏览器；必须先 `auth login` 完成授权
2. **401 自动刷新**：token 接近过期自动刷新（提前 5 分钟）；收到 401 强制刷新并重试一次
3. **scope 限制**：授权时选择的 scope 决定可用能力：
   - `api.quote:read` → 行情
   - `api.account:read` → 账户
   - `api.trade:read` → 订单/持仓查询
   - `api.trade:write` → 下单（需要交易密码授权）
4. **无 trade:write 时不可下单**：下单类命令会失败，需重新授权勾选 Trade execution

## token 存储

- 位置：`~/.tiger/openapi/tokens/{clientId}.json`（0600）
- client registration：`~/.tiger/openapi/clients/{issuerHash}.json`（0600）
- 与签名配置 `~/.tigeropen/` 相互独立
- 自定义存储：通过 `OAuth2SessionManager(store=...)` 注入

## 排错

| 症状 | 原因 | 处理 |
|---|---|---|
| `tigerId null is illegal` | 网关与 issuer 环境不匹配 | 确认 `TIGEROPEN_SERVER_URL` 指向同环境网关 |
| `response sign verify failed` | 响应公钥与网关环境不匹配 | 确认公钥与网关是同一套环境 |
| `permission denied` | 行情权限未 grab | CLI 默认 grab，检查授权账户是否有行情权限 |
| `re-authorization required` | refresh token 失效 | 重新 `auth login` |
