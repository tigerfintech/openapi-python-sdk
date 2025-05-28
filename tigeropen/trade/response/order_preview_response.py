from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline_obj


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
            self.preview_order = camel_to_underline_obj(self.data)
