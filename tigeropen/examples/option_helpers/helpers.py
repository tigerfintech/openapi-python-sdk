# -*- coding: utf-8 -*-
# Helpers for calculating the Greeks of options
# @Date    : 2022/4/15
# @Author  : sukai
import argparse
from typing import List

try:
    import QuantLib as ql
except ImportError:
    pass


class FDDividendOptionHelper(ql.DividendVanillaOption):
    def __init__(self,
                 engine_class,
                 option_type: ql.Option,
                 underlying: float,
                 strike: float,
                 risk_free_rate: float,
                 dividend_rate: float,
                 volatility: float,
                 reference_date: ql.Date,
                 exercise: ql.Exercise,
                 dates: List[ql.Date] = None,
                 dividends: List[float] = None,
                 calendar: ql.Calendar = ql.NullCalendar(),
                 day_counter: ql.DayCounter = ql.Actual365Fixed()
                 ):
        self.dates = dates if dates is not None else list()
        self.dividends = dividends if dividends is not None else list()
        super(FDDividendOptionHelper, self).__init__(ql.PlainVanillaPayoff(option_type, strike), exercise, self.dates,
                                                     self.dividends)

        self.option_type = option_type
        self.underlying = underlying
        self.strike = strike
        self.risk_free_rate = risk_free_rate
        self.dividend_rate = dividend_rate
        self.volatility = volatility
        self.reference_date = reference_date
        self.exercise = exercise
        self.calendar = calendar
        self.day_counter = day_counter
        self.engine_class = engine_class
        self.bsm_process: ql.GeneralizedBlackScholesProcess
        self.underlying_quote = ql.SimpleQuote(underlying)
        self.risk_free_rate_quote = ql.SimpleQuote(risk_free_rate)
        self.dividend_rate_quote = ql.SimpleQuote(dividend_rate)
        self.volatility_quote = ql.SimpleQuote(volatility)

        self.setPricingEngine(self.get_engine(reference_date))

    def get_engine(self, date: ql.Date) -> ql.PricingEngine:
        spot_handle = ql.QuoteHandle(self.underlying_quote)
        risk_free_rate_handle = ql.QuoteHandle(self.risk_free_rate_quote)
        volatility_handle = ql.QuoteHandle(self.volatility_quote)

        r_ts = ql.YieldTermStructureHandle(ql.FlatForward(date, risk_free_rate_handle, self.day_counter))
        vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(date, self.calendar, volatility_handle,
                                                                    self.day_counter))

        if self.dividend_rate is not None:
            dividend_handle = ql.QuoteHandle(self.dividend_rate_quote)
            d_ts = ql.YieldTermStructureHandle(ql.FlatForward(date, dividend_handle, self.day_counter))
            self.bsm_process = ql.BlackScholesMertonProcess(spot_handle,
                                                            d_ts,
                                                            r_ts,
                                                            vol_ts)
        else:
            self.bsm_process = ql.BlackScholesProcess(spot_handle,
                                                      r_ts,
                                                      vol_ts)

        return self.engine_class(self.bsm_process)

    def theta(self) -> float:
        yesterday = self.reference_date - ql.Period(1, ql.Days)
        tomorrow = self.reference_date + ql.Period(1, ql.Days)
        if self.exercise.lastDate() == tomorrow:
            dt = self.day_counter.yearFraction(yesterday, self.reference_date)
        else:
            dt = self.day_counter.yearFraction(yesterday, tomorrow)
            self.setPricingEngine(self.get_engine(tomorrow))
        value_p = self.NPV()
        self.setPricingEngine(self.get_engine(yesterday))
        value_m = self.NPV()

        theta = (value_p - value_m) / dt
        self.setPricingEngine(self.get_engine(self.reference_date))
        return theta / ql.Daily

    def vega(self) -> float:
        return self.numeric_first_order(self.volatility_quote)

    def rho(self) -> float:
        return self.numeric_first_order(self.risk_free_rate_quote)

    def implied_volatility(self, price: float, accuracy: float = 1.0e-4, max_evaluations: int = 100,
                           min_vol: float = 1.0e-7, max_vol: float = 4.0, try_times: int = 4) -> float:
        """

        :param price: expected option NPV
        :param accuracy:
        :param max_evaluations:
        :param min_vol:
        :param max_vol:
        :param try_times:
        :return:
        """
        try:
            return self.impliedVolatility(price, self.bsm_process, accuracy, max_evaluations, min_vol, max_vol)
        except RuntimeError as e:
            if try_times == 0:
                return 0
            elif 'root not bracketed' in str(e):
                return self.implied_volatility(price, accuracy, max_evaluations, min_vol, max_vol * 2, try_times - 1)
            else:
                raise e

    def update_implied_volatility(self, implied_volatility: float):
        self.volatility_quote.setValue(implied_volatility)

    def numeric_first_order(self, quote: ql.SimpleQuote) -> float:
        """
        reference: https://github.com/lballabio/QuantLib/issues/779
        https://github.com/frgomes/jquantlib/blob/master/jquantlib-helpers/src/main/java/org/jquantlib/helpers/FDDividendOptionHelper.java
        :param self:
        :param quote:
        :return:
        """
        sigma0 = quote.value()
        h = sigma0 * 1E-4
        quote.setValue(sigma0 - h)
        p_minus = self.NPV()
        quote.setValue(sigma0 + h)
        p_plus = self.NPV()
        quote.setValue(sigma0)
        return (p_plus - p_minus) / (2 * h) / 100


