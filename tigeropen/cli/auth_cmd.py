# -*- coding: utf-8 -*-
"""
Auth commands: login, login-device, logout, status, token.

Login and logout are deliberately separate from the business commands: a long-lived
process (or a script) should not pop up a browser on its own, so authorization is an
explicit user action. ``status`` and ``token`` are for inspecting the current session.

``login`` defaults to the device flow, which works the same in a remote shell and on a
desktop. ``--loopback`` selects the browser redirect flow.

Issuer / client_id come from the global ``--issuer`` / ``--client-id`` options (or the
``TIGEROPEN_OAUTH2_ISSUER`` / ``TIGEROPEN_CLIENT_ID`` env vars), so they are not
redeclared per command.
"""
import webbrowser

import click

from tigeropen.auth.oauth2 import OAuth2Exception
from tigeropen.cli.oauth2_config import build_session_manager
from tigeropen.cli.settings import resolve_settings


def _show_authorization_url(url):
    """Print the URL and try to open a browser. Printing is the guaranteed path."""
    click.echo('请在浏览器里打开下面的链接完成登录与授权：')
    click.echo()
    click.echo('  ' + url)
    click.echo()
    try:
        webbrowser.open(url)
        click.echo('已尝试自动打开浏览器；若未弹出，请手动复制上面的链接。')
    except Exception:
        click.echo('无法自动打开浏览器，请手动复制上面的链接。')
    click.echo('等待回调…')


def _show_device_code(device):
    click.echo()
    click.echo('请在另一台有浏览器的设备上打开：')
    click.echo()
    if device.verification_uri_complete:
        click.echo('  ' + device.verification_uri_complete)
        click.echo()
        click.echo('或者打开 %s 后输入验证码：' % device.verification_uri)
    else:
        click.echo('  ' + device.verification_uri)
        click.echo()
        click.echo('然后输入验证码：')
    click.echo()
    click.echo('      ' + device.user_code)
    click.echo()
    click.echo('等待授权…（%d 秒内有效）' % device.expires_in)


def _sessions_from_ctx(ctx):
    """Build an OAuth2SessionManager the same way the business commands do.

    Resolving this separately is what let a login store its token under one issuer while
    every later command looked for it under another.
    """
    settings = resolve_settings(ctx.obj or {})
    return build_session_manager(issuer=settings['issuer'],
                                 client_id=settings['client_id'])


def _print_env(sessions, config, token):
    click.echo('issuer     : %s' % sessions.issuer)
    click.echo('client_id  : %s' % sessions.client_id)
    if config is not None:
        click.echo('业务网关   : %s' % getattr(config, 'server_url', None))
        click.echo('行情网关   : %s' % getattr(config, 'quote_server_url', None))
    click.echo('scope      : %s' % (token.scope if token else None))
    if token is not None:
        click.echo('access token 还有 %d 秒到期' % (token.remaining_millis() // 1000))
        click.echo('有 refresh token: %s' % token.has_refresh_token())


@click.group('auth')
def auth():
    """Manage OAuth2 authentication."""
    pass


@auth.command('login')
@click.option('--loopback', is_flag=True,
              help='Use the browser redirect flow instead (loopback + PKCE).')
@click.option('--no-browser', is_flag=True,
              help='With --loopback, only print the URL instead of opening a browser.')
@click.pass_context
def auth_login(ctx, loopback, no_browser):
    """Authorize this machine.

    Device flow by default: a short code to enter on whatever device has a browser. Needs no
    local browser and no loopback port, so it behaves the same over SSH and in a container.

    ``--loopback`` uses the browser redirect flow instead, which binds the authorization to
    this process rather than to a code. Prefer it on a desktop.

    The token is stored under ~/.tiger/openapi/ with mode 0600 and reused by later runs.
    """
    sessions = _sessions_from_ctx(ctx)

    if loopback:
        def show(url):
            if no_browser:
                click.echo('请打开：\n  ' + url)
            else:
                _show_authorization_url(url)

        authorize = lambda: sessions.login_if_needed(show)
    else:
        authorize = lambda: sessions.login_with_device_code_if_needed(_show_device_code)

    try:
        token = authorize()
    except OAuth2Exception as e:
        click.echo('授权失败: %s' % e)
        click.echo('类别    : %s' % e.category.name)
        raise SystemExit(1)

    click.echo()
    click.echo('登录成功.')
    _print_env(sessions, None, token)


@auth.command('login-device')
@click.pass_context
def auth_login_device(ctx):
    """Authorize with the device flow (RFC 8628). Same as ``auth login``."""
    sessions = _sessions_from_ctx(ctx)

    def show(device):
        _show_device_code(device)

    try:
        token = sessions.login_with_device_code_if_needed(show)
    except OAuth2Exception as e:
        click.echo('授权失败: %s' % e)
        click.echo('类别    : %s' % e.category.name)
        raise SystemExit(1)

    click.echo()
    click.echo('登录成功.')
    _print_env(sessions, None, token)


@auth.command('logout')
@click.pass_context
def auth_logout(ctx):
    """Revoke the authorization on the server and clear the local token.

    The registered client_id is kept (it is this machine's application identity).
    """
    sessions = _sessions_from_ctx(ctx)
    try:
        revoked = sessions.logout()
    except OAuth2Exception as e:
        click.echo('登出失败: %s' % e)
        raise SystemExit(1)
    if revoked:
        click.echo('已登出，服务端已撤销。')
    else:
        click.echo('已清除本地 token；服务端撤销未确认（凭据可能仍有效，可重试）。')


@auth.command('status')
@click.pass_context
def auth_status(ctx):
    """Show the current OAuth2 session. Sends no requests."""
    sessions = _sessions_from_ctx(ctx)
    token = sessions.status()
    if token is None:
        click.echo('未授权。运行 tigeropen auth login 进行授权。')
        return
    click.echo('issuer     : %s' % sessions.issuer)
    click.echo('client_id  : %s' % sessions.client_id)
    click.echo('scope      : %s' % token.scope)
    click.echo('access token 还有 %d 秒到期' % (token.remaining_millis() // 1000))
    click.echo('有 refresh token: %s' % token.has_refresh_token())


@auth.command('token')
@click.pass_context
def auth_token(ctx):
    """Print the current access token (for scripts and debugging)."""
    sessions = _sessions_from_ctx(ctx)
    token = sessions.status()
    if token is None:
        click.echo('未授权。运行 tigeropen auth login 进行授权。', err=True)
        raise SystemExit(1)
    click.echo(token.access_token)
