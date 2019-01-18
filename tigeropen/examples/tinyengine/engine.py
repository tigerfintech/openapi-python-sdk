import time
import logging
import pytz
from datetime import datetime, timedelta

from tigeropen.trade.trade_client import TradeClient
from tigeropen.push.push_client import PushClient
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.domain.position import Position

from tigeropen.examples.client_config import get_client_config
from tigeropen.examples.tinyengine.data import Data, minute_bar_util
from tigeropen.examples.tinyengine.context import global_context
from tigeropen.examples.tinyengine.strategy import Strategy


# ============= initialize engine vars ===================
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', filemode='a', )
logger = logging.getLogger('TigerOpenApi')

# ============= get client config ===================
client_config = get_client_config()
account_id = client_config.account


# ============= initialize push client & trade_client & quote_client ===================
protocol, host, port = client_config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))
trade_client = TradeClient(client_config, logger=logger)
quote_client = QuoteClient(client_config, logger=logger)


strategy = Strategy(push_client=push_client, trade_client=trade_client, quote_client=quote_client, context=global_context)

# ============= set symbols ===================
subscribe_symbols = set(strategy.symbol_market_map.keys())
symbol_market_map = strategy.symbol_market_map
# ============= event trigger config ===================
OPEN_TIME = strategy.open_time
CLOSE_TIME = strategy.close_time
TIME_ZONE = strategy.time_zone
UTC = 'UTC'
event_trigger = strategy.event_trigger


def on_query_subscribed_quote(symbols, focus_keys, limit, used):
    print(symbols, focus_keys, limit, used)
    unsubscribe_symbols = set(symbols) - subscribe_symbols
    if unsubscribe_symbols:
        push_client.unsubscribe_quote(symbols=unsubscribe_symbols)

    if event_trigger:
        push_client.quote_changed = on_quote_changed_event_trigger
    else:
        push_client.quote_changed = on_quote_changed
    push_client.subscribe_quote(subscribe_symbols)


def subscribe_initialize():
    push_client.subscribed_symbols = on_query_subscribed_quote
    push_client.query_subscribed_quote()

    push_client.asset_changed = on_asset_changed
    push_client.position_changed = on_position_changed
    push_client.order_changed = on_order_changed

    push_client.subscribe_asset()
    push_client.subscribe_position()
    push_client.subscribe_order()


def unsubscribe_process():
    push_client.unsubscribe_order()
    push_client.unsubscribe_position()
    push_client.unsubscribe_asset()
    push_client.unsubscribe_quote(subscribe_symbols)
    push_client.disconnect()


def add_order(order):
    global_context.order_manager[order.order_id] = order
    global_context.active_order_manager[order.order_id] = order_manager[order.order_id]


# ============= strategy with market trigger ===================
def on_quote_changed(symbol, items, hour_trading):
    strategy.on_ticker(symbol, items, hour_trading)
    #
    # global first
    # if first:
    #     contract = global_context.contract_map.get(symbol)
    #     if contract:
    #         price_dict = dict(items)
    #         latest_price = price_dict.get('latest_price') + 1
    #         order = trade_client.create_order(account_id, contract, 'BUY', 'LMT', 100, limit_price=latest_price)
    #         trade_client.place_order(order)
    #         first = False
    #         add_order(order)
    # if global_context.active_order_manager:
    #     for order_id in global_context.active_order_manager.keys():
    #         print(trade_client.get_order(order_id=order_id))


# ============= strategy with event trigger ===================
def on_quote_changed_event_trigger(symbol, items, hour_trading):
    if hour_trading:
        return
    print(symbol, items, hour_trading)
    minute_bar_util.on_data(symbol, items)


def handle_data(data):
    strategy.on_minute_bar(data)


# ============= subscribe info ===================
def on_asset_changed(account, items):
    # DU575569 [('equity_with_loan', 776871.76), ('gross_position_value', 349025.33), ('excess_liquidity', 653692.01),
    # ('available_funds', 648601.77), ('initial_margin_requirement', 128269.99), ('buying_power', 4324011.82),
    # ('cash', 476021.26), ('net_liquidation', 776871.76), ('maintenance_margin_requirement', 123179.75)]
    print(account, items)
    ret_account = dict(items)
    curr_account = global_context.asset_manager.get(account_id)
    if curr_account:
        curr_account.summary.equity_with_loan = ret_account.get('equity_with_loan')
        curr_account.summary.gross_position_value = ret_account.get('gross_position_value')
        curr_account.summary.excess_liquidity = ret_account.get('excess_liquidity')
        curr_account.summary.available_funds = ret_account.get('available_funds')
        curr_account.summary.initial_margin_requirement = ret_account.get('initial_margin_requirement')
        curr_account.summary.buying_power = ret_account.get('buying_power')
        curr_account.summary.cash = ret_account.get('cash')
        curr_account.summary.net_liquidation = ret_account.get('net_liquidation')
        curr_account.summary.maintenance_margin_requirement = ret_account.get('maintenance_margin_requirement')


