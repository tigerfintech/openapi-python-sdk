# -*- coding: utf-8 -*-
"""
Client factory module for CLI.
Handles config resolution, private key loading, and lazy client creation.
"""
import os
from pathlib import Path

from tigeropen import __VERSION__
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.tiger_open_config import TigerOpenClientConfig

DEFAULT_CONFIG_DIR = str(Path.home() / '.tigeropen')


def resolve_private_key(key_input):
    """
    Resolve private key from file path, PEM string, or raw key string.

    :param key_input: file path, PEM string with headers, or raw key string
    :return: stripped private key string (no PEM headers)
    """
    if not key_input:
        return ''

    # If it's an existing file path, read from file
    if os.path.isfile(key_input):
        return read_private_key(key_input)

    # If it's a full PEM string with headers, strip them
    if '-----BEGIN RSA PRIVATE KEY-----' in key_input:
        return key_input.replace('-----BEGIN RSA PRIVATE KEY-----', '') \
            .replace('-----END RSA PRIVATE KEY-----', '') \
            .replace('\n', '').strip()

    # Otherwise treat as raw key string
    return key_input


def build_config(ctx_obj):
    """
    Build TigerOpenClientConfig from CLI context dict.

    :param ctx_obj: dict with optional keys: config_path, tiger_id, account, private_key, language
    :return: TigerOpenClientConfig
    """
    config_path = ctx_obj.get('config_path') or DEFAULT_CONFIG_DIR
    config = TigerOpenClientConfig(enable_dynamic_domain=False,
                                   props_path=config_path)
    config._channel = f"tigercli"

    if ctx_obj.get('tiger_id'):
        config.tiger_id = ctx_obj['tiger_id']
    if ctx_obj.get('account'):
        config.account = ctx_obj['account']
    if ctx_obj.get('private_key'):
        config.private_key = resolve_private_key(ctx_obj['private_key'])
    if ctx_obj.get('language'):
        config.language = ctx_obj['language']

    return config


def get_quote_client(ctx_obj):
    """Lazily create and cache a QuoteClient."""
    if '_quote_client' not in ctx_obj:
        from tigeropen.quote.quote_client import QuoteClient
        config = build_config(ctx_obj)
        ctx_obj['_quote_client'] = QuoteClient(config, is_grab_permission=False)
    return ctx_obj['_quote_client']


def get_trade_client(ctx_obj):
    """Lazily create and cache a TradeClient."""
    if '_trade_client' not in ctx_obj:
        from tigeropen.trade.trade_client import TradeClient
        config = build_config(ctx_obj)
        ctx_obj['_trade_client'] = TradeClient(config)
    return ctx_obj['_trade_client']
