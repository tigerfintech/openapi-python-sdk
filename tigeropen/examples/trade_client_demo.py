# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import logging
import traceback

from tigeropen.trade.domain.order import OrderStatus
from tigeropen.trade.request.model import AccountsParams
from tigeropen.common.response import TigerResponse
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.trade.trade_client import TradeClient
from tigeropen.quote.request import OpenApiRequest
from tigeropen.examples.client_config import get_client_config
# from tigeropen.common.util.contract_utils import stock_contract, option_contract, future_contract
# from tigeropen.common.util.order_utils import limit_order

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a', )
logger = logging.getLogger('TigerOpenApi')

client_config = get_client_config()


def get_account_info():
    from tigeropen.common.consts.service_types import ACCOUNTS
    openapi_client = TigerOpenClient(client_config)
    account = AccountsParams()
    account.account = client_config.account
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
            print("%d,%s,%s" % (response.code, response.message, response.data))


def get_account_apis():
    openapi_client = TradeClient(client_config, logger=logger)
    openapi_client.get_managed_accounts()
    # 获取订单
    openapi_client.get_orders()
    # 获取未成交订单
    # openapi_client.get_open_orders()
    # 获取已成交订单
    # openapi_client.get_filled_orders(start_time='2019-05-01', end_time='2019-05-21')
    # 获取持仓
    openapi_client.get_positions()
    # 获取资产
    openapi_client.get_assets()


def trade_apis():
    account = client_config.account
    openapi_client = TradeClient(client_config, logger=logger)

    # stock
    contract = openapi_client.get_contracts('AAPL')[0]
    # 或者本地构造合约对象
    # contract = stock_contract(symbol='AAPL', currency='USD')

    # option
    # contract = option_contract(identifier='AAPL  190118P00160000')
    # future
    # contract = future_contract('CHF', 'USD', '20190617', multiplier=125000, exchange='GLOBEX')

    order = openapi_client.create_order(account, contract, 'BUY', 'LMT', 100, limit_price=5.0)
    # 或者本地构造订单对象
    # order = limit_order(account=account, contract=contract, action='BUY', quantity=100, limit_price=5.0)
    openapi_client.place_order(order)
    order_id = order.order_id  # you can operate order via id too

    new_order = openapi_client.get_order(order_id=order.order_id)
    assert order.order_id == new_order.order_id
    openapi_client.modify_order(new_order, quantity=150)
    new_order = openapi_client.get_order(order_id=order_id)
    assert new_order.quantity == 150
    openapi_client.cancel_order(order_id=order_id)
    new_order = openapi_client.get_order(order_id=order_id)
    assert new_order.status == OrderStatus.CANCELLED or new_order.status == OrderStatus.PENDING_CANCEL


if __name__ == '__main__':
    get_account_info()
    get_account_apis()
    trade_apis()
