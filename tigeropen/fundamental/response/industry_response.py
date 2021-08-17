# -*- coding: utf-8 -*-

from tigeropen.common.response import TigerResponse


class IndustryListResponse(TigerResponse):
    def __init__(self):
        super(IndustryListResponse, self).__init__()
        self.industry_list = list()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(IndustryListResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data:
            for ind in self.data:
                industry = dict(industry_level=ind.get('industryLevel'), id=ind.get('id'),
                                name_cn=ind.get('nameCN'),
                                name_en=ind.get('nameEN'))
                self.industry_list.append(industry)


class IndustryStocksResponse(TigerResponse):
    def __init__(self):
        super(IndustryStocksResponse, self).__init__()
        self.industry_stocks = list()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(IndustryStocksResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data:
            for item in self.data:
                industry_list = list()
                industries = item.get('industryDetailDTOList', [])
                for ind in industries:
                    industry_list.append(dict(industry_level=ind.get('industryLevel'), id=ind.get('id'),
                                              name_cn=ind.get('nameCN'),
                                              name_en=ind.get('nameEN')))
                company = dict(symbol=item.get('symbol'), company_name=item.get('companyName'),
                               market=item.get('market'), industry_list=industry_list)
                self.industry_stocks.append(company)


class StockIndustryResponse(TigerResponse):
    def __init__(self):
        super(StockIndustryResponse, self).__init__()
        self.stock_industry = list()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(StockIndustryResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data:
            for item in self.data:
                industry = dict(industry_level=item.get('industryLevel'), id=item.get('id'),
                                name_cn=item.get('nameCN'),
                                name_en=item.get('nameEN'))
                self.stock_industry.append(industry)
