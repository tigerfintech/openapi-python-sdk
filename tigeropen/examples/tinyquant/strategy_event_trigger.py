from .compatibility import *
from .order_methods import *

# 将策略填写在下方
# API 的文档请参考：https://web.itiger.com/tquant/docs/


# 策略初始化方法， 只在开始执行回测时运行一次
def initialize(context):
    context.asset = symbol('AAPL')


def handle_data(context, data):
    print(data.history(context.asset, ['open', 'high', 'low', 'close', 'volume'], 10, '1m'))
    print(data.current(context.asset, ['open', 'high', 'low', 'close', 'volume']))
