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

'''
def fun_with_bb(ind, el, Close, High, Low, BBlower, BBupper):
    if (lastClose[ind] == 0):
        lastClose[ind] = Close
        return

    TR[ind].append(max(High - Low, abs(High - lastClose[ind]), abs(Low - lastClose[ind])))

    if (len(TR[ind]) < 10):
        lastClose[ind] = Close
        lastBBlower[ind] = BBlower
        lastBBupper[ind] = BBupper
        return

    if (len(TR[ind]) > 10):
        TR[ind].popleft()

    ATR = numpy.mean(TR[ind])
    final_upperband = (High + Low) / 2 + 3 * ATR
    final_lowerband = (High + Low) / 2 - 3 * ATR

    if (lastFinal_upperband[ind] == 0):
        if (Close > lastFinal_upperband[ind]):
            supertrend = True
        # if current close price crosses below lowerband
        elif (Close < lastFinal_lowerband[ind]):
            supertrend = False
        lastFinal_upperband[ind] = final_upperband
        lastFinal_lowerband[ind] = final_lowerband
        lastSupertrend[ind] = supertrend

    if (Close > lastFinal_upperband[ind]):
        supertrend = True
    # if current close price crosses below lowerband
    elif (Close < lastFinal_lowerband[ind]):
        supertrend = False
    # else, the trend continues
    else:
        supertrend = lastSupertrend[ind]
        if (supertrend == True and final_lowerband < lastFinal_lowerband[ind]):
            final_lowerband = lastFinal_lowerband[ind]
        if (supertrend == False and final_upperband > lastFinal_upperband[ind]):
            final_upperband = lastFinal_upperband[ind]

    if (Close > BBlower and lastClose[ind] < lastBBlower[ind] and supertrend == True):
        and not (datetime.now(tz).hour - datetime.now(tz).utcoffset().total_seconds() / 3600 == 20 and datetime.now(tz).minute >= 30):
        instr = client.get_market_search_by_ticker(el)
        fg = instr.payload.instruments[0].figi
        try:
            orderbook = (float)(client.get_market_orderbook(figi=fg, depth='1').payload.last_price)
        except:
            list_print[ind].append([el, 'error to get orderbook'])
        list_print[ind].append([el, 'buy', orderbook])
        # request to buy
        try:
            price_buy = comm(el, 1, 'Buy', Close, ind)
            buy_cnt[ind] = 1
            buy_price[ind] = price_buy
            list_print[ind].append([el, 'buy', price_buy])
        except:
            list_print[ind].append([el, 'error buy(1)'])
    random_el = 1

    if ((Close < BBupper and lastClose[ind] > lastBBupper[ind])):
        # or (datetime.now(tz).hour - datetime.now(tz).utcoffset().total_seconds() / 3600 == 20 and datetime.now(tz).minute >= 30)) and (buy_cnt[ind] > 0):
        instr = client.get_market_search_by_ticker(el)
        fg = instr.payload.instruments[0].figi
        try:
            orderbook = (float)(client.get_market_orderbook(figi=fg, depth='1').payload.last_price)
        except:
            list_print[ind].append([el, 'error to get orderbook'])
        list_print[ind].append([el, 'sell', orderbook])
        list_print[ind].append([buy_cnt[ind], (
                    buy_cnt[ind] * orderbook * cnt_stock_lot[ind] - buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[
                ind]) / (buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]), '\n'])
        list_print[ind].append([my_plus])
        # request to sell
        try:
            sell_price = comm(el, 1, 'Sell', Close, ind)
            my_plus += buy_cnt[ind] * sell_price * cnt_stock_lot[ind] - buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]
            list_print[ind].append([el, 'sell', sell_price])
            list_print[ind].append([buy_cnt[ind], (buy_cnt[ind] * sell_price * cnt_stock_lot[ind] - buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]) / (buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]), '\n'])
            list_print[ind].append([my_plus])  
            buy_cnt[ind] = 0
            buy_price[ind] = 0
        except:
            list_print[ind].append([el, 'error sell'])
    random_el = 
    lastFinal_upperband[ind] = final_upperband
    lastFinal_lowerband[ind] = final_lowerband
    lastSupertrend[ind] = supertrend
    lastClose[ind] = Close
    lastBBlower[ind] = BBlower
    lastBBupper[ind] = BBupper
'''

if __name__ == '__main__':
    el = 1