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
            page = self.data.get('page')
            total_page = self.data.get('totalPage')
            total_count = self.data.get('totalCount')
            items = self.data.get('items', [])
            if items:
                df_data = []
                for item in items:
                    formated_item = camel_to_underline_obj(item)
                    # 处理盘前盘后数据
                    hour_trading = formated_item.pop('hour_trading', None)
                    if hour_trading:
                        formated_item['hour_trading_tag'] = hour_trading.get('tag')
                        formated_item['hour_trading_change_rate'] = hour_trading.get('change_rate')
                    df_data.append(formated_item)
                
                self.result = pd.DataFrame(df_data)
                self.result['page'] = page
                self.result['total_page'] = total_page
                self.result['total_count'] = total_count
            