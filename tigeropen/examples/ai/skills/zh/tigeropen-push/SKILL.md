---
name: tigeropen-push
description: 老虎证券 OpenAPI 实时推送技能。通过 PushClient 订阅实时行情变动、深度盘口、逐笔成交、K线推送、订单状态变动、持仓变动、资产变动。支持 Protobuf 和 STOMP 协议。当用户需要接收实时行情推送、监控订单和持仓变化时使用此技能。
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: zh_CN
---

# Tiger Open API 实时推送

## 创建推送客户端

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.push.push_client import PushClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
protocol, host, port = client_config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'), client_config=client_config)
```

## 定义回调函数

```python
def on_quote_changed(frame):
    """行情变动"""
    print(f"{frame.symbol}: 最新价={frame.latest_price}, 涨跌幅={frame.latest_change_percent}")

def on_order_changed(frame):
    """订单变动"""
    print(f"订单 {frame.id}: 状态={frame.status}")

def on_position_changed(frame):
    """持仓变动"""
    print(f"{frame.symbol}: 数量={frame.quantity}")

def on_asset_changed(frame):
    """资产变动"""
    print(f"总资产: {frame.net_liquidation}")

def on_depth_quote(frame):
    """深度行情"""
    print(f"深度: {frame}")

def on_tick(frame):
    """逐笔成交"""
    print(f"成交: {frame}")

def on_kline(frame):
    """K线推送"""
    print(f"K线: {frame}")
```

## 注册回调并连接

```python
# 注册回调
push_client.quote_changed = on_quote_changed
push_client.order_changed = on_order_changed
push_client.position_changed = on_position_changed
push_client.asset_changed = on_asset_changed
push_client.depth_quote_changed = on_depth_quote
push_client.tick_changed = on_tick

# 连接
push_client.connect(client_config.tiger_id, client_config.private_key)
```

## 订阅数据

```python
# 行情变动
push_client.subscribe_quote(['AAPL', 'TSLA'])

# 深度行情
push_client.subscribe_depth_quote(['AAPL'])

# 逐笔成交
push_client.subscribe_tick(['AAPL'])

# 订单/持仓/资产变动
push_client.subscribe_order()
push_client.subscribe_position()
push_client.subscribe_asset()
```

## 取消订阅与断开

```python
push_client.unsubscribe_quote(['AAPL'])
push_client.disconnect()
```

## 完整示例

```python
from tigeropen.push.push_client import PushClient
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
protocol, host, port = config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'), client_config=config)

def on_quote(frame):
    print(f"{frame.symbol}: {frame.latest_price} ({frame.latest_change_percent}%)")

def on_order(frame):
    print(f"订单 {frame.id}: {frame.status}")

push_client.quote_changed = on_quote
push_client.order_changed = on_order

push_client.connect(config.tiger_id, config.private_key)
push_client.subscribe_quote(['AAPL', 'TSLA', '00700'])
push_client.subscribe_order()

# 保持运行
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    push_client.disconnect()
```

## STOMP 协议（备选）

```python
from tigeropen.push.push_client import StompPushClient

protocol, host, port = client_config.socket_host_port
stomp_client = StompPushClient(host, port, use_ssl=(protocol == 'ssl'))
# 使用方式与 PushClient 类似
```

## 注意事项

- 推荐使用 Protobuf 协议（默认），性能优于 STOMP
- 推送客户端有自动重连机制
- 订单/持仓/资产变动在连接后自动推送
- 确保网络稳定，断线后会自动尝试重连
- 行情推送需要对应的行情权限
