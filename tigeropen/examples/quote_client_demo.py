# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import logging

from tigeropen.common.consts import Market, QuoteRight, TimelinePeriod
from tigeropen.quote.quote_client import QuoteClient

from tigeropen.examples.client_config import get_client_config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a', )
logger = logging.getLogger('TigerOpenApi')

client_config = get_client_config()
openapi_client = QuoteClient(client_config, logger=logger)


def get_quote():
    openapi_client.get_market_status(Market.US)
    openapi_client.get_briefs(symbols=['AAPL', '00700', '600519'], include_ask_bid=True, right=QuoteRight.BR)
    openapi_client.get_timeline('AAPL', period=TimelinePeriod.DAY, include_hour_trading=True)
    openapi_client.get_bars('AAPL')
    openapi_client.get_hour_trading_timeline('AAPL')


if __name__ == '__main__':
    get_quote()
