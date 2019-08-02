import logging
import pandas as pd
import talib as ta

from datetime import datetime, timedelta
from time import sleep
from functools import wraps

from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import get_client_config
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.consts import *
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import limit_order

PRIVATE_KEY_PATH = 'your private key path'
TIGER_ID = 'your tiger_id'
# 下单使用的账户
ACCOUNT = 'your account'
# 查询订单成交的重试次数
MAX_RETRY = 30
# 日志文件的路径
LOG_PATH = 'sp500.log'

# sp500 的成分股
UNIVERSE = ['MMM', 'ABT', 'ABBV', 'ACN', 'ATVI', 'AYI', 'ADBE', 'AMD', 'AAP', 'AES', 'AET', 'AMG', 'AFL', 'A', 'APD',
            'AKAM', 'ALK', 'ALB', 'ARE', 'ALXN', 'ALGN', 'ALLE', 'AGN', 'ADS', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO',
            'AMZN', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'APC', 'ADI',
            'ANDV', 'ANSS', 'ANTM', 'AON', 'AOS', 'APA', 'AIV', 'AAPL', 'AMAT', 'APTV', 'ADM', 'ARNC', 'AJG', 'AIZ',
            'T', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'BHGE', 'BLL', 'BAC', 'BK', 'BAX', 'BBT', 'BDX', 'BRK.B', 'BBY',
            'BIIB', 'BLK', 'HRB', 'BA', 'BKNG', 'BWA', 'BXP', 'BSX', 'BHF', 'BMY', 'AVGO', 'BF.B', 'CHRW', 'CA', 'COG',
            'CDNS', 'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CAT', 'CBOE', 'CBRE', 'CBS', 'CELG', 'CNC', 'CNP', 'CTL',
            'CERN', 'CF', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'XEC', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG',
            'CTXS', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL', 'CMCSA', 'CMA', 'CAG', 'CXO', 'COP', 'ED', 'STZ', 'COO',
            'GLW', 'COST', 'COTY', 'CCI', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE', 'DAL', 'XRAY', 'DVN',
            'DLR', 'DFS', 'DISCA', 'DISCK', 'DISH', 'DG', 'DLTR', 'D', 'DOV', 'DWDP', 'DPS', 'DTE', 'DRE', 'DUK',
            'DXC', 'ETFC', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'EMR', 'ETR', 'EVHC', 'EOG', 'EQT', 'EFX',
            'EQIX', 'EQR', 'ESS', 'EL', 'ES', 'RE', 'EXC', 'EXPE', 'EXPD', 'ESRX', 'EXR', 'XOM', 'FFIV', 'FB', 'FAST',
            'FRT', 'FDX', 'FIS', 'FITB', 'FE', 'FISV', 'FLIR', 'FLS', 'FLR', 'FMC', 'FL', 'F', 'FTV', 'FBHS', 'BEN',
            'FCX', 'GPS', 'GRMN', 'IT', 'GD', 'GE', 'GGP', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GS', 'GT', 'GWW', 'HAL',
            'HBI', 'HOG', 'HRS', 'HIG', 'HAS', 'HCA', 'HCP', 'HP', 'HSIC', 'HSY', 'HES', 'HPE', 'HLT', 'HOLX', 'HD',
            'HON', 'HRL', 'HST', 'HPQ', 'HUM', 'HBAN', 'HII', 'IDXX', 'INFO', 'ITW', 'ILMN', 'IR', 'INTC', 'ICE',
            'IBM', 'INCY', 'IP', 'IPG', 'IFF', 'INTU', 'ISRG', 'IVZ', 'IPGP', 'IQV', 'IRM', 'JEC', 'JBHT', 'SJM',
            'JNJ', 'JCI', 'JPM', 'JNPR', 'KSU', 'K', 'KEY', 'KMB', 'KIM', 'KMI', 'KLAC', 'KSS', 'KHC', 'KR', 'LB',
            'LLL', 'LH', 'LRCX', 'LEG', 'LEN', 'LUK', 'LLY', 'LNC', 'LKQ', 'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MAC', 'M',
            'MRO', 'MPC', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MAT', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'MET', 'MTD',
            'MGM', 'KORS', 'MCHP', 'MU', 'MSFT', 'MAA', 'MHK', 'TAP', 'MDLZ', 'MON', 'MNST', 'MCO', 'MS', 'MOS', 'MSI',
            'MSCI', 'MYL', 'NDAQ', 'NOV', 'NAVI', 'NKTR', 'NTAP', 'NFLX', 'NWL', 'NFX', 'NEM', 'NWSA', 'NWS', 'NEE',
            'NLSN', 'NKE', 'NI', 'NBL', 'JWN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 'ORLY', 'OXY',
            'OMC', 'OKE', 'ORCL', 'PCAR', 'PKG', 'PH', 'PAYX', 'PYPL', 'PNR', 'PBCT', 'PEP', 'PKI', 'PRGO', 'PFE',
            'PCG', 'PM', 'PSX', 'PNW', 'PXD', 'PNC', 'RL', 'PPG', 'PPL', 'PX', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG',
            'PSA', 'PHM', 'PVH', 'QRVO', 'PWR', 'QCOM', 'DGX', 'RRC', 'RJF', 'RTN', 'O', 'RHT', 'REG', 'REGN', 'RF',
            'RSG', 'RMD', 'RHI', 'ROK', 'COL', 'ROP', 'ROST', 'RCL', 'CRM', 'SBAC', 'SCG', 'SLB', 'STX', 'SEE', 'SRE',
            'SHW', 'SPG', 'SWKS', 'SLG', 'SNA', 'SO', 'LUV', 'SPGI', 'SWK', 'SBUX', 'STT', 'SRCL', 'SYK', 'STI',
            'SIVB', 'SYMC', 'SYF', 'SNPS', 'SYY', 'TROW', 'TTWO', 'TPR', 'TGT', 'TEL', 'FTI', 'TXN', 'TXT', 'TMO',
            'TIF', 'TWX', 'TJX', 'TMK', 'TSS', 'TSCO', 'TDG', 'TRV', 'TRIP', 'FOXA', 'FOX', 'TSN', 'UDR', 'ULTA',
            'USB', 'UAA', 'UA', 'UNP', 'UAL', 'UNH', 'UPS', 'URI', 'UTX', 'UHS', 'UNM', 'VFC', 'VLO', 'VAR', 'VTR',
            'VRSN', 'VRSK', 'VZ', 'VRTX', 'VIAB', 'V', 'VNO', 'VMC', 'WMT', 'WBA', 'DIS', 'WM', 'WAT', 'WEC', 'WFC',
            'WELL', 'WDC', 'WU', 'WRK', 'WY', 'WHR', 'WMB', 'WLTW', 'WYN', 'WYNN', 'XEL', 'XRX', 'XLNX', 'XL', 'XYL',
            'YUM', 'ZBH', 'ZION', 'ZTS']


