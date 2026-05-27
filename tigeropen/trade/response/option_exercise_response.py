# -*- coding: utf-8 -*-
"""
Response parsers for option exercise (行权/作废) interfaces.
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.trade.domain.option_exercise import (
    OptionExerciseRecord,
    OptionExercisePageResult,
    OptionExerciseCheckResult,
    OptionExercisePosition,
    OptionExercisePositionPageResult,
)


class OptionExerciseSubmitResponse(TigerResponse):
    """提交行权/作废申请 响应 — 服务端无业务 data，仅靠 is_success() 判断结果"""

    def parse_response_content(self, response_content):
        super().parse_response_content(response_content)


class OptionExerciseCancelResponse(TigerResponse):
    """撤销行权申请 响应 — 服务端无业务 data，仅靠 is_success() 判断结果"""

    def parse_response_content(self, response_content):
        super().parse_response_content(response_content)


class OptionExerciseCheckResponse(TigerResponse):
    """行权检验响应"""

    def __init__(self):
        super().__init__()
        self.result = None

    def parse_response_content(self, response_content):
        super().parse_response_content(response_content)

        if self.data and isinstance(self.data, dict):
            obj = OptionExerciseCheckResult()
            for key, value in self.data.items():
                attr = string_utils.camel_to_underline(key)
                if hasattr(obj, attr):
                    setattr(obj, attr, value)
            self.result = obj


class OptionExercisePageResponse(TigerResponse):
    """分页查询行权记录响应"""

    def __init__(self):
        super().__init__()
        self.result = None

    def parse_response_content(self, response_content):
        super().parse_response_content(response_content)

        if self.data and isinstance(self.data, dict):
            page_result = OptionExercisePageResult()
            page_result.page_num = self.data.get('pageNum')
            page_result.page_size = self.data.get('pageSize')
            page_result.item_count = self.data.get('itemCount')
            page_result.page_count = self.data.get('pageCount')
            for item in self.data.get('items') or []:
                record = OptionExerciseRecord()
                for key, value in item.items():
                    attr = string_utils.camel_to_underline(key)
                    if hasattr(record, attr):
                        setattr(record, attr, value)
                page_result.items.append(record)
            self.result = page_result


class OptionExercisePositionResponse(TigerResponse):
    """查询可行权持仓响应"""

    def __init__(self):
        super().__init__()
        self.result = None

    def parse_response_content(self, response_content):
        super().parse_response_content(response_content)

        if self.data and isinstance(self.data, dict):
            page_result = OptionExercisePositionPageResult()
            page_result.page_num = self.data.get('pageNum')
            page_result.page_size = self.data.get('pageSize')
            page_result.item_count = self.data.get('itemCount')
            page_result.page_count = self.data.get('pageCount')
            for item in self.data.get('items') or []:
                pos = OptionExercisePosition()
                for key, value in item.items():
                    attr = string_utils.camel_to_underline(key)
                    if hasattr(pos, attr):
                        setattr(pos, attr, value)
                page_result.items.append(pos)
            self.result = page_result
