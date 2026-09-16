---
name: tigeropen-shared
version: 0.1.0
description: >
  TigerOpen CLI 公共知识：认证方式（签名 vs OAuth2）、配置解析优先级、环境变量、
  token 存储、错误码、行情权限。所有 tigeropen-* skill 的前置必读。
metadata:
  requires:
    bins: ["tigeropen"]
  cliHelp: "tigeropen --help"
---

**CRITICAL — 使用任何 tigeropen 命令前 MUST 先读本文件**，其中包含认证、配置与权限的关键约定。

## 认证方式：签名 vs OAuth2

| | 签名模式（默认） | OAuth2 模式 |
|---|---|---|
| 切换 | 无需标志 | 全局 `--auth oauth2` |
| 凭据 | `tiger_id` + RSA 私钥 | `Authorization: Bearer <token>` |
| 配置来源 | `~/.tigeropen/tiger_openapi_config.properties` | `~/.tiger/openapi/`（token 独立存储） |
| 授权 | `tigeropen config init`（收集私钥） | `tigeropen auth login`（浏览器） |
| 适用 | 已有 API 密钥的开发者 | 无密钥、走 OAuth2 授权的用户 |

OAuth2 模式不依赖私钥：`attach_oauth2` 会清空 `config.private_key` / `config.tiger_id`，签名凭据不进入 OAuth2 会话。

## 认证模式选择规则

- 默认**签名模式**，行为与 `feat_oauth2` 之前完全一致
- 显式 `--auth oauth2` 才启用 OAuth2，避免误用
- `config init --auth oauth2` 写入 `auth_mode=oauth2` 到 props，后续命令自动识别

## 配置解析优先级

参数（CLI 选项）> 环境变量（`TIGEROPEN_*`）> 配置文件（`~/.tigeropen/`）

| 配置项 | 环境变量 | props 键 |
|---|---|---|
| 认证模式 | （无） | `auth_mode` |
| OAuth2 issuer | `TIGEROPEN_OAUTH2_ISSUER` | `issuer` |
| OAuth2 client_id | `TIGEROPEN_CLIENT_ID` | `client_id` |
| tiger_id | `TIGEROPEN_TIGER_ID` | `tiger_id` |
| 私钥 | `TIGEROPEN_PRIVATE_KEY` | `private_key_pk8` |
| 账户 | `TIGEROPEN_ACCOUNT` | `account` |
| 网关 | `TIGEROPEN_SERVER_URL` | `server_url` |

OAuth2 下 `--auth` / `--issuer` / `--client-id` 显式 CLI 选项优先级最高，其次 props。

## OAuth2 授权流程（重要）

```
1. tigeropen auth login            # 浏览器授权（loopback+PKCE），打印 URL 并尝试打开
2. tigeropen auth login-device     # 无浏览器环境（设备码，RFC 8628）
3. tigeropen auth status           # 查看当前 token 状态/scope/剩余秒数
4. tigeropen auth token            # 打印 access token（脚本/调试用）
5. tigeropen auth logout           # 服务端 revoke + 清除本地 token
```

**关键约定**：
- 先 `auth login` 再跑业务命令；**业务命令不会隐式弹浏览器**（授权与查询分离）
- 二次运行自动复用磁盘 token，不重复授权
- token 存 `~/.tiger/openapi/tokens/{clientId}.json`（0600），与签名配置 `~/.tigeropen/` 相互独立
- scope 不含 `api.trade:write` 时**无法下单**（只读查询可用）

## 行情权限（grab）

- `quote briefs` 等行情命令依赖行情权限
- CLI 的 `get_quote_client` **默认 grab**（`QuoteClient(config)`）——device_id 是 MAC 地址，同机重复 grab 幂等，不踢其他设备
- 若在非交易设备上运行，grab 会把权限绑定到当前机器（既有语义）

## 错误码速查

| 错误 | 含义 | 处理 |
|---|---|---|
| `API Error [4]` | 访问被拒 | 检查凭证/权限/scope |
| `API Error [5]` | 频率限制 | 稍后重试 |
| `Config file not found` | 未初始化 | `tigeropen config init` |
| `No quote data found` | 无数据 | 检查标的/市场状态 |

## 环境区分

- 默认 issuer 与网关都指向生产环境，无需额外配置
- 指向其他环境时用 `TIGEROPEN_OAUTH2_ISSUER` 与 `TIGEROPEN_SERVER_URL` 一起改
- issuer / 网关 / 公钥必须指向同一套环境，否则会得到误导性报错
