import os
import time
import pytz
import logbook
import sys
from datetime import datetime, timedelta

ENGINE_PATH = os.path.dirname(os.path.realpath(__file__))
RUN_PATH = os.path.abspath(os.path.join(ENGINE_PATH, os.pardir, os.pardir, os.pardir))
sys.path.insert(0, RUN_PATH)

from tigeropen.trade.domain.position import Position
from tigeropen.examples.tinyquant.data import minute_bar_util, StockQuote as Data
from tigeropen.examples.tinyquant.strategy import CompatibleStrategy, TickStrategy
from tigeropen.examples.tinyquant.client import client_config, push_client, trade_client, quote_client, \
    global_context
import tigeropen.examples.tinyquant.setting as setting


logbook.set_datetime_format("local")
logbook.StreamHandler(sys.stdout,
                      format_string='[{record.time:%Y-%m-%d %H:%M:%S.%f%z}] {record.level_name}: {record.channel}:{record.lineno}: {record.message}').push_application()
logger = logbook.Logger('[engine]')


# ============= set symbols ===================
subscribe_symbols = global_context.subscribed_symbols


timezone = pytz.timezone(setting.MARKET.TIMEZONE)
IS_EVENT_TRIGGER = setting.EVENT_TRIGGER


def on_query_subscribed_quote(symbols, focus_keys, limit, used):
    logger.debug('{symbols}, {focus_keys}, {limit}, {used}'.format(
        symbols=symbols, focus_keys=focus_keys, limit=limit, used=used))
    unsubscribe_symbols = set(symbols) - subscribe_symbols
    if unsubscribe_symbols:
        logger.debug(unsubscribe_symbols)
        # push_client.unsubscribe_quote(symbols=unsubscribe_symbols)

    if IS_EVENT_TRIGGER:
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
    push_client.unsubscribe_quote(symbols=subscribe_symbols)
    push_client.disconnect()


def add_order(order):
    global_context.order_manager[order.order_id] = order
    global_context.active_order_manager[order.order_id] = global_context.order_manager[order.order_id]


# ============= strategy with event trigger ===================
def on_quote_changed_event_trigger(symbol, items, hour_trading):
    if hour_trading:
        return
    if symbol in subscribe_symbols:
        if setting.MARKET.name != 'HK' and setting.MARKET.name != 'US':
            minute_bar_util.on_data(symbol, items)


# ============= subscribe info ===================
def on_asset_changed(account, items):
    # DU575569 [('equity_with_loan', 776871.76), ('gross_position_value', 349025.33), ('excess_liquidity', 653692.01),
    # ('available_funds', 648601.77), ('initial_margin_requirement', 128269.99), ('buying_power', 4324011.82),
    # ('cash', 476021.26), ('net_liquidation', 776871.76), ('maintenance_margin_requirement', 123179.75)]
    logger.debug('{account}, {items}'.format(account=account, items=items))
    ret_account = dict(items)
    curr_account = global_context.asset_manager
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
    logger.debug('{account}, {items}'.format(account=account, items=items))
    ret_position = dict(items)
    symbol = ret_position.get('origin_symbol')
    if symbol in global_context.contract_map:
        curr_position = global_context.position_manager.get(symbol)
        if curr_position:
            curr_position.quantity = ret_position.get('quantity')
            curr_position.average_cost = ret_position.get('average_cost')
            curr_position.market_price = ret_position.get('market_price')
            curr_position.market_value = ret_position.get('market_value')
            curr_position.unrealized_pnl = ret_position.get('unrealized_pnl')
            curr_position.realized_pnl = ret_position.get('realized_pnl')
        else:
            global_context.position_manager[symbol] = Position(account=global_context.account,
                                                               contract=global_context.contract_map[symbol],
                                                               quantity=ret_position.get('quantity'),
                                                               average_cost=ret_position.get('average_cost'),
                                                               market_price=ret_position.get('market_price'),
                                                               market_value=ret_position.get('market_value'),
                                                               realized_pnl=ret_position.get('realized_pnl'),
                                                               unrealized_pnl=ret_position.get('unrealized_pnl'))


def on_order_changed(account, items):
    logger.debug('{account}, {items}'.format(account=account, items=items))
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
            global_context.active_order_manager[curr_order.order_id] = None
            del global_context.active_order_manager[curr_order.order_id]


def cancel_all_open_orders():
    curr_orders = trade_client.get_open_orders()
    for curr_order in curr_orders:
        try:
            trade_client.cancel_order(order_id=curr_order.order_id)
        except Exception as e:
            logger.error(e)


def asset_initialize():
    assets = trade_client.get_assets()
    if assets:
        global_context.asset_manager = assets[0]
    else:
        raise Exception('No assets')


def position_initialize():
    positions = trade_client.get_positions()
    global_context.position_manager = {position.contract.symbol: position for position in positions}


def order_initialize():
    global_context.order_manager = {}
    global_context.active_order_manager = {}