class FDAmericanDividendOptionHelper(FDDividendOptionHelper):
    """American option"""

    def __init__(self,
                 option_type: ql.Option,
                 underlying: float,
                 strike: float,
                 risk_free_rate: float,
                 dividend_rate: float,
                 volatility: float,
                 settlement_date: ql.Date,
                 expiration_date: ql.Date,
                 dates: List[ql.Date] = None,
                 dividends: List[float] = None,
                 calendar: ql.Calendar = ql.NullCalendar(),
                 day_counter: ql.DayCounter = ql.Actual365Fixed(),
                 engine_class: ql.PricingEngine.__class__ = ql.FdBlackScholesVanillaEngine
                 ):
        """

        :param option_type: ql.Option.Call or ql.Option.Put
        :param underlying:
        :param strike:
        :param risk_free_rate:
        :param dividend_rate:
        :param volatility:
        :param settlement_date:
        :param expiration_date:
        :param dates:
        :param dividends:
        :param calendar:
        :param day_counter:
        :param engine_class:

        >>> helper = FDAmericanDividendOptionHelper(ql.Option.Call, 985, 990, 0.017, 0, 0.6153, ql.Date(14, 4, 2022), ql.Date(22, 4, 2022))
        >>> print(f'value:{helper.NPV()}')
        >>> print(f'delta:{helper.delta()}')
        >>> print(f'gamma:{helper.gamma()}')
        >>> print(f'theta:{helper.theta()}')
        >>> print(f'vega:{helper.vega()}')
        >>> print(f'rho:{helper.rho()}')
        """
        super(FDAmericanDividendOptionHelper, self).__init__(engine_class=engine_class,
                                                             option_type=option_type, underlying=underlying,
                                                             strike=strike, risk_free_rate=risk_free_rate,
                                                             dividend_rate=dividend_rate, volatility=volatility,
                                                             reference_date=settlement_date,
                                                             exercise=ql.AmericanExercise(settlement_date,
                                                                                          expiration_date),
                                                             dates=dates, dividends=dividends, calendar=calendar,
                                                             day_counter=day_counter)


