# -*- coding: utf-8 -*-
"""
Quote commands: briefs, bars, timeline, ticks, depth, market-status, option, future.
"""
import click

from tigeropen.cli.client_factory import get_quote_client
from tigeropen.cli.formatting import render, to_records, is_empty


@click.group('quote')
def quote():
    """Query market data (stocks, options, futures)."""
    pass


@quote.command('briefs')
@click.argument('symbols', nargs=-1, required=True)
@click.option('--hour-trading', is_flag=True, help='Include pre/after market data.')
@click.pass_context
def briefs(ctx, symbols, hour_trading):
    """Get real-time stock quotes."""
    client = get_quote_client(ctx.obj)
    result = client.get_stock_briefs(list(symbols), include_hour_trading=hour_trading)
    if is_empty(result):
        click.echo('No quote data found.')
    else:
        render(result, ctx.obj['format'])


@quote.command('bars')
@click.argument('symbols', nargs=-1, required=True)
@click.option('--period', type=click.Choice(
    ['day', 'week', 'month', 'year', '1min', '3min', '5min', '10min', '15min', '30min', '60min'],
    case_sensitive=False), default='day', help='Bar period.')
@click.option('--begin-time', default=None, help='Start time (timestamp or "YYYY-MM-DD").')
@click.option('--end-time', default=None, help='End time (timestamp or "YYYY-MM-DD").')
@click.option('--limit', type=int, default=251, help='Number of bars.')
@click.pass_context
def bars(ctx, symbols, period, begin_time, end_time, limit):
    """Get K-line (candlestick) data."""
    client = get_quote_client(ctx.obj)
    kwargs = {'period': period, 'limit': limit}
    if begin_time:
        kwargs['begin_time'] = begin_time
    if end_time:
        kwargs['end_time'] = end_time
    result = client.get_bars(list(symbols), **kwargs)
    if is_empty(result):
        click.echo('No bar data found.')
    else:
        render(result, ctx.obj['format'])


@quote.command('timeline')
@click.argument('symbols', nargs=-1, required=True)
@click.option('--date', default=None, help='Date in YYYY-MM-DD format.')
@click.pass_context
def timeline(ctx, symbols, date):
    """Get intraday timeline data."""
    client = get_quote_client(ctx.obj)
    kwargs = {}
    if date:
        kwargs['date'] = date
    result = client.get_timeline(list(symbols), **kwargs)
    if is_empty(result):
        click.echo('No timeline data found.')
    else:
        render(result, ctx.obj['format'])


@quote.command('ticks')
@click.argument('symbols', nargs=-1, required=True)
@click.option('--begin-index', type=int, default=None, help='Start index.')
@click.option('--end-index', type=int, default=None, help='End index.')
@click.option('--limit', type=int, default=None, help='Number of ticks.')
@click.pass_context
def ticks(ctx, symbols, begin_index, end_index, limit):
    """Get tick-by-tick trade data."""
    client = get_quote_client(ctx.obj)
    kwargs = {}
    if begin_index is not None:
        kwargs['begin_index'] = begin_index
    if end_index is not None:
        kwargs['end_index'] = end_index
    if limit is not None:
        kwargs['limit'] = limit
    result = client.get_trade_ticks(list(symbols), **kwargs)
    if is_empty(result):
        click.echo('No tick data found.')
    else:
        render(result, ctx.obj['format'])


@quote.command('depth')
@click.argument('symbols', nargs=-1, required=True)
@click.option('--market', type=click.Choice(['US', 'HK', 'CN'], case_sensitive=False),
              required=True, help='Market (required).')
@click.pass_context
def depth(ctx, symbols, market):
    """Get depth / order book data."""
    client = get_quote_client(ctx.obj)
    result = client.get_depth_quote(list(symbols), market=market)
    if is_empty(result):
        click.echo('No depth data found.')
    else:
        render(result, ctx.obj['format'])


@quote.command('market-status')
@click.option('--market', type=click.Choice(['US', 'HK', 'CN', 'ALL'], case_sensitive=False),
              default='ALL', help='Market to query.')
@click.pass_context
def market_status(ctx, market):
    """Get market status."""
    client = get_quote_client(ctx.obj)
    statuses = client.get_market_status(market=market)
    if not is_empty(statuses):
        data = to_records(statuses)
        render(data, ctx.obj['format'])
    else:
        click.echo('No market status data.')


