import decimal
from collections import deque
import tinvest
from copy import deepcopy
from datetime import datetime
import datetime as date_time
import classes_to_portfolio
import datetime_split_day
import time
from test_strategy import indicators


class Stoch_class:
    def __init__(self, periodK : int = 14, periodD : int = 3, smoothK : int = 3):
            self.stoch_deq = deque()
            self.stoch_smooth_deq = deque()
            self.low_deq = deque()
            self.high_deq = deque()
            self.candle = None
            self.periodK = deepcopy(periodK)
            self.periodD = deepcopy(periodD)
            self.smoothK = deepcopy(smoothK)
            self.stochK = 0.0
            self.stochD = 0.0
            self.last_stochK = 0.0
            self.last_stochD = 0.0

    def __deepcopy__(self, memodict):
        my_copy = type(self)(periodK=self.periodK, periodD=self.periodD, smoothK=self.smoothK)
        my_copy.stoch_deq = deepcopy(self.stoch_deq)
        my_copy.stoch_smooth_deq = deepcopy(self.stoch_smooth_deq)
        my_copy.low_deq = deepcopy(self.low_deq)
        my_copy.high_deq = deepcopy(self.high_deq)
        my_copy.candle = deepcopy(self.candle)
        my_copy.stochK = deepcopy(self.stochK)
        my_copy.stochD = deepcopy(self.stochD)
        my_copy.last_stochD = deepcopy(self.last_stochD)
        my_copy.last_stochK = deepcopy(self.last_stochK)
        return my_copy

    def clear(self):
        self.stoch_deq = deque()
        self.stoch_smooth_deq = deque()
        self.low_deq = deque()
        self.high_deq = deque()
        self.candle = None
        self.periodK = self.periodK
        self.periodD = self.periodD
        self.smoothK = self.smoothK
        self.stochK = 0.0
        self.stochD = 0.0
        self.last_stochK = 0.0
        self.last_stochD = 0.0

    def upd_last(self):
        self.last_stochD = deepcopy(self.stochD)
        self.last_stochK = deepcopy(self.stochK)


class Bollinger_bands_class:
    def __init__(self, d : float = 2, n : int = 20, lenSave_candles : int = 3):
        self.n = deepcopy(n)
        self.d = deepcopy(d)
        self.Close_deq = deque()
        self.candle = None
        self.lastCandle = None
        self.ML = 0.0
        self.BL = 0.0
        self.TL = 0.0
        self.lastTL = 0.0
        self.lastML = 0.0
        self.lastBL = 0.0
        self.save_candles = deque()
        self.lenSave_candles = lenSave_candles

    def __deepcopy__(self, memodict):
        my_copy = type(self)(d=self.d, n=self.n)
        my_copy.candle = deepcopy(self.candle)
        my_copy.Close_deq = deepcopy(self.Close_deq)
        my_copy.ML = deepcopy(self.ML)
        my_copy.BL = deepcopy(self.BL)
        my_copy.lastBL = deepcopy(self.lastBL)
        my_copy.lastTL = deepcopy(self.lastTL)
        my_copy.TL = deepcopy(self.TL)
        my_copy.ML = deepcopy(self.ML)
        my_copy.lastCandle = deepcopy(self.lastCandle)
        my_copy.lenSave_candles = deepcopy(self.lenSave_candles)
        my_copy.save_candles = deepcopy(self.save_candles)
        return my_copy

    def clear(self):
        self.candle = None
        self.Close_deq = deque()
        self.ML = 0.0
        self.BL = 0.0
        self.lastBL = 0.0
        self.TL = 0.0
        self.lastTL = 0.0
        self.lastML = 0.0
        self.lastCandle = 0.0
        self.save_candles = deque()

    def upd_last(self):
        self.lastBL = deepcopy(self.BL)
        self.lastTL = deepcopy(self.TL)
        self.lastML = deepcopy(self.ML)
        self.lastCandle = deepcopy(self.candle)
        self.save_candles.append(self.candle)
        if len(self.save_candles) > self.lenSave_candles:
            self.save_candles.popleft()

    def get_max_delta_time_lastCandles(self):
        lastCandle = None
        mx = 0.0
        for candle in self.save_candles:
            if lastCandle is None:
                lastCandle = deepcopy(candle)
                continue
            mx = max(mx, (candle.time - lastCandle.time).seconds / 3600)
            lastCandle = deepcopy(candle)
        return mx


