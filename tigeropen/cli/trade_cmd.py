# -*- coding: utf-8 -*-
"""
Trade commands: order (list/get/place/preview/modify/cancel), position, transaction.
"""
import click

from tigeropen.cli.client_factory import get_trade_client
from tigeropen.cli.formatting import render, to_records, is_empty


@click.group('trade')
def trade():
    """Trading operations (orders, positions, transactions)."""
    pass


# --- Order subgroup ---

@trade.group('order')
def order():
    """Order management."""
    pass


@order.command('list')
@click.option('--status', default=None, help='Filter by status (Filled/Cancelled/Submitted).')
@click.option('--symbol', default=None, help='Filter by symbol.')
@click.option('--market', type=click.Choice(['US', 'HK', 'ALL'], case_sensitive=False),
              default='ALL', help='Market filter.')
@click.option('--limit', type=int, default=100, help='Max number of orders.')
@click.pass_context
def order_list(ctx, status, symbol, market, limit):
    """List orders."""
    client = get_trade_client(ctx.obj)
    kwargs = {'market': market, 'limit': limit}
    if status:
        kwargs['states'] = [status]
    if symbol:
        kwargs['symbol'] = symbol
    orders = client.get_orders(**kwargs)
    if not is_empty(orders):
        data = to_records(orders)
        render(data, ctx.obj['format'])
    else:
        click.echo('No orders found.')


@order.command('get')
@click.argument('order_id', type=int)
@click.pass_context
def order_get(ctx, order_id):
    """Get order details by ID."""
    client = get_trade_client(ctx.obj)
    order = client.get_order(id=order_id)
    if order:
        data = order.to_dict() if hasattr(order, 'to_dict') else order.__dict__
        render(data, ctx.obj['format'])
    else:
        click.echo(f'Order {order_id} not found.')


@order.command('cancel')
@click.argument('order_id', type=int)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt.')
@click.pass_context
def order_cancel(ctx, order_id, yes):
    """Cancel an order."""
    if not yes:
        click.confirm(f'Cancel order {order_id}?', abort=True)
    client = get_trade_client(ctx.obj)
    result = client.cancel_order(id=order_id)
    if result:
        click.echo(f'Order {order_id} cancelled.')
    else:
        click.echo(f'Cancel request sent for order {order_id}.')


@order.command('preview')
@click.option('--symbol', required=True, help='Stock symbol.')
@click.option('--action', type=click.Choice(['BUY', 'SELL'], case_sensitive=False), required=True)
@click.option('--order-type', type=click.Choice(['LMT', 'MKT', 'STP', 'STP_LMT'], case_sensitive=False),
              default='LMT', help='Order type.')
@click.option('--quantity', type=int, required=True, help='Order quantity.')
@click.option('--limit-price', type=float, default=None, help='Limit price.')
@click.option('--sec-type', type=click.Choice(['STK', 'OPT', 'FUT'], case_sensitive=False),
              default='STK', help='Security type.')
@click.pass_context
def order_preview(ctx, symbol, action, order_type, quantity, limit_price, sec_type):
    """Preview an order before placing."""
    client = get_trade_client(ctx.obj)
    from tigeropen.trade.domain.order import Order
    contract = _make_contract(client, symbol, sec_type)
    order = Order(account=client._account, contract=contract, action=action,
                  order_type=order_type, quantity=quantity, limit_price=limit_price)
    result = client.preview_order(order)
    render(result, ctx.obj['format'])


@order.command('place')
@click.option('--symbol', required=True, help='Stock symbol.')
@click.option('--action', type=click.Choice(['BUY', 'SELL'], case_sensitive=False), required=True)
@click.option('--order-type', type=click.Choice(['LMT', 'MKT', 'STP', 'STP_LMT'], case_sensitive=False),
              default='LMT', help='Order type.')
@click.option('--quantity', type=int, required=True, help='Order quantity.')
@click.option('--limit-price', type=float, default=None, help='Limit price.')
@click.option('--sec-type', type=click.Choice(['STK', 'OPT', 'FUT'], case_sensitive=False),
              default='STK', help='Security type.')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt.')
