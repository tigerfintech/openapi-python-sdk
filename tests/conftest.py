# -*- coding: utf-8 -*-
"""pytest configuration: markers and network guard for unit tests."""
import socket

from tests.support import is_integ_run

_LOOPBACK_HOSTS = {'127.0.0.1', '::1', 'localhost'}

_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex


def _is_loopback(address):
    if isinstance(address, (tuple, list)) and address:
        return str(address[0]) in _LOOPBACK_HOSTS
    return False


class NetworkAccessInUnitTest(RuntimeError):
    """Unit test attempted non-loopback network access."""


def _install_network_guard():
    """Patch socket.connect to block non-loopback access."""

    def guarded_connect(self, address, *args, **kwargs):
        if _is_loopback(address):
            return _original_connect(self, address, *args, **kwargs)
        raise NetworkAccessInUnitTest(
            f'unit test attempted to reach {address!r}; mock the request or use TIGER_RUN_INTEG=true')

    def guarded_connect_ex(self, address, *args, **kwargs):
        if _is_loopback(address):
            return _original_connect_ex(self, address, *args, **kwargs)
        raise NetworkAccessInUnitTest(
            f'unit test attempted to reach {address!r}; mock the request or use TIGER_RUN_INTEG=true')

    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = guarded_connect_ex


def _remove_network_guard():
    socket.socket.connect = _original_connect
    socket.socket.connect_ex = _original_connect_ex


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'unit: pure unit tests, no real API calls')
    config.addinivalue_line(
        'markers', 'integ: write-operation tests, manual trigger only')
    if not is_integ_run():
        _install_network_guard()


def pytest_unconfigure(config):
    _remove_network_guard()
