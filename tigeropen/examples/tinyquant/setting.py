
# 是否兼容量化平台的策略
PLATFORM_COMPATIBLE = False

EVENT_TRIGGER = True
TIME_ZONE = 'Asia/Shanghai'
OPEN_TIME = '093000'
CLOSE_TIME = '160000'

# [event trigger] this param is to balance the difference between local system time and the market data time,
# system delay time 5s
SYSTEM_DELAY = 5

# [event trigger][not necessary setting] user customer lunch break
LUNCH_BREAK = '120000'
AFTERNOON_START = '130000'

IS_SANDBOX = True
PRIVATE_KEY = ''
TIGER_ID = ''
ACCOUNT = ''  # 环球账户
STANDARD_ACCOUNT = None  # 标准账户
