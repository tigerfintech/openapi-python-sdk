import unittest

from tigeropen.common.consts import OrderType
from tigeropen.common.consts.filter_fields import MultiTagField
from tigeropen.common.util.contract_utils import cc_contract, option_contract_by_symbol, stock_contract
from tigeropen.common.util.order_utils import algo_order_params, order_leg
from tigeropen.quote.domain.filter import OptionFilter
from tigeropen.quote.request.model import (
    DepthQuoteParams,
    FutureQuoteParams,
    FutureTradingTimeParams,
    MarketScannerParams,
    MultipleQuoteParams,
    OptionAnalysisParams,
    OptionChainParams,
    SingleOptionQuoteParams,
    SingleQuoteParams,
    StockBrokerParams,
    SymbolsParams,
    TradingCalendarParams,
    WarrantFilterParams,
)
from tigeropen.trade.domain.contract import ContractLeg
from tigeropen.trade.domain.transfer import TransferItem
from tigeropen.trade.request.model import (
    AccountsParams,
    AggregateAssetParams,
    AnalyticsAssetParams,
    AssetParams,
    CancelOrderParams,
    ContractParams,
    EstimateTradableQuantityModel,
    ForexTradeOrderParams,
    FundDetailsParams,
    FundingHistoryParams,
    OptionExerciseCancelParams,
    OptionExerciseCheckParams,
    OptionExercisePageParams,
    OptionExercisePositionParams,
    OptionExerciseSubmitParams,
    OrderParams,
    OrdersParams,
    PlaceModifyOrderParams,
    PositionParams,
    PositionTransferDetailParams,
    PositionTransferParams,
    PositionTransferRecordsParams,
    SegmentFundParams,
    TransactionsParams,
)

import pytest


# 纯单测：永远不碰真实接口，contract / integ job 会跳过
pytestmark = pytest.mark.unit


