# -*- coding: utf-8 -*-
"""
Created on 2026/06/08

@author: tigeropen
"""


class ActivePlan:
    """当前生效套餐 / Active subscription plan"""

    def __init__(self):
        self.plan_type = None  # 套餐类型 / Plan type
        self.expire_time = None  # 过期时间(毫秒) / Expire time in milliseconds

    def __repr__(self):
        """String representation for this object."""
        return "ActivePlan(%s)" % self.__dict__


class AddonInfo:
    """附加套餐信息 / Add-on package info"""

    def __init__(self):
        self.plan_type = None  # 套餐类型 / Plan type
        self.active = None  # 是否生效 / Whether it is active
        self.start_time = None  # 生效时间(毫秒) / Start time in milliseconds
        self.expire_time = None  # 过期时间(毫秒) / Expire time in milliseconds

    def __repr__(self):
        """String representation for this object."""
        return "AddonInfo(%s)" % self.__dict__


class Entitlement:
    """权益额度 / Effective entitlement quota"""

    def __init__(self):
        self.history_stock_limit = None  # 历史股票行情额度 / History stock quote limit
        self.history_stock_remaining = None  # 历史股票行情剩余额度 / History stock quote remaining
        self.history_future_limit = None  # 历史期货行情额度 / History future quote limit
        self.history_future_remaining = None  # 历史期货行情剩余额度 / History future quote remaining
        self.history_option_limit = None  # 历史期权行情额度 / History option quote limit
        self.history_option_remaining = None  # 历史期权行情剩余额度 / History option quote remaining
        self.subscribe_limit = None  # 订阅额度 / Subscribe limit
        self.subscribe_remaining = None  # 订阅剩余额度 / Subscribe remaining
        self.subscribe_depth_limit = None  # 深度行情订阅额度 / Subscribe depth limit
        self.subscribe_depth_remaining = None  # 深度行情订阅剩余额度 / Subscribe depth remaining
        self.high_freq_limit = None  # 高频请求额度 / High frequency request limit
        self.mid_freq_limit = None  # 中频请求额度 / Mid frequency request limit
        self.low_freq_limit = None  # 低频请求额度 / Low frequency request limit
        self.rate_multiple = None  # 频率倍数 / Rate multiple

    def __repr__(self):
        """String representation for this object."""
        return "Entitlement(%s)" % self.__dict__


class AddonEntitlement:
    """附加套餐权益 / Add-on entitlement data object"""

    def __init__(self):
        self.user_level = None  # 用户等级 / User level
        self.active_plan = None  # 当前生效套餐 / ActivePlan object
        self.addons = None  # 附加套餐列表 / List of AddonInfo
        self.effective_entitlement = None  # 生效权益额度 / Entitlement object

    def __repr__(self):
        """String representation for this object."""
        return "AddonEntitlement(%s)" % self.__dict__
