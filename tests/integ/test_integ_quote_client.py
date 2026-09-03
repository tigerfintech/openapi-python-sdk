# -*- coding: utf-8 -*-
"""Integration tests - require real API credentials."""
import logging
import time
import unittest

import pandas as pd
import pytest

from tigeropen.common.consts import Market, TradingSession, BarPeriod, CapitalPeriod, Valuation, Income, \
    OptionAnalysisPeriod, SortDirection, FinancialReportPeriodType, SecurityType
from tigeropen.common.consts.filter_fields import StockField, FinancialPeriod, MultiTagField  # noqa: F401 — MultiTagField used in test_get_market_scanner_tags
from tigeropen.quote.domain.filter import StockFilter, SortFilterData, OptionFilter, WarrantFilterItem
from tigeropen.quote.domain.quote_brief import QuoteBrief
from tigeropen.quote.domain.option_analysis import OptionAnalysis
from tigeropen.quote.domain.capital_distribution import CapitalDistribution
from tigeropen.quote.domain.addon_entitlement import AddonEntitlement
from tigeropen.quote.domain.stock_broker import StockBroker
from tigeropen.quote.domain.filter import ScannerResult
from tigeropen.quote.quote_client import QuoteClient
from tests.integ._helpers import is_market_trading
from tests.support import integ_client_config, is_integ_run

logger = logging.getLogger(__name__)


