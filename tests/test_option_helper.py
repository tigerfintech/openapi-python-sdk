# -*- coding: utf-8 -*-
# 
# @Date    : 2025/1/13
# @Author  : sukai
import unittest
import math

from tigeropen.examples.option_helpers.probability_calculator import ProbabilityCalculator
from tigeropen.examples.option_helpers.extra_calculator import ExtraCalculator


class TestProbabilityCalculator(unittest.TestCase):
    """Test all methods of ProbabilityCalculator class"""

    def setUp(self):
        self.calc = ProbabilityCalculator()
        self.delta = 1e-6

    def test_cumulative_probability_normal(self):
        """Test cumulative probability calculation in normal cases"""
        # Test price increase scenario
        result = self.calc.cumulative_probability(240.52, 240, 0.7109, 5)
        # Expected value computed from current implementation
        self.assertAlmostEqual(result, 0.48962385461244784, delta=self.delta)
        
        # Test price decrease scenario
        result = self.calc.cumulative_probability(100, 90, 0.2, 30)
        self.assertLess(result, 0.5)

    def test_cumulative_probability_zero_iv(self):
        """Test cumulative probability with zero implied volatility"""
        # iv=0 and q > p should return 1.0
        result = self.calc.cumulative_probability(100, 110, 0, 30)
        self.assertEqual(result, 1.0)
        
        # iv=0 and q <= p should return 0.0
        result = self.calc.cumulative_probability(100, 90, 0, 30)
        self.assertEqual(result, 0.0)

    def test_cumulative_probability_invalid_input(self):
        """Test invalid input handling"""
        # Negative price should return NaN
        result = self.calc.cumulative_probability(-100, 110, 0.2, 30)
        self.assertTrue(math.isnan(result))

    def test_probability_range(self):
        """Test probability range calculation"""
        result = self.calc.probability(100, 90, 110, 0.2, 30)
        self.assertGreater(result, 0)
        self.assertLess(result, 1)
        
        # Verify result equals difference of two cumulative probabilities
        expected = (self.calc.cumulative_probability(100, 110, 0.2, 30) - 
                   self.calc.cumulative_probability(100, 90, 0.2, 30))
        self.assertAlmostEqual(result, expected, delta=self.delta)

    def test_probability_range_zero_iv(self):
        """Test range probability when iv=0"""
        # Current price 100, range [90,110], iv=0, should return 1.0
        result = self.calc.probability(100, 90, 110, 0, 30)
        self.assertEqual(result, 1.0)

    def test_calc_z_value_from_probability(self):
        """Test z-value calculation from probability"""
        # Z-value for 95% confidence interval is approximately 1.96
        result = self.calc.calc_z_value_from_probability(0.95)
        self.assertAlmostEqual(result, 1.959963984540054, delta=0.01)
        
        # Z-value for 68% confidence interval is approximately 1.0
        result = self.calc.calc_z_value_from_probability(0.68)
        self.assertAlmostEqual(result, 1.0, delta=0.05)

    def test_calc_z_value_boundary(self):
        """Test z-value calculation boundary cases"""
        # None input should return 1.0
        result = self.calc.calc_z_value_from_probability(None)
        self.assertEqual(result, 1.0)
        
        # NaN input should return 1.0
        result = self.calc.calc_z_value_from_probability(float('nan'))
        self.assertEqual(result, 1.0)
        
        # Probability >= 1.0 should be truncated
        result = self.calc.calc_z_value_from_probability(1.5)
        self.assertGreater(result, 0)

    def test_calc_future_price_delta(self):
        """Test future price delta calculation"""
        result = self.calc.calc_future_price_delta(100, 0.2, 30, 1.96)
        self.assertAlmostEqual(result, 11.23829070998752, delta=0.01)
        
        # Test with different parameters
        result = self.calc.calc_future_price_delta(50, 0.3, 60, 2.0)
        self.assertGreater(result, 0)

    def test_calc_future_price_delta_invalid(self):
        """Test price delta calculation boundary cases"""
        # None input should return 0.0
        result = self.calc.calc_future_price_delta(None, 0.2, 30, 1.96)
        self.assertEqual(result, 0.0)
        
        # NaN input should return 0.0
        result = self.calc.calc_future_price_delta(float('nan'), 0.2, 30, 1.96)
        self.assertEqual(result, 0.0)
        
        # future_days=0 should return 0.0
        result = self.calc.calc_future_price_delta(100, 0.2, 0, 1.96)
        self.assertEqual(result, 0.0)

    def test_calc_below_price_probability(self):
        """Test probability of price being below a certain level"""
        # Calculate probability of price below 90 after 30 days
        result = self.calc.calc_below_price_probability(100, 90, 0.2, 30, 1.96)
        self.assertGreater(result, 0)
        self.assertLess(result, 1)

    def test_calc_below_price_probability_invalid(self):
        """Test invalid input cases"""
        # None input should return NaN
        result = self.calc.calc_below_price_probability(None, 90, 0.2, 30, 1.96)
        self.assertTrue(math.isnan(result))

    def test_probability_call_and_put_profit(self):
        """Test call/put profit probability helpers"""
        pc = self.calc
        S0 = 100.0
        K = 105.0
        premium = 2.0  # per-unit premium
        iv = 0.2
        days = 30

        # Call profit probability: S_T > K + premium
        prob_call = pc.probability_long_profit(S0, K, premium, iv, days, option_type="CALL")
        # Should be between 0 and 1
        self.assertGreaterEqual(prob_call, 0.0)
        self.assertLessEqual(prob_call, 1.0)

        # Put profit probability: S_T < K - premium
        prob_put = pc.probability_long_profit(S0, K, premium, iv, days, option_type="PUT")
        self.assertGreaterEqual(prob_put, 0.0)
        self.assertLessEqual(prob_put, 1.0)

        # If premium is zero, call profit probability = P(S_T > K)
        prob_call_no_premium = pc.probability_long_profit(S0, K, 0.0, iv, days, option_type="CALL")
        expected = 1.0 - pc.cumulative_probability(S0, K, iv, days)
        self.assertAlmostEqual(prob_call_no_premium, expected, delta=1e-9)

        # If premium equals K (extreme), breakeven for put becomes 0, prob_put should be P(S_T < 0) ~= 0
        prob_put_extreme = pc.probability_long_profit(S0, K, K, iv, days, option_type="PUT")
        self.assertLess(prob_put_extreme, 1e-6)
        
        # Very small price (<= 1e-12) should return NaN
        result = self.calc.calc_below_price_probability(1e-13, 90, 0.2, 30, 1.96)
        self.assertTrue(math.isnan(result))
        
        # Volatility = 0 should return NaN
        result = self.calc.calc_below_price_probability(100, 90, 0, 30, 1.96)
        self.assertTrue(math.isnan(result))
        
        # future_days=0 should return NaN
        result = self.calc.calc_below_price_probability(100, 90, 0.2, 0, 1.96)
        self.assertTrue(math.isnan(result))


