# -*- coding: utf-8 -*-
"""
Created on 2018/11/1

@author: gaoan
"""
from tigeropen.trade.domain.contract import ContractLeg
from tigeropen.trade.domain.order import Order, OrderLeg, AlgoParams
from tigeropen.common.consts import OrderStatus, OrderType


def market_order(account, contract, action, quantity, time_in_force='DAY'):
    """
    市价单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :return:
    """
    return Order(account, contract, action, 'MKT', quantity, time_in_force=time_in_force)


def market_order_by_amount(account, contract, action, amount, time_in_force='DAY'):
    """
    按金额的市价单(用于基金)
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param amount:
    :return:
    """
    return Order(account, contract, action, 'MKT', total_cash_amount=amount, time_in_force=time_in_force)


def limit_order(account, contract, action, quantity, limit_price, time_in_force='DAY'):
    """
    限价单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param limit_price: 限价的价格
    :return:
    """
    return Order(account, contract, action, 'LMT', quantity, limit_price=limit_price, time_in_force=time_in_force)


def stop_order(account, contract, action, quantity, aux_price, time_in_force='DAY'):
    """
    止损单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param aux_price: 触发止损单的价格
    :return:
    """
    return Order(account, contract, action, 'STP', quantity, aux_price=aux_price, time_in_force=time_in_force)


def stop_limit_order(account, contract, action, quantity, limit_price, aux_price, time_in_force='DAY'):
    """
    限价止损单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param limit_price: 发出限价单的价格
    :param aux_price: 触发止损单的价格
    :return:
    """
    return Order(account, contract, action, 'STP_LMT', quantity, limit_price=limit_price, aux_price=aux_price,
                 time_in_force=time_in_force)


def trail_order(account, contract, action, quantity, trailing_percent=None, aux_price=None, time_in_force='DAY'):
    """
    移动止损单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param trailing_percent: 百分比 (0~100)
    :param aux_price: 价差  aux_price 和 trailing_percent 两者互斥
    :return:
    """
    return Order(account, contract, action, 'TRAIL', quantity, trailing_percent=trailing_percent,
                 aux_price=aux_price, time_in_force=time_in_force)


def auction_limit_order(account, contract, action, quantity, limit_price, time_in_force='DAY'):
    """
    竞价限价单 Auction Limit
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param limit_price: 限价的价格
    :param time_in_force: only support 'DAY' or 'OPG' (Opening Price Gap, 盘前竞价有效)
    :return:
    """
    return Order(account, contract, action, 'AL', quantity, limit_price=limit_price, outside_rth=True,
                 time_in_force=time_in_force)


def auction_market_order(account, contract, action, quantity, time_in_force='DAY'):
    """
    竞价市价单 Auction Market
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param time_in_force: only support 'DAY' or 'OPG' (Opening Price Gap, 盘前竞价有效)
    :return:
    """
    return Order(account, contract, action, 'AM', quantity, outside_rth=True, time_in_force=time_in_force)


def order_leg(leg_type, price=None, time_in_force='DAY', outside_rth=None, limit_price=None, trailing_percent=None,
              trailing_amount=None, quantity=None):
    """
    附加订单
    :param leg_type: 附加订单类型. PROFIT 止盈单类型,  LOSS 止损单类型； LMT/STP/STP_LMT 仅OCA订单支持
    :param price: 附加订单价格.
    :param time_in_force: 附加订单有效期. 'DAY'（当日有效）和'GTC'（取消前有效 Good-Til-Canceled).
    :param outside_rth: 附加订单是否允许盘前盘后交易(美股专属). True 允许, False 不允许.
    :param limit_price: attached stop loss order's limit price
    :param trailing_percent: attached trailing stop loss order's trailing percent
    :param trailing_amount: attached trailing stop loss order's trailing amount
    :param quantity: 数量
    """
    if leg_type == OrderType.LMT.value and limit_price is None:
        limit_price = price
    return OrderLeg(leg_type=leg_type, price=price, time_in_force=time_in_force, outside_rth=outside_rth,
                    limit_price=limit_price, trailing_percent=trailing_percent, trailing_amount=trailing_amount,
                    quantity=quantity)