class FDEuropeanDividendOptionHelper(FDDividendOptionHelper):
    """European option"""

    def __init__(self,
                 option_type: ql.Option,
                 underlying: float,
                 strike: float,
                 risk_free_rate: float,
                 dividend_rate: float,
                 volatility: float,
                 settlement_date: ql.Date,
                 expiration_date: ql.Date,
                 dates: List[ql.Date] = None,
                 dividends: List[float] = None,
                 calendar: ql.Calendar = ql.NullCalendar(),
                 day_counter: ql.DayCounter = ql.Actual365Fixed(),
                 engine_class: ql.PricingEngine.__class__ = ql.FdBlackScholesVanillaEngine
                 ):
        super(FDEuropeanDividendOptionHelper, self).__init__(engine_class=engine_class,
                                                             option_type=option_type, underlying=underlying,
                                                             strike=strike, risk_free_rate=risk_free_rate,
                                                             dividend_rate=dividend_rate, volatility=volatility,
                                                             reference_date=settlement_date,
                                                             exercise=ql.EuropeanExercise(expiration_date),
                                                             dates=dates, dividends=dividends, calendar=calendar,
                                                             day_counter=day_counter)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Helpers for calculating the Greeks of options')

    parser.add_argument('-t', '--type', type=str,
                        help='Option type, CALL/PUT (C/P)', choices=('C', 'P', 'CALL', 'PUT'))
    parser.add_argument('-u', '--underlying', type=float,
                        help='The price of the underlying asset')
    parser.add_argument('-p', '--strike', type=float,
                        help='The strike price at expiration')
    parser.add_argument('-d', '--dividend', type=float, nargs='?', default=0,
                        help='The dividend rate')
    parser.add_argument('-r', '--rfrate', type=float, nargs='?', default=0.01,
                        help='The risk free rate')
    parser.add_argument('-v', '--volatility', type=float, nargs='?', default=0,
                        help='The implied volatility')
    parser.add_argument('-s', '--settlement', type=str,
                        help='The settlement date, like "2022-04-22"')
    parser.add_argument('-e', '--expiration', type=str,
                        help='The expiration date, like "2022-04-29"')
    parser.add_argument('-n', '--npv', type=float, nargs='?',
                        help='The expected NPV of option')
    parser.add_argument('-a', '--ask', type=float, nargs='?',
                        help='The ask price of option')
    parser.add_argument('-b', '--bid', type=float, nargs='?',
                        help='The bid price of option')
    parser.add_argument('-o', '--european', action='store_true',
                        help='Is european option')

    args = parser.parse_args()

    if args.type.upper() in ('C', 'CALL'):
        ql_option_type = ql.Option.Call
    elif args.type.upper() in ('P', 'PUT'):
        ql_option_type = ql.Option.Put
    else:
        parser.error('Wrong option type')
    if args.volatility is None and args.npv is None and args.ask is None and args.bid is None:
        parser.error('Must specify the volatility or option npv(or option\'s ask, bid)')

    print(args.__dict__)
    settlement_date = ql.DateParser.parseFormatted(str(args.settlement).replace('/', '-'), '%Y-%m-%d')
    expiration_date = ql.DateParser.parseFormatted(str(args.expiration).replace('/', '-'), '%Y-%m-%d')

    if args.european:
        helper_class = FDEuropeanDividendOptionHelper
    else:
        helper_class = FDAmericanDividendOptionHelper

    ql.Settings.instance().evaluationDate = settlement_date
    helper = helper_class(option_type=ql_option_type,
                          underlying=args.underlying,
                          strike=args.strike,
                          risk_free_rate=args.rfrate,
                          dividend_rate=args.dividend,
                          volatility=args.volatility,
                          settlement_date=settlement_date,
                          expiration_date=expiration_date)

    if args.volatility is None or args.volatility == 0:
        expected_npv = None
        npv_msg = ''
        if args.ask and args.bid:
            expected_npv = (args.ask + args.bid) / 2
            npv_msg = f'with ask {args.ask}, bid {args.bid}, expected_npv {expected_npv}'
        else:
            expected_npv = args.npv
            npv_msg = f'with expected npv: {expected_npv}'

        volatility = helper.implied_volatility(expected_npv)
        helper.update_implied_volatility(volatility)
        print(f'The implied volatility {npv_msg} is: {volatility}')

    print(f'npv: {helper.NPV()}, delta:{helper.delta()}, gamma:{helper.gamma()}, theta:{helper.theta()}, '
          f'vega:{helper.vega()}, rho:{helper.rho()}')