@click.pass_context
def order_place(ctx, symbol, action, order_type, quantity, limit_price, sec_type, yes):
    """Place an order."""
    client = get_trade_client(ctx.obj)
    from tigeropen.trade.domain.order import Order
    contract = _make_contract(client, symbol, sec_type)
    order = Order(account=client._account, contract=contract, action=action,
                  order_type=order_type, quantity=quantity, limit_price=limit_price)
    if not yes:
        click.echo(f'Order: {action} {quantity} {symbol} @ {order_type} {limit_price or "MKT"}')
        click.confirm('Confirm order placement?', abort=True)
    result = client.place_order(order)
    if result:
        click.echo(f'Order placed. ID: {result}')
    else:
        click.echo('Order placement failed: no ID returned.')


def _make_contract(client, symbol, sec_type='STK'):
    """Create a contract object for the given symbol."""
    contracts = client.get_contracts(symbol, sec_type=sec_type)
    if contracts:
        return contracts[0]
    from tigeropen.trade.domain.contract import Contract
    return Contract(symbol=symbol, sec_type=sec_type, currency='USD')


@order.command('modify')
@click.argument('order_id', type=int)
@click.option('--limit-price', type=float, default=None, help='New limit price.')
@click.option('--quantity', type=int, default=None, help='New quantity.')
@click.option('--aux-price', type=float, default=None, help='New auxiliary/stop price.')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt.')
@click.pass_context
def order_modify(ctx, order_id, limit_price, quantity, aux_price, yes):
    """Modify an existing order."""
    client = get_trade_client(ctx.obj)
    order = client.get_order(id=order_id)
    if not order:
        click.echo(f'Order {order_id} not found.')
        return
    if limit_price is not None:
        order.limit_price = limit_price
    if quantity is not None:
        order.quantity = quantity
    if aux_price is not None:
        order.aux_price = aux_price
    if not yes:
        click.echo(f'Modify order {order_id}: limit_price={limit_price}, quantity={quantity}')
        click.confirm('Confirm modification?', abort=True)
    client.modify_order(order)
    click.echo(f'Order {order_id} modified.')


# --- Position subgroup ---

@trade.group('position')
def position():
    """Position management."""
    pass


@position.command('list')
@click.option('--sec-type', type=click.Choice(['STK', 'OPT', 'FUT', 'WAR'], case_sensitive=False),
              default='STK', help='Security type.')
@click.option('--market', type=click.Choice(['US', 'HK', 'ALL'], case_sensitive=False),
              default='ALL', help='Market filter.')
@click.option('--symbol', default=None, help='Filter by symbol.')
@click.pass_context
def position_list(ctx, sec_type, market, symbol):
    """List current positions."""
    client = get_trade_client(ctx.obj)
    kwargs = {'sec_type': sec_type, 'market': market}
    if symbol:
        kwargs['symbol'] = symbol
    positions = client.get_positions(**kwargs)
    if not is_empty(positions):
        data = []
        for p in positions:
            d = {k: v for k, v in p.__dict__.items() if k != 'contract'}
            if hasattr(p, 'contract') and p.contract:
                d['symbol'] = getattr(p.contract, 'symbol', '')
            data.append(d)
        render(data, ctx.obj['format'])
    else:
        click.echo('No positions found.')


# --- Transaction subgroup ---

@trade.group('transaction')
def transaction():
    """Transaction records."""
    pass


@transaction.command('list')
@click.option('--symbol', default=None, help='Filter by symbol.')
@click.option('--start-time', default=None, help='Start time.')
@click.option('--end-time', default=None, help='End time.')
@click.option('--limit', type=int, default=100, help='Max records.')
@click.pass_context
def transaction_list(ctx, symbol, start_time, end_time, limit):
    """List transaction records."""
    client = get_trade_client(ctx.obj)
    kwargs = {'limit': limit}
    if symbol:
        kwargs['symbol'] = symbol
    if start_time:
        kwargs['start_time'] = start_time
    if end_time:
        kwargs['end_time'] = end_time
    result = client.get_transactions(**kwargs)
    if not is_empty(result):
        data = to_records(result)
        render(data, ctx.obj['format'])
    else:
        click.echo('No transactions found.')
