# -*- coding: utf-8 -*-
"""集成测试专用工具:

- ``is_market_trading`` / ``is_market_open_including_extended``:
  查询 Tiger ``market_state`` 判定市场是否在盘中(或含盘前/盘后)。
  盘中时集成测试必须实跑;非盘中时可以合法 skip.
- ``resolve_us_option_identifier`` / ``resolve_hk_option_symbol``:
  动态从行情接口拉最新期权合约,避免依赖已过期的硬编码 identifier.
- ``place_order_with_rate_limit_handling``:
  在网关限流(``too_many_requests``)时先做指数退避重试,重试仍失败
  则以 ``pytest.skip`` 标记为合法边界,而不是让集成测试报红。

上述接口调用会缓存在进程内(``functools.lru_cache``),同一 test session
内不会重复打网关.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from functools import lru_cache
from typing import Optional

import pytest
import pytz

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate-limit-aware place_order wrapper
# ---------------------------------------------------------------------------

# 网关限流关键词。命中任一片段时视为限流,按退避 / skip 处理。
_RATE_LIMIT_KEYWORDS = (
    "too_many_requests",
    "rate limit",
    "requestrateexceedlimit",
    "rate exceeded",
)


def place_order_with_rate_limit_handling(
    client,
    order,
    *,
    retries: int = 2,
    initial_backoff: float = 1.0,
    pre_delay: float = 0.5,
):
    """调用 ``client.place_order(order=order)``,自动处理网关限流。

    - 每次调用前先 ``sleep(pre_delay)`` 平滑请求节奏。
    - 命中限流关键词时按指数退避重试 ``retries`` 次。
    - 重试后仍限流:调用 ``pytest.skip`` 把测试标记为跳过 —
      账户级 QPS 上限是合法 CI 边界,不应误报为 fail。
    - 其它 ``ApiException`` / 异常原样上抛。

    返回 ``client.place_order`` 的返回值(通常是 int order id)。
    """
    # Import inside the function to keep module import cheap and avoid
    # any circular-import risk with tigeropen internals.
    from tigeropen.common.exceptions import ApiException

    if pre_delay and pre_delay > 0:
        time.sleep(pre_delay)

    delay = initial_backoff
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            return client.place_order(order=order)
        except ApiException as e:
            msg = str(e).lower()
            if not any(k in msg for k in _RATE_LIMIT_KEYWORDS):
                # Not a rate-limit error — surface immediately.
                raise
            last_exc = e
            if attempt < retries:
                logger.info(
                    "place_order rate-limited (attempt %d/%d); backing off %.1fs",
                    attempt + 1, retries + 1, delay,
                )
                time.sleep(delay)
                delay *= 2
                continue
            # Retries exhausted — skip rather than fail.
            pytest.skip(
                f"gateway rate limit hit after {retries + 1} attempts: {e}"
            )

    # Defensive: pytest.skip raises, so we normally never reach here.
    pytest.skip(f"gateway rate limit hit: {last_exc}")


# ``trading_status`` 枚举来源:见 tigeropen.quote.quote_client.get_market_status
# 的 docstring 与 market_status_response.py。
_MAIN_SESSION = {'TRADING'}
_EXTENDED_SESSION = {'TRADING', 'PRE_HOUR_TRADING', 'POST_HOUR_TRADING'}

# Fallback 主时段(小时:分钟, 本地时区)。周末永远视为休市。
_MARKET_TIMEZONES = {
    'US': pytz.timezone('US/Eastern'),
    'HK': pytz.timezone('Asia/Hong_Kong'),
    'CN': pytz.timezone('Asia/Shanghai'),
    'SG': pytz.timezone('Asia/Singapore'),
}

# Regular main-session windows. Multiple ranges support lunch breaks.
_MAIN_WINDOWS = {
    'US': [((9, 30), (16, 0))],
    'HK': [((9, 30), (12, 0)), ((13, 0), (16, 0))],
    'CN': [((9, 30), (11, 30)), ((13, 0), (15, 0))],
    'SG': [((9, 0), (12, 0)), ((13, 0), (17, 0))],
}

# Extended-hours windows (US 有真实盘前/盘后)。其它市场基本与主时段一致。
_EXTENDED_WINDOWS = {
    'US': [((4, 0), (20, 0))],
    'HK': [((9, 0), (16, 10))],
    'CN': [((9, 15), (15, 0))],
    'SG': [((8, 30), (17, 30))],
}


def _normalize_market(market) -> str:
    if hasattr(market, 'value'):
        return str(market.value).upper()
    return str(market).upper()


def _in_windows_local(market_key: str, windows: dict) -> bool:
    """Check whether current local time in ``market_key`` timezone falls in any window."""
    tz = _MARKET_TIMEZONES.get(market_key)
    if tz is None:
        return False
    now = datetime.now(tz)
    if now.weekday() >= 5:  # Saturday/Sunday
        return False
    for (h1, m1), (h2, m2) in windows.get(market_key, []):
        start = now.replace(hour=h1, minute=m1, second=0, microsecond=0)
        end = now.replace(hour=h2, minute=m2, second=0, microsecond=0)
        if start <= now <= end:
            return True
    return False


def _fetch_trading_status(quote_client, market: str) -> Optional[str]:
    """Call ``get_market_status``; return trading_status string or None on failure."""
    try:
        result = quote_client.get_market_status(market=market)
    except Exception as e:  # noqa: BLE001 - fall back to time-based check
        logger.warning('get_market_status(%s) failed: %s', market, e)
        return None
    if not result:
        return None
    for item in result:
        m = getattr(item, 'market', None)
        if m and str(m).upper() == market:
            status = getattr(item, 'trading_status', None)
            return str(status).upper() if status else None
    # Fall back to the first entry when the API didn't echo the market field.
    first = result[0]
    status = getattr(first, 'trading_status', None)
    return str(status).upper() if status else None


@lru_cache(maxsize=32)
def _cached_trading_status(quote_client_id: int, market: str) -> Optional[str]:
    """Cache key includes the quote_client identity so tests reusing the same
    client share results, but different clients (rare in one run) don't collide."""
    # The real client object is looked up via a module-level registry — see
    # ``_get_status_for_client`` below. lru_cache can't hash arbitrary objects.
    return _CLIENT_REGISTRY.get(quote_client_id) \
        and _fetch_trading_status(_CLIENT_REGISTRY[quote_client_id], market)


