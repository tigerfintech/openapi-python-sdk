# -*- coding: utf-8 -*-
"""
Main CLI entry point for tigeropen.
"""
import logging
import sys
import traceback

import click

from tigeropen import __VERSION__
from tigeropen.auth.oauth2.exceptions import Category, OAuth2Exception
from tigeropen.common.exceptions import ApiException
from tigeropen.auth.oauth2.session_manager import ENV_ISSUER
from tigeropen.cli.settings import ENV_ACCOUNT, ENV_CLIENT_ID
from tigeropen.cli.auth_cmd import auth
from tigeropen.cli.config_cmd import config
from tigeropen.cli.quote_cmd import quote
from tigeropen.cli.trade_cmd import trade
from tigeropen.cli.account_cmd import account
from tigeropen.cli.skills_cmd import skills

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

GETTING_STARTED = """\
TigerOpen CLI v{version} — Tiger Brokers Open API

Getting started:

  1. Run interactive setup:
     $ tigeropen config init

  2. Or set environment variables:
     $ export TIGEROPEN_TIGER_ID="your_tiger_id"
     $ export TIGEROPEN_PRIVATE_KEY="your_private_key"
     $ export TIGEROPEN_ACCOUNT="your_account"

  3. Query market data:
     $ tigeropen quote briefs AAPL TSLA
     $ tigeropen quote bars AAPL --period day --limit 10

  4. Manage orders:
     $ tigeropen trade order list
     $ tigeropen trade position list

  5. View account:
     $ tigeropen account assets

Run 'tigeropen -h' to see all commands and options.
Run 'tigeropen <command> -h' for help on a specific command.
"""


class TigerCLI(click.Group):
    """Custom click Group that catches API/generic exceptions and shows
    a getting-started guide when invoked with no arguments."""

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except click.exceptions.Exit:
            raise
        except click.exceptions.Abort:
            click.echo('Aborted.', err=True)
            sys.exit(1)
        except ApiException as e:
            click.echo(f'API Error [{e.code}]: {e.msg}')
            if ctx.obj and ctx.obj.get('verbose'):
                traceback.print_exc()
            sys.exit(1)
        except OAuth2Exception as e:
            if e.category == Category.REAUTHORIZATION_REQUIRED:
                # The SDK message names the Python API; a command line needs the command.
                click.echo('未授权或授权已失效。运行 tigeropen auth login 进行授权。', err=True)
            else:
                click.echo(f'认证失败 [{e.category.name}]: {e.message}', err=True)
            if ctx.obj and ctx.obj.get('verbose'):
                traceback.print_exc()
            sys.exit(1)
        except Exception as e:
            click.echo(f'Error: {e}')
            if ctx.obj and ctx.obj.get('verbose'):
                traceback.print_exc()
            sys.exit(1)

    # Global options that can appear anywhere in the command line
    _GLOBAL_OPTIONS = {
        '-f': 1, '--format': 1,
        '-c': 1, '--config-path': 1,
        '-l': 1, '--language': 1,
        '--auth': 1, '--issuer': 1, '--client-id': 1, '--account': 1,
        '-v': 0, '--verbose': 0,
    }

    def parse_args(self, ctx, args):
        if not args:
            click.echo(GETTING_STARTED.format(version=__VERSION__))
            ctx.exit(0)
        # Move global options to the front so Click's group parser can see them.
        # This allows e.g. `tigeropen quote briefs AAPL -f json` to work.
        front = []
        rest = []
        i = 0
        args = list(args)
        while i < len(args):
            arg = args[i]
            if arg in self._GLOBAL_OPTIONS:
                n_values = self._GLOBAL_OPTIONS[arg]
                front.append(arg)
                for j in range(n_values):
                    if i + 1 + j < len(args):
                        front.append(args[i + 1 + j])
                i += 1 + n_values
            else:
                rest.append(arg)
                i += 1
        return super().parse_args(ctx, front + rest)


@click.group(cls=TigerCLI, context_settings=CONTEXT_SETTINGS)
@click.option('--config-path', '-c', type=click.Path(), envvar='TIGEROPEN_PROPS_PATH',
              help='Path to config directory or properties file.')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'csv'], case_sensitive=False),
              default='json', help='Output format.')
@click.option('--language', '-l',
              type=click.Choice(['en_US', 'zh_CN', 'zh_TW'], case_sensitive=False),
              default='en_US', help='Language.')
@click.option('--auth', 'auth_mode',
              type=click.Choice(['signature', 'oauth2'], case_sensitive=False),
              # default=None so it does not shadow auth_mode in the properties file
              default=None, help='Authentication mode: signature (tiger_id + private key) '
                                 'or oauth2. Defaults to auth_mode from the config file; '
                                 'otherwise oauth2, unless this machine is set up for '
                                 'signature mode and has never authorized.')
@click.option('--issuer', envvar=ENV_ISSUER, default=None,
              help='OAuth2 authorization server (oauth2 mode; omit for the built-in default).')
@click.option('--client-id', envvar=ENV_CLIENT_ID, default=None,
              help='Manually registered clientId (oauth2 mode; omit for dynamic registration).')
