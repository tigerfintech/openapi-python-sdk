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
