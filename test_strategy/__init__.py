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
        buy_cnt = [0 for i in range(len(spis))]
        buy_price = [0 for i in range(len(spis))]
        portfolio = classes_to_portfolio.Portfolio(spis=spis, commission=percent)
        TOKEN = portfolio.Tinvest_cls.get_Token()
        client = tinvest.AsyncClient(TOKEN)

        tz = date_time.timezone.utc
        token = work_with_github.get_token.get_token()
        g = Github(token)
        #for supertrend
        supertrend_cls_mass = [classes_to_indicators.Supertrend_class() for i in range(len(spis))]

        #for bollinger bands
        bb_cls_mass = [classes_to_indicators.Bollinger_bands_class() for i in range(len(spis))]

        #for stoch
        stoch_cls_mass = [classes_to_indicators.Stoch_class() for i in range(len(spis))]

        print('Count stocks in lot is load')

        for ind, tic in enumerate(spis):
            classes_to_indicators.init_indicators(dt_from=dt_from, supertrend_cls=supertrend_cls_mass[ind],
                        bb_cls=bb_cls_mass[ind], stoch_cls=stoch_cls_mass[ind], portfolio=portfolio, ticker=tic,
                        interval=tinvest.CandleResolution.min15)

            print('pre loading is done')

            candles = portfolio.get_stock_by_ticker(ticker=tic).get_candles(dt_from=dt_from, dt_to=dt_to, interval=tinvest.CandleResolution.min15)

            print('candles is load')

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
    asyncio.run(main_program(datetime(2021, 1, 1, 7, 0, 0, tzinfo=tz), datetime(2021, 12, 31, 7, 15, 0, tzinfo=tz), percent=0.04))