@quote.command('symbols')
@click.option('--market', type=click.Choice(['US', 'HK', 'CN'], case_sensitive=False),
              default='US', help='Market to query.')
@click.pass_context
def symbols(ctx, market):
    """List available stock symbols."""
    client = get_quote_client(ctx.obj)
    result = client.get_symbol_names(market=market)
    if is_empty(result):
        click.echo('No symbol data found.')
    else:
        render(result, ctx.obj['format'])


# --- Option subgroup ---

@quote.group('option')
def option():
    """Option market data."""
    pass


@option.command('expirations')
@click.argument('symbol')
@click.pass_context
def option_expirations(ctx, symbol):
    """Get option expiration dates for a symbol."""
    client = get_quote_client(ctx.obj)
    result = client.get_option_expirations([symbol])
    if not is_empty(result):
        render(result, ctx.obj['format'])
    else:
        click.echo('No expiration data.')


@option.command('chain')
@click.argument('symbol')
@click.argument('expiry')
@click.pass_context
def option_chain(ctx, symbol, expiry):
    """Get option chain for a symbol and expiry date."""
    client = get_quote_client(ctx.obj)
    result = client.get_option_chain(symbol, expiry)
    if is_empty(result):
        click.echo('No option chain data found.')
    else:
        render(result, ctx.obj['format'])


@option.command('briefs')
@click.argument('identifiers', nargs=-1, required=True)
@click.pass_context
def option_briefs(ctx, identifiers):
    """Get option quotes by identifiers."""
    client = get_quote_client(ctx.obj)
    result = client.get_option_briefs(list(identifiers))
    if not is_empty(result):
        data = to_records(result)
        render(data, ctx.obj['format'])
    else:
        click.echo('No option brief data.')


@option.command('bars')
@click.argument('identifiers', nargs=-1, required=True)
@click.option('--period', default='day', help='Bar period.')
@click.option('--limit', type=int, default=251, help='Number of bars.')
@click.pass_context
def option_bars(ctx, identifiers, period, limit):
    """Get option K-line data."""
    client = get_quote_client(ctx.obj)
    result = client.get_option_bars(list(identifiers), period=period, limit=limit)
    if is_empty(result):
        click.echo('No option bar data found.')
    else:
        render(result, ctx.obj['format'])


# --- Future subgroup ---

@quote.group('future')
def future():
    """Futures market data."""
    pass


@future.command('exchanges')
@click.pass_context
def future_exchanges(ctx):
    """List available futures exchanges."""
    client = get_quote_client(ctx.obj)
    result = client.get_future_exchanges()
    if not is_empty(result):
        render(result, ctx.obj['format'])
    else:
        click.echo('No exchange data.')


@future.command('contracts')
@click.argument('exchange')
@click.pass_context
def future_contracts(ctx, exchange):
    """List futures contracts for an exchange."""
    client = get_quote_client(ctx.obj)
    result = client.get_future_contracts(exchange)
    if not is_empty(result):
        render(result, ctx.obj['format'])
    else:
        click.echo('No contract data.')


@future.command('briefs')
@click.argument('identifiers', nargs=-1, required=True)
@click.pass_context
def future_briefs(ctx, identifiers):
    """Get futures quotes."""
    client = get_quote_client(ctx.obj)
    result = client.get_future_brief(list(identifiers))
    if not is_empty(result):
        data = to_records(result)
        render(data, ctx.obj['format'])
    else:
        click.echo('No futures brief data.')


@future.command('bars')
@click.argument('identifier')
@click.option('--period', default='day', help='Bar period.')
@click.option('--limit', type=int, default=251, help='Number of bars.')
@click.pass_context
def future_bars(ctx, identifier, period, limit):
    """Get futures K-line data."""
    client = get_quote_client(ctx.obj)
    result = client.get_future_bars(identifier, period=period, limit=limit)
    if is_empty(result):
        click.echo('No futures bar data found.')
    else:
        render(result, ctx.obj['format'])


# --- Capital subgroup ---

@quote.group('capital')
def capital():
    """Capital flow data."""
    pass


