# -*- coding: utf-8 -*-
import json

from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Transaction
from tigeropen.trade.response import CONTRACT_FIELDS

FIELD_MAPPINGS = {'account_id': 'account', 'right': 'put_call'}


class TransactionsResponse(TigerResponse):
    def __init__(self):
        super(TransactionsResponse, self).__init__()
        self.transactions = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(TransactionsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            for item in data_json.get('items', list()):
                trans = self._parse_transactions(string_utils.camel_to_underline_obj(item))
                if trans:
                    self.transactions.append(trans)

    def _parse_transactions(self, item_dict):
        trans = Transaction()
        contract = Contract()
        for k, v in item_dict.items():
            map_k = FIELD_MAPPINGS.get(k, k)
            if map_k in CONTRACT_FIELDS:
                setattr(contract, map_k, v)
            else:
                setattr(trans, map_k, v)
        trans.contract = contract
        return trans
