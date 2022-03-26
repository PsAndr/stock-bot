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
from standart_strategy import datetime_split_day
from standart_strategy import indicators
from standart_strategy import get_candles
from standart_strategy import classes_to_indicators
from standart_strategy import classes_to_portfolio
import asyncio
import work_with_tinvest
from work_with_tinvest import get_information_stock


async def main_program(interval : int = 15, percent : float = 0.3):
    with open('stock_spis.txt', 'r') as stock_spis:
        spis = list(stock_spis.read().split())
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

    for ind, tic in enumerate(spis):
        classes_to_indicators.init_indicators(
            dt_from=datetime.now(tz=tz), supertrend_cls=supertrend_cls_mass[ind],
            bb_cls=bb_cls_mass[ind], stoch_cls=stoch_cls_mass[ind],
            portfolio=portfolio, ticker=tic, interval=tinvest.CandleResolution.min15
        )

        print('pre loading is done {0}, {1}'.format(tic, portfolio.get_stock_by_ticker(tic).figi))

    async def start_f(interval : int = 15):
        while True:
            dt_now = datetime.now(tz=date_time.timezone.utc)
            if (dt_now.minute + 1) % interval == 0 and dt_now.second == 58:
                for ind, tic in enumerate(spis):
                    candle = portfolio.get_stock_by_ticker(ticker=tic).candle_now(interval=tinvest.CandleResolution.min15)

                    if bb_cls_mass[ind].candle.time == candle.time:
                        print(f'oops\n{tic} was load')
                        continue

                    print(f'candle is load: {candle}')

                    stoch_cls_mass[ind].candle = candle
                    bb_cls_mass[ind].candle = candle
                    supertrend_cls_mass[ind].candle = candle
                    strategy.fun_with_bb(el=tic, dt=candle.time, bb_cls=bb_cls_mass[ind], stoch_cls=stoch_cls_mass[ind],
                        supertrend_cls=supertrend_cls_mass[ind], stock_cls=portfolio.get_stock_by_ticker(ticker=tic))
                print('end of candle check')

            time.sleep(1)

    await start_f(interval)

if __name__ == '__main__':
    asyncio.run(main_program(percent=0.04))