@capital.command('flow')
@click.argument('symbol')
@click.option('--market', type=click.Choice(['US', 'HK'], case_sensitive=False), default='US', help='Market.')
@click.option('--period', default='day', help='Period: intraday/day/week/month.')
@click.pass_context
def capital_flow(ctx, symbol, market, period):
    """Get capital flow data for a symbol."""
    client = get_quote_client(ctx.obj)
    result = client.get_capital_flow(symbol, market=market, period=period)
    if is_empty(result):
        click.echo('No capital flow data found.')
    else:
        render(result, ctx.obj['format'])


@capital.command('distribution')
@click.argument('symbol')
@click.option('--market', type=click.Choice(['US', 'HK'], case_sensitive=False), default='US', help='Market.')
@click.pass_context
def capital_distribution(ctx, symbol, market):
    """Get capital distribution for a symbol."""
    client = get_quote_client(ctx.obj)
    result = client.get_capital_distribution(symbol, market=market)
    if result is None:
        click.echo('No capital distribution data found.')
    elif hasattr(result, 'to_dict'):
        render(result.to_dict(), ctx.obj['format'])
    elif hasattr(result, '__dict__'):
        render(result.__dict__, ctx.obj['format'])
    else:
        render(result, ctx.obj['format'])


# --- Fundamental subgroup ---

@quote.group('fundamental')
def fundamental():
    """Fundamental data (financial reports, dividends, earnings)."""
    pass


@fundamental.command('financial')
@click.argument('symbols', nargs=-1, required=True)
@click.option('--market', type=click.Choice(['US', 'HK', 'CN'], case_sensitive=False), default='US', help='Market.')
@click.option('--fields', default='total_revenue,net_income', help='Comma-separated field names (Income/Balance/CashFlow).')
@click.option('--period-type', type=click.Choice(['ANNUAL', 'QUARTERLY', 'LTM'], case_sensitive=False),
              default='ANNUAL', help='Report period type.')
@click.option('--begin-date', default=None, help='Start date (YYYY-MM-DD).')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD).')
@click.pass_context
def financial(ctx, symbols, market, fields, period_type, begin_date, end_date):
    """Get financial report data."""
    from tigeropen.common.consts import FinancialReportPeriodType
    from tigeropen.common.consts.fundamental_fields import Income, Balance, CashFlow
    client = get_quote_client(ctx.obj)
    # Resolve field names to enum values
    field_enums = []
    for name in (f.strip() for f in fields.split(',')):
        for cls in (Income, Balance, CashFlow):
            try:
                field_enums.append(cls(name))
                break
            except ValueError:
                continue
        else:
            field_enums.append(name)
    pt = FinancialReportPeriodType[period_type.upper()]
    kwargs = {'period_type': pt}
    if begin_date:
        kwargs['begin_date'] = begin_date
    if end_date:
        kwargs['end_date'] = end_date
    result = client.get_financial_report(list(symbols), market=market, fields=field_enums, **kwargs)
    if is_empty(result):
        click.echo('No financial data found.')
    else:
        render(result, ctx.obj['format'])


@fundamental.command('dividend')
@click.argument('symbols', nargs=-1, required=True)
@click.option('--market', type=click.Choice(['US', 'HK', 'CN'], case_sensitive=False), default='US', help='Market.')
@click.option('--begin-date', required=True, help='Start date (YYYY-MM-DD).')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD).')
@click.pass_context
def dividend(ctx, symbols, market, begin_date, end_date):
    """Get dividend data."""
    client = get_quote_client(ctx.obj)
    result = client.get_corporate_dividend(list(symbols), market=market, begin_date=begin_date, end_date=end_date)
    if is_empty(result):
        click.echo('No dividend data found.')
    else:
        render(result, ctx.obj['format'])


@fundamental.command('earnings')
@click.option('--market', type=click.Choice(['US', 'HK', 'CN'], case_sensitive=False), default='US', help='Market.')
@click.option('--begin-date', required=True, help='Start date (YYYY-MM-DD).')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD).')
@click.pass_context
def earnings(ctx, market, begin_date, end_date):
    """Get earnings calendar data."""
    client = get_quote_client(ctx.obj)
    result = client.get_corporate_earnings_calendar(market=market, begin_date=begin_date, end_date=end_date)
    if is_empty(result):
        click.echo('No earnings data found.')
    else:
        render(result, ctx.obj['format'])


