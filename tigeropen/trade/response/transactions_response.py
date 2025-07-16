# -*- coding: utf-8 -*-
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Transaction
from tigeropen.trade.response import CONTRACT_FIELDS

FIELD_MAPPINGS = {'account_id': 'account', 'right': 'put_call'}


class TransactionsResponse(TigerResponse):
    def __init__(self, page_token=None):
        super(TransactionsResponse, self).__init__()
        self.result = []
        self.next_page_token = None
        self._page_token = page_token
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(TransactionsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            for item in self.data.get('items', list()):
                trans = self._parse_transactions(string_utils.camel_to_underline_obj(item))
                if trans:
                    self.result.append(trans)
            self.next_page_token = self.data.get('nextPageToken')

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

    def __str__(self):
        return f'<{self.__class__.__name__}: result: {self.result}, next_page_token: {self.next_page_token}>'