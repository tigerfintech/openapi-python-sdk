# Tiger OpenAPI Skill for AI Coding Tools

[中文](#中文) | [English](#english)

> This plugin follows the [Agent Skills](https://agentskills.io) open standard and works with 30+ AI tools including Claude Code, Cursor, Gemini CLI, GitHub Copilot, VS Code, OpenAI Codex, OpenClaw, and more.

---

## 中文

### 简介

本目录包含一个完整的 AI 技能，涵盖老虎证券 OpenAPI Python SDK 的全部功能。导入后，AI 编码工具（Claude Code、Cursor 等）可直接通过自然语言帮你调用老虎 SDK 完成行情查询、下单交易、账户管理等操作。

### 技能模块

| 模块 | 内容 |
|------|------|
| [quickstart](skills/tigeropen/references/quickstart.md) | SDK 安装、配置、客户端创建、枚举/对象参考、错误码、FAQ |
| [quote](skills/tigeropen/references/quote.md) | 股票/期权/期货/基金/数字货币行情、K线、深度、选股器、基本面 |
| [trade](skills/tigeropen/references/trade.md) | 下单(市价/限价/止损/算法单)、订单管理、账户资产、持仓、资金划转 |
| [option](skills/tigeropen/references/option.md) | 期权链、Greeks、单腿/多腿组合策略、期权计算工具 |
| [push](skills/tigeropen/references/push.md) | 实时推送(行情/深度/逐笔/K线/订单/持仓/资产变动) |
| [cli](skills/tigeropen/references/cli.md) | CLI 命令行工具：配置管理、行情查询、交易操作、账户查看、实时推送 |
| [mcp](skills/tigeropen/references/mcp.md) | MCP Server 配置，集成 Cursor/Claude Code/Trae |

### 快速安装

#### 方式一：通过 Plugin Marketplace 安装（推荐）

在 Claude Code 中运行：

```bash
# 添加 marketplace
/plugin marketplace add tigerfintech/openapi-python-sdk

# 安装 plugin
/plugin install tigeropen@tigerbrokers-openapi
```

安装后技能自动生效，通过 `/tigeropen:tigeropen` 调用。

#### 方式二：通过 --plugin-dir 本地加载

```bash
# 克隆仓库
git clone https://github.com/tigerfintech/openapi-python-sdk.git ~/tiger-sdk

# 启动 Claude Code 时加载 plugin
claude --plugin-dir ~/tiger-sdk/tigeropen/examples/ai/skills
```

#### 方式三：克隆到个人 skills 目录（全局生效）

```bash
# 克隆仓库
git clone https://github.com/tigerfintech/openapi-python-sdk.git /tmp/openapi-python-sdk

# 复制 skill 到 Claude Code 个人目录
cp -r /tmp/openapi-python-sdk/tigeropen/examples/ai/skills/skills/tigeropen ~/.claude/skills/

# 清理
rm -rf /tmp/openapi-python-sdk
```

复制后目录结构：
```
~/.claude/skills/
└── tigeropen/
    ├── SKILL.md
    └── references/
        ├── quickstart.md
        ├── quote.md
        ├── trade.md
        ├── option.md
        ├── push.md
        ├── cli.md
        └── mcp.md
```

> 放在 `~/.claude/skills/` 下的技能对所有项目生效，无需重复配置。

#### 方式四：复制到项目目录（仅当前项目生效）

```bash
mkdir -p .claude/skills

git clone https://github.com/tigerfintech/openapi-python-sdk.git /tmp/openapi-python-sdk
cp -r /tmp/openapi-python-sdk/tigeropen/examples/ai/skills/skills/tigeropen .claude/skills/
rm -rf /tmp/openapi-python-sdk
```

#### 方式五：通过 ClawHub 安装

```bash
clawhub install tigeropen
```

#### 方式六：在 CLAUDE.md 中引用

在项目的 `.claude/CLAUDE.md` 或 `~/.claude/CLAUDE.md` 中添加：

```markdown
## Tiger OpenAPI

本项目使用老虎证券 OpenAPI SDK。技能文件位于 ~/.claude/skills/tigeropen/ 目录下。
开发时请参考该技能中的 API 文档和代码示例。
```

### 使用示例

导入后，你可以直接用自然语言操作：

```
> 帮我查询 AAPL 和 TSLA 的实时行情

> 用限价单买入 100 股 AAPL，价格 150

> 获取 AAPL 近 30 天的日K线数据并画图

> 查询我的账户资产和当前持仓

> 获取 AAPL 下个月到期的期权链，筛选 delta 在 0.3-0.7 的

> 订阅 AAPL 和 TSLA 的实时行情推送
```

### 前置条件

1. 安装 SDK：`pip install tigeropen`
2. 有老虎证券账户和 API 权限（[开发者页面](https://developer.itigerup.com/)）
3. 准备好 `tiger_id`、私钥文件和 `account`

---

## English

### Introduction

This directory contains a complete AI skill covering the Tiger Brokers OpenAPI Python SDK. Once imported, AI coding tools (Claude Code, Cursor, etc.) can help you query market data, place orders, manage accounts, and more through natural language.

### Skill Modules

| Module | Coverage |
|--------|----------|
| [quickstart](skills/tigeropen/references/quickstart.md) | SDK setup, config, client creation, enums/objects reference, error codes, FAQ |
| [quote](skills/tigeropen/references/quote.md) | Stock/option/future/fund/crypto quotes, K-lines, depth, scanner, fundamentals |
| [trade](skills/tigeropen/references/trade.md) | Orders (market/limit/stop/algo), order management, assets, positions, fund transfer |
| [option](skills/tigeropen/references/option.md) | Option chains, Greeks, single-leg/multi-leg combo strategies, calculator tools |
| [push](skills/tigeropen/references/push.md) | Real-time push (quotes/depth/ticks/K-line/order/position/asset changes) |
| [cli](skills/tigeropen/references/cli.md) | CLI tool: config management, market data, trading, account info, real-time push |
| [mcp](skills/tigeropen/references/mcp.md) | MCP Server setup for Cursor/Claude Code/Trae integration |

### Quick Install

#### Option 1: Install via Plugin Marketplace (Recommended)

In Claude Code, run:

```bash
# Add the marketplace
/plugin marketplace add tigerfintech/openapi-python-sdk

# Install the plugin
/plugin install tigeropen@tigerbrokers-openapi
```

After installation, the skill is available automatically via `/tigeropen:tigeropen`.

#### Option 2: Load Locally via --plugin-dir

```bash
# Clone the repository
git clone https://github.com/tigerfintech/openapi-python-sdk.git ~/tiger-sdk

# Start Claude Code with the plugin loaded
claude --plugin-dir ~/tiger-sdk/tigeropen/examples/ai/skills
```

#### Option 3: Clone to Personal Skills Directory (Global)

```bash
# Clone the repository
git clone https://github.com/tigerfintech/openapi-python-sdk.git /tmp/openapi-python-sdk

# Copy skill to Claude Code personal directory
cp -r /tmp/openapi-python-sdk/tigeropen/examples/ai/skills/skills/tigeropen ~/.claude/skills/

# Clean up
rm -rf /tmp/openapi-python-sdk
```

Resulting structure:
```
~/.claude/skills/
└── tigeropen/
    ├── SKILL.md
    └── references/
        ├── quickstart.md
        ├── quote.md
        ├── trade.md
        ├── option.md
        ├── push.md
        ├── cli.md
        └── mcp.md
```

> Skills in `~/.claude/skills/` are available across all projects.

#### Option 4: Copy to Project Directory (Project-specific)

```bash
mkdir -p .claude/skills

git clone https://github.com/tigerfintech/openapi-python-sdk.git /tmp/openapi-python-sdk
cp -r /tmp/openapi-python-sdk/tigeropen/examples/ai/skills/skills/tigeropen .claude/skills/
rm -rf /tmp/openapi-python-sdk
```

#### Option 5: Install via ClawHub

```bash
clawhub install tigeropen
```

#### Option 6: Reference in CLAUDE.md

Add to your `.claude/CLAUDE.md` or `~/.claude/CLAUDE.md`:

```markdown
## Tiger OpenAPI

This project uses the Tiger Brokers OpenAPI SDK. Skill files are in ~/.claude/skills/tigeropen/ directory.
Refer to this skill for API documentation and code examples when developing.
```

### Usage Examples

After importing, use natural language:

```
> Get real-time quotes for AAPL and TSLA

> Buy 100 shares of AAPL with a limit order at $150

> Fetch AAPL daily K-line data for the last 30 days and plot it

> Show my account assets and current positions

> Get AAPL option chain expiring next month, filter delta 0.3-0.7

> Subscribe to real-time quote updates for AAPL and TSLA
```

### Prerequisites

1. Install SDK: `pip install tigeropen`
2. Tiger Brokers account with API access ([Developer Page](https://developer.itigerup.com/))
3. Have your `tiger_id`, private key file, and `account` ready
