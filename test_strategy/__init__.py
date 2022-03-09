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

def main_program(dt_from : datetime, dt_to : datetime, interval : int = 15, percent : float = 0.3):
    TOKEN = "t.WVpg6thNk00O9Vd8P4vrne6om7zDgWaGIsKH6TqdRKgT2giER_3Lqp7w9DI7NYdjPWF4AXkj6MRNP5G51zp2lQ"
    S_TOKEN = "t.gJWIDbsjDOGnbAl2y-pm5kzEIxljV-kWYb1To6Skr4STriOvfDp4q4xwvFzuLzaXxWZt2UzRXysejROedAS1TQ"
    client = tinvest.SyncClient(TOKEN)

    tz = date_time.timezone.utc
    token = work_with_github.get_token.get_token()
    g = Github(token)

    def get_stock_in_lot(cnt_stock_lot : list, spis : list):
        for ind, el in enumerate(spis):
            flag = False
            while not flag:
                try:
                    instr = client.get_market_search_by_ticker(el).payload.instruments[0].lot
                    cnt_stock_lot[ind] = instr
                    flag = True
                    time.sleep(0.2)
                except:
                    time.sleep(0.5)
                    flag = False
        return

    def start_f(dt_from : datetime, dt_to : datetime, interval : int = 15):
        with open('stock_spis.txt', 'r') as stock_spis:
            spis = list(stock_spis.read().split())
        buy_cnt = [0] * len(spis)
        buy_price = [0] * len(spis)
        cnt_stock_lot = [1] * len(spis)
        lastClose = [0.0] * len(spis)
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

        my_plus = 0
        my_plus_tic = dict()
        list_print = []

        get_stock_in_lot(cnt_stock_lot, spis)

        while len(buy_cnt) < len(spis):
            buy_cnt.append(0)
            buy_price.append(0)
        for ind, tic in enumerate(spis):
            m_p = my_plus
            flag_ = False
            fg = ''
            while not flag_:
                try:
                    instr = client.get_market_search_by_ticker(tic)
                    fg = instr.payload.instruments[0].figi
                    flag_ = True
                    time.sleep(0.2)
                except:
                    time.sleep(0.5)
                    flag_ = False
            interval_ = tinvest.CandleResolution(str(interval) + 'min')
            dt_l = dt_from + date_time.timedelta(seconds=0)
            dt_r = datetime_split_day.datetime_per_day(dt_from, dt_to)
            candles = list()

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
                new_flag = False
                candles_to_indicator = list()
                delta = date_time.timedelta(seconds=1)
                dt_max = dt_from - delta
                dt_min = datetime_split_day.datetime_begin_of_day(dt_max)

                Close_deq[ind] = deque()
                lastTL[ind] = 0.0
                lastBL[ind] = 0.0
                new_flag_bollinger = False
                while n_back - len(candles_to_indicator) > 0:
                    try:
                        candles_to_indicator += client.get_market_candles(figi=fg, from_=dt_min, to=dt_max, interval=interval_).payload.candles
                    except:
                        time.sleep(0.2)
                        continue
                    dt_min -= delta
                    dt_max = dt_min
                    dt_min = datetime_split_day.datetime_begin_of_day(dt_max)
                    time.sleep(0.1)
                for candle in candles_to_indicator:
                    new_flag, TR[ind], lastFinal_upperband[ind], lastFinal_lowerband[ind], lastSupertrend[ind], lastClose[ind], supertrend, final_upperband, final_lowerband = indicators.Supertrend(TR=TR[ind], lastSupertrend=lastSupertrend[ind], lastClose=lastClose[ind], lastFinal_lowerband=lastFinal_lowerband[ind], lastFinal_upperband=lastFinal_upperband[ind], High=float(candle.h), Low=float(candle.l), Close=float(candle.c))
                    lastFinal_upperband[ind] = final_upperband
                    lastFinal_lowerband[ind] = final_lowerband
                    lastSupertrend[ind] = supertrend
                    lastClose[ind] = float(candle.c)
                    #print(lastClose, lastSupertrend, lastFinal_lowerband, lastFinal_upperband)

                    new_flag_bollinger, Close_deq[ind], TL, BL = indicators.Bollinger_bands(Close_deq=Close_deq[ind], Close=float(candle.c))
                    lastTL[ind] = TL
                    lastBL[ind] = BL
                    '''if new_flag_bollinger:
                        print(TL, BL)
                        print(candle.time)
                        print()'''

                n_back += 1
                flag = new_flag and new_flag_bollinger
            while (dt_to.day - dt_l.day) > 0 or (dt_to.year - dt_l.year) > 0 or (dt_to.month - dt_l.month) > 0 or (dt_to.hour - dt_l.hour) > 0 or (dt_to.second - dt_l.second) > 1:
                delta = date_time.timedelta(seconds=1)
                try:
                    candles += client.get_market_candles(figi=fg, from_=dt_l, to=dt_r, interval=interval_).payload.candles
                    #print(dt_l, dt_r)
                except:
                    time.sleep(0.2)
                    continue
                dt_l = dt_r + delta
                dt_r = datetime_split_day.datetime_per_day(dt_l, dt_to)
                time.sleep(0.1)

            for candle in candles:
                '''print('start new candle', tic)
                print(candle.time)
                print(candle.c)'''
                #lastClose[ind], lastSupertrend[ind], TR[ind], lastFinal_lowerband[ind], lastFinal_upperband[ind], buy_cnt[ind], my_plus =
                t = strategy.fun_with_bb(el=tic, buy_cnt=buy_cnt[ind], Close=float(candle.c), High=float(candle.h), Low=float(candle.l), lastClose=lastClose[ind],
                                            lastSupertrend=lastSupertrend[ind], TR=TR[ind], lastFinal_upperband=lastFinal_upperband[ind],
                                            lastFinal_lowerband=lastFinal_lowerband[ind], cnt_stock_lot=cnt_stock_lot[ind], percent=percent, my_plus=my_plus,
                                            buy_price=buy_price[ind], dt=candle.time, Close_deq=Close_deq[ind], lastTL=lastTL[ind], lastBL=lastBL[ind])

                lastClose[ind], lastSupertrend[ind], TR[ind], lastFinal_lowerband[ind], lastFinal_upperband[ind], buy_cnt[ind], my_plus, buy_price[ind], Close_deq[ind], lastTL[ind], lastBL[ind] = t
                #print(lastClose, lastSupertrend, lastFinal_lowerband, lastFinal_upperband)
            my_plus_tic[tic] = my_plus - m_p
        print(my_plus)
        print(my_plus_tic)

    start_f(dt_from, dt_to, interval)

if __name__ == '__main__':
    tz = date_time.timezone.utc
    main_program(datetime(2020, 1, 1, 7, 0, 0, tzinfo=tz), datetime(2021, 3, 9, 7, 15, 0, tzinfo=tz), percent=0.04)
