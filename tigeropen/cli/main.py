# -*- coding: utf-8 -*-
"""
Main CLI entry point for tigeropen.
"""
import sys
import traceback

import click

from tigeropen import __VERSION__
from tigeropen.common.exceptions import ApiException
from tigeropen.cli.config_cmd import config
from tigeropen.cli.quote_cmd import quote
from tigeropen.cli.trade_cmd import trade
from tigeropen.cli.account_cmd import account

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
@click.option('--verbose', '-v', is_flag=True, help='Enable debug logging.')
@click.pass_context
def cli(ctx, config_path, output_format, language, verbose):
    """TigerOpen CLI - Tiger Brokers Open API command line tool."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config_path
    ctx.obj['format'] = output_format
    ctx.obj['language'] = language
    ctx.obj['verbose'] = verbose


@cli.command('version')
def version():
    """Print the SDK version."""
    click.echo(__VERSION__)


@cli.command('uninstall')
@click.option('--remove-config', is_flag=True, help='Also remove ~/.tigeropen/ configuration directory.')
@click.option('-y', '--yes', is_flag=True, help='Skip confirmation prompts.')
def uninstall(remove_config, yes):
    """Uninstall tigeropen and optionally remove configuration."""
    import subprocess
    import shutil
    from pathlib import Path

    if not yes:
        msg = 'Uninstall tigeropen?'
        if remove_config:
            msg += ' (including ~/.tigeropen/ config directory)'
        if not click.confirm(msg):
            raise SystemExit(0)

    # Remove config directory first (before pip uninstall removes the CLI itself)
    if remove_config:
        config_dir = Path.home() / '.tigeropen'
        if config_dir.exists():
            shutil.rmtree(config_dir)
            click.echo(f'Removed {config_dir}')
        else:
            click.echo(f'{config_dir} not found, skipping.')

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


cli.add_command(config)
cli.add_command(quote)
cli.add_command(trade)
cli.add_command(account)


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
