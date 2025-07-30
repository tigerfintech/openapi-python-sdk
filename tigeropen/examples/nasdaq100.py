import datetime
import logging
import sys
import time

import pandas as pd

from tigeropen.common.consts import BarPeriod, SecurityType, Market, Currency
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import limit_order
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import get_client_config
from tigeropen.trade.trade_client import TradeClient

client_logger = logging.getLogger('client')
client_logger.setLevel(logging.WARNING)
client_logger.addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)

# 纳斯达克100指数成分股 Components of Nasdaq-100. Up to 2021/12/20
UNIVERSE_NDX = ["AAPL", "ADBE", "ADI", "ADP", "ADSK", "AEP", "ALGN", "AMAT", "AMD", "AMGN", "AMZN", "ANSS", "ASML",
                "ATVI", "AVGO", "BIDU", "BIIB", "BKNG", "CDNS", "CDW", "CERN", "CHKP", "CHTR", "CMCSA", "COST", "CPRT",
                "CRWD", "CSCO", "CSX", "CTAS", "CTSH", "DLTR", "DOCU", "DXCM", "EA", "EBAY", "EXC", "FAST", "FB",
                "FISV", "FOX", "GILD", "GOOG", "HON", "IDXX", "ILMN", "INCY", "INTC", "INTU", "ISRG",
                "JD", "KDP", "KHC", "KLAC", "LRCX", "LULU", "MAR", "MCHP", "MDLZ", "MELI", "MNST", "MRNA", "MRVL",
                "MSFT", "MTCH", "MU", "NFLX", "NTES", "NVDA", "NXPI", "OKTA", "ORLY", "PAYX", "PCAR", "PDD", "PEP",
                "PTON", "PYPL", "QCOM", "REGN", "ROST", "SBUX", "SGEN", "SIRI", "SNPS", "SPLK", "SWKS", "TCOM", "TEAM",
                "TMUS", "TSLA", "TXN", "VRSK", "VRSN", "VRTX", "WBA", "WDAY", "XEL", "XLNX", "ZM"]

# 恒生科技指数成分股. Up to 2021/12/20
UNIVERSE_HSTECH = ["00241", "00268", "00285", "00522", "00700", "00772", "00780", "00909", "00981", "00992", "01024",
                   "01347", "01810", "01833", "02013", "02018", "02382", "02518", "03690", "03888", "06060", "06618",
                   "06690", "09618", "09626", "09698", "09888", "09961", "09988", "09999"]

# 持仓股票个数
HOLDING_NUM = 5
# 订单检查次数
ORDERS_CHECK_MAX_TIMES = 10
# 获取行情每次请求symbol个数
REQUEST_SIZE = 50
TARGET_QUANTITY = "target_quantity"
PRE_CLOSE = "pre_close"
LATEST_PRICE = "latest_price"
MARKET_CAPITAL = "market_capital"
SYMBOL = "symbol"
WEIGHT = "weight"
TIME = "time"
CLOSE = "close"
DATE = "date"
LOT_SIZE = "lot_size"

PRIVATE_KEY_PATH = "your private key path"
TIGER_ID = "your tiger id"
ACCOUNT = "your account"
_client_config = get_client_config(private_key_path=PRIVATE_KEY_PATH, tiger_id=TIGER_ID, account=ACCOUNT)
quote_client = QuoteClient(_client_config, logger=client_logger)
trade_client = TradeClient(_client_config, logger=client_logger)


def request(symbols, method, **kwargs):
    """
    :param symbols:
    :param method:
    :param kwargs:
    :return:
    """
    symbols = list(symbols)
    result = pd.DataFrame()
    for i in range(0, len(symbols), REQUEST_SIZE):
        part = symbols[i:i + REQUEST_SIZE]
        quote = method(part, **kwargs)
        result = result.append(quote)
        # for rate limit
        time.sleep(0.5)
    return result


def get_quote(symbols):
    quote = request(symbols, quote_client.get_stock_briefs)
    return quote.set_index(SYMBOL)


def get_trade_meta(symbols):
    metas = request(symbols, quote_client.get_trade_metas)
    return metas.set_index(SYMBOL)


