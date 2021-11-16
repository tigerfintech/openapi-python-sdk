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
    PreMarket = 'PreMarket'  # 盘前
    Regular = 'Regular'  # 盘中
    AfterHours = 'AfterHours'  # 盘后


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