def contract_initialize():
    for symbol in subscribe_symbols:
        curr_contracts = trade_client.get_contracts(symbol,
                                                   sec_type=global_context.security_type_map.get(symbol),
                                                   currency=global_context.currency_map.get(symbol))
        if not curr_contracts:
            raise Exception('Can not get contracts')
        global_context.contract_map[symbol] = curr_contracts[0]


if setting.EVENT_TRIGGER:
    compatible_strategy = CompatibleStrategy(push_client=push_client, trade_client=trade_client, quote_client=quote_client, context=global_context)

    def strategy_initialize():
        compatible_strategy.initialize()
        global_context.load()

    def before_trading_start(data):
        compatible_strategy.before_trading_start(data=data)

    def handle_data(data):
        compatible_strategy.handle_data(data=data)
        global_context.store()

    def run_schedule_func(data):
        if hasattr(global_context, 'schedule_function'):
            global_context.schedule_function.run(data=data)
            global_context.store()

    def dump():
        pass

else:
    strategy = TickStrategy(push_client=push_client, trade_client=trade_client, quote_client=quote_client, context=global_context)

    def on_quote_changed(symbol, items, hour_trading):
        if symbol in subscribe_symbols:
            strategy.on_ticker(symbol_str=symbol, items=items, hour_trading=hour_trading)

    def strategy_initialize():
        strategy.initialize()
        global_context.load()

    def before_trading_start(data):
        strategy.before_trading_start(data=data)

    def handle_data(data):
        pass

    def run_schedule_func(data):
        pass

    def dump():
        strategy.dump()
        global_context.store()


if __name__ == '__main__':
    asset_initialize()
    position_initialize()
    order_initialize()

    strategy_initialize()
    curr_datetime = datetime.now().astimezone(timezone)
    before_trading_start(Data(curr_datetime))

    push_client.connect(client_config.tiger_id, client_config.private_key)
    subscribe_initialize()
    contract_initialize()

    try:
        if IS_EVENT_TRIGGER:
            OPEN_TIME = setting.MARKET.OPEN_TIME
            CLOSE_TIME = setting.MARKET.CLOSE_TIME
            SYSTEM_DELAY = setting.SYSTEM_DELAY

            open_time = datetime.strptime(OPEN_TIME, '%H:%M:%S').replace(tzinfo=timezone).time().replace(
                second=SYSTEM_DELAY)
            close_time = datetime.strptime(CLOSE_TIME, '%H:%M:%S').time()

            if setting.FREQUENCY == 'minute':
                today = datetime.now(tz=timezone).date()

                curr_time = (datetime.now(tz=timezone).replace(second=SYSTEM_DELAY, microsecond=0) + timedelta(minutes=2)).time()
                next_bar_time = max(curr_time, open_time)

                if setting.MARKET.LUNCH_BREAK_START_TIME:
                    lunch_break_start = datetime.strptime(setting.MARKET.LUNCH_BREAK_START_TIME, '%H:%M:%S').time()
                    lunch_break_end = datetime.strptime(setting.MARKET.LUNCH_BREAK_END_TIME, '%H:%M:%S').time()
                    while True:
                        curr_time = datetime.now(tz=timezone).time()
                        if next_bar_time >= close_time:
                            logger.debug('event trigger finished')
                            break
                        elif lunch_break_start < next_bar_time < lunch_break_end:
                            curr_datetime = timezone.localize(datetime.combine(today, next_bar_time) - timedelta(minutes=1))
                            next_bar_time = (curr_datetime + timedelta(minutes=2)).time()
                            time.sleep(1)
                        elif next_bar_time <= curr_time:
                            curr_datetime = timezone.localize(datetime.combine(today, next_bar_time) - timedelta(minutes=1))
                            curr_data = Data(curr_datetime)

                            logger.debug(f'next bar time:{curr_datetime}')
                            run_schedule_func(curr_data)
                            handle_data(curr_data)
                            next_bar_time = (curr_datetime + timedelta(minutes=2)).time()
                        else:
                            time.sleep(1)
                else:
                    while True:
                        curr_time = datetime.now(tz=timezone).time()
                        if next_bar_time >= close_time:
                            logger.debug('event trigger finished')
                            break
                        elif next_bar_time <= curr_time:
                            curr_datetime = timezone.localize(datetime.combine(today, next_bar_time) - timedelta(minutes=1))
                            curr_data = Data(curr_datetime)
                            run_schedule_func(curr_data)
                            handle_data(curr_data)
                            next_bar_time = (curr_datetime + timedelta(minutes=2)).time()
                        else:
                            time.sleep(1)
            elif setting.FREQUENCY == 'daily':
                today = datetime.now(tz=timezone).date()
                while True:
                    curr_datetime = datetime.now(tz=timezone)
                    if curr_datetime.time() >= close_time:
                        logger.debug('daily event trigger finished')
                    elif curr_datetime.time() >= open_time:
                        curr_data = Data(curr_datetime)
                        run_schedule_func(curr_data)
                        handle_data(curr_data)
                        time.sleep(120)
                        break
                    else:
                        time.sleep(1)
        else:
            while True:
                time.sleep(600)
    except (KeyboardInterrupt, SystemExit):
        logger.debug('keyboard interrupt, system exit')
    unsubscribe_process()
    dump()
