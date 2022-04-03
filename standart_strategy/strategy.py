import asyncio
import numpy
import datetime
from collections import deque
from standart_strategy import indicators
import time
import tinvest
import datetime as date_time
from tradingview_ta import TA_Handler, Interval, Exchange
from standart_strategy import classes_to_indicators
from standart_strategy import classes_to_portfolio

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


def fun_with_bb(el, stock_cls : classes_to_portfolio.Stock, dt : datetime,
                bb_cls : classes_to_indicators.Bollinger_bands_class, stoch_cls : classes_to_indicators.Stoch_class,
                supertrend_cls : classes_to_indicators.Supertrend_class):
    flag = indicators.Supertrend(supertrend_cls=supertrend_cls)
    if not flag:
        print('oops', dt)
        return
    flag_BB = indicators.Bollinger_bands(bollinger_bands_cls=bb_cls)
    flag_Stoch = indicators.Stoch(stoch_cls=stoch_cls)

    Open = float(stoch_cls.candle.o)
    High = float(stoch_cls.candle.h)
    Close = float(stoch_cls.candle.c)
    Low = float(stoch_cls.candle.l)

    max_delta_time_candles = bb_cls.get_max_delta_time_lastCandles()

    if Close >= bb_cls.BL and supertrend_cls.lastClose < bb_cls.lastBL and supertrend_cls.supertrend and stock_cls.cnt_buy == 0 \
            and max(stoch_cls.stochD, stoch_cls.stochK) < 40 and min(stoch_cls.stochK, stoch_cls.stochD) < 30 \
            and Close < bb_cls.ML:
        d = stock_cls.buy(buy_price=Close, cnt_buy=1, dt=dt)
        print(bb_cls.lastCandle.time, bb_cls.candle.time)
        print((bb_cls.candle.time - bb_cls.lastCandle.time).seconds / 3600)
        print('_______________')

    if Close <= bb_cls.TL and supertrend_cls.lastClose > bb_cls.lastTL and stock_cls.cnt_buy > 0:
        d = stock_cls.sell(sell_cost=Close, dt=dt)
        print(bb_cls.lastCandle.time, bb_cls.candle.time)
        print((bb_cls.candle.time - bb_cls.lastCandle.time).seconds / 3600)
        print('_______________')

    if stock_cls.buy_price != Close and stock_cls.cnt_buy > 0 and Close <= stock_cls.buy_price * 0.99:
        d = stock_cls.sell(sell_cost=Close, dt=dt)
        print(bb_cls.lastCandle.time, bb_cls.candle.time)
        print((bb_cls.candle.time - bb_cls.lastCandle.time).seconds / 3600)
        print('_______________')

    if stock_cls.cnt_buy > 0 and stock_cls.buy_price != Close and Close <= stock_cls.max_cost * 0.98:
        d = stock_cls.sell(sell_cost=Close, dt=dt)
        print(bb_cls.lastCandle.time, bb_cls.candle.time)
        print((bb_cls.candle.time - bb_cls.lastCandle.time).seconds / 3600)
        print('_______________')

    if stock_cls.cnt_buy > 0 and Close > stock_cls.max_cost:
        stock_cls.max_cost = Close

    supertrend_cls.upd_last()
    bb_cls.upd_last()
    stoch_cls.upd_last()

    return

def strategy_with_tradingview():
    '''with open('stock_spis.txt', 'r') as stock_spis:
        spis = list(stock_spis.read().split())'''
    spis = ["SBER"]
    buy_cnt = [0] * len(spis)
    buy_price = [0] * len(spis)
    cnt_stock_lot = [10] * len(spis)

    '''TOKEN = "t.WVpg6thNk00O9Vd8P4vrne6om7zDgWaGIsKH6TqdRKgT2giER_3Lqp7w9DI7NYdjPWF4AXkj6MRNP5G51zp2lQ"
    S_TOKEN = "t.gJWIDbsjDOGnbAl2y-pm5kzEIxljV-kWYb1To6Skr4STriOvfDp4q4xwvFzuLzaXxWZt2UzRXysejROedAS1TQ"
    client = tinvest.AsyncClient(TOKEN)'''

    tz = date_time.timezone.utc

    async def get_stock_in_lot(cnt_stock_lot : list, spis : list):
        for ind, el in enumerate(spis):
            flag = False
            try_cnt = 0
            while not flag:
                try:
                    instr = await client.get_market_search_by_ticker(el)
                    instr = instr.payload.instruments[0].lot
                    cnt_stock_lot[ind] = instr
                    flag = True
                    time.sleep(0.2)
                except:
                    try_cnt += 1
                    time.sleep(0.5)
                    flag = False
        return

    #asyncio.run(get_stock_in_lot(cnt_stock_lot=cnt_stock_lot, spis=spis))

    for tic in spis:
        ticker = TA_Handler(
            screener='crypto',
            exchange='EXMO',
            symbol='BTCUSD',
            interval=Interval.INTERVAL_15_MINUTES
        )
        print(ticker.symbol)
        flag = True
        while flag:
            try:
                analysis = ticker.get_analysis()
                flag = False
            except:
                flag = True
                time.sleep(0.5)
        print(analysis.oscillators['COMPUTE'])
        print(analysis.moving_averages['COMPUTE'])

if __name__ == "__main__":
    strategy_with_tradingview()