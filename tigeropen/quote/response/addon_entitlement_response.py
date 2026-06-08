# -*- coding: utf-8 -*-
"""
Created on 2026/06/08

@author: tigeropen
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.quote.domain.addon_entitlement import AddonEntitlement, ActivePlan, AddonInfo, Entitlement


class AddonEntitlementResponse(TigerResponse):
    """Response parser for addon entitlement API."""

    def __init__(self):
        super(AddonEntitlementResponse, self).__init__()
        self.result = None
        self._is_success = None

    @staticmethod
    def _fill(obj, value):
        """Fill a domain object from a dict, converting camelCase keys to snake_case.

        Keeps the default attributes declared in the object's __init__ so that fields
        absent from the server response remain None instead of raising AttributeError.
        """
        for key, val in string_utils.camel_to_underline_obj(value).items():
            setattr(obj, key, val)
        return obj

    def parse_response_content(self, response_content):
        response = super(AddonEntitlementResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if not self.data or not isinstance(self.data, dict):
            return

        entitlement = AddonEntitlement()
        for key, value in self.data.items():
            if key == 'activePlan' and isinstance(value, dict):
                entitlement.active_plan = self._fill(ActivePlan(), value)
            elif key == 'addons' and isinstance(value, list):
                entitlement.addons = [self._fill(AddonInfo(), item) for item in value]
            elif key == 'effectiveEntitlement' and isinstance(value, dict):
                entitlement.effective_entitlement = self._fill(Entitlement(), value)
            else:
                setattr(entitlement, string_utils.camel_to_underline(key), value)

        self.result = entitlement
