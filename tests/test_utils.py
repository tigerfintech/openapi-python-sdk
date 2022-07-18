# -*- coding: utf-8 -*-
# 
# @Date    : 2022/7/14
# @Author  : sukai
import unittest

from tigeropen.common.util.price_util import PriceUtil


class TestUtils(unittest.TestCase):
    def test_price_util(self):
        delta = 1e-6
        tick_sizes = [{'begin': '0', 'end': '1', 'type': 'CLOSED', 'tick_size': 0.0001},
                      {'begin': '1', 'end': 'Infinity', 'type': 'OPEN', 'tick_size': 0.01}]
        self.assertFalse(PriceUtil.match_tick_size(None, None))
        self.assertTrue(PriceUtil.match_tick_size(2.33, tick_sizes))
        self.assertTrue(PriceUtil.match_tick_size(2.3, tick_sizes))
        self.assertFalse(PriceUtil.match_tick_size(1.334, tick_sizes))
        self.assertTrue(PriceUtil.match_tick_size(0.5, tick_sizes))
        self.assertFalse(PriceUtil.match_tick_size(0.22223, tick_sizes))
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(2.334, tick_sizes, True), 2.34, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(2.334, tick_sizes, False), 2.33, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(2.3345, None), 2.3345, delta=delta)

        tick_sizes = [{'begin': '0', 'end': '1', 'type': 'CLOSED', 'tick_size': 0.0005},
                      {'begin': '1', 'end': '100', 'type': 'OPEN_CLOSED', 'tick_size': 0.05},
                      {'begin': '100', 'end': '1000', 'type': 'OPEN_CLOSED', 'tick_size': 1.0},
                      {'begin': '1000', 'end': '10000', 'type': 'OPEN_CLOSED', 'tick_size': 2.0},
                      {'begin': '10000', 'end': 'Infinity', 'type': 'OPEN', 'tick_size': 5.0}]
        self.assertTrue(PriceUtil.match_tick_size(0.0005, tick_sizes))
        self.assertTrue(PriceUtil.match_tick_size(1.15, tick_sizes))
        self.assertFalse(PriceUtil.match_tick_size(0.0008, tick_sizes))
        self.assertFalse(PriceUtil.match_tick_size(1.11, tick_sizes))
        self.assertTrue(PriceUtil.match_tick_size(300, tick_sizes))
        self.assertFalse(PriceUtil.match_tick_size(300.5, tick_sizes))
        self.assertFalse(PriceUtil.match_tick_size(5001, tick_sizes))
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(0.0021, tick_sizes), 0.002, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(0.0021, tick_sizes, True), 0.0025, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(3.027, tick_sizes), 3.0, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(3.027, tick_sizes, True), 3.05, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(200.5, tick_sizes), 200, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(2001, tick_sizes, True), 2002, delta=delta)
        self.assertAlmostEqual(PriceUtil.fix_price_by_tick_size(20001, tick_sizes, True), 20005, delta=delta)
