# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.consts import OrderStatus

ORDER_FIELDS_TO_IGNORE = {'type', '_status', 'contract', '_remaining'}
ALGO_PARAMS_TAG_MAP = {'noTakeLiq': 'no_take_liq', 'startTime': 'start_time', 'endTime': 'end_time',
                       'participationRate': 'participation_rate', 'allowPastEndTime': 'allow_past_end_time'}


class Order:
    __slots__ = ["account", "id", "order_id", "parent_id", "order_time", "reason", "trade_time", "contract", "action",
                 "quantity", "filled", "_remaining", "avg_fill_price", "commission", "realized_pnl", "_status",
                 "trail_stop_price", "limit_price", "aux_price", "trailing_percent", "percent_offset", "action",
                 "order_type", "time_in_force", "outside_rth", "order_legs", "algo_params", "algo_strategy",
                 "secret_key", "liquidation", "discount", "attr_desc", "source", 'adjust_limit', 'sub_ids', "user_mark",
                 "update_time", "expire_time"]

    def __init__(self, account, contract, action, order_type, quantity, limit_price=None, aux_price=None,
                 trail_stop_price=None, trailing_percent=None, percent_offset=None, time_in_force=None,
                 outside_rth=None, filled=0, avg_fill_price=0, commission=None, realized_pnl=None,
                 id=None, order_id=None, parent_id=None, order_time=None, trade_time=None, order_legs=None,
                 algo_params=None, secret_key=None, **kwargs):
        """
        - account: 订单所属的账户
        - id: 全局订单 id
        - order_id: 账户自增订单号
        - parent_id: 主订单id, 目前只用于 TigerTrade App端的附加订单中
        - order_time: 下单时间
        - reason: 下单失败时, 会返回失败原因的描述
        - trade_time: 最新成交时间
        - update_time: order updated time
        - action: 交易方向, 'BUY' / 'SELL'
        - quantity: 下单数量
        - filled: 成交数量
        - avg_fill_price: 包含佣金的平均成交价
        - commission: 包含佣金, 印花税, 证监会费等系列费用
        - realized_pnl: 实现盈亏
        - trail_stop_price: 跟踪止损单--触发止损单的价格
        - limit_price: 限价单价格
        - aux_price: 在止损单中, 表示触发止损单的价格, 在移动止损单中, 表示跟踪的价差
        - trailing_percent:  跟踪止损单-百分比, 取值范围为0-100
        - percent_offset: None,
        - order_type: 订单类型, 'MKT' 市价单 / 'LMT' 限价单 / 'STP' 止损单 / 'STP_LMT' 止损限价单 / 'TRAIL' 跟踪止损单
        - time_in_force: 有效期,'DAY' 日内有效 / 'GTC' good till cancel  / 'GTD' good till date
        - outside_rth: 是否允许盘前盘后交易(outside of regular trading hours 美股专属). True 允许, False 不允许
        - contract: 合约对象
        - status: Order_Status 的枚举, 表示订单状态
        - remaining: 未成交的数量
        - order_legs: 附加订单列表
        - algo_params: 算法订单参数
        - secret_key: 机构交易员专有密钥
        - liquidation
        - algo_strategy
        - discount
        - adjust_limit 价格微调幅度（默认为0表示不调整，正数为向上调整，负数向下调整），对传入价格自动调整到合法价位上.
          例如：0.001 代表向上调整且幅度不超过 0.1%；-0.001 代表向下调整且幅度不超过 0.1%。默认 0 表示不调整
        - sub_ids id list of sub orders.
        - user_mark: user's remark
        - expire_time: GTD order's expire time
        """

        self.id = id
        self.order_id = order_id
        self.parent_id = parent_id
        self.account = account
        self.reason = None
        self.contract = contract
        self.action = action
        self.quantity = quantity
        self.filled = filled
        self._remaining = None
        self.avg_fill_price = avg_fill_price
        self.realized_pnl = realized_pnl
        self.commission = commission
        self._status = OrderStatus.NEW
        self.time_in_force = time_in_force
        self.outside_rth = outside_rth
        self.order_type = order_type
        self.limit_price = limit_price
        self.aux_price = aux_price
        self.trail_stop_price = trail_stop_price
        self.trailing_percent = trailing_percent
        self.percent_offset = percent_offset
        self.order_time = order_time
        self.trade_time = trade_time
        self.update_time = kwargs.get('update_time')
        self.order_legs = order_legs
        self.algo_params = algo_params
        self.secret_key = secret_key
        self.liquidation = kwargs.get('liquidation')
        self.algo_strategy = kwargs.get('algo_strategy')
        self.discount = kwargs.get('discount')
        self.attr_desc = kwargs.get('attr_desc')
        self.source = kwargs.get('source')
        self.adjust_limit = kwargs.get('adjust_limit')
        self.sub_ids = kwargs.get('sub_ids')
        self.user_mark = kwargs.get('user_mark')
        self.expire_time = kwargs.get('expire_time')

    def to_dict(self):
        dct = {name: getattr(self, name) for name in self.__slots__ if name not in ORDER_FIELDS_TO_IGNORE}

        dct['contract'] = self.contract
        if self.status:
            dct['status'] = self.status.name
        dct['remaining'] = self.remaining

        return dct

    @property
    def status(self):
        if not self.remaining and self.filled:
            return OrderStatus.FILLED
        elif self._status == OrderStatus.HELD and self.filled:
            return OrderStatus.PARTIALLY_FILLED
        else:
            return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def active(self):
        return self.status in [OrderStatus.PENDING_NEW, OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED,
                               OrderStatus.HELD, OrderStatus.PENDING_CANCEL]

    @property
    def remaining(self):
        return self.quantity - self.filled

    def __repr__(self):
        """
        String representation for this object.
        """
        return "Order(%s)" % self.to_dict().__repr__()


