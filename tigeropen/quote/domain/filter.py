# -*- coding: utf-8 -*-
# 
# @Date    : 2021/11/15
# @Author  : sukai
from tigeropen.common.consts import SortDirection
from tigeropen.common.model import Field

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


class StockFilter:
    def __init__(self, field, min_value=None, max_value=None, sort=None, enable=True):
        """
        stock filter
        :param field: filter field. subclass of tigeropen.common.consts.Field, or field name string
        :param min_value:
        :param max_value:
        :param sort: tigeropen.common.consts.SortDirection. ASC or DESC
        :param enable:
        """
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
        self.sort = sort
        self.enable = enable

    def to_dict(self):
        return {'field': self.field.name if isinstance(self.field, Field) else self.field,
                'min_value': self.min_value,
                'max_value': self.max_value,
                'sort_direction': self.sort.value if isinstance(self.sort, SortDirection) else self.sort,
                }


