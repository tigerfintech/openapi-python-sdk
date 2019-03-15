量化交易引擎：

    引擎可以两种方式独立运行，包括：行情驱动，时间事件驱动。
    功能包含，持仓管理，资产管理，订单管理（全部订单，外挂订单）。
    支持A股市场，港股市场，美股市场。需分别设置对应的时区与开盘收盘时间
    A股及港股存在午休时间，需独立设置。
    支持盘中，盘前启动。
    盘前盘后交易需用户自行设置。


1.运行模式：
    
    行情驱动：on_ticker，将行情数据推送至strategy_quote_trigger:on_ticker
    时间事件驱动：handle_data, 开盘后每分钟会运行一次直至收盘
    支持盘前启动，盘中重启。
    盘中重启，当前的外挂订单是否撤单，需用户自行定义。

2.配置：

    setting.py 配置引擎及账户，私钥等信息。
    其中, 若 EVENT_TRIGGER = True 则为时间事件驱动模式运行(默认), False 则为行情驱动模式运行.



3.运行方式：

    python engine.py

4.修改策略：
    
    行情驱动 strategy_quote_trigger.py, 需实现:
    initialize: 交易开始时运行一次，进行初始化. 若是A股，则需要在此处调用 symbol 订阅要交易的标的；其他市场不需要显式订阅
    before_trading_start: (可选) 交易开始前运行一次，盘中启动时也运行。
    dump：(可选) 每日交易结束后执行。
    on_ticker：行情驱动策略入口
    
    
    时间事件驱动 strategy_event_trigger.py, 需实现:
    initialize: 交易开始时运行一次，进行初始化. 若是A股，则需要在此处调用 symbol 订阅要交易的标的；其他市场不需要显式订阅
    before_trading_start: (可选) 交易开始前运行一次，盘中启动时也运行。
    handle_data: 每个bar运行一次
    dump：(可选) 每日交易结束后执行。
    
5.注意事项

