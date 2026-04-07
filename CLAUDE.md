# CLAUDE.md - TigerOpen Python SDK

## 项目概述

老虎证券 OpenAPI 官方 Python SDK，提供行情、交易、账户、推送一站式接入。

## 技术栈

- Python 3.7+
- WebSocket（实时推送）
- HTTP REST API

## 目录结构

```
tigeropen/
├── cli/           # 命令行工具
├── common/        # 通用模块（配置、常量、异常）
├── examples/      # 示例代码
├── fundamental/   # 基本面数据
├── push/          # WebSocket 推送
├── quote/         # 行情服务
├── trade/         # 交易服务
├── tiger_open_client.py   # 主客户端
└── tiger_open_config.py   # 配置类
```

## 核心模块

| 模块 | 职责 |
|------|------|
| `quote/` | 行情数据：K线、报价、逐笔成交、盘口深度 |
| `trade/` | 交易服务：下单、改单、撤单、订单查询 |
| `push/` | WebSocket 推送：行情、订单、持仓变动 |
| `fundamental/` | 基本面：财报、公司信息 |
| `cli/` | 命令行工具 |

## 安装与运行

```bash
pip install tigeropen
# 或从源码安装
pip install -e .
```

## 测试

```bash
pytest tests/
```

## 文档

- API 文档：https://quant.itigerup.com/openapi/zh/python/overview/introduction.html
- 开发者平台：https://developer.itigerup.com/