client_config = get_client_config(private_key_path=PRIVATE_KEY_PATH, tiger_id=TIGER_ID, account=ACCOUNT,
                                  sandbox_debug=True)
quote_client = QuoteClient(client_config)
trade_client = TradeClient(client_config)


# 初始化 log 模块
logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(message)s',
                    filename=LOG_PATH,
                    filemode='a')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def recorder(func):
    @wraps(func)
    def do_log(*args, **kwargs):
        try:
            log.info('func name is %s, args are %s, kwars are %s' % (func.__name__, args, kwargs))
            return func(*args, **kwargs)
        except Exception as e:
            log.warning(e, exc_info=True)
    return do_log


@recorder
def get_daily_close(symbols):
    """获取日级收盘价
    :param symbols:证券代码列表
    """
    i = 0
    price = pd.DataFrame()
    while i <= len(symbols):
        batch = symbols[i:i+50]
        i += 50
        temp = quote_client.get_bars(symbols=batch)
        temp['time'] = temp['time'].map(lambda x: datetime.fromtimestamp(x/1000))
        price = price.append(temp)
        log.info('batch number is %s' % i)

    return price


@recorder
def calculate_indicators(price):
    """计算用于交易的指标: 昨收价对于 EMA 的偏离值
    :return:Series，index 是 symbol， value 是指标的值
    """
    # 先处理数据结构, index 是时间， column 是股票代码
    price = price[['symbol', 'time', 'close']]
    price.set_index('time', inplace=True)
    close = price.pivot(columns='symbol')
    close.columns = close.columns.droplevel()
    # 计算调仓使用的技术指标
    ema = close.apply(lambda x: ta.EMA(x.values, timeperiod=10))
    indicator = 1 - (ema.iloc[-1, :]/close.iloc[-1, :])
    return indicator


@recorder
def get_optimal_portfolio(indicator, holding_num):
    """计算市值加权的目标调仓权重
    """

    target_stock = indicator.sort_values()[:holding_num]
    log.info('target stock is %s, target num is %s' % (target_stock, holding_num))
    market_cap = quote_client.get_financial_daily(symbols=list(target_stock.index),
                                                  market=Market.US,
                                                  fields=[Valuation.market_capitalization],
                                                  begin_date=(datetime.now()-timedelta(days=4)).timestamp()*1000,
                                                  end_date=datetime.now().timestamp()*1000)

    market_cap = market_cap.sort_values('date', ascending=False).drop_duplicates(subset='symbol', keep='first')
    log.info('market cap is %s' % market_cap)
    market_cap.set_index('symbol', inplace=True)
    market_cap = market_cap['value']
    return market_cap/market_cap.sum()


