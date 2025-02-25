## 3.3.2 (2025-02-25)
### New
- `QuoteClient.get_trade_rank` 热门交易榜
### Mod
- Contract 添加属性 lot_size

## 3.3.1 (2024-12-31)
### New
- `TradeClient.get_funding_history` 出入金历史查询
### Mod
- `QuoteClient.get_bars` 增加 `trade_session` 参数

## 3.3.0 (2024-12-17)
### New
- `QuoteClient.get_stock_fundamental` 获取股票基础数据, 如 ROE, PB
### Fix
- 长连接 `error_callback` 未调用的问题

## 3.2.9 (2024-11-25)
### Fix
- 修复批量获取合约 `TradeClient.get_contracts` 传参错误

## 3.2.8 (2024-11-11)
### Modify
- `TradeClient.get_order` 新增参数 `show_charges`, 订单对象 Order 新增 `charges` 返回佣金明细
- 综合账户资产增加字段 `uncollected`, `locked_funds`
- 推送持仓对象 `PositionData` 新增字段 `positionQty`, `salableQty`

## 3.2.7 (2024-07-12)
### Modify
- `TradeClient.get_positions` 新增字段 `position_qty`, `salable_qty`, `today_pnl`, `last_close_price` 等


## 3.2.6 (2024-07-03)
### Fix
- `QuoteClient.get_option_depth` 修复返回数据处理

# 3.2.5 (2024-06-19)
### New
- 新增 `QuoteClient.get_option_depth`, `QuoteClient.get_option_symbols`
### Modify
- `QuoteClient.get_option_chain` 增加参数 `market`
- `QuoteClient.get_option_briefs` 增加参数 `market`
- `QuoteClient.get_option_expirations` 增加参数 `market`

# 3.2.4 (2024-06-05)
### Modify
- 下单支持夜盘参数, 可通过修改订单对象的 `order.trading_session_type` 来设置
- Position 增加字段 `mm_value`, `mm_percent`

# 3.2.3 (2024-04-11)
### Fix
- `QuoteClient.get_option_expirations` 修复多标的时 pandas 处理列名的问题

# 3.2.2 (2024-04-09)
### New
- 长链接全量 tick 推送
- `TradeClient.get_open_orders` `get_filled_orders` 增加 `limit` 参数

# 3.2.1 (2024-04-09)
### Fix
- `QuoteClient.get_option_briefs` 返回补充字段 `change`

# 3.2.0 (2024-04-02)
### Modify
- `QuoteClient.get_option_chain` 增加参数 `return_greek_value`
### Breaking
- `TradeClieng.get_managed_accounts` 此前不传 `account` 参数时，会设置默认账户，现改为不设置默认账户

# 3.1.9 (2024-03-18)
### New
- 长链接分钟k线推送
### Modify
- `QuoteClient.get_option_chain` 参数 `option_filter` 默认值优化
- `QuoteClient.get_option_expirations` 返回增加周期字段

# 3.1.8 (2024-03-12)
### Modify
- `Order` 增加字段 `quantity_scale` 用于碎股下单指定小数数量
### Fix
- 处理合约 tick 的 PriceUtil 补充一种枚举类型 CLOSED_OPEN

# 3.1.7 (2024-02-28)
### Fix
- 订单推送 commissionAndFee 类型由 double 回滚为 float

# 3.1.6 (2024-02-26)
### Modify
- `Order` 及订单推送数据增加字段 `gst`; 订单推送 commissionAndFee 类型由 float 改为 double

# 3.1.5 (2024-01-19)
### Fix
- 修复长链接 protobuf 消息帧生成问题导致的无法连接问题

# 3.1.4 (2024-01-19)
### Modify
- 优化http请求，复用连接
- 优化rsa签名

# 3.1.3 (2024-01-04)
### Modify
- `QuoteClient.get_symbol_names` 支持 OTC
- `TradeClient.get_prime_assets` 支持 consolidated 参数
### Fix
- `QuoteClient.get_market_scanner_tags` multi_tags_fields 不生效的bug

# 3.1.2 (2023-11-17)
### New
- 支持美股期权深度行情订阅

