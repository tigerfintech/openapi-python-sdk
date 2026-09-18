# -*- coding: utf-8 -*-
"""
Shared click options reused across command groups.
"""
import click

from tigeropen.common.consts import AssetQuoteType


asset_quote_type_option = click.option(
    '--asset-quote-type',
    type=click.Choice([t.value for t in AssetQuoteType], case_sensitive=False),
    default=None, help='Asset quote mode.')