# --- Scanner subgroup ---

def _parse_filter(spec):
    """Parse a filter spec string into a StockFilter.

    Supported formats:
      FIELD_NAME                        -- include field with no range filter (is_no_filter=True)
      FIELD_NAME:min:max                -- numeric range filter
      FIELD_NAME:min:                   -- numeric lower bound only
      FIELD_NAME::max                   -- numeric upper bound only
      FIELD_NAME:tag1,tag2              -- MultiTagField tag list

    FIELD_NAME prefix determines the field type:
      Plain name → StockField (e.g. MarketValue, ChangeRate, PeTTM)
      acc:NAME   → AccumulateField with optional period suffix NAME:period
                   e.g. acc:ROE:0.15::ANNUAL  means AccumulateField.ROE min=0.15, period=ANNUAL
      fin:NAME   → FinancialField (LTM only)
      tag:NAME   → MultiTagField with tag_list

    Shorthand presets:
      gainers     → AccumulateField.ChangeRate min=5 (INTRADAY)
      losers      → AccumulateField.ChangeRate max=-5 (INTRADAY)
    """
    from tigeropen.quote.domain.filter import StockFilter
    from tigeropen.common.consts.filter_fields import (
        StockField, AccumulateField, FinancialField, MultiTagField,
        AccumulatePeriod, FinancialPeriod
    )

    # Presets
    presets = {
        'gainers': lambda: StockFilter(AccumulateField.ChangeRate, filter_min=5),
        'losers': lambda: StockFilter(AccumulateField.ChangeRate, filter_max=-5),
    }
    if spec.lower() in presets:
        return presets[spec.lower()]()

    parts = spec.split(':')
    raw_name = parts[0].strip()

    # Determine field type and lookup
    if raw_name.lower().startswith('acc.'):
        field_name = raw_name[4:]
        try:
            field = AccumulateField[field_name]
        except KeyError:
            raise click.BadParameter(f"Unknown AccumulateField: {field_name}. Examples: ROE, ChangeRate, NetIncome")
        filter_min = float(parts[1]) if len(parts) > 1 and parts[1] else None
        filter_max = float(parts[2]) if len(parts) > 2 and parts[2] else None
        period = None
        if len(parts) > 3 and parts[3]:
            try:
                period = AccumulatePeriod[parts[3].upper()]
            except KeyError:
                raise click.BadParameter(f"Unknown AccumulatePeriod: {parts[3]}. Options: ANNUAL, QUARTERLY, SEMIANNUAL")
        return StockFilter(field, filter_min=filter_min, filter_max=filter_max, accumulate_period=period)

    elif raw_name.lower().startswith('fin.'):
        field_name = raw_name[4:]
        try:
            field = FinancialField[field_name]
        except KeyError:
            raise click.BadParameter(f"Unknown FinancialField: {field_name}. Examples: ReturnOnEquityRate, GrossProfitRate")
        filter_min = float(parts[1]) if len(parts) > 1 and parts[1] else None
        filter_max = float(parts[2]) if len(parts) > 2 and parts[2] else None
        return StockFilter(field, filter_min=filter_min, filter_max=filter_max,
                           financial_period=FinancialPeriod.LTM)

    elif raw_name.lower().startswith('tag.'):
        field_name = raw_name[4:]
        try:
            field = MultiTagField[field_name]
        except KeyError:
            raise click.BadParameter(f"Unknown MultiTagField: {field_name}. Examples: Industry, Concept, OptionsAvailable")
        tag_list = [t.strip() for t in parts[1].split(',')] if len(parts) > 1 else []
        return StockFilter(field, tag_list=tag_list)

    else:
        # Default: StockField
        try:
            field = StockField[raw_name]
        except KeyError:
            raise click.BadParameter(
                f"Unknown StockField: {raw_name}. Use acc./fin./tag. prefix for other types. "
                f"Examples: MarketValue, PeTTM, Volume, TurnoverRate"
            )
        if len(parts) == 1:
            return StockFilter(field, is_no_filter=True)
        filter_min = float(parts[1]) if len(parts) > 1 and parts[1] else None
        filter_max = float(parts[2]) if len(parts) > 2 and parts[2] else None
        return StockFilter(field, filter_min=filter_min, filter_max=filter_max)


