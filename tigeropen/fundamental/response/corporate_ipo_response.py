# -*- coding: utf-8 -*-

import pandas as pd
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'action_type', 'ipo_name', 'listing_date', 'listing_price', 'shares_outstanding',
           'shares_float', 'offer_amount', 'price_range', 'currency', 'min_purchase_quantity',
           'leverage_ratio', 'execute_date', 'market', 'exchange']
FIELD_MAPPINGS = {'actionType': 'action_type', 'ipoName': 'ipo_name', 'listingDate': 'listing_date',
                  'listingPrice': 'listing_price', 'sharesOutstanding': 'shares_outstanding',
                  'sharesFloat': 'shares_float', 'offerAmount': 'offer_amount', 'priceRange': 'price_range',
                  'minPurchaseQuantity': 'min_purchase_quantity', 'leverageRatio': 'leverage_ratio',
                  'executeDate': 'execute_date'}


class CorporateIpoResponse(TigerResponse):
    def __init__(self):
        super(CorporateIpoResponse, self).__init__()
        self.corporate_ipo = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(CorporateIpoResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            items = []
            for symbol, ipo_items in self.data.items():
                for item in ipo_items:
                    item['symbol'] = symbol
                    items.append(item)
            df = pd.DataFrame(items).rename(columns=FIELD_MAPPINGS)
            self.corporate_ipo = df[[c for c in COLUMNS if c in df.columns]]