# 3.1.1 (2023-10-18)
### New
- 支持 OCA 订单，通过 `tigeropen.common.util.order_utils.oca_order` 构造

### Modify
- `QuoteClient.get_timeline` 默认调用 3.0 版本api

# 3.1.0 (2023-10-11)
### Fix
- 修复长连接 `subscribe_option_top` 的枚举参数

# 3.0.9 (2023-08-29)
### Modify
- Order 对象补充字段 `latest_price`

## 3.0.8 (2023-08-16)
### New
- 添加示例代码


## 3.0.7 (2023-08-11)
### New
- 新增基金相关接口
  `QuoteClient.get_fund_symbols` 基金代码列表  
  `QuoteClient.get_fund_quote` 基金行情
  `QuoteClient.get_fund_history_quote` 基金历史行情
  `QuoteClient.get_fund_contracts` 基金合约
- 订单数据推送中新增字段 `totalCashAmount`, `filledCashAmount`
- PushClient 可自定义心跳回调方法

## 3.0.6 (2023-07-31)
### Modify
- 长链接添加统一异常处理

## 3.0.5 (2023-07-24)
### Fix
- 修复长链接订单状态推送时，部分成交状态未转换为对应枚举值的问题

## 3.0.4 (2023-07-19)
### New
- 获取市场股票代码接口 `QuoteClient.get_symbols` 增加参数 `include_otc` 参数，支持返回OTC市场symbol

### Breaking
- 长链接订单状态回调中，回调数据对象 `tigeropen.push.pb.OrderStatusData_pb2.OrderStatusData` 的 `status` 
  字段改为 `tigeropen.common.consts.OrderStatus` 枚举名称的字符串，可通过 `OrderStatus[frame.status]` 或
  `get_order_status(frame.status)` 转换为 `OrderStatus` 枚举

## 3.0.3 (2023-07-10)
### New
- 股票实时行情接口 `QuoteClient.get_stock_briefs` 增加 `include_hour_trading` 参数, 支持返回盘前盘后数据

## 3.0.2 (2023-07-07)
### New
- 期权k线接口支持排序方向参数 `sort_dir`
### Fix
- 修复长链接重连问题

## 3.0.1 (2023-06-21)
### New
- 历史K线额度接口
- 持仓对象新增按均价计算的盈亏字段
- 长链接新增榜单数据推送

## 3.0.0 (2023-06-08)
### Breaking
- 长链接由默认stomp改为默认使用protobuf

## 2.4.0 (2023-06-07)
### New
- 支持期权组合订单
### Fix
- 修复分页获取k线数据为空时pandas字段索引错误

## 2.3.9 (2023-06-01)
### Fix
- 修复protobuf推送tick数据未解压的问题
### Modify
- 修改订单状态推送proto定义，增加 userMark

## 2.3.8 (2023-05-09)
### New
- 合约接口新增字段保证金优惠信息
- QuoteClient 新增获取选股器tag查询接口
### Modify
- 修改选股器部分字段

## 2.3.7 (2023-04-18)
### New
- TradeClient 新增预估可卖数量接口 `TradeClient.get_estimate_tradable_quantity`
- `Order` 订单对象新增字段 `external_id`
- `Position` 持仓对象新增字段 `saleable`，仅A股有值; 持仓推送对象增加 `saleable` 字段


## 2.3.6 (2023-04-11)
### New
- QuoteClient 新增窝轮牛熊证筛选接口 `QuoteClient.get_warrant_filter`, 窝轮牛熊证实时行情接口 `QuoteClient.get_warrant_briefs`
- `QuoteClient.get_option_bars` 期权k线接口新增参数 `limit`


## 2.3.5 (2023-03-28)
### New
- TradeClient 新增不同品种(股票SEC/期货FUT/基金FUND)账户间资金划转接口
  `TradeClient.get_segment_fund_available`  获取可划转资金  
  `TradeClient.transfer_segment_fund`  划转资金  
  `TradeClient.cancel_segment_fund`  取消划转  
  `TradeClient.get_segment_fund_history`  获取划转历史  
  
