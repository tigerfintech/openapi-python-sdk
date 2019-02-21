
IS_SANDBOX = True
PRIVATE_KEY = ''
TIGER_ID = ''
ACCOUNT = ''  # 环球账户
STANDARD_ACCOUNT = None  # 标准账户


class MarketSetting:
    """不同市场的设置
    """
    def __init__(self, name):
        """
        :param name: 市场名称: 美股 US; 港股 HK; A股 CN;
        """
        self.name = name.upper() if name else 'US'
        self.TIMEZONE = None
        self.CURRENCY = None
        # 开盘时间
        self.OPEN_TIME = None
        # 收盘时间
        self.CLOSE_TIME = None
        # 午间休市开始时间
        self.LUNCH_BREAK_START_TIME = None
        # 午间休市结束时间
        self.LUNCH_BREAK_END_TIME = None

        self.init_setting()

    def init_setting(self):
        if self.name == 'US':
            self.TIMEZONE = 'US/Eastern'
            self.OPEN_TIME = '09:30:00'
            self.CLOSE_TIME = '16:00:00'
            self.CURRENCY = 'USD'

        elif self.name == 'HK':
            self.TIMEZONE = 'Asia/Hong_Kong'
            self.OPEN_TIME = '09:30:00'
            self.CLOSE_TIME = '16:00:00'
            self.LUNCH_BREAK_START_TIME = '12:00:00'
            self.LUNCH_BREAK_END_TIME = '13:00:00'
            self.CURRENCY = 'HKD'

        elif self.name == 'CN' or self.name == 'SH' or self.name == 'SZ':
            self.TIMEZONE = 'Asia/Shanghai'
            self.OPEN_TIME = '09:30:00'
            self.CLOSE_TIME = '15:00:00'
            self.LUNCH_BREAK_START_TIME = '11:30:00'
            self.LUNCH_BREAK_END_TIME = '13:00:00'
            self.CURRENCY = 'CNH'


# 设置市场
MARKET = MarketSetting('US')

# 是否使用时间事件驱动模式. 时间事件驱动模式兼容量化平台的策略. 若设置为 False 则使用行情驱动模式
EVENT_TRIGGER = True
# 时间事件驱动模式下策略运行频率 'minute' 或 'daily'
FREQUENCY = 'minute'

# [event trigger] this param is to balance the difference between local system time and the market data time,
# system delay time 5s
SYSTEM_DELAY = 5