@pytest.mark.skipif(not is_integ_run(), reason="requires TIGER_RUN_INTEG=true")
class TestIntegQuoteClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client_config = integ_client_config()
        cls.client = QuoteClient(cls.client_config, logger=logger, is_grab_permission=False)

    # -- Helpers: dynamically fetch expirable identifiers --

    def _get_option_expiry(self, symbol='AAPL', market=Market.US):
        """Prefer an option expiry 14-42 days out; fall back to the second listed expiry."""
        expirations = self.client.get_option_expirations(symbols=[symbol], market=market)
        if expirations is None or expirations.empty:
            return None
        now_ms = int(time.time() * 1000)
        min_ms = now_ms + 14 * 24 * 3600 * 1000
        max_ms = now_ms + 42 * 24 * 3600 * 1000
        if 'timestamp' in expirations.columns:
            candidates = expirations[
                (expirations['timestamp'] >= min_ms) & (expirations['timestamp'] <= max_ms)
            ]
            if not candidates.empty:
                return int(candidates.iloc[0]['timestamp'])
        idx = 1 if len(expirations) > 1 else 0
        return int(expirations.iloc[idx]['timestamp'])

    @staticmethod
    def _num_or_zero(row, column):
        if column not in row or pd.isna(row[column]):
            return 0.0
        try:
            return float(row[column])
        except (TypeError, ValueError):
            return 0.0

    def _rank_option_chain(self, chain, spot):
        rows = []
        for _, row in chain.iterrows():
            identifier = str(row.get('identifier', '')).strip()
            if not identifier:
                continue
            strike = self._num_or_zero(row, 'strike')
            atm_distance = abs(strike - spot) if strike and spot else 0.0
            active = (
                self._num_or_zero(row, 'volume') > 0
                or self._num_or_zero(row, 'latest_price') > 0
                or (self._num_or_zero(row, 'bid_price') > 0 and self._num_or_zero(row, 'ask_price') > 0)
            )
            rows.append((0 if active else 1, atm_distance, identifier))
        rows.sort(key=lambda item: (item[0], item[1]))
        return [identifier for _, _, identifier in rows]

    def _get_option_identifiers(self, symbol='AAPL', market=Market.US, count=2):
        """Fetch option identifiers from the chain; empty list if unavailable."""
        self._last_option_resolution_context = {'symbol': symbol, 'market': market}
        expiry = self._get_option_expiry(symbol, market)
        self._last_option_resolution_context['expiry'] = expiry
        if expiry is None:
            return []
        option_filter = OptionFilter(implied_volatility_min=0.05, implied_volatility_max=1,
                                     delta_min=0, delta_max=1,
                                     open_interest_min=10,
                                     in_the_money=True)
        self._last_option_resolution_context['option_filter'] = option_filter.__dict__
        chain = self.client.get_option_chain(symbol=symbol, expiry=expiry, market=market,
                                             timezone='America/New_York',
                                             option_filter=option_filter,
                                             return_greek_value=True)
        self._last_option_resolution_context['chain'] = chain
        if chain is None or chain.empty:
            return []
        spot = 0.0
        try:
            briefs = self.client.get_stock_briefs(symbols=[symbol], sec_type=SecurityType.STK)
            if briefs is not None and not briefs.empty and 'latest_price' in briefs.columns:
                spot = float(briefs.iloc[0]['latest_price'])
        except Exception:  # noqa: BLE001 - spot is only a ranking hint
            spot = 0.0
        self._last_option_resolution_context['spot'] = spot
        identifiers = self._rank_option_chain(chain, spot)
        self._last_option_resolution_context['identifiers'] = identifiers[:count]
        return identifiers[:count]

    def _require_option_identifiers(self, symbol='AAPL', market=Market.US, count=1):
        """Return fresh option identifiers or trigger skip/fail based on trading hours.

        During main-session trading, empty results indicate a real bug and we
        fail; outside trading hours we accept an empty response and skip.
        """
        identifiers = self._get_option_identifiers(symbol=symbol, market=market, count=count)
        if identifiers and len(identifiers) >= count:
            return identifiers
        market_key = market.value if hasattr(market, 'value') else str(market)
        if is_market_trading(self.client, market_key):
            context = self._format_failure_context(
                **getattr(self, '_last_option_resolution_context', {}))
            self.fail(
                f"Could not resolve {count} {market_key} option identifier(s) "
                f"for {symbol} during {market_key} main trading session — "
                f"option-chain resolver returned empty when data should exist; {context}")
        self.skipTest(
            f"No {market_key} option identifier available for {symbol} "
            f"— {market_key} not in main trading session")

    @staticmethod
    def _format_failure_context(**kwargs):
        parts = []
        for key, value in kwargs.items():
            if isinstance(value, pd.DataFrame):
                rendered = (
                    f"DataFrame(shape={value.shape}, columns={list(value.columns)}, "
                    f"head=\n{value.head(5).to_string()})")
            else:
                rendered = repr(value)
            if len(rendered) > 3000:
                rendered = rendered[:3000] + "...<truncated>"
            parts.append(f"{key}={rendered}")
        return "; ".join(parts)

    def _get_future_contract_code(self, exchange='CME', future_type='ES'):
        """Fetch an active future contract code, preferring the current ES contract."""
        current = self.client.get_current_future_contract(future_type=future_type)
        if current is not None and not current.empty and 'contract_code' in current.columns:
            raw_code = current.iloc[0]['contract_code']
            if pd.notna(raw_code):
                code = str(raw_code).strip()
                if code and code.lower() not in ('none', 'nan'):
                    return code
        contracts = self.client.get_future_contracts(exchange=exchange)
        if contracts is None or contracts.empty:
            return None
        if 'type' in contracts.columns:
            typed = contracts[contracts['type'] == future_type]
            if not typed.empty:
                contracts = typed
        raw_code = contracts.iloc[0]['contract_code']
        if pd.isna(raw_code):
            return None
        code = str(raw_code).strip()
        return code if code and code.lower() not in ('none', 'nan') else None

    def _is_empty(self, result):
        if isinstance(result, pd.DataFrame):
            return result.empty
        if isinstance(result, (list, dict)):
            return not result
        return result is None

    def _skip_if_empty(self, result, name, market='US', **context):
        """Handle empty realtime results:

        - Non-trading hours → skip (server legitimately returns no data)
        - Trading hours → fail (a real bug: server returned empty during a
          live session)
        """
        if not self._is_empty(result):
            return
        if is_market_trading(self.client, market):
            details = self._format_failure_context(result=result, **context)
            self.fail(
                f"{name} empty during {market} main trading session — this "
                "indicates the server returned no data when the market was "
                f"live; treat as bug rather than skip; {details}")
        self.skipTest(f"{name} empty — {market} not in main trading session")

    def test_get_symbols(self):
        result = self.client.get_symbols(market='US')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], str)
        self.assertTrue(len(result[0]) > 0)
        logger.debug(f"Symbols count: {len(result)}")

    def test_get_market_status(self):
        result = self.client.get_market_status(market=Market.US)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        item = result[0]
        self.assertIsNotNone(item.market)
        self.assertIsNotNone(item.status)
        self.assertIsNotNone(item.trading_status)
        self.assertIsNotNone(item.open_time)
        logger.debug(f"Market Status: {result}")

    def test_get_symbol_names(self):
        result = self.client.get_symbol_names(market='US')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, tuple)
        self.assertEqual(len(first), 2)
        self.assertTrue(len(first[0]) > 0)
        self.assertIsNotNone(first[1])
        logger.debug(f"Symbol Names count: {len(result)}")

    def test_get_trade_metas(self):
        result = self.client.get_trade_metas(symbols=['AAPL', 'MSFT'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('AAPL', result['symbol'].values)
        self.assertIn('MSFT', result['symbol'].values)
        self.assertIn('lot_size', result.columns)
        self.assertIn('min_tick', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['lot_size'], 0)
        self.assertGreater(first['min_tick'], 0)
        logger.debug(f"Trade Metas:\n {result}")

    def test_get_stock_briefs(self):
        result = self.client.get_stock_briefs(symbols=['AAPL'],
                                              include_hour_trading=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]['symbol'], 'AAPL')
        self.assertGreater(result.iloc[0]['latest_price'], 0)
        self.assertGreaterEqual(result.iloc[0]['volume'], 0)
        self.assertGreater(result.iloc[0]['high'], 0)
        self.assertGreater(result.iloc[0]['low'], 0)
        logger.debug(f"Stock Briefs:\n {result}")

    def test_get_briefs(self):
        result = self.client.get_briefs(symbols=['AAPL'],
                                        include_hour_trading=True,
                                        include_ask_bid=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        brief = result[0]
        self.assertIsInstance(brief, QuoteBrief)
        self.assertEqual(brief.symbol, 'AAPL')
        self.assertIsNotNone(brief.market)
        self.assertIsNotNone(brief.sec_type)
        self.assertGreater(brief.latest_price, 0)
        logger.debug(f"Briefs: {result}")

    def test_get_stock_delay_briefs(self):
        result = self.client.get_stock_delay_briefs(symbols=['AAPL'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0].symbol, 'AAPL')
        self.assertGreater(result.iloc[0].pre_close, 0)
        self.assertGreaterEqual(result.iloc[0].volume, 0)
        logger.debug(f"Stock Delay Briefs:\n {result}")

    def test_get_timeline(self):
        result = self.client.get_timeline(symbols=['AAPL'],
                                          # trade_session=TradingSession.OverNight
                                          )
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Timeline')
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Timeline (real):\n {result}")

    def test_get_timeline_history(self):
        # Use yesterday to ensure data exists
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        result = self.client.get_timeline_history(symbols=['AAPL'],
                                                  date=yesterday,
                                                  trade_session=TradingSession.OverNight
                                                  )
        self._skip_if_empty(result, 'Timeline History')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['price'], 0)
        logger.debug(f"Timeline History (real):\n {result}")

    def test_get_bars(self):
        result = self.client.get_bars(symbols=['AAPL', 'MSFT'],
                                      period=BarPeriod.DAY,
                                      limit=10,
                                      page_token='',
                                      # trade_session=TradingSession.OverNight
                                      )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('high', result.columns)
        self.assertIn('low', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertIn(first['symbol'], ['AAPL', 'MSFT'])
        self.assertGreater(first['open'], 0)
        self.assertGreater(first['close'], 0)
        self.assertGreater(first['high'], 0)
        self.assertGreater(first['low'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Bars (real):\n {result}")

    def test_get_trade_ticks(self):
        result = self.client.get_trade_ticks(symbols=['AAPL'],
                                             # trade_session=TradingSession.OverNight
                                             )
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Trade Ticks')
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Trade Ticks (real): \n {result}")

    def test_get_short_interest(self):
        self.skipTest("Account does not support short interest API method")
        result = self.client.get_short_interest(symbols=['AAPL'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        if not result.empty:
            self.assertEqual(result.iloc[0]['symbol'], 'AAPL')
            self.assertIn('short_interest', result.columns)
            self.assertGreaterEqual(result.iloc[0]['short_interest'], 0)
        logger.debug(f"Short Interest:\n {result}")

    def test_get_depth_quote(self):
        # 实际调用API
        result = self.client.get_depth_quote(symbols=['AAPL', 'MSFT'],
                                             market=Market.US,
                                             # trade_session=TradingSession.OverNight
                                             )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn('AAPL', result)
        aapl = result['AAPL']
        self.assertEqual(aapl['symbol'], 'AAPL')
        self.assertIsInstance(aapl['asks'], list)
        self.assertIsInstance(aapl['bids'], list)
        if not aapl['asks'] or not aapl['bids']:
            # 盘中订单簿不应为空；非盘中(如盘前/盘后/休市)允许为空,
            # 走到这里说明 SDK 请求/解析链路已验证通过,直接 pass 而非 skip。
            if is_market_trading(self.client, Market.US):
                self.fail(f"empty order book for AAPL during main trading session: {aapl}")
            return
        self.assertGreater(len(aapl['asks']), 0)
        self.assertGreater(len(aapl['bids']), 0)
        self.assertGreater(aapl['asks'][0][0], 0)
        self.assertGreater(aapl['bids'][0][0], 0)
        logger.debug(f"Depth Quote (real):\n {result}")

    def test_get_option_expirations(self):
        result = self.client.get_option_expirations(symbols=['AAPL'],
                                                    market=Market.US)  # todo hk stock
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('date', result.columns)
        self.assertIn('timestamp', result.columns)
        self.assertEqual(result.iloc[0]['symbol'], 'AAPL')
        self.assertIsNotNone(result.iloc[0]['date'])
        logger.debug(f"Option Expirations (real):\n {result}")

    def test_get_option_chain(self):
        expiry = self._get_option_expiry(symbol='AAPL', market=Market.US)
        if expiry is None:
            # Expirations are static reference data — treat missing as a real
            # server issue during trading hours; skip if the market is closed.
            if is_market_trading(self.client, 'US'):
                self.fail("get_option_expirations returned empty for AAPL "
                          "during US main trading session")
            self.skipTest("No option expiry available for AAPL — US market closed")
        option_filter = OptionFilter(implied_volatility_min=0.05, implied_volatility_max=1, delta_min=0,
                                     delta_max=1,
                                     open_interest_min=10, in_the_money=True)
        result = self.client.get_option_chain(symbol='AAPL',
                                              expiry=expiry,
                                              market=Market.US,
                                              timezone='America/New_York',
                                              option_filter=option_filter,
                                              return_greek_value=True)
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Option Chain', market='US', symbol='AAPL', expiry=expiry,
                            option_filter=option_filter.__dict__, return_greek_value=True)
        self.assertIn('symbol', result.columns)
        self.assertIn('identifier', result.columns)
        self.assertIn('strike', result.columns)
        self.assertIn('put_call', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertTrue(len(str(first['identifier']).strip()) > 0)
        self.assertIsNotNone(first['strike'])
        logger.debug(f"Option Chain (real):\n {result}")

    def test_get_option_brief(self):
        identifiers = self._require_option_identifiers(symbol='AAPL', market=Market.US, count=1)
        result = self.client.get_option_briefs(
            identifiers=[identifiers[0]])
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Option Brief', market='US', identifiers=[identifiers[0]])
        self.assertIn('identifier', result.columns)
        self.assertIn('symbol', result.columns)
        first = result.iloc[0]
        self.assertIn('AAPL', str(first['identifier']))
        self.assertIsNotNone(first['symbol'])
        self.assertGreater(first['multiplier'], 0)
        logger.debug(f"Option Brief (real):\n {result}")

    def test_get_option_bars(self):
        identifiers = self._require_option_identifiers(symbol='AAPL', market=Market.US, count=1)
        result = self.client.get_option_bars(
            identifiers=[identifiers[0]], period=BarPeriod.DAY, limit=5,
        )
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Option Bars', market='US', identifiers=[identifiers[0]],
                            period=BarPeriod.DAY, limit=5)
        self.assertIn('identifier', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['identifier']).strip()) > 0)
        self.assertGreater(first['open'], 0)
        self.assertGreater(first['close'], 0)
        logger.debug(f"Option Bars (real):\n {result}")

    def test_get_option_trade_ticks(self):
        identifiers = self._require_option_identifiers(symbol='AAPL', market=Market.US, count=1)
        result = self.client.get_option_trade_ticks(
            identifiers=[identifiers[0]])
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Option Trade Ticks', market='US', identifiers=[identifiers[0]])
        self.assertIn('identifier', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['identifier']).strip()) > 0)
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Option Trade Ticks (real):\n {result}")

    def test_get_option_symbols(self):
        result = self.client.get_option_symbols(market=Market.HK)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('name', result.columns)
        self.assertIn('underlying_symbol', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['symbol']).strip()) > 0)
        self.assertIsNotNone(first['name'])
        logger.debug(f"Option Symbols (real):\n {result}")

    def test_get_option_depth(self):
        identifiers = self._require_option_identifiers(symbol='AAPL', market=Market.US, count=2)
        result = self.client.get_option_depth(identifiers=identifiers,
                                              market=Market.US)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self._skip_if_empty(result, 'Option Depth', market='US', identifiers=identifiers)
        for key, val in result.items():
            self.assertIn('asks', val)
            self.assertIn('bids', val)
            self.assertIsInstance(val['asks'], list)
            self.assertIsInstance(val['bids'], list)
            self.assertGreater(len(val['asks']), 0)
            self.assertGreater(len(val['bids']), 0)
            # Option depth prices can be 0 for illiquid contracts
            self.assertGreaterEqual(val['asks'][0][0], 0)
            self.assertGreaterEqual(val['bids'][0][0], 0)
        logger.debug(f"Option Depth (real): {result}")

    def test_get_option_timeline(self):
        """Option timeline always exercises the wire path. Content is only
        asserted in-hours — empty response out-of-hours is expected because
        the endpoint returns realtime data.
        """
        identifiers = self._require_option_identifiers(symbol='AAPL', market=Market.US, count=1)
        result = self.client.get_option_timeline(identifiers=[identifiers[0]], market=Market.US)
        # Wire shape: always a DataFrame regardless of session.
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Option Timeline', market='US',
                            identifiers=[identifiers[0]])
        self.assertIn('identifier', result.columns)
        self.assertIn('symbol', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('time', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['symbol']).strip()) > 0)
        self.assertGreaterEqual(first['price'], 0)
        logger.debug(f"Option Timeline (real):\n {result}")

    def test_get_option_analysis(self):
        # Real API tests
        result = self.client.get_option_analysis(
            symbols=['AAPL', 'TSLA'],
            period=OptionAnalysisPeriod.FIFTY_TWO_WEEK,
            market=Market.US
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        first = result[0]
        self.assertIsInstance(first, OptionAnalysis)
        self.assertIn(first.symbol, ['AAPL', 'TSLA'])
        self.assertGreater(first.implied_vol_30_days, 0)
        self.assertGreater(first.his_volatility, 0)
        self.assertIsNotNone(first.iv_his_v_ratio)
        self.assertIsNotNone(first.call_put_ratio)
        self.assertIsNotNone(first.iv_metric)
        self.assertIsNotNone(first.iv_metric.period)
        logger.debug(f"Option Analysis (real):\n {result}")

    def test_get_future_exchanges(self):
        result = self.client.get_future_exchanges()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('code', result.columns)
        self.assertIn('name', result.columns)
        self.assertIn('zone', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['code']).strip()) > 0)
        self.assertIsNotNone(first['name'])
        self.assertIsNotNone(first['zone'])
        logger.debug(f"Future Exchanges (real):\n {result}")

    def test_get_future_contracts(self):
        result = self.client.get_future_contracts(exchange='CME')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('contract_code', result.columns)
        self.assertIn('type', result.columns)
        self.assertIn('name', result.columns)
        self.assertIn('multiplier', result.columns)
        first = result.iloc[0]
        self.assertTrue(len(str(first['contract_code']).strip()) > 0)
        self.assertIsNotNone(first['name'])
        self.assertGreater(first['multiplier'], 0)
        logger.debug(f"Future Contracts (real):\n {result}")

    def test_get_future_contract(self):
        result = self.client.get_future_contract(contract_code='CLmain')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        row = result.iloc[0]
        self.assertEqual(row['contract_code'], 'CLmain')
        self.assertGreater(row['multiplier'], 0)
        self.assertGreater(row['min_tick'], 0)
        self.assertIsNotNone(row['currency'])
        self.assertIsNotNone(row['exchange'])
        logger.debug(f"Future Contract (real):\n {result}")

    def test_get_future_continuous_contracts(self):
        result = self.client.get_future_continuous_contracts(future_type='CL')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('contract_code', result.columns)
        self.assertIn('type', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['type'], 'CL')
        self.assertTrue(len(str(first['contract_code']).strip()) > 0)
        logger.debug(f"Future Continuous Contracts (real):\n {result}")

    def test_get_current_future_contract(self):
        result = self.client.get_current_future_contract(future_type='ES')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        row = result.iloc[0]
        self.assertEqual(row['type'], 'ES')
        self.assertTrue(len(str(row['contract_code']).strip()) > 0)
        self.assertGreater(row['multiplier'], 0)
        self.assertGreater(row['min_tick'], 0)
        logger.debug(f"Future Current Contract (real):\n {result}")

    def test_get_future_history_main_contract(self):
        # Use a one-year lookback window instead of hardcoded timestamps
        import time as _time
        end_time = int(_time.time() * 1000)
        begin_time = end_time - 365 * 24 * 3600 * 1000
        result = self.client.get_future_history_main_contract(identifiers=['CLmain'],
                                                              begin_time=begin_time,
                                                              end_time=end_time)
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Future History Main Contract')
        self.assertIn('contract_code', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('refer_contract_code', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['contract_code'], 'CLmain')
        self.assertIsNotNone(first['time'])
        self.assertTrue(len(str(first['refer_contract_code']).strip()) > 0)
        logger.debug(f"Future History Main Contract (real):\n {result}")

    def test_get_all_future_contracts(self):
        result = self.client.get_all_future_contracts(future_type='ES')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('contract_code', result.columns)
        self.assertIn('type', result.columns)
        for _, row in result.iterrows():
            self.assertEqual(row['type'], 'ES')
            self.assertTrue(len(str(row['contract_code']).strip()) > 0)
        logger.debug(f"All Future Contracts (real):\n {result}")

    def test_get_future_trading_times(self):
        contract_code = self._get_future_contract_code(exchange='CME')
        if contract_code is None:
            self.skipTest("No future contract code available from CME")
        result = self.client.get_future_trading_times(identifier=contract_code)
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Future Trading Times')
        self.assertIn('start', result.columns)
        self.assertIn('end', result.columns)
        self.assertIn('trading', result.columns)
        self.assertIn('bidding', result.columns)
        first = result.iloc[0]
        self.assertIsNotNone(first['start'])
        self.assertIsNotNone(first['end'])
        logger.debug(f"Future Trading Times: \n {result}")

    def test_get_future_bars(self):
        contract_code = self._get_future_contract_code(exchange='CME')
        if contract_code is None:
            self.skipTest("No future contract code available from CME")
        result = self.client.get_future_bars(identifiers=[contract_code],
                                             period='day', limit=5)
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Future Bars')
        self.assertIn('identifier', result.columns)
        self.assertIn('time', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['identifier'], contract_code)
        self.assertGreater(first['open'], 0)
        self.assertGreater(first['close'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Future Bars: \n{result}")

    def test_get_future_trade_ticks(self):
        contract_code = self._get_future_contract_code(exchange='CME')
        if contract_code is None:
            self.skipTest("No future contract code available from CME")
        result = self.client.get_future_trade_ticks(identifier=contract_code)
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Future Trade Ticks')
        self.assertIn('identifier', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['identifier'], contract_code)
        self.assertGreater(first['price'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Future Ticks:\n {result}")

    def test_get_future_brief(self):
        contract_code = self._get_future_contract_code(exchange='CME')
        if contract_code is None:
            self.skipTest("No future contract code available from CME")
        result = self.client.get_future_brief(identifiers=[contract_code])
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Future Brief')
        self.assertIn('identifier', result.columns)
        self.assertIn('latest_price', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['identifier'], contract_code)
        self.assertGreater(first['latest_price'], 0)
        logger.debug(f"Future Brief: \n {result}")

    def test_get_future_depth(self):
        contract_code = self._get_future_contract_code(exchange='CME', future_type='ES')
        if contract_code is None:
            self.skipTest("No active ES future contract available from CME")
        identifiers = [contract_code]
        result = self.client.get_future_depth(identifiers=identifiers)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self._skip_if_empty(result, 'Future Depth', identifiers=identifiers)
        first_key = identifiers[0]
        if result.get('identifier') == first_key:
            es = result
        else:
            self.assertIn(first_key, result,
                          self._format_failure_context(identifiers=identifiers, result=result))
            es = result[first_key]
        context = self._format_failure_context(identifiers=identifiers, result=result)
        self.assertEqual(es['identifier'], first_key, context)
        self.assertIsInstance(es.get('asks'), list, context)
        self.assertIsInstance(es.get('bids'), list, context)
        # asks/bids 允许为空列表（无盘口），CME 期货接近 24 小时交易，
        # 不按美股常规时段判断是否该有盘口。
        # 深度档位可能返回 (None, None) 占位；只校验第一个有值的档位。
        ask_price = next((p for p, _ in es['asks'] if p is not None), None)
        if ask_price is not None:
            self.assertGreater(ask_price, 0, context)
        bid_price = next((p for p, _ in es['bids'] if p is not None), None)
        if bid_price is not None:
            self.assertGreater(bid_price, 0, context)
        logger.debug(f"Future Depth: \n {result}")

    def test_get_trading_calendar(self):
        result = self.client.get_trading_calendar(market='US')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, dict)
        self.assertIn('date', first)
        self.assertIn('type', first)
        self.assertTrue(len(str(first['date']).strip()) > 0)
        self.assertIsNotNone(first['type'])
        logger.debug(f"Trading Calendar:\n {result}")

    def test_get_stock_broker(self):
        # HK broker data is only populated during HK main session.
        result = self.client.get_stock_broker(symbol='00700')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StockBroker)
        self.assertEqual(result.symbol, '00700')
        has_data = (result.bid_broker and len(result.bid_broker) > 0) or \
                   (result.ask_broker and len(result.ask_broker) > 0)
        if not has_data:
            if is_market_trading(self.client, 'HK'):
                self.fail("get_stock_broker(00700) returned no bid/ask "
                          "brokers during HK main trading session")
            self.skipTest(
                "Stock broker data empty — HK not in main trading session")
        if result.bid_broker and len(result.bid_broker) > 0:
            first_bid = result.bid_broker[0]
            self.assertGreaterEqual(first_bid.level, 1)
            self.assertGreater(first_bid.price, 0)
        if result.ask_broker and len(result.ask_broker) > 0:
            first_ask = result.ask_broker[0]
            self.assertGreaterEqual(first_ask.level, 1)
            self.assertGreater(first_ask.price, 0)
        logger.debug(f"Stock Broker (real):\n {result}")

    def test_get_broker_hold(self):
        result = self.client.get_broker_hold()
        self.assertIsInstance(result, pd.DataFrame)
        if not result.empty:
            self.assertIn('org_id', result.columns)
            self.assertIn('org_name', result.columns)
            self.assertIn('date', result.columns)
            first = result.iloc[0]
            self.assertTrue(len(str(first['org_id']).strip()) > 0)
            self.assertIsNotNone(first['org_name'])
        logger.debug(f"Broker Hold:\n {result}")

    def test_market_scanner(self):
        # 创建筛选条件和排序设置
        base_filter = StockFilter(StockField.current_ChangeRate,
                                  filter_min=0.01,
                                  filter_max=0.5)
        sort_field_data = SortFilterData(StockField.current_ChangeRate,
                                         sort_dir=SortDirection.DESC)
        page_size = 5
        # 调用市场扫描器方法
        result = self.client.market_scanner(
            market=Market.US,
            filters=[base_filter],
            sort_field_data=sort_field_data,
            page_size=page_size,

        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ScannerResult)
        self.assertIsNotNone(result.page)
        self.assertIsNotNone(result.total_count)
        self.assertGreaterEqual(len(result.items), 1)
        first = result.items[0]
        self.assertTrue(len(str(first.symbol).strip()) > 0)
        self.assertIsNotNone(first.market)
        logger.debug(f"Market Scanner (real): {result}")

    def test_get_corporate_split(self):
        # 实际调用API
        result = self.client.get_corporate_split(symbols=['UVXY'],
                                                 market='US',
                                                 begin_date="2024-01-01",
                                                 end_date="2024-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        self.assertIn('from_factor', result.columns)
        self.assertIn('to_factor', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'UVXY')
        self.assertEqual(first['action_type'], 'SPLIT')
        self.assertGreater(first['from_factor'], 0)
        self.assertGreater(first['to_factor'], 0)
        logger.debug(f"Corporate Action Split:\n {result}")

    def test_get_corporate_symbol_change(self):
        result = self.client.get_corporate_symbol_change(symbols=['META', 'FB'],
                                                         market='US',
                                                         begin_date="2020-01-01",
                                                         end_date="2025-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Corporate Symbol Change')
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        self.assertIn('old_symbol', result.columns)
        self.assertIn('new_symbol', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['action_type'], 'SYMBOL_CHANGE')
        self.assertTrue(len(str(first['old_symbol']).strip()) > 0)
        self.assertTrue(len(str(first['new_symbol']).strip()) > 0)
        logger.debug(f"Corporate Symbol Change:\n {result}")

    def test_get_corporate_delisting(self):
        result = self.client.get_corporate_delisting(symbols=['TWTR', 'GME'],
                                                     market='US',
                                                     begin_date="2018-01-01",
                                                     end_date="2025-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['action_type'], 'DELISTING')
        self.assertTrue(len(str(first['symbol']).strip()) > 0)
        logger.debug(f"Corporate Delisting:\n {result}")

    def test_get_corporate_ipo(self):
        result = self.client.get_corporate_ipo(symbols=['RIVN', 'ABNB', 'COIN'],
                                               market='US',
                                               begin_date="2018-01-01",
                                               end_date="2025-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        if not result.empty:
            first = result.iloc[0]
            self.assertEqual(first['action_type'], 'IPO')
            self.assertTrue(len(str(first['symbol']).strip()) > 0)
            # ipo_name and listing_price may not be present for all symbols
            if 'ipo_name' in result.columns:
                self.assertTrue(len(str(first['ipo_name']).strip()) > 0)
            if 'listing_price' in result.columns:
                self.assertGreater(first['listing_price'], 0)
        logger.debug(f"Corporate IPO:\n {result}")

    def test_get_financial_daily(self):
        # 实际调用API
        result = self.client.get_financial_daily(
            symbols=['AAPL'],
            market='US',
            fields=[Valuation.shares_outstanding],
            begin_date="2023-01-01",
            end_date="2023-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('field', result.columns)
        self.assertIn('date', result.columns)
        self.assertIn('value', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertEqual(first['field'], 'shares_outstanding')
        self.assertGreater(first['value'], 0)
        logger.debug(f"Financial Daily:\n {result}")

    def test_get_financial_report(self):
        result = self.client.get_financial_report(
            symbols=['AAPL'],
            market='US',
            fields=[Income.net_income],
            period_type=FinancialPeriod.LTM,
            begin_date="2023-01-01",
            end_date="2023-12-31")
        logger.debug(f"Financial Report: \n {result}")

        # 验证真实API调用的基本结构
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Financial report data should not be empty")
        expected_columns = ['symbol', 'currency', 'field', 'value', 'period_end_date', 'filing_date']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"Expected column {col} not found in result")
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertEqual(first['field'], 'net_income')
        self.assertIsNotNone(first['currency'])
        self.assertTrue(len(str(first['value']).strip()) > 0)
        self.assertIsNotNone(first['period_end_date'])

    def test_get_industry_list(self):
        result = self.client.get_industry_list()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, dict)
        self.assertIn('id', first)
        self.assertIn('name_en', first)
        self.assertTrue(len(str(first['id']).strip()) > 0)
        self.assertIsNotNone(first['name_en'])
        logger.debug(f"Industry List: {result}")

    def test_get_capital_flow(self):
        result = self.client.get_capital_flow(symbol="AAPL",
                                              market='US',
                                              period=CapitalPeriod.DAY)
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Capital Flow')
        self.assertIn('time', result.columns)
        self.assertIn('net_inflow', result.columns)
        self.assertIn('symbol', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertIsNotNone(first['net_inflow'])
        logger.debug(f"Capital Flow: \n{result}")

    def test_get_capital_distribution(self):
        result = self.client.get_capital_distribution(symbol="AAPL", market='US')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CapitalDistribution)
        self.assertEqual(result.symbol, 'AAPL')
        # Non-trading hours: net_inflow/in_all/out_all may be zero/None
        self.assertIsNotNone(result.net_inflow)
        self.assertGreaterEqual(result.in_all, 0)
        self.assertGreaterEqual(result.out_all, 0)
        logger.debug(f"Capital Distribution:\n {result}")

    def test_get_kline_quota(self):
        result = self.client.get_kline_quota()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, dict)
        self.assertIn('remain', first)
        self.assertIn('used', first)
        self.assertIn('method', first)
        self.assertIsNotNone(first['method'])
        logger.debug(f"Kline Quota:\n {result}")

    # ── get_kline tests (US daily, US weekly, HK daily) ───────────────

    def test_get_kline_us_daily(self):
        """US daily kline — assert volume and open fields."""
        import time as _time
        end_time = int(_time.time() * 1000)
        begin_time = end_time - 30 * 24 * 3600 * 1000
        result = self.client.get_bars(symbols=['AAPL'],
                                       period=BarPeriod.DAY,
                                       begin_time=begin_time,
                                       end_time=end_time,
                                       limit=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['open'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Kline US daily:\n {result}")

    def test_get_kline_us_weekly(self):
        """US weekly kline — period=week variant."""
        import time as _time
        end_time = int(_time.time() * 1000)
        begin_time = end_time - 180 * 24 * 3600 * 1000
        result = self.client.get_bars(symbols=['AAPL'],
                                       period=BarPeriod.WEEK,
                                       begin_time=begin_time,
                                       end_time=end_time,
                                       limit=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('open', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['open'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Kline US weekly:\n {result}")

    def test_get_kline_hk_daily(self):
        """HK daily kline — market=HK variant."""
        import time as _time
        end_time = int(_time.time() * 1000)
        begin_time = end_time - 30 * 24 * 3600 * 1000
        result = self.client.get_bars(symbols=['00700'],
                                       period=BarPeriod.DAY,
                                       begin_time=begin_time,
                                       end_time=end_time,
                                       limit=10)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('open', result.columns)
        self.assertIn('volume', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['open'], 0)
        self.assertGreaterEqual(first['volume'], 0)
        logger.debug(f"Kline HK daily:\n {result}")

    # ── get_quote_real_time tests (US + HK) ───────────────────────────

    def test_get_quote_real_time_us(self):
        """US real-time quote — assert latest_price and amount fields."""
        result = self.client.get_stock_briefs(symbols=['AAPL'])
        if result is None:
            self.skipTest('Quote Real Time US: no response data')
        self.assertIsInstance(result, pd.DataFrame)
        if result.empty:
            self.skipTest('Quote Real Time US: empty response')
        self.assertIn('latest_price', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['latest_price'], 0)
        self.assertIn('amount', result.columns)
        self.assertIsNotNone(first['amount'])
        self.assertGreater(first['amount'], 0)
        logger.debug(f"Quote Real Time US:\n {result}")

    def test_get_quote_real_time_cc(self):
        """Crypto real-time quote — assert amount field."""
        result = self.client.get_stock_briefs(symbols=['BTC.USD'], sec_type=SecurityType.CC)
        if result is None:
            self.skipTest('Quote Real Time CC: no response data')
        self.assertIsInstance(result, pd.DataFrame)
        if result.empty:
            self.skipTest('Quote Real Time CC: empty response for BTC.USD')
        if 'amount' not in result.columns:
            self.skipTest('Quote Real Time CC: amount not returned by current server')
        first = result.iloc[0]
        self.assertIsNotNone(first['amount'])
        self.assertGreater(first['amount'], 0)
        logger.debug(f"Quote Real Time CC:\n {result}")

    def test_get_quote_real_time_hk(self):
        """HK real-time quote — market=HK variant."""
        result = self.client.get_briefs(symbols=['00700'])
        self.assertIsInstance(result, list)
        if not result:
            self.skipTest('Quote Real Time HK: empty response')
        first = result[0]
        self.assertGreater(first.latest_price, 0)
        logger.debug(f"Quote Real Time HK:\n {result}")

    # ── get_option_chain: expiry field assertion ───────────────────────

    def test_get_option_chain_expiry_field(self):
        """Option chain — assert strike and expiry fields are populated."""
        expiry = self._get_option_expiry(symbol='AAPL', market=Market.US)
        if expiry is None:
            if is_market_trading(self.client, 'US'):
                self.fail("get_option_expirations returned empty for AAPL during US main session")
            self.skipTest("No option expiry available for AAPL — US market closed")
        option_filter = OptionFilter(implied_volatility_min=0.05, implied_volatility_max=1,
                                     delta_min=0, delta_max=1,
                                     open_interest_min=10,
                                     in_the_money=True)
        result = self.client.get_option_chain(symbol='AAPL',
                                              expiry=expiry,
                                              market=Market.US,
                                              timezone='America/New_York',
                                              option_filter=option_filter,
                                              return_greek_value=True)
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Option Chain expiry field', market='US', symbol='AAPL', expiry=expiry,
                            option_filter=option_filter.__dict__, return_greek_value=True)
        self.assertIn('strike', result.columns)
        self.assertIn('expiry', result.columns)
        first = result.iloc[0]
        self.assertIsNotNone(first['strike'])
        self.assertGreater(float(first['strike']), 0)
        self.assertIsNotNone(first['expiry'])
        logger.debug(f"Option Chain expiry field:\n {result}")

    # ── get_stock_detail: latest_price assertion ───────────────────────

    def test_get_stock_detail_latest_price(self):
        """Stock detail — assert latest_price is populated."""
        result = self.client.get_stock_details(symbols=['AAPL'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('latest_price', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['latest_price'], 0)
        logger.debug(f"Stock Detail latest_price:\n {result}")

    # ── get_trade_tick: price assertion ───────────────────────────────

    def test_get_trade_tick_price(self):
        """Trade tick — assert price field > 0."""
        result = self.client.get_trade_ticks(symbols=['AAPL'])
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Trade Tick price')
        self.assertIn('price', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['price'], 0)
        logger.debug(f"Trade Tick price:\n {result}")

    # ── get_future_real_time_quote: latest_price assertion ────────────

    def test_get_future_real_time_quote_latest_price(self):
        """Future real-time quote — assert latest_price field."""
        contract_code = self._get_future_contract_code(exchange='CME')
        if contract_code is None:
            self.skipTest("No future contract code available from CME")
        result = self.client.get_future_brief(identifiers=[contract_code])
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Future Real Time Quote')
        self.assertIn('latest_price', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['latest_price'], 0)
        logger.debug(f"Future Real Time Quote latest_price:\n {result}")

    # ── get_market_state: status field assertion ───────────────────────

    def test_get_market_state_status(self):
        """Market state — assert status field is populated."""
        result = self.client.get_market_status(market=Market.US)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, (list, pd.DataFrame))
        if isinstance(result, pd.DataFrame):
            self.assertFalse(result.empty)
            self.assertIn('status', result.columns)
            first = result.iloc[0]
            self.assertIsNotNone(first['status'])
        else:
            self.assertGreater(len(result), 0)
            first = result[0]
            # support both dict and object
            status = first.get('status') if isinstance(first, dict) else getattr(first, 'status', None)
            self.assertIsNotNone(status)
        logger.debug(f"Market State status:\n {result}")

    # ── get_timeline HK variant ───────────────────────────────────────

    def test_get_timeline_hk(self):
        """HK timeline — market=HK variant."""
        result = self.client.get_timeline(symbols=['00700'])
        self.assertIsInstance(result, pd.DataFrame)
        self._skip_if_empty(result, 'Timeline HK', market='HK')
        self.assertIn('symbol', result.columns)
        self.assertIn('price', result.columns)
        first = result.iloc[0]
        self.assertGreater(first['price'], 0)
        logger.debug(f"Timeline HK:\n {result}")

    # ── get_quote_depth HK variant ────────────────────────────────────

    def test_get_quote_depth_hk(self):
        """HK depth quote — market=HK variant."""
        result = self.client.get_depth_quote(symbols=['00700'],
                                              market=Market.HK)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self._skip_if_empty(result, 'Quote Depth HK', market='HK')
        # single-symbol response is {'symbol': '00700', 'asks': [...], 'bids': [...]}
        self.assertIn('asks', result)
        self.assertIn('bids', result)
        self.assertIsInstance(result['asks'], list)
        self.assertIsInstance(result['bids'], list)
        logger.debug(f"Quote Depth HK:\n {result}")

    # ── get_financial_report: quarterly variant ───────────────────────

    def test_get_financial_report_quarterly(self):
        """Financial report — period=quarterly variant."""
        result = self.client.get_financial_report(
            symbols=['AAPL'],
            market='US',
            fields=[Income.net_income],
            period_type=FinancialReportPeriodType.QUARTERLY,
            begin_date="2023-01-01",
            end_date="2023-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Financial report quarterly data should not be empty")
        expected_columns = ['symbol', 'field', 'value', 'period_end_date']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"Expected column {col} not found")
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertEqual(first['field'], 'net_income')
        self.assertIsNotNone(first['period_end_date'])
        logger.debug(f"Financial Report quarterly:\n {result}")

    # ── get_orders: status=FILLED filter variant ──────────────────────

    def test_get_orders_filled_filter(self):
        """Quote-side: get_orders with status=FILLED filter — param variant."""
        # get_orders may not be a quote client method; skip gracefully if absent.
        if not hasattr(self.client, 'get_orders'):
            self.skipTest("QuoteClient does not expose get_orders")
        from tigeropen.common.exceptions import ApiException
        try:
            result = self.client.get_orders(states=['FILLED'], limit=5)
        except ApiException as e:
            self.skipTest(f"get_orders FILLED filter not supported: {e}")
        self.assertIsNotNone(result)
        logger.debug(f"Orders FILLED filter:\n {result}")


    def test_get_addon_entitlement(self):
        result = self.client.get_addon_entitlement()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, AddonEntitlement)
        self.assertIsNotNone(result.user_level)
        self.assertIsNotNone(result.active_plan)
        self.assertIsNotNone(result.effective_entitlement)
        logger.debug(f"Addon Entitlement:\n {result}")

    # ── Missing quote interface tests ──────────────────────────────

    def test_get_stock_details(self):
        result = self.client.get_stock_details(symbols=['AAPL'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('latest_price', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['latest_price'], 0)
        logger.debug(f"Stock Details:\n {result}")

    def test_get_bars_by_page(self):
        result = self.client.get_bars_by_page(symbol='AAPL',
                                              period=BarPeriod.DAY,
                                              total=3,
                                              page_size=2)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('time', result.columns)
        first = result.iloc[0]
        self.assertEqual(first['symbol'], 'AAPL')
        self.assertGreater(first['open'], 0)
        self.assertGreater(first['close'], 0)
        logger.debug(f"Bars By Page:\n {result}")

    def test_get_corporate_dividend(self):
        result = self.client.get_corporate_dividend(symbols=['AAPL'],
                                                    market='US',
                                                    begin_date="2024-01-01",
                                                    end_date="2025-12-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        self.assertIn('amount', result.columns)
        if not result.empty:
            first = result.iloc[0]
            self.assertEqual(first['symbol'], 'AAPL')
            self.assertEqual(first['action_type'], 'DIVIDEND')
            self.assertIsNotNone(first['amount'])
        logger.debug(f"Corporate Dividend:\n {result}")

    def test_get_corporate_earnings_calendar(self):
        result = self.client.get_corporate_earnings_calendar(market='US',
                                                              begin_date="2025-08-01",
                                                              end_date="2025-08-31")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        self.assertIn('action_type', result.columns)
        if not result.empty:
            first = result.iloc[0]
            self.assertIn(first['action_type'], ['EARNING', 'EARNINGS_CALENDAR'])
            self.assertTrue(len(str(first['symbol']).strip()) > 0)
        logger.debug(f"Corporate Earnings Calendar:\n {result}")

    def test_get_financial_currency(self):
        result = self.client.get_financial_currency(symbols=['AAPL', 'MSFT'],
                                                    market='US')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        self.assertIn('currency', result.columns)
        self.assertIn('company_currency', result.columns)
        if not result.empty:
            first = result.iloc[0]
            self.assertTrue(len(str(first['symbol']).strip()) > 0)
            self.assertIsNotNone(first['currency'])
        logger.debug(f"Financial Currency:\n {result}")

    def test_get_financial_exchange_rate(self):
        result = self.client.get_financial_exchange_rate(currency_list=['HKD', 'USD'],
                                                         begin_date="2025-01-01",
                                                         end_date="2025-01-02")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('currency', result.columns)
        self.assertIn('date', result.columns)
        self.assertIn('value', result.columns)
        if not result.empty:
            first = result.iloc[0]
            self.assertTrue(len(str(first['currency']).strip()) > 0)
            self.assertIsNotNone(first['value'])
        logger.debug(f"Financial Exchange Rate:\n {result}")

    def test_get_industry_stocks(self):
        industries = self.client.get_industry_list()
        self.assertGreater(len(industries), 0)
        industry_id = industries[0]['id']
        result = self.client.get_industry_stocks(industry=industry_id,
                                                 market=Market.US)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            first = result[0]
            self.assertIsInstance(first, dict)
            self.assertIn('symbol', first)
            self.assertTrue(len(str(first['symbol']).strip()) > 0)
        logger.debug(f"Industry Stocks (industry={industry_id}):\n {result}")

    def test_get_stock_industry(self):
        result = self.client.get_stock_industry(symbol='AAPL', market=Market.US)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIsInstance(first, dict)
        self.assertIn('industry_level', first)
        self.assertIn('id', first)
        self.assertTrue(len(str(first['id']).strip()) > 0)
        logger.debug(f"Stock Industry:\n {result}")

    def test_get_market_scanner_tags(self):
        result = self.client.get_market_scanner_tags(
            market=Market.US,
            tag_fields=[MultiTagField.Industry, MultiTagField.Concept])
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            first = result[0]
            self.assertIsInstance(first, dict)
        logger.debug(f"Market Scanner Tags:\n {result}")

    def test_get_quote_permission(self):
        result = self.client.get_quote_permission()
        # Permission entries may be None if the account has no active market data access
        if result is None:
            self.skipTest("Permission entries are unavailable; the account may have no active market data access")
        self.assertIsInstance(result, list)
        logger.debug(f"Market data permissions:\n {result}")

    def test_get_warrant_filter(self):
        result = self.client.get_warrant_filter(symbol='00700',
                                                page=0,
                                                page_size=5)
        self.assertIsNotNone(result)
        # get_warrant_filter returns a WarrantFilterItem object, not a list.
        # Wire shape: server returns a bare array of warrant items with no
        # {total, page, pageSize} wrapper — the wrapper's counters stay at
        # their defaults, so only ``items`` carries the answer.
        self.assertIsInstance(result, WarrantFilterItem)
        items_empty = result.items is None or result.items.empty
        if items_empty:
            # During HK main trading session 00700 must return at least one
            # warrant. Otherwise (market closed) empty is legitimate.
            if is_market_trading(self.client, 'HK'):
                self.fail("get_warrant_filter(00700) returned no items during "
                          "HK main trading session")
            self.skipTest(
                "No warrant data available for 00700 — HK not in main trading session")
        first_row = result.items.iloc[0]
        self.assertIn('symbol', result.items.columns)
        self.assertTrue(len(str(first_row['symbol']).strip()) > 0)
        logger.debug(f"Warrant Filter:\n {result}")

    def test_get_warrant_briefs(self):
        # First get warrant symbols from warrant_filter
        warrant_result = self.client.get_warrant_filter(symbol='00700', page=0, page_size=5)
        warrant_empty = (
            not warrant_result
            or warrant_result.items is None
            or warrant_result.items.empty
        )
        if warrant_empty:
            if is_market_trading(self.client, 'HK'):
                self.fail("get_warrant_filter(00700) returned no items during "
                          "HK main trading session")
            self.skipTest(
                "No warrant data available for 00700 — HK not in main trading session")
        warrant_symbol = warrant_result.items.iloc[0].get('symbol')
        if not warrant_symbol:
            self.fail("Warrant filter returned rows but no symbol column value")
        result = self.client.get_warrant_briefs(symbols=[warrant_symbol])
        self.assertIsNotNone(result)
        logger.debug(f"Warrant Briefs:\n {result}")

    def test_get_fund_symbols(self):
        result = self.client.get_fund_symbols()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        logger.debug(f"Fund Symbols count: {len(result) if result else 0}")

    def test_get_fund_contracts(self):
        # Get a fund symbol first
        fund_symbols = self.client.get_fund_symbols()
        if not fund_symbols:
            self.skipTest("No fund symbols available")
        symbol = fund_symbols[0]
        result = self.client.get_fund_contracts(symbols=[symbol])
        self.assertIsNotNone(result)
        logger.debug(f"Fund Contracts:\n {result}")

    def test_get_fund_quote(self):
        fund_symbols = self.client.get_fund_symbols()
        if not fund_symbols:
            self.skipTest("No fund symbols available")
        symbol = fund_symbols[0]
        result = self.client.get_fund_quote(symbols=[symbol])
        self.assertIsNotNone(result)
        logger.debug(f"Fund Quote:\n {result}")

    def test_get_fund_history_quote(self):
        import time as _time
        end_time = int(_time.time() * 1000)
        begin_time = end_time - 180 * 24 * 3600 * 1000  # ~6 months
        fund_symbols = self.client.get_fund_symbols()
        if not fund_symbols:
            self.skipTest("No fund symbols available")
        symbol = fund_symbols[0]
        result = self.client.get_fund_history_quote(symbols=[symbol],
                                                    begin_time=begin_time,
                                                    end_time=end_time,
                                                    limit=5)
        self.assertIsNotNone(result)
        logger.debug(f"Fund History Quote:\n {result}")

    def test_get_stock_fundamental(self):
        result = self.client.get_stock_fundamental(symbols=['AAPL', 'MSFT'],
                                                   market='US')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('symbol', result.columns)
        self.assertIn('ttm_pe_rate', result.columns)
        self.assertIn('market_cap', result.columns)
        first = result.iloc[0]
        self.assertIn(first['symbol'], ['AAPL', 'MSFT'])
        self.assertIsNotNone(first['market_cap'])
        logger.debug(f"Stock Fundamental:\n {result}")

    def test_get_trade_rank(self):
        result = self.client.get_trade_rank(market='US')
        self.assertIsNotNone(result)
        logger.debug(f"Trade Rank:\n {result}")

    def test_get_quote_overnight(self):
        result = self.client.get_quote_overnight(symbols=['AAPL'])
        self.assertIsNotNone(result)
        logger.debug(f"Quote Overnight:\n {result}")

    # ── K线时间范围与OHLC约束测试 ───────────────────────────────────────

    def test_get_bars_daily_30day_ohlc_us_hk(self):
        """30天日K，断言 bar 数量、时间戳升序、OHLC 合法性 (US + HK)"""
        import time as _time
        end_time = int(_time.time() * 1000)
        begin_time = end_time - 30 * 24 * 3600 * 1000  # 30 calendar days ago
        for symbol in ['AAPL', '00700']:
            with self.subTest(symbol=symbol):
                result = self.client.get_bars(
                    symbols=[symbol],
                    period=BarPeriod.DAY,
                    begin_time=begin_time,
                    end_time=end_time,
                )
                self.assertIsInstance(result, pd.DataFrame)
                self._skip_if_empty(result, f'Daily Bars ({symbol})')
                self.assertGreaterEqual(
                    len(result), 15,
                    f"{symbol}: expected >= 15 trading bars in a 30-day window")
                # Timestamps strictly ascending
                times = result['time'].tolist()
                for i in range(1, len(times)):
                    self.assertGreater(
                        times[i], times[i - 1],
                        f"{symbol}: bar timestamps must be strictly ascending (index {i})")
                # OHLC integrity: High >= max(Open,Close) >= min(Open,Close) >= Low, Volume >= 0
                for idx, row in result.iterrows():
                    hi, lo = row['high'], row['low']
                    op, cl = row['open'], row['close']
                    self.assertGreaterEqual(
                        hi, max(op, cl),
                        f"{symbol} bar@{row['time']}: high({hi}) < max(open,close)({max(op,cl)})")
                    self.assertLessEqual(
                        lo, min(op, cl),
                        f"{symbol} bar@{row['time']}: low({lo}) > min(open,close)({min(op,cl)})")
                    self.assertGreaterEqual(
                        row['volume'], 0,
                        f"{symbol} bar@{row['time']}: volume must be >= 0")
        logger.debug("30-day daily OHLC constraint test passed for AAPL and 00700")

    def test_get_bars_60min_5day_ohlc_us_hk(self):
        """5天60分钟K，断言 bar 数量、时间戳升序、OHLC 合法性 (US + HK)"""
        import time as _time
        end_time = int(_time.time() * 1000)
        begin_time = end_time - 5 * 24 * 3600 * 1000  # 5 calendar days ago
        for symbol in ['AAPL', '00700']:
            with self.subTest(symbol=symbol):
                result = self.client.get_bars(
                    symbols=[symbol],
                    period=BarPeriod.ONE_HOUR,
                    begin_time=begin_time,
                    end_time=end_time,
                )
                self.assertIsInstance(result, pd.DataFrame)
                self._skip_if_empty(result, f'60min Bars ({symbol})')
                self.assertGreaterEqual(
                    len(result), 5,
                    f"{symbol}: expected >= 5 bars in a 5-day 60min window")
                # Timestamps strictly ascending
                times = result['time'].tolist()
                for i in range(1, len(times)):
                    self.assertGreater(
                        times[i], times[i - 1],
                        f"{symbol}: bar timestamps must be strictly ascending (index {i})")
                # OHLC integrity
                for idx, row in result.iterrows():
                    hi, lo = row['high'], row['low']
                    op, cl = row['open'], row['close']
                    self.assertGreaterEqual(
                        hi, max(op, cl),
                        f"{symbol} bar@{row['time']}: high({hi}) < max(open,close)({max(op,cl)})")
                    self.assertLessEqual(
                        lo, min(op, cl),
                        f"{symbol} bar@{row['time']}: low({lo}) > min(open,close)({min(op,cl)})")
                    self.assertGreaterEqual(
                        row['volume'], 0,
                        f"{symbol} bar@{row['time']}: volume must be >= 0")
        logger.debug("5-day 60min OHLC constraint test passed for AAPL and 00700")

    # ── 盘口价格合理性测试 ──────────────────────────────────────────────

    def test_get_depth_quote_spread_us_hk(self):
        """盘口合理性: asks 升序、bids 降序、lowestAsk >= highestBid、所有价格 > 0 (AAPL + 00700)"""
        test_cases = [
            ('AAPL', Market.US),
            ('00700', Market.HK),
        ]
        for symbol, market in test_cases:
            with self.subTest(symbol=symbol, market=market):
                result = self.client.get_depth_quote(symbols=[symbol], market=market)
                self.assertIsNotNone(result)
                # Single-symbol call: result may be the order book dict directly
                # or keyed by symbol — normalise to order_book
                if isinstance(result, dict) and 'asks' in result:
                    order_book = result
                elif isinstance(result, dict) and symbol in result:
                    order_book = result[symbol]
                else:
                    self.skipTest(
                        f"Depth quote data unavailable for {symbol} — non-trading hours or unsupported")
                    return
                asks = order_book.get('asks', [])
                bids = order_book.get('bids', [])
                if not asks or not bids:
                    self.skipTest(
                        f"Depth quote asks/bids empty for {symbol} — non-trading hours")
                    return
                ask_prices = [a[0] for a in asks]
                bid_prices = [b[0] for b in bids]
                # All prices > 0
                for p in ask_prices:
                    self.assertGreater(p, 0, f"{symbol}: ask price {p} must be > 0")
                for p in bid_prices:
                    self.assertGreater(p, 0, f"{symbol}: bid price {p} must be > 0")
                # Asks sorted ascending by price
                self.assertEqual(
                    ask_prices, sorted(ask_prices),
                    f"{symbol}: asks must be sorted ascending by price, got {ask_prices}")
                # Bids sorted descending by price
                self.assertEqual(
                    bid_prices, sorted(bid_prices, reverse=True),
                    f"{symbol}: bids must be sorted descending by price, got {bid_prices}")
                # Spread non-negative: lowest ask >= highest bid
                lowest_ask = ask_prices[0]
                highest_bid = bid_prices[0]
                self.assertGreaterEqual(
                    lowest_ask, highest_bid,
                    f"{symbol}: lowestAsk({lowest_ask}) < highestBid({highest_bid}) — negative spread")
        logger.debug("Depth quote spread test passed for AAPL(US) and 00700(HK)")

    # ── 多市场实时行情 ─────────────────────────────────────────────────

    def test_get_briefs_multi_market_realtime(self):
        """多市场实时行情: LatestPrice > 0, High >= Low, AskPrice >= BidPrice (AAPL/00700/09988)"""
        result = self.client.get_briefs(
            symbols=['AAPL', '00700', '09988'],
            include_hour_trading=True,
            include_ask_bid=True,
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self._skip_if_empty(result, 'Multi-market Realtime Briefs')
        for brief in result:
            self.assertIsInstance(brief, QuoteBrief)
            self.assertGreater(
                brief.latest_price, 0,
                f"{brief.symbol}: latest_price({brief.latest_price}) must be > 0")
            # High >= Low when both non-zero
            if brief.high_price and brief.low_price:
                self.assertGreaterEqual(
                    brief.high_price, brief.low_price,
                    f"{brief.symbol}: high({brief.high_price}) < low({brief.low_price})")
            # AskPrice >= BidPrice when both non-zero
            if brief.ask_price and brief.bid_price:
                self.assertGreaterEqual(
                    brief.ask_price, brief.bid_price,
                    f"{brief.symbol}: ask({brief.ask_price}) < bid({brief.bid_price})")
        logger.debug(f"Multi-market Realtime Briefs:\n {result}")
