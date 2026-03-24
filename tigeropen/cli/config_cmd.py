# -*- coding: utf-8 -*-
"""
Config commands: init, show, set, path.
"""
import os

import click
from jproperties import Properties

from tigeropen.tiger_open_config import DEFAULT_PROPS_FILE
from tigeropen.cli.client_factory import resolve_private_key, DEFAULT_CONFIG_DIR


@click.group('config')
def config():
    """Manage tigeropen configuration."""
    pass


@config.command('init')
@click.pass_context
def config_init(ctx):
    """Interactive configuration setup."""
    tiger_id = click.prompt('Tiger ID')
    account = click.prompt('Account')

    # Private key: support multi-line paste (PEM or raw base64).
    # Read lines until an empty line signals end of input.
    click.echo('Private Key (file path or key content, blank line to finish):')
    lines = []
    stdin = click.get_text_stream('stdin')
    while True:
        line = stdin.readline()
        if not line:  # EOF
            break
        line = line.rstrip('\n').rstrip('\r')
        if not line and lines:
            break
        if line:
            lines.append(line)
    private_key = ''.join(lines)

    if not private_key:
        raise click.ClickException('Private key cannot be empty.')

    secret_key = click.prompt('Secret Key (institutional only, press Enter to skip)',
                              default='', show_default=False)
    config_dir = click.prompt('Config directory', default=DEFAULT_CONFIG_DIR)

    os.makedirs(config_dir, exist_ok=True)
    props_file = os.path.join(config_dir, DEFAULT_PROPS_FILE)

    p = Properties()
    p['tiger_id'] = tiger_id
    p['account'] = account
    p['private_key_pk8'] = resolve_private_key(private_key)

    if secret_key:
        p['secret_key'] = secret_key

    with open(props_file, 'wb') as f:
        p.store(f, encoding='utf-8')

    click.echo(f'Config written to {props_file}')


@config.command('show')
@click.pass_context
def config_show(ctx):
    """Display current configuration (private key masked)."""
    config_path = ctx.obj.get('config_path') if ctx.obj else None
    config_path = config_path or DEFAULT_CONFIG_DIR
    if os.path.isdir(config_path):
        props_file = os.path.join(config_path, DEFAULT_PROPS_FILE)
    else:
        props_file = config_path

    if not os.path.exists(props_file):
        click.echo(f'Config file not found: {props_file}')
        return

    p = Properties()
    with open(props_file, 'rb') as f:
        p.load(f, 'utf-8')

    for key in p:
        value = p[key].data
        if 'private_key' in key and value:
            # Mask: show first 4 and last 4 chars
            if len(value) > 8:
                value = value[:4] + '****' + value[-4:]
            else:
                value = '****'
        click.echo(f'{key}={value}')


@config.command('set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx, key, value):
    """Set a configuration value."""
    config_path = ctx.obj.get('config_path') if ctx.obj else None
    config_path = config_path or DEFAULT_CONFIG_DIR
    if os.path.isdir(config_path):
        props_file = os.path.join(config_path, DEFAULT_PROPS_FILE)
    else:
        props_file = config_path

    p = Properties()
    if os.path.exists(props_file):
        with open(props_file, 'rb') as f:
            p.load(f, 'utf-8')

    p[key] = value

    os.makedirs(os.path.dirname(props_file) if os.path.dirname(props_file) else '.', exist_ok=True)
    with open(props_file, 'wb') as f:
        p.store(f, encoding='utf-8')

    click.echo(f'Set {key}={value}')


@config.command('path')
@click.pass_context
def config_path(ctx):
    """Print the config directory path."""
    config_dir = ctx.obj.get('config_path') if ctx.obj else None
    click.echo(config_dir or DEFAULT_CONFIG_DIR)
