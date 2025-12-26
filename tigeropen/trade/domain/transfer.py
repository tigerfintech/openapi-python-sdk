# -*- coding: utf-8 -*-
"""
Created on 2025/12/23

@author: sukai
"""
from tigeropen.common.util.string_utils import camel_to_underline


class PositionTransfer:
    def __init__(self, id=None, account_id=None, counterparty_account_id=None, method=None, direction=None, status=None,
                 comment=None, user_id=None, user_name=None, memo=None, finished_at=None, updated_at=None,
                 created_at=None):
        self.id = id
        self.account_id = account_id
        self.counterparty_account_id = counterparty_account_id
        self.method = method
        self.direction = direction
        self.status = status
        self.comment = comment
        self.user_id = user_id
        self.user_name = user_name
        self.memo = memo
        self.finished_at = finished_at
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self):
        return "PositionTransfer(%s)" % self.__dict__


class PositionTransferRecord:
    def __init__(self, id=None, account_id=None, counterparty_account_id=None, method=None, direction=None, status=None,
                 memo=None, user_id=None, user_name=None, finished_at=None, updated_at=None, created_at=None):
        self.id = id
        self.account_id = account_id
        self.counterparty_account_id = counterparty_account_id
        self.method = method
        self.direction = direction
        self.status = status
        self.memo = memo
        self.user_id = user_id
        self.user_name = user_name
        self.finished_at = finished_at
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self):
        return "PositionTransferRecord(%s)" % self.__dict__


class PositionTransferDetail:
    def __init__(self, id=None, account_id=None, counterparty_account_id=None, method=None, direction=None, status=None,
                 memo=None, user_id=None, user_name=None, finished_at=None, updated_at=None, created_at=None,
                 detail=None):
        self.id = id
        self.account_id = account_id
        self.counterparty_account_id = counterparty_account_id
        self.method = method
        self.direction = direction
        self.status = status
        self.memo = memo
        self.user_id = user_id
        self.user_name = user_name
        self.finished_at = finished_at
        self.updated_at = updated_at
        self.created_at = created_at
        self.detail = detail

    def __repr__(self):
        return "PositionTransferDetail(%s)" % self.__dict__


class TransferDetailItem:
    def __init__(self, transfer_id=None, direction=None, symbol=None, formatted_symbol=None,
                 market=None, quantity=None, status=None, message=None, updated_at=None, created_at=None):
        self.transfer_id = transfer_id
        self.direction = direction
        self.symbol = symbol
        self.formatted_symbol = formatted_symbol
        self.market = market
        self.quantity = quantity
        self.status = status
        self.message = message
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self):
        return "TransferDetailItem(%s)" % self.__dict__


class PositionTransferExternalRecord:
    def __init__(self, id=None, status=None, all_finished=None, counterparty_contacted=None, account_id=None,
                 transfer_method=None, transfer_property_infos=None, institution_name=None, institution_type=None,
                 remote_clearing_broker=None, dtc_number=None, remote_user_name=None, remote_account=None,
                 contact_name=None, contact_email=None, contact_phone=None, cancelable=None, created_at=None,
                 updated_at=None, side=None, market=None, user_name=None, transfer_hin=None,
                 full_portfolio=None):
        self.id = id
        self.status = status
        self.all_finished = all_finished
        self.counterparty_contacted = counterparty_contacted
        self.account_id = account_id
        self.transfer_method = transfer_method
        self.transfer_property_infos = transfer_property_infos
        self.institution_name = institution_name
        self.institution_type = institution_type
        self.remote_clearing_broker = remote_clearing_broker
        self.dtc_number = dtc_number
        self.remote_user_name = remote_user_name
        self.remote_account = remote_account
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.cancelable = cancelable
        self.created_at = created_at
        self.updated_at = updated_at
        self.side = side
        self.market = market
        self.user_name = user_name
        self.transfer_hin = transfer_hin
        self.full_portfolio = full_portfolio

    def __repr__(self):
        return "PositionTransferExternalRecord(%s)" % self.__dict__


class TransferPropertyInfo:
    def __init__(self, id=None, symbol=None, market=None, sec_type=None, stock_name=None, quantity=None,
                 average_cost=None, status=None, cancelable=None, updated_at=None):
        self.id = id
        self.symbol = symbol
        self.market = market
        self.sec_type = sec_type
        self.stock_name = stock_name
        self.quantity = quantity
        self.average_cost = average_cost
        self.status = status
        self.cancelable = cancelable
        self.updated_at = updated_at

    def __repr__(self):
        return "TransferPropertyInfo(%s)" % self.__dict__

class TransferItem:
    def __init__(self, symbol=None, quantity=None, expiry=None, strike=None, right=None, sec_type=None):
        self.symbol = symbol
        self.quantity = quantity
        self.expiry = expiry
        self.strike = strike
        self.right = right
        self.sec_type = sec_type

    def __repr__(self):
        return "TransferItem(%s)" % self.__dict__
