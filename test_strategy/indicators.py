import numpy
from collections import deque
import math
from test_strategy import classes_to_indicators

def Supertrend(TR : deque, lastFinal_upperband : float, lastFinal_lowerband : float, lastSupertrend : bool,
               High : float, Low : float, Close : float, lastClose : float, last_ATR : float, n : int = 10, d : float = 3.0):
    def to_return(is_available : bool, TR : deque, lastFinal_upperband : float, lastFinal_lowerband : float,
                  lastSupertrend : bool, lastClose : float, supertrend : bool, final_upperband : float, final_lowerband : float, last_ATR : float):
        return [is_available, TR, lastFinal_upperband, lastFinal_lowerband, lastSupertrend, lastClose, supertrend, final_upperband, final_lowerband, last_ATR]

    if lastClose == 0:
        lastClose = Close
        return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=False, lastClose=lastClose, supertrend=False, final_lowerband=0, final_upperband=0, last_ATR=0.0)

    TR.append(max(High - Low, abs(High - lastClose), abs(Low - lastClose)))

    if (len(TR) < n):
        return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=False, lastClose=lastClose, supertrend=False, final_lowerband=0, final_upperband=0, last_ATR=0.0)

    if last_ATR == 0:
        last_ATR = numpy.mean(list(TR)[:-1])

    if (len(TR) > n):
        TR.popleft()

    ATR = (last_ATR * (n - 1) + TR[-1]) / n
    final_upperband = (High + Low) / 2 + d * ATR
    final_lowerband = (High + Low) / 2 - d * ATR

    last_ATR = ATR

    if (lastFinal_upperband == 0):
        if (Close > lastFinal_upperband):
            supertrend = True
        # if current close price crosses below lowerband
        elif (Close < lastFinal_lowerband):
            supertrend = False
        lastFinal_upperband = final_upperband
        lastFinal_lowerband = final_lowerband
        lastSupertrend = False
        return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=False, lastClose=lastClose, supertrend=False, final_upperband=final_upperband, final_lowerband=final_lowerband, last_ATR=last_ATR)

    supertrend = False

    if Close > lastFinal_upperband:
        supertrend = True
    # if current close price crosses below lowerband
    elif Close < lastFinal_lowerband:
        supertrend = False
    # else, the trend continues
    else:
        supertrend = lastSupertrend
        if supertrend and final_lowerband < lastFinal_lowerband:
            final_lowerband = lastFinal_lowerband
        if not supertrend and final_upperband > lastFinal_upperband:
            final_upperband = lastFinal_upperband
    return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=True, lastClose=lastClose, supertrend=supertrend, final_lowerband=final_lowerband, final_upperband=final_upperband, last_ATR=last_ATR)

def Bollinger_bands(Close_deq : deque, Close : float, d : float = 2, n : int = 20):
    def to_return(is_available : bool, Close_deq_ : deque, TL_ : float, BL_ : float, ML_ : float):
        return [is_available, Close_deq_, TL_, BL_, ML_]

    Close_deq.append(Close)

    if len(Close_deq) < n:
        return to_return(is_available=False, Close_deq_=Close_deq, TL_=0, BL_=0, ML_=0)

    if len(Close_deq) > n:
        Close_deq.popleft()

    ML = sum(Close_deq) / n

    sum_to_stdDev = 0
    avg = numpy.mean(Close_deq)
    for close in Close_deq:
        sum_to_stdDev += (close - avg) ** 2
    sum_to_stdDev /= n

    StdDev = math.sqrt(sum_to_stdDev)

    TL = ML + (d * StdDev)
    BL = ML - (d * StdDev)

    return to_return(is_available=True, Close_deq_=Close_deq, TL_=TL, BL_=BL, ML_=ML)


def Stoch(stoch_cls : classes_to_indicators.Stoch_classobject):
    def to_return(is_available : bool):
        return is_available

    Close = float(stoch_cls.candle.c)
    Low = float(stoch_cls.candle.l)
    High = float(stoch_cls.candle.h)

    stoch_cls.low_deq.append(Low)
    stoch_cls.high_deq.append(High)

    if len(stoch_cls.low_deq) < stoch_cls.periodK:
        return to_return(is_available=False)

    if len(stoch_cls.low_deq) > stoch_cls.periodK:
        stoch_cls.low_deq.popleft()
        stoch_cls.high_deq.popleft()

    stochK_without_smooth = 100 * (Close - min(stoch_cls.low_deq)) / (max(stoch_cls.high_deq) - min(stoch_cls.low_deq))

    stoch_cls.stoch_deq.append(stochK_without_smooth)

    if len(stoch_cls.stoch_deq) < stoch_cls.smoothK:
        return to_return(is_available=False)

    if len(stoch_cls.stoch_deq) > stoch_cls.smoothK:
        stoch_cls.stoch_deq.popleft()

    stoch_cls.stochK = numpy.mean(stoch_cls.stoch_deq)
    stoch_cls.stoch_smooth_deq.append(stoch_cls.stochK)

    if len(stoch_cls.stoch_smooth_deq) < stoch_cls.periodD:
        return to_return(is_available=False)

    if len(stoch_cls.stoch_smooth_deq) > stoch_cls.periodD:
        stoch_cls.stoch_smooth_deq.popleft()

    stoch_cls.stochD = numpy.mean(stoch_cls.stoch_smooth_deq)

    return to_return(is_available=True)
