---
name: tigeropen-push
description: Tiger Brokers OpenAPI real-time push skill. Subscribe to real-time quote changes, depth quotes, trade ticks, K-line updates, order status changes, position changes, and asset changes via PushClient. Supports Protobuf and STOMP protocols. Use this skill when users need real-time market data push or order/position monitoring.
metadata:
  author: tigerbrokers
  version: "3.5.4"
  language: en_US
---

# Tiger Open API Real-time Push

## Create Push Client

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.push.push_client import PushClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
protocol, host, port = client_config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'), client_config=client_config)
```

## Define Callbacks

```python
def on_quote_changed(frame):
    print(f"{frame.symbol}: price={frame.latest_price}, change%={frame.latest_change_percent}")

def on_order_changed(frame):
    print(f"Order {frame.id}: status={frame.status}")

def on_position_changed(frame):
    print(f"{frame.symbol}: qty={frame.quantity}")

def on_asset_changed(frame):
    print(f"Net Liquidation: {frame.net_liquidation}")

def on_depth_quote(frame):
    print(f"Depth: {frame}")

def on_tick(frame):
    print(f"Tick: {frame}")
```

## Register Callbacks & Connect

```python
push_client.quote_changed = on_quote_changed
push_client.order_changed = on_order_changed
push_client.position_changed = on_position_changed
push_client.asset_changed = on_asset_changed
push_client.depth_quote_changed = on_depth_quote
push_client.tick_changed = on_tick

push_client.connect(client_config.tiger_id, client_config.private_key)
```

## Subscribe

```python
push_client.subscribe_quote(['AAPL', 'TSLA'])
push_client.subscribe_depth_quote(['AAPL'])
push_client.subscribe_tick(['AAPL'])
push_client.subscribe_order()
push_client.subscribe_position()
push_client.subscribe_asset()
```

## Unsubscribe & Disconnect

```python
push_client.unsubscribe_quote(['AAPL'])
push_client.disconnect()
```

## Complete Example

```python
from tigeropen.push.push_client import PushClient
from tigeropen.tiger_open_config import TigerOpenClientConfig

config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
protocol, host, port = config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'), client_config=config)

def on_quote(frame):
    print(f"{frame.symbol}: {frame.latest_price} ({frame.latest_change_percent}%)")

def on_order(frame):
    print(f"Order {frame.id}: {frame.status}")

push_client.quote_changed = on_quote
push_client.order_changed = on_order

push_client.connect(config.tiger_id, config.private_key)
push_client.subscribe_quote(['AAPL', 'TSLA', '00700'])
push_client.subscribe_order()

import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    push_client.disconnect()
```

## Notes

- Protobuf protocol (default) recommended over STOMP for better performance
- Push client has automatic reconnection
- Order/position/asset changes are auto-pushed after connection
- Quote push requires corresponding quote permissions
