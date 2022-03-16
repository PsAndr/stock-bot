import decimal
from collections import deque
import tinvest
from copy import deepcopy


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

    def __deepcopy__(self, memodict):
        my_copy = type(self)(periodK=self.periodK, periodD=self.periodD, smoothK=self.smoothK)
        my_copy.stoch_deq = deepcopy(self.stoch_deq)
        my_copy.stoch_smooth_deq = deepcopy(self.stoch_smooth_deq)
        my_copy.low_deq = deepcopy(self.low_deq)
        my_copy.high_deq = deepcopy(self.high_deq)
        my_copy.candle = deepcopy(self.candle)
        my_copy.stochK = deepcopy(self.stochK)
        my_copy.stochD = deepcopy(self.stochD)
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


class Bollinger_bands_class:
    def __init__(self, d : float = 2, n : int = 20):
        self.n = deepcopy(n)
        self.d = deepcopy(d)
        self.Close_deq = deque()
        self.candle = None
        self.ML = 0.0
        self.BL = 0.0
        self.TL = 0.0
        self.lastTL = 0.0
        self.lastML = 0.0
        self.lastBL = 0.0

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

    def upd_last(self):
        self.lastBL = deepcopy(self.BL)
        self.lastTL = deepcopy(self.TL)
        self.lastML = deepcopy(self.ML)


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
