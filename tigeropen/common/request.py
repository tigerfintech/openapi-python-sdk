# -*- coding: utf-8 -*-
# 
# @Date    : 2022/1/20
# @Author  : sukai
import json

from tigeropen.common.consts.params import P_METHOD, P_VERSION, P_BIZ_CONTENT


class OpenApiRequest:
    def __init__(self, method, biz_model=None):
        self._method = method
        self._biz_model = biz_model

    @property
    def biz_model(self):
        return self._biz_model

    @biz_model.setter
    def biz_model(self, value):
        self._biz_model = value

    def get_params(self):
        params = dict()
        params[P_METHOD] = self._method
        params[P_VERSION] = getattr(self.biz_model, P_VERSION, None)

        if self.biz_model:
            params[P_BIZ_CONTENT] = json.dumps(obj=self.biz_model.to_openapi_dict(), ensure_ascii=False, sort_keys=True,
                                               separators=(',', ':'))

        return params