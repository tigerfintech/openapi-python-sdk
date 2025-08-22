import json
import logging
import os
import unittest
from unittest.mock import MagicMock

from tigeropen.common.consts import OrderStatus
from tigeropen.common.util import web_utils
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import limit_order
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Order
from tigeropen.trade.trade_client import TradeClient

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class TestTradeClient(unittest.TestCase):

    def setUp(self):
        self.is_mock = True
        current_dir = os.path.dirname(__file__)
        self.client_config = TigerOpenClientConfig(
            props_path=os.path.join(current_dir, ".config/prod_20150899/"))
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
                        "symbol": "NVDA", "market": "US", "contractId": 113, "secType": "STK", "account": "123123",
                        "position": 773, "positionScale": 5, "positionQty": 0.00773, "salableQty": 0.00773,
                        "averageCost": 129.45, "averageCostByAverage": 129.45, "unrealizedPnl": 0.42,
                        "unrealizedPnlByAverage": 0.42, "unrealizedPnlPercent": 0.4177,
                        "unrealizedPnlPercentByAverage": 0.4177, "unrealizedPnlByCostOfCarry": 0.42,
                        "unrealizedPnlPercentByCostOfCarry": 0.4177, "realizedPnl": 0.0, "realizedPnlByAverage": 0.0,
                        "averageCostOfCarry": 129.45, "marketValue": 1.4186, "currency": "USD", "multiplier": 1.0,
                        "status": 0, "identifier": "NVDA", "latestPrice": 183.52, "updateTimestamp": 1755074116660,
                        "comboTypes": [], "comboTypeMap": {}, "mmPercent": 0.0, "mmValue": 0.3547, "todayPnl": 0.0,
                        "todayPnlPercent": 0.002, "categories": [], "lastClosePrice": 183.16},
                        {"symbol": "ROSGQ", "market": "US", "contractId": 7451, "secType": "STK", "account": "123123",
                         "position": 6, "positionScale": 0, "positionQty": 6.0, "salableQty": 6.0,
                         "averageCost": 1.1932, "averageCostByAverage": 1.1932, "unrealizedPnl": -7.16,
                         "unrealizedPnlByAverage": -7.16, "unrealizedPnlPercent": -0.9999,
                         "unrealizedPnlPercentByAverage": -0.9999, "unrealizedPnlByCostOfCarry": -7.16,
                         "unrealizedPnlPercentByCostOfCarry": -0.9999, "realizedPnl": 0.0, "realizedPnlByAverage": 0.0,
                         "averageCostOfCarry": 1.1932, "marketValue": 6.0E-4, "currency": "USD", "multiplier": 1.0,
                         "status": 0, "identifier": "ROSGQ", "latestPrice": 1.0E-4, "updateTimestamp": 1755074116660,
                         "comboTypes": [], "comboTypeMap": {}, "mmPercent": 0.0, "mmValue": 6.0E-4, "todayPnl": 0.0,
                         "todayPnlPercent": 0.0, "categories": [], "lastClosePrice": 1.0E-4}]
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
                    "contractId": 113, "identifier": "NVDA", "symbol": "NVDA", "secType": "STK", "multiplier": 1.0,
                    "lotSize": 1.0, "market": "US", "primaryExchange": "NASDAQ", "currency": "USD",
                    "localSymbol": "NVDA", "tradingClass": "NVDA", "name": "NVIDIA", "status": 1, "tradeable": True,
                    "marginable": True, "shortMargin": 0.35, "shortInitialMargin": 0.35, "shortMaintenanceMargin": 0.3,
                    "longInitialMargin": 0.3, "longMaintenanceMargin": 0.25, "shortFeeRate": 3.75, "shortable": True,
                    "shortableCount": 38061067, "closeOnly": False,
                    "tickSizes": [{"begin": "0", "end": "1", "type": "CLOSED", "tickSize": 1.0E-4},
                                  {"begin": "1", "end": "Infinity", "type": "OPEN", "tickSize": 0.01}], "isEtf": False,
                    "supportOvernightTrading": True, "supportFractionalShare": True
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
            result = self.client.get_contract(symbol="NVDA")
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
                    "items": [{"symbol": "61486", "market": "HK", "secType": "IOPT", "currency": "HKD",
                               "expiry": "20260930", "strike": "114.0", "right": "CALL", "identifier": "61486",
                               "id": 40130901147389952, "externalId": "1755073615.997798", "orderId": 0,
                               "account": "123123", "action": "BUY", "orderType": "LMT", "limitPrice": 0.023,
                               "totalQuantity": 5000, "totalQuantityScale": 0, "filledQuantity": 0,
                               "filledQuantityScale": 0, "filledCashAmount": 0.0, "avgFillPrice": 0.0,
                               "timeInForce": "DAY", "outsideRth": False, "commission": 0.0, "gst": 0.0,
                               "realizedPnl": 0.0, "liquidation": False, "openTime": 1755073677000,
                               "updateTime": 1755073700000, "latestTime": 1755073700000, "name": "SG#MTUANRC2609E.C",
                               "attrDesc": "", "userMark": "", "attrList": [], "algoStrategy": "LMT",
                               "status": "Cancelled", "source": "iOS", "discount": 0, "replaceStatus": "NONE",
                               "cancelStatus": "RECEIVED", "canModify": False, "canCancel": False, "isOpen": True,
                               "orderDiscount": 0, "tradingSessionType": "RTH"},
                              {"symbol": "AAPL", "market": "US", "secType": "MLEG", "currency": "USD",
                               "identifier": "AAPL", "id": 40130857465156608, "externalId": "1755073339.428326",
                               "orderId": 0, "account": "123123", "action": "BUY", "orderType": "LMT",
                               "limitPrice": -2.52, "totalQuantity": 1, "totalQuantityScale": 0, "filledQuantity": 0,
                               "filledQuantityScale": 0, "filledCashAmount": 0.0, "avgFillPrice": 0.0,
                               "timeInForce": "DAY", "outsideRth": False, "commission": 0.0, "gst": 0.0,
                               "realizedPnl": 0.0, "liquidation": False, "openTime": 1755073344000,
                               "updateTime": 1755073361000, "latestTime": 1755073361000,
                               "name": "AAPL VERTICAL 250815 PUT 227.5/PUT 232.5", "attrDesc": "", "userMark": "",
                               "attrList": [], "algoStrategy": "LMT", "status": "Cancelled", "source": "iOS",
                               "discount": 0, "replaceStatus": "NONE", "cancelStatus": "RECEIVED", "canModify": False,
                               "canCancel": False, "isOpen": True, "orderDiscount": 0, "comboType": "VERTICAL",
                               "comboTypeDesc": "Vertical", "legs": [
                                  {"symbol": "AAPL", "expiry": "20250815", "strike": "227.5", "right": "PUT",
                                   "action": "BUY", "secType": "OPT", "ratio": 1, "market": "US", "currency": "USD",
                                   "multiplier": 100, "totalQuantity": 1.0, "filledQuantity": 0.0,
                                   "avgFilledPrice": 0.0, "createdAt": 1755073344483, "updatedAt": 1755073344483},
                                  {"symbol": "AAPL", "expiry": "20250815", "strike": "232.5", "right": "PUT",
                                   "action": "SELL", "secType": "OPT", "ratio": 1, "market": "US", "currency": "USD",
                                   "multiplier": 100, "totalQuantity": 1.0, "filledQuantity": 0.0,
                                   "avgFilledPrice": 0.0, "createdAt": 1755073344482, "updatedAt": 1755073344482}],
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
                "data": {"symbol": "AAPL", "market": "US", "secType": "MLEG", "currency": "USD", "identifier": "AAPL",
                         "id": 40130857465156608, "externalId": "1755073339.428326", "orderId": 0, "account": "123123",
                         "action": "BUY", "orderType": "LMT", "limitPrice": -2.52, "totalQuantity": 1,
                         "totalQuantityScale": 0, "filledQuantity": 0, "filledQuantityScale": 0,
                         "filledCashAmount": 0.0, "avgFillPrice": 0.0, "timeInForce": "DAY", "outsideRth": False,
                         "commission": 0.0, "gst": 0.0, "realizedPnl": 0.0, "liquidation": False,
                         "openTime": 1755073344000, "updateTime": 1755073361000, "latestTime": 1755073361000,
                         "name": "AAPL VERTICAL 250815 PUT 227.5/PUT 232.5", "attrDesc": "", "userMark": "",
                         "attrList": [], "algoStrategy": "LMT", "status": "Cancelled", "source": "iOS", "discount": 0,
                         "replaceStatus": "NONE", "cancelStatus": "RECEIVED", "canModify": False, "canCancel": False,
                         "isOpen": True, "orderDiscount": 0, "comboType": "VERTICAL", "comboTypeDesc": "Vertical",
                         "legs": [{
                             "symbol": "AAPL", "expiry": "20250815", "strike": "227.5", "right": "PUT", "action": "BUY",
                             "secType": "OPT", "ratio": 1, "market": "US", "currency": "USD", "multiplier": 100,
                             "totalQuantity": 1.0, "filledQuantity": 0.0, "avgFilledPrice": 0.0,
                             "createdAt": 1755073344483,
                             "updatedAt": 1755073344483
                         }, {
                             "symbol": "AAPL", "expiry": "20250815", "strike": "232.5", "right": "PUT",
                             "action": "SELL",
                             "secType": "OPT", "ratio": 1, "market": "US", "currency": "USD", "multiplier": 100,
                             "totalQuantity": 1.0, "filledQuantity": 0.0, "avgFilledPrice": 0.0,
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
                        "capability": "RegTMargin", "category": "S", "currency": "USD", "cashBalance": 7198.59,
                        "cashAvailableForTrade": 5717.69, "grossPositionValue": -250.58, "equityWithLoan": 7200.00,
                        "netLiquidation": 6948.00, "initMargin": 500.42, "maintainMargin": 500.35,
                        "overnightMargin": 500.35, "unrealizedPL": 5.85, "unrealizedPLByCostOfCarry": 5.85,
                        "realizedPL": 0.00, "totalTodayPL": 0.00, "excessLiquidation": 6699.65,
                        "overnightLiquidation": 6699.65, "buyingPower": 22870.76, "lockedFunds": 981.89,
                        "leverage": 0.08, "uncollected": 0.00,
                        "currencyAssets": [{
                            "currency": "USD", "cashBalance": 6302.06, "cashAvailableForTrade": 5320.17},
                            {"currency": "HKD", "cashBalance": 5800.29, "cashAvailableForTrade": 5800.29},
                            {"currency": "NZD", "cashBalance": 1.50, "cashAvailableForTrade": 1.50},
                            {"currency": "CNH", "cashBalance": 1123.95, "cashAvailableForTrade": 1123.95},
                            {"currency": "AUD", "cashBalance": 0.00, "cashAvailableForTrade": 0.00},
                            {"currency": "EUR", "cashBalance": 0.12, "cashAvailableForTrade": 0.12}],
                        "consolidatedSegTypes": ["SEC", "FUND"]
                    }, {
                        "capability": "RegTMargin", "category": "C", "currency": "USD", "cashBalance": 2302.46,
                        "cashAvailableForTrade": 2302.46, "grossPositionValue": 0.00, "equityWithLoan": 2302.46,
                        "netLiquidation": 2302.46, "initMargin": 0.00, "maintainMargin": 0.00, "overnightMargin": 0.00,
                        "unrealizedPL": 0.00, "unrealizedPLByCostOfCarry": 0.00, "realizedPL": 2.46,
                        "totalTodayPL": 2.46, "excessLiquidation": 2302.46, "overnightLiquidation": 2302.46,
                        "buyingPower": 0.00, "lockedFunds": 0.00, "leverage": 0.00, "uncollected": 0.00,
                        "currencyAssets": [{
                            "currency": "USD", "cashBalance": 2302.46, "cashAvailableForTrade": 2302.46},
                            {"currency": "HKD", "cashBalance": 0.00, "cashAvailableForTrade": 0.00},
                            {"currency": "CNH", "cashBalance": 0.00, "cashAvailableForTrade": 0.00}],
                        "consolidatedSegTypes": ["FUT"]
                    }, {
                        "capability": "RegTMargin", "category": "F", "currency": "USD", "cashBalance": 0.00,
                        "cashAvailableForTrade": 5717.69, "grossPositionValue": 0.00, "equityWithLoan": 7200.00,
                        "netLiquidation": 0.00, "initMargin": 500.42, "maintainMargin": 500.35,
                        "overnightMargin": 500.35, "unrealizedPL": 0.00, "unrealizedPLByCostOfCarry": 0.00,
                        "realizedPL": 0.78, "totalTodayPL": 0.00, "excessLiquidation": 6699.65,
                        "overnightLiquidation": 6699.65, "buyingPower": 22870.76, "lockedFunds": 981.89,
                        "leverage": 0.08, "uncollected": 0.00,
                        "currencyAssets": [{
                            "currency": "USD",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00
                        }, {
                            "currency": "HKD",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00
                        }, {
                            "currency": "CNH",
                            "cashBalance": 0.00,
                            "cashAvailableForTrade": 0.00
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

            # Check HKD assets
            hkd_asset = stock_segment.currency_assets['HKD']
            self.assertEqual(hkd_asset.currency, 'HKD')
            self.assertEqual(hkd_asset.cash_balance, 5800.29)
            self.assertEqual(hkd_asset.cash_available_for_trade, 5800.29)

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
                        "symbol": "AAPL", "market": "US", "secType": "STK", "currency": "USD", "identifier": "AAPL",
                        "id": 40132638459956224, "externalId": "1169", "orderId": 1169, "account": "123123",
                        "action": "BUY", "orderType": "LMT", "limitPrice": 90.5, "totalQuantity": 2,
                        "totalQuantityScale": 0, "filledQuantity": 0, "filledQuantityScale": 0, "filledCashAmount": 0.0,
                        "avgFillPrice": 0.0, "timeInForce": "DAY", "outsideRth": True, "commission": 0.0, "gst": 0.0,
                        "realizedPnl": 0.0, "remark": "", "liquidation": False, "openTime": 1755086932000,
                        "updateTime": 1755086932000, "latestTime": 1755086932000, "name": "Apple",
                        "latestPrice": 230.14, "attrDesc": "", "userMark": "", "attrList": [], "algoStrategy": "LMT",
                        "status": "Initial", "source": "OpenApi", "discount": 0, "replaceStatus": "NONE",
                        "cancelStatus": "NONE", "canModify": True, "canCancel": True, "isOpen": True,
                        "orderDiscount": 0, "tradingSessionType": "PRE_RTH_POST"
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

            mock_order = Order(
                account="123123",
                contract=mock_contract,
                action="BUY",
                order_type="LMT",
                quantity=2
            )
            mock_order.id = 40139406481165312
            mock_order.order_id = 1169
            mock_order.limit_price = 90.5
            mock_order.time_in_force = "DAY"

            # Test modifying price only
            mock_result_price_only = self.client.modify_order(
                order=mock_order,
                limit_price=100.5
            )
            self.assertIsNotNone(mock_result_price_only)
            self.assertEqual(mock_result_price_only, 40139406481165312)

            # Test modifying multiple parameters
            mock_result_multiple = self.client.modify_order(
                order=mock_order,
                quantity=5,
                limit_price=105.5,
                time_in_force="GTC",
                outside_rth=True
            )
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
