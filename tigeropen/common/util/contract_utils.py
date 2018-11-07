# -*- coding: utf-8 -*-
"""
Created on 2018/11/1

@author: gaoan
"""
from tigeropen.trade.domain.contract import Contract


def stock_contract(symbol, currency, local_symbol=None, exchange=None, contract_id=None):
    return Contract(symbol, currency, sec_type='STK', local_symbol=local_symbol, exchange=exchange,
                    contract_id=contract_id)


def option_contract(symbol, currency, expiry, strike, right, multiplier=100, local_symbol=None, contract_id=None):
    return Contract(symbol, currency, sec_type='OPT', expiry=expiry, strike=strike, right=right,
                    multiplier=multiplier, local_symbol=local_symbol, contract_id=contract_id)


def future_contract(symbol, currency, expiry, multiplier=None, local_symbol=None):
    return Contract(symbol, currency, sec_type='FUT', expiry=expiry, multiplier=multiplier, local_symbol=local_symbol)


def future_option_contract(symbol, currency, expiry, strike, right, multiplier=None, local_symbol=None,
                           contract_id=None):
    return Contract(symbol, currency, sec_type='FOP', expiry=expiry, strike=strike, right=right,
                    multiplier=multiplier, local_symbol=local_symbol, contract_id=contract_id)


def cash_contract(symbol, currency, local_symbol=None):
    return Contract(symbol, currency, sec_type='CASH', local_symbol=local_symbol)
