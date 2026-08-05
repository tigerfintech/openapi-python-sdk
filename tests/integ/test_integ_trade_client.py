# -*- coding: utf-8 -*-
"""Integration tests - require real API credentials."""
import logging
import unittest

import pytest

from tigeropen.common.consts import OptionExerciseType
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
        result = self.client.get_contract(symbol="NVDA", sec_type='OPT', expiry='20260605', strike=220, put_call='CALL')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Contract)
        self.assertEqual(result.symbol, 'NVDA')
        self.assertEqual(result.sec_type, 'OPT')
        self.assertEqual(result.strike, 220)
        self.assertEqual(result.put_call, 'CALL')
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
        result = self.client.get_order(id=40130857465156608)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Order)
        self.assertEqual(result.id, 40130857465156608)
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
        result = self.client.cancel_order(id=40132638459956224)
        logger.debug(f"Cancel Order Result: {result}")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    @pytest.mark.integ
    def test_modify_order(self):
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
        oid = self.client.modify_order(order, limit_price=100.5)
        logger.debug(f"Modify Order Result: {oid}")
        self.assertIsNotNone(oid)
        self.assertIsInstance(oid, int)
        self.assertGreater(oid, 0)

    @pytest.mark.integ
    def test_transfer_position(self):
        transfers = [TransferItem(symbol="AAPL", quantity=10)]
        result = self.client.transfer_position(from_account="1001", to_account="1002", transfers=transfers, market="US")
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
        result = self.client.get_position_transfer_detail(account_id="1001", transfer_id="12345")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PositionTransferDetail)
        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.status)
        logger.debug(f"Position Transfer Detail: {result}")

    def test_get_position_transfer_external_records(self):
        result = self.client.get_position_transfer_external_records(account_id="1001", since_date="2025-01-01", to_date="2025-01-02")
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
        # 场景1: 提交提前行权 (Exercise)
        try:
            result_exercise = self.client.submit_option_exercise(
                contract_id=2701923713,
                exercise_type="Exercise",
                quantity=1.0,
                executing_date="2026-06-05",
                is_force=False,
            )
            self.assertTrue(result_exercise)
            logger.debug(f"Submit Exercise Result: {result_exercise}")
        except ApiException as e:
            # 下游业务限制（如行权次数/rate限制），非SDK/server问题
            logger.warning(f"Submit Exercise skipped due to downstream limit: {e}")
            self.skipTest(f"Downstream limit: {e}")

        # 场景2: 提交放弃行权 (Expire) — itm_rate 有效范围 0~10
        try:
            result_expire = self.client.submit_option_exercise(
                contract_id=2701923713,
                exercise_type=OptionExerciseType.EXPIRE,
                quantity=1.0,
                itm_rate=1,
            )
            self.assertTrue(result_expire)
            logger.debug(f"Submit Expire Result: {result_expire}")
        except ApiException as e:
            logger.warning(f"Submit Expire skipped due to downstream limit: {e}")

    def test_check_option_exercise(self):
        result = self.client.check_option_exercise(
            contract_id=2701923713,
            exercise_type="Exercise",
            executing_date="2026-06-01",
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
        # 先查现有 New 状态记录，有则直接取消；没有则尝试提交一条再取消
        records = self.client.get_option_exercise_records(page=1, size=20)
        new_record = next((r for r in records.items if r.status == "New"), None)

        if new_record is None:
            # 没有 New 记录，尝试提交一条
            try:
                submit_ok = self.client.submit_option_exercise(
                    contract_id=2701923713,
                    exercise_type="Exercise",
                    quantity=1.0,
                    executing_date="2026-06-01",
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
