# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from enum import Enum

import delorean
import pytz

from tigeropen.common.consts import Market

eastern = pytz.timezone('US/Eastern')
china = pytz.timezone('Asia/Shanghai')
hongkong = pytz.timezone('Asia/Hong_Kong')


def has_value(m, key):
    if not m:
        return False
    if key not in m:
        return False
    if not m[key]:
        return False
    return True


def get_enum_value(e, enum_type=None):
    if enum_type is None:
        return e.value if isinstance(e, Enum) else e
    return e.value if isinstance(e, enum_type) else e


def date_str_to_timestamp(dt, timezone):
    """
    :param dt: date str. like "2019-01-01" or "2019-01-01 12:00:00"
    :param timezone: pytz timezone
    :return: timestamp in milliseconds
    """
    try:
        if isinstance(dt, str) and timezone:
            return int(delorean.parse(dt, timezone=timezone, dayfirst=False).datetime.timestamp() * 1000)
    except Exception:
        pass
    return dt

def get_tz_by_market(market: Market):
    if Market.HK == market:
        return hongkong
    elif Market.CN == market:
        return china
    return eastern