@quote.command('scanner')
@click.option('--market', type=click.Choice(['US', 'HK'], case_sensitive=False), default='US',
              help='Market: US or HK.')
@click.option('--filter', 'filters', multiple=True,
              help='Filter spec. Formats: FIELD, FIELD:min:max, acc.FIELD:min:max:PERIOD, '
                   'fin.FIELD:min:max, tag.FIELD:tag1,tag2. '
                   'Presets: gainers, losers. '
                   'Examples: --filter MarketValue:1e9: --filter acc.ROE:0.15::ANNUAL')
@click.option('--sort', default=None,
              help='Sort field name (same format as --filter field, e.g. MarketValue or acc.ChangeRate).')
@click.option('--sort-dir', type=click.Choice(['ASC', 'DESC'], case_sensitive=False), default='DESC',
              help='Sort direction.')
@click.option('--limit', type=int, default=20, help='Max results to display.')
@click.option('--page-size', type=int, default=20, help='Page size per API request.')
@click.pass_context
def scanner(ctx, market, filters, sort, sort_dir, limit, page_size):
    """Scan stocks using filters. Use --filter to add criteria.

    \b
    Examples:
      # Top gainers today
      tigeropen quote scanner --filter gainers --sort acc.ChangeRate --sort-dir DESC

      # Large-cap US stocks with P/E under 20
      tigeropen quote scanner --filter MarketValue:1e10: --filter PeTTM::20 --sort MarketValue

      # High ROE stocks (annual)
      tigeropen quote scanner --filter acc.ROE:0.15::ANNUAL --sort acc.ROE:ANNUAL --sort-dir DESC

      # Stocks with options available
      tigeropen quote scanner --filter tag.OptionsAvailable:1
    """
    from tigeropen.quote.domain.filter import StockFilter, SortFilterData
    from tigeropen.common.consts.filter_fields import (
        StockField, AccumulateField, FinancialField, AccumulatePeriod, FinancialPeriod
    )
    from tigeropen.common.consts import SortDirection, Market

    client = get_quote_client(ctx.obj)

    # Parse filters
    filter_objects = []
    for f in filters:
        filter_objects.append(_parse_filter(f))

    # Parse sort field
    sort_filter_data = None
    if sort:
        sort_parts = sort.split(':')
        raw_sort = sort_parts[0]
        sort_period = None

        if raw_sort.lower().startswith('acc.'):
            sort_field = AccumulateField[raw_sort[4:]]
            if len(sort_parts) > 1 and sort_parts[1]:
                try:
                    sort_period = AccumulatePeriod[sort_parts[1].upper()]
                except KeyError:
                    pass
        elif raw_sort.lower().startswith('fin.'):
            sort_field = FinancialField[raw_sort[4:]]
        else:
            sort_field = StockField[raw_sort]

        sd = SortDirection.DESC if sort_dir.upper() == 'DESC' else SortDirection.ASC
        sort_filter_data = SortFilterData(sort_field, sort_dir=sd, period=sort_period)

    market_enum = Market.US if market.upper() == 'US' else Market.HK

    # Execute scan
    result = client.market_scanner(
        market=market_enum,
        filters=filter_objects if filter_objects else None,
        sort_field_data=sort_filter_data,
        page_size=min(page_size, limit)
    )

    if not result or not result.items:
        click.echo('No results found.')
        return

    # Build output rows
    rows = []
    collected = 0
    cursor_id = result.cursor_id

    while True:
        for item in result.items:
            if collected >= limit:
                break
            row = {'symbol': item.symbol, 'market': item.market}
            for f in filter_objects:
                val = item[f]
                if val is not None:
                    row[f.field.name] = val
            if sort_filter_data:
                val = item[sort_filter_data.field]
                if val is not None:
                    row[sort_filter_data.field.name] = val
            rows.append(row)
            collected += 1
        if collected >= limit or not cursor_id or result.page >= result.total_page - 1:
            break
        result = client.market_scanner(
            market=market_enum,
            filters=filter_objects if filter_objects else None,
            sort_field_data=sort_filter_data,
            page_size=page_size,
            cursor_id=cursor_id
        )
        if not result or not result.items:
            break
        cursor_id = result.cursor_id

    click.echo(f"Showing {len(rows)} of {result.total_count} total results")
    render(rows, ctx.obj['format'])