@recorder
def batch_get_stock_briefs(symbols):
    i = 0
    briefs = pd.DataFrame()
    while i <= len(symbols):
        batch = symbols[i:i+50]
        i += 50
        temp = quote_client.get_stock_briefs(symbols=batch)
        briefs = briefs.append(temp)
        log.info('batch number is %s' % i)

    return briefs


@recorder
def execute(target_weight):
    """调仓，并返回结果
    """
    positions = trade_client.get_positions(account=ACCOUNT, market=Market.US)
    # 当前持仓
    current_holdings = {}
    # 卖单
    sell_orders = {}
    # 买单
    buy_orders = {}

    for i in positions:
        current_holdings.update({i.contract.symbol: i.quantity})
    if len(current_holdings.keys()) != 0:
        # 先卖出当前持仓中不在目标调仓列表中的股票
        briefs = batch_get_stock_briefs(symbols=list(current_holdings.keys()))
        briefs.set_index('symbol', inplace=True)
        latest_price = briefs.latest_price
        current_holdings = pd.Series(current_holdings)

        liquidation_list = set(current_holdings.index) - set(target_weight.index)
        log.info('executing sell orders ,latest_price are %s' % latest_price)

        for symbol in liquidation_list:
            contract = stock_contract(symbol, currency='USD')
            quantity = current_holdings[symbol]
            limit_price = round(latest_price[symbol], 2)
            order = limit_order(account=ACCOUNT,
                                contract=contract,
                                action='SELL' if quantity > 0 else 'BUY',
                                quantity=abs(int(quantity)),
                                limit_price=limit_price)
            try:
                trade_client.place_order(order)
                sell_orders.update({order.id: order})
            except Exception:
                log.error('Faild to get result, contract: %s, limit_price: %s' % (contract, limit_price), exc_info=True)
        # 轮询卖单的执行情况
        retry_time = 0
        while retry_time < MAX_RETRY and len(sell_orders.keys()) != 0:
            filled_orders = trade_client.get_filled_orders(account=ACCOUNT,
                                                           sec_type=SecurityType.STK,
                                                           market=Market.US,
                                                           start_time=(datetime.now()-timedelta(days=1)).timestamp()*1000,
                                                           end_time=datetime.now().timestamp()*1000)
            for order in filled_orders:
                sell_orders.pop(order.id, None)

            retry_time += 1
            sleep(20)
            log.info('retry time %s, remaining orders %s' % (retry_time, len(sell_orders.keys())))
        else:
            # 取消所有open 状态的订单
            for id in sell_orders.keys():
                trade_client.cancel_order(account=ACCOUNT, id=id)
        sleep(2)

    # 下买单
    # 先获取 security Segment 的账户信息（标准与模拟账户都类似， 环球账户不同）
    assets = trade_client.get_assets(account=ACCOUNT)[0].segments['S']
    # 按照当前的可用现金下单（无杠杆）
    cash = assets.cash
    if cash < 0:
        return
    target_value = cash * target_weight
    briefs = batch_get_stock_briefs(symbols=list(target_value.index))
    briefs.set_index('symbol', inplace=True)
    latest_price = briefs.latest_price
    log.info('cash is %s, target_value is %s' % (cash, target_value))
    for symbol in target_value.index:
        contract = stock_contract(symbol, 'USD')
        limit_price = round(latest_price[symbol], 2)  # 不同合约对下单价格的变动单位不同
        order = limit_order(account=ACCOUNT,
                            contract=contract,
                            action='BUY',
                            quantity=int(target_value[symbol]/latest_price[symbol]),
                            limit_price=limit_price)
        try:
            trade_client.place_order(order)
            buy_orders.update({order.id: order})
        except Exception:
            log.error('Faild to get result, contract: %s, limit_price: %s' % (contract, limit_price), exc_info=True)

    # 检查更新订单的状态
    for  id in buy_orders.keys():
        order = trade_client.get_order(account=ACCOUNT, id=id)
        buy_orders[id] = order
    log.info('buy order status %s' % buy_orders)


def run():
    price = get_daily_close(symbols=UNIVERSE)
    indicator = calculate_indicators(price)
    optimal_portfolio = get_optimal_portfolio(indicator, 10)
    execute(optimal_portfolio)


if __name__ == '__main__':
    run()
