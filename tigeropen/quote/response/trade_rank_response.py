from tigeropen.common.response import TigerResponse
import pandas as pd
from tigeropen.common.util.string_utils import camel_to_underline_obj

class TradeRankResponse(TigerResponse):
    def __init__(self):
        super(TradeRankResponse, self).__init__()
        self.result = pd.DataFrame()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(TradeRankResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            df_data = []
            for item in self.data:
                formated_item = camel_to_underline_obj(item)
                hour_trading = formated_item.pop('hour_trading', None)
                if hour_trading:
                    for key, value in hour_trading.items():
                        formated_item['hour_trading_' + key] = value
                df_data.append(formated_item)

            self.result = pd.DataFrame(df_data)

            