def limit_order_with_legs(account, contract, action, quantity, limit_price, order_legs=None, time_in_force='DAY'):
    """
    限价单 + 附加订单(仅环球账户支持)
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param limit_price: 限价单价格
    :param order_legs: 附加订单列表
    :return:
    """
    if order_legs and len(order_legs) > 2:
        raise Exception('2 order legs at most')
    return Order(account, contract, action, 'LMT', quantity, limit_price=limit_price, order_legs=order_legs,
                 time_in_force=time_in_force)


def algo_order_params(start_time=None, end_time=None, no_take_liq=None, allow_past_end_time=None,
                      participation_rate=None):
    """
    算法订单参数
    :param start_time: 生效开始时间(时间戳 TWAP和VWAP专用)
    :param end_time: 生效结束时间(时间戳 TWAP和VWAP专用)
    :param no_take_liq: 是否尽可能减少交易次数(VWAP订单专用)
    :param allow_past_end_time: 是否允许生效时间结束后继续完成成交(TWAP和VWAP专用)
    :param participation_rate: 参与率(VWAP专用,0.01-0.5)
    :return:
    """
    return AlgoParams(start_time=start_time, end_time=end_time, no_take_liq=no_take_liq,
                      allow_past_end_time=allow_past_end_time, participation_rate=participation_rate)


def algo_order(account, contract, action, quantity, strategy, algo_params=None, limit_price=None, time_in_force='DAY'):
    """
    算法订单
    :param account:
    :param contract:
    :param action:
    :param quantity:
    :param strategy: 交易量加权平均价格（VWAP）/时间加权平均价格(TWAP)
    :param algo_params: tigeropen.trade.domain.order.AlgoParams
    :param limit_price:
    :return:
    """
    return Order(account, contract, action, order_type=strategy, quantity=quantity, algo_params=algo_params,
                 limit_price=limit_price, outside_rth=False, time_in_force=time_in_force)


def contract_leg(symbol=None, sec_type=None, expiry=None, strike=None, put_call=None, action=None,
                 ratio=1):
    return ContractLeg(symbol=symbol, sec_type=sec_type, expiry=expiry, strike=strike, put_call=put_call,
                       action=action, ratio=ratio)


def combo_order(account, contract_legs, combo_type, action, quantity, order_type=OrderType.LMT.value, limit_price=None,
                aux_price=None, trailing_percent=None):
    return Order(account, None, action=action, order_type=order_type, quantity=quantity, limit_price=limit_price,
                 aux_price=aux_price, trailing_percent=trailing_percent, combo_type=combo_type,
                 contract_legs=contract_legs)


def oca_order(account, contract, action, order_legs, quantity=None):
    return Order(account, contract, action=action, quantity=quantity, order_legs=order_legs,
                 order_type=OrderType.OCA.value)


def get_order_status(value, filled_quantity=0):
    """
    Invalid(-2), Initial(-1), PendingCancel(3), Cancelled(4), Submitted(5), Filled(6), Inactive(7), PendingSubmit(8)
    :param value:
    :param filled_quantity:
    :return:
    """
    if value in (-1, 'Initial', 'NEW', 'New'):
        return OrderStatus.NEW
    elif value in (2, 5, 8, 'Submitted', 'PendingSubmit', 'HELD', 'Held'):
        if Order.is_partially_filled(OrderStatus.HELD, filled_quantity):
            return OrderStatus.PARTIALLY_FILLED
        return OrderStatus.HELD
    elif value in (3, 'PendingCancel', 'PENDING_CANCEL'):
        return OrderStatus.PENDING_CANCEL
    elif value in (4, 'Cancelled', 'CANCELLED'):
        return OrderStatus.CANCELLED
    elif value in (6, 'Filled', 'FILLED'):
        return OrderStatus.FILLED
    elif value in (7, 'Inactive', 'REJECTED'):
        return OrderStatus.REJECTED
    elif value in (-2, 'Invalid', 'EXPIRED'):
        return OrderStatus.EXPIRED

    return OrderStatus.PENDING_NEW
