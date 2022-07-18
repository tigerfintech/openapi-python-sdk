# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import logging
import traceback

from tigeropen.common.util.price_util import PriceUtil
from tigeropen.trade.domain.order import OrderStatus
from tigeropen.trade.request.model import AccountsParams
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.response import TigerResponse
from tigeropen.common.request import OpenApiRequest
from tigeropen.common.consts import Currency, SecurityType
from tigeropen.common.util.contract_utils import stock_contract, option_contract_by_symbol, future_contract, \
     war_contract_by_symbol, iopt_contract_by_symbol
from tigeropen.common.util.order_utils import limit_order, limit_order_with_legs, order_leg, algo_order_params, \
    algo_order
from tigeropen.examples.client_config import get_client_config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a', )
logger = logging.getLogger('TigerOpenApi')

client_config = get_client_config()


def get_contract_apis():
    openapi_client = TradeClient(client_config, logger=logger)
    contract = openapi_client.get_contracts('AAPL')[0]
    print(contract)
    contract = openapi_client.get_contract('AAPL', SecurityType.STK, currency=Currency.USD)
    print(contract)
    # get derivative contracts of stock. include OPT, WAR, IOPT
    contracts = openapi_client.get_derivative_contracts('00700', SecurityType.WAR, '20220929')
    print(contracts)

def get_account_apis():
    openapi_client = TradeClient(client_config, logger=logger)
    openapi_client.get_managed_accounts()
    # 获取订单
    openapi_client.get_orders()
    # 获取未成交订单
    # openapi_client.get_open_orders()
    # 获取已成交订单
    # openapi_client.get_filled_orders(start_time='2019-05-01', end_time='2019-05-21')

    # 获取订单成交记录, 仅适用于综合账户
    transactions = openapi_client.get_transactions(symbol='AAPL', sec_type=SecurityType.STK, start_time=1641398400000,
                                                   end_time=1642398400000)
    # transactions = openapi_client.get_transactions(symbol='CL2201', sec_type=SecurityType.FUT)
    # transactions = openapi_client.get_transactions(order_id=24844739769009152)
    # transactions = openapi_client.get_transactions(symbol='BABA', sec_type='OPT', strike=121, expiry='20220121',
    #                put_call='CALL')

    # 获取持仓
    openapi_client.get_positions()
    # 获取资产
    openapi_client.get_assets()
    # 综合/模拟账户获取资产
    openapi_client.get_prime_assets()

    # get asset history
    openapi_client.get_analytics_asset(start_date='2021-12-01', end_date='2021-12-07')


def trade_apis():
    account = client_config.account
    openapi_client = TradeClient(client_config, logger=logger)

    # 通过请求获取合约
    contract = openapi_client.get_contracts('AAPL')[0]
    # contract = openapi_client.get_contract('AAPL', SecurityType.STK, currency=Currency.USD)

    # 本地构造合约
    # stock 股票
    # contract = stock_contract(symbol='AAPL', currency='USD')
    # option 期权
    # contract = option_contract(identifier='AAPL  190118P00160000')
    # contract = option_contract_by_symbol('AAPL', '20200110', strike=280.0, put_call='PUT', currency='USD')
    # future 期货
    # contract = future_contract('CHF', 'USD', '20190617', multiplier=125000, exchange='GLOBEX')
    # war 港股窝轮
    # contract = war_contract_by_symbol('02318', '20200326', 107.08, 'CALL', local_symbol='12616', currency='HKD')
    # iopt 港股牛熊证
    # contract = iopt_contract_by_symbol('02318', '20200420', 87.4, 'CALL', local_symbol='63379', currency='HKD')

    order = openapi_client.create_order(account, contract, 'BUY', 'LMT', 100, limit_price=5.0)
    # 或者本地构造订单对象
    # order = limit_order(account=account, contract=contract, action='BUY', quantity=100, limit_price=5.0)
    openapi_client.place_order(order)

    new_order = openapi_client.get_order(id=order.id)
    assert order.order_id == new_order.order_id
    openapi_client.modify_order(new_order, quantity=150)
    new_order = openapi_client.get_order(id=order.id)
    assert new_order.quantity == 150
    openapi_client.cancel_order(id=order.id)
    new_order = openapi_client.get_order(id=order.id)
    assert new_order.status == OrderStatus.CANCELLED or new_order.status == OrderStatus.PENDING_CANCEL

    # 预览订单 (下单前后保证金要求, 佣金等预览)
    result = openapi_client.preview_order(order)
    print(result)

    # 限价单 + 附加订单 (仅主订单为限价单时支持附加订单)
    stop_loss_order_leg = order_leg('LOSS', 8.0, time_in_force='GTC')  # 附加止损
    profit_taker_order_leg = order_leg('PROFIT', 12.0, time_in_force='GTC')  # 附加止盈

    main_order = openapi_client.create_order(account, contract, 'BUY', 'LMT', quantity=100, limit_price=10.0,
                                             order_legs=[stop_loss_order_leg, profit_taker_order_leg])
    # 本地构造限价单 + 附加订单
    # main_order = limit_order_with_legs(account, contract, 'BUY', 100, limit_price=10.0,
    # order_legs=[stop_loss_order_leg])

    openapi_client.place_order(main_order)
    print(main_order)
    # 查询主订单所关联的附加订单
    order_legs = openapi_client.get_open_orders(account, parent_id=main_order.order_id)
    print(order_legs)

    # adjust price by contract tick sizes
    contract = openapi_client.get_contract('UVXY')
    price = 10.125
    if not PriceUtil.match_tick_size(price, contract.tick_sizes):
        price = PriceUtil.fix_price_by_tick_size(price, contract.tick_sizes)



def algo_order_demo():
    account = client_config.account
    openapi_client = TradeClient(client_config, logger=logger)
    contract = stock_contract(symbol='AAPL', currency='USD')
    params = algo_order_params(start_time='2020-11-19 23:00:00', end_time='2020-11-19 23:50:00', no_take_liq=True,
                               allow_past_end_time=True, participation_rate=0.1)
    order = algo_order(account, contract, 'BUY', 1000, 'VWAP', algo_params=params, limit_price=100.0)
    openapi_client.place_order(order)
    print(order)


def get_account_info():
    """
    request by build OpenApiRequest. Not recommend.
    :return:
    """
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


if __name__ == '__main__':
    get_account_apis()
    trade_apis()
