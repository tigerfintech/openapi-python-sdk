# -*- coding: utf-8 -*-
"""
Response parsers for option exercise (行权/作废) interfaces.
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.trade.domain.option_exercise import (
    OptionExerciseRecord,
    OptionExerciseCheckResult,
    OptionExercisePosition,
    OptionExerciseActionResult,
)


def _extract_inner_data(outer_data):
    """Extract the actual payload from the inner response envelope {status, msg, data, ...}."""
    if not outer_data or not isinstance(outer_data, dict):
        return None
    return outer_data.get('data')


class OptionExerciseSubmitResponse(TigerResponse):
    """提交行权/作废申请 响应"""

    def __init__(self):
        super().__init__()
        self.result = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)

        inner = _extract_inner_data(self.data)
        if inner and isinstance(inner, dict):
            obj = OptionExerciseActionResult()
            for key, value in inner.items():
                attr = string_utils.camel_to_underline(key)
                if hasattr(obj, attr):
                    setattr(obj, attr, value)
            self.result = obj


class OptionExerciseCheckResponse(TigerResponse):
    """行权检验响应"""

    def __init__(self):
        super().__init__()
        self.result = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)

        inner = _extract_inner_data(self.data)
        if inner and isinstance(inner, dict):
            obj = OptionExerciseCheckResult()
            for key, value in inner.items():
                attr = string_utils.camel_to_underline(key)
                if hasattr(obj, attr):
                    setattr(obj, attr, value)
            self.result = obj


class OptionExercisePageResponse(TigerResponse):
    """分页查询行权记录响应"""

    def __init__(self):
        super().__init__()
        self.result = []
        self.total = None
        self.page = None
        self.size = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)

        inner = _extract_inner_data(self.data)
        if inner and isinstance(inner, dict):
            self.total = inner.get('itemCount')
            self.page = inner.get('pageNum')
            self.size = inner.get('pageSize')
            items = inner.get('items') or []
            for item in items:
                record = OptionExerciseRecord()
                for key, value in item.items():
                    attr = string_utils.camel_to_underline(key)
                    if hasattr(record, attr):
                        setattr(record, attr, value)
                self.result.append(record)


class OptionExercisePositionResponse(TigerResponse):
    """查询可行权持仓响应"""

    def __init__(self):
        super().__init__()
        self.result = []

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)

        inner = _extract_inner_data(self.data)
        if inner:
            items = inner if isinstance(inner, list) else inner.get('items') or []
            for item in items:
                pos = OptionExercisePosition()
                for key, value in item.items():
                    attr = string_utils.camel_to_underline(key)
                    if hasattr(pos, attr):
                        setattr(pos, attr, value)
                self.result.append(pos)


class OptionExerciseCancelResponse(TigerResponse):
    """撤销行权申请响应"""

    def __init__(self):
        super().__init__()
        self.result = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)

        inner = _extract_inner_data(self.data)
        if inner and isinstance(inner, dict):
            obj = OptionExerciseActionResult()
            for key, value in inner.items():
                attr = string_utils.camel_to_underline(key)
                if hasattr(obj, attr):
                    setattr(obj, attr, value)
            self.result = obj