def on_position_changed(account, items):
    # DU575569 [('market_price', 23.37599945), ('market_value', 9350.4), ('sec_type', 'STK'),
    # ('origin_symbol', '600053'), ('unrealized_pnl', -101.62), ('quantity', 400.0), ('average_cost', 23.630052)]
    print(account, items)
    ret_position = dict(items)
    symbol = ret_position.get('origin_symbol')
    curr_position = global_context.position_manager.get(symbol)
    if curr_position:
        curr_position.quantity = ret_position.get('quantity')
        curr_position.average_cost = ret_position.get('average_cost')
        curr_position.market_price = ret_position.get('market_price')
        curr_position.market_value = ret_position.get('market_value')
        curr_position.unrealized_pnl = ret_position.get('unrealized_pnl')
        curr_position.realized_pnl = ret_position.get('realized_pnl')
    else:
        global_context.position_manager[symbol] = Position(account=account_id,
                                                           contract=global_context.contract_map[symbol],
                                                           quantity=ret_position.get('quantity'),
                                                           average_cost=ret_position.get('average_cost'),
                                                           market_price=ret_position.get('market_price'),
                                                           market_value=ret_position.get('market_value'),
                                                           realized_pnl=ret_position.get('realized_pnl'),
                                                           unrealized_pnl=ret_position.get('unrealized_pnl'))


def on_order_changed(account, items):
    print(account, items)
    # DU575569 [('order_type', 'LMT'), ('order_id', 1000051287), ('sec_type', 'STK'),
    # ('filled', 100), ('origin_symbol', '000513'), ('quantity', 100), ('order_time', 1547620277910),
    # ('time_in_force', 'DAY'), ('limit_price', 27.81), ('last_fill_price', 0.0), ('outside_rth', True),
    # ('avg_fill_price', 26.88), ('trade_time', 1547620279026)]
    ret_order = dict(items)
    curr_order = global_context.order_manager.get(ret_order.get('order_id'))
    if curr_order:
        curr_order.filled = ret_order.get('filled')
        curr_order.order_time = ret_order.get('order_time')
        curr_order.last_fill_price = ret_order.get('last_fill_price')
        curr_order.avg_fill_price = ret_order.get('avg_fill_price')
        curr_order.trade_time = ret_order.get('trade_time')
        curr_order.reason = ret_order.get('reason')
        curr_order.realized_pnl = ret_order.get('realized_pnl')
        curr_order.commission = ret_order.get('commission')

        if curr_order.remaining <= 0:
            active_order_manager[curr_order.order_id] = None
            del active_order_manager[curr_order.order_id]


def cancel_all_open_orders():
    curr_orders = trade_client.get_open_orders()
    for curr_order in curr_orders:
        try:
            trade_client.cancel_order(order_id=curr_order.order_id)
        except Exception as e:
            print(e)


def asset_initialize():
    accounts = trade_client.get_managed_accounts()
    assets = trade_client.get_assets()

    global_context.asset_manager = {accounts[0].account: assets[0]}


def position_initialize():
    positions = trade_client.get_positions()
    global_context.position_manager = {position.contract.symbol: position for position in positions}


def order_initialize():
    cancel_all_open_orders()
    global order_manager
    order_manager = {}

    global active_order_manager
    active_order_manager = {}


def contract_initialize():
    for symbol in subscribe_symbols:
        curr_contract = trade_client.get_contracts(symbol, sec_type=symbol_market_map.get('security'),
                                                   currency=symbol_market_map.get('currency'))[0]
        global_context.contract_map[symbol] = curr_contract


def before_trading_start():
    strategy.before_trading_start()


def dump():
    strategy.dump()


if __name__ == '__main__':
    asset_initialize()
    position_initialize()
    order_initialize()
    contract_initialize()

    before_trading_start()

    push_client.connect(client_config.tiger_id, client_config.private_key)
    subscribe_initialize()

    try:
        if event_trigger:
            curr_timezone = pytz.timezone(TIME_ZONE)
            today = datetime.now().astimezone(curr_timezone).date()

            open_time = datetime.strptime(str(OPEN_TIME), '%H%M%S').time()
            close_time = datetime.strptime(str(CLOSE_TIME), '%H%M%S').time()

            one_minute = timedelta(minutes=1)
            curr_time = (datetime.now().astimezone(curr_timezone).replace(second=0, microsecond=0) + one_minute).time()
            open_time = max(curr_time, open_time)

            while True:
                curr_time = datetime.now().astimezone(curr_timezone).time()
                if open_time >= close_time:
                    print('event trigger finished')
                    break
                elif curr_time >= open_time:
                    curr_data = Data(datetime.combine(today, open_time, curr_timezone))
                    minute_bar_util.set_data(curr_data)
                    handle_data(curr_data)

                    open_time = open_time.replace(minute=open_time.minute + 1)
                else:
                    time.sleep(1)
        else:
            while True:
                time.sleep(600)
    except (KeyboardInterrupt, SystemExit):
        print('keyboard interrupt, system exit')
    cancel_all_open_orders()
    unsubscribe_process()
    dump()
