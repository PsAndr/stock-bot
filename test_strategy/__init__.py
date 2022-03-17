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
from test_strategy import classes_to_portfolio
import asyncio
import work_with_tinvest
from work_with_tinvest import get_information_stock


async def main_program(dt_from : datetime, dt_to : datetime, interval : int = 15, percent : float = 0.3):
    async def start_f(dt_from : datetime, dt_to : datetime, interval : int = 15):
        with open('stock_spis.txt', 'r') as stock_spis:
            spis = list(stock_spis.read().split())
        buy_cnt = [0] * len(spis)
        buy_price = [0] * len(spis)
        cnt_stock_lot = [10] * len(spis)
        portfolio = classes_to_portfolio.Portfolio(spis)
        TOKEN = portfolio.Tinvest_cls.get_Token()
        client = tinvest.AsyncClient(TOKEN)

        tz = date_time.timezone.utc
        token = work_with_github.get_token.get_token()
        g = Github(token)
        #for supertrend
        supertrend_cls_mass = [classes_to_indicators.Supertrend_class()] * len(spis)

        #for bollinger bands
        bb_cls_mass = [classes_to_indicators.Bollinger_bands_class()] * len(spis)

        #for stoch
        stoch_cls_mass = [classes_to_indicators.Stoch_class()] * len(spis)

        print('Count stocks in lot is loaded')

        while len(buy_cnt) < len(spis):
            buy_cnt.append(0)
            buy_price.append(0)
        for ind, tic in enumerate(spis):
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
                new_flag = False
                candles_to_indicator = list()
                delta = date_time.timedelta(seconds=1)
                dt_max = dt_from - delta
                dt_min = datetime_split_day.datetime_begin_of_day(dt_max)

                supertrend_cls_mass[ind].clear()

                bb_cls_mass[ind].clear()
                new_flag_bollinger = False

                new_flag_stoch = False
                stoch_cls_mass[ind].clear()

                fg = portfolio.get_stock_by_ticker(ticker=tic).figi

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
                    supertrend_cls_mass[ind].candle = candle
                    new_flag = indicators.Supertrend(supertrend_cls=supertrend_cls_mass[ind])
                    supertrend_cls_mass[ind].upd_last()

                    '''if new_flag:
                        print(candle.time)
                        print(supertrend_cls_mass[ind].lastClose, supertrend_cls_mass[ind].lastSupertrend, supertrend_cls_mass[ind].lastFinal_lowerband, supertrend_cls_mass[ind].lastFinal_upperband)
                        print()'''

                    bb_cls_mass[ind].candle = candle
                    new_flag_bollinger = indicators.Bollinger_bands(bollinger_bands_cls=bb_cls_mass[ind])
                    bb_cls_mass[ind].upd_last()
                    '''if new_flag_bollinger:
                        print(bb_cls_mass[ind].TL, bb_cls_mass[ind].BL)
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

            client_ = portfolio.Tinvest_cls.client

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
                bb_cls_mass[ind].candle = candle
                supertrend_cls_mass[ind].candle = candle
                strategy.fun_with_bb(el=tic, dt=candle.time, bb_cls=bb_cls_mass[ind], stoch_cls=stoch_cls_mass[ind],
                        supertrend_cls=supertrend_cls_mass[ind], stock_cls=portfolio.get_stock_by_ticker(ticker=tic))
                #print(lastClose, lastSupertrend, lastFinal_lowerband, lastFinal_upperband)
            print(portfolio.get_stock_by_ticker(ticker=tic).plus)

        for i in portfolio.stock_mass:
            print("{1}: {0}".format(i.plus, i.ticker))

        await client.close()

    await start_f(dt_from, dt_to, interval)

if __name__ == '__main__':
    tz = date_time.timezone.utc
    asyncio.run(main_program(datetime(2020, 1, 1, 7, 0, 0, tzinfo=tz), datetime(2022, 3, 9, 7, 15, 0, tzinfo=tz), percent=0.04))
