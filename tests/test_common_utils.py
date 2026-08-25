import base64
import os
import tempfile
import unittest
from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tigeropen.common.consts import Market, OrderStatus, OrderType, PriceType
from tigeropen.common.util.account_util import AccountUtil
from tigeropen.common.util.common_utils import date_str_to_timestamp, get_enum_value, get_tz_by_market, has_value
from tigeropen.common.util.contract_utils import (
    cash_contract,
    cc_contract,
    extract_option_info,
    fund_contract,
    future_contract,
    future_option_contract,
    get_option_identifier,
    iopt_contract_by_symbol,
    is_hk_option_underlying_symbol,
    option_contract,
    option_contract_by_symbol,
    stock_contract,
    war_contract_by_symbol,
)
from tigeropen.common.util.order_utils import (
    algo_order,
    algo_order_params,
    auction_limit_order,
    auction_market_order,
    combo_order,
    contract_leg,
    get_order_status,
    iceberg_order,
    limit_order,
    limit_order_by_amount,
    limit_order_with_legs,
    market_order,
    market_order_by_amount,
    oca_order,
    order_leg,
    stop_limit_order,
    stop_order,
    trail_order,
)
from tigeropen.common.util.signature_utils import (
    fill_private_key_marker,
    fill_public_key_marker,
    get_sign_content,
    read_private_key,
    read_public_key,
    sign_with_rsa,
    verify_with_rsa,
)
from tigeropen.common.util.string_utils import (
    add_start_end,
    camel_to_underline,
    camel_to_underline_obj,
    underline_to_camel,
)

import pytest


# 纯单测：永远不碰真实接口，contract / integ job 会跳过
pytestmark = pytest.mark.unit


class TestCommonUtils(unittest.TestCase):

    def test_mapping_enum_date_and_timezone_helpers(self):
        self.assertFalse(has_value(None, 'key'))
        self.assertFalse(has_value({}, 'key'))
        self.assertFalse(has_value({'key': 0}, 'key'))
        self.assertTrue(has_value({'key': 1}, 'key'))

        self.assertEqual(get_enum_value(Market.HK), Market.HK.value)
        self.assertEqual(get_enum_value('HK'), 'HK')
        self.assertEqual(get_enum_value(Market.HK, Market), Market.HK.value)
        self.assertEqual(get_enum_value('HK', Market), 'HK')

        timestamp = date_str_to_timestamp('2024-01-02 12:00:00', 'UTC')
        self.assertEqual(timestamp, 1704196800000)
        self.assertEqual(date_str_to_timestamp('invalid', 'UTC'), 'invalid')
        self.assertEqual(date_str_to_timestamp(123, 'UTC'), 123)
        self.assertEqual(get_tz_by_market(Market.HK).zone, 'Asia/Hong_Kong')
        self.assertEqual(get_tz_by_market(Market.CN).zone, 'Asia/Shanghai')
        self.assertEqual(get_tz_by_market(Market.US).zone, 'US/Eastern')

    def test_string_and_account_helpers(self):
        self.assertEqual(add_start_end('key', '<', '>'), '<key>')
        self.assertEqual(add_start_end('<key>', '<', '>'), '<key>')
        self.assertEqual(camel_to_underline('latestPrice2D'), 'latest_price2_d')
        self.assertEqual(underline_to_camel('latest_price'), 'latestPrice')
        self.assertEqual(
            camel_to_underline_obj({'outerKey': [{'innerKey': 1}, 'raw']}),
            {'outer_key': [{'inner_key': 1}, 'raw']},
        )
        self.assertTrue(AccountUtil.is_paper_account('12345678901234567'))
        self.assertTrue(AccountUtil.is_paper_account(12345678901234567))
        self.assertFalse(AccountUtil.is_paper_account('DU123456'))
        self.assertFalse(AccountUtil.is_paper_account(None))


