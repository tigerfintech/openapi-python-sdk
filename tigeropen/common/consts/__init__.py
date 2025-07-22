# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import threading
from enum import Enum, unique

from .fundamental_fields import Valuation, Income, Balance, CashFlow, BalanceSheetRatio, Growth, \
    Leverage, Profitability
from .quote_keys import QuoteChangeKey, QuoteKeyType

OPEN_API_SERVICE_VERSION_V1 = "1.0"
OPEN_API_SERVICE_VERSION = "2.0"
OPEN_API_SERVICE_VERSION_V3 = "3.0"

THREAD_LOCAL = threading.local()


@unique
class Market(Enum):
    """Enum for market """

    ALL = 'ALL'
    US = 'US'  # 美股
    HK = 'HK'  # 港股
    CN = 'CN'  # A股
    SG = 'SG'  # 新加坡


@unique
class TradingSession(Enum):
    All = 'All'
    PreMarket = 'PreMarket'  # 盘前
    Regular = 'Regular'  # 盘中
    AfterHours = 'AfterHours'  # 盘后
    OverNight = 'OverNight'


@unique
class TradingSessionType(Enum):
    PRE_RTH_POST = 'PRE_RTH_POST'
    OVERNIGHT ='OVERNIGHT' # 夜盘
    RTH = 'RTH' # 盘中
    FULL ='FULL' # 全时段
    HK_AUC = 'HK_AUC'
    HK_CTS = 'HK_CTS'
    HK_AUC_CTS ='HK_AUC_CTS'


@unique
class SecurityType(Enum):
    """Enum for sec_type """

    ALL = 'ALL'
    STK = 'STK'  # 股票
    OPT = 'OPT'  # 期权
    WAR = 'WAR'  # 窝轮
    IOPT = 'IOPT'  # 权证(牛熊证)
    FUT = 'FUT'  # 期货
    FOP = 'FOP'  # 期货期权
    CASH = 'CASH'  # 外汇
    MLEG = 'MLEG'  # 期权组合
    FUND = 'FUND'  # 基金


@unique
class SegmentType(Enum):
    ALL = 'ALL'
    SEC = 'SEC'
    FUT = 'FUT'
    FUND = 'FUND'


@unique
class Currency(Enum):
    """Enum for currency """

    ALL = 'ALL'
    USD = 'USD'  # 美元
    HKD = 'HKD'  # 港币
    CNH = 'CNH'  # 离岸人民币
    SGD = 'SGD'  # 新加坡币


@unique
class Language(Enum):
    zh_CN = 'zh_CN'  # 简体中文
    zh_TW = 'zh_TW'  # 繁体中文
    en_US = 'en_US'  # 英文


@unique
class QuoteRight(Enum):
    BR = 'br'  # 前复权
    NR = 'nr'  # 不复权


@unique
class TimelinePeriod(Enum):
    DAY = 'day'  # 当天分时
    FIVE_DAYS = '5day'  # 5日分时


@unique
class BarPeriod(Enum):
    DAY = 'day'  # 日K
    WEEK = 'week'  # 周K
    MONTH = 'month'  # 月K
    YEAR = 'year'  # 年K
    ONE_MINUTE = '1min'  # 1分钟
    THREE_MINUTES = '3min'  # 3分钟
    FIVE_MINUTES = '5min'  # 5分钟
    TEN_MINUTES = '10min'  # 10分钟
    FIFTEEN_MINUTES = '15min'  # 15分钟
    HALF_HOUR = '30min'  # 30分钟
    FORTY_FIVE_MINUTES = '45min'  # 45分钟
    ONE_HOUR = '60min'  # 60分钟
    TWO_HOURS = '2hour'  # 2小时
    THREE_HOURS = '3hour'  # 3小时
    FOUR_HOURS = '4hour'  # 4小时
    SIX_HOURS = '6hour'  # 6小时


class CapitalPeriod(Enum):
    INTRADAY = "intraday"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    QUARTER = "quarter"
    HALFAYEAR = "6month"


