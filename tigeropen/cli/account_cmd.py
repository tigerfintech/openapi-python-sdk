# -*- coding: utf-8 -*-
"""
Account commands: info, assets, analytics.
"""
import click

from tigeropen.cli.client_factory import get_trade_client
from tigeropen.cli.formatting import render, to_records, is_empty


@click.group('account')
def account():
    """Account information and assets."""
    pass


@account.command('info')
@click.pass_context
def account_info(ctx):
    """Show account information."""
    client = get_trade_client(ctx.obj)
    accounts = client.get_managed_accounts()
    if not is_empty(accounts):
        data = to_records(accounts)
        render(data, ctx.obj['format'])
    else:
        click.echo('No account info available.')


def _segment_to_dict(segment):
    """Serialize a Segment object to a plain dict."""
    d = {k: v for k, v in segment.__dict__.items() if not k.startswith('_')}
    d['currency_assets'] = {
        currency: {k: v for k, v in ca.__dict__.items()}
        for currency, ca in segment.currency_assets.items()
    }
    return d


def _portfolio_account_to_dict(account):
    """Serialize a PortfolioAccount object to a plain dict."""
    return {
        'account': account.account,
        'update_timestamp': account.update_timestamp,
        'segments': {
            key: _segment_to_dict(seg)
            for key, seg in account._segments.items()
        },
    }


@account.command('assets')
@click.option('--currency', default=None, help='Currency filter (USD, HKD, etc.).')
@click.pass_context
def account_assets(ctx, currency):
    """Show account asset summary."""
    client = get_trade_client(ctx.obj)
    kwargs = {}
    if currency:
        kwargs['base_currency'] = currency
    result = client.get_prime_assets(**kwargs)
    if not is_empty(result):
        render(_portfolio_account_to_dict(result), ctx.obj['format'])
    else:
        click.echo('No asset data available.')


@account.command('analytics')
@click.option('--start-date', default=None, help='Start date (YYYY-MM-DD).')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD).')
@click.pass_context
def account_analytics(ctx, start_date, end_date):
    """Show asset analytics."""
    client = get_trade_client(ctx.obj)
    kwargs = {}
    if start_date:
        kwargs['start_date'] = start_date
    if end_date:
        kwargs['end_date'] = end_date
    result = client.get_analytics_asset(**kwargs)
    if not is_empty(result):
        render(result, ctx.obj['format'])
    else:
        click.echo('No analytics data available.')
