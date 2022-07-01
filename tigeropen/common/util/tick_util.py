# -*- coding: utf-8 -*-
# 
# @Date    : 2022/6/24
# @Author  : sukai

from tigeropen.common.consts.tick_constants import PART_CODE_MAP, PART_CODE_NAME_MAP, HK_QUOTE_LEVEL_PREFIX, \
    HK_TRADE_COND_MAP, US_TRADE_COND_MAP


def get_part_code(code):
    return PART_CODE_MAP.get(code)


def get_part_code_name(code):
    return PART_CODE_NAME_MAP.get(code)


def get_trade_condition_map(quote_level):
    if quote_level.lower().startswith(HK_QUOTE_LEVEL_PREFIX):
        return HK_TRADE_COND_MAP
    return US_TRADE_COND_MAP


def get_trade_condition(cond, cond_map):
    return cond_map.get(cond)


