# -*- coding: utf-8 -*-
"""
Option utility class for fetching option quotes and calculating option metrics.
@Date    : 2026/1/5
@Author  : sukai
"""
from typing import List, Optional, Union, Dict
import pandas as pd
from datetime import datetime
from dataclasses import dataclass

try:
    import QuantLib as ql
except ImportError:
    ql = None

from tigeropen.quote.quote_client import QuoteClient
from tigeropen.examples.option_helpers.helpers import (
    FDAmericanDividendOptionHelper, 
    FDEuropeanDividendOptionHelper
)
from tigeropen.examples.option_helpers.probability_calculator import ProbabilityCalculator
from tigeropen.examples.option_helpers.extra_calculator import ExtraCalculator


@dataclass
class OptionMetric:
    """
    Data class representing comprehensive option metrics.
    
    Attributes:
        identifier: Option identifier (e.g. "AAPL 250815C00125000")
        symbol: Underlying stock symbol
        strike: Strike price
        put_call: Option direction ('CALL' or 'PUT')
        expiry: Expiration date (millisecond timestamp)
        multiplier: Option multiplier
        latest_price: Current option price
        ask_price: Ask price
        bid_price: Bid price
        ask_size: Ask size
        bid_size: Bid size
        open_interest: Open interest
        volume: Trading volume
        delta: Delta greek
        gamma: Gamma greek
        theta: Theta greek (daily decay)
        vega: Vega greek
        rho: Rho greek
        npv: Net present value
        implied_vol: Implied volatility
        leverage_ratio: Leverage ratio
        annualized_sell_return: Annualized return for selling the option
        profit_probability: Probability that long position will be profitable at expiry
    """
    identifier: str
    symbol: str
    strike: float
    put_call: str
    expiry: int
    multiplier: int
    latest_price: Optional[float]
    ask_price: Optional[float] = None
    bid_price: Optional[float] = None
    ask_size: Optional[float] = None
    bid_size: Optional[float] = None
    open_interest: Optional[float] = None
    volume: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None
    npv: Optional[float] = None
    implied_vol: Optional[float] = None
    leverage_ratio: Optional[float] = None
    annualized_sell_return: Optional[float] = None
    profit_probability: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.__dict__
    
    def __str__(self) -> str:
        """String representation."""
        return (f"OptionMetric({self.identifier}, strike={self.strike}, "
                f"price={self.latest_price:.2f}, delta={self.delta:.4f}, "
                f"iv={self.implied_vol:.4f})")