- TradeClient 新增换汇下单接口
  `TradeClient.place_forex_order`
  
- `QuoteClient.get_option_bars` 期权k线接口新增参数 `period`, 支持获取分钟k线


## 2.3.4 (2023-03-20)
### New
- 支持AM/AL(盘前竞价单)
### Fix
- 修复PushClient报错模块找不到的问题

## 2.3.3 (2023-03-10)
### Modify
- 支持多进程运行场景下的 token 刷新，需安装 pip install watchdog 已开启 token 文件监听
### Fix
- 修复日历接口


## 2.3.2 (2023-03-03)
### New
- PushClient长链接支持Protobuf，当前版本默认不开启，可通过在 PushClient 初始化时传人 `user_protobuf=True ` 开启，
未来版本将默认使用Protobuf。
  Protobuf方式的订阅方式与之前版本基本兼容一致；回调方法的参数改用Protobuf对象，与之前不兼容，

## 2.3.1 (2023-02-23)
### New
- 支持2FA token自定义刷新间隔，可通过 client_config.token_refresh_duration = 0 关闭自动刷新
### Fix
- tick数据推送字段异常问题
- 若开启token，刷新线程不随主线程退出的问题


## 2.3.0 (2023-02-16)
### New
- 支持配置文件
- 支持2FA token


## 2.2.9 (2023-02-09)
### Fix
- 修复tick数据推送报错的问题
### Modify
- 除下单/改单/撤单外的接口，增加重试机制。默认重试5次，可通过 client_config.retry_max_tries 参数修改，设置为0则不进行重试


## 2.2.8 (2023-02-03)
### Fix
- 修复期权合约四要素解析工具无法处理部分港股期权的问题


## 2.2.7 (2023-01-11)
### New
- 支持配置日志路径


## 2.2.6 (2022-12-14)
### Fix
- 修复 Windows 系统编码为gbk时安装报编码错误的问题

## 2.2.5 (2022-12-12)
### New
- `TradeClient.get_contract` 返回的合约对象 `tigeropen.trade.domain.contract.Contract` 新增属性: `is_etf`, `etf_leverage`


## 2.2.4 (2022-12-09)
### New
- 资金流接口 `QuoteClient.get_capital_flow`
- 资金分布接口 `QuoteClient.get_capital_distribution`
- 港股经纪商接口 `QuoteClient.get_stock_broker`


## 2.2.3 (2022-12-07)
### new
- 选股器 `QuoteClient.market_scanner`


## 2.2.2 (2022-11-22)
### New
- 订单支持GTD类型, 下单时可通过指定 Order 属性 time_in_force = "GTD" 设置
- 订单成交明细支持长链接订阅推送

## 2.2.1 (2022-11-07)
### Fixed
- 修复 `TradeClient.get_trade_ticks` begin_index 参数传 0 不生效的问题


## 2.2.0 (2022-11-01)
### New
- 长链接支持期货逐笔推送. 可通过 `PushClient.subscribe_tick` 订阅，使用 `PushClient.tick_changed` 接收回调


## 2.1.9 (2022-10-12)
### New
- 支持多牌照配置, 分牌照请求不同域名. 可通过 client_config.license 指定牌照
### Modify
- `Contract` 新增属性 `short_initial_margin`, `short_maintenance_margin`, 新增方法 `to_str()` 可打印全部属性
- `QuoteClient.get_financial_report` 增加参数 `begin_date`, `end_date`
- `QuoteClient.get_trade_ticks` 兼容 1.0 版本接口


## 2.1.8 (2022-08-26)
### Modify
- `TradeClient.get_orders` 新增参数 `seg_type`， 可指定交易品种(证券SEC/期货FUT/全部ALL)  
- `PushClient` 修改自动重连重试次数
- `TradeClient.get_contract` 接口版本升级到V3
### Fixed
- 修复 `TradeClient.get_contract` 获取港股期权合约时返回空的问题


## 2.1.7 (2022-08-19)
### New
- 新增获取期货某类型所有合约接口 `QuoteClient.get_all_future_contracts`
- 附加订单支持追踪止损单

