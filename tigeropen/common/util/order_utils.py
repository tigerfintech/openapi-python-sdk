# -*- coding: utf-8 -*-
"""
Created on 2018/11/1

@author: gaoan
"""
from tigeropen.trade.domain.order import Order, OrderLeg
from tigeropen.common.consts import OrderStatus


def market_order(account, contract, action, quantity):
    """
    市价单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :return:
    """
    return Order(account, contract, action, 'MKT', quantity)


def limit_order(account, contract, action, quantity, limit_price):
    """
    限价单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param limit_price: 限价的价格
    :return:
    """
    return Order(account, contract, action, 'LMT', quantity, limit_price=limit_price)


def stop_order(account, contract, action, quantity, aux_price):
    """
    止损单
    :param account:
    :param contract:
    :param action: BUY/SELL
    :param quantity:
    :param aux_price: 触发止损单的价格
    :return:
    """
    return Order(account, contract, action, 'STP', quantity, aux_price=aux_price)


def stop_limit_order(account, contract, action, quantity, limit_price, aux_price):
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
    return Order(account, contract, action, 'STP_LMT', quantity, limit_price=limit_price, aux_price=aux_price)


def trail_order(account, contract, action, quantity, trailing_percent=None, aux_price=None):
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
    return Order(account, contract, action, 'TRAIL', quantity, trailing_percent=trailing_percent, aux_price=aux_price)


def order_leg(leg_type, price, time_in_force='DAY', outside_rth=None):
    """
    附加订单
    :param leg_type: 附加订单类型. PROFIT 止盈单类型,  LOSS 止损单类型
    :param price: 附加订单价格.
    :param time_in_force: 附加订单有效期. 'DAY'（当日有效）和'GTC'（取消前有效 Good-Til-Canceled).
    :param outside_rth: 附加订单是否允许盘前盘后交易(美股专属). True 允许, False 不允许.
    """
    return OrderLeg(leg_type=leg_type, price=price, time_in_force=time_in_force, outside_rth=outside_rth)


def limit_order_with_legs(account, contract, action, quantity, limit_price, order_legs=None):
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
    return Order(account, contract, action, 'LMT', quantity, limit_price=limit_price, order_legs=order_legs)


def get_order_status(value):
    """
    Invalid(-2), Initial(-1), PendingCancel(3), Cancelled(4), Submitted(5), Filled(6), Inactive(7), PendingSubmit(8)
    :param value:
    :return:
    """
    if value == -1 or value == 'Initial':
        return OrderStatus.NEW
    elif value == 2 or value == 5 or value == 8 or value == 'Submitted' or value == 'PendingSubmit':
        return OrderStatus.HELD
    elif value == 3 or value == 'PendingCancel':
        return OrderStatus.PENDING_CANCEL
    elif value == 4 or value == 'Cancelled':
        return OrderStatus.CANCELLED
    elif value == 6 or value == 'Filled':
        return OrderStatus.FILLED
    elif value == 7 or value == 'Inactive':
        return OrderStatus.REJECTED
    elif value == -2 or value == 'Invalid':
        return OrderStatus.EXPIRED

    return OrderStatus.PENDING_NEW