@click.option('--account', envvar=ENV_ACCOUNT, default=None,
              help='Trading account. Defaults to account from the config file.')
@click.option('--verbose', '-v', is_flag=True, help='Enable debug logging.')
@click.pass_context
def cli(ctx, config_path, output_format, language, auth_mode, issuer, client_id, account,
        verbose):
    """TigerOpen CLI - Tiger Brokers Open API command line tool."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config_path
    ctx.obj['format'] = output_format
    ctx.obj['language'] = language
    ctx.obj['auth'] = auth_mode
    ctx.obj['issuer'] = issuer
    ctx.obj['client_id'] = client_id
    ctx.obj['account'] = account
    ctx.obj['verbose'] = verbose
    _configure_sdk_logging(verbose)


#: The SDK logs through two named trees: the clients use ``tiger_openapi``, while modules
#: calling ``getLogger(__name__)`` sit under ``tigeropen``. Both are needed; neither is a
#: parent of the other.
SDK_LOGGERS = ('tigeropen', 'tiger_openapi')


def _configure_sdk_logging(verbose):
    """Keep the SDK's own logger output off the terminal unless -v is given.

    It logs with exc_info=True and has no handler of its own, so those tracebacks reach stderr
    through logging's last resort. This CLI reports errors itself.

    -v also turns on the root logger: the push transport logs through it, and a stream cannot
    be diagnosed without those lines.
    """
    level = logging.DEBUG if verbose else logging.CRITICAL
    for name in SDK_LOGGERS:
        logging.getLogger(name).setLevel(level)
    if verbose:
        # Set explicitly rather than through basicConfig, which does nothing at all once the
        # root logger has a handler.
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        if not root.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s'))
            root.addHandler(handler)


@cli.command('version')
def version():
    """Print the SDK version."""
    click.echo(__VERSION__)


@cli.command('uninstall')
@click.option('--remove-config', is_flag=True,
              help='Also remove the configuration file and this CLI\'s OAuth2 credentials.')
@click.option('-y', '--yes', is_flag=True, help='Skip confirmation prompts.')
@click.pass_context
def uninstall(ctx, remove_config, yes):
    """Uninstall tigeropen and optionally remove configuration.

    Credentials live in two places: signature ones in the configuration directory, OAuth2
    ones in the token store. Both are cleared by --remove-config, but only the CLI's own
    OAuth2 credentials: the token store is shared with the SDKs.
    """
    import subprocess
    import shutil
    from pathlib import Path

    if not yes:
        msg = 'Uninstall tigeropen?'
        if remove_config:
            msg += ' (including the configuration file and this CLI\'s OAuth2 credentials)'
        if not click.confirm(msg):
            raise SystemExit(0)

    # Remove local state first, before pip uninstall takes the CLI itself away
    if remove_config:
        config_dir = Path.home() / '.tigeropen'
        if config_dir.exists():
            shutil.rmtree(config_dir)
            click.echo(f'Removed {config_dir}')
        else:
            click.echo(f'{config_dir} not found, skipping.')
        _remove_oauth2_credentials(ctx)

    # Run pip uninstall with the same Python interpreter
    click.echo('Uninstalling tigeropen...')
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'uninstall', 'tigeropen', '-y'],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        click.echo('tigeropen has been uninstalled.')
    else:
        click.echo(f'pip uninstall failed:\n{result.stderr.strip()}', err=True)
        sys.exit(1)


def _remove_oauth2_credentials(ctx):
    """Revoke and delete the CLI's OAuth2 credentials, reporting what was left alone.

    Nothing here may abort the uninstall: the package still has to come off even if the
    store is unreadable or the authorization server cannot be reached.
    """
    from tigeropen.cli.oauth2_config import remove_stored_credentials
    from tigeropen.cli.settings import resolve_settings
    try:
        settings = resolve_settings(ctx.obj or {})
        revoked, removed = remove_stored_credentials(issuer=settings['issuer'],
                                                     client_id=settings['client_id'])
    except Exception as e:
        click.echo(f'Could not remove OAuth2 credentials: {e}', err=True)
        return
    for path in removed:
        click.echo(f'Removed {path}')
    if not removed:
        click.echo('No OAuth2 credentials stored for this CLI, skipping.')
    if removed and not revoked:
        click.echo('Note: the server was not reached, so the authorization may still be '
                   'listed there. Remove it on the authorization page if you want it gone.')


cli.add_command(auth)
cli.add_command(config)
cli.add_command(quote)
cli.add_command(trade)
cli.add_command(account)
cli.add_command(skills)


def _load_push_command():
    """Lazy-load push command to avoid importing protobuf at startup."""
    try:
        from tigeropen.cli.push_cmd import push
        cli.add_command(push)
    except ImportError:
        @cli.command('push')
        @click.argument('args', nargs=-1)
        def push_unavailable(args):
            """Real-time data streaming (requires protobuf>=5.28)."""
            click.echo('Error: push command requires protobuf>=5.28.\n'
                        'Please upgrade:  pip install --upgrade protobuf')
            sys.exit(1)


_load_push_command()


def main():
    cli()


if __name__ == '__main__':
    main()
