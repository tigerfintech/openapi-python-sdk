from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline_obj
from tigeropen.trade.domain.prime_account import AggregateAsset


class AggregateAssetsResponse(TigerResponse):
    def __init__(self):
        super().__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.result = AggregateAsset.from_dict(camel_to_underline_obj(self.data))