class OrderStatus(Enum):
    PENDING_NEW = 'PendingNew'
    NEW = 'Initial'  # 订单初始状态
    HELD = 'Submitted'  # 已提交
    PARTIALLY_FILLED = 'PartiallyFilled'  # 部分成交
    FILLED = 'Filled'  # 完全成交
    CANCELLED = 'Cancelled'  # 已取消
    PENDING_CANCEL = 'PendingCancel'  # 待取消
    REJECTED = 'Inactive'  # 已失效
    EXPIRED = 'Invalid'  # 非法状态


@unique
class FinancialReportPeriodType(Enum):
    """
    财报类型
    """
    ANNUAL = 'Annual'  # 年报
    QUARTERLY = 'Quarterly'  # 季报
    LTM = 'LTM'  # 最近四个季度


@unique
class CorporateActionType(Enum):
    """
    公司行动类型
    """
    SPLIT = 'split'  # 拆合股
    DIVIDEND = 'dividend'  # 分红
    EARNINGS_CALENDAR = 'earning'  # 财报日历


@unique
class IndustryLevel(Enum):
    """
    行业级别. 级别从1级到4级依次为: GSECTOR, GGROUP, GIND, GSUBIND
    """
    GSECTOR = 'GSECTOR'
    GGROUP = 'GGROUP'
    GIND = 'GIND'
    GSUBIND = 'GSUBIND'


@unique
class SortDirection(Enum):
    NO = 'SortDir_No'
    ASC = 'SortDir_Ascend'
    DESC = 'SortDir_Descend'


@unique
class TickSizeType(Enum):
    CLOSED = 'CLOSED'
    OPEN_CLOSED = 'OPEN_CLOSED'
    OPEN = 'OPEN'
    CLOSED_OPEN = 'CLOSED_OPEN'


@unique
class OrderSortBy(Enum):
    LATEST_CREATED = 'LATEST_CREATED'
    LATEST_STATUS_UPDATED = 'LATEST_STATUS_UPDATED'


@unique
class OrderType(Enum):
    MKT = 'MKT'  # 市价单
    LMT = 'LMT'  # 限价单
    STP = 'STP'  # 止损单
    STP_LMT = 'STP_LMT'  # 止损限价单
    TRAIL = 'TRAIL'  # 跟踪止损单
    AM = 'AM'  # Auction Market ，竞价市价单
    AL = 'AL'  # Auction Limit ，竞价限价单
    TWAP = 'TWAP'  # 'Time Weighted Average Price' 时间加权平均价格算法
    VWAP = 'VWAP'  # 'Volume Weighted Average Price'  成交量加权平均价格算法
    OCA = 'OCA'


@unique
class License(Enum):
    TBNZ = 'TBNZ'
    TBSG = 'TBSG'
    TBHK = 'TBHK'
    TBAU = 'TBAU'
    TBUS = 'TBUS'


@unique
class ServiceType(Enum):
    COMMON = 'COMMON'
    TRADE = 'TRADE'
    QUOTE = 'QUOTE'


@unique
class ComboType(Enum):
    COVERED = 'COVERED'
    PROTECTIVE = 'PROTECTIVE'
    VERTICAL = 'VERTICAL'
    STRADDLE = 'STRADDLE'
    STRANGLE = 'STRANGLE'
    CALENDAR = 'CALENDAR'
    DIAGONAL = 'DIAGONAL'
    SYNTHETIC = 'SYNTHETIC'
    CUSTOM = 'CUSTOM'


class StockRankingIndicator(Enum):
    ChangeRate = "changeRate"
    ChangeRate5Min = "changeRate5Min"
    TurnoverRate = "turnoverRate"
    Amount = "amount"  # trade amount
    Volume = "volume"  # trade volume
    Amplitude = "amplitude"


class OptionRankingIndicator(Enum):
    BigOrder = "bigOrder"
    Volume = "volume"
    Amount = "amount"
    OpenInt = "openInt"

class AssetQuoteType(Enum):
    # Includes pre-market, intra-day, and after-hours trading data. For night session, the closing price of the previous after-hours trading is used for calculation.
    ETH = "ETH"
    # Only intra-day trading data. For pre-market, after-hours, and night session, the intra-day closing price is used for calculation.
    RTH = "RTH"
    # Includes night session trading data. For night session, the night session trading data is used for calculation.
    OVERNIGHT = "OVERNIGHT"