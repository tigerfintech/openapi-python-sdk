# -*- coding: utf-8 -*-
"""
Created on 2024

@author: tigeropen
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.quote.domain.option_analysis import OptionAnalysis, IVMetric, VolatilityListItem


class OptionAnalysisResponse(TigerResponse):
    """Response parser for option analysis API."""
    
    # Field mappings for special cases where camel_to_underline doesn't produce the desired result
    FIELD_MAPPINGS = {
        'impliedVol30Days': 'implied_vol_30_days',
        'ivHisVRatio': 'iv_his_v_ratio',
    }
    
    def __init__(self):
        super(OptionAnalysisResponse, self).__init__()
        self.analysis_list = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionAnalysisResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if not self.data or not isinstance(self.data, list):
            self.analysis_list = []
            return

        analysis_list = []
        for item in self.data:
            analysis = OptionAnalysis()
            
            for key, value in item.items():
                if key == 'impliedVolMetric' and isinstance(value, dict):
                    # Create nested IVMetric object
                    metric = IVMetric()
                    metric.period = value.get('period')
                    metric.percentile = value.get('percentile')
                    metric.rank = value.get('rank')
                    analysis.iv_metric = metric
                elif key == 'volatilityList' and isinstance(value, list):
                    # Parse volatility list
                    vol_list = []
                    for vol_item in value:
                        vi = VolatilityListItem()
                        for vk, vv in vol_item.items():
                            snake_vk = self.FIELD_MAPPINGS.get(vk, string_utils.camel_to_underline(vk))
                            setattr(vi, snake_vk, vv)
                        vol_list.append(vi)
                    analysis.volatility_list = vol_list
                else:
                    # Convert camelCase to snake_case, using field mappings for special cases
                    snake_key = self.FIELD_MAPPINGS.get(key, string_utils.camel_to_underline(key))
                    setattr(analysis, snake_key, value)
            
            analysis_list.append(analysis)
        
        self.analysis_list = analysis_list
