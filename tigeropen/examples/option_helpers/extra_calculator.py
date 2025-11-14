from __future__ import annotations

import math
from typing import Optional


class ExtraCalculator:
    """Utility class containing leverage-related calculation methods."""

    @staticmethod
    def annualized_levered_sell_return(option_time_value: float,
                                       contracts: int,
                                       margin_per_option: float,
                                       days_to_expiry: int) -> float:
        """Calculate annualized levered sell return (for covered calls or cash-secured puts).

        Formula (applies to both calls and puts):
            Annualized Return = (Time Value * Contracts / Margin) * 365 / Days to Expiry
        """
        try:
            if days_to_expiry <= 0 or margin_per_option <= 0 or contracts <= 0:
                return float("nan")
            numerator = option_time_value * contracts
            annualized = numerator / margin_per_option * 365.0 / float(days_to_expiry)
            return float(annualized)
        except Exception:
            return float("nan")

    @staticmethod
    def leverage_ratio(delta: float, underlying_price: float, option_price: float) -> Optional[float]:
        """Calculate leverage ratio: delta * underlying_price / option_price.

        Returns NaN when option_price is 0 or inputs are invalid.
        """
        try:
            if option_price == 0 or math.isnan(delta) or math.isnan(underlying_price) or math.isnan(option_price):
                return float("nan")
            return float(delta * underlying_price / option_price)
        except Exception:
            return float("nan")


if __name__ == "__main__":
    # Simple example (for smoke testing only)
    print("Example annualized levered sell return:", ExtraCalculator.annualized_levered_sell_return(1.5, 1, 1000.0, 30))
    print("Example leverage ratio:", ExtraCalculator.leverage_ratio(0.5, 50.0, 2.0))