class Supertrend_class:
    def __init__(self, n : int = 10, d : float = 3.0):
        self.n = deepcopy(n)
        self.d = deepcopy(d)
        self.TR = deque()
        self.lastFinal_upperband = 0.0
        self.lastFinal_lowerband = 0.0
        self.lastSupertrend = False
        self.candle = None
        self.lastClose = 0.0
        self.last_ATR = 0.0
        self.supertrend = False
        self.final_lowerband = 0.0
        self.final_upperband = 0.0
        self.ATR = 0.0

    def __deepcopy__(self, memodict):
        my_copy = type(self)(n=self.n, d=self.d)
        my_copy.last_ATR = deepcopy(self.last_ATR)
        my_copy.candle = deepcopy(self.candle)
        my_copy.TR = deepcopy(self.TR)
        my_copy.lastFinal_upperband = deepcopy(self.lastFinal_upperband)
        my_copy.lastFinal_lowerband = deepcopy(self.lastFinal_lowerband)
        my_copy.lastSupertrend = deepcopy(self.lastSupertrend)
        my_copy.lastClose = deepcopy(self.lastClose)
        my_copy.supertrend = deepcopy(self.supertrend)
        my_copy.final_lowerband = deepcopy(self.final_lowerband)
        my_copy.final_upperband = deepcopy(self.final_upperband)
        my_copy.ATR = deepcopy(self.ATR)

    def clear(self):
        self.TR = deque()
        self.lastFinal_upperband = 0.0
        self.lastFinal_lowerband = 0.0
        self.lastSupertrend = False
        self.candle = None
        self.lastClose = 0.0
        self.last_ATR = 0.0
        self.supertrend = False
        self.final_lowerband = 0.0
        self.final_upperband = 0.0
        self.ATR = 0.0

    def upd_last(self):
        self.lastFinal_upperband = deepcopy(self.final_upperband)
        self.lastFinal_lowerband = deepcopy(self.final_lowerband)
        self.lastClose = deepcopy(float(self.candle.c))
        self.lastSupertrend = deepcopy(self.supertrend)
        self.last_ATR = deepcopy(self.ATR)


def init_indicators(dt_from : datetime, supertrend_cls : Supertrend_class, bb_cls : Bollinger_bands_class,
            stoch_cls : Stoch_class, portfolio : classes_to_portfolio.Portfolio, ticker : str,
                    interval : tinvest.CandleResolution):
    flag = False
    n_back = 30
    while not flag:
        new_flag_supertrend = False
        delta = date_time.timedelta(seconds=1)
        dt_max = dt_from - delta
        dt_min = datetime_split_day.datetime_begin_of_day(dt_max)

        supertrend_cls.clear()

        bb_cls.clear()
        new_flag_bollinger = False

        new_flag_stoch = False
        stoch_cls.clear()

        fg = portfolio.get_stock_by_ticker(ticker=ticker).figi

        candles_to_indicator = list()

        while n_back - len(candles_to_indicator) > 0:
            candles_load = portfolio.Tinvest_cls.get_candles_day_figi(figi=fg, dt_from=dt_min,
                                                                          dt_to=dt_max, interval=interval)
            candles_to_indicator = candles_load + candles_to_indicator
            dt_min -= delta
            dt_max = dt_min
            dt_min = datetime_split_day.datetime_begin_of_day(dt_max)

        for candle in candles_to_indicator:
            supertrend_cls.candle = candle
            new_flag_supertrend = indicators.Supertrend(supertrend_cls=supertrend_cls)
            supertrend_cls.upd_last()

            bb_cls.candle = candle
            new_flag_bollinger = indicators.Bollinger_bands(bollinger_bands_cls=bb_cls)
            bb_cls.upd_last()
            '''if new_flag_bollinger:
                print(bb_cls_mass[ind].TL, bb_cls_mass[ind].BL)
                print(candle.time)
                print()'''

            stoch_cls.candle = candle
            new_flag_stoch = indicators.Stoch(stoch_cls=stoch_cls)
            stoch_cls.upd_last()

            '''if new_flag_stoch:
                print(stochK, stochD)
                print(candle.time)
                print()'''

        n_back += 1
        flag = new_flag_supertrend and new_flag_bollinger and new_flag_stoch
