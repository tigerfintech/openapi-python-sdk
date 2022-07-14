# -*- coding: utf-8 -*-
# 
# @Date    : 2022/7/13
# @Author  : sukai
from decimal import Decimal, ROUND_DOWN

import math

from tigeropen.common.consts import TickSizeType


class PriceUtil:
    INFINITY = 'Infinity'
    RELATIVE_TOLERANCE = 1e-6

    @staticmethod
    def match_tick_size(price, tick_sizes):
        """
        check if the price matches the tick sizes
        :param price: user input price
        :param tick_sizes: tick sizes list like:
                        [{'begin': '0', 'end': '1', 'type': 'CLOSED', 'tick_size': 0.0001},
                        {'begin': '1', 'end': 'Infinity', 'type': 'OPEN', 'tick_size': 0.01}]
        :return:
        """
        if not price or not tick_sizes:
            return False
        fixed_price = PriceUtil.fix_price_by_tick_size(price=price, tick_sizes=tick_sizes)
        return math.isclose(price, fixed_price, rel_tol=PriceUtil.RELATIVE_TOLERANCE)

    @staticmethod
    def fix_price_by_tick_size(price, tick_sizes, is_up=False):
        """
        fix the user input price by tick sizes of the contract
        :param price:
        :param tick_sizes:
        :param is_up:
        :return:
        """
        if not price:
            return None
        tick_size_item = PriceUtil._find_tick_size_item(price=price, tick_sizes=tick_sizes)
        if not tick_size_item:
            return price
        min_tick = tick_size_item.get('tick_size')
        begin = tick_size_item.get('begin')
        return PriceUtil._round_with_tick(price=price, begin=begin, min_tick=min_tick, is_up=is_up)

    @staticmethod
    def _find_tick_size_item(price, tick_sizes):
        """
        :param price:
        :param tick_sizes: tick size infos, example:
                    [{'begin': '0', 'end': '1', 'type': 'CLOSED', 'tick_size': 0.0001},
                     {'begin': '1', 'end': 'Infinity', 'type': 'OPEN', 'tick_size': 0.01}]
        :return: dict
        """
        if not price or not tick_sizes:
            return None
        for item in tick_sizes:
            type_ = item.get('type')
            begin = float(item.get('begin'))
            end = float('inf') if PriceUtil.INFINITY == item.get('end') else float(item.get('end'))

            if TickSizeType.OPEN.value == type_:
                if begin < price < end:
                    return item
            elif TickSizeType.OPEN_CLOSED.value == type_:
                if begin < price <= end:
                    return item
            elif TickSizeType.CLOSED.value == type_:
                if begin <= price <= end:
                    return item
        return None

    @staticmethod
    def _round_with_tick(price, begin, min_tick, is_up):
        p = Decimal(str(price))
        t = Decimal(str(min_tick))
        base = Decimal(str(begin))
        multiple = (p - base) / t
        if multiple <= 0:
            return price
        if is_up:
            multiple += Decimal(1)

        return float(multiple.quantize(0, ROUND_DOWN) * t + base)