class TestContractUtils(unittest.TestCase):

    def test_contract_factories(self):
        stock = stock_contract('AAPL', 'USD', exchange='NASDAQ', contract_id=1)
        self.assertEqual((stock.symbol, stock.sec_type, stock.exchange, stock.contract_id),
                         ('AAPL', 'STK', 'NASDAQ', 1))

        option = option_contract_by_symbol('AAPL', '20270115', 200, 'CALL', 'USD', contract_id=2)
        self.assertEqual((option.sec_type, option.expiry, option.strike, option.put_call),
                         ('OPT', '20270115', 200, 'CALL'))
        parsed = option_contract('AAPL  270115P00200000')
        self.assertEqual((parsed.symbol, parsed.expiry, parsed.strike, parsed.put_call),
                         ('AAPL', '20270115', 200.0, 'PUT'))

        future = future_contract('ES', 'USD', exchange='CME', contract_month='202703')
        self.assertEqual((future.sec_type, future.exchange, future.contract_month), ('FUT', 'CME', '202703'))
        self.assertEqual(future_option_contract('ES', 'USD', '20270319', 5000, 'CALL').sec_type, 'FOP')
        self.assertEqual(cash_contract('USD.HKD', 'HKD').sec_type, 'CASH')
        self.assertEqual(fund_contract('FUND001').sec_type, 'FUND')
        self.assertEqual(cc_contract('BTC').sec_type, 'CC')
        self.assertEqual(war_contract_by_symbol('00700', '20270101', 500, 'CALL', '12345').sec_type, 'WAR')
        self.assertEqual(iopt_contract_by_symbol('00700', '20270101', 500, 'CALL', '54321').sec_type, 'IOPT')

    def test_option_identifier_helpers(self):
        self.assertEqual(
            extract_option_info('BRK.B 270115C00400000'),
            ('BRK.B', '2027-01-15', 'CALL', 400.0),
        )
        self.assertEqual(extract_option_info('invalid'), (None, None, None, None))
        self.assertIsNone(extract_option_info(None))
        self.assertEqual(get_option_identifier('AAPL', '20270115', 'CALL', '200'), 'AAPL  270115C00200000')
        timestamp = int(datetime(2027, 1, 15).timestamp() * 1000)
        self.assertEqual(get_option_identifier('AAPL', timestamp, 'P', 200), 'AAPL  270115P00200000')
        self.assertTrue(is_hk_option_underlying_symbol('00700.HK'))
        self.assertFalse(is_hk_option_underlying_symbol('AAPL'))


