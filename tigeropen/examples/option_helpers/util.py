# -*- coding: utf-8 -*-
"""
Option utility class for fetching option quotes and calculating option metrics.
@Date    : 2026/1/5
@Author  : sukai
"""
from typing import List, Optional, Union, Dict
import logging
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    import QuantLib as ql
except ImportError:
    ql = None

from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.util.contract_utils import option_contract_by_symbol
from tigeropen.common.util.order_utils import limit_order
from tigeropen.common.util.contract_utils import option_contract_by_symbol
from tigeropen.examples.option_helpers.helpers import (
    FDAmericanDividendOptionHelper, 
    FDEuropeanDividendOptionHelper
)
from tigeropen.examples.option_helpers.probability_calculator import ProbabilityCalculator
from tigeropen.examples.option_helpers.extra_calculator import ExtraCalculator

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



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
        underlying_price: Current underlying stock price
        delta: Delta greek
        gamma: Gamma greek
        theta: Theta greek (daily decay)
        vega: Vega greek
        rho: Rho greek
        npv: Net present value
        implied_vol: Implied volatility
        leverage_ratio: Leverage ratio
        annualized_leveraged_sell_return: Annualized return for selling the option
        profit_probability: Probability that long position will be profitable at expiry
    """
    identifier: str
    symbol: str
    strike: float
    put_call: str
    expiry: int
    multiplier: int
    latest_price: Optional[float]
    underlying_price: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None
    npv: Optional[float] = None
    implied_vol: Optional[float] = None
    leverage_ratio: Optional[float] = None
    annualized_leveraged_sell_return: Optional[float] = None
    profit_probability: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.__dict__
    
    def __str__(self) -> str:
        """String representation."""
        return (f"OptionMetric<{self.to_dict()}>")


class OptionUtil:
    """
    Utility class for fetching option market data and calculating option metrics.
    
    This class integrates QuoteClient to fetch real-time option quotes and uses
    various calculators to compute Greeks, probabilities, and other option metrics.
    """
    
    def __init__(self, quote_client: QuoteClient, trade_client: Optional[TradeClient] = None):
        """
        Initialize OptionUtil with a QuoteClient instance.
        
        Args:
            quote_client: Configured QuoteClient instance for fetching market data
            trade_client: Optional TradeClient instance for fetching contract margin data
        """
        self.quote_client = quote_client
        self.trade_client = trade_client
        self.probability_calculator = ProbabilityCalculator()
        self.extra_calculator = ExtraCalculator()
        
        if ql is None:
            raise ImportError("QuantLib is required for this module. Please install QuantLib>=1.40")
    
    def get_option_metrics(self,
                          identifiers: Union[str, List[str]],
                          underlying_price: Optional[float] = None,
                          risk_free_rate: float = 0.03,
                          dividend_rate: Optional[float] = None,
                          is_european: bool = False,
                          reference_date: Optional[ql.Date] = None,
                          market: str = 'US',
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
            market: Market code (US/HK)
            timezone: Timezone for date processing
            return_type: Return format - 'dataframe' (default) for pandas DataFrame or 'list' for list of OptionMetric objects
            
        Returns:
            If return_type='dataframe': pandas.DataFrame with columns:
                - All fields from get_option_briefs (price, Greeks, etc.)
                - delta, gamma, theta, vega, rho (calculated)
                - npv (Net Present Value)
                - implied_vol (implied volatility)
                - leverage_ratio
                - annualized_leveraged_sell_return
                - profit_probability (long position)
                
            If return_type='list': List[OptionMetric] objects containing all calculated metrics
        """
        # Fetch option quotes
        briefs = self.quote_client.get_option_briefs(identifiers, market=market, timezone=timezone)
        
        if briefs is None or briefs.empty:
            error_msg = f"No option data returned for identifiers: {identifiers}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Get unique underlying symbols
        underlying_symbols = briefs['symbol'].unique().tolist()
        
        # Fetch underlying stock prices if not provided
        underlying_prices = {}
        if underlying_price is None and underlying_symbols:
            stock_briefs = self.quote_client.get_stock_briefs(underlying_symbols)
            if stock_briefs is None or stock_briefs.empty:
                error_msg = f"No stock data returned for symbols: {underlying_symbols}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            for _, row in stock_briefs.iterrows():
                symbol = row.get('symbol')
                latest_price = row.get('latest_price')
                if symbol and not pd.isna(latest_price):
                    underlying_prices[symbol] = float(latest_price)
            logger.debug(f"Fetched underlying prices: {underlying_prices}")
        
        # Fetch dividend rates for underlying symbols if not provided
        dividend_rates = {}
        if dividend_rate is None and underlying_symbols:
            # Fetch fundamental data
            fundamental_data = self.quote_client.get_stock_fundamental(
                underlying_symbols, 
                market=market
            )
            
            if fundamental_data is None or fundamental_data.empty:
                error_msg = f"No fundamental data returned for symbols: {underlying_symbols}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Extract dividend rates
            for _, row in fundamental_data.iterrows():
                symbol = row.get('symbol')
                div_rate = row.get('divide_rate', 0.0)
                if symbol and not pd.isna(div_rate):
                    dividend_rates[symbol] = float(div_rate)
        
        # Set reference date
        if reference_date is None:
            today = datetime.today() - timedelta(days=1)
            reference_date = ql.Date(today.day, today.month, today.year)
        
        ql.Settings.instance().evaluationDate = reference_date
        
        # Initialize result columns
        briefs['underlying_price'] = None
        briefs['delta'] = None
        briefs['gamma'] = None
        briefs['theta'] = None
        briefs['vega'] = None
        briefs['rho'] = None
        briefs['npv'] = None
        briefs['implied_vol'] = None
        briefs['leverage_ratio'] = None
        briefs['annualized_leveraged_sell_return'] = None
        briefs['profit_probability'] = None
        
        # Calculate metrics for each option
        for idx, row in briefs.iterrows():
            # Extract option parameters first to get underlying symbol
            underlying_symbol = row.get('symbol', '')
            
            # Determine underlying price
            if underlying_price is not None:
                current_underlying = underlying_price
            else:
                # Get underlying price from fetched stock prices
                current_underlying = underlying_prices.get(underlying_symbol, None)
                
            if current_underlying is None or pd.isna(current_underlying):
                logger.warning(f"Skipping {row.get('identifier', 'unknown')}: no underlying price available")
                continue
            current_underlying = float(current_underlying)
            
            # Store underlying price in result
            briefs.loc[idx, 'underlying_price'] = current_underlying

            # Extract option parameters
            strike = row.get('strike', 0)
            if strike is None or pd.isna(strike):
                logger.warning(f"Skipping {row.get('identifier', 'unknown')}: invalid strike price")
                continue
            strike = float(strike)
            
            put_call = row.get('put_call', 'CALL')
            expiry_timestamp = row.get('expiry', 0)
            if expiry_timestamp is None or pd.isna(expiry_timestamp):
                logger.warning(f"Skipping {row.get('identifier', 'unknown')}: invalid expiry")
                continue
            expiry_timestamp = int(expiry_timestamp)
            
            multiplier = row.get('multiplier', 100)
            if multiplier is None or pd.isna(multiplier):
                multiplier = 100
            multiplier = int(multiplier)

            # Get dividend rate for this underlying
            if dividend_rate is not None:
                current_dividend_rate = float(dividend_rate)
            else:
                current_dividend_rate = float(dividend_rates.get(underlying_symbol, 0.0))

            # Calculate days to expiry
            expiry_date = self._timestamp_to_ql_date(expiry_timestamp)
            days_to_expiry = expiry_date - reference_date

            if days_to_expiry <= 0:
                continue

            # Get option type
            option_type = ql.Option.Call if put_call == 'CALL' else ql.Option.Put

            # Get market data for calculations
            raw_mark_price = row.get('mark_price')
            mark_price = float(raw_mark_price) if raw_mark_price and not pd.isna(raw_mark_price) else None

            raw_latest_price = row.get('latest_price')
            latest_price_value = float(raw_latest_price) if raw_latest_price and not pd.isna(raw_latest_price) else None

            # Determine option price for calculations (mark -> latest fallback)
            option_price = mark_price if mark_price is not None else (latest_price_value if latest_price_value is not None else 0.0)

            if option_price <= 0:
                continue

            # Get or use provided rates
            rf_rate = row.get('rates_bonds', risk_free_rate)
            if pd.isna(rf_rate):
                rf_rate = risk_free_rate
            else:
                rf_rate = float(rf_rate)
            
            logger.debug(f"Calculating metrics for {row.get('identifier', 'unknown')}:")
            logger.debug(f"  Underlying: {underlying_symbol} @ {current_underlying:.2f}")
            logger.debug(f"  Strike: {strike:.2f}, Type: {put_call}, Days to expiry: {days_to_expiry}")
            logger.debug(f"  Option price: {option_price:.4f}")
            logger.debug(f"  Risk-free rate: {rf_rate:.4f}")
            logger.debug(f"  Dividend rate: {current_dividend_rate:.4f}")
            logger.debug(f"  Reference date: {reference_date}")

            helper_class = FDEuropeanDividendOptionHelper if is_european else FDAmericanDividendOptionHelper
            helper = helper_class(
                option_type=option_type,
                underlying=current_underlying,
                strike=strike,
                risk_free_rate=rf_rate,
                dividend_rate=current_dividend_rate,
                volatility=0,
                settlement_date=reference_date,
                expiration_date=expiry_date
            )

            # Calculate implied volatility
            try:
                implied_vol = helper.implied_volatility(option_price)
                helper.update_implied_volatility(implied_vol)
                briefs.loc[idx, 'implied_vol'] = implied_vol
            except Exception as e:
                logger.warning(
                    "  Implied vol solve failed (%s); skipping metrics for %s",
                    e,
                    row.get('identifier', 'unknown')
                )
                continue

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
            
            option_identifier = row.get('identifier', '')
            currency = row.get('currency', 'USD')
            sell_margin = self._calculate_sell_margin(
                underlying_symbol=underlying_symbol,
                strike=strike,
                put_call=put_call,
                multiplier=multiplier,
                expiry_timestamp=expiry_timestamp,
                current_underlying=current_underlying,
                option_identifier=option_identifier,
                currency=currency,
                mark_price=mark_price,
                option_price=option_price
            )

            ann_return = self.extra_calculator.annualized_leveraged_sell_return(
                time_value, sell_margin, days_to_expiry, multiplier
            )
            briefs.loc[idx, 'annualized_leveraged_sell_return'] = ann_return

            # Calculate profit probability for long position
            profit_prob = self.probability_calculator.probability_long_profit(
                stock_price=current_underlying,
                strike=strike,
                premium=option_price,
                iv=implied_vol,
                days=days_to_expiry,
                option_type=put_call,
            )
            briefs.loc[idx, 'profit_probability'] = profit_prob
        
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
                underlying_price=row['underlying_price'] if 'underlying_price' in row else None,
                delta=row['delta'] if 'delta' in row else None,
                gamma=row['gamma'] if 'gamma' in row else None,
                theta=row['theta'] if 'theta' in row else None,
                vega=row['vega'] if 'vega' in row else None,
                rho=row['rho'] if 'rho' in row else None,
                npv=row['npv'] if 'npv' in row else None,
                implied_vol=row['implied_vol'] if 'implied_vol' in row else None,
                leverage_ratio=row['leverage_ratio'] if 'leverage_ratio' in row else None,
                annualized_leveraged_sell_return=row['annualized_leveraged_sell_return'] if 'annualized_leveraged_sell_return' in row else None,
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

    def _calculate_sell_margin(self,
                               underlying_symbol: str,
                               strike: float,
                               put_call: str,
                               multiplier: int,
                               expiry_timestamp: int,
                               current_underlying: float,
                               option_identifier: str = '',
                               currency: Optional[str] = 'USD',
                               mark_price: Optional[float] = None,
                               option_price: Optional[float] = None) -> float:
        """Compute sell margin, preferring preview_order delta when available."""
        if self.trade_client is None:
            return self._estimate_sell_margin(put_call, strike, current_underlying, multiplier)

        limit_price = mark_price if mark_price is not None and mark_price > 0 else option_price
        if limit_price is None or limit_price <= 0:
            logger.warning(f"  No valid price for previewing margin on {option_identifier}; using estimate")
            return self._estimate_sell_margin(put_call, strike, current_underlying, multiplier)

        expiry_str = self._timestamp_to_date_str(expiry_timestamp)
        try:
            contract = option_contract_by_symbol(
                symbol=underlying_symbol,
                expiry=expiry_str,
                strike=strike,
                put_call=put_call,
                currency=currency or 'USD',
                multiplier=multiplier
            )
        except Exception as exc:
            logger.warning(f"  Failed to build local contract for {option_identifier}: {exc}")
            return self._estimate_sell_margin(put_call, strike, current_underlying, multiplier)

        preview_margin = self._preview_option_sell_margin(contract, option_identifier, limit_price)
        if preview_margin is not None:
            return preview_margin

        return self._estimate_sell_margin(put_call, strike, current_underlying, multiplier)

    def _preview_option_sell_margin(self,
                                    contract,
                                    option_identifier: str,
                                    limit_price: float) -> Optional[float]:
        if limit_price is None or limit_price <= 0:
            logger.warning(f"  Invalid limit price for {option_identifier}; skipping preview")
            return None

        account = getattr(self.trade_client, '_account', None)
        if not account:
            logger.warning("  TradeClient has no account configured; cannot preview margin")
            return None

        order = limit_order(
            account=account,
            contract=contract,
            action='SELL',
            quantity=1,
            limit_price=limit_price
        )

        try:
            preview = self.trade_client.preview_order(order)
        except Exception as exc:
            logger.warning(f"  preview_order failed for {option_identifier}: {exc}")
            return None

        if not preview:
            return None

        init_before = preview.get('init_margin_before') if isinstance(preview, dict) else getattr(preview, 'init_margin_before', None)
        init_after = preview.get('init_margin') if isinstance(preview, dict) else getattr(preview, 'init_margin', None)

        if init_before is None or init_after is None:
            logger.warning(f"  preview_order returned no init margin data for {option_identifier}")
            return None

        delta = float(init_after) - float(init_before)
        return max(delta, 0.0)

    @staticmethod
    def _estimate_sell_margin(put_call: str,
                              strike: float,
                              current_underlying: float,
                              multiplier: int) -> float:
        sell_margin = strike * multiplier if put_call == 'PUT' else current_underlying * multiplier
        logger.debug(f"  Using estimated sell_margin: {sell_margin}")
        return sell_margin

    def _timestamp_to_ql_date(self, timestamp_ms: int) -> ql.Date:
        """Convert millisecond timestamp to QuantLib Date."""
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
        return ql.Date(dt.day, dt.month, dt.year)
    
    def _timestamp_to_date_str(self, timestamp_ms: int) -> str:
        """Convert millisecond timestamp to date string in YYYYMMDD format."""
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
        return dt.strftime('%Y%m%d')


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.max_rows', 5000)
    pd.set_option('display.width', 5000)
    # Example usage (requires configured QuoteClient)
    from tigeropen.tiger_open_config import TigerOpenClientConfig

    # Configure client with your properties file
    client_config = TigerOpenClientConfig(props_path='../../../tests/.config/prod/')
    quote_client = QuoteClient(client_config)
    trade_client = TradeClient(client_config)

    option_util = OptionUtil(quote_client, trade_client)

    # Calculate metrics for specific options
    identifiers = ['TSLA 260220C00385000']

    # Example 1: Return as DataFrame
    logger.info("Example 1: Return as DataFrame")
    metrics_df = option_util.get_option_metrics(identifiers, return_type='dataframe')
    logger.info(f"\n{metrics_df}")

    # Example 2: Return as List of OptionMetric objects
    logger.info("Example 2: Return as List of OptionMetric objects")
    metrics_list = option_util.get_option_metrics(identifiers, return_type='list')
    for metric in metrics_list:
        logger.info(metric)
        logger.info(f"  Greeks: delta={metric.delta}, gamma={metric.gamma}, "
              f"theta={metric.theta}, vega={metric.vega}")
        logger.info(f"  Risk: implied_vol={metric.implied_vol}, leverage={metric.leverage_ratio}")
        logger.info(f"  Probability: profit_prob={metric.profit_probability}")
