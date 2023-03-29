# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import logging
from collections import defaultdict


class Account:
    """
    The account object tracks information about the trading account. The
    values are updated as the algorithm runs and its keys remain unchanged.
    If connected to a broker, one can update these values with the trading
    account values as reported by the broker.

    ∆ 开头的表示只是用于证券Segment
    - accrued_cash: 当前月份的累积应付利息，按照日频更新。
    - accrued_dividend: 累计分红. 指的是所有已执行但仍未支付的分红累加值
    - available_funds: 可用资金（可用于交易）。 计算方法为 equity_with_loan - initial_margin_requirement
    - ∆ buying_power: 购买力。 预估您还可以购入多少美元的股票资产。保证金账户日内最多有四倍于资金（未被占用做保证金的资金）的购买力。
                      隔夜最多有两倍的购买力。
    - cash: 现金
    - currency: 币种
    - cushion: 剩余流动性占总资产的比例，计算方法为: excess_liquidity/net_liquidation
    - ∆ day_trades_remaining: 当日剩余日内交易次数， -1 表示无限制
    - equity_with_loan:含借贷值股权(含贷款价值资产)
        - 证券 Segment: 现金价值 + 股票价值
        - 期货 Segment: 现金价值 - 维持保证金
    - excess_liquidity:剩余流动性
        - 证券 Segment: 计算方法: equity_with_loan - maintenance_margin_requirement
        - 期货 Segment: 计算方法: net_liquidation - maintenance_margin_requirement
    - ∆ gross_position_value: 证券总价值: 做多股票的价值+做空股票价值+做多期权价值+做空期权价值。以上各项取绝对值计算。
    - initial_margin_requirement: 初始保证金
    - maintenance_margin_requirement: 维持保证金
    - net_liquidation: 总资产(净清算价值)
        - 证券 Segment: 现金价值 + 股票价值 + 股票期权价值
        - 期货 Segment: 现金价值 + 盯市盈亏
    - realized_pnl: 本日已实现盈亏
    - ∆ regt_equity: 仅针对证券Segment，即根据 Regulation T 法案计算的 equity with loan（含借贷股权值）
    - ∆ regt_margin:仅针对证券Segment， 即根据 Regulation T 法案计算的 initial margin requirements（初始保证金）
    - ∆ sma: 仅针对证券Segment。隔夜风控值，每个交易日收盘前10分钟左右对账户持仓的隔夜风险进行检查，隔夜风控值需要大于0，
             否则会在收盘前对账户部分头寸强制平仓。如果交易日盘中出现隔夜风控值低于0，而时间未到收盘前10分钟，账户不会出发强平。
    - unrealized_pnl: 未实现盈亏
    - timestamp: 更新时间
    """
    def __init__(self):
        self.accrued_cash = float('inf')
        self.accrued_dividend = float('inf')
        self.available_funds = float('inf')
        self.buying_power = float('inf')
        self.cash = float('inf')
        self.currency = None
        self.cushion = float('inf')
        self.day_trades_remaining = float('inf')
        self.equity_with_loan = float('inf')
        self.excess_liquidity = float('inf')
        self.gross_position_value = float('inf')
        self.initial_margin_requirement = float('inf')
        self.maintenance_margin_requirement = float('inf')
        self.net_liquidation = float('inf')
        self.realized_pnl = float('inf')
        self.regt_equity = float('inf')
        self.regt_margin = float('inf')
        self.sma = float('inf')
        self.timestamp = None
        self.unrealized_pnl = float('inf')

    def __repr__(self):
        return "Account({0})".format(self.__dict__)


class SecuritySegment:
    """
    - accrued_cash: 当前月份的累积应付利息，按照日频更新。
    - accrued_dividend: 累计分红. 指的是所有已执行但仍未支付的分红累加值
    - available_funds: 可用资金（可用于交易）。 计算方法为 equity_with_loan - initial_margin_requirement
    - cash: 现金
    - equity_with_loan: 含借贷值股权(含贷款价值资产)。计算方法： 现金价值 + 股票价值
    - excess_liquidity: 剩余流动性。计算方法: equity_with_loan - maintenance_margin_requirement
    - gross_position_value: 证券总价值: 做多股票的价值+做空股票价值+做多期权价值+做空期权价值。
    - initial_margin_requirement: 初始保证金
    - leverage: gross_position_value / net_liquidation
    - maintenance_margin_requirement: 维持保证金
    - net_liquidation: 总资产(净清算价值)。 计算方法： 现金价值 + 股票价值 + 股票期权价值
    - regt_equity: 根据 Regulation T 法案计算的 equity with loan（含借贷股权值）
    - regt_margin: 根据 Regulation T 法案计算的 initial margin requirements（初始保证金）
    - sma: 隔夜风控值，每个交易日收盘前10分钟左右对账户持仓的隔夜风险进行检查，隔夜风控值需要大于0，
             否则会在收盘前对账户部分头寸强制平仓。如果交易日盘中出现隔夜风控值低于0，而时间未到收盘前10分钟，账户不会出发强平。
    - timestamp: 更新时间
    """
    def __init__(self):
        self.accrued_cash = float('inf')
        self.accrued_dividend = float('inf')
        self.available_funds = float('inf')
        self.cash = float('inf')
        self.equity_with_loan = float('inf')
        self.excess_liquidity = float('inf')
        self.gross_position_value = float('inf')
        self.initial_margin_requirement = float('inf')
        self.leverage = float('inf')
        self.maintenance_margin_requirement = float('inf')
        self.net_liquidation = float('inf')
        self.regt_equity = float('inf')
        self.regt_margin = float('inf')
        self.sma = float('inf')
        self.timestamp = None

    def __repr__(self):
        return "SecuritySegment({0})".format(self.__dict__)


