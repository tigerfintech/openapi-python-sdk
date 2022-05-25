# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import logging

from tigeropen.common.consts import THREAD_LOCAL, SecurityType, Market, Currency
from tigeropen.common.consts.service_types import CONTRACTS, ACCOUNTS, POSITIONS, ASSETS, ORDERS, ORDER_NO, \
    CANCEL_ORDER, MODIFY_ORDER, PLACE_ORDER, ACTIVE_ORDERS, INACTIVE_ORDERS, FILLED_ORDERS, CONTRACT, PREVIEW_ORDER, \
    PRIME_ASSETS, ORDER_TRANSACTIONS, QUOTE_CONTRACT
from tigeropen.common.exceptions import ApiException
from tigeropen.common.util.common_utils import get_enum_value
from tigeropen.common.request import OpenApiRequest
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.trade.domain.order import Order
from tigeropen.trade.request.model import ContractParams, AccountsParams, AssetParams, PositionParams, OrdersParams, \
    OrderParams, PlaceModifyOrderParams, CancelOrderParams, TransactionsParams
from tigeropen.trade.response.account_profile_response import ProfilesResponse
from tigeropen.trade.response.assets_response import AssetsResponse
from tigeropen.trade.response.contracts_response import ContractsResponse
from tigeropen.trade.response.order_id_response import OrderIdResponse
from tigeropen.trade.response.order_preview_response import PreviewOrderResponse
from tigeropen.trade.response.orders_response import OrdersResponse
from tigeropen.trade.response.positions_response import PositionsResponse
from tigeropen.trade.response.prime_assets_response import PrimeAssetsResponse
from tigeropen.trade.response.transactions_response import TransactionsResponse


