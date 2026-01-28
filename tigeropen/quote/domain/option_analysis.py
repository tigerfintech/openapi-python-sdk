# -*- coding: utf-8 -*-
"""
Created on 2025/01/31

@author: tigeropen
"""


class IVMetric:
    """隐含波动率指标 / Implied volatility metric"""
    
    def __init__(self):
        self.period = None  # 分析周期 / Analysis period (e.g., "52week")
        self.percentile = None  # IV百分位 / IV percentile (0-1)
        self.rank = None  # IV排名 / IV rank (0-1)

    def __repr__(self):
        """String representation for this object."""
        return "IVMetric(%s)" % self.__dict__


class OptionAnalysis:
    """期权分析数据对象 / Option analysis data object"""
    
    def __init__(self):
        self.symbol = None  # 股票代号 / Stock symbol
        self.implied_vol_30_days = None  # 30天隐含波动率 / 30-day implied volatility
        self.his_volatility = None  # 历史波动率 / Historical volatility
        self.iv_his_v_ratio = None  # IV/HV比率 / IV to HV ratio
        self.call_put_ratio = None  # 看涨看跌比率 / Call/Put ratio
        self.iv_metric = None  # 隐含波动率指标对象 / IVMetric object

    def __repr__(self):
        """String representation for this object."""
        return "OptionAnalysis(%s)" % self.__dict__