class TestExtraCalculator(unittest.TestCase):
    """Test all methods of ExtraCalculator class"""

    def setUp(self):
        self.delta = 1e-6

    def test_annualized_leveraged_sell_return_normal(self):
        """Test annualized levered sell return in normal cases"""
        # Time value 1.5 per share, multiplier 100, margin 1000 per contract, 30 days to expiry
        result = ExtraCalculator.annualized_leveraged_sell_return(1.5, 1000.0, 30, multiplier=100)
        expected = (1.5 * 100) / 1000.0 * 365.0 / 30.0
        self.assertAlmostEqual(result, expected, delta=self.delta)
        self.assertAlmostEqual(result, 1.825, delta=self.delta)

    def test_annualized_leveraged_sell_return_custom_multiplier(self):
        """Test with a custom contract multiplier"""
        # Time value 2.0 per share, multiplier 150 shares, margin 50000 per contract, 60 days
        result = ExtraCalculator.annualized_leveraged_sell_return(2.0, 50000.0, 60, multiplier=150)
        expected = (2.0 * 150) / 50000.0 * 365.0 / 60.0
        self.assertAlmostEqual(result, expected, delta=self.delta)
        self.assertGreater(result, 0)

    def test_annualized_leveraged_sell_return_short_expiry(self):
        """Test short-term expiry case"""
        # 1 day to expiry, annualized return should be high
        result = ExtraCalculator.annualized_leveraged_sell_return(1.0, 1000.0, 1, multiplier=100)
        self.assertGreater(result, 0.3)  # Should be greater than 30%

    def test_annualized_leveraged_sell_return_invalid_days(self):
        """Test invalid days to expiry"""
        # days_to_expiry <= 0 should return NaN
        result = ExtraCalculator.annualized_leveraged_sell_return(1.5, 1000.0, 0, multiplier=100)
        self.assertTrue(math.isnan(result))
        
        result = ExtraCalculator.annualized_leveraged_sell_return(1.5, 1000.0, -10, multiplier=100)
        self.assertTrue(math.isnan(result))

    def test_annualized_leveraged_sell_return_invalid_margin(self):
        """Test invalid margin"""
        # sell_margin <= 0 should return NaN
        result = ExtraCalculator.annualized_leveraged_sell_return(1.5, 0, 30, multiplier=100)
        self.assertTrue(math.isnan(result))
        
        result = ExtraCalculator.annualized_leveraged_sell_return(1.5, -1000.0, 30, multiplier=100)
        self.assertTrue(math.isnan(result))

    def test_annualized_leveraged_sell_return_invalid_multiplier(self):
        """Test invalid multiplier (shares per contract)"""
        # multiplier <= 0 should return NaN
        result = ExtraCalculator.annualized_leveraged_sell_return(1.5, 1000.0, 30, multiplier=0)
        self.assertTrue(math.isnan(result))
        
        result = ExtraCalculator.annualized_leveraged_sell_return(1.5, 1000.0, 30, multiplier=-1)
        self.assertTrue(math.isnan(result))

    def test_leverage_ratio_normal(self):
        """Test leverage ratio in normal cases"""
        # delta=0.5, underlying price 50, option price 2
        result = ExtraCalculator.leverage_ratio(0.5, 50.0, 2.0)
        expected = 0.5 * 50.0 / 2.0
        self.assertAlmostEqual(result, expected, delta=self.delta)
        self.assertAlmostEqual(result, 12.5, delta=self.delta)

    def test_leverage_ratio_high_delta(self):
        """Test high delta case (deep in-the-money option)"""
        # delta=0.9, underlying price 100, option price 10
        result = ExtraCalculator.leverage_ratio(0.9, 100.0, 10.0)
        expected = 0.9 * 100.0 / 10.0
        self.assertAlmostEqual(result, expected, delta=self.delta)
        self.assertAlmostEqual(result, 9.0, delta=self.delta)

    def test_leverage_ratio_low_delta(self):
        """Test low delta case (out-of-the-money option)"""
        # delta=0.1, underlying price 50, option price 0.5
        result = ExtraCalculator.leverage_ratio(0.1, 50.0, 0.5)
        expected = 0.1 * 50.0 / 0.5
        self.assertAlmostEqual(result, expected, delta=self.delta)
        self.assertAlmostEqual(result, 10.0, delta=self.delta)

    def test_leverage_ratio_zero_option_price(self):
        """Test when option price is zero"""
        # option_price = 0 should return NaN
        result = ExtraCalculator.leverage_ratio(0.5, 50.0, 0)
        self.assertTrue(math.isnan(result))

    def test_leverage_ratio_nan_inputs(self):
        """Test NaN inputs"""
        # delta is NaN
        result = ExtraCalculator.leverage_ratio(float('nan'), 50.0, 2.0)
        self.assertTrue(math.isnan(result))
        
        # underlying_price is NaN
        result = ExtraCalculator.leverage_ratio(0.5, float('nan'), 2.0)
        self.assertTrue(math.isnan(result))
        
        # option_price is NaN
        result = ExtraCalculator.leverage_ratio(0.5, 50.0, float('nan'))
        self.assertTrue(math.isnan(result))

    def test_leverage_ratio_negative_delta(self):
        """Test negative delta case (put option)"""
        # Put options have negative delta, but leverage ratio uses absolute value
        result = ExtraCalculator.leverage_ratio(-0.5, 50.0, 2.0)
        # According to formula, negative delta results in negative leverage ratio
        self.assertAlmostEqual(result, -12.5, delta=self.delta)


if __name__ == '__main__':
    unittest.main()
