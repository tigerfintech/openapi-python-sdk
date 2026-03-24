# -*- coding: utf-8 -*-
"""
Push commands: real-time streaming for quotes, orders, positions, assets.
"""
import json
import threading

import click

from tigeropen.cli.client_factory import build_config
from tigeropen.push.push_client import PushClient


@click.group('push')
def push():
    """Real-time data streaming (quotes, orders, positions)."""
    pass


def _create_push_client(ctx_obj):
    """Create and configure a PushClient from CLI context."""
    config = build_config(ctx_obj)
    protocol, host, port = config.socket_host_port
    use_ssl = (protocol == 'ssl')
    client = PushClient(host, port, use_ssl=use_ssl)
    return client, config


def _stream_output(data, fmt='table'):
    """Output streaming data as JSON lines (for piping) or formatted."""
    if fmt == 'json':
        click.echo(json.dumps(data, ensure_ascii=False, default=str))
    else:
        click.echo(str(data))


def _wait_for_interrupt():
    """Block until KeyboardInterrupt. Uses short-timeout loop so signals are delivered."""
    try:
        while True:
            threading.Event().wait(timeout=0.5)
    except KeyboardInterrupt:
        pass


def _run_push(ctx, callback_attr, subscribe_fn, label):
    """
    Common push command logic: connect, subscribe, stream, disconnect.

    :param ctx: Click context
    :param callback_attr: name of the PushClient callback attribute (e.g. 'quote_changed')
    :param subscribe_fn: callable(push_client, config) that performs the subscription
    :param label: human-readable label for output messages
    """
    fmt = ctx.obj.get('format', 'table')
    push_client, config = _create_push_client(ctx.obj)

    def on_changed(frame):
        _stream_output(frame, fmt)

    setattr(push_client, callback_attr, on_changed)

    try:
        push_client.connect(config.tiger_id, config.private_key)
        subscribe_fn(push_client, config)
        click.echo(f'Subscribed to {label} updates.')
        click.echo('Press Ctrl+C to stop.')
        _wait_for_interrupt()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            push_client.disconnect()
        except Exception:
            pass
    click.echo('Disconnected.')


@push.command('quote')
@click.argument('symbols', nargs=-1, required=True)
@click.pass_context
def push_quote(ctx, symbols):
    """Stream real-time quote updates. Press Ctrl+C to stop."""
    def subscribe(client, config):
        client.subscribe_quote(list(symbols))

    click.echo(f'Subscribing to: {", ".join(symbols)}')
    _run_push(ctx, 'quote_changed', subscribe, 'quote')


@push.command('order')
@click.pass_context
def push_order(ctx):
    """Stream order status updates. Press Ctrl+C to stop."""
    def subscribe(client, config):
        client.subscribe_order(account=config.account)

    _run_push(ctx, 'order_changed', subscribe, 'order')


@push.command('position')
@click.pass_context
def push_position(ctx):
    """Stream position updates. Press Ctrl+C to stop."""
    def subscribe(client, config):
        client.subscribe_position(account=config.account)

    _run_push(ctx, 'position_changed', subscribe, 'position')


@push.command('asset')
@click.pass_context
def push_asset(ctx):
    """Stream asset updates. Press Ctrl+C to stop."""
    def subscribe(client, config):
        client.subscribe_asset(account=config.account)

    _run_push(ctx, 'asset_changed', subscribe, 'asset')