class OptionUtil:
    """
    Utility class for fetching option market data and calculating option metrics.
    
    This class integrates QuoteClient to fetch real-time option quotes and uses
    various calculators to compute Greeks, probabilities, and other option metrics.
    """
    
    def __init__(self, quote_client: QuoteClient):
        """
        Initialize OptionUtil with a QuoteClient instance.
        
        Args:
            quote_client: Configured QuoteClient instance for fetching market data
        """
        self.quote_client = quote_client
        self.probability_calculator = ProbabilityCalculator()
        self.extra_calculator = ExtraCalculator()
        
        if ql is None:
            raise ImportError("QuantLib is required for this module. Please install QuantLib>=1.40")
    
    def get_option_metrics(self,
                          identifiers: Union[str, List[str]],
                          underlying_price: Optional[float] = None,
                          risk_free_rate: float = 0.02,
                          dividend_rate: Optional[float] = None,
                          is_european: bool = False,
                          reference_date: Optional[ql.Date] = None,
                          market: Optional[str] = None,
                          timezone: Optional[str] = None,
                          return_type: str = 'dataframe') -> Union[pd.DataFrame, List[OptionMetric]]:
        """
        Fetch option quotes and calculate comprehensive option metrics including Greeks.
        
        Args:
            identifiers: Single option identifier or list of identifiers
                        e.g. "AAPL 250815C00125000" or ["AAPL 250815C00125000", ...]
            underlying_price: Current underlying asset price. If None, will try to fetch from quote
            risk_free_rate: Risk-free interest rate (annualized, default 0.02)
            dividend_rate: Dividend rate (annualized). If None, will fetch from get_stock_fundamental
            is_european: Whether the option is European style (default False for American)
            reference_date: Reference date for calculations. If None, uses today
            market: Market code (US/HK/CN)
            timezone: Timezone for date processing
            return_type: Return format - 'dataframe' (default) for pandas DataFrame or 'list' for list of OptionMetric objects
            
        Returns:
            If return_type='dataframe': pandas.DataFrame with columns:
                - All fields from get_option_briefs (price, Greeks, etc.)
                - delta, gamma, theta, vega, rho (calculated)
                - npv (Net Present Value)
                - implied_vol (implied volatility)
                - leverage_ratio
                - annualized_sell_return
                - profit_probability (long position)
                
            If return_type='list': List[OptionMetric] objects containing all calculated metrics
        """
        # Fetch option quotes
        briefs = self.quote_client.get_option_briefs(identifiers, market=market, timezone=timezone)
        
        if briefs.empty:
            if return_type == 'list':
                return []
            return briefs
        
        # Fetch dividend rates for underlying symbols if not provided
        dividend_rates = {}
        if dividend_rate is None:
            try:
                # Get unique underlying symbols
                underlying_symbols = briefs['symbol'].unique().tolist()
                if underlying_symbols:
                    # Infer market if not provided
                    inferred_market = market
                    if inferred_market is None:
                        # Try to infer from first symbol
                        first_symbol = underlying_symbols[0]
                        if first_symbol.startswith('0') or first_symbol.startswith('3') or first_symbol.startswith('6'):
                            inferred_market = 'CN'
                        elif len(first_symbol) == 5 and first_symbol.isdigit():
                            inferred_market = 'HK'
                        else:
                            inferred_market = 'US'
                    
                    # Fetch fundamental data
                    fundamental_data = self.quote_client.get_stock_fundamental(
                        underlying_symbols, 
                        market=inferred_market
                    )
                    
                    # Extract dividend rates
                    if fundamental_data is not None and not fundamental_data.empty:
                        for _, row in fundamental_data.iterrows():
                            symbol = row.get('symbol')
                            div_rate = row.get('divide_rate', 0.0)
                            if symbol and not pd.isna(div_rate):
                                dividend_rates[symbol] = float(div_rate)
            except Exception as e:
                print(f"Warning: Failed to fetch dividend rates: {str(e)}. Using 0.0 as default.")
                # Continue with empty dividend_rates dict
        
        # Set reference date
        if reference_date is None:
            today = datetime.today()
            reference_date = ql.Date(today.day, today.month, today.year)
        
        ql.Settings.instance().evaluationDate = reference_date
        
        # Initialize result columns
        briefs['delta'] = None
        briefs['gamma'] = None
        briefs['theta'] = None
        briefs['vega'] = None
        briefs['rho'] = None
        briefs['npv'] = None
        briefs['implied_vol'] = None
        briefs['leverage_ratio'] = None
        briefs['annualized_sell_return'] = None
        briefs['profit_probability'] = None
        
        # Calculate metrics for each option
        for idx, row in briefs.iterrows():
            try:
                # Determine underlying price
                current_underlying = underlying_price if underlying_price is not None else row.get('latest_price', None)
                if current_underlying is None or pd.isna(current_underlying):
                    continue
                
                # Extract option parameters
                strike = row.get('strike', 0)
                put_call = row.get('put_call', 'CALL')
                expiry_timestamp = row.get('expiry', 0)
                multiplier = row.get('multiplier', 100)
                underlying_symbol = row.get('symbol', '')
                
                # Get dividend rate for this underlying
                if dividend_rate is not None:
                    current_dividend_rate = dividend_rate
                else:
                    current_dividend_rate = dividend_rates.get(underlying_symbol, 0.0)
                
                # Calculate days to expiry
                expiry_date = self._timestamp_to_ql_date(expiry_timestamp)
                days_to_expiry = expiry_date - reference_date
                
                if days_to_expiry <= 0:
                    continue
                
                # Get option type
                option_type = ql.Option.Call if put_call == 'CALL' else ql.Option.Put
                
                # Get market data for calculations
                ask_price = row.get('ask_price', 0)
                bid_price = row.get('bid_price', 0)
                latest_price = row.get('latest_price', 0)
                
                # Determine option price for calculations
                if latest_price and not pd.isna(latest_price) and latest_price > 0:
                    option_price = latest_price
                elif ask_price and bid_price and not pd.isna(ask_price) and not pd.isna(bid_price):
                    option_price = (ask_price + bid_price) / 2
                else:
                    continue
                
                # Get or use provided rates
                rf_rate = row.get('rates_bonds', risk_free_rate)
                if pd.isna(rf_rate):
                    rf_rate = risk_free_rate
                
                # Get historical volatility as initial guess
                hist_vol = row.get('volatility', 0.3)
                if pd.isna(hist_vol) or hist_vol == 0:
                    hist_vol = 0.3
                else:
                    # Convert from percentage if needed
                    if hist_vol > 1:
                        hist_vol = hist_vol / 100.0
                
                # Create option hecurrent_lper
                helper_class = FDEuropeanDividendOptionHelper if is_european else FDAmericanDividendOptionHelper
                helper = helper_class(
                    option_type=option_type,
                    underlying=current_underlying,
                    strike=strike,
                    risk_free_rate=rf_rate,
                    dividend_rate=current_dividend_rate,
                    volatility=hist_vol,
                    settlement_date=reference_date,
                    expiration_date=expiry_date
                )
                
                # Calculate implied volatility
                try:
                    implied_vol = helper.implied_volatility(option_price)
                    helper.update_implied_volatility(implied_vol)
                    briefs.loc[idx, 'implied_vol'] = implied_vol
                except Exception:
                    implied_vol = hist_vol
                    briefs.loc[idx, 'implied_vol'] = implied_vol
                
                # Calculate Greeks
                briefs.loc[idx, 'npv'] = helper.NPV()
                briefs.loc[idx, 'delta'] = helper.delta()
                briefs.loc[idx, 'gamma'] = helper.gamma()
                briefs.loc[idx, 'theta'] = helper.theta()
                briefs.loc[idx, 'vega'] = helper.vega()
                briefs.loc[idx, 'rho'] = helper.rho()
                
                # Calculate leverage ratio
                delta = helper.delta()
                leverage = self.extra_calculator.leverage_ratio(delta, current_underlying, option_price)
                briefs.loc[idx, 'leverage_ratio'] = leverage
                
                # Calculate annualized sell return (if selling margin available)
                time_value = option_price - max(0, 
                    (current_underlying - strike) if put_call == 'CALL' else (strike - current_underlying))
                # Estimate sell margin (simplified)
                if put_call == 'PUT':
                    sell_margin = strike * multiplier
                else:
                    sell_margin = current_underlying * multiplier
                
                ann_return = self.extra_calculator.annualized_leveraged_sell_return(
                    time_value, sell_margin, days_to_expiry, multiplier
                )
                briefs.loc[idx, 'annualized_sell_return'] = ann_return
                
                # Calculate profit probability for long position
                profit_prob = self.probability_calculator.probability_long_profit(
                    stock_price=current_underlying,
                    strike=strike,
                    premium=option_price,
                    iv=implied_vol,
                    days=days_to_expiry,
                    option_type=put_call,
                    contract_multiplier=multiplier
                )
                briefs.loc[idx, 'profit_probability'] = profit_prob
                
            except Exception as e:
                # Log error but continue with other options
                print(f"Error calculating metrics for {row.get('identifier', 'unknown')}: {str(e)}")
                continue
        
        # Return in requested format
        if return_type == 'list':
            return self._dataframe_to_metrics(briefs)
        else:
            return briefs
    
    def _dataframe_to_metrics(self, briefs: pd.DataFrame) -> List[OptionMetric]:
        """Convert DataFrame to list of OptionMetric objects."""
        metrics_list = []
        for _, row in briefs.iterrows():
            metric = OptionMetric(
                identifier=row['identifier'] if 'identifier' in row else '',
                symbol=row['symbol'] if 'symbol' in row else '',
                strike=row['strike'] if 'strike' in row else 0.0,
                put_call=row['put_call'] if 'put_call' in row else '',
                expiry=row['expiry'] if 'expiry' in row else 0,
                multiplier=row['multiplier'] if 'multiplier' in row else 100,
                latest_price=row['latest_price'] if 'latest_price' in row else None,
                ask_price=row['ask_price'] if 'ask_price' in row else None,
                bid_price=row['bid_price'] if 'bid_price' in row else None,
                ask_size=row['ask_size'] if 'ask_size' in row else None,
                bid_size=row['bid_size'] if 'bid_size' in row else None,
                open_interest=row['open_interest'] if 'open_interest' in row else None,
                volume=row['volume'] if 'volume' in row else None,
                delta=row['delta'] if 'delta' in row else None,
                gamma=row['gamma'] if 'gamma' in row else None,
                theta=row['theta'] if 'theta' in row else None,
                vega=row['vega'] if 'vega' in row else None,
                rho=row['rho'] if 'rho' in row else None,
                npv=row['npv'] if 'npv' in row else None,
                implied_vol=row['implied_vol'] if 'implied_vol' in row else None,
                leverage_ratio=row['leverage_ratio'] if 'leverage_ratio' in row else None,
                annualized_sell_return=row['annualized_sell_return'] if 'annualized_sell_return' in row else None,
                profit_probability=row['profit_probability'] if 'profit_probability' in row else None
            )
            metrics_list.append(metric)
        return metrics_list
    
    def calculate_price_probabilities(self,
                                     stock_price: float,
                                     target_price: float,
                                     iv: float,
                                     days: float) -> Dict[str, float]:
        """
        Calculate probability metrics for price movements.
        
        Args:
            stock_price: Current stock price
            target_price: Target price level
            iv: Implied volatility (annualized)
            days: Time horizon in days
            
        Returns:
            Dictionary with probability metrics
        """
        cumulative_prob = self.probability_calculator.cumulative_probability(
            stock_price, target_price, iv, days
        )
        
        return {
            'cumulative_probability': cumulative_prob,
            'probability_above': 1.0 - cumulative_prob
        }
    
    def calculate_price_range_probability(self,
                                         stock_price: float,
                                         lower_price: float,
                                         upper_price: float,
                                         iv: float,
                                         days: float) -> float:
        """
        Calculate probability that price will be within a range.
        
        Args:
            stock_price: Current stock price
            lower_price: Lower bound
            upper_price: Upper bound
            iv: Implied volatility (annualized)
            days: Time horizon in days
            
        Returns:
            Probability that price will be in [lower_price, upper_price]
        """
        return self.probability_calculator.probability(
            stock_price, lower_price, upper_price, iv, days
        )
    
    def _timestamp_to_ql_date(self, timestamp_ms: int) -> ql.Date:
        """Convert millisecond timestamp to QuantLib Date."""
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
        return ql.Date(dt.day, dt.month, dt.year)


