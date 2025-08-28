# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import logging
from typing import Optional, Union, List

from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.position import Position
from tigeropen.trade.domain.prime_account import PortfolioAccount

from tigeropen.common.consts import THREAD_LOCAL, SecurityType, Market, Currency, Language, OPEN_API_SERVICE_VERSION_V3, \
    SegmentType, OrderStatus, OrderSortBy
from tigeropen.common.consts.service_types import CONTRACTS, ACCOUNTS, POSITIONS, ASSETS, ORDERS, ORDER_NO, \
    CANCEL_ORDER, MODIFY_ORDER, PLACE_ORDER, ACTIVE_ORDERS, INACTIVE_ORDERS, FILLED_ORDERS, CONTRACT, PREVIEW_ORDER, \
    PRIME_ASSETS, ORDER_TRANSACTIONS, QUOTE_CONTRACT, ANALYTICS_ASSET, SEGMENT_FUND_AVAILABLE, SEGMENT_FUND_HISTORY, \
    TRANSFER_FUND, \
    TRANSFER_SEGMENT_FUND, CANCEL_SEGMENT_FUND, PLACE_FOREX_ORDER, ESTIMATE_TRADABLE_QUANTITY, AGGREGATE_ASSETS, \
    FUND_DETAILS
from tigeropen.common.exceptions import ApiException
from tigeropen.common.util.common_utils import get_enum_value, date_str_to_timestamp
from tigeropen.common.request import OpenApiRequest
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.tiger_open_config import LANGUAGE
from tigeropen.trade.domain.order import Order
from tigeropen.trade.request.model import ContractParams, AccountsParams, AssetParams, PositionParams, OrdersParams, \
    OrderParams, PlaceModifyOrderParams, CancelOrderParams, TransactionsParams, AnalyticsAssetParams, SegmentFundParams, \
    ForexTradeOrderParams, EstimateTradableQuantityModel, FundingHistoryParams, AggregateAssetParams, FundDetailsParams
from tigeropen.trade.response.account_profile_response import ProfilesResponse
from tigeropen.trade.response.aggregate_assets_response import AggregateAssetsResponse
from tigeropen.trade.response.analytics_asset_response import AnalyticsAssetResponse
from tigeropen.trade.response.assets_response import AssetsResponse
from tigeropen.trade.response.contracts_response import ContractsResponse
from tigeropen.trade.response.forex_order_response import ForexOrderResponse
from tigeropen.trade.response.fund_details_response import FundDetailsResponse
from tigeropen.trade.response.order_id_response import OrderIdResponse
from tigeropen.trade.response.order_preview_response import PreviewOrderResponse
from tigeropen.trade.response.orders_response import OrdersResponse
from tigeropen.trade.response.positions_response import PositionsResponse, EstimateTradableQuantityResponse
from tigeropen.trade.response.prime_assets_response import PrimeAssetsResponse
from tigeropen.trade.response.segment_fund_response import SegmentFundAvailableResponse, \
    SegmentFundHistoryResponse, SegmentFundCancelResponse
from tigeropen.trade.response.segment_fund_response import SegmentFundTransferResponse
from tigeropen.trade.response.transactions_response import TransactionsResponse
from tigeropen.trade.response.funding_history_response import FundingHistoryResponse


