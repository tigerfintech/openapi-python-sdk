from __future__ import annotations

import math
from typing import Optional


class ExtraCalculator:
    """Utility class containing leverage-related calculation methods."""

    @staticmethod
    def annualized_levered_sell_return(option_time_value: float,
                                       sell_margin: float,
                                       days_to_expiry: int,
                                       n_contracts: int = 1) -> float:
        """Calculate annualized levered sell return (for covered calls or cash-secured puts).

        Formula (applies to both calls and puts):
            Annualized Return = (Time Value * N_contracts / Margin) * 365 / Days to Expiry

        Parameters
        ----------
        option_time_value : float
            Time value (premium) received per contract (per underlying unit if margin is per unit).
        sell_margin : float
            Total sell margin required per option (per contract).
        days_to_expiry : int
            Days until expiry.
        n_contracts : int
            Number of contracts sold (default 1).
        """
        try:
            if days_to_expiry <= 0 or sell_margin <= 0 or n_contracts <= 0:
                return float("nan")
            numerator = option_time_value * n_contracts
            annualized = numerator / sell_margin * 365.0 / float(days_to_expiry)
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
    # n_contracts = number of contracts sold
    print("Example annualized levered sell return:", ExtraCalculator.annualized_levered_sell_return(6.76, 6.76, 4, n_contracts=1))
    print("Example leverage ratio:", ExtraCalculator.leverage_ratio(0.472, 240.52, 6.76))
