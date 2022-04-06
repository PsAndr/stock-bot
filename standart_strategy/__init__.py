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
from standart_strategy import strategy
from standart_strategy import indicators
from standart_strategy import get_candles
from standart_strategy import classes_to_indicators
from standart_strategy import classes_to_portfolio
import asyncio
from copy import deepcopy
import work_with_tinvest
from work_with_tinvest import get_information_stock


async def main_program(interval : int = 15, percent : float = 0.3):
    '''with open('stock_spis.txt', 'r') as stock_spis:
        spis = list(stock_spis.read().split())'''
    spis = ['GAZP', 'MTSS', 'ALRS', 'DSKY', 'RUAL', 'SBER', 'YNDX', 'VTBR', 'AFLT', 'MVID', 'IRAO']
    buy_cnt = [0 for i in range(len(spis))]
    buy_price = [0 for i in range(len(spis))]
    portfolio = classes_to_portfolio.Portfolio(spis=spis, commission=percent)

    print('Count stocks in lot is load')

    tz = date_time.timezone.utc
    token = work_with_github.get_token.get_token()
    g = Github(token)
    # for supertrend
    supertrend_cls_mass = [classes_to_indicators.Supertrend_class() for i in range(len(spis))]

    # for bollinger bands
    bb_cls_mass = [classes_to_indicators.Bollinger_bands_class() for i in range(len(spis))]

    # for stoch
    stoch_cls_mass = [classes_to_indicators.Stoch_class() for i in range(len(spis))]

    procs = list()

    datetime_now = datetime.now(tz=tz)
    time_delta = date_time.timedelta(minutes=interval - 1, seconds=59, milliseconds=500)

    for ind, tic in enumerate(spis):
        classes_to_indicators.init_indicators(
            dt_from=datetime_now - time_delta, supertrend_cls=supertrend_cls_mass[ind],
            bb_cls=bb_cls_mass[ind], stoch_cls=stoch_cls_mass[ind],
            portfolio=portfolio, ticker=tic, interval=tinvest.CandleResolution.min15
        )

        print('pre loading is done {0}, {1}'.format(tic, portfolio.get_stock_by_ticker(tic).figi))

    async def start_f(interval: int = 15):
        while True:
            dt_now = datetime.now(tz=date_time.timezone.utc)
            #print(f'datetime now: {dt_now}')
            if (dt_now.minute + 1) % interval == 0 and dt_now.second == 58:
                for ind, tic in enumerate(spis):
                    candle = portfolio.get_stock_by_ticker(ticker=tic).candle_now(interval=tinvest.CandleResolution.min15)

                    print(f'candle now: {candle}\ncandle before: {bb_cls_mass[ind].candle}')

                    if bb_cls_mass[ind].candle.time == candle.time:
                        print(f'oops\n{tic} was load')
                        continue

                    print(f'candle is load: {candle}')

                    stoch_cls = deepcopy(stoch_cls_mass[ind])
                    bb_cls = deepcopy(bb_cls_mass[ind])
                    supertrend_cls = deepcopy(supertrend_cls_mass[ind])

                    stoch_cls.candle = candle
                    bb_cls.candle = candle
                    supertrend_cls.candle = candle
                    strategy.fun_with_bb(
                        el=tic,
                        dt=candle.time,
                        bb_cls=bb_cls,
                        stoch_cls=stoch_cls,
                        supertrend_cls=supertrend_cls,
                        stock_cls=portfolio.get_stock_by_ticker(ticker=tic)
                    )
                print(f'end of candle check: {datetime.now(tz=tz)}')

                for ind, tic in enumerate(spis):
                    print(f'start get candle to save: {tic}')
                    print(f'date range\n{dt_now - date_time.timedelta(minutes=15)}\n{dt_now - date_time.timedelta(seconds=30)}')
                    candle = portfolio.get_stock_by_ticker(ticker=tic).get_candles(
                        dt_from=dt_now - date_time.timedelta(minutes=15),
                        dt_to=dt_now - date_time.timedelta(seconds=30),
                        interval=tinvest.CandleResolution.min15
                    )
                    if len(candle) == 0:
                        print(f'error save candle: {tic}\n{dt_now - date_time.timedelta(minutes=15)}\n{dt_now - date_time.timedelta(seconds=30)}\n___________________')
                        pass
                    else:
                        candle = candle[-1]

                        if bb_cls_mass[ind].candle.time == candle.time:
                            continue

                        print(f'candle to save {tic}: {candle}')

                        stoch_cls_mass[ind].candle = candle
                        bb_cls_mass[ind].candle = candle
                        supertrend_cls_mass[ind].candle = candle

                        indicators.Stoch(stoch_cls=stoch_cls_mass[ind])
                        indicators.Bollinger_bands(bollinger_bands_cls=bb_cls_mass[ind])
                        indicators.Supertrend(supertrend_cls=supertrend_cls_mass[ind])

                        stoch_cls_mass[ind].upd_last()
                        bb_cls_mass[ind].upd_last()
                        supertrend_cls_mass[ind].upd_last()
            time_to_sleep = (int(1e6) - datetime.now(tz=tz).microsecond) / int(1e6)

            time.sleep(time_to_sleep)

    await start_f(interval)

if __name__ == '__main__':
    asyncio.run(main_program(percent=0.04))