### Breaking
- 期货tick接口 `QuoteClient.get_future_trade_ticks`, 合约参数由接受列表改为只接受单个合约

## 2.1.6 (2022-08-11)
### Modify
- 支持全局时区配置， 可通过 ClientConfig.timezone 设置时区


## 2.1.5 (2022-08-01) 
### Modify
- 交易相关接口支持全局语言配置, 可通过 ClientConfig.language 改变默认语言


## 2.1.4 (2022-07-18)
### New
- 新增历史资产分析接口 `TradeClient.get_analytics_asset`
- 新增合约价格校正工具函数 `tigeropen.common.util.price_util.PriceUtil`, 可根据请求到的合约tick size, 校正输入的下单价格
- 订单对象新增属性: 更新时间: `update_time`
- 查询订单列表接口 `TradeClieng.get_orders (get_open_orders/get_filled_orders)` 支持指定排序规则, 按照订单创建时间或订单状态更新时间排序
- 查询持仓接口 `TradeClient.get_positions` 支持期权要素(expiry, strike, put_call)参数过滤


## 2.1.3 (2022-07-01)
### New
- 长连接新增逐笔订阅: `PushClient.subscribe_tick`, 退订 `PushClient.unsubscribe_tick`
- 新增已订阅查询回调方法 `PushClient.query_subscribed_callback` 取代旧有的 `Pushclient.subscribed_symbols`
- `QuoteClient.get_trade_ticks` 新增 `trade_session` 参数，可指定该参数查询盘前盘后数据

### Modify
- `Pushclient.subscribed_symbols` 标记为废弃


## 2.1.2 (2022-06-14)
### Modify
- 升级 stomp.py 版本, 将之前的 4.1.24 升级到 8.0.1
### Breaking
- PushClient 去除 `auto_reconnect` 参数，如需自定义重连方式，可自定义方法并绑定 `disconnect_callback` 进行重连
- 处理连接被踢的情况，如果有多台设备使用相同 tiger_id 连接, 新连接会将较早的连接踢掉，较早连接会抛出异常，停止接收消息

## 2.1.1 (2022-05-25)
### New
- 新增批量分页获取k线接口
  股票：`QuoteClient.get_bars_by_page`
  期货：`QuoteClient.get_future_bars_by_page`
- `QuoteClient.get_future_bars`, `QuoteClient.get_bars` 增加 `page_token` 参数，可用于分页请求定位下一页位置
- `tigeropen.trade.domain.order.Order` 新增 `user_mark` 属性，用户下单时可传入一定长度的备注信息，该属性值在查询订单时会返回。(需用户提前向平台申请配置)

## 2.1.0 (2022-05-07)
### New
- 动态获取服务域名；更改默认域名
- 新增期权计算工具(examples.option_helpers.helpers)
- 新增根据期货代码获取期货合约接口 `QuoteClient.get_future_contract`
- 新增根据正股查衍生合约接口 `TradeClient.get_derivative_contracts`


## 2.0.9 (2022-04-18)
### New
- 新增历史分时接口 `QuoteClient.get_timeline_history`
- Order 对象新增字段
  sub_ids: 附加订单子订单id列表(仅在下附加订单时此字段会有值)
  adjust_limit: 限价单价格调整限制比例(作为下单参数使用, 查询时不返回)
  
### Breaking
- 下单 `TradeClient.place_order`, 改单 `TradeClient.modify_order`, 撤单 `TradeClient.cancel_order` 三个接口返回值，由之前的
  `True` 或 `False` 改为订单 id
- 行情权限抢占，改为在 `QuoteClient` 初始化时默认自动抢占，提供参数 `is_grab_permission` 可配置为不自动抢占。若该参数设置为 `False`, 
  则需用户自行调用 `QuoteClient.grab_quote_permission()` 进行行情权限抢占


## 2.0.7 (2022-01-31)
### Modify
- 修改服务域名

## 2.0.6 (2022-01-24)
### New 
- Contract 合约对象新增字段。  
  marginable：是否可融资  
  close_only：是否只允许平仓   
  shortable_count：做空池剩余  
