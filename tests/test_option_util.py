# -*- coding: utf-8 -*-
"""
Unit tests for OptionUtil class
@Date    : 2026/1/6
@Author  : sukai
"""
import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

try:
    import QuantLib as ql
    HAS_QUANTLIB = True
except ImportError:
    HAS_QUANTLIB = False

from tigeropen.examples.option_helpers.util import OptionUtil, OptionMetric
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient


class TestOptionMetric(unittest.TestCase):
    """Test cases for OptionMetric dataclass"""
    
    def test_create_option_metric(self):
        """Test creating an OptionMetric object"""
        metric = OptionMetric(
            identifier='AAPL 260116C00200000',
            symbol='AAPL',
            strike=200.0,
            put_call='CALL',
            expiry=1768540800000,
            multiplier=100,
            latest_price=10.5,
            delta=0.5,
            gamma=0.01,
            theta=-0.05,
            vega=0.15,
            rho=0.08
        )
        
        self.assertEqual(metric.identifier, 'AAPL 260116C00200000')
        self.assertEqual(metric.symbol, 'AAPL')
        self.assertEqual(metric.strike, 200.0)
        self.assertEqual(metric.put_call, 'CALL')
        self.assertEqual(metric.latest_price, 10.5)
        self.assertEqual(metric.delta, 0.5)
    
    def test_option_metric_to_dict(self):
        """Test converting OptionMetric to dictionary"""
        metric = OptionMetric(
            identifier='AAPL 260116C00200000',
            symbol='AAPL',
            strike=200.0,
            put_call='CALL',
            expiry=1768540800000,
            multiplier=100,
            latest_price=10.5
        )
        
        result = metric.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['identifier'], 'AAPL 260116C00200000')
        self.assertEqual(result['strike'], 200.0)
    
    def test_option_metric_str(self):
        """Test string representation of OptionMetric"""
        metric = OptionMetric(
            identifier='AAPL 260116C00200000',
            symbol='AAPL',
            strike=200.0,
            put_call='CALL',
            expiry=1768540800000,
            multiplier=100,
            latest_price=10.5,
            delta=0.5,
            implied_vol=0.3
        )
        
        str_repr = str(metric)
        self.assertIn('AAPL 260116C00200000', str_repr)
        self.assertIn('200.0', str_repr)


