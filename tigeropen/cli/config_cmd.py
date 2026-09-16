# -*- coding: utf-8 -*-
"""
Config commands: init, show, set, path.
"""
import os

import click
from jproperties import Properties

from tigeropen.auth.oauth2 import OAuth2SessionManager
from tigeropen.tiger_open_config import DEFAULT_PROPS_FILE
from tigeropen.cli.client_factory import resolve_private_key, DEFAULT_CONFIG_DIR


@click.group('config')
def config():
    """Manage tigeropen configuration."""
    pass


@config.command('init')
@click.pass_context
def config_init(ctx):
    """Interactive configuration setup.

    Authentication mode comes from the global --auth option:
      tigeropen --auth oauth2 config init    # no private key, collects issuer
      tigeropen config init                  # signature mode (default), as before
    """
    auth_mode = (ctx.obj or {}).get('auth') or 'signature'
    if auth_mode == 'oauth2':
        _config_init_oauth2()
        return
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
    p['auth_mode'] = auth_mode
    p['tiger_id'] = tiger_id
    p['account'] = account
    p['private_key_pk8'] = resolve_private_key(private_key)

    if secret_key:
        p['secret_key'] = secret_key

    with open(props_file, 'wb') as f:
        p.store(f, encoding='utf-8')

    click.echo(f'Config written to {props_file}')


def _config_init_oauth2():
    """Configure the CLI for OAuth2 authentication. No private key is collected.

    The issuer and the gateway are not asked for: both follow the built-in defaults, and a
    value written here would outlive the default it was copied from. Override them with
    TIGEROPEN_OAUTH2_ISSUER and TIGEROPEN_SERVER_URL, or `config set`.
    """
    click.echo('Authorization server: %s' % OAuth2SessionManager.default_issuer())
    client_id = click.prompt('Client ID (manual registration only, press Enter to skip)',
                             default='', show_default=False)
    account = click.prompt('Account (business parameter, needed for trading)')
    config_dir = click.prompt('Config directory', default=DEFAULT_CONFIG_DIR)

    os.makedirs(config_dir, exist_ok=True)
    props_file = os.path.join(config_dir, DEFAULT_PROPS_FILE)

    p = Properties()
    p['auth_mode'] = 'oauth2'
    if client_id:
        p['client_id'] = client_id
    p['account'] = account

    with open(props_file, 'wb') as f:
        p.store(f, encoding='utf-8')

    click.echo(f'Config written to {props_file}')
    click.echo('下一步：运行 tigeropen auth login 完成授权。')


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

    auth_mode = p.get('auth_mode', None)
    if auth_mode and auth_mode.data == 'oauth2':
        # OAuth2 mode: show auth_mode/issuer/client_id (masked), skip private key.
        for key in ('auth_mode', 'issuer', 'client_id', 'server_url', 'account'):
            if key not in p:
                continue
            value = p[key].data
            if key == 'client_id' and value:
                value = _mask(value)
            click.echo(f'{key}={value}')
        return

    for key in p:
        value = p[key].data
        if 'private_key' in key and value:
            # Mask: show first 4 and last 4 chars
            if len(value) > 8:
                value = value[:4] + '****' + value[-4:]
            else:
                value = '****'
        click.echo(f'{key}={value}')


def _mask(value):
    """Mask a string, keeping the first and last 4 chars."""
    if len(value) <= 8:
        return '****'
    return value[:4] + '****' + value[-4:]


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