class TestQuoteRequestModels(unittest.TestCase):

    def test_single_quote_serializes_all_fields_and_false_values(self):
        params = SingleQuoteParams()
        values = {
            'lang': 'en_US',
            'version': '3.0',
            'market': 'US',
            'sec_type': 'OPT',
            'symbol': 'AAPL',
            'put_call': 'CALL',
            'expiry': '20270115',
            'strike': 200.0,
            'include_hour_trading': False,
            'include_ask_bid': False,
            'right': 'PUT',
            'period': 'day',
            'begin_time': 1000,
            'end_time': 2000,
            'begin_index': 0,
            'end_index': 0,
            'limit': 50,
        }
        for field, value in values.items():
            setattr(params, field, value)
            self.assertEqual(getattr(params, field), value)

        self.assertEqual(params.to_openapi_dict(), {
            'lang': 'en_US',
            'version': '3.0',
            'market': 'US',
            'sec_type': 'OPT',
            'symbol': 'AAPL',
            'right': 'PUT',
            'expiry': '20270115',
            'strike': 200.0,
            'include_hour_trading': False,
            'include_ask_bid': False,
            'period': 'day',
            'begin_time': 1000,
            'end_time': 2000,
            'begin_index': 0,
            'end_index': 0,
            'limit': 50,
        })

    def test_warrant_filter_builder_serializes_ranges_and_sets(self):
        params = WarrantFilterParams()
        params.lang = 'en_US'
        params.symbol = '00700'
        params.page = 2
        params.page_size = 50
        params.sort_field_name = 'effective_leverage'
        params.sort_dir = 'DESC'
        params.set_issuer_name('GS')
        params.set_expire_ym('2027-06')
        params.set_state(2)
        params.add_warrant_type(1)
        params.add_warrant_type(3)
        params.add_in_out_price(-1)
        params.add_lot_size(100)
        params.add_entitlement_ratio(10.0)
        params.set_strike_range(100.0, 600.0)
        params.set_effective_leverage_range(1.0, 10.0)
        params.set_leverage_ratio_range(2.0, 20.0)
        params.set_call_price_range(0.1, 5.0)
        params.set_volume_range(1000, 100000)
        params.set_premium_range(-0.2, 0.3)
        params.set_outstanding_ratio_range(0.0, 0.8)
        params.set_implied_volatility_range(10, 80)

        result = params.to_openapi_dict()
        self.assertEqual(result['sort_field_name'], 'effectiveLeverage')
        self.assertEqual(result['issuer_name'], 'GS')
        self.assertEqual(result['expire_ym'], '2027-06')
        self.assertEqual(result['state'], 2)
        self.assertEqual(set(result['warrant_type']), {1, 3})
        self.assertEqual(set(result['in_out_price']), {-1})
        self.assertEqual(set(result['lot_size']), {100})
        self.assertEqual(set(result['entitlement_ratio']), {10.0})
        self.assertEqual(result['strike'], {'min': 100.0, 'max': 600.0})
        self.assertEqual(result['effective_leverage'], {'min': 1.0, 'max': 10.0})
        self.assertEqual(result['leverage_ratio'], {'min': 2.0, 'max': 20.0})
        self.assertEqual(result['call_price'], {'min': 0.1, 'max': 5.0})
        self.assertEqual(result['volume'], {'min': 1000, 'max': 100000})
        self.assertEqual(result['premium'], {'min': -0.2, 'max': 0.3})
        self.assertEqual(result['outstanding_ratio'], {'min': 0.0, 'max': 0.8})
        self.assertEqual(result['implied_volatility'], {'min': 10, 'max': 80})

    def test_warrant_filter_properties_and_range_compatibility(self):
        params = WarrantFilterParams()
        values = {
            'warrant_type': {2},
            'issuer_name': 'UBS',
            'expire_ym': '2027-12',
            'state': 3,
            'in_out_price': {1},
            'lot_size': {500},
            'entitlement_ratio': {5.0},
            'strike': [100.0, 200.0],
            'effective_leverage': (1.0, 2.0),
            'leverage_ratio': (2.0, 3.0),
            'call_price': (0.2, 0.5),
            'volume': (10, 20),
            'premium': (-0.1, 0.1),
            'outstanding_ratio': (0.2, 0.4),
            'implied_volatility': (20, 40),
        }
        for field, value in values.items():
            setattr(params, field, value)
            self.assertEqual(getattr(params, field), value)
        self.assertEqual(params.convert_range_param([1, 2]), {'min': 1, 'max': 2})
        self.assertEqual(params.convert_range_param((1, 2, 3)), (1, 2, 3))
        self.assertEqual(params.convert_range_param('unchanged'), 'unchanged')

    def test_remaining_quote_model_branches(self):
        symbols = SymbolsParams()
        symbols.include_otc = True
        self.assertTrue(symbols.to_openapi_dict()['include_otc'])

        multiple = MultipleQuoteParams()
        multiple.symbols = ['AAPL']
        multiple.include_hour_trading = False
        multiple.include_ask_bid = False
        multiple.limit = 0
        multiple.begin_index = 0
        multiple.end_index = 0
        multiple.page_token = 'next'
        multiple.trade_session = 'OverNight'
        multiple.with_fundamental = True
        result = multiple.to_openapi_dict()
        self.assertEqual(result['limit'], 0)
        self.assertEqual(result['begin_index'], 0)
        self.assertEqual(result['end_index'], 0)
        self.assertTrue(result['with_fundamental'])

        option_quote = SingleOptionQuoteParams()
        option_quote.sort_dir = 'ASC'
        self.assertEqual(option_quote.to_openapi_dict()['sort_dir'], 'ASC')

        future_time = FutureTradingTimeParams()
        future_time.trading_date = '2027-01-15'
        self.assertEqual(future_time.to_openapi_dict()['trading_date'], '2027-01-15')

        future_quote = FutureQuoteParams()
        future_quote.begin_index = 0
        future_quote.end_index = 0
        future_quote.page_token = 'next'
        self.assertEqual(future_quote.to_openapi_dict()['page_token'], 'next')

        depth = DepthQuoteParams()
        depth.trade_session = 'Regular'
        self.assertEqual(depth.to_openapi_dict()['trade_session'], 'Regular')

        chain = OptionChainParams()
        chain.option_filter = OptionFilter(implied_volatility_min=0.1, in_the_money=True)
        chain.return_greek_value = False
        chain_result = chain.to_openapi_dict()
        self.assertFalse(chain_result['return_greek_value'])
        self.assertEqual(chain_result['option_filter']['implied_volatility']['min'], 0.1)

        calendar = TradingCalendarParams()
        calendar.begin_date = '2027-01-01'
        calendar.end_date = '2027-01-31'
        self.assertEqual(calendar.to_openapi_dict()['end_date'], '2027-01-31')

        scanner = MarketScannerParams()
        scanner.accumulate_filter_list = [{'field_name': 'changeRate'}]
        scanner.financial_filter_list = [{'field_name': 'pe'}]
        scanner.multi_tags_filter_list = [{'field_name': 'isOTC'}]
        scanner.cursor_id = 'cursor'
        scanner.multi_tags_fields = [MultiTagField.StockCode]
        scanner_result = scanner.to_openapi_dict()
        self.assertEqual(scanner_result['cursor_id'], 'cursor')
        self.assertEqual(scanner_result['multi_tag_field_list'], ['MultiTagField_StockCode'])

        broker = StockBrokerParams()
        broker.sec_type = 'STK'
        self.assertEqual(broker.to_openapi_dict()['sec_type'], 'STK')

        analysis = OptionAnalysisParams()
        analysis.symbols = [{'symbol': 'AAPL', 'period': '52week'}]
        analysis.market = 'US'
        self.assertEqual(analysis.symbols[0]['symbol'], 'AAPL')
        self.assertEqual(analysis.market, 'US')