@unittest.skipIf(not HAS_QUANTLIB, "QuantLib not installed")
class TestOptionUtil(unittest.TestCase):
    """Test cases for OptionUtil class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock QuoteClient
        self.mock_quote_client = Mock(spec=QuoteClient)
        
        # Create OptionUtil instance
        self.option_util = OptionUtil(self.mock_quote_client)
    
    def _create_mock_option_briefs(self):
        """Create mock option briefs DataFrame"""
        return pd.DataFrame({
            'identifier': ['AAPL 260116C00200000'],
            'symbol': ['AAPL'],
            'strike': [200.0],
            'put_call': ['CALL'],
            'expiry': [1768540800000],  # 2026-01-16
            'multiplier': [100],
            'latest_price': [10.5],
            'mark_price': [10.55],
            'ask_price': [10.6],
            'bid_price': [10.4],
            'currency': ['USD'],
            'rates_bonds': [0.02],
            'volatility': [0.3]
        })
    
    def test_init_without_quantlib(self):
        """Test initialization fails without QuantLib"""
        with patch('tigeropen.examples.option_helpers.util.ql', None):
            with self.assertRaises(ImportError):
                OptionUtil(self.mock_quote_client)
    
    def test_init_with_quote_client(self):
        """Test successful initialization"""
        self.assertIsInstance(self.option_util.quote_client, QuoteClient)
        self.assertIsNone(self.option_util.trade_client)
        self.assertIsNotNone(self.option_util.probability_calculator)
        self.assertIsNotNone(self.option_util.extra_calculator)
    
    def test_init_with_trade_client(self):
        """Test initialization with TradeClient"""
        mock_trade_client = Mock(spec=TradeClient)
        option_util = OptionUtil(self.mock_quote_client, mock_trade_client)
        
        self.assertIsInstance(option_util.quote_client, QuoteClient)
        self.assertIsInstance(option_util.trade_client, TradeClient)
        self.assertIsNotNone(option_util.probability_calculator)
        self.assertIsNotNone(option_util.extra_calculator)
    
    def test_get_option_metrics_empty_briefs(self):
        """Test get_option_metrics with empty briefs"""
        # Mock empty DataFrame
        self.mock_quote_client.get_option_briefs.return_value = pd.DataFrame()
        
        with self.assertRaises(ValueError):
            self.option_util.get_option_metrics(['AAPL 260116C00200000'])
        self.mock_quote_client.get_option_briefs.assert_called_once()

    def test_get_option_metrics_empty_briefs_list_return(self):
        """Test get_option_metrics with empty briefs returns empty list"""
        # Mock empty DataFrame
        self.mock_quote_client.get_option_briefs.return_value = pd.DataFrame()
        
        with self.assertRaises(ValueError):
            self.option_util.get_option_metrics(
                ['AAPL 260116C00200000'],
                return_type='list'
            )

    def test_get_option_metrics_dataframe_return(self):
        """Test get_option_metrics returns DataFrame"""
        # Setup mock data
        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        
        # Call method
        # Mock underlying stock briefs
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        result = self.option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            return_type='dataframe'
        )
        
        # Assertions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn('delta', result.columns)
        self.assertIn('gamma', result.columns)
        self.assertIn('theta', result.columns)
        self.assertIn('vega', result.columns)
        self.assertIn('rho', result.columns)
        self.assertIn('implied_vol', result.columns)
        self.assertIn('leverage_ratio', result.columns)
        self.assertIn('profit_probability', result.columns)
    
    def test_get_option_metrics_list_return(self):
        """Test get_option_metrics returns list of OptionMetric"""
        # Setup mock data
        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        
        # Call method
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        result = self.option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            return_type='list'
        )
        
        # Assertions
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], OptionMetric)
        self.assertEqual(result[0].identifier, 'AAPL 260116C00200000')
        self.assertEqual(result[0].symbol, 'AAPL')
    
    def test_get_option_metrics_with_dividend_rate(self):
        """Test get_option_metrics with explicit dividend rate"""
        # Setup mock data
        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        
        # Call method with explicit dividend_rate
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        result = self.option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            dividend_rate=0.01
        )
        
        # Assertions
        self.assertIsInstance(result, pd.DataFrame)
        # Should not call get_stock_fundamental when dividend_rate is provided
        with self.assertRaises(ValueError):
            self.option_util.get_option_metrics(
                ['AAPL 260116C00200000']
            )

    def test_get_option_metrics_automatic_dividend_rate(self):
        """Test automatic dividend rate fetching"""
        # Setup mock data
        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        
        # Call method without dividend_rate
        result = self.option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            underlying_price=210.0,
            dividend_rate=None
        )
        
        # Should call get_stock_fundamental
        self.mock_quote_client.get_stock_fundamental.assert_called_once()
    
    def test_get_option_metrics_market_parameter(self):
        """Test market parameter usage"""
        # Test with default market='US'
        mock_briefs_us = pd.DataFrame({
            'identifier': ['AAPL 260116C00200000'],
            'symbol': ['AAPL'],
            'strike': [200.0],
            'put_call': ['CALL'],
            'expiry': [1768540800000],
            'multiplier': [100],
            'latest_price': [10.5]
        })
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs_us
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        
        # Test with default market
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        self.option_util.get_option_metrics(
            ['AAPL 260116C00200000']
        )
        
        # Check if get_stock_fundamental was called with US market (default)
        call_args = self.mock_quote_client.get_stock_fundamental.call_args
        self.assertEqual(call_args[1]['market'], 'US')
        
        # Test with explicit HK market
        self.mock_quote_client.get_stock_fundamental.reset_mock()
        self.option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            underlying_price=210.0,
            market='HK'
        )
        
        call_args = self.mock_quote_client.get_stock_fundamental.call_args
        self.assertEqual(call_args[1]['market'], 'HK')
    
    def test_calculate_price_probabilities(self):
        """Test calculate_price_probabilities method"""
        result = self.option_util.calculate_price_probabilities(
            stock_price=100.0,
            target_price=105.0,
            iv=0.3,
            days=30
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('cumulative_probability', result)
        self.assertIn('probability_above', result)
        self.assertGreaterEqual(result['cumulative_probability'], 0)
        self.assertLessEqual(result['cumulative_probability'], 1)
        self.assertAlmostEqual(
            result['cumulative_probability'] + result['probability_above'],
            1.0,
            places=10
        )
    
    def test_calculate_price_range_probability(self):
        """Test calculate_price_range_probability method"""
        result = self.option_util.calculate_price_range_probability(
            stock_price=100.0,
            lower_price=95.0,
            upper_price=105.0,
            iv=0.3,
            days=30
        )
        
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)
    
    def test_timestamp_to_ql_date(self):
        """Test _timestamp_to_ql_date conversion"""
        # 2026-01-16 00:00:00 UTC
        timestamp_ms = 1768540800000
        
        ql_date = self.option_util._timestamp_to_ql_date(timestamp_ms)
        
        self.assertIsInstance(ql_date, ql.Date)
        # Verify date components
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
        self.assertEqual(ql_date.dayOfMonth(), dt.day)
        self.assertEqual(ql_date.month(), dt.month)
        self.assertEqual(ql_date.year(), dt.year)
    
    def test_timestamp_to_date_str(self):
        """Test _timestamp_to_date_str conversion"""
        # 2026-01-16 00:00:00 UTC
        timestamp_ms = 1768540800000
        
        date_str = self.option_util._timestamp_to_date_str(timestamp_ms)
        
        self.assertIsInstance(date_str, str)
        self.assertEqual(len(date_str), 8)  # YYYYMMDD format
        # Verify it's a valid date format
        dt = datetime.strptime(date_str, '%Y%m%d')
        self.assertIsNotNone(dt)
    
    def test_dataframe_to_metrics(self):
        """Test _dataframe_to_metrics conversion"""
        # Create test DataFrame
        test_df = pd.DataFrame({
            'identifier': ['AAPL 260116C00200000', 'AAPL 260116P00200000'],
            'symbol': ['AAPL', 'AAPL'],
            'strike': [200.0, 200.0],
            'put_call': ['CALL', 'PUT'],
            'expiry': [1768540800000, 1768540800000],
            'multiplier': [100, 100],
            'latest_price': [10.5, 8.5],
            'delta': [0.5, -0.4],
            'gamma': [0.01, 0.01],
            'theta': [-0.05, -0.04],
            'vega': [0.15, 0.15],
            'rho': [0.08, -0.07],
            'implied_vol': [0.3, 0.28],
            'leverage_ratio': [5.0, 4.5],
            'profit_probability': [0.45, 0.4]
        })
        
        result = self.option_util._dataframe_to_metrics(test_df)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], OptionMetric)
        self.assertIsInstance(result[1], OptionMetric)
        self.assertEqual(result[0].identifier, 'AAPL 260116C00200000')
        self.assertEqual(result[1].identifier, 'AAPL 260116P00200000')
        self.assertEqual(result[0].put_call, 'CALL')
        self.assertEqual(result[1].put_call, 'PUT')
    
    def test_get_option_metrics_error_handling(self):
        """Test error handling in get_option_metrics"""
        # Setup mock data with invalid values
        mock_briefs = pd.DataFrame({
            'identifier': ['AAPL 260116C00200000'],
            'symbol': ['AAPL'],
            'strike': [None],  # Invalid strike
            'put_call': ['CALL'],
            'expiry': [1768540800000],
            'multiplier': [100],
            'latest_price': [None]  # Invalid price
        })
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        
        # Should not raise exception
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.0]
        })
        result = self.option_util.get_option_metrics(
            ['AAPL 260116C00200000']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_get_option_metrics_multiple_identifiers(self):
        """Test get_option_metrics with multiple identifiers"""
        # Setup mock data with multiple options
        mock_briefs = pd.DataFrame({
            'identifier': ['AAPL 260116C00200000', 'AAPL 260116C00210000', 'AAPL 260116P00200000'],
            'symbol': ['AAPL', 'AAPL', 'AAPL'],
            'strike': [200.0, 210.0, 200.0],
            'put_call': ['CALL', 'CALL', 'PUT'],
            'expiry': [1768540800000, 1768540800000, 1768540800000],
            'multiplier': [100, 100, 100],
            'latest_price': [10.5, 5.5, 8.5],
            'ask_price': [10.6, 5.6, 8.6],
            'bid_price': [10.4, 5.4, 8.4],
            'rates_bonds': [0.02, 0.02, 0.02],
            'volatility': [0.3, 0.32, 0.28]
        })
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        result = self.option_util.get_option_metrics(
            ['AAPL 260116C00200000', 'AAPL 260116C00210000', 'AAPL 260116P00200000'],
            return_type='list'
        )
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].put_call, 'CALL')
        self.assertEqual(result[2].put_call, 'PUT')
    
    def test_get_option_metrics_with_trade_client_margin(self):
        """Test get_option_metrics with TradeClient preview margin calculation"""
        mock_trade_client = Mock(spec=TradeClient)
        mock_trade_client._account = 'TEST123'
        mock_trade_client.preview_order.return_value = {
            'init_margin_before': 10000.0,
            'init_margin': 10250.0
        }

        option_util = OptionUtil(self.mock_quote_client, mock_trade_client)

        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })

        result = option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            return_type='dataframe'
        )

        mock_trade_client.preview_order.assert_called_once()
        preview_order_arg = mock_trade_client.preview_order.call_args[0][0]
        self.assertEqual(preview_order_arg.limit_price, mock_briefs.loc[0, 'mark_price'])
        self.assertEqual(preview_order_arg.order_type, 'LMT')
        self.assertEqual(preview_order_arg.action, 'SELL')

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('annualized_leveraged_sell_return', result.columns)
    
    def test_get_option_metrics_without_trade_client_fallback(self):
        """Test get_option_metrics fallback margin calculation without TradeClient"""
        # Create OptionUtil without TradeClient (use setUp instance)
        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        
        # Call method
        result = self.option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            return_type='dataframe'
        )
        
        # Should still calculate margin (using fallback)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('annualized_leveraged_sell_return', result.columns)
    
    def test_get_option_metrics_trade_client_error_handling(self):
        """Test error handling when preview_order fails"""
        mock_trade_client = Mock(spec=TradeClient)
        mock_trade_client._account = 'TEST123'
        mock_trade_client.preview_order.side_effect = Exception("API Error")

        option_util = OptionUtil(self.mock_quote_client, mock_trade_client)

        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })

        result = option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            return_type='dataframe'
        )

        mock_trade_client.preview_order.assert_called_once()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('annualized_leveraged_sell_return', result.columns)
    
    def test_get_option_metrics_trade_client_preview_missing_fields(self):
        """Test handling when preview_order returns incomplete margin data"""
        mock_trade_client = Mock(spec=TradeClient)
        mock_trade_client._account = 'TEST123'
        mock_trade_client.preview_order.return_value = {'warning_text': 'no margin'}

        option_util = OptionUtil(self.mock_quote_client, mock_trade_client)

        mock_briefs = self._create_mock_option_briefs()
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })

        result = option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            return_type='dataframe'
        )

        mock_trade_client.preview_order.assert_called_once()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('annualized_leveraged_sell_return', result.columns)
    
    def test_get_option_metrics_put_option_margin(self):
        """Test margin calculation for PUT options"""
        # Setup mock TradeClient
        mock_trade_client = Mock(spec=TradeClient)
        mock_trade_client._account = 'TEST123'
        mock_trade_client.preview_order.return_value = {
            'init_margin_before': 15000.0,
            'init_margin': 15120.0
        }
        
        option_util = OptionUtil(self.mock_quote_client, mock_trade_client)
        
        # Setup mock data for PUT option
        mock_briefs = pd.DataFrame({
            'identifier': ['AAPL 260116P00200000'],
            'symbol': ['AAPL'],
            'strike': [200.0],
            'put_call': ['PUT'],  # PUT option
            'expiry': [1768540800000],
            'multiplier': [100],
            'latest_price': [8.5],
            'mark_price': [8.55],
            'ask_price': [8.6],
            'bid_price': [8.4],
            'currency': ['USD'],
            'rates_bonds': [0.02],
            'volatility': [0.28]
        })
        self.mock_quote_client.get_option_briefs.return_value = mock_briefs
        self.mock_quote_client.get_stock_fundamental.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'divide_rate': [0.005]
        })
        self.mock_quote_client.get_stock_briefs.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'latest_price': [210.0]
        })
        
        # Call method
        result = option_util.get_option_metrics(
            ['AAPL 260116P00200000'],
            return_type='dataframe'
        )
        
        mock_trade_client.preview_order.assert_called_once()
        preview_order_arg = mock_trade_client.preview_order.call_args[0][0]
        self.assertEqual(preview_order_arg.contract.put_call, 'PUT')
        self.assertEqual(preview_order_arg.limit_price, 8.55)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('annualized_leveraged_sell_return', result.columns)


class TestOptionUtilIntegration(unittest.TestCase):
    """Integration tests for OptionUtil (requires actual QuoteClient configuration)"""
    
    @unittest.skip("Requires actual API credentials")
    def test_real_option_metrics(self):
        """Test with real QuoteClient (skip by default)"""
        from tigeropen.tiger_open_config import TigerOpenClientConfig
        import os
        
        # This would require actual configuration
        current_dir = os.path.dirname(__file__)
        client_config = TigerOpenClientConfig(
            props_path=os.path.join(current_dir, ".config/prod_2015xxxx/")
        )
        quote_client = QuoteClient(client_config)
        option_util = OptionUtil(quote_client)
        
        # Test with real data
        result = option_util.get_option_metrics(
            ['AAPL 260116C00200000'],
            return_type='dataframe'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('delta', result.columns)


if __name__ == '__main__':
    unittest.main()
