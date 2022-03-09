import numpy
import datetime
from collections import deque
from test_strategy import indicators

def fun_without_bb(el, Close : float, High : float, Low : float, lastClose, lastSupertrend, TR : deque, lastFinal_lowerband, lastFinal_upperband, buy_cnt, cnt_stock_lot, percent, my_plus, buy_price, dt : datetime):
    flag, TR, lastFinal_upperband, lastFinal_lowerband, lastSupertrend, lastClose, supertrend, final_upperband, final_lowerband = indicators.Supertrend(TR=TR, lastSupertrend=lastSupertrend, lastClose=lastClose, lastFinal_lowerband=lastFinal_lowerband, lastFinal_upperband=lastFinal_upperband, High=High, Low=Low, Close=Close)
    if not flag:
        print('oops', dt)
        return lastClose, lastSupertrend, TR, lastFinal_lowerband, lastFinal_upperband, buy_cnt, my_plus, buy_price

    if buy_cnt == 0 and supertrend:
        buy_cnt = 1
        buy_price = Close
        print(dt)
        print(el, 'buy', Close)
        print(final_lowerband, final_upperband)
        print('_______________')

    if not supertrend and buy_cnt == 1:
        print(dt)
        print(el, 'sell', Close)
        print(buy_cnt, (buy_cnt * Close * cnt_stock_lot - buy_cnt * buy_price * cnt_stock_lot) / (buy_cnt * buy_price * cnt_stock_lot), '\n')
        my_plus += buy_cnt * Close * cnt_stock_lot - buy_cnt * buy_price * cnt_stock_lot - (percent / 100) * buy_cnt * buy_price * cnt_stock_lot - (percent / 100) * buy_cnt * Close * cnt_stock_lot
        print(my_plus, ' | ', buy_cnt * Close * cnt_stock_lot - buy_cnt * buy_price * cnt_stock_lot - (percent / 100) * buy_cnt * buy_price * cnt_stock_lot - (percent / 100) * buy_cnt * Close * cnt_stock_lot)
        print(final_lowerband, final_upperband)
        print('_______________')
        buy_cnt = 0
    '''print('lower band', final_lowerband)
    print('upper band' ,final_upperband)
    print('_________________________________')'''
    lastFinal_upperband = final_upperband
    lastFinal_lowerband = final_lowerband
    lastSupertrend = supertrend
    lastClose = Close
    return lastClose, lastSupertrend, TR, lastFinal_lowerband, lastFinal_upperband, buy_cnt, my_plus, buy_price


def fun_with_bb(el, Close : float, High : float, Low : float, lastClose, lastSupertrend, TR : deque, lastFinal_lowerband,
                lastFinal_upperband, buy_cnt, cnt_stock_lot, percent : float, my_plus, buy_price, dt : datetime,
                Close_deq : deque, lastTL : float, lastBL : float):
    flag, TR, lastFinal_upperband, lastFinal_lowerband, lastSupertrend, lastClose, supertrend, final_upperband, final_lowerband = indicators.Supertrend(
        TR=TR, lastSupertrend=lastSupertrend, lastClose=lastClose, lastFinal_lowerband=lastFinal_lowerband,
        lastFinal_upperband=lastFinal_upperband, High=High, Low=Low, Close=Close)
    if not flag:
        print('oops', dt)
        return lastClose, lastSupertrend, TR, lastFinal_lowerband, lastFinal_upperband, buy_cnt, my_plus, buy_price
    flag_BB, Close_deq, TL, BL = indicators.Bollinger_bands(Close_deq=Close_deq, Close=Close)
    if Close > BL and lastClose < lastBL and supertrend and buy_cnt == 0:
        buy_cnt = 1
        buy_price = Close
        print(dt)
        print(el, 'buy', Close)
        print(final_lowerband, final_upperband, '\n')
        print(TL, BL)
        print('_______________')

    if Close < TL and lastClose > TL and buy_cnt > 0:
        print(dt)
        print(el, 'sell', Close)
        print(buy_cnt, (buy_cnt * Close * cnt_stock_lot - buy_cnt * buy_price * cnt_stock_lot) / (
                    buy_cnt * buy_price * cnt_stock_lot), '\n')
        my_plus += buy_cnt * Close * cnt_stock_lot - buy_cnt * buy_price * cnt_stock_lot - (
                    percent / 100) * buy_cnt * buy_price * cnt_stock_lot - (
                               percent / 100) * buy_cnt * Close * cnt_stock_lot
        print(my_plus, ' | ', buy_cnt * Close * cnt_stock_lot - buy_cnt * buy_price * cnt_stock_lot - (
                    percent / 100) * buy_cnt * buy_price * cnt_stock_lot - (
                          percent / 100) * buy_cnt * Close * cnt_stock_lot)
        print(final_lowerband, final_upperband, '\n')
        print(TL, BL)
        print('_______________')
        buy_cnt = 0

    lastFinal_upperband = final_upperband
    lastFinal_lowerband = final_lowerband
    lastSupertrend = supertrend
    lastClose = Close
    lastTL = TL
    lastBL = BL

    return lastClose, lastSupertrend, TR, lastFinal_lowerband, lastFinal_upperband, buy_cnt, my_plus, buy_price, Close_deq, lastTL, lastBL