- Order 订单对象新增字段。
  attr_desc：属性描述（如期权是否为被动行权）  
  source：订单来源  

### Breaking
- 将 `tigeropen.quote.request.OpenApiRequest` 移动到 `tigeropen.common.request.OpenApiRequest`


## 2.0.5 (2022-01-10)
### New
- 查询行情权限接口 QuoteClient.get_quote_permission
- 订单综合账户成交记录接口 TradeClient.get_transactions
- 增加一个完整的策略示例

### Changed
- 方法枚举参数优化，使用枚举参数的方法也可以直接使用该枚举对应值
- TradeClient.place_order 去除返回数据中 Order.order_id 属性的校验
- 将 SDK 内部的日志级别由 INFO 调整为 DEBUG, 防止默认情况下输出 SDK 的日志
- 去除 pandas 固定版本号, 方便安装时灵活指定版本

### Breaking
- 行情权限抢占接口 QuoteClient.grab_quote_permission 返回的数据项中，'expireAt' 字段格式转换为 'expire_at'

## 2.0.4 (2021-12-08)
### New
- 综合/模拟账户查询资产接口 TradeClient.get_prime_assets

## 2.0.3 (2021-12-01)
### New
- 期权链查询接口支持过滤 QuoteClient.get_option_chain 
- 新增延迟行情接口 QuoteClient.get_stock_delay_briefs

## 2.0.2 (2021-11-01)
### Changed
-  移除 client_config 中不常用的属性
-  长链接订阅优化

## 2.0.1 (2021-09-18)
### Breaking
-  移除 python2 的兼容

## 1.4.0 (2021-06-28)
### New
-  新增深度行情查询及订阅
-  新增行情权限抢占接口

## 1.2.0 (2020-04-02)
### New
-  新增行业接口

## 1.1.10 (2020-01-19)
### New
-  新增公司行动日历数据
-  新增附加订单（仅环球账户）

## 1.1.9 (2019-10-28)
### Fixed
-  修复 1.1.8 的安装问题

## 1.1.8 (2019-10-27)
### New
-  持仓、订单相关接口中增加identifier，做为相关标的的唯一识别符。
-  期权增增加 underlying asset 的历史波动率

## 1.1.7 (2019-08-02)
### New
-  期货行情的推送价格默认处理为小数
-  订单与持仓推送中增加 symbol 字段（请注意标准账户与环球账户的差异）
-  账户资产（asset）推送中新增 segment ，表示推送的账户类型。
-  股票合约中增加保证金交易相关数据
-  example 中增加了一个示例策略
-  新增一个生成 client_config 的方法


## 1.1.6 (2019-07-12)
### New
-  支持按照 account 订阅持仓、订单、资产信息

## 1.1.5 (2019-06-27)
### New
-  get_contracts 支持批量获取合约
-  PushClient 中的行情支持按照成交与报价分类订阅
-  PushClient 修复盘前成交推送的bug
-  PushClient 中的时间戳改为按需推送，不再需要单独订阅
-  重新梳理了get_assets接口，股票与期货交易使用更加清晰
### Documentation
-  SDK 中补全了文档，方便在IDE中快速查看


## 1.1.4 (2019-06-06)
### New
-  创建订单不再需要联网请求合约数据和申请订单号， 减少为 place_order 一个请求
-  获取订单列表，订单列表支持一次查询股票和期货订单
-  行情订阅的 focus_key 订阅逻辑修复， 支持订阅指定字段的推送
-  get_order 支持按照 id 查询订单
-  get_trade_ticks 返回多只股票
-  新增公司行动数据 API， 含分红以及拆合股数据
-  添加基本面 API，含日级别的估值数据以及财报级别的三大报表及衍生因子
-  增加已成交、待撤销和已撤销的订单列表
-  push_client 中新增加分钟分时的推送
-  push_client 中的订单状态改为 OrderStatus 对象
-  push_client 中增加心跳，减少链接断开的可能
-  期货增加 3min、45min 等周期行情的查询， 修复期货 1min 周期的查询
### Fixed
-  修复 get_orders 的 sec_type 无效的问题
