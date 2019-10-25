import json
from tigeropen.common.response import TigerResponse

PREVIEW_ORDER_FIELD_MAPPING = {"initMarginBefore": "init_margin_before", "commissionCurrency": "commission_currency",
                               "maintMargin": "maint_margin", "equityWithLoan": "equity_with_loan",
                               "minCommission": "min_commission", "maintMarginBefore": "maint_margin_before",
                               "initMargin": "init_margin", "equityWithLoanBefore": "equity_with_loan_before",
                               "marginCurrency": "margin_currency", "maxCommission": "max_commission",
                               "warningText": "warning_text"}


class PreviewOrderResponse(TigerResponse):
    def __init__(self):
        super(PreviewOrderResponse, self).__init__()
        self.preview_order = dict()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(PreviewOrderResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            for key, value in data_json.items():
                field = PREVIEW_ORDER_FIELD_MAPPING.get(key, key)
                self.preview_order[field] = value

