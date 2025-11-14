from __future__ import annotations

import math
from scipy.stats import norm


class ProbabilityCalculator:
    """Helper for probability calculations related to underlying price moves.

    Methods mirror the original C++ implementation and use the log-normal model
    where z = ln(q/p) / (iv * sqrt(time/365)).
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

    def cumulative_probability(self, p: float, q: float, iv: float, time: float) -> float:
        """Compute cumulative probability that price moves from p to q within time days.

        Parameters
        ----------
        p : float
            Current/latest price (must be > 0).
        q : float
            Target price (must be > 0).
        iv : float
            Implied volatility (annualized, e.g. 0.2 for 20%).
        time : float
            Time horizon in days.

        Returns
        -------
        float
            Probability that the log-return scaled by iv*sqrt(time/365) is <= target.
        """
        if iv == 0:
            return 1.0 if q > p else 0.0
        try:
            z = math.log(q / p) / (iv * math.sqrt(time / 365.0))
        except Exception:
            return float("nan")
        return self._normal_cdf(z)

    def probability(self, p: float, q1: float, q2: float, iv: float, time: float) -> float:
        """Probability that price will be between q1 and q2 after time days.

        This is P(q1 < S_t <= q2) under the log-normal approximation.

        Parameters
        ----------
        p : float
            Latest/current underlying price (spot). Expected > 0.
        q1 : float
            Lower bound target price. The function returns probability that S_t > q1.
        q2 : float
            Upper bound target price. The function returns probability that S_t <= q2.
        iv : float
            Implied volatility (annualized, e.g. 0.2 for 20%). Used as the
            scale for log-returns: iv * sqrt(time/365).
        time : float
            Time horizon in days.

        Returns
        -------
        float
            Probability that the underlying price at horizon `time` lies in
            (q1, q2] under the log-normal approximation. Returns NaN if inputs
            are invalid (e.g. non-positive prices) or if computation fails.
        """
        return self.cumulative_probability(p, q2, iv, time) - self.cumulative_probability(p, q1, iv, time)

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

        This function follows the algebra from the C++ implementation and returns
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
    """
    import argparse

    parser = argparse.ArgumentParser(prog="probability_calculator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_cum = sub.add_parser("cumulative", help="Compute cumulative_probability")
    p_cum.add_argument("p", type=float)
    p_cum.add_argument("q", type=float)
    p_cum.add_argument("iv", type=float)
    p_cum.add_argument("time", type=float)

    p_range = sub.add_parser("range", help="Compute probability between q1 and q2")
    p_range.add_argument("p", type=float)
    p_range.add_argument("q1", type=float)
    p_range.add_argument("q2", type=float)
    p_range.add_argument("iv", type=float)
    p_range.add_argument("time", type=float)

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

    args = parser.parse_args(argv)
    pc = ProbabilityCalculator()

    if args.cmd == "cumulative":
        out = pc.cumulative_probability(args.p, args.q, args.iv, args.time)
    elif args.cmd == "range":
        out = pc.probability(args.p, args.q1, args.q2, args.iv, args.time)
    elif args.cmd == "z":
        out = pc.calc_z_value_from_probability(args.prob)
    elif args.cmd == "delta":
        out = pc.calc_future_price_delta(args.latest_price, args.volatility, args.future_days, args.z_value)
    elif args.cmd == "below":
        out = pc.calc_below_price_probability(args.latest_price, args.price, args.volatility, args.future_days, args.z_value)
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
    raise SystemExit(main())
