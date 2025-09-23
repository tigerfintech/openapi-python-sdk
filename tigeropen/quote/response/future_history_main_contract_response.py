
import pandas as pd

from tigeropen.common.response import TigerResponse



class FutureHistoryMainContractResponse(TigerResponse):
    def __init__(self):
        super(FutureHistoryMainContractResponse, self).__init__()
        self.result = pd.DataFrame()
        self._is_success = None

    def parse_response_content(self, response_content, skip_main=True):
        response = super(FutureHistoryMainContractResponse, self).parse_response_content(response_content)

        if self.data:
            records = []
            for item in self.data:
                contract_code = item.get('contractCode')
                for refer in item.get('mainReferItems', []):
                    records.append({
                        'contract_code': contract_code,
                        'time': refer.get('time'),
                        'refer_contract_code': refer.get('referContractCode')
                    })
            if records:
                self.result = pd.DataFrame(records)