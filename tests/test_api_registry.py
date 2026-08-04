# -*- coding: utf-8 -*-
"""本仓自查测试：wire method 注册表与契约覆盖完整性。."""
import ast
import re
from pathlib import Path

import pytest

# 纯静态分析，不碰真实接口
pytestmark = pytest.mark.unit

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TESTS_DIR = Path(__file__).resolve().parent

# 所有会构造 OpenApiRequest 的模块
_CLIENT_SOURCES = (
    'tigeropen/quote/quote_client.py',
    'tigeropen/trade/trade_client.py',
    'tigeropen/tiger_open_client.py',
)
_SERVICE_TYPES = 'tigeropen/common/consts/service_types.py'

# 公开但不发起 wire 调用的方法。加新条目前先确认它真的只是本地封装。
_LOCAL_ONLY_PUBLIC_METHODS = frozenset({
    'execute',                    # 泛用发送入口，method 由调用方给
    'get_bars_by_page',           # 分页封装，内部循环调 get_bars
    'get_future_bars_by_page',    # 分页封装，内部循环调 get_future_bars
    'refresh_token',              # 内部调 query_token
    'run',                        # 定时器线程的 run，不是 API 方法
})

# 棘轮清单：当前还没有任何用例覆盖的 wire method。
# 只允许变短。补齐一个用例就从这里删掉一行，否则 test_wire_method_is_exercised_by_test 会红。
_WIRE_METHODS_WITHOUT_TEST = frozenset({
})

# 测试里持有 client 的变量名
_CLIENT_ATTR_NAMES = frozenset({'client', 'quote_client', 'trade_client'})


def _openapi_request_constants(func_node):
    """取出一个函数体里 OpenApiRequest(...) 用到的常量名。

    两种写法都要认：OpenApiRequest(MARKET_STATE, biz_model=params) 和
    OpenApiRequest(method=USER_LICENSE)。
    """
    constants = set()
    for node in ast.walk(func_node):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == 'OpenApiRequest'):
            continue
        candidates = list(node.args)
        candidates += [kw.value for kw in node.keywords if kw.arg == 'method']
        for arg in candidates:
            if isinstance(arg, ast.Name):
                constants.add(arg.id)
    return constants


def _scan_clients():
    """返回 (方法名 -> wire 常量名集合, 公开方法名集合)。"""
    method_to_wire = {}
    public_methods = set()
    for rel_path in _CLIENT_SOURCES:
        tree = ast.parse((_REPO_ROOT / rel_path).read_text())
        for class_node in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            for func in (n for n in class_node.body
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
                if not func.name.startswith('_'):
                    public_methods.add(func.name)
                constants = _openapi_request_constants(func)
                if constants:
                    method_to_wire.setdefault(func.name, set()).update(constants)
    return method_to_wire, public_methods


def _wire_method_constants():
    """service_types.py 里声明的所有常量名。"""
    source = (_REPO_ROOT / _SERVICE_TYPES).read_text()
    pattern = re.compile(r'^([A-Z][A-Z0-9_]*)\s*=\s*[\'"][a-z0-9_]+[\'"]', re.M)
    return {m.group(1) for m in pattern.finditer(source)}


def _client_methods_called_in_tests():
    """测试里通过 client 调用过的方法名。

    识别 ``self.client.xxx()`` / ``client.xxx()`` / ``self.quote_client.xxx()`` 这几种写法。
    """
    called = set()
    for path in sorted(_TESTS_DIR.rglob('test_*.py')):
        for node in ast.walk(ast.parse(path.read_text())):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            owner = node.func.value
            if isinstance(owner, ast.Attribute) and owner.attr in _CLIENT_ATTR_NAMES:
                called.add(node.func.attr)
            elif isinstance(owner, ast.Name) and owner.id in _CLIENT_ATTR_NAMES:
                called.add(node.func.attr)
    return called


def test_no_dangling_wire_method_constant():
    """No dangling constants in service_types.py."""
    method_to_wire, _ = _scan_clients()
    declared = _wire_method_constants()
    referenced = set().union(*method_to_wire.values())

    dangling = sorted(declared - referenced)
    assert not dangling, (
        f'service_types.py 里有 {len(dangling)} 个常量没有任何 client 方法引用：{dangling}。'
        f'要么补上对应的 client 方法，要么删掉常量。')

    unknown = sorted(referenced - declared)
    assert not unknown, f'client 引用了 service_types.py 里不存在的常量：{unknown}'


def test_public_client_method_has_wire_method():
    """Public methods must either make a wire call or be in the local-only list."""
    method_to_wire, public_methods = _scan_clients()

    without_wire = {m for m in public_methods if m not in method_to_wire}
    unexpected = sorted(without_wire - _LOCAL_ONLY_PUBLIC_METHODS)
    assert not unexpected, (
        f'这些公开方法既不发起 wire 调用，也不在本地封装允许清单里：{unexpected}。'
        f'如果确实只是本地封装，加进 _LOCAL_ONLY_PUBLIC_METHODS 并写明理由。')

    stale = sorted(_LOCAL_ONLY_PUBLIC_METHODS - without_wire)
    assert not stale, (
        f'_LOCAL_ONLY_PUBLIC_METHODS 里这些条目已经不需要了（方法已发 wire 调用或已删除）：'
        f'{stale}，请从清单里移除。')


def test_wire_method_is_exercised_by_test():
    """Every wire method must be exercised by at least one test."""
    method_to_wire, _ = _scan_clients()
    referenced = set().union(*method_to_wire.values())
    called_methods = _client_methods_called_in_tests()

    covered = set()
    for method in called_methods:
        covered |= method_to_wire.get(method, set())
    uncovered = referenced - covered

    newly_uncovered = sorted(uncovered - _WIRE_METHODS_WITHOUT_TEST)
    assert not newly_uncovered, (
        f'这些 wire method 没有任何用例覆盖：{newly_uncovered}。'
        f'新增接口必须同时补用例，不要往 _WIRE_METHODS_WITHOUT_TEST 里加条目。')

    now_covered = sorted(_WIRE_METHODS_WITHOUT_TEST - uncovered)
    assert not now_covered, (
        f'这些 wire method 已经有用例覆盖了：{now_covered}，'
        f'请从 _WIRE_METHODS_WITHOUT_TEST 里删掉，让棘轮往前走一格。')