class TradeClient(TigerOpenClient):

    def __init__(self, client_config, logger=None):
        if not logger:
            logger = logging.getLogger('tiger_openapi')
        super(TradeClient, self).__init__(client_config, logger=logger)
        if client_config:
            self._account = client_config.account
            self._lang = client_config.language
            self._secret_key = client_config.secret_key
            self._timezone = client_config.timezone
        else:
            self._account = None
            self._lang = LANGUAGE
            self._secret_key = None
            self._timezone = None

    def get_managed_accounts(self, account=None, lang=None):
        """
        获取管理的账号列表
        :param account:
        :return: AccountProfile 对象, 有如下属性：
            account： 交易账户
            capability： 账户类型(CASH:现金账户, MGRN: Reg T 保证金账户, PMGRN: 投资组合保证金)
            status： 账户状态(New, Funded, Open, Pending, Abandoned, Rejected, Closed, Unknown)
        """
        params = AccountsParams()
        if account:
            params.account = account
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.secret_key = self._secret_key
        request = OpenApiRequest(ACCOUNTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ProfilesResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.profiles
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_contracts(self,
                      symbol,
                      sec_type=SecurityType.STK,
                      currency=None,
                      exchange=None,
                      lang=None):
        """
        批量获取合约
        :param symbol:
        :param sec_type: 合约类型 tigeropen.common.consts.SecurityType
        :param currency: 币种 tigeropen.common.consts.Currency
        :param exchange: 交易所
        :return: 合约对象列表, 每个列表项的对象信息同 get_contract 返回
        """
        params = ContractParams()
        params.account = self._account
        params.secret_key = self._secret_key
        params.symbols = symbol if isinstance(symbol, list) else [symbol]
        params.sec_type = get_enum_value(sec_type)
        params.currency = get_enum_value(currency)
        params.exchange = exchange
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(CONTRACTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ContractsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_contract(
            self,
            symbol: str,
            sec_type: Union[SecurityType, str] = SecurityType.STK,
            currency: Optional[Union[Currency, str]] = None,
            exchange: Optional[str] = None,
            expiry: Optional[str] = None,
            strike: Optional[float] = None,
            put_call: Optional[str] = None,
            lang: Optional[Union[Language,
                                 str]] = None) -> Optional['Contract']:
        """
        Get contract information. 获取合约信息

        :param symbol: Symbol/Ticker of the contract. 合约代码/股票代码
        :param sec_type: Security type. 合约类型. From tigeropen.common.consts.SecurityType (e.g., STK, OPT, FUT)
        :param currency: Currency. 币种. From tigeropen.common.consts.Currency (e.g., USD, HKD, CNH)
        :param exchange: Exchange. 交易所 (e.g., NASDAQ, SEHK, SSE)
        :param expiry: Expiry date for Pptions (format: yyyyMMdd). 期权合约到期日，格式：yyyyMMdd
        :param strike: Strike price for options. 期权行权价
        :param put_call: Option type (CALL/PUT). 期权类型（看涨/看跌）
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: Contract object with the following attributes:
                 Contract对象，具有以下属性：
            symbol: Symbol/ticker. 合约代码/股票代码
            identifier: Unique contract identifier. 合约唯一标识符
            currency: Currency. 币种
            exchange: Exchange. 交易所
            name: Contract name. 合约名称
            sec_type: Security type. 合约类型
            long_initial_margin: Initial margin ratio for long positions. 做多初始保证金比例
            long_maintenance_margin: Maintenance margin ratio for long positions. 做多维持保证金比例
            short_fee_rate: Fee rate for short positions. 做空费率
            short_margin: Margin for short positions. 做空保证金
            shortable: Whether can be shorted. 是否可做空
            shortable_count: Available shortable shares. 可做空股数
            multiplier: Contract multiplier. 合约乘数
            expiry: Contract expiry date (futures/options). 合约到期日(期货/期权)
            contract_month: Contract month (futures). 合约月份(期货)
            strike: Strike price (options). 行权价(期权)
            put_call: Put/Call type (options). 看跌/看涨(期权)
            market: Market. 市场
            primary_exchange: Primary exchange. 主要交易所
            tick_sizes: Tick size rules. 最小价格变动单位规则
            trading_class: Trading class. 交易类别
            status: Contract status. 合约状态
            marginable: Whether marginable. 是否可融资
            lot_size: Lot size. 最小交易单位
            support_overnight_trading: Whether overnight trading is supported. 是否支持隔夜交易
            support_fractional_share: Whether fractional shares are supported. 是否支持零股交易

        :return example:
        {'contract_id': 113, 'symbol': 'NVDA', 'currency': 'USD', 'sec_type': 'STK', 'exchange': None, 'origin_symbol': None, 'local_symbol': 'NVDA', 'expiry': None, 'strike': None, 'put_call': None, 'multiplier': 1.0, 'name': 'NVIDIA', 'short_margin': 0.35, 'short_initial_margin': 0.35, 'short_maintenance_margin': 0.3, 'short_fee_rate': 3.75, 'shortable': True, 'shortable_count': 38061067, 'long_initial_margin': 0.3, 'long_maintenance_margin': 0.25, 'contract_month': None, 'identifier': 'NVDA', 'primary_exchange': 'NASDAQ', 'market': 'US', 'min_tick': None, 'tick_sizes': [{'begin': '0', 'end': '1', 'type': 'CLOSED', 'tick_size': 0.0001}, {'begin': '1', 'end': 'Infinity', 'type': 'OPEN', 'tick_size': 0.01}], 'trading_class': 'NVDA', 'status': 1, 'marginable': True, 'trade': True, 'close_only': False, 'continuous': None, 'last_trading_date': None, 'first_notice_date': None, 'last_bidding_close_time': None, 'is_etf': False, 'etf_leverage': None, 'discounted_day_initial_margin': None, 'discounted_day_maintenance_margin': None, 'discounted_time_zone_code': None, 'discounted_start_at': None, 'discounted_end_at': None, 'categories': None, 'lot_size': 1.0, 'support_overnight_trading': True, 'support_fractional_share': True}
        """
        params = ContractParams()
        params.account = self._account
        params.secret_key = self._secret_key
        params.symbol = symbol
        params.sec_type = get_enum_value(sec_type)
        params.currency = get_enum_value(currency)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.version = OPEN_API_SERVICE_VERSION_V3
        if expiry:
            params.expiry = expiry
        if strike:
            params.strike = strike
        if put_call:
            params.right = put_call
        params.exchange = exchange

        request = OpenApiRequest(CONTRACT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ContractsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts[0] if len(
                    response.contracts) == 1 else None
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_derivative_contracts(self, symbol, sec_type, expiry, lang=None):
        """

        :param symbol:
        :param sec_type: type of contract. tigeropen.common.consts.SecurityType. support: OPTION, WAR, IOPT
        :param expiry: expiry date string, like '20220929'
        :param lang:
        :return: list of Contract
        """
        params = ContractParams()
        params.symbols = symbol if isinstance(symbol, list) else [symbol]
        params.sec_type = get_enum_value(sec_type)
        params.expiry = expiry
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(QUOTE_CONTRACT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ContractsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_positions(
        self,
        account: Optional[str] = None,
        sec_type: Union[SecurityType, str] = SecurityType.STK,
        currency: Union[Currency, str] = Currency.ALL,
        market: Union[Market, str] = Market.ALL,
        symbol: Optional[str] = None,
        sub_accounts: Optional[List[str]] = None,
        expiry: Optional[str] = None,
        strike: Optional[str] = None,
        put_call: Optional[str] = None,
        asset_quote_type: Optional[str] = None,
        lang: Optional[Union[Language,
                             str]] = None) -> Optional[List['Position']]:
        """
        Get portfolio position data. 获取持仓数据

        :param account: Account ID. 账户ID
        :param sec_type: Security type. 证券类型. From tigeropen.common.consts.SecurityType (e.g., STK, OPT, FUT)
        :param currency: Currency filter. 币种筛选. From tigeropen.common.consts.Currency
        :param market: Market filter. 市场筛选. From tigeropen.common.consts.Market
        :param symbol: Symbol to filter positions. 按证券代码筛选持仓
        :param sub_accounts: List of sub-accounts. 子账户列表
        :param expiry: Option/future expiry date (format: yyyyMMdd). 期权/期货到期日（格式：yyyyMMdd）
        :param strike: Option strike price. 期权行权价
        :param put_call: Option type (PUT/CALL). 期权类型（看跌/看涨）
        :param asset_quote_type: Asset quote mode. 资产行情模式
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: List of Position objects. Each Position object has the following attributes:
                Position对象构成的列表。每个Position对象具有以下属性：
            account: Account ID. 所属账户ID
            contract: Contract object. 合约对象
            quantity: Position quantity. 持仓数量
            average_cost: Position cost. 持仓成本
            average_cost_by_average: Average cost (by average). 平均持仓成本
            average_cost_of_carry: Average cost of carry. 移仓平均成本
            market_price: Latest price. 最新价格
            market_value: Market value. 市值
            realized_pnl: Realized P&L. 已实现盈亏
            realized_pnl_by_average: Realized P&L (by average). 已实现盈亏(平均)
            unrealized_pnl: Unrealized P&L. 未实现盈亏
            unrealized_pnl_by_average: Unrealized P&L (by average). 未实现盈亏(平均)
            position_scale: Position scale. 仓位比例
            unrealized_pnl_percent: Unrealized P&L percent. 未实现盈亏百分比
            unrealized_pnl_percent_by_average: Unrealized P&L percent (by average). 未实现盈亏百分比(平均)
            mm_value: Maintenance margin value. 维持保证金价值
            mm_percent: Maintenance margin percent. 维持保证金百分比
            position_qty: Position quantity (decimal). 持仓数量(小数)
            salable_qty: Salable quantity. 可卖数量
            today_pnl: Today's P&L. 今日盈亏
            today_pnl_percent: Today's P&L percent. 今日盈亏百分比
            last_close_price: Previous close price. 昨日收盘价

        :return example:
        [Position({'account': '123123', 'contract': NVDA/STK/USD, 'quantity': 773, 'average_cost': 129.45, 'average_cost_by_average': 129.45, 'average_cost_of_carry': 129.45, 'market_price': 183.52, 'market_value': 1.4186, 'realized_pnl': 0.0, 'realized_pnl_by_average': 0.0, 'unrealized_pnl': 0.42, 'unrealized_pnl_by_average': 0.42, 'position_scale': 5, 'unrealized_pnl_percent': 0.4177, 'unrealized_pnl_percent_by_average': 0.4177, 'mm_value': 0.3547, 'mm_percent': 0.0, 'position_qty': 0.00773, 'salable_qty': 0.00773, 'salable': 0.00773, 'saleable': 0.00773, 'today_pnl': 0.0, 'today_pnl_percent': 0.002, 'yesterday_pnl': None, 'last_close_price': 183.16, 'unrealized_pnl_by_cost_of_carry': 0.42, 'unrealized_pnl_percent_by_cost_of_carry': 0.4177, 'is_level0_price': None}),
         Position({'account': '123123', 'contract': ROSGQ/STK/USD, 'quantity': 6, 'average_cost': 1.1932, 'average_cost_by_average': 1.1932, 'average_cost_of_carry': 1.1932, 'market_price': 0.0001, 'market_value': 0.0006, 'realized_pnl': 0.0, 'realized_pnl_by_average': 0.0, 'unrealized_pnl': -7.16, 'unrealized_pnl_by_average': -7.16, 'position_scale': 0, 'unrealized_pnl_percent': -0.9999, 'unrealized_pnl_percent_by_average': -0.9999, 'mm_value': 0.0006, 'mm_percent': 0.0, 'position_qty': 6.0, 'salable_qty': 6.0, 'salable': 6.0, 'saleable': 6.0, 'today_pnl': 0.0, 'today_pnl_percent': 0.0, 'yesterday_pnl': None, 'last_close_price': 0.0001, 'unrealized_pnl_by_cost_of_carry': -7.16, 'unrealized_pnl_percent_by_cost_of_carry': -0.9999, 'is_level0_price': None})]
        """
        params = PositionParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.sub_accounts = sub_accounts
        params.currency = get_enum_value(currency)
        params.market = get_enum_value(market)
        params.symbol = symbol
        if expiry:
            params.expiry = expiry
        if strike:
            params.strike = strike
        if put_call:
            params.right = put_call
        if asset_quote_type:
            params.asset_quote_type = get_enum_value(asset_quote_type)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(POSITIONS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = PositionsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.positions
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_assets(self,
                   account=None,
                   sub_accounts=None,
                   segment=False,
                   market_value=False):
        """
        获取账户资产信息
        :param account:
        :param sub_accounts: 子账户列表
        :param segment: 是否包含证券/期货分类
        :param market_value: 是否包含分市场市值
        :return: 由 PortfolioAccount 对象构成的列表. PortfolioAccount 对象下的 summary 属性包含一个 Account 对象，
         Account 对象有如下属性：
            net_liquidation: 净清算值
            accrued_cash: 净累计利息
            accrued_dividend: 净累计分红
            available_funds: 可用资金(可用于交易)
            accrued_interest: 累计利息
            buying_power: 购买力
            cash: 证券账户金额+期货账户金额
            currency: 货币
            cushion: 当前保证金缓存
            day_trades_remaining: 剩余日内交易次数，-1表示无限制
            equity_with_loan: 含借贷值股权
            excess_liquidity: 当前结余流动性，为保持当前拥有的头寸，必须维持的缓冲保证金的数额，日内风险数值（App）
            gross_position_value: 持仓市值
            initial_margin_requirement: 初始保证金要求
            maintenance_margin_requirement: 维持保证金要求
            regt_equity: RegT 资产
            regt_margin: RegT 保证金
            sma: 特殊备忘录账户，隔夜风险数值（App）
            settled_cash: 结算利息
            leverage: 总杠杆
            net_leverage: 净杠杆
        """
        params = AssetParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sub_accounts = sub_accounts
        params.segment = segment
        params.market_value = market_value
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(ASSETS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = AssetsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.assets
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_prime_assets(
        self,
        account: Optional[str] = None,
        base_currency: Optional[Union[Currency, str]] = None,
        consolidated: bool = True,
        lang: Optional[Union[Language, str]] = None
    ) -> Optional['PortfolioAccount']:
        """
        Get prime account assets. 获取 Prime 账户资产信息
        
        :param account: Account ID. 账户ID
        :param base_currency: Base currency for asset calculation. 资产计算的基础货币.
                            From tigeropen.common.consts.Currency, like Currency.USD
        :param consolidated: Whether to consolidate assets. 是否合并资产
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: PortfolioAccount object with the following structure:
                PortfolioAccount 对象，包含以下结构：
            account: Account ID. 账户ID
            update_timestamp: Asset update timestamp. 资产更新时间戳
            segments: Dictionary of Segment objects keyed by category. 按类别分类的 Segment 对象字典：
                'S': Stock segment. 股票分部
                'C': Commodity futures segment. 商品期货分部
                'F': Financial futures segment.
            
            Each Segment object contains:
            每个 Segment 对象包含：
                currency: Currency. 货币
                capability: Account capability. 账户能力
                category: Segment category. 分部类别
                cash_balance: Cash balance. 现金余额
                cash_available_for_trade: Cash available for trading. 可用于交易的现金
                gross_position_value: Gross position value. 总持仓价值
                equity_with_loan: Equity with loan. 含借贷值的资产
                net_liquidation: Net liquidation value. 净清算价值
                init_margin: Initial margin. 初始保证金
                maintain_margin: Maintenance margin. 维持保证金
                buying_power: Buying power. 购买力
                leverage: Leverage. 杠杆
                currency_assets: Dictionary of CurrencyAsset objects by currency. 按货币分类的 CurrencyAsset 对象字典
                
            Each CurrencyAsset object contains:
            每个 CurrencyAsset 对象包含：
                currency: Currency. 货币
                cash_balance: Cash balance. 现金余额
                cash_available_for_trade: Cash available for trading. 可用于交易的现金
                
        :return example:
        PortfolioAccount({'account': '123123', 'update_timestamp': 1755078296228, 'segments': {'S': Segment({'currency': 'USD', 'capability': 'RegTMargin', 'category': 'S', 'cash_balance': 7198.59, 'cash_available_for_trade': 5717.69, 'cash_available_for_withdrawal': inf, 'gross_position_value': -250.58, 'equity_with_loan': 7200.0, 'net_liquidation': 6948.0, 'init_margin': 500.42, 'maintain_margin': 500.35, 'overnight_margin': 500.35, 'unrealized_pl': 5.85, 'realized_pl': 0.0, 'excess_liquidation': 6699.65, 'overnight_liquidation': 6699.65, 'buying_power': 22870.76, 'leverage': 0.08, 'consolidated_seg_types': ['SEC', 'FUND'], 'locked_funds': 981.89, 'uncollected': 0.0, 'unrealized_plby_cost_of_carry': 5.85, 'total_today_pl': 0.0, 'currency_assets': {'USD': CurrencyAsset({'currency': 'USD', 'cash_balance': 6302.06, 'cash_available_for_trade': 5320.17, 'gross_position_value': inf, 'stock_market_value': inf, 'futures_market_value': inf, 'option_market_value': inf, 'unrealized_pl': inf, 'realized_pl': inf}), 'HKD': CurrencyAsset({'currency': 'HKD', 'cash_balance': 5800.29, 'cash_available_for_trade': 5800.29, 'gross_position_value': inf, 'stock_market_value': inf, 'futures_market_value': inf, 'option_market_value': inf, 'unrealized_pl': inf, 'realized_pl': inf})}})}})
        """
        params = AssetParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.base_currency = get_enum_value(base_currency)
        params.consolidated = consolidated

        request = OpenApiRequest(PRIME_ASSETS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = PrimeAssetsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.assets
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_aggregate_assets(self,
                             account=None,
                             seg_type=SegmentType.SEC,
                             base_currency=None):
        params = AggregateAssetParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.lang = get_enum_value(self._lang)
        params.base_currency = get_enum_value(base_currency)
        params.seg_type = get_enum_value(seg_type)
        request = OpenApiRequest(AGGREGATE_ASSETS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = AggregateAssetsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def get_orders(
            self,
            account: Optional[str] = None,
            sec_type: Optional[Union[SecurityType, str]] = None,
            market: Union[Market, str] = Market.ALL,
            symbol: Optional[str] = None,
            start_time: Optional[Union[int, str]] = None,
            end_time: Optional[Union[int, str]] = None,
            limit: int = 100,
            is_brief: bool = False,
            states: Optional[List[Union[OrderStatus, str]]] = None,
            sort_by: Optional[Union['OrderSortBy', str]] = None,
            seg_type: Optional[Union[SegmentType, str]] = None,
            lang: Optional[Union[Language, str]] = None,
            page_token: Optional[str] = None) -> Optional[List['Order']]:
        """
        Get order list. 获取订单列表
        
        :param account: Account ID. 账户ID
        :param sec_type: Security type. 证券类型. From tigeropen.common.consts.SecurityType
        :param market: Market filter. 市场筛选. From tigeropen.common.consts.Market
        :param symbol: Symbol to filter orders. 按证券代码筛选订单
        :param start_time: Start time (inclusive). 开始时间(闭区间，包含). 
                          Either timestamp in milliseconds (13-digit integer) or date string (e.g., "2017-01-01", "2017-01-01 12:00:00")
                          可以是毫秒时间戳(13位整数)或日期字符串(如"2017-01-01"和"2017-01-01 12:00:00")
        :param end_time: End time (exclusive). 截止时间(开区间，不包含). Format same as start_time. 格式同 start_time
        :param limit: Maximum number of orders to return. 每次获取订单的最大数量
        :param is_brief: Whether to return simplified order data. 是否返回精简的订单数据
        :param states: List of order status enums for filtering. 订单状态枚举对象列表，用于筛选.
                      From tigeropen.common.consts.OrderStatus
        :param sort_by: Field used for sorting and filtering. 用于排序和筛选的字段.
                      From tigeropen.common.consts.OrderSortBy (e.g., LATEST_CREATED or LATEST_STATUS_UPDATED)
        :param seg_type: Segment type. 分部类型. From tigeropen.common.consts.SegmentType
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :param page_token: Token for pagination. 分页令牌
        :return: List of Order objects. Each Order object has attributes such as:
                 Order对象列表，每个Order对象具有以下属性：
            account: Account ID. 账户ID
            id: Global order ID. 全局订单ID
            order_id: Account-specific order ID. 账户特定订单ID
            symbol: Symbol/ticker. 证券代码
            action: Order action (BUY/SELL). 交易动作(买/卖)
            order_type: Order type (e.g., LMT, MKT). 订单类型(如限价、市价等)
            status: Order status. 订单状态
            quantity: Order quantity. 订单数量
            filled: Filled quantity. 已成交数量
            remaining: Remaining quantity. 剩余数量
            limit_price: Limit price. 限价
            aux_price: Auxiliary price. 辅助价格
            avg_fill_price: Average fill price. 平均成交价格
            commission: Commission cost. 佣金
            time_in_force: Order time in force (e.g., DAY, GTC). 订单有效期(如当日有效、撤销前有效)
            outside_rth: Whether order can be executed outside regular trading hours. 是否允许盘前盘后交易
            order_time: Order creation timestamp. 订单创建时间戳
            update_time: Order last update timestamp. 订单最后更新时间戳
            trade_time: Trade execution timestamp. 成交时间戳
            contract: Contract object. 合约对象
            contract_legs: List of contract legs for multi-leg orders. 组合订单的合约腿列表

        :return example:
        [Order({'account': '123123', 'id': 40130901147389952, 'order_id': 0, 'parent_id': None, 'order_time': 1755073677000, 'reason': None, 'trade_time': 1755073700000, 'action': 'BUY', 'quantity': 5000, 'filled': 0, 'avg_fill_price': 0.0, 'commission': 0.0, 'realized_pnl': 0.0, 'trail_stop_price': None, 'limit_price': 0.023, 'aux_price': None, 'trailing_percent': None, 'percent_offset': None, 'order_type': 'LMT', 'time_in_force': 'DAY', 'outside_rth': False, 'order_legs': None, 'algo_params': None, 'algo_strategy': 'LMT', 'secret_key': '', 'liquidation': False, 'discount': 0, 'attr_desc': None, 'source': 'iOS', 'adjust_limit': None, 'sub_ids': None, 'user_mark': '', 'update_time': 1755073700000, 'expire_time': None, 'can_modify': False, 'external_id': '1755073615.997798', 'combo_type': None, 'combo_type_desc': None, 'is_open': True, 'contract_legs': None, 'filled_scale': 0, 'total_cash_amount': None, 'filled_cash_amount': 0.0, 'refund_cash_amount': None, 'attr_list': [], 'latest_price': None, 'orders': None, 'gst': 0.0, 'quantity_scale': 0, 'trading_session_type': 'RTH', 'charges': None, 'contract': 61486/IOPT/HKD, 'status': 'CANCELLED', 'remaining': 5000}),
        Order({'account': '123123', 'id': 40130857465156608, 'order_id': 0, 'parent_id': None, 'order_time': 1755073344000, 'reason': None, 'trade_time': 1755073361000, 'action': 'BUY', 'quantity': 1, 'filled': 0, 'avg_fill_price': 0.0, 'commission': 0.0, 'realized_pnl': 0.0, 'trail_stop_price': None, 'limit_price': -2.52, 'aux_price': None, 'trailing_percent': None, 'percent_offset': None, 'order_type': 'LMT', 'time_in_force': 'DAY', 'outside_rth': False, 'order_legs': None, 'algo_params': None, 'algo_strategy': 'LMT', 'secret_key': '', 'liquidation': False, 'discount': 0, 'attr_desc': None, 'source': 'iOS', 'adjust_limit': None, 'sub_ids': None, 'user_mark': '', 'update_time': 1755073361000, 'expire_time': None, 'can_modify': False, 'external_id': '1755073339.428326', 'combo_type': 'VERTICAL', 'combo_type_desc': 'Vertical', 'is_open': True, 'contract_legs': [{'symbol': 'AAPL', 'sec_type': 'OPT', 'expiry': '20250815', 'strike': '227.5', 'put_call': 'PUT', 'action': 'BUY', 'ratio': 1, 'market': 'US', 'currency': 'USD', 'multiplier': 100, 'total_quantity': 1.0, 'filled_quantity': 0.0, 'avg_filled_price': 0.0, 'created_at': 1755073344483, 'updated_at': 1755073344483}, {'symbol': 'AAPL', 'sec_type': 'OPT', 'expiry': '20250815', 'strike': '232.5', 'put_call': 'PUT', 'action': 'SELL', 'ratio': 1, 'market': 'US', 'currency': 'USD', 'multiplier': 100, 'total_quantity': 1.0, 'filled_quantity': 0.0, 'avg_filled_price': 0.0, 'created_at': 1755073344482, 'updated_at': 1755073344482}], 'filled_scale': 0, 'total_cash_amount': None, 'filled_cash_amount': 0.0, 'refund_cash_amount': None, 'attr_list': [], 'latest_price': None, 'orders': None, 'gst': 0.0, 'quantity_scale': 0, 'trading_session_type': 'RTH', 'charges': None, 'contract': AAPL/MLEG/USD, 'status': 'CANCELLED', 'remaining': 1})]
        """
        params = OrdersParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.market = get_enum_value(market)
        params.symbol = symbol
        params.start_date = date_str_to_timestamp(start_time, self._timezone)
        params.end_date = date_str_to_timestamp(end_time, self._timezone)
        params.limit = limit
        params.is_brief = is_brief
        params.states = [get_enum_value(state)
                         for state in states] if states else None
        params.sort_by = get_enum_value(sort_by)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.seg_type = get_enum_value(seg_type)
        params.page_token = page_token
        request = OpenApiRequest(ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content,
                                            secret_key=params.secret_key)
            if response.is_success():
                if page_token is not None:
                    return response
                else:
                    return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_open_orders(self,
                        account=None,
                        sec_type=None,
                        market=Market.ALL,
                        symbol=None,
                        start_time=None,
                        end_time=None,
                        parent_id=None,
                        sort_by=None,
                        seg_type=None,
                        lang=None,
                        **kwargs):
        """
        获取待成交订单列表. 参数同 get_orders
        :param parent_id: 主订单 order_id
        """
        params = OrdersParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.market = get_enum_value(market)
        params.symbol = symbol
        params.start_date = date_str_to_timestamp(start_time, self._timezone)
        params.end_date = date_str_to_timestamp(end_time, self._timezone)
        params.parent_id = parent_id
        params.sort_by = get_enum_value(sort_by)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.seg_type = get_enum_value(seg_type)
        if kwargs:
            for key, value in kwargs.items():
                setattr(params, key, value)
        request = OpenApiRequest(ACTIVE_ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content,
                                            secret_key=params.secret_key)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_cancelled_orders(self,
                             account=None,
                             sec_type=None,
                             market=Market.ALL,
                             symbol=None,
                             start_time=None,
                             end_time=None,
                             sort_by=None,
                             seg_type=None,
                             lang=None,
                             **kwargs):
        """
        获取已撤销订单列表. 参数同 get_orders
        """
        params = OrdersParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.market = get_enum_value(market)
        params.symbol = symbol
        params.start_date = date_str_to_timestamp(start_time, self._timezone)
        params.end_date = date_str_to_timestamp(end_time, self._timezone)
        params.sort_by = get_enum_value(sort_by)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.seg_type = get_enum_value(seg_type)
        if kwargs:
            for key, value in kwargs.items():
                setattr(params, key, value)
        request = OpenApiRequest(INACTIVE_ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content,
                                            secret_key=params.secret_key)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_filled_orders(self,
                          account=None,
                          sec_type=None,
                          market=Market.ALL,
                          symbol=None,
                          start_time=None,
                          end_time=None,
                          sort_by=None,
                          seg_type=None,
                          lang=None,
                          **kwargs):
        """
        获取已成交订单列表. 参数同 get_orders
        """
        params = OrdersParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.market = get_enum_value(market)
        params.symbol = symbol
        params.start_date = date_str_to_timestamp(start_time, self._timezone)
        params.end_date = date_str_to_timestamp(end_time, self._timezone)
        params.sort_by = get_enum_value(sort_by)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.seg_type = get_enum_value(seg_type)
        if kwargs:
            for key, value in kwargs.items():
                setattr(params, key, value)
        request = OpenApiRequest(FILLED_ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content,
                                            secret_key=params.secret_key)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_order(self,
                  account: Optional[str] = None,
                  id: Optional[int] = None,
                  order_id: Optional[int] = None,
                  is_brief: bool = False,
                  show_charges: Optional[bool] = None,
                  lang: Optional[Union[Language, str]] = None) -> Optional['Order']:
        """
        Get a specific order by ID. 获取指定订单信息
        
        :param account: Account ID. If not provided, the default account is used. 账户ID，如果不提供则使用默认账户
        :param id: Global order ID. 全局订单ID
        :param order_id: Account-specific order ID. 账户特定订单ID
        :param is_brief: Whether to return simplified order data. 是否返回精简的订单数据
        :param show_charges: Whether to include order charges information. 是否包含订单费用信息
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: Order object with the following attributes:
                 Order对象，具有以下属性：
            account: Account ID. 账户ID
            id: Global order ID. 全局订单ID
            order_id: Account-specific order ID. 账户特定订单ID
            symbol: Symbol/ticker. 证券代码
            action: Order action (BUY/SELL). 交易动作(买/卖)
            order_type: Order type (e.g., LMT, MKT). 订单类型(如限价、市价等)
            status: Order status. 订单状态
            quantity: Order quantity. 订单数量
            filled: Filled quantity. 已成交数量
            remaining: Remaining quantity. 剩余数量
            limit_price: Limit price. 限价
            aux_price: Auxiliary price. 辅助价格
            avg_fill_price: Average fill price. 平均成交价格
            commission: Commission cost. 佣金
            time_in_force: Order time in force (e.g., DAY, GTC). 订单有效期(如当日有效、撤销前有效)
            outside_rth: Whether order can be executed outside regular trading hours. 是否允许盘前盘后交易
            order_time: Order creation timestamp. 订单创建时间戳
            update_time: Order last update timestamp. 订单最后更新时间戳
            trade_time: Trade execution timestamp. 成交时间戳
            contract: Contract object. 合约对象
            contract_legs: List of contract legs for multi-leg orders. 组合订单的合约腿列表
        
        :return example:
        {'account': '123123', 'id': 40130857465156608, 'order_id': 0, 'parent_id': None, 'order_time': 1755073344000,
         'reason': None, 'trade_time': 1755073361000, 'action': 'BUY', 'quantity': 1, 'filled': 0, 'avg_fill_price': 0.0,
         'commission': 0.0, 'realized_pnl': 0.0, 'trail_stop_price': None, 'limit_price': -2.52, 'aux_price': None,
         'trailing_percent': None, 'percent_offset': None, 'order_type': 'LMT', 'time_in_force': 'DAY',
         'outside_rth': False, 'order_legs': None, 'algo_params': None, 'algo_strategy': 'LMT', 'secret_key': '',
         'liquidation': False, 'discount': 0, 'attr_desc': None, 'source': 'iOS', 'adjust_limit': None,
         'sub_ids': None, 'user_mark': '', 'update_time': 1755073361000, 'expire_time': None, 'can_modify': False,
         'external_id': '1755073339.428326', 'combo_type': 'VERTICAL', 'combo_type_desc': 'Vertical',
         'is_open': True, 'contract_legs': [{'symbol': 'AAPL', 'sec_type': 'OPT', 'expiry': '20250815',
         'strike': '227.5', 'put_call': 'PUT', 'action': 'BUY', 'ratio': 1, 'market': 'US', 'currency': 'USD', 
         'multiplier': 100, 'total_quantity': 1.0, 'filled_quantity': 0.0, 'avg_filled_price': 0.0, 
         'created_at': 1755073344483, 'updated_at': 1755073344483}, {'symbol': 'AAPL', 'sec_type': 'OPT', 
         'expiry': '20250815', 'strike': '232.5', 'put_call': 'PUT', 'action': 'SELL', 'ratio': 1, 'market': 'US', 
         'currency': 'USD', 'multiplier': 100, 'total_quantity': 1.0, 'filled_quantity': 0.0, 'avg_filled_price': 0.0, 
         'created_at': 1755073344482, 'updated_at': 1755073344482}], 'filled_scale': 0, 'total_cash_amount': None, 
         'filled_cash_amount': 0.0, 'refund_cash_amount': None, 'attr_list': [], 'latest_price': None, 
         'orders': None, 'gst': 0.0, 'quantity_scale': 0, 'trading_session_type': 'RTH', 'charges': None, 
         'contract': AAPL/MLEG/USD, 'status': 'CANCELLED', 'remaining': 1}
        """
        params = OrderParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.id = id
        params.order_id = order_id
        params.is_brief = is_brief
        params.show_charges = show_charges
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content,
                                            secret_key=params.secret_key)
            if response.is_success():
                return response.result[0] if len(
                    response.result) == 1 else None
            else:
                raise ApiException(response.code, response.message)
        return None

    def create_order(self,
                     account,
                     contract,
                     action,
                     order_type,
                     quantity,
                     limit_price=None,
                     aux_price=None,
                     trail_stop_price=None,
                     trailing_percent=None,
                     percent_offset=None,
                     time_in_force=None,
                     outside_rth=None,
                     order_legs=None,
                     algo_params=None,
                     lang=None,
                     **kwargs):
        """
        创建订单对象.
        :param account:
        :param contract:
        :param action:
        :param order_type:
        :param quantity:
        :param limit_price: 限价
        :param aux_price: 在止损单表示止损价格; 在跟踪止损单表示价差
        :param trail_stop_price: 跟踪止损单--触发止损单的价格
        :param trailing_percent: 跟踪止损单--百分比
        :param percent_offset:
        :param time_in_force: 订单有效期， 'DAY'（当日有效）和'GTC'（取消前有效)
        :param outside_rth: 是否允许盘前盘后交易(美股专属)
        :param order_legs: 附加订单
        :param algo_params: 算法订单参数
        """
        params = AccountsParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(ORDER_NO, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                order_id = response.order_id
                order = Order(account,
                              contract,
                              action,
                              order_type,
                              quantity,
                              limit_price=limit_price,
                              aux_price=aux_price,
                              trail_stop_price=trail_stop_price,
                              trailing_percent=trailing_percent,
                              percent_offset=percent_offset,
                              time_in_force=time_in_force,
                              outside_rth=outside_rth,
                              order_id=order_id,
                              order_legs=order_legs,
                              algo_params=algo_params,
                              secret_key=params.secret_key,
                              **kwargs)
                return order
            else:
                raise ApiException(response.code, response.message)

        return None

    def preview_order(self, order, lang=None):
        """
        预览订单
        :param order:  Order 对象
        :return: dict. 字段如下
            init_margin_before      下单前账户初始保证金
            init_margin             预计下单后的账户初始保证金
            maint_margin_before     下单前账户的维持保证金
            maint_margin            预计下单后的账户维持保证金
            margin_currency         保证金货币币种
            equity_with_loan_before 下单前账户的含借贷值股权(含贷款价值资产)
            equity_with_loan        下单后账户的含借贷值股权(含贷款价值资产)
            min_commission          预期最低佣金
            max_commission          预期最高佣金
            commission_currency     佣金货币币种

            若无法下单, 返回的 dict 中仅有如下字段:
            warning_text            无法下单的原因
        """
        params = PlaceModifyOrderParams()
        params.account = order.account
        params.contract = order.contract
        params.action = order.action
        params.order_type = order.order_type
        params.order_id = order.order_id
        params.quantity = order.quantity
        params.quantity_scale = order.quantity_scale
        params.limit_price = order.limit_price
        params.aux_price = order.aux_price
        params.trail_stop_price = order.trail_stop_price
        params.trailing_percent = order.trailing_percent
        params.percent_offset = order.percent_offset
        params.time_in_force = order.time_in_force
        params.outside_rth = order.outside_rth
        params.order_legs = order.order_legs
        params.algo_params = order.algo_params
        params.secret_key = order.secret_key if order.secret_key else self._secret_key
        params.adjust_limit = order.adjust_limit
        params.user_mark = order.user_mark
        params.expire_time = order.expire_time
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.combo_type = get_enum_value(order.combo_type)
        params.contract_legs = order.contract_legs
        params.total_cash_amount = order.total_cash_amount
        params.trading_session_type = get_enum_value(
            order.trading_session_type)

        request = OpenApiRequest(PREVIEW_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = PreviewOrderResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.preview_order
            else:
                raise ApiException(response.code, response.message)

    def place_order(
            self,
            order: 'Order',
            lang: Optional[Union[Language, str]] = None) -> Optional[int]:
        """
        Place an order to the market. 向市场提交订单

        :param order: Order object with details of the order to be placed. 包含订单详细信息的Order对象
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :return: Global order ID if successful. 如果成功，返回全局订单ID
        
        The order parameter should be an Order object containing the following essential attributes:
        订单参数应该是一个包含以下必要属性的Order对象：
            account: Account ID. 账户ID
            contract: Contract object. 合约对象
            action: Order action (BUY/SELL). 交易动作(买/卖)
            order_type: Order type (e.g., LMT, MKT). 订单类型(如限价、市价等)
            quantity: Order quantity. 订单数量
            
        Optional order attributes include:
        可选的订单属性包括：
            limit_price: Limit price for limit orders. 限价订单的限价
            aux_price: Stop price for stop orders or price offset for trailing stop orders. 止损单的触发价格或跟踪止损单的价差
            trail_stop_price: Activation price for trailing stop orders. 跟踪止损单的激活价格
            trailing_percent: Trailing percentage for trailing stop orders. 跟踪止损单的百分比
            time_in_force: Order time in force (e.g., DAY, GTC). 订单有效期(如当日有效、撤销前有效)
            outside_rth: Whether order can be executed outside regular trading hours. 是否允许盘前盘后交易

        :return: Order ID. The order argument will be updated with place order parameters, and the `id`, `sub_ids`, `orders`.
                order 参数对象，除了下单的各个属性会填充外，还将更新 `id`, `sub_ids`, `orders` 等相关信息。
        """
        params = PlaceModifyOrderParams()
        params.account = order.account
        params.contract = order.contract
        params.action = order.action
        params.order_type = order.order_type
        params.order_id = order.order_id
        params.quantity = order.quantity
        params.quantity_scale = order.quantity_scale
        params.limit_price = order.limit_price
        params.aux_price = order.aux_price
        params.trail_stop_price = order.trail_stop_price
        params.trailing_percent = order.trailing_percent
        params.percent_offset = order.percent_offset
        params.time_in_force = order.time_in_force
        params.outside_rth = order.outside_rth
        params.order_legs = order.order_legs
        params.algo_params = order.algo_params
        params.secret_key = order.secret_key if order.secret_key else self._secret_key
        params.adjust_limit = order.adjust_limit
        params.user_mark = order.user_mark
        params.expire_time = order.expire_time
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        params.combo_type = get_enum_value(order.combo_type)
        params.contract_legs = order.contract_legs
        params.total_cash_amount = order.total_cash_amount
        params.trading_session_type = get_enum_value(
            order.trading_session_type)

        request = OpenApiRequest(PLACE_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                order.id = response.id
                order.sub_ids = response.sub_ids
                order.orders = response.orders
                if order.order_id is None and response.order_id:
                    order.order_id = response.order_id
                return response.id
            else:
                raise ApiException(response.code, response.message)

    def modify_order(
            self,
            order: 'Order',
            quantity: Optional[Union[int, float]] = None,
            limit_price: Optional[float] = None,
            aux_price: Optional[float] = None,
            trail_stop_price: Optional[float] = None,
            trailing_percent: Optional[float] = None,
            percent_offset: Optional[float] = None,
            time_in_force: Optional[str] = None,
            outside_rth: Optional[bool] = None,
            lang: Optional[Union[Language, str]] = None,
            **kwargs) -> Optional[int]:
        """
        Modify an order. 修改订单
        
        :param order: Order object to modify. 需要修改的订单对象
        :param quantity: New quantity. If not provided, the original value is used. 新数量，如果不提供则使用原值
        :param limit_price: New limit price for limit orders. 限价订单的新限价
        :param aux_price: New auxiliary price. For stop orders, this is the stop price; for trailing stop orders, this is the offset. 新辅助价格。对于止损单，是止损价格；对于跟踪止损单，是价差
        :param trail_stop_price: New activation price for trailing stop orders. 跟踪止损单的新激活价格
        :param trailing_percent: New trailing percentage for trailing stop orders. 跟踪止损单的新百分比
        :param percent_offset: New percent offset. 新百分比偏移
        :param time_in_force: New time in force (e.g., 'DAY', 'GTC'). 新订单有效期（如"当日有效"，"撤销前有效"）
        :param outside_rth: Whether to allow execution outside regular trading hours. 是否允许在常规交易时间外执行（美股专属）
        :param lang: Language. 语言. Available options: zh_CN/zh_TW/en_US
        :param kwargs: Additional parameters such as:
                       额外参数，例如：
            quantity_scale: Quantity scale. 数量比例
            expire_time: Order expiration time. 订单过期时间
            adjust_limit: Adjust limit. 调整限制
        :return: Global order ID if successfully modified. 如果修改成功，返回全局订单ID
        
        :return example:
        40139406481165312
        """
        params = PlaceModifyOrderParams()
        params.account = order.account
        params.order_id = order.order_id
        params.id = order.id
        params.contract = order.contract
        params.action = order.action
        params.order_type = order.order_type
        params.quantity = quantity if quantity is not None else order.quantity
        params.quantity_scale = kwargs.get('quantity_scale',
                                           order.quantity_scale)
        params.limit_price = limit_price if limit_price is not None else order.limit_price
        params.aux_price = aux_price if aux_price is not None else order.aux_price
        params.trail_stop_price = trail_stop_price if trail_stop_price is not None else order.trail_stop_price
        params.trailing_percent = trailing_percent if trailing_percent is not None else order.trailing_percent
        params.percent_offset = percent_offset if percent_offset is not None else order.percent_offset
        params.time_in_force = time_in_force if time_in_force is not None else order.time_in_force
        expire_time = kwargs.get('expire_time', order.expire_time)
        if expire_time is not None:
            params.expire_time = expire_time
        params.outside_rth = outside_rth if outside_rth is not None else order.outside_rth
        params.secret_key = order.secret_key if order.secret_key else self._secret_key
        params.adjust_limit = kwargs.get('adjust_limit', order.adjust_limit)
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(MODIFY_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.id
            else:
                raise ApiException(response.code, response.message)

    def cancel_order(
        self,
        account: Optional[str] = None,
        id: Optional[int] = None,
        order_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Cancel an order. 取消订单
        
        :param account: Account ID. If not provided, the default account is used. 账户ID，如果不提供则使用默认账户
        :param id: Global order ID. 全局订单ID
        :param order_id: Account-specific order ID. 账户特定订单ID
        :return: Global order ID if successfully cancelled. 如果取消成功，返回全局订单ID
        
        :return example:
        40132638459956224
        """
        params = CancelOrderParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.order_id = order_id
        params.id = id
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(CANCEL_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.id
            else:
                raise ApiException(response.code, response.message)

    def get_transactions(self,
                         account: Optional[str]=None,
                         order_id: Optional[int]=None,
                         symbol: Optional[str]=None,
                         sec_type: Optional[Union[SecurityType, str]]=None,
                         start_time: Optional[int]=None,
                         end_time: Optional[int]=None,
                         limit: int=100,
                         expiry: Optional[str]=None,
                         strike: Optional[float]=None,
                         put_call: Optional[str]=None,
                         lang: Optional[Union[Language, str]]=None,
                         page_token: Optional[str]=None):
        """
        query order transactions, only prime accounts are supported.
        :param account: account id. If not passed, the default account is used
        :param order_id: order's id
        :param symbol: symbol of contract, like 'AAPL', '00700', 'CL2201'
        :param sec_type: security type. tigeropen.common.consts.SecurityType, like SecurityType.STK
        :param start_time: timestamp in milliseconds, like 1641398400000
        :param end_time: timestamp in milliseconds, like 1641398400000
        :param limit: limit number of response
        :param expiry: expiry date of Option. 'yyyyMMdd', like '220121'
        :param strike: strike price of Option
        :param put_call: Option right, PUT or CALL
        :return:
        """
        params = TransactionsParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.order_id = order_id
        params.sec_type = get_enum_value(sec_type)
        params.symbol = symbol
        params.start_date = date_str_to_timestamp(start_time, self._timezone)
        params.end_date = date_str_to_timestamp(end_time, self._timezone)
        params.limit = limit
        params.expiry = expiry
        params.strike = strike
        params.right = put_call
        params.page_token = page_token
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(ORDER_TRANSACTIONS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = TransactionsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                if page_token is not None:
                    return response
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_analytics_asset(self,
                            account: Optional[str]=None,
                            start_date: Optional[str]=None,
                            end_date: Optional[str]=None,
                            seg_type: Optional[Union[SegmentType, str]]=None,
                            currency: Optional[Union[Currency, str]]=None,
                            sub_account: Optional[str]=None,
                            lang: Optional[Union[Language, str]]=None):
        """
        get analytics of history asset
        :param account:
        :param start_date: date str. format yyyy-MM-dd, like '2021-12-01'
        :param end_date: date_str.
        :param seg_type: tigeropen.common.consts.SegmentType, like SegmentType.SEC
        :param currency: tigeropen.common.consts.Currency, like Currency.USD
        :param sub_account: sub account of institution account
        :return:
        """
        params = AnalyticsAssetParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.seg_type = get_enum_value(seg_type)
        params.start_date = start_date
        params.end_date = end_date
        params.currency = get_enum_value(currency)
        params.sub_account = sub_account
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)
        request = OpenApiRequest(ANALYTICS_ASSET, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = AnalyticsAssetResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_segment_fund_available(self, from_segment=None, currency=None):
        """
        get segment fund available
        :return:
        """
        params = SegmentFundParams()
        params.account = self._account
        params.from_segment = get_enum_value(from_segment)
        params.currency = get_enum_value(currency)
        params.secret_key = self._secret_key
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(SEGMENT_FUND_AVAILABLE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SegmentFundAvailableResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.data
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_segment_fund_history(self, limit=None):
        """
        get segment fund history
        :return:
        """
        params = SegmentFundParams()
        params.account = self._account
        params.limit = limit
        params.secret_key = self._secret_key
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(SEGMENT_FUND_HISTORY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SegmentFundHistoryResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.data
            else:
                raise ApiException(response.code, response.message)
        return None

    def transfer_segment_fund(self,
                              from_segment=None,
                              to_segment=None,
                              amount=None,
                              currency=None):
        """
        transfer segment fund
        :param from_segment: FUT 期货； SEC 股票。可用枚举 tigeropen.common.consts.SegmentType
        :param to_segment:
        :param amount:
        :param currency:
        :return:
        """
        params = SegmentFundParams()
        params.account = self._account
        params.secret_key = self._secret_key
        params.from_segment = get_enum_value(from_segment)
        params.to_segment = get_enum_value(to_segment)
        params.amount = amount
        params.currency = get_enum_value(currency)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(TRANSFER_SEGMENT_FUND, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SegmentFundTransferResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.data
            else:
                raise ApiException(response.code, response.message)
        return None

    def cancel_segment_fund(self, id=None):
        """
        cancel segment fund
        :param id:
        :return:
        """
        params = SegmentFundParams()
        params.account = self._account
        params.secret_key = self._secret_key
        params.id = id
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(CANCEL_SEGMENT_FUND, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SegmentFundCancelResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.data
            else:
                raise ApiException(response.code, response.message)

    def place_forex_order(self, seg_type, source_currency, target_currency,
                          source_amount):
        """
        place forex order
        :param seg_type:
        :param source_currency:
        :param target_currency:
        :param source_amount:
        :return:
        """
        params = ForexTradeOrderParams()
        params.account = self._account
        params.secret_key = self._secret_key
        params.seg_type = get_enum_value(seg_type)
        params.source_currency = get_enum_value(source_currency)
        params.target_currency = get_enum_value(target_currency)
        params.source_amount = source_amount
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(PLACE_FOREX_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ForexOrderResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.data
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_estimate_tradable_quantity(self, order, seg_type=None):
        params = EstimateTradableQuantityModel()
        params.account = self._account
        params.secret_key = self._secret_key
        params.lang = get_enum_value(self._lang)
        params.contract = order.contract
        params.order_type = order.order_type
        params.action = order.action
        params.limit_price = order.limit_price
        params.stop_price = order.aux_price
        params.seg_type = get_enum_value(seg_type)

        request = OpenApiRequest(ESTIMATE_TRADABLE_QUANTITY, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = EstimateTradableQuantityResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_funding_history(self, seg_type=None):
        params = FundingHistoryParams()
        params.account = self._account
        params.secret_key = self._secret_key
        params.seg_type = get_enum_value(seg_type)
        params.lang = get_enum_value(self._lang)
        request = OpenApiRequest(TRANSFER_FUND, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FundingHistoryResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_fund_details(self,
                         seg_types,
                         account=None,
                         fund_type=None,
                         currency=None,
                         start=0,
                         limit=None,
                         start_date=None,
                         end_date=None,
                         secret_key=None,
                         lang=None):
        params = FundDetailsParams()
        params.account = account if account else self._account
        params.secret_key = secret_key if secret_key else self._secret_key
        if seg_types:
            seg_types_list = seg_types if isinstance(seg_types,
                                                     list) else [seg_types]
            seg_types_params = [get_enum_value(t) for t in seg_types_list]
            params.seg_types = seg_types_params
        params.fund_type = get_enum_value(fund_type)
        params.currency = get_enum_value(currency)
        params.start = start
        params.limit = limit
        params.start_date = start_date
        params.end_date = end_date
        params.lang = get_enum_value(lang) if lang else get_enum_value(
            self._lang)

        request = OpenApiRequest(FUND_DETAILS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FundDetailsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.result
            else:
                raise ApiException(response.code, response.message)

    def __fetch_data(self, request):
        try:
            response = super(TradeClient, self).execute(request)
            return response
        except Exception as e:
            if THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e