class OrderLeg:
    """
    附加订单
    """

    def __init__(self, leg_type, price, time_in_force='DAY', outside_rth=None, limit_price=None, trailing_percent=None,
                 trailing_amount=None):
        """
        :param leg_type: 附加订单类型(仅限价单支持). PROFIT 止盈单; LOSS 止损单
        :param price: 附加订单触发价格
        :param time_in_force: 附加订单有效期. 'DAY'（当日有效）和 'GTC'（取消前有效).
        :param outside_rth: 附加订单是否允许盘前盘后交易(美股专属). True 允许, False 不允许.
        :param limit_price: attached stop loss order's limit price
        :param trailing_percent: attached trailing stop loss order's trailing percent
        :param trailing_amount: attached trailing stop loss order's trailing amount
        """
        self.leg_type = leg_type
        self.price = price
        self.time_in_force = time_in_force
        self.outside_rth = outside_rth
        self.limit_price = limit_price
        self.trailing_percent = trailing_percent
        self.trailing_amount = trailing_amount

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return "OrderLeg(%s)" % self.to_dict()


class AlgoParams:
    """
    算法订单参数
    """
    def __init__(self, start_time=None, end_time=None, no_take_liq=None, allow_past_end_time=None,
                 participation_rate=None):
        """
        :param start_time: 生效开始时间(时间戳 TWAP和VWAP专用)
        :param end_time: 生效结束时间(时间戳 TWAP和VWAP专用)
        :param no_take_liq: 是否尽可能减少交易次数(VWAP订单专用)
        :param allow_past_end_time: 是否允许生效时间结束后继续完成成交(TWAP和VWAP专用)
        :param participation_rate: 参与率(VWAP专用,0.01-0.5)
        """
        self.start_time = start_time
        self.end_time = end_time
        self.no_take_liq = no_take_liq
        self.allow_past_end_time = allow_past_end_time
        self.participation_rate = participation_rate

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_tags(tag_values):
        """
        :param tag_values:
        :return: AlgoParams 对象
        """
        algo_params = AlgoParams()
        if tag_values:
            for item in tag_values:
                tag = item.get('tag')
                value = item.get('value')
                setattr(algo_params, ALGO_PARAMS_TAG_MAP.get(tag), value)
            return algo_params
        return None

    def __repr__(self):
        return "AlgoParams(%s)" % self.to_dict()
    

class Transaction:
    """
    订单成交记录。Transactions of order.
    """
    def __init__(self, account=None, order_id=None, contract=None, id_=None, action=None,
                 filled_quantity=None, filled_price=None, filled_amount=None, transacted_at=None):
        self.account = account
        self.order_id = order_id
        self.contract = contract
        self.id = id_
        self.action = action
        self.filled_quantity = filled_quantity
        self.filled_price = filled_price
        self.filled_amount = filled_amount
        self.transacted_at = transacted_at

    def __repr__(self):
        return "Transaction({})".format(self.__dict__)