_CLIENT_REGISTRY: dict = {}


def _get_status(quote_client, market: str) -> Optional[str]:
    key = id(quote_client)
    _CLIENT_REGISTRY[key] = quote_client
    return _cached_trading_status(key, market)


def is_market_trading(quote_client, market) -> bool:
    """True when the given market is in its main trading session.

    Prefers ``get_market_status`` (trading_status == 'TRADING'); on any failure
    falls back to a pytz-based hard-coded main-session window.
    """
    m = _normalize_market(market)
    status = _get_status(quote_client, m)
    if status is not None:
        return status in _MAIN_SESSION
    return _in_windows_local(m, _MAIN_WINDOWS)


def is_market_open_including_extended(quote_client, market) -> bool:
    """True when the market is in main session or pre/post-market."""
    m = _normalize_market(market)
    status = _get_status(quote_client, m)
    if status is not None:
        return status in _EXTENDED_SESSION
    return _in_windows_local(m, _EXTENDED_WINDOWS)


# --------------------------------------------------------------------------- #
# Option identifier resolvers
# --------------------------------------------------------------------------- #

_OPTION_CACHE: dict = {}


def _pick_atm_row(chain):
    """Given an option chain DataFrame, return the row closest to ATM.

    Uses row index median as an ATM proxy when we don't have a spot price
    (Tiger's option-chain already filters by ITM/OTM window in most fixtures,
    so mid-row ≈ ATM in practice)."""
    if chain is None or chain.empty:
        return None
    if 'put_call' in chain.columns:
        calls = chain[chain['put_call'] == 'CALL']
        if calls.empty:
            calls = chain
    else:
        calls = chain
    if calls.empty:
        return None
    if 'strike' in calls.columns:
        calls_sorted = calls.sort_values('strike').reset_index(drop=True)
    else:
        calls_sorted = calls.reset_index(drop=True)
    return calls_sorted.iloc[len(calls_sorted) // 2]


def resolve_us_option_identifier(quote_client, symbol: str = 'AAPL') -> Optional[str]:
    """Return a fresh AAPL option identifier string (e.g. 'AAPL 250919C00250000').

    Strategy: nearest expiration → get_option_chain → mid-strike CALL → identifier.
    Returns None if any step yields empty data (caller decides whether to skip
    or fail based on trading hours)."""
    cache_key = ('us_option_identifier', symbol, id(quote_client))
    if cache_key in _OPTION_CACHE:
        return _OPTION_CACHE[cache_key]

    try:
        # get_option_expirations accepts either a list or bare string.
        expirations = quote_client.get_option_expirations(symbols=[symbol])
    except Exception as e:  # noqa: BLE001
        logger.warning('get_option_expirations(%s) failed: %s', symbol, e)
        _OPTION_CACHE[cache_key] = None
        return None

    if expirations is None or expirations.empty:
        _OPTION_CACHE[cache_key] = None
        return None
    if 'timestamp' not in expirations.columns:
        _OPTION_CACHE[cache_key] = None
        return None
    try:
        expiry_ts = int(expirations.iloc[0]['timestamp'])
    except (KeyError, ValueError, TypeError):
        _OPTION_CACHE[cache_key] = None
        return None

    try:
        chain = quote_client.get_option_chain(
            symbol=symbol, expiry=expiry_ts,
            timezone='America/New_York', return_greek_value=True)
    except Exception as e:  # noqa: BLE001
        logger.warning('get_option_chain(%s, %s) failed: %s', symbol, expiry_ts, e)
        _OPTION_CACHE[cache_key] = None
        return None

    row = _pick_atm_row(chain)
    if row is None:
        _OPTION_CACHE[cache_key] = None
        return None
    identifier = str(row.get('identifier', '')).strip() if hasattr(row, 'get') else str(row['identifier']).strip()
    if not identifier:
        _OPTION_CACHE[cache_key] = None
        return None
    _OPTION_CACHE[cache_key] = identifier
    return identifier


def resolve_us_option_identifiers(quote_client, symbol: str = 'AAPL',
                                  count: int = 2) -> list:
    """Return up to ``count`` US option identifiers for ``symbol``."""
    cache_key = ('us_option_identifiers', symbol, count, id(quote_client))
    if cache_key in _OPTION_CACHE:
        return _OPTION_CACHE[cache_key]

    try:
        expirations = quote_client.get_option_expirations(symbols=[symbol])
    except Exception as e:  # noqa: BLE001
        logger.warning('get_option_expirations(%s) failed: %s', symbol, e)
        _OPTION_CACHE[cache_key] = []
        return []
    if expirations is None or expirations.empty or 'timestamp' not in expirations.columns:
        _OPTION_CACHE[cache_key] = []
        return []
    try:
        expiry_ts = int(expirations.iloc[0]['timestamp'])
    except (KeyError, ValueError, TypeError):
        _OPTION_CACHE[cache_key] = []
        return []
    try:
        chain = quote_client.get_option_chain(
            symbol=symbol, expiry=expiry_ts,
            timezone='America/New_York', return_greek_value=True)
    except Exception as e:  # noqa: BLE001
        logger.warning('get_option_chain(%s, %s) failed: %s', symbol, expiry_ts, e)
        _OPTION_CACHE[cache_key] = []
        return []

    if chain is None or chain.empty or 'identifier' not in chain.columns:
        _OPTION_CACHE[cache_key] = []
        return []
    identifiers = [str(x).strip() for x in chain['identifier'].tolist() if str(x).strip()]
    result = identifiers[:count]
    _OPTION_CACHE[cache_key] = result
    return result


def resolve_hk_option_symbol(trade_client, underlying: str = '00700') -> Optional[str]:
    """Return the first available HK option contract_id for ``underlying``.

    Uses ``get_derivative_contracts`` with a 60-day forward expiry window."""
    from datetime import timedelta

    from tigeropen.common.consts import SecurityType
    cache_key = ('hk_option', underlying, id(trade_client))
    if cache_key in _OPTION_CACHE:
        return _OPTION_CACHE[cache_key]

    future_expiry = (datetime.now() + timedelta(days=60)).strftime('%Y%m%d')
    try:
        contracts = trade_client.get_derivative_contracts(
            symbol=underlying, sec_type=SecurityType.OPT, expiry=future_expiry)
    except Exception as e:  # noqa: BLE001
        logger.warning('get_derivative_contracts(%s) failed: %s', underlying, e)
        _OPTION_CACHE[cache_key] = None
        return None

    if not contracts:
        _OPTION_CACHE[cache_key] = None
        return None
    result = contracts[0]
    _OPTION_CACHE[cache_key] = result
    return result


def reset_cache() -> None:
    """Clear all cached results — primarily for unit tests of these helpers."""
    _CLIENT_REGISTRY.clear()
    _cached_trading_status.cache_clear()
    _OPTION_CACHE.clear()
