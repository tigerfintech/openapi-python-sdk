# -*- coding: utf-8 -*-


class FinancialDailyParams(object):
    def __init__(self):
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
        params = dict()

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


class FinancialReportParams(object):
    def __init__(self):
        self._symbols = None
        self._market = None
        self._fields = None
        self._period_type = None

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

    def to_openapi_dict(self):
        params = dict()

        if self.symbols:
            params['symbols'] = self.symbols

        if self.market:
            params['market'] = self.market

        if self.fields:
            params['fields'] = self.fields

        if self.period_type:
            params['period_type'] = self.period_type

        return params


class CorporateActionParams(object):
    def __init__(self):
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
        params = dict()

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

