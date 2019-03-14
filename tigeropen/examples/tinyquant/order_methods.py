from functools import partial
from .client import trade_client, global_context, quote_client

create_order = partial(trade_client.create_order, account=global_context.account)
place_order = trade_client.place_order
get_open_orders = partial(trade_client.get_open_orders, account=global_context.account)


def _order(contract, action, order_type, quantity, limit_price=None, aux_price=None,
           trail_stop_price=None, trailing_percent=None, percent_offset=None, time_in_force=None,
           outside_rth=None):
    order_obj = create_order(contract=contract, action=action, order_type=order_type, quantity=quantity,
                             limit_price=limit_price, aux_price=aux_price, trail_stop_price=trail_stop_price,
                             trailing_percent=trailing_percent, percent_offset=percent_offset,
                             time_in_force=time_in_force, outside_rth=outside_rth)
    if order_obj and place_order(order_obj):
        return order_obj.order_id
    return False


def order(asset, amount, style='market', limit_price=0.0):
    if amount == 0:
        return
    action = 'BUY' if amount > 0 else 'SELL'
    contract = global_context.contract_map.get(asset)
    if style == 'market':
        return _order(contract=contract, action=action, order_type='MKT', quantity=abs(amount))
    elif style == 'limit' and limit_price > 0:
        return _order(contract=contract, action=action, order_type='LMT', quantity=abs(amount), limit_price=limit_price)


def order_value(asset, value, style='market', limit_price=0.0):
    action = 'BUY' if value > 0 else 'SELL'
    contract = global_context.contract_map.get(asset)
    if style == 'market':
        curr_close = quote_client.get_stock_briefs(symbols=[asset]).latest_price.iloc[0]
        if curr_close is None:
            raise Exception('no price data')
        return _order(contract=contract, action=action, order_type='MKT', quantity=abs(value) // curr_close)
    elif style == 'limit' and limit_price > 0:
        return _order(contract=contract, action=action, order_type='LMT', quantity=abs(value) // limit_price, limit_price=limit_price)


def get_order(order_id):
    return trade_client.get_order(account=global_context.account, order_id=order_id)


def cancel_order(order_id):
    return trade_client.cancel_order(account=global_context.account, order_id=order_id)


def order_percent(asset, percent, style='market', limit_price=0.0):
    raise NotImplemented
    # portfolio_value = global_context.asset_manager.summary.gross_position_value + global_context.asset_manager.summary.available_funds
    # value = portfolio_value * percent
    # return order_value(asset, value, style, limit_price)


def order_target(asset, amount, style='market', limit_price=0.0):
    raise NotImplemented
    # curr_position = global_context.position_manager.get(asset)
    # if curr_position:
    #     if curr_position.quantity != amount:
    #         diff_amount = amount - curr_position.quantity
    #         return order(asset, diff_amount, style, limit_price)
    # else:
    #     return order(asset, amount, style, limit_price)


def order_target_value(asset, amount, style='market', limit_price=0.0):
    raise NotImplemented
    # if style == 'market':
    #     #curr_price = minute_bar_util.get_curr_bar(assets=asset,  fields='close')
    #     quote_client.get_stock_briefs(symbols=[asset]).latest_price.iloc[0]
    # else:
    #     curr_price = limit_price
    # if curr_price > 0:
    #     target_qty = abs(amount) // curr_price
    #     return order_target(asset, target_qty if amount >= 0 else (-target_qty), style, limit_price)


def order_target_percent(asset, percent, style='market', limit_price=0.0):
    raise NotImplemented
    # target_value = global_context.asset_manager.summary.gross_position_value + global_context.asset_manager.summary.available_funds * percent
    # return order_target_value(asset, target_value, style, limit_price)


