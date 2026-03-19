
# Tiger Open API 实时推送 / Real-time Push

> 中文 | English — 双语技能。Bilingual skill.
> 官方文档 Docs: https://docs.itigerup.com/docs/push-quote

## 创建推送客户端 / Create Push Client

```python
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.push.push_client import PushClient

client_config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
protocol, host, port = client_config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'), client_config=client_config)
```

---

## 回调函数 / Callback Functions

### 行情变动 / Quote Change

```python
def on_quote_changed(frame):
    """股票/期权/期货行情变动 Stock/option/future quote change"""
    print(f"{frame.symbol}: price={frame.latest_price}, "
          f"change%={frame.latest_change_percent}, volume={frame.volume}")
    # 属性: symbol, latest_price, latest_change, latest_change_percent, volume, amount,
    #       open, high, low, pre_close, latest_time, market_status
    # 盘前盘后: hour_trading_latest_price, hour_trading_change_percent, hour_trading_volume
```

### 深度行情 / Depth Quote Change

```python
def on_depth_quote(frame):
    """深度盘口变动 Depth quote change"""
    print(f"{frame.symbol}: asks={frame.asks}, bids={frame.bids}")
    # asks/bids 各为列表: [price, volume, order_count]
```

### 逐笔成交 / Tick Change

```python
def on_tick(frame):
    """逐笔成交推送 Trade tick push"""
    print(f"{frame.symbol}: price={frame.price}, volume={frame.volume}, time={frame.time}")
    # 属性: symbol, price, volume, time, type, sn
```

### K线推送 / K-line Change

```python
def on_kline(frame):
    """分钟K线推送 Minute K-line push"""
    print(f"{frame.symbol}: open={frame.open}, high={frame.high}, "
          f"low={frame.low}, close={frame.close}, volume={frame.volume}")
    # 属性: symbol, time, open, high, low, close, volume
```

### 订单变动 / Order Change

```python
def on_order_changed(frame):
    """订单状态变动 Order status change"""
    print(f"Order {frame.id}: symbol={frame.symbol}, status={frame.status}, "
          f"action={frame.action}, filled={frame.filled_quantity}/{frame.quantity}")
    # 属性: id, order_id, symbol, sec_type, action, order_type, status,
    #       quantity, filled_quantity, avg_fill_price, limit_price, aux_price,
    #       trade_time, time_in_force, outside_rth, cancel_status, replace_status
```

### 持仓变动 / Position Change

```python
def on_position_changed(frame):
    """持仓变动 Position change"""
    print(f"{frame.symbol}: qty={frame.quantity}, cost={frame.average_cost}, "
          f"price={frame.latest_price}, pnl={frame.unrealized_pnl}")
    # 属性: symbol, sec_type, market, currency, quantity, average_cost,
    #       latest_price, market_value, unrealized_pnl, realized_pnl
```

### 资产变动 / Asset Change

```python
def on_asset_changed(frame):
    """资产变动 Asset change"""
    print(f"Net: {frame.net_liquidation}, Available: {frame.available_funds}")
    # 属性: net_liquidation, available_funds, excess_liquidity, buying_power,
    #       cash_balance, init_margin, maintain_margin, realized_pnl, unrealized_pnl
```

### 成交推送 / Transaction Change

```python
def on_transaction_changed(frame):
    """成交推送 Transaction push"""
    print(f"Order {frame.order_id}: filled {frame.filled_quantity} @ {frame.filled_price}")
    # 属性: order_id, filled_price, filled_quantity, transact_time
```

### 连接/断开/错误回调 / Connection Callbacks

```python
def on_connected():
    """连接成功 Connected"""
    print("Push connected")

def on_disconnected():
    """断开连接 Disconnected (自动重连 auto-reconnects)"""
    print("Push disconnected, will auto-reconnect")

def on_error(frame):
    """错误 Error"""
    print(f"Push error: {frame}")

def on_kickout(frame):
    """被踢出(新连接登录) Kicked out by new connection"""
    print(f"Kicked out: {frame}")
```

---

## 注册回调并连接 / Register Callbacks & Connect

```python
# 注册回调 / Register callbacks
push_client.quote_changed = on_quote_changed
push_client.depth_quote_changed = on_depth_quote
push_client.tick_changed = on_tick
push_client.kline_changed = on_kline
push_client.order_changed = on_order_changed
push_client.position_changed = on_position_changed
push_client.asset_changed = on_asset_changed
push_client.transaction_changed = on_transaction_changed

# 连接/断开回调 / Connection callbacks
push_client.connect_callback = on_connected
push_client.disconnect_callback = on_disconnected
push_client.error_callback = on_error
push_client.kickout_callback = on_kickout

# 连接 / Connect
push_client.connect(client_config.tiger_id, client_config.private_key)
```

---

## 订阅数据 / Subscribe

### 股票行情 / Stock Quotes

```python
# 订阅行情变动 / Subscribe quote changes
push_client.subscribe_quote(['AAPL', 'TSLA', '00700'])

# 取消订阅 / Unsubscribe
push_client.unsubscribe_quote(['AAPL'])
```

### 期权行情 / Option Quotes

```python
# 订阅期权行情 / Subscribe option quotes
push_client.subscribe_quote(['AAPL  250829C00150000'])
push_client.unsubscribe_quote(['AAPL  250829C00150000'])
```

### 期货行情 / Future Quotes

```python
# 订阅期货行情 / Subscribe future quotes
push_client.subscribe_quote(['CL2509'])
push_client.unsubscribe_quote(['CL2509'])
```

