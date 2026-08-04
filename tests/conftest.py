# -*- coding: utf-8 -*-
"""pytest 全局配置：测试分层 marker 与 L1 禁网守卫。

分层约定（与其他语言 SDK 口径一致）：

============  ==================================  ============================
层             含义                                选择方式
============  ==================================  ============================
L1 unit       零凭据、零网络                        默认（不设 TIGER_RUN_INTEG）
L2 contract   真实接口，只读，断言字段与类型          TIGER_RUN_INTEG=true -m "not unit and not integ"
L3 integ      真实接口，含写操作                     TIGER_RUN_INTEG=true -m integ
============  ==================================  ============================

marker 语义是「这个用例需要什么」，不是「它属于哪一层」：

- ``unit``  —— 永远不会碰真实接口的用例（纯函数、序列化、配置解析等）。
- ``integ`` —— 涉及下单、撤单、行权、划转等写操作，只应手动或定时触发。
- 不打 marker —— 只读接口用例。mock 模式下是 L1，真实模式下是 L2。

L1 禁网守卫见 ``_install_network_guard``。
"""
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
    """L1 单测尝试访问网络。

    出现这个异常说明某个用例漏了 mock，或者双分支判断写反了。不要通过放开守卫来
    绕过它 —— L1 的定义就是零网络。需要连真实接口的用例请打 integ marker，
    或放到 TIGER_RUN_INTEG=true 下运行。
    """


def _install_network_guard():
    """禁止 L1 单测访问网络（loopback 除外）。

    历史问题：test_get_future_exchanges 的 is_mock 分支曾写反，导致 mock 模式下
    真的向线上网关发请求；setUp 里 enable_dynamic_domain 曾跟随 is_mock，导致每个
    用例构造 config 时都去拉一次域名配置。两者在有真实凭据的机器上都是「绿」的，
    只有禁网才能暴露。
    """

    def guarded_connect(self, address, *args, **kwargs):
        if _is_loopback(address):
            return _original_connect(self, address, *args, **kwargs)
        raise NetworkAccessInUnitTest(
            f'unit test attempted to reach {address!r}; '
            f'mock the request, or mark it as integ and run with TIGER_RUN_INTEG=true')

    def guarded_connect_ex(self, address, *args, **kwargs):
        if _is_loopback(address):
            return _original_connect_ex(self, address, *args, **kwargs)
        raise NetworkAccessInUnitTest(
            f'unit test attempted to reach {address!r}; '
            f'mock the request, or mark it as integ and run with TIGER_RUN_INTEG=true')

    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = guarded_connect_ex


def _remove_network_guard():
    socket.socket.connect = _original_connect
    socket.socket.connect_ex = _original_connect_ex


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'unit: 永远不碰真实接口的用例（纯函数、序列化、配置解析等）')
    config.addinivalue_line(
        'markers', 'integ: 涉及写操作的真实接口用例，只应手动或定时触发')
    if not is_integ_run():
        _install_network_guard()


def pytest_unconfigure(config):
    _remove_network_guard()