class TestOrderUtils(unittest.TestCase):

    def setUp(self):
        self.contract = stock_contract('AAPL', 'USD')

    def test_basic_order_factories(self):
        orders = [
            (market_order('A', self.contract, 'BUY', 2), 'MKT'),
            (limit_order('A', self.contract, 'BUY', 2, 100), 'LMT'),
            (stop_order('A', self.contract, 'SELL', 2, 90), 'STP'),
            (stop_limit_order('A', self.contract, 'SELL', 2, 89, 90), 'STP_LMT'),
            (trail_order('A', self.contract, 'SELL', 2, trailing_percent=5), 'TRAIL'),
            (auction_limit_order('A', self.contract, 'BUY', 2, 100, 'OPG'), 'AL'),
            (auction_market_order('A', self.contract, 'BUY', 2, 'OPG'), 'AM'),
        ]
        for order, order_type in orders:
            with self.subTest(order_type=order_type):
                self.assertEqual(order.order_type, order_type)
                self.assertEqual(order.account, 'A')
                self.assertIs(order.contract, self.contract)

        self.assertEqual(market_order_by_amount('A', self.contract, 'BUY', 1000).total_cash_amount, 1000)
        by_amount = limit_order_by_amount('A', self.contract, 'BUY', 1000, 99)
        self.assertEqual((by_amount.total_cash_amount, by_amount.limit_price), (1000, 99))
        self.assertTrue(orders[5][0].outside_rth)
        self.assertEqual(orders[3][0].aux_price, 90)

    def test_advanced_order_factories(self):
        leg = order_leg(OrderType.LMT.value, price=110, quantity=1)
        self.assertEqual((leg.limit_price, leg.quantity), (110, 1))
        attached = limit_order_with_legs('A', self.contract, 'BUY', 1, 100, [leg])
        self.assertEqual(attached.order_legs, [leg])
        with self.assertRaisesRegex(Exception, '2 order legs at most'):
            limit_order_with_legs('A', self.contract, 'BUY', 1, 100, [leg, leg, leg])

        iceberg = iceberg_order('A', self.contract, 'BUY', 100, 99, 10, price_type=PriceType.BID_PRICE)
        self.assertEqual((iceberg.order_type, iceberg.display_size, iceberg.price_type),
                         ('ICEBERG', 10, 'BID_PRICE'))
        string_price_type = iceberg_order('A', self.contract, 'BUY', 100, 99, 10, price_type='ASK_PRICE')
        self.assertEqual(string_price_type.price_type, 'ASK_PRICE')

        params = algo_order_params(1, 2, True, False, 0.2)
        algo = algo_order('A', self.contract, 'BUY', 10, 'VWAP', params, 100)
        self.assertEqual((algo.order_type, algo.algo_params, algo.outside_rth), ('VWAP', params, False))

        contract_legs = [contract_leg('AAPL', 'OPT', '20270115', 200, 'CALL', 'BUY')]
        combo = combo_order('A', contract_legs, 'CUSTOM', 'BUY', 1, limit_price=2.5)
        self.assertEqual((combo.contract_legs, combo.combo_type, combo.limit_price),
                         (contract_legs, 'CUSTOM', 2.5))
        oca = oca_order('A', self.contract, 'SELL', [leg], quantity=1)
        self.assertEqual((oca.order_type, oca.order_legs), ('OCA', [leg]))

    def test_order_status_mapping(self):
        cases = {
            'Initial': OrderStatus.NEW,
            'Submitted': OrderStatus.HELD,
            'PendingCancel': OrderStatus.PENDING_CANCEL,
            'Cancelled': OrderStatus.CANCELLED,
            'Filled': OrderStatus.FILLED,
            'Inactive': OrderStatus.REJECTED,
            'Invalid': OrderStatus.EXPIRED,
            'unknown': OrderStatus.PENDING_NEW,
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(get_order_status(value), expected)
        self.assertEqual(get_order_status('Submitted', filled_quantity=1), OrderStatus.PARTIALLY_FILLED)


class TestSignatureUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
        private_der = cls.private_key.private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
        public_pem = cls.private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        cls.private_key_string = base64.b64encode(private_der).decode()
        cls.public_key_string = public_pem.replace('-----BEGIN PUBLIC KEY-----\n', '').replace(
            '\n-----END PUBLIC KEY-----\n', '')

    def test_sign_content_and_markers(self):
        self.assertEqual(get_sign_content({'b': {'x': 1}, 'a': 'value'}), 'a=value&b={"x": 1}')
        self.assertTrue(fill_private_key_marker(self.private_key_string).startswith('-----BEGIN RSA PRIVATE KEY-----'))
        self.assertTrue(fill_public_key_marker(self.public_key_string).endswith('-----END PUBLIC KEY-----'))

    def test_sign_verify_and_key_files(self):
        message = b'account=123&symbol=AAPL'
        signature = sign_with_rsa(self.private_key_string, message.decode(), 'utf-8')
        self.assertTrue(verify_with_rsa(self.public_key_string, message, signature))
        with self.assertRaises(Exception):
            verify_with_rsa(self.public_key_string, b'tampered', signature)

        private_pem = self.private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ).decode()
        public_pem = fill_public_key_marker(self.public_key_string)
        with tempfile.TemporaryDirectory() as directory:
            private_path = os.path.join(directory, 'private.pem')
            public_path = os.path.join(directory, 'public.pem')
            with open(private_path, 'w') as private_file:
                private_file.write(private_pem)
            with open(public_path, 'w') as public_file:
                public_file.write(public_pem)
            self.assertEqual(read_private_key(private_path).replace('\n', ''), self.private_key_string)
            self.assertEqual(
                read_public_key(public_path).replace('\n', ''),
                self.public_key_string.replace('\n', ''),
            )


if __name__ == '__main__':
    unittest.main()
