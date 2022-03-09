import numpy
from collections import deque
import math

def Supertrend(TR : deque, lastFinal_upperband : float, lastFinal_lowerband : float, lastSupertrend : bool, High : float, Low : float, Close : float, lastClose : float, n : int = 10, d : float = 3.0):
    def to_return(is_available : bool, TR : deque, lastFinal_upperband : float, lastFinal_lowerband : float, lastSupertrend : bool, lastClose : float, supertrend : bool, final_upperband : float, final_lowerband : float):
        return [is_available, TR, lastFinal_upperband, lastFinal_lowerband, lastSupertrend, lastClose, supertrend, final_upperband, final_lowerband]

    if lastClose == 0:
        lastClose = Close
        return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=False, lastClose=lastClose, supertrend=False, final_lowerband=0, final_upperband=0)

    TR.append(max(High - Low, abs(High - lastClose), abs(Low - lastClose)))

    if (len(TR) < 10):
        return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=False, lastClose=lastClose, supertrend=False, final_lowerband=0, final_upperband=0)

    if (len(TR) > 10):
        TR.popleft()

    ATR = numpy.mean(TR)
    final_upperband = (High + Low) / 2 + d * ATR
    final_lowerband = (High + Low) / 2 - d * ATR

    if (lastFinal_upperband == 0):
        if (Close > lastFinal_upperband):
            supertrend = True
        # if current close price crosses below lowerband
        elif (Close < lastFinal_lowerband):
            supertrend = False
        lastFinal_upperband = final_upperband
        lastFinal_lowerband = final_lowerband
        lastSupertrend = False
        return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=False, lastClose=lastClose, supertrend=False, final_upperband=final_upperband, final_lowerband=final_lowerband)

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
    return to_return(TR=TR, lastSupertrend=lastSupertrend, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, is_available=True, lastClose=lastClose, supertrend=supertrend, final_lowerband=final_lowerband, final_upperband=final_upperband)

#дописать
def Bollinger_bands(Close_deq : deque, Close : float, d : float = 2, n : int = 20):
    def to_return(is_available : bool, Close_deq_ : deque, TL_ : float, BL_ : float):
        return [is_available, Close_deq_, TL_, BL_]

    Close_deq.append(Close)

    if len(Close_deq) < n:
        return to_return(is_available=False, Close_deq_=Close_deq, TL_=0, BL_=0)

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

    return to_return(is_available=True, Close_deq_=Close_deq, TL_=TL, BL_=BL)
