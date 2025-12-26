# -*- coding: utf-8 -*-
"""
Created on 2025/12/23

@author: sukai
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.trade.domain.transfer import PositionTransfer, PositionTransferRecord, PositionTransferDetail, \
    TransferDetailItem, PositionTransferExternalRecord, TransferPropertyInfo


class PositionTransferResponse(TigerResponse):
    def __init__(self):
        super(PositionTransferResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(PositionTransferResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.result = PositionTransfer()
            for key, value in self.data.items():
                if hasattr(self.result, string_utils.camel_to_underline(key)):
                    setattr(self.result, string_utils.camel_to_underline(key), value)


class PositionTransferRecordsResponse(TigerResponse):
    def __init__(self):
        super(PositionTransferRecordsResponse, self).__init__()
        self.result = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(PositionTransferRecordsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            for item in self.data:
                record = PositionTransferRecord()
                for key, value in item.items():
                    if hasattr(record, string_utils.camel_to_underline(key)):
                        setattr(record, string_utils.camel_to_underline(key), value)
                self.result.append(record)


class PositionTransferDetailResponse(TigerResponse):
    def __init__(self):
        super(PositionTransferDetailResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(PositionTransferDetailResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.result = PositionTransferDetail()
            for key, value in self.data.items():
                if key == 'detail':
                    details = []
                    for detail_item in value:
                        item = TransferDetailItem()
                        for k, v in detail_item.items():
                            if hasattr(item, string_utils.camel_to_underline(k)):
                                setattr(item, string_utils.camel_to_underline(k), v)
                        details.append(item)
                    self.result.detail = details
                elif hasattr(self.result, string_utils.camel_to_underline(key)):
                    setattr(self.result, string_utils.camel_to_underline(key), value)


class PositionTransferExternalRecordsResponse(TigerResponse):
    def __init__(self):
        super(PositionTransferExternalRecordsResponse, self).__init__()
        self.result = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(PositionTransferExternalRecordsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            for item in self.data:
                record = PositionTransferExternalRecord()
                for key, value in item.items():
                    if key == 'transferPropertyInfos':
                        infos = []
                        for info_item in value:
                            info = TransferPropertyInfo()
                            for k, v in info_item.items():
                                if hasattr(info, string_utils.camel_to_underline(k)):
                                    setattr(info, string_utils.camel_to_underline(k), v)
                            infos.append(info)
                        record.transfer_property_infos = infos
                    elif hasattr(record, string_utils.camel_to_underline(key)):
                        setattr(record, string_utils.camel_to_underline(key), value)
                self.result.append(record)
