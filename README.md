# TigerOpen - 老虎量化开放平台 (Tiger Quant Open API)

### 简介

老虎开放平台可以为个人开发者和机构客户提供接口服务，投资者可以充分的利用老虎的交易服务、行情服务、账户服务等实现自己的投资应用程序。

- [官方在线文档](https://quant.itiger.com/openapi/zh/python/overview/introduction.html)

-------------------

### 安装
```
pip install tigeropen

或者

git clone https://github.com/tigerfintech/openapi-python-sdk.git
python setup.py install

```

### 使用须知

- 接入前需要在[开放平台](https://quant.itiger.com/#openapi)登记开发者信息
- 详情查看[接入说明](https://quant.itiger.com/openapi/zh/python/overview/introduction.html)

###### 注: 本SDK当前支持 Python3.4 及以上版本

---

### 快速上手
- 行情和交易接口
```
import traceback

from tigeropen.common.consts import Language, Market, TimelinePeriod, QuoteRight
from tigeropen.common.response import TigerResponse
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.quote.request import OpenApiRequest
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.common.consts.service_types import ACCOUNTS
from tigeropen.trade.request.model import AccountsParams
from tigeropen.trade.trade_client import TradeClient


def get_client_config():
    """
    :return:
    """
    is_sandbox = False
    client_config = TigerOpenClientConfig(sandbox_debug=is_sandbox)
    client_config.private_key = read_private_key('your private key file path')
    client_config.tiger_id = 'your tiger id'
    client_config.account = 'your account'
    client_config.language = Language.en_US
    return client_config

def get_account_info():
    client_config = get_client_config()
    openapi_client = TigerOpenClient(client_config)
    account = AccountsParams()
    account.account = 'DU575569'
    request = OpenApiRequest(method=ACCOUNTS, biz_model=account)

    response_content = None
    try:
        response_content = openapi_client.execute(request)
    except Exception as e:
        print(traceback.format_exc())
    if not response_content:
        print("failed to execute")
    else:
        response = TigerResponse()
        response.parse_response_content(response_content)
        if response.is_success():
            print("get response data:" + response.data)
        else:
            print(response.code + "," + response.msg + "," + response.data)

def get_trade_apis():
    client_config = get_client_config()
    trade_client = TradeClient(client_config)
    trade_client.get_managed_accounts()
    
def get_quote_apis():
    client_config = get_client_config()
    quote_client = QuoteClient(client_config)
    quote_client.get_market_status(Market.US)
    quote_client.get_briefs(symbols=['AAPL', '00700', '600519'], include_ask_bid=True, right=QuoteRight.BR)
    quote_client.get_timeline(['AAPL'], period=TimelinePeriod.DAY, include_hour_trading=True)
    quote_client.get_bars(['AAPL'])
    
def get_option_quote():
    client_config = get_client_config()
    quote_client = QuoteClient(client_config)
    symbol = 'AAPL'
    expirations = quote_client.get_option_expirations(symbols=[symbol])
    if len(expirations) > 1:
        expiry = int(expirations[expirations['symbol'] == symbol].at[0, 'timestamp'])
        quote_client.get_option_chain(symbol, expiry)

    quote_client.get_option_briefs(['AAPL  190104C00121000'])
    quote_client.get_option_bars(['AAPL  190104P00134000'])
    quote_client.get_option_trade_ticks(['AAPL  190104P00134000'])


def get_future_quote():
    client_config = get_client_config()
    quote_client = QuoteClient(client_config)
    exchanges = quote_client.get_future_exchanges()
    print(exchanges)
    quote_client.get_future_bars(['CN1901'], begin_time=-1, end_time=1545105097358)
    quote_client.get_future_trade_ticks(['CN1901'])
    quote_client.get_future_contracts('CME')
    quote_client.get_future_trading_times('CN1901', trading_date=1545049282852)
    quote_client.get_future_brief(['ES1906', 'CN1901'])

```

- 行情和交易信息推送
```
from tigeropen.common.consts import Language
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.push.push_client import PushClient
from tigeropen.tiger_open_config import TigerOpenClientConfig


def on_query_subscribed_quote(symbols, focus_keys, limit, used):
    print(symbols, focus_keys, limit, used)


def on_quote_changed(symbol, items, hour_trading):
    print(symbol, items, hour_trading)


is_sandbox = False
client_config = TigerOpenClientConfig(sandbox_debug=is_sandbox)
client_config.private_key = read_private_key('your private key file path')
# https://www.itiger.com/openapi/info 开发者信息获取
client_config.tiger_id = 'your tiger id'
client_config.account = 'your account'
client_config.language = Language.en_US
protocol, host, port = client_config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))
push_client.quote_changed = on_quote_changed
push_client.subscribed_symbols = on_query_subscribed_quote
push_client.connect(client_config.tiger_id, client_config.private_key)
push_client.query_subscribed_quote()
push_client.subscribe_quote(['AAPL', 'GOOG'])
push_client.subscribe_asset()

time.sleep(600)
push_client.disconnect()

```

---

### 示例代码

- 示例代码位于目录: (tigeropen包安装目录)/tigeropen/examples

***

### 开放平台及量化平台交流

* 老虎量化QQ群(869893807) 
* 团队或公司客户请在入群后联系群主

***

### 使用说明

* 有任何问题可以到 issues  处提出，我们会及时进行解答。
* 使用新版本时请先仔细阅读接口文档，大部分问题都可以在接口文档中找到你想要的答案。
* 欢迎大家提出建议、也可以提出各种需求，我们一定会尽量满足大家的需求。

---