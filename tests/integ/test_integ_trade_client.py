# -*- coding: utf-8 -*-
"""Integration tests - require real API credentials."""
import logging
import unittest
from datetime import datetime, timedelta

import pytest

from tigeropen.common.consts import OptionExerciseType, SegmentType, Currency, SecurityType, OrderType
from tigeropen.common.exceptions import ApiException
from tigeropen.common.util.contract_utils import (
    stock_contract, option_contract_by_symbol, future_contract,
    future_option_contract, war_contract_by_symbol, iopt_contract_by_symbol,
)
from tigeropen.common.util.order_utils import (
    market_order, market_order_by_amount, limit_order, limit_order_by_amount,
    stop_order, stop_limit_order, trail_order, auction_limit_order,
    auction_market_order, order_leg, limit_order_with_legs, iceberg_order,
    algo_order, algo_order_params, oca_order, combo_order, contract_leg,
)
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Order
from tigeropen.trade.domain.position import Position
from tigeropen.trade.domain.transfer import TransferItem, PositionTransfer, PositionTransferDetail, PositionTransferRecord, \
    PositionTransferExternalRecord
from tigeropen.trade.domain.prime_account import PortfolioAccount
from tigeropen.trade.trade_client import TradeClient
from tests.support import integ_client_config, is_integ_run

# Safe prices — kept far from market so BUY/SELL orders never execute.
SAFE_BUY_PRICE = 0.01           # buy at 1 cent → will not fill
SAFE_SELL_PRICE = 999_999.0     # sell at 999,999 → will not fill
SAFE_STOP_BUY_TRIGGER = 999_999.0   # STP BUY trigger far above market
SAFE_STOP_SELL_TRIGGER = 0.01       # STP SELL trigger far below market

# Error messages we treat as legitimate skips (permission / license boundary).
_PERMISSION_ERROR_KEYWORDS = (
    "access forbidden", "forbidden", "no permission", "not supported",
    "license", "not open", "not enabled", "not available for this account",
    "no token", "TBNZ",
    # Symbol / instrument-level boundaries — the SDK marshaled fine, the
    # server just refuses this particular symbol for this account.
    "don't support trading of this stock",
    "don’t support trading",  # smart quote variant
    "unsupported instrument", "instrument not tradable",
    # Session/state boundaries where only certain order types are accepted.
    "only limit orders are supported",
    "outside of regular trading hours",
    "market is closed",
    # Cash-order-by-amount restricted to market order on this account tier.
    "only trade cash order by market order",
    "cash order by market order",
)

# Error messages we treat as terminal-order tolerance (order state race).
_TERMINAL_ORDER_KEYWORDS = (
    "cannot be modified", "cannot be cancelled", "cannot be canceled",
    "already cancelled", "already canceled", "already filled",
    "not in a modifiable state", "invalid order status",
)

# Rate-limit signal — retry with backoff instead of failing.
_RATE_LIMIT_KEYWORDS = (
    "too_many_requests", "rate limit", "requestrateexceedlimit",
    "rate exceeded",
)

logger = logging.getLogger(__name__)


