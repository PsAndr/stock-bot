import numpy
from collections import deque
import math
from standart_strategy import classes_to_indicators


def Supertrend(supertrend_cls : classes_to_indicators.Supertrend_class):
    def to_return(is_available : bool):
        return is_available

    Close = float(supertrend_cls.candle.c)
    High = float(supertrend_cls.candle.h)
    Low = float(supertrend_cls.candle.l)

    if supertrend_cls.lastClose == 0:
        supertrend_cls.upd_last()
        return to_return(is_available=False)

    supertrend_cls.TR.append(max(High - Low, abs(High - supertrend_cls.lastClose), abs(Low - supertrend_cls.lastClose)))

    if (len(supertrend_cls.TR) < supertrend_cls.n):
        supertrend_cls.upd_last()
        return to_return(is_available=False)

    if supertrend_cls.last_ATR == 0 and len(supertrend_cls.TR) == supertrend_cls.n:
        supertrend_cls.upd_last()
        supertrend_cls.last_ATR = numpy.mean(list(supertrend_cls.TR))
        return to_return(is_available=False)

    if (len(supertrend_cls.TR) > supertrend_cls.n):
        supertrend_cls.TR.popleft()

    supertrend_cls.ATR = (supertrend_cls.last_ATR * (supertrend_cls.n - 1) + supertrend_cls.TR[-1]) / supertrend_cls.n
    supertrend_cls.final_upperband = (High + Low) / 2 + supertrend_cls.d * supertrend_cls.ATR
    supertrend_cls.final_lowerband = (High + Low) / 2 - supertrend_cls.d * supertrend_cls.ATR

    if (supertrend_cls.lastFinal_upperband == 0):
        if (Close > supertrend_cls.lastFinal_upperband):
            supertrend = True
        # if current close price crosses below lowerband
        elif (Close < supertrend_cls.lastFinal_lowerband):
            supertrend_cls.supertrend = False
        supertrend_cls.lastFinal_upperband = supertrend_cls.final_upperband
        supertrend_cls.lastFinal_lowerband = supertrend_cls.final_lowerband
        supertrend_cls.lastSupertrend = False
        supertrend_cls.upd_last()
        return to_return(is_available=False)

    supertrend_cls.supertrend = False

    if Close > supertrend_cls.lastFinal_upperband:
        supertrend_cls.supertrend = True
    # if current close price crosses below lowerband
    elif Close < supertrend_cls.lastFinal_lowerband:
        supertrend_cls.supertrend = False
    # else, the trend continues
    else:
        supertrend_cls.supertrend = supertrend_cls.lastSupertrend
        if supertrend_cls.supertrend and supertrend_cls.final_lowerband < supertrend_cls.lastFinal_lowerband:
            supertrend_cls.final_lowerband = supertrend_cls.lastFinal_lowerband
        if not supertrend_cls.supertrend and supertrend_cls.final_upperband > supertrend_cls.lastFinal_upperband:
            supertrend_cls.final_upperband = supertrend_cls.lastFinal_upperband
    return to_return(is_available=True)


def Bollinger_bands(bollinger_bands_cls : classes_to_indicators.Bollinger_bands_class):
    def to_return(is_available: bool):
        return is_available

    Close = float(bollinger_bands_cls.candle.c)

    bollinger_bands_cls.Close_deq.append(Close)

    if len(bollinger_bands_cls.Close_deq) < bollinger_bands_cls.n:
        return to_return(is_available=False)

    if len(bollinger_bands_cls.Close_deq) > bollinger_bands_cls.n:
        bollinger_bands_cls.Close_deq.popleft()

    bollinger_bands_cls.ML = sum(bollinger_bands_cls.Close_deq) / bollinger_bands_cls.n

    sum_to_stdDev = 0
    avg = numpy.mean(bollinger_bands_cls.Close_deq)

    for close in bollinger_bands_cls.Close_deq:
        sum_to_stdDev += (close - avg) ** 2
    sum_to_stdDev /= bollinger_bands_cls.n

    StdDev = math.sqrt(sum_to_stdDev)

    bollinger_bands_cls.TL = bollinger_bands_cls.ML + (bollinger_bands_cls.d * StdDev)
    bollinger_bands_cls.BL = bollinger_bands_cls.ML - (bollinger_bands_cls.d * StdDev)

    return to_return(is_available=True)


def Stoch(stoch_cls : classes_to_indicators.Stoch_class):
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


'''def RSI(rsi_cls: classes_to_indicators.RSI_class):
    pass'''


def Fibonacci_levels(fib_levels_cls: classes_to_indicators.Fib_levels_class):
    Close = float(fib_levels_cls.candle.c)
    Low = float(fib_levels_cls.candle.l)
    High = float(fib_levels_cls.candle.h)

    fib_levels_cls.high_deq.append(High)

    if len(fib_levels_cls.high_deq) < fib_levels_cls.n:
        return False

    if len(fib_levels_cls.high_deq) > fib_levels_cls.n:
        fib_levels_cls.high_deq.popleft()

    fib_levels_cls.low_deq.append(Low)

    if len(fib_levels_cls.low_deq) < fib_levels_cls.n:
        return False

    if len(fib_levels_cls.low_deq) > fib_levels_cls.n:
        fib_levels_cls.low_deq.popleft()

    max_price = -1
    max_price_ind = -1
    min_price = 1e100
    min_price_ind = -1

    for ind, el in enumerate(fib_levels_cls.high_deq):
        if el > max_price:
            max_price = el
            max_price_ind = ind

    for ind, el in enumerate(fib_levels_cls.low_deq):
        if el < min_price:
            min_price = el
            min_price_ind = ind

    diff = max_price - min_price

    levels = dict()

    if max_price_ind >= min_price_ind:
        levels[1] = min_price
        levels[0.786] = max_price - 0.786 * diff
        levels[0.618] = max_price - 0.618 * diff
        levels[0.5] = max_price - 0.5 * diff
        levels[0.382] = max_price - 0.382 * diff
        levels[0.236] = max_price - 0.236 * diff
        levels[0] = max_price
    else:
        levels[0] = min_price
        levels[0.236] = min_price + 0.236 * diff
        levels[0.382] = min_price + 0.382 * diff
        levels[0.5] = min_price + 0.5 * diff
        levels[0.618] = min_price + 0.618 * diff
        levels[0.786] = min_price + 0.786 * diff
        levels[1] = max_price

    fib_levels_cls.levels = levels

    return True
