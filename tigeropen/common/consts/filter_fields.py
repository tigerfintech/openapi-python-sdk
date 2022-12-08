# -*- coding: utf-8 -*-
# 
# @Date    : 2022/12/1
# @Author  : sukai
from abc import abstractmethod
from enum import Enum


class FilterField(Enum):
    def __new__(cls, index, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = index
        return obj

    def __init__(self, index, field):
        self.index = index
        self.field = field

    @property
    def field_type(self):
        return self.__class__.__name__

    @property
    def field_type_request_name(self):
        return self.field_type + '_Type'


class StockField(FilterField):
    # 最新价*（精确到小数点后 3 位，超出部分会被舍弃）例如填写[10,20]值区间
    CurPrice = 2, "latestPrice"
    # 买入价（精确到小数点后 3 位，超出部分会被舍弃）例如填写[10,20]值区间
    BidPrice = 3, "bidPrice"
    # 卖出价（精确到小数点后 3 位，超出部分会被舍弃）例如填写[10,20]值区间
    AskPrice = 4, "askPrice"
    # 今开价（精确到小数点后 3 位，超出部分会被舍弃）例如填写[10,20]值区间
    OpenPrice = 5, "open"
    # 昨收价（精确到小数点后 3 位，超出部分会被舍弃）例如填写[10,20]值区间
    PreClosePrice = 6, "preClose"
    # 最高价
    HighPrice = 7, "high"
    # 最低价
    LowPrice = 8, "low"
    # 盘前价*（精确到小数点后 3 位，超出部分会被舍弃）例如填写[10,20]值区间
    HourTradingPrePrice = 9, "hourTradingPrePrice"
    # 盘后价*（精确到小数点后 3 位，超出部分会被舍弃）例如填写[10,20]值区间
    HourTradingAfterPrice = 10, "hourTradingAfterPrice"
    # 成交量*
    Volume = 11, "volume"
    # 成交额*
    Amount = 12, "amount"
    # 流通股本*
    FloatShare = 13, "floatShares"
    # 52周最高价格*
    Week52High = 14, "week52High"
    # 52周最低价格*
    Week52Low = 15, "week52Low"
    # 通市值* FloatMarketVal  自己计算 FloatShare* 当前价格
    FloatMarketVal = 16, "floatMarketCap"
    # 总市值*  MarketVal  shares * 当前价格
    MarketValue = 17, "marketValue"
    # 盘前涨跌幅   (curPrice-盘前左收）自己计算 最新价-close / close
    preHourTradingChangeRate = 18, "preHourTradingChangeRate"
    # 盘后涨跌幅 自己计算
    postHourTradingChangeRate = 19, "postHourTradingChangeRate"
    # 每股收益 滚动市盈率 TTM=过去12个月  Last Twelve Month  通过hermes获取 eps
    ttm_Eps = 20, "ttmEps"
    # 量比*（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    VolumeRatio = 21, "volumeRatio"
    # 委比*（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    BidAskRatio = 22, "committee"
    # 下次财报日期 *
    EarningDate = 23, "earningDate"
    # 市盈率* TTM（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    PeTTM = 24, "peRate"
    # 市净率*（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    PbRate = 25, "pbRate"
    # 股息   hermes $
    DividePrice = 26, "dividePrice"
    # 股息收益率 选股服务自身计算
    DivideRate = 27, "divideRate"
    # 股票交易市场
    Exchange = 29, "exchange"
    # 换手率*（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    TurnoverRate = 30, "turnoverRate"
    # 上市时间
    ListingDate = 31, "listingDate"
    # 市盈率LYR* TTM（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    LyrPeRate = 32, "LyrPeRate"
    # 总股本*
    Share = 33, "shares"
    # 上市价格*
    ListingPrice = 34, "listingPrice"
    # 交易币种*
    TradeCurrency = 35, "tradeCurrency"
    # 最新价-发行价*
    DiffBetweenLastPriceAndListPrice = 36, "DiffBetweenLastPriceAndListPrice"
    # 每股收益 lyr=Last Year Ratio 静态市盈率
    lyr_Eps = 37, "lyrEps"
    # 未平仓做空量
    Open_Short_Interest = 38, "OpenShortInterest"
    # 未平仓做空比例 = 未平仓做空量/总股本
    Open_Short_Interest_Ratio = 39, "OpenShortInterestRatio"
    # 产权比率 = Liability/Equity 总负债/股东
    Equity_Ratio = 40, "EquityRatio"
    # 权益乘数 = Asset/Equity
    Equity_Multiplier = 41, "EquityMultiplier"
    # 最新股东数
    Holder_Nums = 42, "holderNums"
    # 最新股东户数增长率
    Holder_Nums_Ratio = 43, "holderRatio"
    # 户均持股数量
    Per_Hold_Nums = 44, "perHolderNums"
    # 户均持股金额
    Per_Hold_Money = 45, "perHolderMoney"
    # 户均持股数半年增长率
    HalfYear_Holder_Nums_Ratio = 46, "HalfYearholderRatio"
    # 发行时间 - ETF
    InceptionDate = 47, "inceptionDate"
    # 申购费用 - ETF
    CreationFee = 48, "creationFee"
    # 管理费用 - ETF
    ManagementFee = 49, "managementFee"
    # 成分股Top10 占比 - ETF
    Top10_Composition_Rate = 50, "Top10CompoRate"
    # 成分股Top15 占比 - ETF
    Top15_Composition_Rate = 51, "Top15CompoRate"
    # 成分股Top20 占比 - ETF
    Top20_Composition_Rate = 52, "Top20CompoRate"
    # 溢价率(折扣率) - ETF
    DiscountPremium = 53, "discountPremium"
    # 股息率 - ETF
    dividend_Rate = 54, "dividendRate"
    # 资产规模-净值 - ETF
    Net_Worth_Aum = 55, "aum"
    # 资产规模-现价 - ETF
    assetSize = 56, "assetSize"
    # 振幅
    Amplitude = 57, "Amplitude"


class AccumulateField(FilterField):
    # 涨跌幅*（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    ChangeRate = 1, "changeRate"
    # 涨跌额*（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    ChangeValue = 2, "change"
    # 总负债增长率
    TotalLiabilities_Ratio_Annual = 3, "totalLiabilitiesRatio"
    # 净资产增长率
    TotalCommonEquity_Ratio_Annual = 4, "totalCommonEquityRatio"
    # 每股收益同比增长率
    BasicEps_Ratio_Annual = 5, "basicEpsRatio"
    # 净利润同比增长率
    NetIncome_Ratio_Annual = 6, "netIncomeRatio"
    # 营业利润同比增长率
    OperatingIncome_Ratio_Annual = 7, "opeIncomeratio"
    # 每股收益
    Eps = 8, "eps"
    # 每股净资产
    NetAsset_PerShare = 9, "bookValueshare"
    # 净利润
    Net_Income = 10, "netIncome"
    # 营业利润
    Operating_Income = 11, "operatingIncome"
    # 营业收入
    Total_Revenue = 12, "total_revenue"
    # ROE = 资产回报率
    ROE = 13, "ROE"
    # ROA = 净资产收益率
    ROA = 14, "ROA"
    # 股息   hermes $
    DividePrice = 15, "dividePrice"
    # 股息收益率 选股服务自身计算
    DivideRate = 16, "divideRate"
    # 毛利率
    GrossProfitRate = 17, "grossMargin"
    # 净利率*
    NetProfitRate = 18, "netIncomeMargin"
    # 总资产*
    TotalAssets = 19, "totalAssets"
    # 流动比率
    CurrentRatio = 20, "currentRatio"
    # 速动比率
    QuickRatio = 21, "quickRatio"
    # 经营现金流
    CashFromOps = 22, "cash4Ops"
    # 投资现金流
    CashFromInvesting = 23, "cash4Invest"
    # 筹资现金流
    CashFromFinancing = 24, "cash4Finance"
    # 资产负债率
    TotalLiabilitiesToTotalAssets = 25, "allLiabAndAssets"
    # 经营现金流同比增长率; （T期CFO-T-1期CFO）/T-1期CFO *100%
    CashFromOps_yearOnYear_Ratio = 26, "cash4OpsYearOnYearRatio"
    # 净资产收益率ROE同比增长率  （T期ROE-T-1期ROE）/T-1期ROE *100%
    ROE_yearOnYear_Ratio = 27, "netIncomeYearOnYearRatio"


class FinancialField(FilterField):
    # 毛利率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    GrossProfitRate = 1, "grossMargin"
    # 净利率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    NetProfitRate = 2, "netIncomeMargin"
    # 扣非净利润率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    EarningsFromContOpsMargin = 3, "earningsFromContOpsMargin"
    # 总负债/股东权益 (单位：元)
    TotalDebtToEquity = 4, "totalDebtToEquity"
    # 长期负债/股东权益
    LongTermDebtToEquity = 5, "ltDebtToEquity"
    # EBIT/利息支出
    EbitToInterestExp = 6, "ebitToInterestExp"
    # 总负债/总资产
    TotalLiabilitiesToTotalAssets = 7, "totalLiabilitiesToTotalAssets"
    # 总资产周转率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    TotalAssetTurnover = 8, "totalAssetTurnover"
    # 应收帐款周转率
    AccountsReceivableTurnover = 9, "accountsReceivableTurnover"
    # 存货周转率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    InventoryTurnover = 10, "inventoryTurnover"
    # 流动比率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    CurrentRatio = 11, "currentRatio"
    # 速动比率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    QuickRatio = 12, "quickRatio"
    # 资产回报率 总资产收益率 *$ TTM（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    ROATTM = 13, "roa"
    # 净资产收益率 $（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    ReturnOnEquityRate = 14, "roe"
    # 营业收入一年增长率 或者 营收增长率
    TotalRevenues1YrGrowth = 15, "totalRevenues1YrGrowth"
    # 毛利润率一年增长率  营业利润增长率
    GrossProfit1YrGrowth = 16, "grossProfit1YrGrowth"
    # 净利润一年增长率
    NetIncome1YrGrowth = 17, "netIncome1YrGrowth"
    # 应收帐款一年增长率
    AccountsReceivable1YrGrowth = 18, "accountsReceivable1YrGrowth"
    # 存货一年增长率
    Inventory1YrGrowth = 19, "inventory1YrGrowth"
    # 总资产一年增长率
    TotalAssets1YrGrowth = 20, "totalAssets1YrGrowth"
    # 有形资产一年增长率
    TangibleBookValue1YrGrowth = 21, "tangibleBookValue1YrGrowth"
    # 经营现金流一年增长率
    CashFromOperations1YrGrowth = 22, "cashFromOperations1YrGrowth"
    # 资本开支一年增长率
    CapitalExpenditures1YrGrowth = 23, "capitalExpenditures1YrGrowth"
    # 营业收入三年增长率 或者叫 营收3年复合增长率
    TotalRevenues3YrCagr = 24, "totalRevenues3YrCagr"
    # 毛利润率三年增长率
    GrossProfit3YrCagr = 25, "grossProfit3YrCagr"
    # 净利润三年增长率
    NetIncome3YrCagr = 26, "netIncome3YrCagr"
    # 应收帐款三年增长率
    AccountsReceivable3YrCagr = 27, "accountsReceivable3YrCagr"
    # 存货三年增长率
    Inventory3YrCagr = 28, "inventory3YrCagr"
    # 总资产三年增长率
    TotalAssets3YrCagr = 29, "totalAssets3YrCagr"
    # 有形资产三年增长率
    TangibleBookValue3YrCagr = 30, "tangibleBookValue3YrCagr"
    # 经营现金流三年增长率
    CashFromOps3YrCagr = 31, "cashFromOps3YrCagr"
    # 资本开支三年增长率
    CapitalExpenditures3YrCagr = 32, "capitalExpenditures3YrCagr"
    # 净利润
    NetIncomeToCompany = 33, "netIncomeToCompany"
    # 经营现金流
    CashFromOperations = 34, "cashFromOps"
    # 投资现金流
    CashFromInvesting = 35, "cashFromInvesting"
    # 筹资现金流
    CashFromFinancing = 36, "cashFromFinancing"
    # 净利润2年复合增长率
    NormalizedNetIncome2YrCagr = 37, "normalizedNetIncome2YrCagr"
    # 营收2年复合增长率
    TotalRevenues2YrCagr = 38, "totalRevenues2YrCagr"
    # 净利润5年复合增长率
    NetIncome5YrCagr = 39, "netIncome5YrCagr"
    # 营收5年复合增长率
    TotalRevenues5YrCagr = 40, "totalRevenues5YrCagr"
    # 总资产
    TotalAssets = 41, "totalAssets"
    # 固定资产周转率（精确到小数点后 3 位，超出部分会被舍弃）例如填写 [0.005,0.01] 值区间
    FixedAssetTurnover = 42, "fixedAssetTurnover"
    # 营业利润
    OperatingIncome = 43, "operatingIncome"
    # 营业总收入
    TotalRevenue = 44, "totalRevenue"
    # 市盈率LYR PE =price-to-earnings ratio
    LYR_PE = 45, "LyrPE"
    # 市盈率TTM PE =price-to-earnings ratio
    TTM_PE = 46, "ttmPE"
    # 市销率LYR PS =Price-to-sales Ratio
    LYR_PS = 47, "LyrPS"
    # 市销率TTM PS =Price-to-sales Ratio
    TTM_PS = 48, "ttmPS"
    # 市净率LYR PB =price/book value ratio
    LYR_PB = 47, "LyrPB"
    # 市净率TTM PB =price/book value ratio
    TTM_PB = 48, "ttmPB"
    # 当日主力净流入额
    LargeInflowAmountToday = 49, "largeInflowAmountToday"
    # 当日主力增仓占比
    LargeInflowAmountTodayPre = 50, "largeInflowAmountTodayPre"
    # 未平仓做空量
    ShortInterest = 51, "shortInterest"
    # 未平仓做空比例
    ShortInterestPre = 52, "shortInterestPre"
    # 港股通持股比例=港股通(深)持股比例=港股通(沪)持股比例
    HK_StockConnectRate = 53, "hkStockConnectRate"
    # 沪股通持股比例
    SH_StockConnectRate = 54, "shStockConnectRate"
    # 深股通持股比例
    SZ_StockConnectRate = 55, "szStockConnectRate"
    # 营业利润占比
    Operating_Profits_Rate = 56, "operatingProfitsRate"
    # 港股通(沪)净买入额
    HK_StockShConnectInflow = 57, "hkStockShConnectInflow"
    # 港股通(深)净买入额
    HK_StockSzConnectInflow = 58, "hkStockSzConnectInflow"
    # 沪股通净买入额
    SH_StockConnectInflow = 59, "shStockConnectInflow"
    # 深股通净买入额
    SZ_StockConnectInflow = 60, "szStockConnectInflow"
    # 上市以来年化收益率 ETF
    ListingAnnualReturn = 61, "listingAnnualReturn"
    # 近1年年化收益率  ETF
    LstYearAnnualReturn = 62, "lstYearAnnualReturn"
    # 近2年年化收益率  ETF
    Lst2YearAnnualReturn = 63, "lst2YearAnnualReturn"
    # 近5年年化收益率  ETF
    Lst5YearAnnualReturn = 64, "lst5YearAnnualReturn"
    # 上市以来年化波动率  ETF
    ListingAnnualVolatility = 65, "listingAnnualVolatility"
    # 近1年年化波动率  ETF
    LstYearAnnualVolatility = 66, "lstYearAnnualVolatility"
    # 近2年年化波动率  ETF
    Lst2YearAnnualVolatility = 67, "lst2YearAnnualVolatility"
    # 近5年年化波动率  ETF
    Lst5YearAnnualVolatility = 68, "lst5YearAnnualVolatility"


class MultiTagField(FilterField):
    # 所属行业
    Industry = 1, "industry"
    # 所属概念
    Concept = 2, "concept"
    # 是否为otc股票.1=是，0=否
    isOTC = 3, "isOTC"
    StockCode = 4, "symbol"
    # 股票类型 stock or etf ;股票类型,非0表示该股票是ETF,1表示不带杠杆的etf,2表示2倍杠杆etf,3表示3倍etf杠杆,负值表示反向的ETF
    Type = 5, "type"
    # 成交量异常.1=是，0=否 ;当日实时成交量> 5* 最近一年的平均成交量
    Volume_Spike = 6, "volSpike"
    # 破净股票；市净率PB<1
    Net_Broken = 7, "netBroken"
    # 破发股票 ； 最新价<发行价
    Issue_Price_Broken = 8, "issuePriceBroken"
    # 跟踪指数/资产 - ETF
    PrimaryBenchmark = 9, "primaryBenchmark"
    # 发行人 - ETF
    Issuer = 10, "issuer"
    # 托管人 - ETF
    Custodian = 11, "custodian"
    # 分红频率 - ETF
    DistributionFrequency = 12, "distributionFrequency"
    # 是否支持期权 - ETF ; 1=是，0=否
    OptionsAvailable = 13, "optionsAvailable"
    # 今日创历史新高 - ETF 1=是，0=否
    Today_HistoryHigh = 14, "todayHistoryHigh"
    # 今日创历史新低 - ETF 1=是，0=否
    Today_HistoryLow = 15, "todayHistoryLow"
    # 股票包
    Stock_Package = 16, "StockPkg"
    # 52周最高 0 否 1是*
    Week52HighFlag = 17, "week52HighFlag"
    # 52周最低 0 否 1是
    Week52LowFlag = 18, "week52LowFlag"


class FieldBelongType(Enum):
    """选股排序字段对应的filter类别
    """
    def __new__(cls, field_type, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = field_type
        return obj

    def __init__(self, field_type, field_class):
        self.field_type = field_type
        self.field_class = field_class

    BASE = 'StockField', StockField
    ACCUMULATE = 'AccumulateField', AccumulateField
    FINANCIAL = 'FinancialField', FinancialField
    MULTI_TAG = 'MultiTagField', MultiTagField


class FinancialPeriod(Enum):
    LTM = 'LTM'


class AccumulatePeriod(Enum):
    def __new__(cls, index, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = index
        return obj

    def __init__(self, index, suffix, range):
        self.index = index
        self.suffix = suffix
        self.range = range

    # 近五分钟
    Five_Minutes = 0, "_5_min", "changeRate"
    # 近五天
    Five_Days = 1, "_5_days", "changeRate"
    # 近10日
    Ten_Days = 2, "_10_days", "changeRate"
    # 近20日
    Twenty_Days = 3, "_20_days", "changeRate"
    # 年初至今
    Beginning_Of_The_Year_To_Now = 4, "_1_year", "changeRate"
    # 近半年
    Half_Year = 5, "_half_year", "changeRate"
    # 近一年
    Last_Year = 6, "_last_year", "changeRate"
    # 近两年
    Last_Two_Year = 7, "_last_two_year", "changeRate"
    # 近五年
    Last_Five_Year = 8, "_last_five_year", "changeRate"
    # 上市至今
    Listing_Date_To_Now = 9, "_ListDateToNow", "changeRate"
    # 年度范围
    ANNUAL = 10, "_annu", "totalLiabilitiesRatio,totalCommonEquityRatio,basicEpsRatio,netIncomeRatio,opeIncomeratio,eps,bookValueshare,netIncome,operatingIncome,total_revenue,ROE,ROA,dividePrice,divideRate,grossMargin,netIncomeMargin,totalAssets,currentRatio,quickRatio,cash4Ops,cash4Invest,cash4Finance,allLiabAndAssets,cash4Ops,netIncomeYearOnYearRatio,cash4OpsYearOnYearRatio"
    # 一季度报
    QUARTERLY = 11, "_quart", "totalLiabilitiesRatio,totalCommonEquityRatio,basicEpsRatio,netIncomeRatio,opeIncomeratio,eps,bookValueshare,netIncome,operatingIncome,total_revenue,ROE,ROA,dividePrice,divideRate,grossMargin,netIncomeMargin,totalAssets,currentRatio,quickRatio,cash4Ops,cash4Invest,cash4Finance,allLiabAndAssets,cash4Ops,netIncomeYearOnYearRatio,cash4OpsYearOnYearRatio"
    # 三季度报
    QUARTERLY_Recent_Third = 12, "_3_ytd", "totalLiabilitiesRatio,totalCommonEquityRatio,basicEpsRatio,netIncomeRatio,opeIncomeratio,eps,bookValueshare,netIncome,operatingIncome,total_revenue,ROE,ROA,dividePrice,divideRate,grossMargin,netIncomeMargin,totalAssets,currentRatio,quickRatio,cash4Ops,cash4Invest,cash4Finance,allLiabAndAssets,cash4Ops,netIncomeYearOnYearRatio,cash4OpsYearOnYearRatio"
    # 中报
    SEMIANNUAL = 13, "_semiAnnu", "totalLiabilitiesRatio,totalCommonEquityRatio,basicEpsRatio,netIncomeRatio,opeIncomeratio,eps,bookValueshare,netIncome,operatingIncome,total_revenue,ROE,ROA,dividePrice,divideRate,grossMargin,netIncomeMargin,totalAssets,currentRatio,quickRatio,cash4Ops,cash4Invest,cash4Finance,allLiabAndAssets,cash4Ops,netIncomeYearOnYearRatio,cash4OpsYearOnYearRatio"