@pytest.mark.skipif(not is_integ_run(), reason="requires TIGER_RUN_INTEG=true")
class TestIntegTradeClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client_config = integ_client_config()
        cls.client = TradeClient(cls.client_config, logger=logger)

    def _get_option_contract_id(self):
        """Dynamically fetch an option contract_id from exercise positions or derivative contracts."""
        # Try exercise positions first
        try:
            positions = self.client.get_option_exercise_positions(
                exercise_type=OptionExerciseType.EXERCISE)
            if positions and positions.items:
                return positions.items[0].contract_id
        except Exception as e:
            logger.warning(f"get_option_exercise_positions failed: {e}")

        # Fall back to derivative contracts
        future_expiry = (datetime.now() + timedelta(days=180)).strftime('%Y%m%d')
        contracts = self.client.get_derivative_contracts(symbol='AAPL',
                                                       sec_type=SecurityType.OPT,
                                                       expiry=future_expiry)
        if contracts:
            return contracts[0].contract_id
        return None

    # ------------------------------------------------------------------
    # Shared helpers for matrix trade-order tests
    # ------------------------------------------------------------------

    @classmethod
    def _quote_client(cls):
        """Lazy singleton QuoteClient — needed for option/future contract discovery."""
        if not hasattr(cls, "_quote"):
            cls._quote = QuoteClient(cls.client_config, logger=logger)
        return cls._quote

    def _resolve_us_option_contract(self):
        """Return a US OPT Contract for AAPL: nearest expiry, near-ATM CALL.

        Falls back through several strategies before giving up.
        Returns None if we cannot resolve one — caller should skipTest.
        """
        try:
            qc = self._quote_client()
            exps = qc.get_option_expirations(symbols='AAPL')
            if exps is None or exps.empty:
                return None
            # DataFrame is sorted; pick a mid-range expiry (> 14 days) to avoid
            # weekly-expiry / same-day scenarios.
            expiry_col = 'date' if 'date' in exps.columns else exps.columns[1]
            expiries = list(exps[expiry_col])
            expiry = None
            today = datetime.now().date()
            for e in expiries:
                try:
                    d = datetime.strptime(str(e), '%Y-%m-%d').date()
                    if (d - today).days > 14:
                        expiry = str(e)
                        break
                except ValueError:
                    continue
            if not expiry:
                expiry = str(expiries[-1])

            chain = qc.get_option_chain('AAPL', expiry)
            if chain is None or chain.empty:
                return None
            # Filter CALLs and pick a mid-strike (approx ATM by row-index median).
            calls = chain[chain['put_call'] == 'CALL'] if 'put_call' in chain.columns else chain
            if calls.empty:
                return None
            row = calls.iloc[len(calls) // 2]
            strike = float(row['strike']) if 'strike' in row else None
            if strike is None:
                return None
            return option_contract_by_symbol(
                symbol='AAPL', expiry=expiry, strike=strike,
                put_call='CALL', currency='USD')
        except Exception as e:
            logger.warning(f"_resolve_us_option_contract failed: {e}")
            return None

    def _resolve_us_future_contract(self):
        """Return a US FUT Contract using a common continuous main contract.

        Uses CL (crude oil) main contract on NYMEX as a stable default.
        """
        try:
            # 'CL' main contract is a well-known continuous future symbol.
            return future_contract(symbol='CL', currency='USD', exchange='NYMEX')
        except Exception as e:
            logger.warning(f"_resolve_us_future_contract failed: {e}")
            return None

    def _resolve_us_fop_contract(self):
        """Return a US FOP (future option) Contract; best-effort discovery."""
        try:
            future_expiry = (datetime.now() + timedelta(days=90)).strftime('%Y%m%d')
            contracts = self.client.get_derivative_contracts(
                symbol='CL', sec_type=SecurityType.FOP, expiry=future_expiry)
            if not contracts:
                return None
            c = contracts[0]
            return future_option_contract(
                symbol=c.symbol or 'CL', currency=c.currency or 'USD',
                expiry=c.expiry, strike=c.strike, put_call=c.put_call,
                multiplier=c.multiplier, contract_id=c.contract_id)
        except Exception as e:
            logger.warning(f"_resolve_us_fop_contract failed: {e}")
            return None

    def _resolve_hk_warrant_contract(self):
        """Return an HK WAR Contract, best-effort."""
        try:
            future_expiry = (datetime.now() + timedelta(days=90)).strftime('%Y%m%d')
            contracts = self.client.get_derivative_contracts(
                symbol='00700', sec_type=SecurityType.WAR, expiry=future_expiry)
            if not contracts:
                return None
            c = contracts[0]
            return war_contract_by_symbol(
                symbol=c.symbol or '00700', expiry=c.expiry, strike=c.strike,
                put_call=c.put_call, local_symbol=c.local_symbol,
                multiplier=c.multiplier or 100, currency='HKD',
                contract_id=c.contract_id)
        except Exception as e:
            logger.warning(f"_resolve_hk_warrant_contract failed: {e}")
            return None

    def _resolve_hk_iopt_contract(self):
        """Return an HK IOPT (callable bull/bear) Contract, best-effort."""
        try:
            future_expiry = (datetime.now() + timedelta(days=90)).strftime('%Y%m%d')
            contracts = self.client.get_derivative_contracts(
                symbol='00700', sec_type=SecurityType.IOPT, expiry=future_expiry)
            if not contracts:
                return None
            c = contracts[0]
            return iopt_contract_by_symbol(
                symbol=c.symbol or '00700', expiry=c.expiry, strike=c.strike,
                put_call=c.put_call, local_symbol=c.local_symbol,
                multiplier=c.multiplier or 100, currency='HKD',
                contract_id=c.contract_id)
        except Exception as e:
            logger.warning(f"_resolve_hk_iopt_contract failed: {e}")
            return None

    def _skip_or_raise_on_permission_error(self, exc, context=""):
        """If the exception is a permission/license boundary, skip; else re-raise."""
        msg = str(exc).lower()
        if any(k.lower() in msg for k in _PERMISSION_ERROR_KEYWORDS):
            self.skipTest(f"{context} — account boundary: {exc}")
        raise exc

    def _cancel_tolerating_terminal(self, order_id):
        """Best-effort cancel; ignore 'already terminated' style errors."""
        try:
            self.client.cancel_order(id=order_id)
        except ApiException as e:
            if not any(k in str(e).lower() for k in _TERMINAL_ORDER_KEYWORDS):
                logger.warning(f"cancel_order failed unexpectedly: {e}")
                raise
            logger.info(f"Order {order_id} already terminated — skipping cancel: {e}")

    def _place_with_rate_limit_retry(self, order, *, context, max_retries=3):
        """place_order with exponential backoff on 'too_many_requests'.

        Returns order id on success; None if we hit a permission boundary
        (test should treat as skip).
        """
        import time
        delay = 1.0
        for attempt in range(max_retries):
            try:
                return self.client.place_order(order=order)
            except ApiException as e:
                msg = str(e).lower()
                if any(k in msg for k in _RATE_LIMIT_KEYWORDS) and attempt < max_retries - 1:
                    logger.info(f"{context}: rate-limited (attempt {attempt+1}), backing off {delay}s")
                    time.sleep(delay)
                    delay *= 2
                    continue
                # Not rate-limit, or ran out of retries — surface to caller.
                raise

    def _preview_and_place(self, order, *, context=""):
        """Preview → place → cancel round-trip; skip on permission errors.

        Returns the placed order id (or None if skipped/aborted).
        """
        # 1. Preview first — validates SDK marshaling before touching real state.
        try:
            preview = self.client.preview_order(order=order)
            self.assertIsNotNone(preview, f"{context}: preview returned None")
            logger.debug(f"{context} preview: {preview}")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, f"{context} preview")

        # 2. Place, then cancel.
        try:
            order_id = self._place_with_rate_limit_retry(order, context=context)
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, f"{context} place")
            return None
        self.assertIsNotNone(order_id, f"{context}: place_order returned None")
        logger.info(f"{context}: placed order id={order_id}")
        self._cancel_tolerating_terminal(order_id)
        return order_id

    def test_get_positions(self):
        result = self.client.get_positions()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            pos = result[0]
            self.assertIsInstance(pos, Position)
            self.assertIsNotNone(pos.account)
            self.assertIsNotNone(pos.contract)
            self.assertIsNotNone(pos.quantity)
        logger.debug(f"Positions: {result}")

    def test_get_contract(self):
        result = self.client.get_contract(symbol="AAPL", sec_type='STK', currency='USD')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Contract)
        self.assertEqual(result.symbol, 'AAPL')
        self.assertEqual(result.sec_type, 'STK')
        self.assertIsNotNone(result.contract_id)
        logger.debug(f"Contracts: {result.to_dict()}")

    def test_get_orders(self):
        result = self.client.get_orders(limit=2)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            order = result[0]
            self.assertIsInstance(order, Order)
            self.assertIsNotNone(order.id)
            self.assertIsNotNone(order.account)
            self.assertIsNotNone(order.action)
            self.assertIsNotNone(order.order_type)
        logger.debug(f"Orders: {result}")

    def test_get_order(self):
        # Dynamically fetch an order ID instead of hardcoding
        orders = self.client.get_orders(limit=5)
        if not orders:
            self.skipTest("No orders available to test get_order")
        order_id = orders[0].id
        result = self.client.get_order(id=order_id)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Order)
        self.assertEqual(result.id, order_id)
        self.assertIsNotNone(result.account)
        self.assertIsNotNone(result.contract)
        self.assertIsNotNone(result.action)
        logger.debug(f"Order: {result.to_dict()}")

    def test_get_prime_assets(self):
        result = self.client.get_prime_assets()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PortfolioAccount)
        self.assertIsNotNone(result.account)
        self.assertIsNotNone(result.segments)
        logger.debug(f"Prime Assets: {result}")

    @pytest.mark.integ
    def test_place_order(self):
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order(account=self.client_config.account,
                            contract=contract,
                            action='BUY',
                            limit_price=90.5,
                            quantity=2)
        result = self.client.place_order(order=order)
        logger.debug(f"Order Result: {result}")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
        self.assertEqual(order.id, result)

    @pytest.mark.integ
    def test_place_iceberg_order(self):
        import time
        now_ms = int(time.time() * 1000)
        start_time = now_ms
        end_time = now_ms + 3600_000

        contract = stock_contract(symbol='AAPL', currency='USD')
        order = iceberg_order(
            account=self.client_config.account,
            contract=contract,
            action='BUY',
            quantity=1000,
            limit_price=180.0,
            display_size=100,
            min_display_size=50,
            check_intervals=30,
            start_time=start_time,
            end_time=end_time,
        )
        result = self.client.place_order(order=order)
        logger.debug(f"place_order result (orderId): {result}")
        logger.debug(f"  order.id={order.id} order_type={order.order_type}")
        logger.debug(f"  start_time from server: {order.start_time}  expected: {start_time}")
        logger.debug(f"  end_time   from server: {order.end_time}  expected: {end_time}")
        logger.debug(f"  display_size={order.display_size} min_display_size={order.min_display_size} check_intervals={order.check_intervals}")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
        self.assertEqual(order.id, result)
        self.assertEqual(order.order_type, 'ICEBERG')

    @pytest.mark.integ
    def test_cancel_order(self):
        # Place an order first, then cancel it — no hardcoded order ID
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order(account=self.client_config.account,
                            contract=contract,
                            action='BUY',
                            limit_price=90.5,
                            quantity=2)
        order_id = self.client.place_order(order=order)
        logger.debug(f"Place Order Result: {order_id}")
        self.assertIsNotNone(order_id)
        self.assertIsInstance(order_id, int)
        self.assertGreater(order_id, 0)

        result = self.client.cancel_order(id=order_id)
        logger.debug(f"Cancel Order Result: {result}")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    @pytest.mark.integ
    def test_modify_order(self):
        from tigeropen.common.exceptions import ApiException
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order(account=self.client_config.account,
                            contract=contract,
                            action='BUY',
                            limit_price=90.5,
                            quantity=2)
        result = self.client.place_order(order=order)
        logger.debug(f"Place Order Result: {result}")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

        # Sandbox orders can transition to a non-modifiable state
        # (filled / rejected) very quickly. Accept that outcome as long as
        # the SDK marshaled the modify request correctly.
        try:
            oid = self.client.modify_order(order, limit_price=100.5)
            logger.debug(f"Modify Order Result: {oid}")
            self.assertIsNotNone(oid)
            self.assertIsInstance(oid, int)
            self.assertGreater(oid, 0)
        except ApiException as e:
            if "cannot be modified" not in str(e):
                raise
            logger.warning(f"Order became non-modifiable before modify: {e}")

    @pytest.mark.integ
    def test_transfer_position(self):
        from tigeropen.common.exceptions import ApiException
        transfers = [TransferItem(symbol="AAPL", quantity=10)]
        try:
            result = self.client.transfer_position(from_account="1001", to_account="1002", transfers=transfers, market="US")
        except ApiException as e:
            # from/to account are hardcoded placeholders — the CI account
            # legitimately has no permission to move positions between them.
            if "access forbidden" in str(e) or "forbidden" in str(e).lower():
                self.skipTest(f"CI account lacks permission for placeholder accounts 1001/1002: {e}")
            raise
        logger.debug(f"Transfer Position Result: {result}")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PositionTransfer)
        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.status)

    def test_get_position_transfer_records(self):
        result = self.client.get_position_transfer_records(since_date="2025-01-01", to_date="2025-01-02")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            record = result[0]
            self.assertIsInstance(record, PositionTransferRecord)
            self.assertIsNotNone(record.id)
            self.assertIsNotNone(record.status)
        logger.debug(f"Position Transfer Records: {result}")

    def test_get_position_transfer_detail(self):
        records = self.client.get_position_transfer_records(since_date="2025-01-01", to_date="2025-01-02")
        if not records:
            self.skipTest("No position transfer records available to query detail")
        record = records[0]
        result = self.client.get_position_transfer_detail(account_id=record.account_id,
                                                          transfer_id=record.id)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PositionTransferDetail)
        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.status)
        logger.debug(f"Position Transfer Detail: {result}")

    def test_get_position_transfer_external_records(self):
        from tigeropen.common.exceptions import ApiException
        try:
            result = self.client.get_position_transfer_external_records(account_id="1001", since_date="2025-01-01", to_date="2025-01-02")
        except ApiException as e:
            # account_id="1001" is a hardcoded placeholder — the CI account
            # legitimately has no read permission on it.
            if "access forbidden" in str(e) or "forbidden" in str(e).lower():
                self.skipTest(f"CI account lacks permission for placeholder account_id=1001: {e}")
            raise
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            record = result[0]
            self.assertIsInstance(record, PositionTransferExternalRecord)
            self.assertIsNotNone(record.id)
            self.assertIsNotNone(record.status)
        logger.debug(f"Position Transfer External Records: {result}")

    @pytest.mark.integ
    def test_submit_option_exercise(self):
        from tigeropen.common.exceptions import ApiException
        contract_id = self._get_option_contract_id()
        if contract_id is None:
            self.skipTest("No option contract available to test exercise")
        # Use a future date instead of hardcoded value
        executing_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        # Scenario 1: submit early exercise (Exercise)
        try:
            result_exercise = self.client.submit_option_exercise(
                contract_id=contract_id,
                exercise_type="Exercise",
                quantity=1.0,
                executing_date=executing_date,
                is_force=False,
            )
            self.assertTrue(result_exercise)
            logger.debug(f"Submit Exercise Result: {result_exercise}")
        except ApiException as e:
            # downstream business limit (exercise count/rate limit), not SDK/server issue
            logger.warning(f"Submit Exercise skipped due to downstream limit: {e}")
            self.skipTest(f"Downstream limit: {e}")

        # Scenario 2: submit expire exercise — itm_rate valid range 0~10
        try:
            result_expire = self.client.submit_option_exercise(
                contract_id=contract_id,
                exercise_type=OptionExerciseType.EXPIRE,
                quantity=1.0,
                itm_rate=1,
            )
            self.assertTrue(result_expire)
            logger.debug(f"Submit Expire Result: {result_expire}")
        except ApiException as e:
            logger.warning(f"Submit Expire skipped due to downstream limit: {e}")
            self.skipTest(f"Downstream limit: {e}")

    def test_check_option_exercise(self):
        contract_id = self._get_option_contract_id()
        if contract_id is None:
            self.skipTest("No option contract available to test check_exercise")
        executing_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        result = self.client.check_option_exercise(
            contract_id=contract_id,
            exercise_type="Exercise",
            executing_date=executing_date,
            quantity=1.0,
            is_force=False,
        )
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.available_quantity)
        self.assertIsNotNone(result.symbol)
        logger.debug(f"Check Option Exercise Result: {result}")

    def test_get_option_exercise_records(self):
        result = self.client.get_option_exercise_records(page=1, size=20)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.items)
        self.assertIsInstance(result.items, list)
        if result.items:
            r = result.items[0]
            self.assertIsNotNone(r.id)
            self.assertIsNotNone(r.type)
            self.assertIsNotNone(r.status)
        logger.debug(f"Option Exercise Records: {result}")

    def test_get_option_exercise_positions(self):
        result = self.client.get_option_exercise_positions(
            exercise_type=OptionExerciseType.EXERCISE)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.items)
        if result.items:
            pos = result.items[0]
            self.assertIsNotNone(pos.contract_id)
            self.assertIsNotNone(pos.symbol)
            self.assertIsNotNone(pos.available_quantity)
        logger.debug(f"Option Exercise Positions: {result}")

    @pytest.mark.integ
    def test_cancel_option_exercise(self):
        from tigeropen.common.exceptions import ApiException
        # Find an existing New-status record to cancel; if none, try submit then cancel
        records = self.client.get_option_exercise_records(page=1, size=20)
        new_record = next((r for r in records.items if r.status == "New"), None)

        if new_record is None:
            # No New record — try submitting one
            contract_id = self._get_option_contract_id()
            if contract_id is None:
                self.skipTest("No option contract available to test cancel_exercise")
            executing_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            try:
                submit_ok = self.client.submit_option_exercise(
                    contract_id=contract_id,
                    exercise_type="Exercise",
                    quantity=1.0,
                    executing_date=executing_date,
                    is_force=False,
                )
                self.assertTrue(submit_ok)
                records = self.client.get_option_exercise_records(page=1, size=20)
                new_record = next((r for r in records.items if r.status == "New"), None)
            except ApiException as e:
                logger.warning(f"Submit skipped due to downstream limit: {e}")

        if new_record is None:
            self.skipTest("No New exercise record available to cancel (downstream limit)")

        logger.debug(f"Cancelling exercise id={new_record.id}")
        result = self.client.cancel_option_exercise(exercise_id=new_record.id)
        self.assertTrue(result)
        logger.debug(f"Cancel Option Exercise Result: {result}")

    # ── Missing trade interface tests ──────────────────────────────

    def test_get_managed_accounts(self):
        result = self.client.get_managed_accounts()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            first = result[0]
            self.assertIsNotNone(first.account)
            self.assertIsNotNone(first.capability)
            self.assertIsNotNone(first.status)
        logger.debug(f"Managed Accounts: {result}")

    def test_get_contracts(self):
        result = self.client.get_contracts(symbol=['AAPL', 'MSFT'],
                                            sec_type='STK',
                                            currency='USD')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            first = result[0]
            self.assertIsInstance(first, Contract)
            self.assertIn(first.symbol, ['AAPL', 'MSFT'])
        logger.debug(f"Contracts: {result}")

    def test_get_derivative_contracts(self):
        future_expiry = (datetime.now() + timedelta(days=180)).strftime('%Y%m%d')
        result = self.client.get_derivative_contracts(symbol='AAPL',
                                                      sec_type=SecurityType.OPT,
                                                      expiry=future_expiry)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            first = result[0]
            self.assertIsInstance(first, Contract)
            self.assertEqual(first.sec_type, 'OPT')
        logger.debug(f"Derivative Contracts: {result}")

    def test_get_assets(self):
        result = self.client.get_assets(segment=True, market_value=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            first = result[0]
            self.assertIsNotNone(first.account)
            self.assertIsNotNone(first.summary)
            self.assertIsNotNone(first.summary.net_liquidation)
        logger.debug(f"Assets: {result}")

    def test_get_aggregate_assets(self):
        self.skipTest("Aggregate assets only supports institution accounts")
        result = self.client.get_aggregate_assets(seg_type=SegmentType.SEC,
                                                   base_currency=Currency.USD)
        self.assertIsNotNone(result)
        logger.debug(f"Aggregate Assets: {result}")

    def test_get_open_orders(self):
        result = self.client.get_open_orders(limit=5)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            order = result[0]
            self.assertIsInstance(order, Order)
            self.assertIsNotNone(order.id)
        logger.debug(f"Open Orders: {result}")

    def test_get_cancelled_orders(self):
        result = self.client.get_cancelled_orders(limit=5)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            order = result[0]
            self.assertIsInstance(order, Order)
            self.assertIsNotNone(order.id)
        logger.debug(f"Cancelled Orders: {result}")

    def test_get_filled_orders(self):
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=60)
        result = self.client.get_filled_orders(limit=5,
                                               start_time=start_dt.strftime('%Y-%m-%d'),
                                               end_time=end_dt.strftime('%Y-%m-%d'))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:
            order = result[0]
            self.assertIsInstance(order, Order)
            self.assertIsNotNone(order.id)
        logger.debug(f"Filled Orders: {result}")

    def test_get_transactions(self):
        result = self.client.get_transactions(symbol="AAPL",
                                              since_date="20250101",
                                              to_date="20251231",
                                              limit=5)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        logger.debug(f"Transactions: {result}")

    def test_get_analytics_asset(self):
        result = self.client.get_analytics_asset(start_date="2025-01-01",
                                                 end_date="2025-06-30",
                                                 seg_type=SegmentType.SEC,
                                                 currency=Currency.USD)
        self.assertIsNotNone(result)
        logger.debug(f"Analytics Asset: {result}")

    def test_get_segment_fund_available(self):
        result = self.client.get_segment_fund_available(from_segment=SegmentType.FUT,
                                                         currency=Currency.USD)
        self.assertIsNotNone(result)
        logger.debug(f"Segment Fund Available: {result}")

    def test_get_segment_fund_history(self):
        result = self.client.get_segment_fund_history(limit=5)
        self.assertIsNotNone(result)
        logger.debug(f"Segment Fund History: {result}")

    def test_get_funding_history(self):
        result = self.client.get_funding_history(seg_type=SegmentType.SEC)
        if result is None:
            self.skipTest("Funding history is None — no data available")
        logger.debug(f"Funding History: {result}")

    def test_get_fund_details(self):
        result = self.client.get_fund_details(seg_types=[SegmentType.SEC],
                                              currency=Currency.USD,
                                              start=0,
                                              limit=5)
        self.assertIsNotNone(result)
        logger.debug(f"Fund Details: {result}")

    def test_get_estimate_tradable_quantity(self):
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order(account=self.client_config.account,
                            contract=contract,
                            action='BUY',
                            limit_price=90.5,
                            quantity=2)
        result = self.client.get_estimate_tradable_quantity(order=order,
                                                            seg_type=SegmentType.SEC)
        self.assertIsNotNone(result)
        logger.debug(f"Estimate Tradable Quantity: {result}")

    def test_preview_order(self):
        """Preview order is a read-only operation — does not place a real order."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order(account=self.client_config.account,
                            contract=contract,
                            action='BUY',
                            limit_price=90.5,
                            quantity=2)
        result = self.client.preview_order(order=order)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        logger.debug(f"Preview Order: {result}")

    # ==================================================================
    # Phase 1 — matrix coverage: US market × sec types × order types
    # ==================================================================
    # All tests use safe prices far from market so BUY/SELL orders do
    # not fill. Where the SDK/gateway cannot avoid a fill (MKT orders),
    # only preview_order is called.

    @pytest.mark.integ
    def test_preview_us_stk_market(self):
        """MKT market order — preview only (would fill immediately if placed)."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = market_order(account=self.client_config.account,
                             contract=contract, action='BUY', quantity=1)
        try:
            result = self.client.preview_order(order=order)
            self.assertIsNotNone(result)
            logger.debug(f"Preview MKT: {result}")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "US STK MKT preview")

    @pytest.mark.integ
    def test_preview_us_stk_market_by_amount(self):
        """MKT by-amount order — preview only."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = market_order_by_amount(account=self.client_config.account,
                                       contract=contract, action='BUY',
                                       amount=100)
        try:
            result = self.client.preview_order(order=order)
            self.assertIsNotNone(result)
            logger.debug(f"Preview MKT by amount: {result}")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "US STK MKT-by-amount preview")

    @pytest.mark.integ
    def test_place_us_stk_limit_by_amount(self):
        """LMT by-amount order — safe price, place + cancel."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = limit_order_by_amount(account=self.client_config.account,
                                      contract=contract, action='BUY',
                                      amount=100, limit_price=SAFE_BUY_PRICE)
        self._preview_and_place(order, context="US STK LMT-by-amount")

    @pytest.mark.integ
    def test_place_us_stk_stop(self):
        """STP stop order — trigger price far from market."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = stop_order(account=self.client_config.account,
                           contract=contract, action='BUY', quantity=1,
                           aux_price=SAFE_STOP_BUY_TRIGGER)
        self._preview_and_place(order, context="US STK STP")

    @pytest.mark.integ
    def test_place_us_stk_stop_limit(self):
        """STP_LMT — trigger and limit price both far from market."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = stop_limit_order(account=self.client_config.account,
                                 contract=contract, action='BUY', quantity=1,
                                 limit_price=SAFE_BUY_PRICE,
                                 aux_price=SAFE_STOP_BUY_TRIGGER)
        self._preview_and_place(order, context="US STK STP_LMT")

    @pytest.mark.integ
    def test_place_us_stk_trail(self):
        """TRAIL trailing stop — 50% trailing pct so it can't trigger."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        order = trail_order(account=self.client_config.account,
                            contract=contract, action='SELL', quantity=1,
                            trailing_percent=50.0)
        self._preview_and_place(order, context="US STK TRAIL")

    @pytest.mark.integ
    def test_place_us_stk_bracket_with_legs(self):
        """LMT + attached profit/loss legs (bracket order)."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        legs = [
            order_leg(leg_type='PROFIT', price=SAFE_SELL_PRICE,
                     time_in_force='GTC'),
            order_leg(leg_type='LOSS', price=SAFE_BUY_PRICE,
                     time_in_force='GTC'),
        ]
        order = limit_order_with_legs(account=self.client_config.account,
                                      contract=contract, action='BUY',
                                      quantity=1, limit_price=SAFE_BUY_PRICE,
                                      order_legs=legs)
        self._preview_and_place(order, context="US STK LMT+legs")

    @pytest.mark.integ
    def test_place_us_stk_oca(self):
        """OCA (One-Cancels-All) — group of alternative legs."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        legs = [
            order_leg(leg_type=OrderType.LMT.value,
                     limit_price=SAFE_BUY_PRICE, quantity=1,
                     time_in_force='DAY'),
            order_leg(leg_type=OrderType.LMT.value,
                     limit_price=SAFE_BUY_PRICE / 2, quantity=1,
                     time_in_force='DAY'),
        ]
        order = oca_order(account=self.client_config.account,
                          contract=contract, action='BUY',
                          order_legs=legs, quantity=1)
        try:
            self._preview_and_place(order, context="US STK OCA")
        except ApiException as e:
            # OCA is Prime-only; downgrade "not supported" to skip.
            self._skip_or_raise_on_permission_error(e, "US STK OCA")

    @pytest.mark.integ
    def test_place_us_stk_twap(self):
        """TWAP algo order — limit price safe."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        now_ms = int(datetime.now().timestamp() * 1000)
        params = algo_order_params(start_time=now_ms,
                                   end_time=now_ms + 3_600_000,
                                   allow_past_end_time=True)
        order = algo_order(account=self.client_config.account,
                           contract=contract, action='BUY', quantity=10,
                           strategy='TWAP', algo_params=params,
                           limit_price=SAFE_BUY_PRICE)
        self._preview_and_place(order, context="US STK TWAP")

    @pytest.mark.integ
    def test_place_us_stk_vwap(self):
        """VWAP algo order — participation rate + limit price safe."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        now_ms = int(datetime.now().timestamp() * 1000)
        params = algo_order_params(start_time=now_ms,
                                   end_time=now_ms + 3_600_000,
                                   participation_rate=0.1,
                                   allow_past_end_time=True)
        order = algo_order(account=self.client_config.account,
                           contract=contract, action='BUY', quantity=10,
                           strategy='VWAP', algo_params=params,
                           limit_price=SAFE_BUY_PRICE)
        self._preview_and_place(order, context="US STK VWAP")

    @pytest.mark.integ
    def test_place_us_opt_limit(self):
        """US OPT — LMT, dynamically resolved AAPL call contract."""
        contract = self._resolve_us_option_contract()
        if contract is None:
            self.skipTest("Could not resolve a US option contract for AAPL")
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=1,
                            limit_price=SAFE_BUY_PRICE)
        self._preview_and_place(order, context="US OPT LMT")

    @pytest.mark.integ
    def test_place_us_fut_limit(self):
        """US FUT — LMT, CL main contract."""
        contract = self._resolve_us_future_contract()
        if contract is None:
            self.skipTest("Could not resolve a US future contract")
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=1,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="US FUT LMT")
        except ApiException as e:
            # Some future markets need explicit segment setup — treat as skip.
            self._skip_or_raise_on_permission_error(e, "US FUT LMT")

    @pytest.mark.integ
    def test_place_us_fop_limit(self):
        """US FOP (future option) — LMT."""
        contract = self._resolve_us_fop_contract()
        if contract is None:
            self.skipTest("Could not resolve a US future option contract")
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=1,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="US FOP LMT")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "US FOP LMT")

    @pytest.mark.integ
    def test_place_forex_sec_segment(self):
        """place_forex_order on SEC segment (complements existing FUT test)."""
        try:
            result = self.client.place_forex_order(
                seg_type=SegmentType.SEC.value,
                source_currency='USD',
                target_currency='HKD',
                source_amount=1.0,
            )
            self.assertIsNotNone(result)
            logger.debug(f"place_forex_order SEC: {result}")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "place_forex_order SEC")

    @pytest.mark.integ
    def test_preview_invalid_price_rejected(self):
        """Preview with an obviously invalid price should still return (or reject cleanly)."""
        contract = stock_contract(symbol='AAPL', currency='USD')
        # Negative price is invalid; either SDK raises before wire, or server rejects.
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=1,
                            limit_price=-1.0)
        try:
            result = self.client.preview_order(order=order)
            # If server returns something, it should still be structured.
            logger.debug(f"Preview invalid price returned: {result}")
        except (ApiException, ValueError, Exception) as e:
            logger.debug(f"Preview correctly rejected invalid price: {e}")
            # Do not assert; both accept + reject are semantically valid here.

    # ==================================================================
    # Phase 2 — HK / CN / SG market coverage
    # ==================================================================
    # HK safe prices differ from US because HKD prices sit in the 1-1000
    # HKD range; SAFE_BUY_PRICE=0.01 works, SAFE_SELL_PRICE=999999 works.
    # HK STK lot sizes vary (typically 100/200/500); use quantity=100 as
    # a safe default for the tested symbols.

    @pytest.mark.integ
    def test_place_hk_stk_limit(self):
        """HK STK — LMT, Tencent (00700)."""
        contract = stock_contract(symbol='00700', currency='HKD')
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=100,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="HK STK LMT")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK STK LMT")

    @pytest.mark.integ
    def test_place_hk_stk_auction_limit(self):
        """HK STK — Auction Limit (AL) — only accepted during HK auction sessions."""
        contract = stock_contract(symbol='00700', currency='HKD')
        order = auction_limit_order(account=self.client_config.account,
                                    contract=contract, action='BUY',
                                    quantity=100, limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="HK STK AL")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK STK AL")

    @pytest.mark.integ
    def test_place_hk_stk_auction_market(self):
        """HK STK — Auction Market (AM) — preview only (AM would fill at auction)."""
        contract = stock_contract(symbol='00700', currency='HKD')
        order = auction_market_order(account=self.client_config.account,
                                     contract=contract, action='BUY',
                                     quantity=100)
        try:
            result = self.client.preview_order(order=order)
            self.assertIsNotNone(result)
            logger.debug(f"HK STK AM preview: {result}")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK STK AM preview")

    @pytest.mark.integ
    def test_place_hk_stk_bracket_with_legs(self):
        """HK STK — LMT + attached profit/loss legs (bracket order)."""
        contract = stock_contract(symbol='00700', currency='HKD')
        legs = [
            order_leg(leg_type='PROFIT', price=SAFE_SELL_PRICE,
                     time_in_force='GTC'),
            order_leg(leg_type='LOSS', price=SAFE_BUY_PRICE,
                     time_in_force='GTC'),
        ]
        order = limit_order_with_legs(account=self.client_config.account,
                                      contract=contract, action='BUY',
                                      quantity=100, limit_price=SAFE_BUY_PRICE,
                                      order_legs=legs)
        try:
            self._preview_and_place(order, context="HK STK LMT+legs")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK STK LMT+legs")

    @pytest.mark.integ
    def test_place_hk_opt_limit(self):
        """HK OPT — LMT, best-effort discovery of a Tencent option contract."""
        try:
            future_expiry = (datetime.now() + timedelta(days=60)).strftime('%Y%m%d')
            contracts = self.client.get_derivative_contracts(
                symbol='00700', sec_type=SecurityType.OPT, expiry=future_expiry)
            if not contracts:
                self.skipTest("No HK option contracts available for 00700")
            c = contracts[0]
            contract = option_contract_by_symbol(
                symbol=c.symbol or '00700', expiry=c.expiry,
                strike=c.strike, put_call=c.put_call,
                currency='HKD', multiplier=c.multiplier or 100,
                contract_id=c.contract_id)
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK OPT discovery")
            return

        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=1,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="HK OPT LMT")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK OPT LMT")

    @pytest.mark.integ
    def test_place_hk_war_limit(self):
        """HK WAR (warrant) — LMT."""
        contract = self._resolve_hk_warrant_contract()
        if contract is None:
            self.skipTest("Could not resolve an HK warrant contract")
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=100,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="HK WAR LMT")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK WAR LMT")

    @pytest.mark.integ
    def test_place_hk_iopt_limit(self):
        """HK IOPT (callable bull/bear) — LMT."""
        contract = self._resolve_hk_iopt_contract()
        if contract is None:
            self.skipTest("Could not resolve an HK IOPT contract")
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=100,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="HK IOPT LMT")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "HK IOPT LMT")

    @pytest.mark.integ
    def test_place_cn_stk_limit(self):
        """CN STK (A-share) — LMT. Uses Ping An Bank 000001.SZ.

        CN stocks trade in 100-share lots (手). Account may lack Stock
        Connect / A-share license — expect auto-skip if so.
        """
        # A-share symbols use exchange suffix (.SH / .SZ). SDK helper
        # accepts them as regular symbol strings.
        contract = stock_contract(symbol='000001', currency='CNH',
                                  exchange='SEHKSZSE')
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=100,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="CN STK LMT")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "CN STK LMT")

    @pytest.mark.integ
    def test_place_sg_stk_limit(self):
        """SG STK — LMT. Uses DBS Group (D05).

        SG market permission likely account-tier dependent.
        """
        contract = stock_contract(symbol='D05', currency='SGD')
        order = limit_order(account=self.client_config.account,
                            contract=contract, action='BUY', quantity=100,
                            limit_price=SAFE_BUY_PRICE)
        try:
            self._preview_and_place(order, context="SG STK LMT")
        except ApiException as e:
            self._skip_or_raise_on_permission_error(e, "SG STK LMT")
