import json
import logging
import os
import unittest
from unittest.mock import MagicMock

from tigeropen.common.consts import OrderStatus, OptionExerciseType
from tigeropen.common.util import web_utils
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import limit_order
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Order
from tigeropen.trade.domain.transfer import TransferItem
from tigeropen.trade.trade_client import TradeClient

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class TestTradeClient(unittest.TestCase):

    def setUp(self):
        self.is_mock = False
        self.client_config = TigerOpenClientConfig(
            props_path=os.path.expanduser("~/.tigeropen/"))

        self.client: TradeClient = TradeClient(self.client_config,
                                               logger=logger)
        self.origin_do_request = web_utils.do_request

    def tearDown(self):
        web_utils.do_request = self.origin_do_request

    def test_get_positions(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755074116661,
                "data": {
                    "items": [{
                        "symbol": "NVDA",
                        "market": "US",
                        "contractId": 113,
                        "secType": "STK",
                        "account": "123123",
                        "position": 773,
                        "positionScale": 5,
                        "positionQty": 0.00773,
                        "salableQty": 0.00773,
                        "averageCost": 129.45,
                        "averageCostByAverage": 129.45,
                        "unrealizedPnl": 0.42,
                        "unrealizedPnlByAverage": 0.42,
                        "unrealizedPnlPercent": 0.4177,
                        "unrealizedPnlPercentByAverage": 0.4177,
                        "unrealizedPnlByCostOfCarry": 0.42,
                        "unrealizedPnlPercentByCostOfCarry": 0.4177,
                        "realizedPnl": 0.0,
                        "realizedPnlByAverage": 0.0,
                        "averageCostOfCarry": 129.45,
                        "marketValue": 1.4186,
                        "currency": "USD",
                        "multiplier": 1.0,
                        "status": 0,
                        "identifier": "NVDA",
                        "latestPrice": 183.52,
                        "updateTimestamp": 1755074116660,
                        "comboTypes": [],
                        "comboTypeMap": {},
                        "mmPercent": 0.0,
                        "mmValue": 0.3547,
                        "todayPnl": 0.0,
                        "todayPnlPercent": 0.002,
                        "categories": [],
                        "lastClosePrice": 183.16
                    }, {
                        "symbol": "ROSGQ",
                        "market": "US",
                        "contractId": 7451,
                        "secType": "STK",
                        "account": "123123",
                        "position": 6,
                        "positionScale": 0,
                        "positionQty": 6.0,
                        "salableQty": 6.0,
                        "averageCost": 1.1932,
                        "averageCostByAverage": 1.1932,
                        "unrealizedPnl": -7.16,
                        "unrealizedPnlByAverage": -7.16,
                        "unrealizedPnlPercent": -0.9999,
                        "unrealizedPnlPercentByAverage": -0.9999,
                        "unrealizedPnlByCostOfCarry": -7.16,
                        "unrealizedPnlPercentByCostOfCarry": -0.9999,
                        "realizedPnl": 0.0,
                        "realizedPnlByAverage": 0.0,
                        "averageCostOfCarry": 1.1932,
                        "marketValue": 6.0E-4,
                        "currency": "USD",
                        "multiplier": 1.0,
                        "status": 0,
                        "identifier": "ROSGQ",
                        "latestPrice": 1.0E-4,
                        "updateTimestamp": 1755074116660,
                        "comboTypes": [],
                        "comboTypeMap": {},
                        "mmPercent": 0.0,
                        "mmValue": 6.0E-4,
                        "todayPnl": 0.0,
                        "todayPnlPercent": 0.0,
                        "categories": [],
                        "lastClosePrice": 1.0E-4
                    }]
                }
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_positions()

            # Verify mock_result is a list of Position objects
            self.assertIsNotNone(mock_result)
            self.assertIsInstance(mock_result, list)
            self.assertEqual(len(mock_result), 2)

            # Verify the first position (NVDA)
            nvda_position = mock_result[0]
            self.assertEqual(nvda_position.account, '123123')
            self.assertEqual(nvda_position.contract.symbol, 'NVDA')
            self.assertEqual(nvda_position.contract.sec_type, 'STK')
            self.assertEqual(nvda_position.quantity, 773)
            self.assertEqual(nvda_position.position_scale, 5)
            self.assertEqual(nvda_position.average_cost, 129.45)
            self.assertEqual(nvda_position.market_price, 183.52)
            self.assertEqual(nvda_position.unrealized_pnl, 0.42)
            self.assertEqual(nvda_position.unrealized_pnl_percent, 0.4177)
            self.assertEqual(nvda_position.position_qty, 0.00773)
            self.assertEqual(nvda_position.salable_qty, 0.00773)

        else:
            result = self.client.get_positions()
            logger.debug(f"Positions: {result}")

    def test_get_contract(self):
        if self.is_mock:
            mock_data = {
                "code":
                    0,
                "message":
                    "success",
                "timestamp":
                    1755075981228,
                "data": [{
                    "contractId":
                        113,
                    "identifier":
                        "NVDA",
                    "symbol":
                        "NVDA",
                    "secType":
                        "STK",
                    "multiplier":
                        1.0,
                    "lotSize":
                        1.0,
                    "market":
                        "US",
                    "primaryExchange":
                        "NASDAQ",
                    "currency":
                        "USD",
                    "localSymbol":
                        "NVDA",
                    "tradingClass":
                        "NVDA",
                    "name":
                        "NVIDIA",
                    "status":
                        1,
                    "tradeable":
                        True,
                    "marginable":
                        True,
                    "shortMargin":
                        0.35,
                    "shortInitialMargin":
                        0.35,
                    "shortMaintenanceMargin":
                        0.3,
                    "longInitialMargin":
                        0.3,
                    "longMaintenanceMargin":
                        0.25,
                    "shortFeeRate":
                        3.75,
                    "shortable":
                        True,
                    "shortableCount":
                        38061067,
                    "closeOnly":
                        False,
                    "tickSizes": [{
                        "begin": "0",
                        "end": "1",
                        "type": "CLOSED",
                        "tickSize": 1.0E-4
                    }, {
                        "begin": "1",
                        "end": "Infinity",
                        "type": "OPEN",
                        "tickSize": 0.01
                    }],
                    "isEtf":
                        False,
                    "supportOvernightTrading":
                        True,
                    "supportFractionalShare":
                        True
                }]
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_contract(symbol="NVDA")

            # Verify the contract object was returned and is correctly typed
            self.assertIsNotNone(mock_result)

            # Verify basic contract details
            self.assertEqual(mock_result.symbol, 'NVDA')
            self.assertEqual(mock_result.identifier, 'NVDA')
            self.assertEqual(mock_result.sec_type, 'STK')
            self.assertEqual(mock_result.currency, 'USD')
            self.assertEqual(mock_result.market, 'US')
            self.assertEqual(mock_result.contract_id, 113)
            self.assertEqual(mock_result.primary_exchange, 'NASDAQ')
            self.assertEqual(mock_result.name, 'NVIDIA')

            # Verify margin and fee details
            self.assertEqual(mock_result.long_initial_margin, 0.3)
            self.assertEqual(mock_result.long_maintenance_margin, 0.25)
            self.assertEqual(mock_result.short_margin, 0.35)
            self.assertEqual(mock_result.short_initial_margin, 0.35)
            self.assertEqual(mock_result.short_maintenance_margin, 0.3)
            self.assertEqual(mock_result.short_fee_rate, 3.75)

            # Verify tradability flags
            self.assertEqual(mock_result.shortable, True)
            self.assertEqual(mock_result.shortable_count, 38061067)
            self.assertEqual(mock_result.marginable, True)
            self.assertEqual(mock_result.close_only, False)
            self.assertEqual(mock_result.multiplier, 1.0)
            self.assertEqual(mock_result.lot_size, 1.0)

            # Verify extended features
            self.assertEqual(mock_result.is_etf, False)
            self.assertEqual(mock_result.support_overnight_trading, True)
            self.assertEqual(mock_result.support_fractional_share, True)

            # Verify tick size information
            self.assertIsNotNone(mock_result.tick_sizes)
            self.assertEqual(len(mock_result.tick_sizes), 2)
            self.assertEqual(mock_result.tick_sizes[0]['begin'], '0')
            self.assertEqual(mock_result.tick_sizes[0]['end'], '1')
            self.assertEqual(mock_result.tick_sizes[0]['type'], 'CLOSED')
            self.assertEqual(mock_result.tick_sizes[0]['tick_size'], 0.0001)
            self.assertEqual(mock_result.tick_sizes[1]['begin'], '1')
            self.assertEqual(mock_result.tick_sizes[1]['end'], 'Infinity')
            self.assertEqual(mock_result.tick_sizes[1]['type'], 'OPEN')
            self.assertEqual(mock_result.tick_sizes[1]['tick_size'], 0.01)
        else:
            result = self.client.get_contract(symbol="NVDA", sec_type='OPT', expiry='20260605', strike=220, put_call='CALL')
            logger.debug(f"Contracts: {result.to_dict()}")

    def test_get_orders(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755077013218,
                "data": {
                    "nextPageToken":
                        "b3JkZXJzfG51bGx8bnVsbHw0MDEzMDg1NzQ2NTE1NjYwOA==",
                    "items": [{
                        "symbol": "61486",
                        "market": "HK",
                        "secType": "IOPT",
                        "currency": "HKD",
                        "expiry": "20260930",
                        "strike": "114.0",
                        "right": "CALL",
                        "identifier": "61486",
                        "id": 40130901147389952,
                        "externalId": "1755073615.997798",
                        "orderId": 0,
                        "account": "123123",
                        "action": "BUY",
                        "orderType": "LMT",
                        "limitPrice": 0.023,
                        "totalQuantity": 5000,
                        "totalQuantityScale": 0,
                        "filledQuantity": 0,
                        "filledQuantityScale": 0,
                        "filledCashAmount": 0.0,
                        "avgFillPrice": 0.0,
                        "timeInForce": "DAY",
                        "outsideRth": False,
                        "commission": 0.0,
                        "gst": 0.0,
                        "realizedPnl": 0.0,
                        "liquidation": False,
                        "openTime": 1755073677000,
                        "updateTime": 1755073700000,
                        "latestTime": 1755073700000,
                        "name": "SG#MTUANRC2609E.C",
                        "attrDesc": "",
                        "userMark": "",
                        "attrList": [],
                        "algoStrategy": "LMT",
                        "status": "Cancelled",
                        "source": "iOS",
                        "discount": 0,
                        "replaceStatus": "NONE",
                        "cancelStatus": "RECEIVED",
                        "canModify": False,
                        "canCancel": False,
                        "isOpen": True,
                        "orderDiscount": 0,
                        "tradingSessionType": "RTH"
                    }, {
                        "symbol":
                            "AAPL",
                        "market":
                            "US",
                        "secType":
                            "MLEG",
                        "currency":
                            "USD",
                        "identifier":
                            "AAPL",
                        "id":
                            40130857465156608,
                        "externalId":
                            "1755073339.428326",
                        "orderId":
                            0,
                        "account":
                            "123123",
                        "action":
                            "BUY",
                        "orderType":
                            "LMT",
                        "limitPrice":
                            -2.52,
                        "totalQuantity":
                            1,
                        "totalQuantityScale":
                            0,
                        "filledQuantity":
                            0,
                        "filledQuantityScale":
                            0,
                        "filledCashAmount":
                            0.0,
                        "avgFillPrice":
                            0.0,
                        "timeInForce":
                            "DAY",
                        "outsideRth":
                            False,
                        "commission":
                            0.0,
                        "gst":
                            0.0,
                        "realizedPnl":
                            0.0,
                        "liquidation":
                            False,
                        "openTime":
                            1755073344000,
                        "updateTime":
                            1755073361000,
                        "latestTime":
                            1755073361000,
                        "name":
                            "AAPL VERTICAL 250815 PUT 227.5/PUT 232.5",
                        "attrDesc":
                            "",
                        "userMark":
                            "",
                        "attrList": [],
                        "algoStrategy":
                            "LMT",
                        "status":
                            "Cancelled",
                        "source":
                            "iOS",
                        "discount":
                            0,
                        "replaceStatus":
                            "NONE",
                        "cancelStatus":
                            "RECEIVED",
                        "canModify":
                            False,
                        "canCancel":
                            False,
                        "isOpen":
                            True,
                        "orderDiscount":
                            0,
                        "comboType":
                            "VERTICAL",
                        "comboTypeDesc":
                            "Vertical",
                        "legs": [{
                            "symbol": "AAPL",
                            "expiry": "20250815",
                            "strike": "227.5",
                            "right": "PUT",
                            "action": "BUY",
                            "secType": "OPT",
                            "ratio": 1,
                            "market": "US",
                            "currency": "USD",
                            "multiplier": 100,
                            "totalQuantity": 1.0,
                            "filledQuantity": 0.0,
                            "avgFilledPrice": 0.0,
                            "createdAt": 1755073344483,
                            "updatedAt": 1755073344483
                        }, {
                            "symbol": "AAPL",
                            "expiry": "20250815",
                            "strike": "232.5",
                            "right": "PUT",
                            "action": "SELL",
                            "secType": "OPT",
                            "ratio": 1,
                            "market": "US",
                            "currency": "USD",
                            "multiplier": 100,
                            "totalQuantity": 1.0,
                            "filledQuantity": 0.0,
                            "avgFilledPrice": 0.0,
                            "createdAt": 1755073344482,
                            "updatedAt": 1755073344482
                        }],
                        "tradingSessionType":
                            "RTH"
                    }]
                }
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_orders()

            # Verify mock_result is a list of Order objects
            self.assertIsNotNone(mock_result)
            self.assertIsInstance(mock_result, list)
            self.assertEqual(len(mock_result), 2)

            # Verify the first order details (IOPT)
            iopt_order = mock_result[0]
            self.assertEqual(iopt_order.id, 40130901147389952)
            self.assertEqual(iopt_order.account, '123123')
            self.assertEqual(iopt_order.contract.symbol, '61486')
            self.assertEqual(iopt_order.contract.sec_type, 'IOPT')
            self.assertEqual(iopt_order.contract.currency, 'HKD')
            self.assertEqual(iopt_order.action, 'BUY')
            self.assertEqual(iopt_order.order_type, 'LMT')
            self.assertEqual(iopt_order.limit_price, 0.023)
            self.assertEqual(iopt_order.quantity, 5000)
            self.assertEqual(iopt_order.status, OrderStatus.CANCELLED)
            self.assertEqual(iopt_order.time_in_force, 'DAY')
            self.assertEqual(iopt_order.outside_rth, False)

            # Verify the second order details (MLEG/combo order)
            mleg_order = mock_result[1]
            self.assertEqual(mleg_order.id, 40130857465156608)
            self.assertEqual(mleg_order.account, '123123')
            self.assertEqual(mleg_order.contract.symbol, 'AAPL')
            self.assertEqual(mleg_order.contract.sec_type, 'MLEG')
            self.assertEqual(mleg_order.contract.currency, 'USD')
            self.assertEqual(mleg_order.action, 'BUY')
            self.assertEqual(mleg_order.order_type, 'LMT')
            self.assertEqual(mleg_order.limit_price, -2.52)
            self.assertEqual(mleg_order.quantity, 1)
            self.assertEqual(mleg_order.status, OrderStatus.CANCELLED)
            self.assertEqual(mleg_order.combo_type, 'VERTICAL')

            # Verify contract legs for the combo order
            self.assertIsNotNone(mleg_order.contract_legs)
            self.assertEqual(len(mleg_order.contract_legs), 2)

            # First leg (BUY PUT)
            buy_leg = mleg_order.contract_legs[0]
            self.assertEqual(buy_leg.symbol, 'AAPL')
            self.assertEqual(buy_leg.sec_type, 'OPT')
            self.assertEqual(buy_leg.expiry, '20250815')
            self.assertEqual(buy_leg.strike, '227.5')
            self.assertEqual(buy_leg.put_call, 'PUT')
            self.assertEqual(buy_leg.action, 'BUY')

            # Second leg (SELL PUT)
            sell_leg = mleg_order.contract_legs[1]
            self.assertEqual(sell_leg.symbol, 'AAPL')
            self.assertEqual(sell_leg.sec_type, 'OPT')
            self.assertEqual(sell_leg.expiry, '20250815')
            self.assertEqual(sell_leg.strike, '232.5')
            self.assertEqual(sell_leg.put_call, 'PUT')
            self.assertEqual(sell_leg.action, 'SELL')
        else:
            result = self.client.get_orders(limit=2)
            logger.debug(f"Orders: {result}")

    def test_get_order(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755089070452,
                "data": {
                    "symbol":
                        "AAPL",
                    "market":
                        "US",
                    "secType":
                        "MLEG",
                    "currency":
                        "USD",
                    "identifier":
                        "AAPL",
                    "id":
                        40130857465156608,
                    "externalId":
                        "1755073339.428326",
                    "orderId":
                        0,
                    "account":
                        "123123",
                    "action":
                        "BUY",
                    "orderType":
                        "LMT",
                    "limitPrice":
                        -2.52,
                    "totalQuantity":
                        1,
                    "totalQuantityScale":
                        0,
                    "filledQuantity":
                        0,
                    "filledQuantityScale":
                        0,
                    "filledCashAmount":
                        0.0,
                    "avgFillPrice":
                        0.0,
                    "timeInForce":
                        "DAY",
                    "outsideRth":
                        False,
                    "commission":
                        0.0,
                    "gst":
                        0.0,
                    "realizedPnl":
                        0.0,
                    "liquidation":
                        False,
                    "openTime":
                        1755073344000,
                    "updateTime":
                        1755073361000,
                    "latestTime":
                        1755073361000,
                    "name":
                        "AAPL VERTICAL 250815 PUT 227.5/PUT 232.5",
                    "attrDesc":
                        "",
                    "userMark":
                        "",
                    "attrList": [],
                    "algoStrategy":
                        "LMT",
                    "status":
                        "Cancelled",
                    "source":
                        "iOS",
                    "discount":
                        0,
                    "replaceStatus":
                        "NONE",
                    "cancelStatus":
                        "RECEIVED",
                    "canModify":
                        False,
                    "canCancel":
                        False,
                    "isOpen":
                        True,
                    "orderDiscount":
                        0,
                    "comboType":
                        "VERTICAL",
                    "comboTypeDesc":
                        "Vertical",
                    "legs": [{
                        "symbol": "AAPL",
                        "expiry": "20250815",
                        "strike": "227.5",
                        "right": "PUT",
                        "action": "BUY",
                        "secType": "OPT",
                        "ratio": 1,
                        "market": "US",
                        "currency": "USD",
                        "multiplier": 100,
                        "totalQuantity": 1.0,
                        "filledQuantity": 0.0,
                        "avgFilledPrice": 0.0,
                        "createdAt": 1755073344483,
                        "updatedAt": 1755073344483
                    }, {
                        "symbol": "AAPL",
                        "expiry": "20250815",
                        "strike": "232.5",
                        "right": "PUT",
                        "action": "SELL",
                        "secType": "OPT",
                        "ratio": 1,
                        "market": "US",
                        "currency": "USD",
                        "multiplier": 100,
                        "totalQuantity": 1.0,
                        "filledQuantity": 0.0,
                        "avgFilledPrice": 0.0,
                        "createdAt": 1755073344482,
                        "updatedAt": 1755073344482
                    }],
                    "tradingSessionType":
                        "RTH"
                }
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_order(order_id=40130857465156608)

            # Verify the order object was returned
            self.assertIsNotNone(mock_result)

            # Verify basic order information
            self.assertEqual(mock_result.id, 40130857465156608)
            self.assertEqual(mock_result.account, "123123")
            self.assertEqual(mock_result.action, "BUY")
            self.assertEqual(mock_result.order_type, "LMT")
            self.assertEqual(mock_result.limit_price, -2.52)
            self.assertEqual(mock_result.quantity, 1)
            self.assertEqual(
                mock_result.status,
                OrderStatus.CANCELLED)  # Ensure proper status enum conversion
            self.assertEqual(mock_result.filled, 0)

            # Verify timing attributes
            self.assertEqual(mock_result.order_time, 1755073344000)
            self.assertEqual(mock_result.update_time, 1755073361000)

            # Verify contract information
            self.assertEqual(mock_result.contract.symbol, "AAPL")
            self.assertEqual(mock_result.contract.sec_type, "MLEG")
            self.assertEqual(mock_result.contract.currency, "USD")

            # Verify order flags and settings
            self.assertEqual(mock_result.time_in_force, "DAY")
            self.assertEqual(mock_result.outside_rth, False)
            self.assertEqual(mock_result.combo_type, "VERTICAL")
            self.assertEqual(mock_result.is_open, True)

            # Verify contract legs for combo order
            self.assertIsNotNone(mock_result.contract_legs)
            self.assertEqual(len(mock_result.contract_legs), 2)

            # Verify first leg details (BUY PUT)
            leg1 = mock_result.contract_legs[0]
            self.assertEqual(leg1.symbol, "AAPL")
            self.assertEqual(leg1.sec_type, "OPT")
            self.assertEqual(leg1.expiry, "20250815")
            self.assertEqual(leg1.strike, "227.5")
            self.assertEqual(leg1.put_call, "PUT")
            self.assertEqual(leg1.action, "BUY")

            # Verify second leg details (SELL PUT)
            leg2 = mock_result.contract_legs[1]
            self.assertEqual(leg2.symbol, "AAPL")
            self.assertEqual(leg2.sec_type, "OPT")
            self.assertEqual(leg2.expiry, "20250815")
            self.assertEqual(leg2.strike, "232.5")
            self.assertEqual(leg2.put_call, "PUT")
            self.assertEqual(leg2.action, "SELL")

        else:
            result = self.client.get_order(id=40130857465156608)
            logger.debug(f"Order: {result.to_dict()}")

    def test_get_transactions(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1766374646884,
                "data": {
                    "nextPageToken": "b3JkZXJfdHJhbnNhY3Rpb25zfDB8MHx8fDQwNjgzNzAxMTc1MTkzNjAw",
                    "items": [{
                        "id": 41063075987197952,
                        "accountId": 7350302,
                        "orderId": 41063075975138304,
                        "secType": "FOREX",
                        "symbol": "USD.HKD",
                        "currency": "HKD",
                        "market": "US",
                        "action": "SELL",
                        "filledQuantity": 10,
                        "filledQuantityScale": 0,
                        "filledPrice": 7.76064,
                        "filledAmount": 77.61,
                        "transactedAt": "2025-11-04 00:00:07",
                        "transactionTime": 1762185607350
                    }, {
                        "id": 40683701175193600,
                        "accountId": 7350302,
                        "orderId": 40683701159202816,
                        "secType": "FOREX",
                        "symbol": "USD.HKD",
                        "currency": "HKD",
                        "market": "US",
                        "action": "SELL",
                        "filledQuantity": 10,
                        "filledQuantityScale": 0,
                        "filledPrice": 7.76947,
                        "filledAmount": 77.69,
                        "transactedAt": "2025-10-01 12:00:07",
                        "transactionTime": 1759291207230
                    }]
                }
            }

            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_transactions()

            # Verify result is a list of Transaction objects
            self.assertIsNotNone(mock_result)
            self.assertIsInstance(mock_result, list)
            self.assertEqual(len(mock_result), 2)

            # Verify first transaction
            t0 = mock_result[0]
            self.assertEqual(t0.id, 41063075987197952)
            self.assertEqual(t0.account, 7350302)
            self.assertEqual(t0.order_id, 41063075975138304)
            self.assertIsNotNone(t0.contract)
            self.assertEqual(t0.contract.symbol, 'USD.HKD')
            self.assertEqual(t0.action, 'SELL')
            self.assertEqual(t0.filled_quantity, 10)
            self.assertEqual(t0.filled_price, 7.76064)
            self.assertEqual(t0.filled_amount, 77.61)
            self.assertEqual(t0.transacted_at, '2025-11-04 00:00:07')
            # transaction_time may be set as attribute from response
            self.assertEqual(getattr(t0, 'transaction_time'), 1762185607350)

            # Verify second transaction
            t1 = mock_result[1]
            self.assertEqual(t1.id, 40683701175193600)
            self.assertEqual(t1.account, 7350302)
            self.assertEqual(t1.order_id, 40683701159202816)
            self.assertEqual(t1.contract.symbol, 'USD.HKD')
            self.assertEqual(t1.filled_price, 7.76947)
            self.assertEqual(t1.filled_amount, 77.69)
            self.assertEqual(t1.transacted_at, '2025-10-01 12:00:07')
            self.assertEqual(getattr(t1, 'transaction_time'), 1759291207230)

    def test_get_prime_assets(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755078296228,
                "data": {
                    "accountId":
                        "123123",
                    "segments": [{
                        "capability":
                            "RegTMargin",
                        "category":
                            "S",
                        "currency":
                            "USD",
                        "cashBalance":
                            7198.59,
                        "cashAvailableForTrade":
                            5717.69,
                        "grossPositionValue":
                            -250.58,
                        "equityWithLoan":
                            7200.00,
                        "netLiquidation":
                            6948.00,
                        "initMargin":
                            500.42,
                        "maintainMargin":
                            500.35,
                        "overnightMargin":
                            500.35,
                        "unrealizedPL":
                            5.85,
                        "unrealizedPLByCostOfCarry":
                            5.85,
                        "realizedPL":
                            0.00,
                        "totalTodayPL":
                            0.00,
                        "excessLiquidation":
                            6699.65,
                        "overnightLiquidation":
                            6699.65,
                        "buyingPower":
                            22870.76,
                        "lockedFunds":
                            981.89,
                        "leverage":
                            0.08,
                        "uncollected":
                            0.00,
                        "currencyAssets": [{
                            "currency": "USD",
                            "cashBalance": 6302.06,
                            "cashAvailableForTrade": 5320.17,
                            "forexRate": 1.0
                        }, {
                            "currency": "HKD",
                            "cashBalance": 5800.29,
                            "cashAvailableForTrade": 5800.29,
                            "forexRate": 0.1279
                        }, {
                            "currency": "NZD",
                            "cashBalance": 1.50,
                            "cashAvailableForTrade": 1.50,
                            "forexRate": 0.6201
                        }, {
                            "currency": "CNH",
                            "cashBalance": 1123.95,
                            "cashAvailableForTrade": 1123.95,
                            "forexRate": 0.1415
                        }, {
                            "currency": "AUD",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00,
                            "forexRate": 0.6651
                        }, {
                            "currency": "EUR",
                            "cashBalance": 0.12,
                            "cashAvailableForTrade": 0.12,
                            "forexRate": 1.0080
                        }],
                        "consolidatedSegTypes": ["SEC", "FUND"]
                    }, {
                        "capability":
                            "RegTMargin",
                        "category":
                            "C",
                        "currency":
                            "USD",
                        "cashBalance":
                            2302.46,
                        "cashAvailableForTrade":
                            2302.46,
                        "grossPositionValue":
                            0.00,
                        "equityWithLoan":
                            2302.46,
                        "netLiquidation":
                            2302.46,
                        "initMargin":
                            0.00,
                        "maintainMargin":
                            0.00,
                        "overnightMargin":
                            0.00,
                        "unrealizedPL":
                            0.00,
                        "unrealizedPLByCostOfCarry":
                            0.00,
                        "realizedPL":
                            2.46,
                        "totalTodayPL":
                            2.46,
                        "excessLiquidation":
                            2302.46,
                        "overnightLiquidation":
                            2302.46,
                        "buyingPower":
                            0.00,
                        "lockedFunds":
                            0.00,
                        "leverage":
                            0.00,
                        "uncollected":
                            0.00,
                        "currencyAssets": [{
                            "currency": "USD",
                            "cashBalance": 2302.46,
                            "cashAvailableForTrade": 2302.46,
                            "forexRate": 1.0
                        }, {
                            "currency": "HKD",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00,
                            "forexRate": 0.1279
                        }, {
                            "currency": "CNH",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00,
                            "forexRate": 0.1415
                        }],
                        "consolidatedSegTypes": ["FUT"]
                    }, {
                        "capability":
                            "RegTMargin",
                        "category":
                            "F",
                        "currency":
                            "USD",
                        "cashBalance":
                            0.00,
                        "cashAvailableForTrade":
                            5717.69,
                        "grossPositionValue":
                            0.00,
                        "equityWithLoan":
                            7200.00,
                        "netLiquidation":
                            0.00,
                        "initMargin":
                            500.42,
                        "maintainMargin":
                            500.35,
                        "overnightMargin":
                            500.35,
                        "unrealizedPL":
                            0.00,
                        "unrealizedPLByCostOfCarry":
                            0.00,
                        "realizedPL":
                            0.78,
                        "totalTodayPL":
                            0.00,
                        "excessLiquidation":
                            6699.65,
                        "overnightLiquidation":
                            6699.65,
                        "buyingPower":
                            22870.76,
                        "lockedFunds":
                            981.89,
                        "leverage":
                            0.08,
                        "uncollected":
                            0.00,
                        "currencyAssets": [{
                            "currency": "USD",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00,
                            "forexRate": 1.0
                        }, {
                            "currency": "HKD",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00,
                            "forexRate": 0.1279
                        }, {
                            "currency": "CNH",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00,
                            "forexRate": 0.1415
                        }],
                        "consolidatedSegTypes": ["SEC", "FUND"]
                    }],
                    "updateTimestamp":
                        1755078296228
                }
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.get_prime_assets()

            # Verify the PortfolioAccount object was returned properly
            self.assertIsNotNone(mock_result)

            # Verify account info
            self.assertEqual(mock_result.account, '123123')
            self.assertEqual(mock_result.update_timestamp, 1755078296228)

            # Verify segments
            self.assertIsNotNone(mock_result.segments)
            self.assertEqual(len(mock_result.segments), 3)
            self.assertIn('S', mock_result.segments)  # Stock segment
            self.assertIn('C',
                          mock_result.segments)  # Commodity futures segment
            self.assertIn('F',
                          mock_result.segments)  # Financial futures segment

            # Verify stock segment (S) details
            stock_segment = mock_result.segments['S']
            self.assertEqual(stock_segment.currency, 'USD')
            self.assertEqual(stock_segment.capability, 'RegTMargin')
            self.assertEqual(stock_segment.category, 'S')
            self.assertEqual(stock_segment.cash_balance, 7198.59)
            self.assertEqual(stock_segment.cash_available_for_trade, 5717.69)
            self.assertEqual(stock_segment.gross_position_value, -250.58)
            self.assertEqual(stock_segment.equity_with_loan, 7200.00)
            self.assertEqual(stock_segment.net_liquidation, 6948.00)
            self.assertEqual(stock_segment.buying_power, 22870.76)
            self.assertEqual(stock_segment.leverage, 0.08)
            self.assertEqual(stock_segment.locked_funds, 981.89)

            # Verify currency assets in stock segment
            self.assertIsNotNone(stock_segment.currency_assets)
            self.assertEqual(len(stock_segment.currency_assets),
                             6)  # USD, HKD, NZD, CNH, AUD, EUR

            # Check USD assets
            usd_asset = stock_segment.currency_assets['USD']
            self.assertEqual(usd_asset.currency, 'USD')
            self.assertEqual(usd_asset.cash_balance, 6302.06)
            self.assertEqual(usd_asset.cash_available_for_trade, 5320.17)
            # Verify forex rate for USD
            self.assertEqual(usd_asset.forex_rate, 1.0)

            # Check HKD assets
            hkd_asset = stock_segment.currency_assets['HKD']
            self.assertEqual(hkd_asset.currency, 'HKD')
            self.assertEqual(hkd_asset.cash_balance, 5800.29)
            self.assertEqual(hkd_asset.cash_available_for_trade, 5800.29)
            # Verify forex rate for HKD
            self.assertEqual(hkd_asset.forex_rate, 0.1279)

            # Verify commodity futures segment (C)
            commodity_segment = mock_result.segments['C']
            self.assertEqual(commodity_segment.currency, 'USD')
            self.assertEqual(commodity_segment.category, 'C')
            self.assertEqual(commodity_segment.cash_balance, 2302.46)
            self.assertEqual(commodity_segment.cash_available_for_trade,
                             2302.46)
            self.assertEqual(commodity_segment.realized_pl, 2.46)
            self.assertEqual(commodity_segment.consolidated_seg_types, ['FUT'])

            # Verify financial futures segment (F)
            financial_segment = mock_result.segments['F']
            self.assertEqual(financial_segment.currency, 'USD')
            self.assertEqual(financial_segment.category, 'F')
            self.assertEqual(financial_segment.cash_balance, 0.00)
            self.assertEqual(financial_segment.realized_pl, 0.78)
            self.assertEqual(financial_segment.consolidated_seg_types,
                             ['SEC', 'FUND'])

        else:
            result = self.client.get_prime_assets()
            logger.debug(f"Prime Assets: {result}")

    def test_place_order(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755086932402,
                "data": {
                    "id":
                        40132638459956224,
                    "subIds": [],
                    "order_id":
                        1169,
                    "orders": [{
                        "symbol": "AAPL",
                        "market": "US",
                        "secType": "STK",
                        "currency": "USD",
                        "identifier": "AAPL",
                        "id": 40132638459956224,
                        "externalId": "1169",
                        "orderId": 1169,
                        "account": "123123",
                        "action": "BUY",
                        "orderType": "LMT",
                        "limitPrice": 90.5,
                        "totalQuantity": 2,
                        "totalQuantityScale": 0,
                        "filledQuantity": 0,
                        "filledQuantityScale": 0,
                        "filledCashAmount": 0.0,
                        "avgFillPrice": 0.0,
                        "timeInForce": "DAY",
                        "outsideRth": True,
                        "commission": 0.0,
                        "gst": 0.0,
                        "realizedPnl": 0.0,
                        "remark": "",
                        "liquidation": False,
                        "openTime": 1755086932000,
                        "updateTime": 1755086932000,
                        "latestTime": 1755086932000,
                        "name": "Apple",
                        "latestPrice": 230.14,
                        "attrDesc": "",
                        "userMark": "",
                        "attrList": [],
                        "algoStrategy": "LMT",
                        "status": "Initial",
                        "source": "OpenApi",
                        "discount": 0,
                        "replaceStatus": "NONE",
                        "cancelStatus": "NONE",
                        "canModify": True,
                        "canCancel": True,
                        "isOpen": True,
                        "orderDiscount": 0,
                        "tradingSessionType": "PRE_RTH_POST"
                    }]
                }
            }

            # Create a mock order object for testing
            from tigeropen.trade.domain.order import Order
            from tigeropen.trade.domain.contract import Contract

            mock_contract = Contract()
            mock_contract.symbol = "AAPL"
            mock_contract.currency = "USD"
            mock_contract.sec_type = "STK"

            mock_order = Order(account="123123",
                               contract=mock_contract,
                               action="BUY",
                               order_type="LMT",
                               quantity=2)
            mock_order.limit_price = 90.5
            mock_order.outside_rth = True
            mock_order.time_in_force = "DAY"

            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())
            mock_result = self.client.place_order(order=mock_order)

            # Verify the order ID was returned
            self.assertIsNotNone(mock_result)
            self.assertEqual(mock_result, 40132638459956224)

            # Verify the order object was updated with the response data
            self.assertEqual(mock_order.id, 40132638459956224)
            # self.assertEqual(mock_order.order_id, 1169)
            self.assertIsNotNone(mock_order.orders)
            self.assertEqual(len(mock_order.orders), 1)

            # Verify order details were correctly set in the submitted order
            submitted_order = mock_order.orders[0]
            self.assertEqual(submitted_order['symbol'], "AAPL")
            self.assertEqual(submitted_order['market'], "US")
            self.assertEqual(submitted_order['secType'], "STK")
            self.assertEqual(submitted_order['action'], "BUY")
            self.assertEqual(submitted_order['orderType'], "LMT")
            self.assertEqual(submitted_order['limitPrice'], 90.5)
            self.assertEqual(submitted_order['totalQuantity'], 2)
            self.assertEqual(submitted_order['outsideRth'], True)
            self.assertEqual(submitted_order['timeInForce'], "DAY")
            self.assertEqual(submitted_order['status'], "Initial")

        else:
            contract = stock_contract(symbol='AAPL', currency='USD')
            order = limit_order(account=self.client_config.account,
                                contract=contract,
                                action='BUY',
                                limit_price=90.5,
                                quantity=2)
            result = self.client.place_order(order=order)
            logger.debug(f"Order Result: {result}")

    def test_cancel_order(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755089890524,
                "data": {
                    "id": 40132638459956224
                }
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            # Test cancelling by order_id
            mock_result_by_order_id = self.client.cancel_order(
                order_id=40132638459956224)

            # Verify the order ID was returned
            self.assertIsNotNone(mock_result_by_order_id)
            self.assertEqual(mock_result_by_order_id, 40132638459956224)

            # Test cancelling by global id
            mock_result_by_id = self.client.cancel_order(id=40132638459956224)
            self.assertIsNotNone(mock_result_by_id)
            self.assertEqual(mock_result_by_id, 40132638459956224)

            # Test cancelling with account specified
            mock_result_with_account = self.client.cancel_order(
                account="123123", id=40132638459956224)
            self.assertIsNotNone(mock_result_with_account)
            self.assertEqual(mock_result_with_account, 40132638459956224)

        else:
            result = self.client.cancel_order(id=40132638459956224)
            logger.debug(f"Cancel Order Result: {result}")

    def test_modify_order(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755138568508,
                "data": {
                    "id": 40139406481165312
                }
            }
            web_utils.do_request = MagicMock(
                return_value=json.dumps(mock_data).encode())

            mock_contract = Contract()
            mock_contract.symbol = "AAPL"
            mock_contract.currency = "USD"
            mock_contract.sec_type = "STK"

            mock_order = Order(account="123123",
                               contract=mock_contract,
                               action="BUY",
                               order_type="LMT",
                               quantity=2)
            mock_order.id = 40139406481165312
            mock_order.order_id = 1169
            mock_order.limit_price = 90.5
            mock_order.time_in_force = "DAY"

            # Test modifying price only
            mock_result_price_only = self.client.modify_order(
                order=mock_order, limit_price=100.5)
            self.assertIsNotNone(mock_result_price_only)
            self.assertEqual(mock_result_price_only, 40139406481165312)

            # Test modifying multiple parameters
            mock_result_multiple = self.client.modify_order(
                order=mock_order,
                quantity=5,
                limit_price=105.5,
                time_in_force="GTC",
                outside_rth=True)
            self.assertIsNotNone(mock_result_multiple)
            self.assertEqual(mock_result_multiple, 40139406481165312)

        else:
            contract = stock_contract(symbol='AAPL', currency='USD')
            order = limit_order(account=self.client_config.account,
                                contract=contract,
                                action='BUY',
                                limit_price=90.5,
                                quantity=2)
            result = self.client.place_order(order=order)
            logger.debug(f"Place Order Result: {result}")
            oid = self.client.modify_order(order, limit_price=100.5)
            logger.debug(f"Modify Order Result: {oid}")

    def test_transfer_position(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "data": {
                    "id": "12345",
                    "accountId": "1001",
                    "counterpartyAccountId": "1002",
                    "method": "INTERNAL",
                    "direction": "OUT",
                    "status": "PENDING",
                    "comment": "test transfer",
                    "userId": "u1",
                    "userName": "user1",
                    "memo": "memo1",
                    "finishedAt": "2025-01-01",
                    "updatedAt": "2025-01-01",
                    "createdAt": "2025-01-01"
                }
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            transfers = [TransferItem(symbol="AAPL", quantity=10)]
            mock_result = self.client.transfer_position(from_account="1001", to_account="1002", transfers=transfers, market="US")

            self.assertIsNotNone(mock_result)
            self.assertEqual(mock_result.id, "12345")
            self.assertEqual(mock_result.account_id, "1001")
            self.assertEqual(mock_result.counterparty_account_id, "1002")
            self.assertEqual(mock_result.status, "PENDING")
        else:
            transfers = [TransferItem(symbol="AAPL", quantity=10)]
            result = self.client.transfer_position(from_account="1001", to_account="1002", transfers=transfers, market="US")
            logger.debug(f"Transfer Position Result: {result}")

    def test_get_position_transfer_records(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "data": [
                    {
                        "id": "12345",
                        "accountId": "1001",
                        "counterpartyAccountId": "1002",
                        "method": "INTERNAL",
                        "direction": "OUT",
                        "status": "PENDING",
                        "memo": "memo1",
                        "userId": "u1",
                        "userName": "user1",
                        "finishedAt": "2025-01-01",
                        "updatedAt": "2025-01-01",
                        "createdAt": "2025-01-01"
                    }
                ]
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_position_transfer_records(since_date="2025-01-01", to_date="2025-01-02")

            self.assertIsNotNone(mock_result)
            self.assertIsInstance(mock_result, list)
            self.assertEqual(len(mock_result), 1)
            self.assertEqual(mock_result[0].id, "12345")
            self.assertEqual(mock_result[0].account_id, "1001")
        else:
            result = self.client.get_position_transfer_records(since_date="2025-01-01", to_date="2025-01-02")
            logger.debug(f"Position Transfer Records: {result}")

    def test_get_position_transfer_detail(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "data": {
                    "id": "12345",
                    "accountId": "1001",
                    "detail": [
                        {
                            "id": "d1",
                            "transferId": "12345",
                            "symbol": "AAPL",
                            "quantity": 10
                        }
                    ]
                }
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_position_transfer_detail(account_id="1001", transfer_id="12345")

            self.assertIsNotNone(mock_result)
            self.assertEqual(mock_result.id, "12345")
            self.assertEqual(len(mock_result.detail), 1)
            self.assertEqual(mock_result.detail[0].symbol, "AAPL")
        else:
            result = self.client.get_position_transfer_detail(account_id="1001", transfer_id="12345")
            logger.debug(f"Position Transfer Detail: {result}")

    def test_get_position_transfer_external_records(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "data": [
                    {
                        "id": "ext1",
                        "accountId": "1001",
                        "status": "PENDING",
                        "transferPropertyInfos": [
                            {
                                "symbol": "AAPL",
                                "quantity": 100
                            }
                        ]
                    }
                ]
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            mock_result = self.client.get_position_transfer_external_records(account_id="1001", since_date="2025-01-01", to_date="2025-01-02")

            self.assertIsNotNone(mock_result)
            self.assertIsInstance(mock_result, list)
            self.assertEqual(len(mock_result), 1)
            self.assertEqual(mock_result[0].id, "ext1")
            self.assertEqual(len(mock_result[0].transfer_property_infos), 1)
            self.assertEqual(mock_result[0].transfer_property_infos[0].symbol, "AAPL")
        else:
            result = self.client.get_position_transfer_external_records(account_id="1001", since_date="2025-01-01", to_date="2025-01-02")

    def test_submit_option_exercise(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755200000000,
                "data": None
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            # Test with str
            result = self.client.submit_option_exercise(
                contract_id=112233,
                exercise_type="Exercise",
                quantity=1.0,
                executing_date="2025-06-20",
                is_force=False,
            )
            self.assertTrue(result)

            # Test with OptionExerciseType enum
            result_enum = self.client.submit_option_exercise(
                contract_id=112233,
                exercise_type=OptionExerciseType.EXERCISE,
                quantity=1.0,
                executing_date="2025-06-20",
                is_force=False,
            )
            self.assertTrue(result_enum)

            # Test Expire type via enum, itm_rate optional (0-10), defaults to 0
            result_expire = self.client.submit_option_exercise(
                contract_id=112233,
                exercise_type=OptionExerciseType.EXPIRE,
                quantity=1.0,
                itm_rate=5,
            )
            self.assertTrue(result_expire)
        else:
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
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755200000000,
                "data": {
                    "availableQuantity": 5.0,
                    "position": 5.0,
                    "stkPosition": 0.0,
                    "stkPositionChange": 500.0,
                    "stkPositionBefore": 0.0,
                    "stkPositionAfter": 500.0,
                    "symbol": "AAPL"
                }
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            result = self.client.check_option_exercise(
                contract_id=2702385833,
                exercise_type="Exercise",
                quantity=5.0,
                executing_date="2025-06-20",
                is_force=False,
            )
            self.assertIsNotNone(result)
            self.assertEqual(result.available_quantity, 5.0)
            self.assertEqual(result.symbol, "AAPL")
            self.assertEqual(result.stk_position_after, 500.0)
        else:
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
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1779795108734,
                "data": {
                    "pageNum": 1,
                    "pageSize": 20,
                    "itemCount": 2,
                    "pageCount": 1,
                    "items": [
                        {
                            "id": 302,
                            "type": "Exercise",
                            "status": "New",
                            "contractId": 2701923713,
                            "symbol": "AAPL",
                            "stkSymbol": "AAPL",
                            "expireDate": "20260605",
                            "strike": "305.0",
                            "callPut": "PUT",
                            "accountId": 600021133765,
                            "requestQuantity": 1.0,
                            "quantity": 0.0,
                            "executingDate": "20260513",
                            "itmRate": 0,
                            "isForce": False
                        },
                        {
                            "id": 226,
                            "type": "Exercise",
                            "status": "Success",
                            "contractId": 2506306537,
                            "symbol": "AAPL",
                            "stkSymbol": "AAPL",
                            "expireDate": "20260501",
                            "strike": "225.0",
                            "callPut": "CALL",
                            "accountId": 600021133765,
                            "requestQuantity": 10.0,
                            "quantity": 10.0,
                            "executingDate": "20260416",
                            "itmRate": 9,
                            "isForce": True
                        }
                    ]
                }
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            result = self.client.get_option_exercise_records(page=1, size=20)
            self.assertIsNotNone(result)
            self.assertEqual(result.page_num, 1)
            self.assertEqual(result.page_size, 20)
            self.assertEqual(result.item_count, 2)
            self.assertEqual(result.page_count, 1)
            self.assertEqual(len(result.items), 2)
            record = result.items[0]
            self.assertEqual(record.id, 302)
            self.assertEqual(record.symbol, "AAPL")
            self.assertEqual(record.stk_symbol, "AAPL")
            self.assertEqual(record.type, "Exercise")
            self.assertEqual(record.status, "New")
            self.assertEqual(record.call_put, "PUT")
            self.assertEqual(record.expire_date, "20260605")
            self.assertEqual(record.account_id, 600021133765)
            self.assertEqual(record.request_quantity, 1.0)
            self.assertEqual(record.is_force, False)
        else:
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
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1779798601559,
                "data": {
                    "pageNum": 1,
                    "pageSize": 4,
                    "itemCount": 4,
                    "pageCount": 1,
                    "items": [
                        {
                            "market": "US",
                            "contractId": 1684414425,
                            "stkSymbol": "AAPL",
                            "symbol": "AAPL",
                            "expireDate": "20260417",
                            "strike": "280.0",
                            "callPut": "PUT",
                            "accountId": 600021133765,
                            "position": 10.0,
                            "availableQuantity": 10.0
                        },
                        {
                            "market": "US",
                            "contractId": 2701923713,
                            "stkSymbol": "AAPL",
                            "symbol": "AAPL",
                            "expireDate": "20260605",
                            "strike": "305.0",
                            "callPut": "PUT",
                            "accountId": 600021133765,
                            "position": 197.0,
                            "availableQuantity": 197.0
                        }
                    ]
                }
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            result = self.client.get_option_exercise_positions(exercise_type="Exercise")
            self.assertIsNotNone(result)
            self.assertEqual(result.page_num, 1)
            self.assertEqual(result.page_size, 4)
            self.assertEqual(result.item_count, 4)
            self.assertEqual(result.page_count, 1)
            self.assertEqual(len(result.items), 2)
            pos = result.items[0]
            self.assertEqual(pos.contract_id, 1684414425)
            self.assertEqual(pos.market, "US")
            self.assertEqual(pos.symbol, "AAPL")
            self.assertEqual(pos.stk_symbol, "AAPL")
            self.assertEqual(pos.call_put, "PUT")
            self.assertEqual(pos.expire_date, "20260417")
            self.assertEqual(pos.account_id, 600021133765)
            self.assertEqual(pos.position, 10.0)
            self.assertEqual(pos.available_quantity, 10.0)

            # Test with OptionExerciseType enum
            result_enum = self.client.get_option_exercise_positions(
                exercise_type=OptionExerciseType.EXERCISE)
            self.assertIsNotNone(result_enum)
            self.assertEqual(result_enum.items[0].symbol, "AAPL")
        else:
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

    def test_cancel_option_exercise(self):
        if self.is_mock:
            mock_data = {
                "code": 0,
                "message": "success",
                "timestamp": 1755200000000,
                "data": None
            }
            web_utils.do_request = MagicMock(return_value=json.dumps(mock_data).encode())

            result = self.client.cancel_option_exercise(exercise_id=9876543210)
            self.assertTrue(result)
        else:
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