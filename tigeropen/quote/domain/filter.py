# -*- coding: utf-8 -*-
# 
# @Date    : 2021/11/15
# @Author  : sukai
from tigeropen.common.consts.filter_fields import FilterField, FieldBelongType

GREEKS = ['delta', 'gamma', 'theta', 'vega', 'rho']


class OptionFilter:
    def __init__(self, implied_volatility_min=None, implied_volatility_max=None, open_interest_min=None,
                 open_interest_max=None, delta_min=None, delta_max=None, gamma_min=None, gamma_max=None,
                 theta_min=None, theta_max=None, vega_min=None, vega_max=None, rho_min=None, rho_max=None,
                 in_the_money=None):
        """
        option filter
        :param implied_volatility_min:
        :param implied_volatility_max:
        :param open_interest_min:
        :param open_interest_max:
        :param delta_min:
        :param delta_max:
        :param gamma_min:
        :param gamma_max:
        :param theta_min:
        :param theta_max:
        :param vega_min:
        :param vega_max:
        :param rho_min:
        :param rho_max:
        :param in_the_money:
        """
        self.implied_volatility_min = implied_volatility_min
        self.implied_volatility_max = implied_volatility_max
        self.open_interest_min = open_interest_min
        self.open_interest_max = open_interest_max
        self.delta_min = delta_min
        self.delta_max = delta_max
        self.gamma_min = gamma_min
        self.gamma_max = gamma_max
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.vega_min = vega_min
        self.vega_max = vega_max
        self.rho_min = rho_min
        self.rho_max = rho_max
        self.in_the_money = in_the_money

    def to_dict(self):
        return {'greeks': self._get_greeks(),
                'implied_volatility': self._min_max('implied_volatility'),
                'open_interest': self._min_max('open_interest'),
                'in_the_money': self.in_the_money}

    def _get_greeks(self):
        return {greek: self._min_max(greek) for greek in GREEKS}

    def _min_max(self, k):
        return {'min': getattr(self, k + '_min'), 'max': getattr(self, k + '_max')}


class SortFilterData:
    def __init__(self, field, sort_dir, period=None):
        """

        :param field: filter field, subclass of tigeropen.common.consts.filter_fields.FilterField
        :param sort_dir: tigeropen.common.consts.SortDirection
        :param period: tigeropen.common.consts.filter_fields.AccumulateField
        """
        # 排序属性
        self.field = field
        # SortDir 排序方向，默认不排序
        self.sort_dir = sort_dir
        # 时间周期 AccumulatePeriod非必传项-只有排序为ACC相关字段,需要此字段
        self.period = period

    def to_dict(self):
        return {
            'field_name': self.field.index,
            'field_type': self.field.field_type_request_name,
            'sort_dir': self.sort_dir.value,
            'period': self.period.value
        }


class StockFilter:
    def __init__(self, field, filter_min=None, filter_max=None, is_no_filter=False, accumulate_period=None,
                 financial_period=None, tag_list=None):
        """
        stock filter
        :param field: filter field, subclass of tigeropen.common.consts.filter_fields.FilterField
        :param filter_min: Lower limit of the interval (closed interval), if not pass, means negative infinity
        :param filter_max: Upper limit of the interval (closed interval), if not pass, means positive infinity
        :param is_no_filter: is enable filter for this field
        :param accumulate_period: tigeropen.common.consts.filter_fields.AccumulateField
        :param financial_period: tigeropen.common.consts.filter_fields.FinancialPeriod
        :param tag_list:
        """
        self.field = field
        self.min_value = filter_min
        self.max_value = filter_max
        self.is_no_filter = is_no_filter
        self.accumulate_period = accumulate_period
        self.financial_period = financial_period
        self.tag_list = tag_list

    @property
    def field_belong_type(self):
        return FieldBelongType(self.field.field_type)

    def to_dict(self):
        param = {'field_name': self.field.field_type + '_' + self.field.name,
                 'is_no_filter': self.is_no_filter
                 }
        if self.field_belong_type != FieldBelongType.MULTI_TAG:
            param.update({'filter_min': self.min_value,
                          'filter_max': self.max_value})
        if self.field_belong_type == FieldBelongType.ACCUMULATE and self.accumulate_period:
            param['period'] = self.accumulate_period.name
        if self.field_belong_type == FieldBelongType.FINANCIAL and self.financial_period:
            param['financial_period'] = self.financial_period.name
        if self.field_belong_type == FieldBelongType.MULTI_TAG and self.tag_list:
            param['tag_list'] = self.tag_list
        return param


class ScannerResultItem:
    def __init__(self, symbol, market, base_data_list=None, accumulate_data_list=None, financial_data_list=None,
                 multi_tag_data_list=None):
        self.symbol = symbol
        self.market = market
        self.field_data = dict()
        self.field_data.update(self._build_data_map(base_data_list, FieldBelongType.BASE))
        self.field_data.update(self._build_data_map(accumulate_data_list, FieldBelongType.ACCUMULATE))
        self.field_data.update(self._build_data_map(financial_data_list, FieldBelongType.FINANCIAL))
        self.field_data.update(self._build_data_map(multi_tag_data_list, FieldBelongType.MULTI_TAG))

    def _build_data_map(self, data_list, field_belong_type):
        data_map = dict()
        if data_list:
            for item in data_list:
                field = field_belong_type.field_class(item.get('index'))
                data_map[field] = item.get('value')
        return data_map

    def __getitem__(self, key):
        if isinstance(key, StockFilter):
            return self.field_data.get(key.field)
        elif isinstance(key, FilterField):
            return self.field_data.get(key)

    def __repr__(self):
        return "ScannerResultItem(%s)" % self.__dict__


class ScannerResult:
    def __init__(self, page, page_size, total_page, total_count, items):
        """
        {'page': 0, 'total_page': 668, 'total_count': 6678, 'page_size': 10,
        'items': [
            {'symbol': 'MMIT', 'market': 'US',
                'base_data_list': [{'index': 13, 'name': 'floatShares', 'value': 10000000.0}],
                'accumulate_data_list': [],
                'financial_data_list': [],
                'multi_tag_data_list': []},
            {'symbol': 'DPM', 'market': 'US',
                'base_data_list': [{'index': 13, 'name': 'floatShares', 'value': 10000000.0}],
                 'accumulate_data_list': [],
                 'financial_data_list': [],
                 'multi_tag_data_list': []},
                ]
        }
        """
        self.page = page
        self.total_page = total_page
        self.total_count = total_count
        self.page_size = page_size
        self.items = list()
        self.symbols = list()
        self._build_items(items)

    def _build_items(self, items):
        result_items = list()
        symbols = set()
        if items:
            for item in items:
                result_item = ScannerResultItem(symbol=item.get('symbol'),
                                         market=item.get('market'),
                                         base_data_list=item.get('base_data_list'),
                                         accumulate_data_list=item.get('accumulate_data_list'),
                                         financial_data_list=item.get('financial_data_list'),
                                         multi_tag_data_list=item.get('multi_tag_data_list'))
                result_items.append(result_item)
                symbols.add(item.get('symbol'))
        self.items = result_items
        self.symbols = list(symbols)

    def __repr__(self):
        return "ScannerResult(%s)" % self.__dict__
