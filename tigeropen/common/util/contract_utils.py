# -*- coding: utf-8 -*-
"""
Created on 2018/11/1

@author: gaoan
"""
import re
from tigeropen.trade.domain.contract import Contract


def stock_contract(symbol, currency, local_symbol=None, exchange=None, contract_id=None):
    return Contract(symbol, currency, sec_type='STK', local_symbol=local_symbol, exchange=exchange,
                    contract_id=contract_id)


def option_contract(symbol, expiry, strike, put_call, currency, multiplier=100, local_symbol=None, contract_id=None):
    return Contract(symbol, currency, sec_type='OPT', expiry=expiry, strike=strike, put_call=put_call,
                    multiplier=multiplier, local_symbol=local_symbol, contract_id=contract_id)


def option_contract_full(identifier, multiplier=100, currency='USD'):
    symbol, expiry, put_call, strike = extract_option_info(identifier)
    if expiry and '-' in expiry:
        expiry = expiry.replace('-', '')
    return Contract(symbol, currency, sec_type='OPT', expiry=expiry, strike=strike, put_call=put_call,
                    multiplier=multiplier)


def future_contract(symbol, currency, expiry, exchange, multiplier=None, local_symbol=None):
    return Contract(symbol, currency, sec_type='FUT', expiry=expiry, exchange=exchange, multiplier=multiplier,
                    local_symbol=local_symbol)


def future_option_contract(symbol, currency, expiry, strike, put_call, multiplier=None, local_symbol=None,
                           contract_id=None):
    return Contract(symbol, currency, sec_type='FOP', expiry=expiry, strike=strike, put_call=put_call,
                    multiplier=multiplier, local_symbol=local_symbol, contract_id=contract_id)


def cash_contract(symbol, currency, local_symbol=None):
    return Contract(symbol, currency, sec_type='CASH', local_symbol=local_symbol)


def extract_option_info(identifier):
    """
    从期权中提取 symbol, expiry 等信息
    :param identifier:
    :return:
    """
    if identifier:
        tokens = re.findall(r'(\w+)\s*(\d{6})(C|P)(\d+)', identifier, re.M)
        if len(tokens) == 1:
            underlying_symbol, expiry, put_call, strike = tokens[0]
            expiry = '20' + expiry
            if len(expiry) == 8:
                expiry = expiry[:4] + '-' + expiry[4:6] + '-' + expiry[6:]
            strike = float(strike) / 1000
            put_call = 'CALL' if put_call == 'C' else 'PUT'
            return underlying_symbol, expiry, put_call, strike
        else:
            return None, None, None, None


def get_option_identifier(underlying_symbol, expiry, put_call, strike):
    """
    获取期权合约的唯一标识
    :param underlying_symbol: like AAPL
    :param expiry: like 20100101
    :param put_call: like C or CALL or P or PUT
    :param strike: like 5.0
    :return:
    """
    direction = 'C' if put_call == 'C' or put_call == 'CALL' else 'P'
    return underlying_symbol.ljust(6, ' ') + expiry[2:] + direction + str(int(strike * 1000)).zfill(8)
