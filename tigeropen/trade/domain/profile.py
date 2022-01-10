# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class AccountProfile:
    def __init__(self, account, capability, status, account_type=None):
        self.account = account
        self.capability = capability
        self.status = status
        self.account_type = account_type

    def __repr__(self):
        """
        String representation for this object.
        """
        return "AccountProfile(%s)" % self.__dict__
