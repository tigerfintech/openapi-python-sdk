# -*- coding: utf-8 -*-
# 
# @Date    : 2022/6/23
# @Author  : sukai

HK_QUOTE_LEVEL_PREFIX = "hk"
US_QUOTE_LEVEL_PREFIX = "us"

PART_CODE_NAME_MAP = {
    "a": "NYSE American, LLC (NYSE American)",
    "b": "NASDAQ OMX BX, Inc. (NASDAQ OMX BX)",
    "c": "NYSE National, Inc. (NYSE National)",
    "d": "FINRA Alternative Display Facility (ADF)",
    "h": "MIAX Pearl Exchange, LLC (MIAX)",
    "i": "International Securities Exchange, LLC (ISE)",
    "j": "Cboe EDGA Exchange, Inc. (Cboe EDGA)",
    "k": "Cboe EDGX Exchange, Inc. (Cboe EDGX)",
    "l": "Long-Term Stock Exchange, Inc. (LTSE)",
    "m": "NYSE Chicago, Inc. (NYSE Chicago)",
    "n": "New York Stock Exchange, LLC (NYSE)",
    "p": "NYSE Arca, Inc. (NYSE Arca)",
    "s": "Consolidated Tape System (CTS)",
    "t": "NASDAQ Stock Market, LLC (NASDAQ)",
    "u": "Members Exchange, LLC (MEMX)",
    "v": "Investors’ Exchange, LLC. (IEX)",
    "w": "CBOE Stock Exchange, Inc. (CBSX)",
    "x": "NASDAQ OMX PSX, Inc. (NASDAQ OMX PSX)",
    "y": "Cboe BYX Exchange, Inc. (Cboe BYX)",
    "z": "Cboe BZX Exchange, Inc. (Cboe BZX)",
}

PART_CODE_MAP = {
    "a": "AMEX",
    "b": "BX",
    "c": "NSX",
    "d": "ADF",
    "h": "MIAX",
    "i": "ISE",
    "j": "EDGA",
    "k": "EDGX",
    "l": "LTSE",
    "m": "CHO",
    "n": "NYSE",
    "p": "ARCA",
    "s": "CTS",
    "t": "NSDQ",
    "u": "MEMX",
    "v": "IEX",
    "w": "CBSX",
    "x": "PSX",
    "y": "BYX",
    "z": "BZX",
}

US_TRADE_COND_MAP = {
    " ": "US_REGULAR_SALE",  # 自动对盘
    "B": "US_BUNCHED_TRADE",  # 批量交易
    "C": "US_CASH_TRADE",  # 现金交易
    "F": "US_INTERMARKET_SWEEP",  # 跨市场交易
    "G": "US_BUNCHED_SOLD_TRADE",  # 批量卖出
    "H": "US_PRICE_VARIATION_TRADE",  # 离价交易
    "I": "US_ODD_LOT_TRADE",  # 碎股交易
    "K": "US_RULE_127_OR_155_TRADE",  # 纽交所 第127条交易 或 第155条交易
    "L": "US_SOLD_LAST",  # 延迟交易
    "M": "US_MARKET_CENTER_CLOSE_PRICE",  # 中央收市价
    "N": "US_NEXT_DAY_TRADE",  # 隔日交易
    "O": "US_MARKET_CENTER_OPENING_TRADE",  # 中央开盘价交易
    "P": "US_PRIOR_REFERENCE_PRICE",  # 前参考价
    "Q": "US_MARKET_CENTER_OPEN_PRICE",  # 中央开盘价
    "R": "US_SELLER",  # 卖方
    "T": "US_FORM_T",  # 盘前盘后交易
    "U": "US_EXTENDED_TRADING_HOURS",  # 延长交易时段
    "V": "US_CONTINGENT_TRADE",  # 合单交易
    "W": "US_AVERAGE_PRICE_TRADE",  # 均价交易
    "X": "US_CROSS_TRADE",  #
    "Z": "US_SOLD_OUT_OF_SEQUENCE",  # 场外售出
    "0": "US_ODD_LOST_CROSS_TRADE",  # 碎股跨市场交易
    "4": "US_DERIVATIVELY_PRICED",  # 衍生工具定价
    "5": "US_MARKET_CENTER_RE_OPENING_TRADE",  # 再开盘定价
    "6": "US_MARKET_CENTER_CLOSING_TRADE",  # 收盘定价
    "7": "US_QUALIFIED_CONTINGENT_TRADE",  # 合单交易
    "9": "US_CONSOLIDATED_LAST_PRICE_PER_LISTING_PACKET",  # 综合延迟价格
}

HK_TRADE_COND_MAP = {
    " ": "HK_AUTOMATCH_NORMAL",  # 自动对盘
    "D": "HK_ODD_LOT_TRADE",  # 碎股交易
    "U": "HK_AUCTION_TRADE",  # 竞价交易
    "*": "HK_OVERSEAS_TRADE",  # 场外交易
    "P": "HK_LATE_TRADE_OFF_EXCHG",  # 开市前成交
    "M": "HK_NON_DIRECT_OFF_EXCHG_TRADE",  # 非自动对盘
    "X": "HK_DIRECT_OFF_EXCHG_TRADE",  # 同券商自动对盘
    "Y": "HK_AUTOMATIC_INTERNALIZED",  # 同券商非自动对盘
}
