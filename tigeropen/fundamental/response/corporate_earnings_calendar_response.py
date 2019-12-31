# -*- coding: utf-8 -*-
from itertools import chain

import pandas as pd
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'reportDate', 'reportTime', 'executeDate', 'expectedEps', 'actualEps',
           'fiscalQuarterEnding', 'market', 'exchange', 'actionType']
EARNINGS_CALENDAR_FIELD_MAPPINGS = {'actionType': 'action_type', 'actualEps': 'actual_eps',
                                    'expectedEps': 'expected_eps', 'executeDate': 'execute_date',
                                    'fiscalQuarterEnding': 'fiscal_quarter_ending', 'reportDate': 'report_date',
                                    'reportTime': 'report_time',
                                    }


class EarningsCalendarResponse(TigerResponse):
    def __init__(self):
        super(EarningsCalendarResponse, self).__init__()
        self.earnings_calendar = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(EarningsCalendarResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.earnings_calendar = pd.DataFrame(chain.from_iterable(self.data.values()), columns=COLUMNS).rename(
                columns=EARNINGS_CALENDAR_FIELD_MAPPINGS).sort_values(by=['report_date']).reset_index(drop=True)