def get_history(symbols, total=200, batch_size=50) -> pd.DataFrame:
    """

    :param symbols:
    :param total:
    :param batch_size:
    :return:
                                               time      open     high       low   close     volume
    date                      symbol
    2021-03-05 00:00:00-05:00 AAPL    1614920400000  120.9800  121.935  117.5700  121.42  153766601
                              ADBE    1614920400000  444.8800  444.950  423.7101  440.83    4614971
                              ADI     1614920400000  149.0000  149.620  143.3900  148.88    4040153
                              ADP     1614920400000  171.8300  179.000  171.5003  178.26    2535893
                              ADSK    1614920400000  270.3300  270.330  255.0200  267.39    1835526
    ...                                         ...       ...      ...       ...     ...        ...
    2021-12-16 00:00:00-05:00 WBA     1639630800000   48.5035   50.150   48.5000   49.26    5551852
                              WDAY    1639630800000  277.3300  278.365  269.2600  272.23    1206784
                              XEL     1639630800000   68.5800   69.570   68.3100   68.95    3774564
                              XLNX    1639630800000  217.3700  218.080  198.5100  199.78    4299386
                              ZM      1639630800000  183.7900  185.720  177.0000  182.40    4224447
    """
    end = int(datetime.datetime.today().timestamp() * 1000)
    history = pd.DataFrame()
    for i in range(0, total, batch_size):
        if i + batch_size <= total:
            limit = batch_size
        else:
            limit = i + batch_size - total
        logger.info(f'query history, end_time:{end}, limit:{limit}')
        part = request(symbols, quote_client.get_bars, period=BarPeriod.DAY, end_time=end, limit=limit)
        part[DATE] = pd.to_datetime(part[TIME], unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
        end = min(part[TIME])
        history = history.append(part)
    history.set_index([DATE, SYMBOL], inplace=True)
    history.sort_index(inplace=True)
    return history


class Strategy:

    def __init__(self):
        self.market = Market.US
        self.currency = Currency.USD
        self.universe = UNIVERSE_NDX
        # self.market = Market.HK
        # self.currency = Currency.HKD
        # self.universe = UNIVERSE_HSTECH

        self.selected_symbols = list()
        # 计算动量的时间周期
        self.momentum_period = 30
        # 持仓股票个数
        self.holding_num = HOLDING_NUM
        # 调仓后隔夜剩余流动性目标占比，剩余流动性占比越高，风控状态越安全，如果隔夜剩余流动性占比过低（比如小于5%), 则存在被强平的风险。
        self.target_overnight_liquidation_ratio = 0.6

    def screen_stocks(self):
        """screen stock by price momentum
        按动量筛选股票. 选取周期内涨幅最高的若干股票
        :return:
        """
        history = get_history(self.universe)
        close_data = history[CLOSE].unstack()
        momentum = close_data.pct_change(periods=self.momentum_period).iloc[-1]
        self.selected_symbols = momentum.nlargest(self.holding_num).index.values.tolist()
        return self.selected_symbols

    def rebalance_portfolio(self):
        """
        调仓。先将本次选股未选中但在持仓中的股票进行平仓，然后将选中的股票按照等股数权重买入
        :return:
        """
        position_list = trade_client.get_positions(sec_type=SecurityType.STK, market=self.market)
        positions = dict()
        for pos in position_list:
            positions[pos.contract.symbol] = pos.quantity

        need_close_symbols = set(positions.keys()) - set(self.selected_symbols)

        # 如果不是美股，需要获取股票的每手股数，每次下单的股数只能使用每手股数的整数倍
        lot_size = get_trade_meta(set(positions.keys()).union(self.selected_symbols))[LOT_SIZE]
        latest_price = get_quote(need_close_symbols)[LATEST_PRICE]
        orders = list()
        for symbol in need_close_symbols:
            contract = stock_contract(symbol, currency=self.currency.name)
            # 将下单股数处理为每手股数的整数倍
            quantity = int(positions[symbol] // lot_size[symbol] * lot_size[symbol])
            if quantity == 0:
                logger.warning(f'can not place order with this quantity, symbol:{symbol}, lot_size:{lot_size[symbol]},'
                               f'quantity:{positions[symbol]}')
                continue
            limit_price = latest_price[symbol]
            order = limit_order(account=ACCOUNT,
                                contract=contract,
                                action='SELL' if quantity > 0 else 'BUY',
                                quantity=abs(quantity),
                                limit_price=limit_price)
            orders.append(order)
        self.execute_orders(orders)

        # 环球账户 global account
        # asset = trade_client.get_assets(account=ACCOUNT, segment=True)[0].segments['S']
        # target_overnight_liquidation = asset.equity_with_loan * self.target_overnight_liquidation_ratio
        # adjust_value = asset.sma - target_overnight_liquidation

        # 综合/模拟账户 prime/paper account
        asset = trade_client.get_prime_assets(account=ACCOUNT).segments['S']
        # 调仓后目标隔夜剩余流动性(隔夜剩余流动性 overnight_liquidation = 含贷款价值总权益 equity_with_loan - 隔夜保证金 overnight_margin)
        # 隔夜剩余流动性比例 = 隔夜剩余流动性 overnight_liquidation / 含贷款价值总权益 equity_with_loan
        target_overnight_liquidation = asset.equity_with_loan * self.target_overnight_liquidation_ratio
        # 如果流动性充足，需要买入的金额
        adjust_value = asset.overnight_liquidation - target_overnight_liquidation
        if adjust_value <= 0:
            logger.info('no enough liquidation')
            return
        quote = get_quote(self.selected_symbols)
        # 按持股数量等权重持仓，equal weight
        quote[WEIGHT] = 1 / len(self.selected_symbols)
        quote[TARGET_QUANTITY] = (adjust_value * quote[WEIGHT] / quote[LATEST_PRICE]).astype(int)

        orders = list()
        for symbol in quote.index:
            contract = stock_contract(symbol, self.currency.name)
            quantity = int(quote[TARGET_QUANTITY][symbol] // lot_size[symbol] * lot_size[symbol])
            # 该检查主要针对非美股。如果目前下单股数不是log_size的整数倍，则不能下单，只能通过app进行碎股卖出
            if quantity == 0:
                logger.warning(f'can not place order with this quantity, symbol:{symbol}, lot_size:{lot_size[symbol]},'
                               f'quantity:{quote[TARGET_QUANTITY][symbol]}')
                continue
            order = limit_order(account=ACCOUNT,
                                contract=contract,
                                action='BUY',
                                quantity=quantity,
                                limit_price=quote[LATEST_PRICE][symbol])
            order.time_in_force = 'GTC'  # 'DAY' 日内有效 / 'GTC' 撤销前有效
            orders.append(order)
        self.execute_orders(orders)

    def execute_orders(self, orders):
        local_orders = dict()
        for order in orders:
            try:
                trade_client.place_order(order)
                logger.info(f'place order, {order.action} {order.contract.symbol} {order.quantity} {order.limit_price}')
                local_orders[order.id] = order
            except Exception as e:
                logger.error(f'place order error:{order}')
                logger.error(e, exc_info=True)

        time.sleep(20)
        i = 0
        while i <= ORDERS_CHECK_MAX_TIMES:
            logger.info(f'check {i} times')
            history_open_orders = trade_client.get_open_orders(account=ACCOUNT, sec_type=SecurityType.STK,
                                                               market=self.market,
                                                               start_time=self.get_time_from_now(
                                                                   datetime.timedelta(days=1)),
                                                               end_time=self.get_time_from_now())
            if not history_open_orders:
                break

            # 检查一定次数后如果还未成交， 进行一次改单， 修改限价为最新价格
            if i == ORDERS_CHECK_MAX_TIMES // 2:
                for open_order in history_open_orders:
                    latest_price = get_quote([open_order.contract.symbol])[LATEST_PRICE][open_order.contract.symbol]
                    try:
                        trade_client.modify_order(open_order, limit_price=latest_price)
                        logger.info(f'modify order, id:{open_order.id}, symbol:{open_order.contract.symbol},'
                                    f' old_price:{open_order.limit_price}, new_price:{latest_price}')
                    except Exception as e:
                        logger.error(f'modify order error:{open_order.id}')
                        logger.error(e)
            # 如果达到最大检查次数还未成交，则进行撤单
            if i >= ORDERS_CHECK_MAX_TIMES:
                for order in history_open_orders:
                    logger.info(f'the order was not filled, now cancel it: {order}')
                    try:
                        trade_client.cancel_order(ACCOUNT, id=order.id)
                    except Exception as e:
                        logger.error(f'cancel order error: {order}')
                        logger.error(e, exc_info=True)
            i += 1
            time.sleep(10)

        # 打印已成交订单信息
        filled_orders = trade_client.get_filled_orders(account=ACCOUNT,
                                                       sec_type=SecurityType.STK,
                                                       market=self.market,
                                                       start_time=self.get_time_from_now(datetime.timedelta(days=1)),
                                                       end_time=self.get_time_from_now())
        order_infos = [(str(order.id) + ':' + order.contract.symbol + ':' + order.action + ':' + str(order.filled)
                        + ':' + str(order.avg_fill_price)) for order in filled_orders]
        logger.info(f'recently filled orders:{order_infos}')

        # 打印未成交订单信息
        unfilled_order_ids = set(local_orders.keys()) - set(order.id for order in filled_orders)
        for order_id in unfilled_order_ids:
            order = trade_client.get_order(ACCOUNT, id=order_id)
            logger.info(f'order was cancelled, id:{order.id}, status:{order.status}, reason:{order.reason}')

    @staticmethod
    def get_time_from_now(delta=None):
        if not delta:
            return int(datetime.datetime.now().timestamp()) * 1000
        return int((datetime.datetime.now() - delta).timestamp()) * 1000

    def run(self):
        perms = quote_client.grab_quote_permission()
        logger.info(perms)
        self.screen_stocks()
        self.rebalance_portfolio()


if __name__ == '__main__':
    strategy = Strategy()
    strategy.run()
