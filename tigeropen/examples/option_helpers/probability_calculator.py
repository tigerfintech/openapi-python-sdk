from __future__ import annotations

import math
try:
    from scipy.stats import norm
except ImportError as e:
    raise ImportError("scipy is required for this module to work. Please install scipy.") from e


class ProbabilityCalculator:
    """Helper for probability calculations related to underlying price moves.

    Methods mirror the original C++ implementation and use the log-normal model
    where z = ln(target_price/current_price) / (iv * sqrt(days/365)).
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def _normal_cdf(x: float) -> float:
        """Standard normal cumulative distribution function."""
        return float(norm.cdf(x))

    @staticmethod
    def _inv_normal_cdf(p: float) -> float:
        """Inverse standard normal CDF (quantile function).

        Returns NaN if input is NaN.
        """
        if math.isnan(p):
            return float("nan")
        return float(norm.ppf(p))

    def cumulative_probability(self, stock_price: float, target_price: float, iv: float, days: float) -> float:
        """Compute cumulative probability that price moves from stock_price to target_price within days.

        Parameters
        ----------
        stock_price : float
            Current/latest price (must be > 0).
        target_price : float
            Target price (must be > 0).
        iv : float
            Implied volatility (annualized, e.g. 0.2 for 20%).
        days : float
            Time horizon in days.

        Returns
        -------
        float
            Probability that the log-return scaled by iv*sqrt(days/365) is <= target.
        """
        if iv == 0:
            return 1.0 if target_price > stock_price else 0.0
        try:
            z = math.log(target_price / stock_price) / (iv * math.sqrt(days / 365.0))
        except Exception:
            return float("nan")
        return self._normal_cdf(z)

    def probability(self, stock_price: float, lower_price: float, upper_price: float, iv: float, days: float) -> float:
        """Probability that price will be between lower_price and upper_price after days.

        This is P(lower_price < S_t <= upper_price) under the log-normal approximation.

        Parameters
        ----------
        stock_price : float
            Latest/current underlying price (spot). Expected > 0.
        lower_price : float
            Lower bound target price. The function returns probability that S_t > lower_price.
        upper_price : float
            Upper bound target price. The function returns probability that S_t <= upper_price.
        iv : float
            Implied volatility (annualized, e.g. 0.2 for 20%). Used as the
            scale for log-returns: iv * sqrt(time/365).
        days : float
            Time horizon in days.

        Returns
        -------
        float
            Probability that the underlying price at horizon `days` lies in
            (lower_price, upper_price] under the log-normal approximation. Returns NaN if inputs
            are invalid (e.g. non-positive prices) or if computation fails.
        """
        return self.cumulative_probability(stock_price, upper_price, iv, days) - self.cumulative_probability(stock_price, lower_price, iv, days)

    def calc_z_value_from_probability(self, probability: float) -> float:
        """Convert a two-sided central probability to a positive z-value.

        The input `probability` is the central probability (e.g. 0.95 for 95%).
        We convert it to a one-sided tail and return the corresponding positive z.
        """
        if probability is None or math.isnan(probability):
            return 1.0
        p = probability
        if p >= 1.0:
            p = 0.99999999
        tail = (1.0 - p) / 2.0
        return abs(self._inv_normal_cdf(tail))

    def probability_long_profit(self, stock_price: float, strike: float, premium: float, iv: float, days: float, option_type: str = "CALL") -> float:
        """Probability that a long option (CALL or PUT) will be profitable at expiry.

        Parameters
        ----------
        stock_price : float
            Current underlying price.
        strike : float
            Option strike price.
        premium : float
            Option premium per contract unit.
        iv : float
            Annualized implied volatility (decimal).
        days : float
            Time to expiry in days.
        option_type : str
            Either 'CALL' or 'PUT' (case-insensitive).
        """
        if stock_price is None or strike is None or premium is None or iv is None or days == 0:
            return float("nan")
        try:
            premium_per_unit = float(premium)
        except Exception:
            return float("nan")

        opt = (option_type or "").strip().upper()
        if opt == "CALL":
            breakeven = strike + premium_per_unit
            return 1.0 - self.cumulative_probability(stock_price, breakeven, iv, days)
        elif opt == "PUT":
            breakeven = strike - premium_per_unit
            if breakeven <= 0:
                return 0.0
            return self.cumulative_probability(stock_price, breakeven, iv, days)
        else:
            raise ValueError("option_type must be 'CALL' or 'PUT'.")

    def calc_future_price_delta(self, latest_price: float, volatility: float, future_days: int, z_value: float) -> float:
        """Estimate absolute price delta: z * price * vol * sqrt(days/365).

        Parameters
        ----------
        latest_price : float
            Current/latest underlying price.
        volatility : float
            Annualized volatility (decimal, e.g. 0.2).
        future_days : int
            Horizon in days.
        z_value : float
            Z-value (e.g. from calc_z_value_from_probability).
        """
        if latest_price is None or volatility is None or math.isnan(latest_price) or math.isnan(volatility) or future_days == 0:
            return 0.0
        return z_value * latest_price * volatility * math.sqrt(future_days / 365.0)

    def calc_below_price_probability(self, latest_price: float, price: float, volatility: float, future_days: int, z_value: float) -> float:
        """Probability the underlying will be below `price` after `future_days`.

        the standard-normal CDF of the appropriately scaled log-ratio.
        """
        if (latest_price is None or math.isnan(latest_price) or abs(latest_price) <= 1e-12
                or abs(volatility) <= 1e-12 or math.isnan(volatility) or future_days == 0):
            return float("nan")
        try:
            factor1 = math.log(price / latest_price)
        except Exception:
            return float("nan")
        factor2 = math.sqrt(future_days / 365.0)
        result = factor1 / (volatility * factor2 * z_value)
        return self._normal_cdf(result)


__all__ = ["ProbabilityCalculator"]


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point for quick calculations.

        Subcommands:
            cumulative -- compute cumulative_probability
            range      -- compute probability (between q1 and q2)
            z          -- compute z from central probability
            delta      -- compute future price delta
            below      -- compute probability price will be below a level
            long_profit -- compute long option (CALL/PUT) profit probability at expiry
    """
    import argparse

    parser = argparse.ArgumentParser(prog="probability_calculator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_cum = sub.add_parser("cumulative", help="Compute cumulative_probability")
    p_cum.add_argument("stock_price", type=float)
    p_cum.add_argument("target_price", type=float)
    p_cum.add_argument("iv", type=float)
    p_cum.add_argument("days", type=float)

    p_range = sub.add_parser("range", help="Compute probability between lower_price and upper_price")
    p_range.add_argument("stock_price", type=float)
    p_range.add_argument("lower_price", type=float)
    p_range.add_argument("upper_price", type=float)
    p_range.add_argument("iv", type=float)
    p_range.add_argument("days", type=float)

    p_z = sub.add_parser("z", help="Compute z from central probability")
    p_z.add_argument("prob", type=float)

    p_delta = sub.add_parser("delta", help="Compute future price delta")
    p_delta.add_argument("latest_price", type=float)
    p_delta.add_argument("volatility", type=float)
    p_delta.add_argument("future_days", type=int)
    p_delta.add_argument("z_value", type=float)

    p_below = sub.add_parser("below", help="Compute probability price will be below a level")
    p_below.add_argument("latest_price", type=float)
    p_below.add_argument("price", type=float)
    p_below.add_argument("volatility", type=float)
    p_below.add_argument("future_days", type=int)
    p_below.add_argument("z_value", type=float)

    p_opt = sub.add_parser("long_profit", help="Compute long option (CALL/PUT) profit probability at expiry")
    p_opt.add_argument("stock_price", type=float)
    p_opt.add_argument("strike", type=float)
    p_opt.add_argument("premium", type=float)
    p_opt.add_argument("iv", type=float)
    p_opt.add_argument("days", type=float)
    p_opt.add_argument("option_type", type=str, choices=["CALL", "PUT"])

    args = parser.parse_args(argv)
    pc = ProbabilityCalculator()

    if args.cmd == "cumulative":
        out = pc.cumulative_probability(args.stock_price, args.target_price, args.iv, args.days)
    elif args.cmd == "range":
        out = pc.probability(args.stock_price, args.lower_price, args.upper_price, args.iv, args.days)
    elif args.cmd == "z":
        out = pc.calc_z_value_from_probability(args.prob)
    elif args.cmd == "delta":
        out = pc.calc_future_price_delta(args.latest_price, args.volatility, args.future_days, args.z_value)
    elif args.cmd == "below":
        out = pc.calc_below_price_probability(args.latest_price, args.price, args.volatility, args.future_days, args.z_value)
    elif args.cmd == "long_profit":
        out = pc.probability_long_profit(args.stock_price, args.strike, args.premium, args.iv, args.days, args.option_type)
    else:
        parser.print_help()
        return 2

    if isinstance(out, float):
        # Print with reasonable precision
        print(out)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    stock_price = 240.52
    strike = 240.0
    premium = 6.76
    iv = 0.7109
    days = 4
    option_type = "PUT"
    pc = ProbabilityCalculator()
    buy_call_prob = pc.probability_long_profit(stock_price, strike=strike, premium=premium, iv=iv, days=days, option_type=option_type)
    print(f"Probability that a {option_type} option with strike={strike} and premium={premium} will be profitable at expiry in {days} days: {buy_call_prob:.4f}"
    )
    # raise SystemExit(main())
