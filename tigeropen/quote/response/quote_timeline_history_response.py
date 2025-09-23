
import pandas as pd

from tigeropen.common.consts import TradingSession
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline_obj, camel_to_underline

FIELD_PREMARKET = 'preMarket'
FIELD_ITEMS = 'items'
FIELD_AFTERHOURS = 'afterHours'
FIELD_OVERNIGHT = 'overnight'
COLUMN_TRADE_SESSION = 'trade_session'

class QuoteTimelineHistoryResponse(TigerResponse):
    def __init__(self):
        super(QuoteTimelineHistoryResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteTimelineHistoryResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            timeline_items = []
            for symbol_item in self.data:
                symbol = symbol_item.get('symbol')
                if FIELD_PREMARKET in symbol_item:  # 盘前
                    pre_markets = symbol_item[FIELD_PREMARKET]
                    if pre_markets:
                        for item in pre_markets:
                            item_values = self.parse_timeline(item, symbol, TradingSession.PreMarket.value)
                            timeline_items.append(camel_to_underline_obj(item_values))
                if FIELD_ITEMS in symbol_item:
                    regulars = symbol_item[FIELD_ITEMS]
                    if regulars:
                        for item in regulars:
                            item_values = self.parse_timeline(item, symbol,  TradingSession.Regular.value)
                            timeline_items.append(camel_to_underline_obj(item_values))
                if FIELD_AFTERHOURS in symbol_item:  # 盘后
                    after_hours = symbol_item[FIELD_AFTERHOURS]
                    if after_hours:
                        for item in after_hours:
                            item_values = self.parse_timeline(item, symbol, TradingSession.AfterHours.value)
                            timeline_items.append(camel_to_underline_obj(item_values))
                if FIELD_OVERNIGHT in symbol_item:  # 夜盘
                    overnights = symbol_item[FIELD_OVERNIGHT]
                    if overnights:
                        for item in overnights:
                            item_values = self.parse_timeline(item, symbol, TradingSession.OverNight.value)
                            timeline_items.append(camel_to_underline_obj(item_values))

            self.result = pd.DataFrame(timeline_items)

    @staticmethod
    def parse_timeline(item, symbol, trading_session):
        item_values = {'symbol': symbol, COLUMN_TRADE_SESSION: trading_session}
        for key, value in item.items():
            if value is None:
                continue
            tag = camel_to_underline(key)
            item_values[tag] = value

        return item_values
