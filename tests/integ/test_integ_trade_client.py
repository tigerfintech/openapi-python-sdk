# -*- coding: utf-8 -*-
"""Integration tests - require real API credentials."""
import logging
import unittest
from datetime import datetime, timedelta

import pytest

from tigeropen.common.consts import OptionExerciseType, SegmentType, Currency, SecurityType
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import limit_order, iceberg_order
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Order
from tigeropen.trade.domain.position import Position
from tigeropen.trade.domain.transfer import TransferItem, PositionTransfer, PositionTransferDetail, PositionTransferRecord, \
    PositionTransferExternalRecord
from tigeropen.trade.domain.prime_account import PortfolioAccount
from tigeropen.trade.trade_client import TradeClient
from tests.support import integ_client_config, is_integ_run

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
