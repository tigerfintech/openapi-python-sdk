# -*- coding: utf-8 -*-
"""
Domain models for option exercise (行权/作废) interfaces.
"""


class OptionExerciseRecord:
    """行权申请记录"""

    def __init__(self):
        self.id = None
        self.account_id = None
        self.contract_id = None
        self.symbol = None
        self.stk_symbol = None
        self.expire_date = None
        self.strike = None
        self.call_put = None
        self.type = None          # 'Exercise' | 'Expire'
        self.request_quantity = None
        self.quantity = None
        self.status = None
        self.executing_date = None
        self.itm_rate = None
        self.is_force = None
        self.reason = None

    def __repr__(self):
        return 'OptionExerciseRecord(%s)' % self.__dict__


class OptionExercisePageResult:
    """行权记录分页查询结果"""

    def __init__(self):
        self.items = []
        self.page_num = None
        self.page_size = None
        self.item_count = None
        self.page_count = None

    def __repr__(self):
        return 'OptionExercisePageResult(%s)' % self.__dict__


class OptionExerciseCheckResult:
    """行权预估检验结果"""

    def __init__(self):
        self.available_quantity = None
        self.position = None
        self.stk_position = None
        self.stk_position_change = None
        self.stk_position_before = None
        self.stk_position_after = None
        self.symbol = None

    def __repr__(self):
        return 'OptionExerciseCheckResult(%s)' % self.__dict__


class OptionExercisePosition:
    """可行权持仓信息"""

    def __init__(self):
        self.market = None
        self.contract_id = None
        self.stk_symbol = None
        self.symbol = None
        self.expire_date = None
        self.strike = None
        self.call_put = None
        self.account_id = None
        self.position = None
        self.available_quantity = None

    def __repr__(self):
        return 'OptionExercisePosition(%s)' % self.__dict__


class OptionExercisePositionPageResult:
    """可行权持仓分页查询结果"""

    def __init__(self):
        self.items = []
        self.page_num = None
        self.page_size = None
        self.item_count = None
        self.page_count = None

    def __repr__(self):
        return 'OptionExercisePositionPageResult(%s)' % self.__dict__


