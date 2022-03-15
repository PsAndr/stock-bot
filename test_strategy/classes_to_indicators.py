from collections import deque
import tinvest
from copy import deepcopy


class Stoch_classobject:
    def __init__(self, periodK : int = 14, periodD : int = 3, smoothK : int = 3):
            self.stoch_deq = deque()
            self.stoch_smooth_deq = deque()
            self.low_deq = deque()
            self.high_deq = deque()
            self.candle = None
            self.periodK = periodK
            self.periodD = periodD
            self.smoothK = smoothK
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

