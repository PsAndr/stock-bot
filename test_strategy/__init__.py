from tradingview_ta import TA_Handler, Interval, Exchange
from datetime import datetime
import time
import tinvest
import asyncio
import os
from multiprocessing import Process
import threading
import pickle
from github import Github
import github
from tzlocal import get_localzone
from collections import deque
import numpy
import datetime as date_time
from can_buy import can_buy
import work_with_github
from test_strategy import strategy
from test_strategy import datetime_split_day
from test_strategy import indicators
from test_strategy import get_candles
from test_strategy import classes_to_indicators
import asyncio

async def main_program(dt_from : datetime, dt_to : datetime, interval : int = 15, percent : float = 0.3):
    TOKEN = "t.WVpg6thNk00O9Vd8P4vrne6om7zDgWaGIsKH6TqdRKgT2giER_3Lqp7w9DI7NYdjPWF4AXkj6MRNP5G51zp2lQ"
    S_TOKEN = "t.gJWIDbsjDOGnbAl2y-pm5kzEIxljV-kWYb1To6Skr4STriOvfDp4q4xwvFzuLzaXxWZt2UzRXysejROedAS1TQ"
    client = tinvest.AsyncClient(TOKEN)

    tz = date_time.timezone.utc
    token = work_with_github.get_token.get_token()
    g = Github(token)

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
                    time.sleep(10)
                    flag = False
                    print(try_cnt)
        return

    async def start_f(dt_from : datetime, dt_to : datetime, interval : int = 15):
        with open('stock_spis.txt', 'r') as stock_spis:
            spis = list(stock_spis.read().split())
        buy_cnt = [0] * len(spis)
        buy_price = [0] * len(spis)
        cnt_stock_lot = [10] * len(spis)
        lastClose = [0.0] * len(spis)
        last_ATR = [0.0] * len(spis)
        TR = [deque()] * len(spis)
        lastFinal_upperband = [0] * len(spis)
        lastFinal_lowerband = [0] * len(spis)
        lastBBlower = [0] * len(spis)
        lastBBupper = [0] * len(spis)
        lastSupertrend = [False] * len(spis)

        #for bollinger bands
        Close_deq = [deque()] * len(spis)
        lastTL = [0.0] * len(spis)
        lastBL = [0.0] * len(spis)
        lastML = [0.0] * len(spis)

        #for stoch
        stoch_cls_mass = [classes_to_indicators.Stoch_classobject()] * len(spis)

        max_cost = [0.0] * len(spis)
        my_plus = 0
        my_plus_tic = dict()
        list_print = []

        await get_stock_in_lot(cnt_stock_lot, spis)

        print('Count stocks in lot is loaded')

        while len(buy_cnt) < len(spis):
            buy_cnt.append(0)
            buy_price.append(0)
        for ind, tic in enumerate(spis):
            m_p = my_plus
            flag_ = False
            fg = ''
            while not flag_:
                try:
                    instr = await client.get_market_search_by_ticker(tic)
                    fg = instr.payload.instruments[0].figi
                    flag_ = True
                    time.sleep(0.2)
                except:
                    time.sleep(1.5)
                    flag_ = False
            interval_ = tinvest.CandleResolution(str(interval) + 'min')
            dt_l = dt_from + date_time.timedelta(seconds=0)
            dt_r = datetime_split_day.datetime_per_day(dt_from, dt_to)
            candles = [0]
            flag = False
            n_back = 1
            while not flag:
                buy_cnt[ind] = 0
                buy_price[ind] = 0
                lastClose[ind] = 0.0
                TR[ind] = deque()
                lastFinal_upperband[ind] = 0
                lastFinal_lowerband[ind] = 0
                lastSupertrend[ind] = False
                last_ATR[ind] = 0.0
                new_flag = False
                candles_to_indicator = list()
                delta = date_time.timedelta(seconds=1)
                dt_max = dt_from - delta
                dt_min = datetime_split_day.datetime_begin_of_day(dt_max)

                Close_deq[ind] = deque()
                lastTL[ind] = 0.0
                lastBL[ind] = 0.0
                lastML[ind] = 0.0
                new_flag_bollinger = False

                new_flag_stoch = False
                stoch_cls_mass[ind].clear()

                while n_back - len(candles_to_indicator) > 0:
                    try:
                        candles_load = await client.get_market_candles(figi=fg, from_=dt_min, to=dt_max, interval=interval_)
                        candles_to_indicator += candles_load.payload.candles
                    except:
                        time.sleep(1.5)
                        continue
                    dt_min -= delta
                    dt_max = dt_min
                    dt_min = datetime_split_day.datetime_begin_of_day(dt_max)
                    time.sleep(0.1)
                for candle in candles_to_indicator:
                    new_flag, TR[ind], lastFinal_upperband[ind], lastFinal_lowerband[ind], lastSupertrend[ind], lastClose[ind], supertrend, final_upperband, final_lowerband, last_ATR[ind] = indicators.Supertrend(TR=TR[ind], lastSupertrend=lastSupertrend[ind], lastClose=lastClose[ind], lastFinal_lowerband=lastFinal_lowerband[ind], lastFinal_upperband=lastFinal_upperband[ind], High=float(candle.h), Low=float(candle.l), Close=float(candle.c), last_ATR=last_ATR[ind])
                    lastFinal_upperband[ind] = final_upperband
                    lastFinal_lowerband[ind] = final_lowerband
                    lastSupertrend[ind] = supertrend
                    lastClose[ind] = float(candle.c)
                    '''if new_flag:
                        print(candle.time)
                        print(lastClose, lastSupertrend, lastFinal_lowerband, lastFinal_upperband)
                        print()'''

                    new_flag_bollinger, Close_deq[ind], TL, BL, ML = indicators.Bollinger_bands(Close_deq=Close_deq[ind], Close=float(candle.c))
                    lastTL[ind] = TL
                    lastBL[ind] = BL
                    lastML[ind] = ML
                    '''if new_flag_bollinger:
                        print(TL, BL)
                        print(candle.time)
                        print()'''

                    stoch_cls_mass[ind].candle = candle
                    new_flag_stoch = indicators.Stoch(stoch_cls_mass[ind])

                    '''if new_flag_stoch:
                        print(stochK, stochD)
                        print(candle.time)
                        print()'''

                n_back += 1
                flag = new_flag and new_flag_bollinger and new_flag_stoch
            print('pre loading is done')
            procs = []
            index = 0

            client_ = tinvest.SyncClient(TOKEN)

            while (dt_to.day - dt_l.day) > 0 or (dt_to.year - dt_l.year) > 0 or (dt_to.month - dt_l.month) > 0 or (dt_to.hour - dt_l.hour) > 0 or (dt_to.second - dt_l.second) > 1:
                delta = date_time.timedelta(seconds=1)
                proc = threading.Thread(target=get_candles.get, args=(tic, dt_l, dt_r, interval_, candles, index, client_))
                dt_l = dt_r + delta
                dt_r = datetime_split_day.datetime_per_day(dt_l, dt_to)
                procs.append(proc)
                index += 1

            procs_now = []
            for proc in procs:
                procs_now.append(proc)
                proc.start()
                proc.join()
                time.sleep(0.05)

            candles = candles[:-1]

            print('candles is loaded')

            for candle in candles:
                '''print('start new candle', tic)
                print(candle.time)
                print(candle.c)'''
                #lastClose[ind], lastSupertrend[ind], TR[ind], lastFinal_lowerband[ind], lastFinal_upperband[ind], buy_cnt[ind], my_plus =
                stoch_cls_mass[ind].candle = candle
                t = strategy.fun_with_bb(el=tic, buy_cnt=buy_cnt[ind], Close=float(candle.c), High=float(candle.h), Low=float(candle.l), lastClose=lastClose[ind],
                                            lastSupertrend=lastSupertrend[ind], TR=TR[ind], lastFinal_upperband=lastFinal_upperband[ind],
                                            lastFinal_lowerband=lastFinal_lowerband[ind], cnt_stock_lot=cnt_stock_lot[ind], percent=percent, my_plus=my_plus,
                                            buy_price=buy_price[ind], dt=candle.time, Close_deq=Close_deq[ind], lastTL=lastTL[ind], lastBL=lastBL[ind], last_ATR=last_ATR[ind],
                                         max_cost=max_cost[ind], lastML=lastML[ind], Open=candle.o, stoch_cls=stoch_cls_mass[ind])

                [lastClose[ind], lastSupertrend[ind], TR[ind], lastFinal_lowerband[ind], lastFinal_upperband[ind], buy_cnt[ind], my_plus, buy_price[ind],
                Close_deq[ind], lastTL[ind], lastBL[ind], last_ATR[ind], max_cost[ind], lastML[ind]] = t
                #print(lastClose, lastSupertrend, lastFinal_lowerband, lastFinal_upperband)
            my_plus_tic[tic] = my_plus - m_p
            print(my_plus_tic[tic])
        print(my_plus)
        print(my_plus_tic)

    await start_f(dt_from, dt_to, interval)

    await client.close()

if __name__ == '__main__':
    tz = date_time.timezone.utc
    asyncio.run(main_program(datetime(2020, 1, 1, 7, 0, 0, tzinfo=tz), datetime(2022, 3, 9, 7, 15, 0, tzinfo=tz), percent=0.04))