class TestTradeRequestModels(unittest.TestCase):

    def assert_model(self, cls, values, expected=None):
        model = cls()
        for field, value in values.items():
            setattr(model, field, value)
            self.assertEqual(getattr(model, field), value)
        result = model.to_openapi_dict()
        for field, value in (expected or values).items():
            self.assertEqual(result[field], value, '{}.{}'.format(cls.__name__, field))
        return result

    def test_account_position_contract_and_order_models(self):
        self.assert_model(AccountsParams, {'account': 'A', 'secret_key': 'K'})
        asset = self.assert_model(AssetParams, {
            'account': 'A', 'secret_key': 'K', 'segment': True, 'market_value': True,
            'sub_accounts': ['S'], 'base_currency': 'USD', 'consolidated': False,
        })
        self.assertFalse(asset['consolidated'])
        self.assert_model(AggregateAssetParams, {
            'account': 'A', 'secret_key': 'K', 'seg_type': 'SEC', 'base_currency': 'USD',
        })
        self.assert_model(PositionParams, {
            'account': 'A', 'secret_key': 'K', 'symbol': 'AAPL', 'sec_type': 'OPT',
            'currency': 'USD', 'market': 'US', 'sub_accounts': ['S'], 'expiry': '20270115',
            'strike': 200, 'right': 'CALL', 'asset_quote_type': 'USD',
        })
        self.assert_model(ContractParams, {
            'account': 'A', 'secret_key': 'K', 'symbol': 'AAPL', 'symbols': ['AAPL'],
            'sec_type': 'OPT', 'currency': 'USD', 'exchange': 'SMART', 'expiry': '20270115',
            'strike': 200, 'right': 'CALL',
        })
        order = self.assert_model(OrderParams, {
            'account': 'A', 'secret_key': 'K', 'order_id': 1, 'id': 2,
            'is_brief': True, 'show_charges': False,
        })
        self.assertFalse(order['show_charges'])
        self.assert_model(OrdersParams, {
            'account': 'A', 'secret_key': 'K', 'market': 'US', 'sec_type': 'STK', 'seg_type': 'SEC',
            'symbol': 'AAPL', 'start_date': '2027-01-01', 'end_date': '2027-01-31', 'limit': 10,
            'is_brief': True, 'states': ['Filled'], 'parent_id': 3, 'sort_by': 'LATEST_CREATED',
            'show_charges': False, 'page_token': 'next',
        })
        self.assert_model(TransactionsParams, {
            'account': 'A', 'secret_key': 'K', 'order_id': 1, 'sec_type': 'OPT', 'symbol': 'AAPL',
            'expiry': '20270115', 'strike': 200, 'right': 'CALL', 'start_date': '2027-01-01',
            'end_date': '2027-01-31', 'since_date': '2027-01-01', 'to_date': '2027-01-31',
            'limit': 10, 'page_token': 'next',
        })
        self.assert_model(CancelOrderParams, {'account': 'A', 'secret_key': 'K', 'order_id': 1, 'id': 2})

    def test_account_service_models(self):
        self.assert_model(AnalyticsAssetParams, {
            'account': 'A', 'sub_account': 'S', 'secret_key': 'K', 'seg_type': 'SEC',
            'currency': 'USD', 'sub_accounts': ['S'], 'start_date': '2027-01-01', 'end_date': '2027-01-31',
        })
        self.assert_model(SegmentFundParams, {
            'id': 1, 'account': 'A', 'secret_key': 'K', 'from_segment': 'S', 'to_segment': 'C',
            'currency': 'USD', 'amount': 100, 'limit': 10,
        })
        self.assert_model(ForexTradeOrderParams, {
            'account': 'A', 'secret_key': 'K', 'source_currency': 'USD', 'source_amount': 100,
            'target_currency': 'HKD', 'seg_type': 'SEC', 'external_id': 'E', 'time_in_force': 'DAY',
        })
        self.assert_model(FundingHistoryParams, {'account': 'A', 'secret_key': 'K', 'seg_type': 'SEC'})
        fund = self.assert_model(FundDetailsParams, {
            'account': 'A', 'secret_key': 'K', 'seg_types': ['SEC'], 'fund_type': 'DEPOSIT',
            'currency': 'USD', 'start_date': '2027-01-01', 'end_date': '2027-01-31',
            'start': 0, 'limit': 10,
        })
        self.assertEqual(fund['start'], 0)

        estimate = EstimateTradableQuantityModel()
        estimate_values = {
            'account': 'A', 'secret_key': 'K',
            'contract': option_contract_by_symbol('AAPL', '20270115', 200, 'CALL', 'USD'),
            'seg_type': 'SEC', 'action': 'BUY', 'order_type': 'STP_LMT',
            'limit_price': 101, 'stop_price': 100,
        }
        for field, value in estimate_values.items():
            setattr(estimate, field, value)
            self.assertEqual(getattr(estimate, field), value)
        estimate_result = estimate.to_openapi_dict()
        self.assertEqual(estimate_result['right'], 'CALL')
        self.assertEqual(estimate_result['stop_price'], 100)

    def test_place_modify_order_full_bracket_combo_and_cc(self):
        params = PlaceModifyOrderParams()
        params.account = 'A'
        params.secret_key = 'K'
        params.id = 1
        params.order_id = 2
        params.contract = option_contract_by_symbol('AAPL', '20270115', 200, 'CALL', 'USD', local_symbol='OPT')
        params.action = 'BUY'
        params.order_type = 'LMT'
        params.quantity = 0
        params.quantity_scale = 0
        params.limit_price = 0
        params.aux_price = 0
        params.trail_stop_price = 0
        params.trailing_percent = 0
        params.percent_offset = 0
        params.time_in_force = 'GTC'
        params.outside_rth = False
        params.adjust_limit = False
        params.user_mark = ''
        params.expire_time = 0
        params.total_cash_amount = 0
        params.algo_params = algo_order_params(1, 2, True, False, 0.2)
        params.combo_type = 'VERTICAL'
        params.trading_session_type = 'RTH'
        params.display_size = 0
        params.min_display_size = 0
        params.check_intervals = 0
        params.price_type = 'LIMIT_PRICE'
        params.start_time = 0
        params.end_time = 0
        params.order_legs = [
            order_leg('PROFIT', price=220, outside_rth=False),
            order_leg('LOSS', price=180, outside_rth=False, limit_price=179,
                      trailing_percent=2, trailing_amount=3),
        ]
        params.contract_legs = [ContractLeg('AAPL', 'OPT', '20270115', 200, 'CALL', 'BUY', 1)]
        result = params.to_openapi_dict()
        self.assertEqual(result['sec_type'], 'MLEG')
        self.assertEqual(result['contract_legs'][0]['right'], 'CALL')
        self.assertEqual(result['attach_type'], 'BRACKETS')
        self.assertEqual(result['profit_taker_price'], 220)
        self.assertEqual(result['stop_loss_limit_price'], 179)
        self.assertEqual(result['stop_loss_trailing_amount'], 3)
        self.assertEqual(result['total_quantity'], 0)
        self.assertFalse(result['outside_rth'])
        self.assertEqual(result['display_size'], 0)
        self.assertEqual(len(result['algo_params']), 5)

        cc = PlaceModifyOrderParams()
        cc.contract = cc_contract('BTC')
        cc.time_in_force = 'DAY'
        self.assertIsNone(cc.to_openapi_dict()['time_in_force'])

    def test_place_modify_order_oca_variants(self):
        params = PlaceModifyOrderParams()
        params.account = 'A'
        params.secret_key = 'K'
        params.contract = stock_contract('AAPL', 'USD')
        params.action = 'SELL'
        params.order_type = OrderType.OCA.value
        params.quantity = 10
        params.order_legs = [
            order_leg('LMT', price=110),
            order_leg('STP', price=90, quantity=5, outside_rth=False),
            order_leg('STP_LMT', price=85, limit_price=84, quantity=6, outside_rth=True),
        ]
        result = params.to_openapi_dict()
        self.assertNotIn('order_type', result)
        self.assertNotIn('action', result)
        self.assertNotIn('total_quantity', result)
        self.assertEqual(len(result['oca_orders']), 3)
        self.assertEqual(result['oca_orders'][0]['limit_price'], 110)
        self.assertEqual(result['oca_orders'][0]['total_quantity'], 10)
        self.assertEqual(result['oca_orders'][1]['aux_price'], 90)
        self.assertFalse(result['oca_orders'][1]['outside_rth'])
        self.assertEqual(result['oca_orders'][2]['limit_price'], 84)

    def test_position_transfer_and_option_exercise_models(self):
        transfer = PositionTransferParams()
        transfer.from_account = 'A1'
        transfer.to_account = 'A2'
        transfer.market = 'US'
        transfer.secret_key = 'K'
        transfer.transfers = [
            TransferItem('AAPL', 0, '20270115', 200, put_call='CALL', sec_type='OPT'),
            TransferItem('MSFT', 2),
        ]
        result = transfer.to_openapi_dict()
        self.assertEqual(result['transfers'][0]['quantity'], 0)
        self.assertEqual(result['transfers'][0]['right'], 'CALL')
        self.assertNotIn('expiry', result['transfers'][1])

        records = PositionTransferRecordsParams()
        for field, value in {
            'account_id': 'A1', 'since_date': '2027-01-01', 'to_date': '2027-01-31',
            'status': 'SUCCESS', 'market': 'US', 'symbol': 'AAPL', 'secret_key': 'K',
        }.items():
            setattr(records, field, value)
        self.assertEqual(records.to_openapi_dict()['status'], 'SUCCESS')

        detail = PositionTransferDetailParams()
        detail.id = 'T1'
        detail.account_id = 'A1'
        detail.secret_key = 'K'
        self.assertEqual(detail.to_openapi_dict()['id'], 'T1')

        submit_values = {
            'account': 'A', 'contract_id': 0, 'type': 'Exercise', 'quantity': 0,
            'executing_date': '2027-01-15', 'is_force': False, 'itm_rate': 0, 'secret_key': 'K',
        }
        for cls in (OptionExerciseSubmitParams, OptionExerciseCheckParams):
            model = cls()
            for field, value in submit_values.items():
                setattr(model, field, value)
                self.assertEqual(getattr(model, field), value)
            serialized = model.to_openapi_dict()
            self.assertEqual(serialized['contract_id'], 0)
            self.assertEqual(serialized['quantity'], 0)
            self.assertFalse(serialized['is_force'])
            self.assertEqual(serialized['itm_rate'], 0)

        page = OptionExercisePageParams()
        for field, value in {
            'account': 'A', 'page': 0, 'size': 0, 'status': 'New', 'type': 'Exercise',
            'symbol': 'AAPL', 'order_by': 'createdAt', 'secret_key': 'K',
        }.items():
            setattr(page, field, value)
            self.assertEqual(getattr(page, field), value)
        self.assertEqual(page.to_openapi_dict()['page'], 0)

        position = OptionExercisePositionParams()
        position.account = 'A'
        position.type = 'Exercise'
        position.secret_key = 'K'
        self.assertEqual(position.to_openapi_dict()['type'], 'Exercise')

        cancel = OptionExerciseCancelParams()
        cancel.account = 'A'
        cancel.id = 0
        cancel.secret_key = 'K'
        self.assertEqual(cancel.to_openapi_dict()['id'], 0)


if __name__ == '__main__':
    unittest.main()
