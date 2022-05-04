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
from standart_strategy import start_file_strategy_bb_st_fib_stch
from standart_strategy import strategy
from standart_strategy import indicators
from standart_strategy import get_candles
from standart_strategy import classes_to_indicators
from standart_strategy import classes_to_portfolio
import asyncio
from copy import deepcopy
import work_with_tinvest
from work_with_tinvest import get_information_stock


def now_straregy():
    start_file_strategy_bb_st_fib_stch.start()


def best_main():
    spis = ['FIVE', 'GAZP', 'MTSS', 'ALRS', 'DSKY', 'RUAL', 'SBER', 'YNDX', 'VTBR', 'AFLT', 'MVID', 'IRAO', 'FIXP']
    #spis = ['FIXP']

    portfolio = classes_to_portfolio.Portfolio(spis=spis)

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

    #for fib
    fib_cls_mass = [classes_to_indicators.Fib_levels_class(n=35) for i in range(len(spis))]

    procs = list()

    datetime_now = datetime.now(tz=tz)
    time_delta = date_time.timedelta(minutes=15 - 1, seconds=59, milliseconds=500)

    indicators_condition_mass = [{'BB': 'sell', 'Stoch': 'sell', 'Fib_levels': 'sell', 'Supertrend': 'sell'} for i in range(len(spis))]

    for ind, tic in enumerate(spis):
        classes_to_indicators.init_indicators(
            dt_from=datetime_now - time_delta, supertrend_cls=supertrend_cls_mass[ind],
            bb_cls=bb_cls_mass[ind], stoch_cls=stoch_cls_mass[ind],
            portfolio=portfolio, ticker=tic, interval=tinvest.CandleResolution.min15,
            fib_levels_cls=fib_cls_mass[ind], indicators_condition=indicators_condition_mass[ind]
        )

        portfolio.get_stock_by_ticker(tic).price_now()

        print('pre loading is done {0}, {1}'.format(tic, portfolio.get_stock_by_ticker(tic).figi))
        print(f'indicators condition {tic}: {indicators_condition_mass[ind]}')

    pool_lists = work_with_github.save_and_load_lists_float.PoolLists()

    buy_cnt = work_with_github.save_and_load_lists_float.load(
        path='standart_strategy/saves/save_buy_info.txt',
        ls_name='buy_cnt'
    )
    buy_price = work_with_github.save_and_load_lists_float.load(
        path='standart_strategy/saves/save_buy_info.txt',
        ls_name='buy_price'
    )

    stop_loss = work_with_github.save_and_load_lists_float.load(
        path='standart_strategy/saves/save_buy_info.txt',
        ls_name='stop_loss'
    )

    while len(buy_cnt) < len(spis):
        buy_cnt.append(0.0)

    while len(buy_price) < len(spis):
        buy_price.append(0.0)

    while len(stop_loss) < len(spis):
        stop_loss.append(0.0)

    work_with_github.save_and_load_lists_float.save(
        path='standart_strategy/saves/save_buy_info.txt',
        ls=buy_cnt,
        ls_name='buy_cnt'
    )

    work_with_github.save_and_load_lists_float.save(
        path='standart_strategy/saves/save_buy_info.txt',
        ls=buy_price,
        ls_name='buy_price'
    )

    work_with_github.save_and_load_lists_float.save(
        path='standart_strategy/saves/save_buy_info.txt',
        ls=stop_loss,
        ls_name='stop_loss'
    )

    pool_lists.set_to_pool({'buy_cnt': buy_cnt})
    pool_lists.set_to_pool({'buy_price': buy_price})

    portfolio.update_buy_price_ticker(work_with_github.merge_lists_to_dict.merge(spis, buy_price))
    portfolio.update_cnt_buy_ticker(work_with_github.merge_lists_to_dict.merge(spis, buy_cnt))
    portfolio.update_stop_loss_ticker(work_with_github.merge_lists_to_dict.merge(spis, stop_loss))


    while True:
        dt_now = datetime.now(tz=date_time.timezone.utc)
        # print(f'datetime now: {dt_now}')
        if dt_now.second % 5 == 0:
            # print(dt_candle)
            for ind, tic in enumerate(spis):
                if portfolio.get_stock_by_ticker(tic).can_buy():
                    candle = portfolio.get_stock_by_ticker(ticker=tic).candle_now(
                        interval=tinvest.CandleResolution.min15)

                    # print(f'candle now: {candle}\ncandle before: {bb_cls_mass[ind].candle}')

                    print(f'ticker: {tic}')
                    print(f'candle is load: {candle}')

                    supertrend_cls = deepcopy(supertrend_cls_mass[ind])
                    fib_cls = deepcopy(fib_cls_mass[ind])
                    bb_cls = deepcopy(bb_cls_mass[ind])
                    stoch_cls = deepcopy(stoch_cls_mass[ind])

                    supertrend_cls.candle = candle
                    fib_cls.candle = candle
                    bb_cls.candle = candle
                    stoch_cls.candle = candle

                    strategy.fun_with_fib(
                        el=tic,
                        dt=candle.time,
                        supertrend_cls=supertrend_cls,
                        stock_cls=portfolio.get_stock_by_ticker(ticker=tic),
                        fib_levels_cls=fib_cls,
                        bb_cls=bb_cls,
                        stoch_cls=stoch_cls,
                        indicators_condition=indicators_condition_mass[ind]
                    )

                    print(f'levels: {fib_cls.levels}\n')
            # print(f'end of candle check: {datetime.now(tz=tz)}')
            stop_loss = portfolio.get_list_stop_loss()

            work_with_github.save_and_load_lists_float.save(
                path='standart_strategy/saves/save_buy_info.txt',
                ls=stop_loss,
                ls_name='stop_loss'
            )
            if not buy_cnt == portfolio.get_list_cnt_buy():
                # print('_________________\nsave\n_________________')
                buy_cnt = portfolio.get_list_cnt_buy()
                buy_price = portfolio.get_list_buy_price()

                work_with_github.save_and_load_lists_float.save(
                    path='standart_strategy/saves/save_buy_info.txt',
                    ls=buy_cnt,
                    ls_name='buy_cnt'
                )

                work_with_github.save_and_load_lists_float.save(
                    path='standart_strategy/saves/save_buy_info.txt',
                    ls=buy_price,
                    ls_name='buy_price'
                )


        dt_now = datetime.now(tz=date_time.timezone.utc)

        if True:
            dt_candle = deepcopy(dt_now)
            dt_candle = dt_candle.replace(second=0, microsecond=0)
            dt_candle = dt_candle.replace(minute=dt_candle.minute // 15 * 15)
            for ind, tic in enumerate(spis):
                # print(f'start get candle to save: {tic}')
                # print(f'date range\n{dt_now - date_time.timedelta(minutes=15)}\n{dt_now - date_time.timedelta(seconds=30)}')
                candle = portfolio.get_stock_by_ticker(ticker=tic).get_candles(
                    dt_from=dt_now - date_time.timedelta(minutes=15 * 2),
                    dt_to=dt_now,
                    interval=tinvest.CandleResolution.min15
                )
                if len(candle) == 0:
                    # print(f'error save candle: {tic}\n{dt_now - date_time.timedelta(minutes=15)}\n{dt_now - date_time.timedelta(seconds=30)}\n___________________')
                    pass
                else:
                    candle_to_save = None
                    for cn in candle:
                        if cn.time == dt_candle:
                            candle_to_save = cn

                    candle = candle_to_save

                    if candle is None:
                        continue

                    if supertrend_cls_mass[ind].candle.time == candle.time:
                        continue

                    # print(f'candle to save {tic}: {candle}')
                    supertrend_cls_mass[ind].candle = candle
                    fib_cls_mass[ind].candle = candle
                    stoch_cls_mass[ind].candle = candle
                    bb_cls_mass[ind].candle = candle

                    indicators.Supertrend(supertrend_cls=supertrend_cls_mass[ind])
                    indicators.Fibonacci_levels(fib_levels_cls=fib_cls_mass[ind])
                    indicators.Bollinger_bands(bollinger_bands_cls=bb_cls_mass[ind])
                    indicators.Stoch(stoch_cls=stoch_cls_mass[ind])

                    supertrend_cls_mass[ind].upd_last()
                    stoch_cls_mass[ind].upd_last()
                    bb_cls_mass[ind].upd_last()

        time_to_sleep = (int(1e6) - datetime.now(tz=tz).microsecond) / int(1e6)

        time.sleep(time_to_sleep)



async def main_program(interval: int = 15, percent: float = 0.3):
    '''with open('stock_spis.txt', 'r') as stock_spis:
        spis = list(stock_spis.read().split())'''
    spis = ['GAZP', 'MTSS', 'ALRS', 'DSKY', 'RUAL', 'SBER', 'YNDX', 'VTBR', 'AFLT', 'MVID', 'IRAO']

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
        pool_lists = work_with_github.save_and_load_lists_float.PoolLists()

        buy_cnt = work_with_github.save_and_load_lists_float.load(
            path='standart_strategy/saves/save_buy_info.txt',
            ls_name='buy_cnt'
        )
        buy_price = work_with_github.save_and_load_lists_float.load(
            path='standart_strategy/saves/save_buy_info.txt',
            ls_name='buy_price'
        )

        while len(buy_cnt) < len(spis):
            buy_cnt.append(0)

        while len(buy_price) < len(spis):
            buy_price.append(0)

        work_with_github.save_and_load_lists_float.save(
            path='standart_strategy/saves/save_buy_info.txt',
            ls=buy_cnt,
            ls_name='buy_cnt'
        )

        work_with_github.save_and_load_lists_float.save(
            path='standart_strategy/saves/save_buy_info.txt',
            ls=buy_price,
            ls_name='buy_price'
        )

        pool_lists.set_to_pool({'buy_cnt': buy_cnt})
        pool_lists.set_to_pool({'buy_price': buy_price})

        portfolio.update_buy_price_ticker(work_with_github.merge_lists_to_dict.merge(spis, buy_price))
        portfolio.update_cnt_buy_ticker(work_with_github.merge_lists_to_dict.merge(spis, buy_cnt))

        while True:
            dt_now = datetime.now(tz=date_time.timezone.utc)
            #print(f'datetime now: {dt_now}')
            if (dt_now.minute + 1) % interval == 0 and dt_now.second == 58:
                dt_candle = deepcopy(dt_now)
                dt_candle += date_time.timedelta(minutes=1)
                dt_candle = dt_candle.replace(second=0, microsecond=0)
                dt_candle -= date_time.timedelta(minutes=interval)
                #print(dt_candle)
                for ind, tic in enumerate(spis):
                    candle = portfolio.get_stock_by_ticker(ticker=tic).candle_now(interval=tinvest.CandleResolution.min15)

                    #print(f'candle now: {candle}\ncandle before: {bb_cls_mass[ind].candle}')

                    if bb_cls_mass[ind].candle.time == candle.time:
                        print(f'oops\n{tic} was load')
                        continue

                    #print(f'candle is load: {candle}')

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
                #print(f'end of candle check: {datetime.now(tz=tz)}')

                for ind, tic in enumerate(spis):
                    #print(f'start get candle to save: {tic}')
                    #print(f'date range\n{dt_now - date_time.timedelta(minutes=15)}\n{dt_now - date_time.timedelta(seconds=30)}')
                    candle = portfolio.get_stock_by_ticker(ticker=tic).get_candles(
                        dt_from=dt_now - date_time.timedelta(minutes=interval * 2),
                        dt_to=dt_now,
                        interval=tinvest.CandleResolution.min15
                    )
                    if len(candle) == 0:
                        #print(f'error save candle: {tic}\n{dt_now - date_time.timedelta(minutes=15)}\n{dt_now - date_time.timedelta(seconds=30)}\n___________________')
                        pass
                    else:
                        candle_to_save = None
                        for cn in candle:
                            if cn.time == dt_candle:
                                candle_to_save = cn

                        candle = candle_to_save

                        if candle is None:
                            continue

                        if bb_cls_mass[ind].candle.time == candle.time:
                            continue

                        #print(f'candle to save {tic}: {candle}')

                        stoch_cls_mass[ind].candle = candle
                        bb_cls_mass[ind].candle = candle
                        supertrend_cls_mass[ind].candle = candle

                        indicators.Stoch(stoch_cls=stoch_cls_mass[ind])
                        indicators.Bollinger_bands(bollinger_bands_cls=bb_cls_mass[ind])
                        indicators.Supertrend(supertrend_cls=supertrend_cls_mass[ind])

                        stoch_cls_mass[ind].upd_last()
                        bb_cls_mass[ind].upd_last()
                        supertrend_cls_mass[ind].upd_last()

                if not buy_cnt == portfolio.get_list_cnt_buy():
                    #print('_________________\nsave\n_________________')
                    buy_cnt = portfolio.get_list_cnt_buy()
                    buy_price = portfolio.get_list_buy_price()


                    work_with_github.save_and_load_lists_float.save(
                        path='standart_strategy/saves/save_buy_info.txt',
                        ls=buy_cnt,
                        ls_name='buy_cnt'
                    )

                    work_with_github.save_and_load_lists_float.save(
                        path='standart_strategy/saves/save_buy_info.txt',
                        ls=buy_price,
                        ls_name='buy_price'
                    )

            time_to_sleep = (int(1e6) - datetime.now(tz=tz).microsecond) / int(1e6)

            time.sleep(time_to_sleep)

    await start_f(interval)

if __name__ == '__main__':
    #asyncio.run(main_program(percent=0.04))
    now_straregy()
