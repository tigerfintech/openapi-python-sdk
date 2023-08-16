# -*- coding: utf-8 -*-
from tigeropen.common.model import BaseParams


class FinancialDailyParams(BaseParams):
    def __init__(self):
        super(FinancialDailyParams, self).__init__()
        self._symbols = None
        self._market = None
        self._period_type = None
        self._fields = None
        self._begin_date = None
        self._end_date = None

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def period_type(self):
        return self._period_type

    @period_type.setter
    def period_type(self, value):
        self._period_type = value

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value

    @property
    def begin_date(self):
        return self._begin_date

    @begin_date.setter
    def begin_date(self, value):
        self._begin_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()

        if self.symbols:
            params['symbols'] = self.symbols

        if self.market:
            params['market'] = self.market

        if self.period_type:
            params['period_type'] = self.period_type

        if self.fields:
            params['fields'] = self.fields

        if self.begin_date:
            params['begin_date'] = self.begin_date

        if self.end_date:
            params['end_date'] = self.end_date

        return params


class FinancialReportParams(BaseParams):
    def __init__(self):
        super(FinancialReportParams, self).__init__()
        self._symbols = None
        self._market = None
        self._fields = None
        self._period_type = None
        self._begin_date = None
        self._end_date = None

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value

    @property
    def period_type(self):
        return self._period_type

    @period_type.setter
    def period_type(self, value):
        self._period_type = value

    @property
    def begin_date(self):
        return self._begin_date

    @begin_date.setter
    def begin_date(self, value):
        self._begin_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()

        if self.symbols:
            params['symbols'] = self.symbols

        if self.market:
            params['market'] = self.market

        if self.fields:
            params['fields'] = self.fields

        if self.period_type:
            params['period_type'] = self.period_type

        if self.begin_date:
            params['begin_date'] = self.begin_date

        if self.end_date:
            params['end_date'] = self.end_date

        return params


class FinancialExchangeRateParams(BaseParams):
    def __init__(self):
        super(FinancialExchangeRateParams, self).__init__()
        self._currency_list = None
        self._begin_date = None
        self._end_date = None
        self._timezone = None

    @property
    def currency_list(self):
        return self._currency_list

    @currency_list.setter
    def currency_list(self, value):
        self._currency_list = value

    @property
    def begin_date(self):
        return self._begin_date

    @begin_date.setter
    def begin_date(self, value):
        self._begin_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        self._timezone = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()

        if self.currency_list:
            params['currency_list'] = self.currency_list

        if self.begin_date:
            params['begin_date'] = self.begin_date

        if self.end_date:
            params['end_date'] = self.end_date

        if self.timezone:
            params['timezone'] = self.timezone

        return params

class CorporateActionParams(BaseParams):
    def __init__(self):
        super(CorporateActionParams, self).__init__()
        self._symbols = None
        self._market = None
        self._action_type = None
        self._begin_date = None
        self._end_date = None

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def action_type(self):
        return self._action_type

    @action_type.setter
    def action_type(self, value):
        self._action_type = value

    @property
    def begin_date(self):
        return self._begin_date

    @begin_date.setter
    def begin_date(self, value):
        self._begin_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()

        if self.symbols:
            params['symbols'] = self.symbols

        if self.market:
            params['market'] = self.market

        if self.action_type:
            params['action_type'] = self.action_type

        if self.begin_date:
            params['begin_date'] = self.begin_date

        if self.end_date:
            params['end_date'] = self.end_date

        return params


class IndustryParams(BaseParams):
    def __init__(self):
        super(IndustryParams, self).__init__()
        self._industry_level = None
        self._industry_id = None
        self._market = None
        self._symbol = None

    @property
    def industry_level(self):
        return self._industry_level

    @industry_level.setter
    def industry_level(self, value):
        self._industry_level = value

    @property
    def industry_id(self):
        return self._industry_id

    @industry_id.setter
    def industry_id(self, value):
        self._industry_id = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()

        if self.industry_level:
            params['industry_level'] = self.industry_level

        if self.industry_id:
            params['industry_id'] = self.industry_id

        if self.market:
            params['market'] = self.market

        if self.symbol:
            params['symbol'] = self.symbol

        return params
