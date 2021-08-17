# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['contract_code', 'symbol', 'type', 'name', 'contract_month', 'multiplier', 'exchange', 'currency',
           'first_notice_date', 'last_bidding_close_time', 'last_trading_date', 'trade', 'continuous', 'min_tick']
CONTRACT_FIELD_MAPPINGS = {'contractCode': 'contract_code', 'exchangeCode': 'exchange', 'ibCode': 'symbol',
                           'contractMonth': 'contract_month', 'firstNoticeDate': 'first_notice_date',
                           'lastBiddingCloseTime': 'last_bidding_close_time', 'lastTradingDate': 'last_trading_date',
                           'minTick': 'min_tick'}


class FutureContractResponse(TigerResponse):
    def __init__(self):
        super(FutureContractResponse, self).__init__()
        self.contracts = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureContractResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            contract_items = []
            if isinstance(self.data, list):
                for item in self.data:
                    item_values = self.parse_contract(item)
                    contract_code = item_values.get('contract_code')
                    if contract_code is None or contract_code.endswith('main'):
                        continue
                    contract_items.append([item_values.get(tag) for tag in COLUMNS])
            elif isinstance(self.data, dict):
                item_values = self.parse_contract(self.data)
                contract_code = item_values.get('contract_code')
                if contract_code and not contract_code.endswith('main'):
                    contract_items.append([item_values.get(tag) for tag in COLUMNS])

            self.contracts = pd.DataFrame(contract_items, columns=COLUMNS)

    @staticmethod
    def parse_contract(item):
        item_values = dict()
        for key, value in item.items():
            if value is None:
                continue
            if key in ('lastBiddingCloseTime', 'firstNoticeDate') and (value == 0 or value == ''):
                continue
            tag = CONTRACT_FIELD_MAPPINGS[key] if key in CONTRACT_FIELD_MAPPINGS else key
            item_values[tag] = value
        return item_values