### 数字货币行情 / Crypto Quotes

```python
push_client.subscribe_cc(['BTC/USD', 'ETH/USD'])
push_client.unsubscribe_cc(['BTC/USD'])
```

### 深度盘口 / Depth Quotes

```python
push_client.subscribe_depth_quote(['AAPL'])  # 需要 L2 权限 / Requires L2
push_client.unsubscribe_depth_quote(['AAPL'])
```

### 逐笔成交 / Trade Ticks

```python
push_client.subscribe_tick(['AAPL'])
push_client.unsubscribe_tick(['AAPL'])

# 完整逐笔(含历史) / Full tick (includes history)
push_client.use_full_tick = True  # 连接前设置 / Set before connect
push_client.subscribe_tick(['AAPL'])
```

### K线推送 / K-line Push

```python
# 订阅分钟K线 / Subscribe minute K-lines
push_client.subscribe_kline(['AAPL'])
push_client.unsubscribe_kline(['AAPL'])
```

### 交易相关 / Trading Events

```python
# 订单变动 / Order changes (连接后自动推送 / auto-pushed after connect)
push_client.subscribe_order()
push_client.unsubscribe_order()

# 持仓变动 / Position changes
push_client.subscribe_position()
push_client.unsubscribe_position()

# 资产变动 / Asset changes
push_client.subscribe_asset()
push_client.unsubscribe_asset()

# 成交推送 / Transaction changes
push_client.subscribe_transaction()
push_client.unsubscribe_transaction()
```

### 热门排行 / Hot Trading Rank

```python
# 股票热门排行 / Stock hot trading rank
push_client.subscribe_stock_top()
push_client.unsubscribe_stock_top()

# 期权热门排行 / Option hot trading rank
push_client.subscribe_option_top()
push_client.unsubscribe_option_top()
```

### 查询已订阅 / Query Subscriptions

```python
subscribed = push_client.query_subscribed_quote()
print(f"已订阅: {subscribed}")
```

---

## 断开连接 / Disconnect

```python
push_client.disconnect()
```

---

## 完整示例 / Complete Example

```python
import time
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.push.push_client import PushClient

config = TigerOpenClientConfig(props_path='/path/to/your/tiger_openapi_config.properties')
protocol, host, port = config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'), client_config=config)

def on_quote(frame):
    print(f"{frame.symbol}: {frame.latest_price} ({frame.latest_change_percent}%)")

def on_order(frame):
    print(f"Order {frame.id}: {frame.status}, filled={frame.filled_quantity}")

def on_position(frame):
    print(f"{frame.symbol}: qty={frame.quantity}, pnl={frame.unrealized_pnl}")

def on_asset(frame):
    print(f"Net: {frame.net_liquidation}, Available: {frame.available_funds}")

def on_connected():
    print("Connected! Subscribing...")
    push_client.subscribe_quote(['AAPL', 'TSLA', '00700'])
    push_client.subscribe_order()
    push_client.subscribe_position()
    push_client.subscribe_asset()

def on_disconnected():
    print("Disconnected, will auto-reconnect...")

push_client.quote_changed = on_quote
push_client.order_changed = on_order
push_client.position_changed = on_position
push_client.asset_changed = on_asset
push_client.connect_callback = on_connected
push_client.disconnect_callback = on_disconnected

push_client.connect(config.tiger_id, config.private_key)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    push_client.disconnect()
    print("Disconnected")
```

---

## 带自动重连的断线处理 / Reconnection with Resubscription

```python
def on_disconnected():
    """断线回调，PushClient 会自动重连，重连后需要重新订阅"""
    print("Disconnected, auto-reconnecting...")

def on_connected():
    """重连成功后重新订阅"""
    print("Reconnected, resubscribing...")
    push_client.subscribe_quote(['AAPL', 'TSLA'])
    push_client.subscribe_order()

push_client.connect_callback = on_connected
push_client.disconnect_callback = on_disconnected
```

---

## STOMP 协议(备选) / STOMP Protocol (Alternative)

```python
from tigeropen.push.push_client import StompPushClient

protocol, host, port = client_config.socket_host_port
stomp_client = StompPushClient(host, port, use_ssl=(protocol == 'ssl'))
# 使用方式与 PushClient 类似 / Usage similar to PushClient
```

---

## 订阅限制 / Subscription Limits

订阅数量取决于行情权限等级(基于资产/交易量)：
Subscription limits depend on permission tier (based on assets/volume):

| 等级 Tier | 标准订阅 Standard | 深度订阅 Depth |
|----------|------------------|---------------|
| 基础 Base | 20 | 10 |
| 高级 Advanced ($50K+) | 100 | 50 |
| 顶级 Top ($1M+) | 2000 | 500 |

---

## 注意事项 / Notes

- 推荐 Protobuf 协议(默认)，性能优于 STOMP / Protobuf (default) recommended over STOMP
- PushClient 有自动重连机制 / Auto-reconnects after disconnection
- 同一 tiger_id 只能有一个推送连接 / Only one push connection per tiger_id
- 新连接会踢掉旧连接(触发 kickout_callback) / New connection kicks old one
- 订单/持仓/资产变动连接后自动推送 / Trade events auto-pushed after connect
- 行情推送需对应行情权限 / Quote push requires corresponding permissions
- 深度推送需 L2 权限 / Depth push requires L2 permission
- 断线重连后需重新订阅 / Resubscribe after reconnection
- `use_full_tick = True` 需在连接前设置 / Set before connect