class TradeClient(TigerOpenClient):
    def __init__(self, client_config, logger=None):
        if not logger:
            logger = logging.getLogger('tiger_openapi')
        super(TradeClient, self).__init__(client_config, logger=logger)
        if client_config:
            self._account = client_config.account
            self._lang = client_config.language
            self._secret_key = client_config.secret_key
        else:
            self._account = None
            self._secret_key = None

    def get_managed_accounts(self, account=None):
        """
        获取管理的账号列表
        :param account:
        :return: AccountProfile 对象, 有如下属性：
            account： 交易账户
            capability： 账户类型(CASH:现金账户, MGRN: Reg T 保证金账户, PMGRN: 投资组合保证金)
            status： 账户状态(New, Funded, Open, Pending, Abandoned, Rejected, Closed, Unknown)
        """
        params = AccountsParams()
        params.account = account if account else self._account
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

    def get_contracts(self, symbol, sec_type=SecurityType.STK, currency=None, exchange=None):
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

    def get_contract(self, symbol, sec_type=SecurityType.STK, currency=None, exchange=None, expiry=None, strike=None,
                     put_call=None):
        """
        获取合约
        :param symbol:
        :param sec_type: 合约类型 tigeropen.common.consts.SecurityType
        :param currency: 币种 tigeropen.common.consts.Currency
        :param exchange: 交易所
        :param expiry: 合约到期日(期货/期权) yyyyMMdd
        :param strike: 行权价(期权)
        :param put_call: CALL/PUT
        :return: Contract 对象. 有如下属性:
            symbol: 合约 symbol
            identifier: 合约唯一标识
            currency: 币种
            exchange: 交易所
            name: 合约名称
            sec_type: 合约类型
            long_initial_margin: 做多初始保证金比例
            long_maintenance_margin: 做多维持保证金比例
            short_fee_rate: 做空费率
            short_margin: 做空保证金
            shortable: 做空池剩余
            multiplier: 合约乘数
            expiry: 合约到期日(期货/期权)
            contract_month: 合约月份(期货)
            strike: 行权价(期权)
            put_call: 看跌/看涨(期权)
        """
        params = ContractParams()
        params.account = self._account
        params.secret_key = self._secret_key
        params.symbol = symbol
        params.sec_type = get_enum_value(sec_type)
        params.currency = get_enum_value(currency)
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
                return response.contracts[0] if len(response.contracts) == 1 else None
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
        params.lang = get_enum_value(lang) if lang else get_enum_value(self._lang)

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

    def get_positions(self, account=None, sec_type=SecurityType.STK, currency=Currency.ALL, market=Market.ALL,
                      symbol=None, sub_accounts=None):
        """
        获取持仓数据
        :param account:
        :param sec_type:
        :param currency:
        :param market:
        :param symbol:
        :param sub_accounts:
        :return: 由 Position 对象构成的列表. Position 对象有如下属性:
            account: 所属账户
            contract: 合约对象
            quantity: 持仓数量
            average_cost: 持仓成本
            market_price: 最新价格
            market_value: 市值
            realized_pnl: 实现盈亏
            unrealized_pnl: 持仓盈亏
        """
        params = PositionParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.sub_accounts = sub_accounts
        params.currency = get_enum_value(currency)
        params.market = get_enum_value(market)
        params.symbol = symbol

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

    def get_assets(self, account=None, sub_accounts=None, segment=False, market_value=False):
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

    def get_prime_assets(self, account=None):
        """
        get prime account assets
        :param account:
        :return: tigeropen.trade.domain.prime_account.PortfolioAccount
        """
        params = AssetParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key

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

    def get_orders(self, account=None, sec_type=None, market=Market.ALL, symbol=None, start_time=None, end_time=None,
                   limit=100, is_brief=False, states=None):
        """
        获取订单列表
        :param account:
        :param sec_type:
        :param market:
        :param symbol:
        :param start_time: 开始时间. 若是时间戳需要精确到毫秒, 为13位整数；
                                    或是日期时间格式的字符串，如"2017-01-01"和 "2017-01-01 12:00:00"
        :param end_time: 截至时间. 格式同 start_time
        :param limit: 每次获取订单的数量
        :param is_brief: 是否返回精简的订单数据
        :param states: 订单状态枚举对象列表, 可选, 若传递则按状态筛选
        :return: Order 对象构成的列表. Order 对象信息参见 tigeropen.trade.domain.order
        """
        params = OrdersParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.market = get_enum_value(market)
        params.symbol = symbol
        params.start_date = start_time
        params.end_date = end_time
        params.limit = limit
        params.is_brief = is_brief
        params.states = [get_enum_value(state) for state in states] if states else None
        request = OpenApiRequest(ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content, secret_key=params.secret_key)
            if response.is_success():
                return response.orders
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_open_orders(self, account=None, sec_type=None, market=Market.ALL, symbol=None, start_time=None,
                        end_time=None, parent_id=None):
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
        params.start_date = start_time
        params.end_date = end_time
        params.parent_id = parent_id
        request = OpenApiRequest(ACTIVE_ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content, secret_key=params.secret_key)
            if response.is_success():
                return response.orders
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_cancelled_orders(self, account=None, sec_type=None, market=Market.ALL, symbol=None, start_time=None,
                             end_time=None):
        """
        获取已撤销订单列表. 参数同 get_orders
        """
        params = OrdersParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.market = get_enum_value(market)
        params.symbol = symbol
        params.start_date = start_time
        params.end_date = end_time
        request = OpenApiRequest(INACTIVE_ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content, secret_key=params.secret_key)
            if response.is_success():
                return response.orders
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_filled_orders(self, account=None, sec_type=None, market=Market.ALL, symbol=None, start_time=None,
                          end_time=None):
        """
        获取已成交订单列表. 参数同 get_orders
        """
        params = OrdersParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.sec_type = get_enum_value(sec_type)
        params.market = get_enum_value(market)
        params.symbol = symbol
        params.start_date = start_time
        params.end_date = end_time
        request = OpenApiRequest(FILLED_ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content, secret_key=params.secret_key)
            if response.is_success():
                return response.orders
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_order(self, account=None, id=None, order_id=None, is_brief=False):
        """
        获取指定订单
        :param account:
        :param id:
        :param order_id:
        :param is_brief: 是否返回精简的订单数据
        :return: Order 对象. 对象信息参见 tigeropen.trade.domain.order
        """
        params = OrderParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.id = id
        params.order_id = order_id
        params.is_brief = is_brief
        request = OpenApiRequest(ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content, secret_key=params.secret_key)
            if response.is_success():
                return response.orders[0] if len(response.orders) == 1 else None
            else:
                raise ApiException(response.code, response.message)
        return None

    def create_order(self, account, contract, action, order_type, quantity, limit_price=None, aux_price=None,
                     trail_stop_price=None, trailing_percent=None, percent_offset=None, time_in_force=None,
                     outside_rth=None, order_legs=None, algo_params=None, **kwargs):
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
        request = OpenApiRequest(ORDER_NO, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                order_id = response.order_id
                order = Order(account, contract, action, order_type, quantity, limit_price=limit_price,
                              aux_price=aux_price, trail_stop_price=trail_stop_price,
                              trailing_percent=trailing_percent, percent_offset=percent_offset,
                              time_in_force=time_in_force, outside_rth=outside_rth, order_id=order_id,
                              order_legs=order_legs, algo_params=algo_params, secret_key=params.secret_key, **kwargs)
                return order
            else:
                raise ApiException(response.code, response.message)

        return None

    def preview_order(self, order):
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
        params.limit_price = order.limit_price
        params.aux_price = order.aux_price
        params.trail_stop_price = order.trail_stop_price
        params.trailing_percent = order.trailing_percent
        params.percent_offset = order.percent_offset
        params.time_in_force = order.time_in_force
        params.outside_rth = order.outside_rth
        params.secret_key = order.secret_key if order.secret_key else self._secret_key
        request = OpenApiRequest(PREVIEW_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = PreviewOrderResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.preview_order
            else:
                raise ApiException(response.code, response.message)

    def place_order(self, order):
        """
        下单
        :param order:  Order 对象
        :return:
        """
        params = PlaceModifyOrderParams()
        params.account = order.account
        params.contract = order.contract
        params.action = order.action
        params.order_type = order.order_type
        params.order_id = order.order_id
        params.quantity = order.quantity
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

        request = OpenApiRequest(PLACE_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                order.id = response.id
                order.sub_ids = response.sub_ids
                if order.order_id is None and response.order_id:
                    order.order_id = response.order_id
                return response.id
            else:
                raise ApiException(response.code, response.message)

    def modify_order(self, order, quantity=None, limit_price=None, aux_price=None,
                     trail_stop_price=None, trailing_percent=None, percent_offset=None,
                     time_in_force=None, outside_rth=None, **kwargs):
        """
        修改订单
        :param order:
        :param quantity:
        :param limit_price: 限价
        :param aux_price: 在止损单表示止损价格; 在跟踪止损单表示价差
        :param trail_stop_price: 跟踪止损单--触发止损单的价格
        :param trailing_percent: 跟踪止损单--百分比
        :param percent_offset:
        :param time_in_force: 订单有效期， 'DAY'（当日有效）和'GTC'（取消前有效)
        :param outside_rth: 是否允许盘前盘后交易(美股专属)
        :return:
        """
        params = PlaceModifyOrderParams()
        params.account = order.account
        params.order_id = order.order_id
        params.id = order.id
        params.contract = order.contract
        params.action = order.action
        params.order_type = order.order_type
        params.quantity = quantity if quantity is not None else order.quantity
        params.limit_price = limit_price if limit_price is not None else order.limit_price
        params.aux_price = aux_price if aux_price is not None else order.aux_price
        params.trail_stop_price = trail_stop_price if trail_stop_price is not None else order.trail_stop_price
        params.trailing_percent = trailing_percent if trailing_percent is not None else order.trailing_percent
        params.percent_offset = percent_offset if percent_offset is not None else order.percent_offset
        params.time_in_force = time_in_force if time_in_force is not None else order.time_in_force
        params.outside_rth = outside_rth if outside_rth is not None else order.outside_rth
        params.secret_key = order.secret_key if order.secret_key else self._secret_key
        params.adjust_limit = kwargs.get('adjust_limit', order.adjust_limit)

        request = OpenApiRequest(MODIFY_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.id
            else:
                raise ApiException(response.code, response.message)

    def cancel_order(self, account=None, id=None, order_id=None):
        """
        取消订单
        :param account:
        :param id: 全局订单 id
        :param order_id: 账户自增订单 id
        :return:
        """
        params = CancelOrderParams()
        params.account = account if account else self._account
        params.secret_key = self._secret_key
        params.order_id = order_id
        params.id = id
        request = OpenApiRequest(CANCEL_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.id
            else:
                raise ApiException(response.code, response.message)

    def get_transactions(self, account=None, order_id=None, symbol=None, sec_type=None, start_time=None, end_time=None,
                         limit=100, expiry=None, strike=None, put_call=None):
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
        params.start_date = start_time
        params.end_date = end_time
        params.limit = limit
        params.expiry = expiry
        params.strike = strike
        params.right = put_call
        request = OpenApiRequest(ORDER_TRANSACTIONS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = TransactionsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.transactions
            else:
                raise ApiException(response.code, response.message)
        return None

    def __fetch_data(self, request):
        try:
            response = super(TradeClient, self).execute(request)
            return response
        except Exception as e:
            if THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e