class CommoditySegment:
    """
    - accrued_cash: 当前月份的累积应付利息，按照日频更新。
    - accrued_dividend:累计分红. 指的是所有已执行但仍未支付的分红累加值
    - available_funds: 可用资金（可用于交易）。 计算方法为 equity_with_loan - initial_margin_requirement
    - cash: 现金
    - equity_with_loan:含借贷值股权(含贷款价值资产)计算方法：现金价值 - 维持保证金
    - excess_liquidity:剩余流动性。计算方法：net_liquidation - maintenance_margin_requirement
    - initial_margin_requirement: 初始保证金
    - maintenance_margin_requirement: 维持保证金
    - net_liquidation: 总资产(净清算价值)。计算方法：现金价值 + 盯市盈亏
    - gross_position_value: 持仓总价值
    - timestamp: 更新时间
    """
    def __init__(self):
        self.accrued_cash = float('inf')
        self.accrued_dividend = float('inf')
        self.available_funds = float('inf')
        self.cash = float('inf')
        self.equity_with_loan = float('inf')
        self.excess_liquidity = float('inf')
        self.initial_margin_requirement = float('inf')
        self.maintenance_margin_requirement = float('inf')
        self.net_liquidation = float('inf')
        self.gross_position_value = float('inf')
        self.timestamp = None

    def __repr__(self):
        return "CommoditySegment({0})".format(self.__dict__)


class MarketValue:
    """
    - currency: 货币单位
    - net_liquidation: 总资产(净清算价值)
    - cash_balance: 现金
    - stock_market_value: 股票市值
    - option_market_value: 期权市值
    - warrant_value: 窝轮市值
    - futures_pnl: 盯市盈亏
    - unrealized_pnl: 未实现盈亏
    - realized_pnl: 已实现盈亏
    - exchange_rate: 对账户主币种的汇率
    - net_dividend: 应付股息与应收股息的净值
    - timestamp: 更新时间
    """
    def __init__(self):
        self.currency = None
        self.net_liquidation = float('inf')
        self.cash_balance = float('inf')
        self.stock_market_value = float('inf')
        self.option_market_value = float('inf')
        self.warrant_value = float('inf')
        self.futures_pnl = float('inf')
        self.unrealized_pnl = float('inf')
        self.realized_pnl = float('inf')
        self.exchange_rate = float('inf')
        self.net_dividend = float('inf')
        self.timestamp = None

    def __repr__(self):
        return "MarketValue({0})".format(self.__dict__)


class PortfolioAccount:
    def __init__(self, account):
        self._account = account
        self._summary = Account()
        self._segments = defaultdict(Account)
        self._market_values = defaultdict(MarketValue)

    @property
    def account(self):
        """账户 id"""
        return self._account

    @property
    def summary(self):
        """
        对几个 segments 下的统计
        :return: Account 对象
        """
        return self._summary

    def segment(self, segment_name):
        if segment_name not in self._segments:  # C, S, F
            if segment_name == 'C':
                segment = CommoditySegment()
            elif segment_name == 'S':
                segment = SecuritySegment()
            elif segment_name == 'F':
                segment = Account()
            else:
                logging.info("unknown segment %s", segment_name)
                segment = Account()
            self._segments[segment_name] = segment
            return segment
        else:
            return self._segments.get(segment_name)

    @property
    def segments(self):
        """
        按照交易品种区分的账户信息
        :return: dict，分别有两个 key，'S'表示股票， 'C' 表示期货；
        """
        return self._segments

    def market_value(self, currency):
        if currency in self._market_values:
            return self._market_values.get(currency)
        else:
            market_value = MarketValue()
            self._market_values[currency] = market_value
            return market_value

    @property
    def market_values(self):
        """
        按照币种区分的市值信息
        :return: dict， 其中的 key: 'USD' 表示美元， 'HKD' 表示港币; value 是一个 MarketValue 对象
        """
        return self._market_values

    def __repr__(self):
        return "PortfolioAccount({0})".format({'account': self.account, 'summary': self.summary,
                                               'segments': self.segments, 'market_values': self.market_values})


class SegmentFundAvailableItem:
    def __init__(self, from_segment=None, currency=None, amount=None):
        self.from_segment = from_segment
        self.currency = currency
        self.amount = amount

    def __repr__(self):
        return "SegmentFundAvailableItem({0})".format(self.__dict__)


class SegmentFundItem:
    def __init__(self, id=None, from_segment=None, to_segment=None, currency=None, amount=None, status=None,
                 status_desc=None, message=None, settled_at=None, updated_at=None, created_at=None):
        self.id = id
        self.from_segment = from_segment
        self.to_segment = to_segment
        self.currency = currency
        self.amount = amount
        self.status = status
        self.status_desc = status_desc
        self.message = message
        self.settled_at = settled_at
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self):
        return "SegmentFundItem({0})".format(self.__dict__)