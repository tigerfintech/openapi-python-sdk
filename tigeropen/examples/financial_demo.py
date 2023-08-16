import time
from datetime import datetime, timedelta

import pandas as pd
from pandas import DataFrame

from tigeropen.common.consts import Market, Valuation, Balance, Income, CashFlow, FinancialReportPeriodType

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)


class IndicatorCalculator:
    """市盈率等指标计算"""

    def __init__(self, quote_client, symbols, market=Market.US):
        self.quote_client = quote_client
        self.symbols = symbols
        self.market = market

    def get_company_currency(self) -> DataFrame:
        """获取标的公司总市值的所使用的货币单位
        """
        # result 示例
        #        currency company_currency
        # symbol
        # AAPL        USD              USD
        # BABA        USD              USD
        result: DataFrame = self.quote_client.get_financial_currency(self.symbols, self.market).set_index('symbol')
        return result

    def get_exchange_rate(self, source_currency, target_currency) -> float:
        """
        1 source 可以兑换多少 target， 如 source CNY， target HKD， 则返回 7.82/7.26 = 1.077
        """
        if source_currency == target_currency:
            return 1
        today = int(time.time()) * 1000
        # 获取货币和美元兑换的汇率（1美元换多少单位其他货币） result example
        #                    date    value
        # currency
        # HKD       1692028800000  7.81878
        # CNY       1692028800000  7.26230
        result: DataFrame = self.quote_client.get_financial_exchange_rate([source_currency, target_currency],
                                                                          today).set_index('currency')
        rate = result.loc[target_currency].value / result.loc[source_currency].value
        return rate

    def get_market_capital(self):
        """获取总市值

        """
        end = datetime.today()
        begin = end - timedelta(days=1)

        # result example:
        #                         field           date         value
        # symbol
        # AAPL    market_capitalization  1691942400000  2.779610e+12
        # BABA    market_capitalization  1691942400000  2.437778e+11
        result: DataFrame = self.quote_client.get_financial_daily(self.symbols, self.market,
                                                                  fields=[Valuation.market_capitalization],
                                                                  begin_date=int(begin.timestamp()) * 1000,
                                                                  end_date=int(end.timestamp()) * 1000).set_index(
            'symbol')
        return result['value']

    def get_financial(self):
        fields = [
            # 总普通股本
            Balance.total_common_equity,
            # 净收入
            Income.net_income,
            # 总收入
            Income.total_revenue,
            # 每股净资产
            Balance.book_valueshare,
            # 经营净额现金流
            CashFlow.cash_from_ops,

        ]
        #   symbol currency                field       value period_end_date filing_date
        # 0   AAPL      USD  total_common_equity   5.0672E10      2022-09-24  2022-10-28
        # 1   AAPL      USD           net_income   9.9803E10      2022-09-24  2022-10-28
        # 2   AAPL      USD        total_revenue  3.94328E11      2022-09-24  2022-10-28
        # 3   AAPL      USD      book_valueshare    3.178238      2022-09-24  2022-10-28
        # 4   AAPL      USD        cash_from_ops  1.22151E11      2022-09-24  2022-10-28
        # 5   BABA      CNY  total_common_equity  9.89657E11      2023-03-31  2023-07-21
        # 6   BABA      CNY           net_income   7.2783E10      2023-03-31  2023-07-21
        # 7   BABA      CNY        total_revenue  8.68687E11      2023-03-31  2023-07-21
        # 8   BABA      CNY      book_valueshare  385.718073      2023-03-31  2023-07-21
        # 9   BABA      CNY        cash_from_ops  1.99752E11      2023-03-31  2023-07-21
        result = self.quote_client.get_financial_report(self.symbols, self.market, fields,
                                                        period_type=FinancialReportPeriodType.LTM,
                                                        )
        result['value'] = pd.to_numeric(result['value'], errors='coerce')

        # field  currency period_end_date filing_date book_valueshare cash_from_ops net_income total_common_equity total_revenue
        # symbol
        # AAPL        USD      2022-09-24  2022-10-28        3.178238    1.22151E11  9.9803E10           5.0672E10    3.94328E11
        # BABA        CNY      2023-03-31  2023-07-21      385.718073    1.99752E11  7.2783E10          9.89657E11    8.68687E11
        pivot_df = result.pivot(index=['symbol', 'currency', 'period_end_date', 'filing_date'], columns='field',
                                values='value').reset_index().set_index('symbol')
        company_currency = self.get_company_currency()
        pivot_df['company_currency'] = company_currency['company_currency']
        pivot_df['exchange_rate'] = pivot_df.apply(
            lambda row: self.get_exchange_rate(row['company_currency'], row['currency']), axis=1)
        market_cap = self.get_market_capital()
        pivot_df['market_capitalization'] = market_cap * pivot_df['exchange_rate']
        # print(pivot_df)
        # 市净率
        pivot_df['pb_rate'] = pivot_df['market_capitalization'] / pivot_df['total_common_equity']
        # 市盈率
        pivot_df['pe_rate'] = pivot_df['market_capitalization'] / pivot_df['net_income']
        # 市销率
        pivot_df['ps_rate'] = pivot_df['market_capitalization'] / pivot_df['total_revenue']

        # 结果示例
        # field  currency period_end_date filing_date  book_valueshare  cash_from_ops    net_income  total_common_equity  total_revenue company_currency  exchange_rate  market_capitalization    pb_rate    pe_rate   ps_rate
        # symbol
        # AAPL        USD      2023-07-01  2023-08-04         3.851898   1.130720e+11  9.476000e+10         6.027400e+10   3.839330e+11              USD         1.0000           2.779610e+12  46.116238  29.333159  7.239831
        # BABA        CNY      2023-06-30  2023-08-10       397.452549   2.111890e+11  8.436600e+10         1.013504e+12   8.972880e+11              USD         7.2623           1.770387e+12   1.746798  20.984605  1.973042
        print(pivot_df)
        # 打印第一个股票的市盈率
        print(f'{self.symbols[0]} PE rate: {pivot_df.loc[self.symbols[0]]["pe_rate"]}')


if __name__ == '__main__':
    # 此处修改为自己环境对应的 quote_client 实例
    from client import quote_client

    calculator = IndicatorCalculator(quote_client, symbols=['AAPL', 'BABA'], market=Market.US)
    # calculator = IndicatorCalculator(quote_client, symbols=['09988'], market=Market.HK)
    calculator.get_financial()