if __name__ == '__main__':
    # Example usage (requires configured QuoteClient)
    from tigeropen.tiger_open_config import TigerOpenClientConfig
    
    # Configure client with your properties file
    client_config = TigerOpenClientConfig(props_path='/path/to/your/properties/file/')
    quote_client = QuoteClient(client_config)
    
    option_util = OptionUtil(quote_client)
    
    # Calculate metrics for specific options
    identifiers = ['AAPL 260116C00200000']
    
    # Example 1: Return as DataFrame
    print("=" * 80)
    print("Example 1: Return as DataFrame")
    print("=" * 80)
    metrics_df = option_util.get_option_metrics(identifiers, underlying_price=240.52, return_type='dataframe')
    print(metrics_df[['identifier', 'strike', 'put_call', 'latest_price', 
                      'delta', 'gamma', 'theta', 'vega', 'implied_vol', 
                      'leverage_ratio', 'profit_probability']])
    
    # Example 2: Return as List of OptionMetric objects
    print("\n" + "=" * 80)
    print("Example 2: Return as List of OptionMetric objects")
    print("=" * 80)
    metrics_list = option_util.get_option_metrics(identifiers, underlying_price=240.52, return_type='list')
    for metric in metrics_list:
        print(metric)
        print(f"  Greeks: delta={metric.delta:.4f}, gamma={metric.gamma:.6f}, "
              f"theta={metric.theta:.4f}, vega={metric.vega:.4f}")
        print(f"  Risk: implied_vol={metric.implied_vol:.4f}, leverage={metric.leverage_ratio:.4f}")
        print(f"  Probability: profit_prob={metric.profit_probability:.4f}")
