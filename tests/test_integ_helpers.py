# -*- coding: utf-8 -*-
"""tests/integ/_helpers.py 边界分类函数的单元测试。

分类词表决定集成测试把服务端报错判为「合法边界(skip)」还是「真实回归(fail)」。
词表漏一条新措辞,CI 在对应时段就会误报红 —— 例如 2026-11 美股夜盘对
cash-amount 订单的碎股拒绝。这里用服务端出现过的原文把分类行为钉住。
"""
import unittest

import pytest

from tests.integ._helpers import (
    _is_order_type_restriction,
    _is_trading_hours_error,
)

pytestmark = pytest.mark.unit


class _BoundaryError(Exception):
    """str() 形态对齐真实 ApiException 的报错文本。"""


class TestOrderTypeRestrictionClassification(unittest.TestCase):

    def test_overnight_fractional_share_rejection(self):
        # 2026-11 实测:美股夜盘(20:00–04:00 ET)里 cash-amount 订单数量
        # 由服务端计算为碎股,服务端按 bad_request 拒绝。
        exc = _BoundaryError(
            "standard account response error(bad_request:Orders that "
            "include a fraction of a share cannot be traded during the "
            "overnight session. You may choose a \"Trading Hour\" that "
            "does not include the overnight session or adjust your order "
            "quantity to include only whole shares.)")
        self.assertTrue(_is_order_type_restriction(exc))

    def test_rth_fractional_share_rejection(self):
        # 2026-08 实测:盘前/盘后时段同一规则的另一种措辞。
        exc = _BoundaryError(
            "standard account response error(bad_request:Only regular "
            "trading hours supported when trading fractional shares.)")
        self.assertTrue(_is_order_type_restriction(exc))

    def test_market_closed_is_not_order_type_restriction(self):
        # 「市场已收盘」属于 hours 分类(需市场状态复核),不能混进
        # 无条件 skip 的 order-type restriction。
        exc = _BoundaryError(
            "standard account response error(forbidden:market is closed.)")
        self.assertFalse(_is_order_type_restriction(exc))
        self.assertTrue(_is_trading_hours_error(exc))
