# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class AccountProfile(object):
    def __init__(self, account, capability, status):
        self.account = account
        self.capability = capability
        self.status = status

    def __repr__(self):
        """
        String representation for this object.
        """
        return "AccountProfile(%s)" % self.__dict__
