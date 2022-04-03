import tinvest
import time
import asyncio
import datetime as date_time
from work_with_datetime import datetime_split_day
from work_with_datetime import compare_datetime
from datetime import datetime
from copy import deepcopy


class Tinvest_class:
    def __init__(self):
        self.client = tinvest.SyncClient(self.get_Token())

    def get_Token(self):
        TOKEN = "t.WVpg6thNk00O9Vd8P4vrne6om7zDgWaGIsKH6TqdRKgT2giER_3Lqp7w9DI7NYdjPWF4AXkj6MRNP5G51zp2lQ"
        S_TOKEN = "t.gJWIDbsjDOGnbAl2y-pm5kzEIxljV-kWYb1To6Skr4STriOvfDp4q4xwvFzuLzaXxWZt2UzRXysejROedAS1TQ"
        return TOKEN

    def get_figi_from_ticker(self, ticker : str):
        flag_ = False
        fg = ''
        while not flag_:
            try:
                instr = self.client.get_market_search_by_ticker(ticker)
                fg = instr.payload.instruments[0].figi
                flag_ = True
                time.sleep(0.2)
            except:
                time.sleep(1.5)
                flag_ = False
        return fg

    def get_cnt_lot_from_ticker(self, ticker : str):
        flag_ = False
        cnt = 0
        while not flag_:
            try:
                instr = self.client.get_market_search_by_ticker(ticker)
                cnt = instr.payload.instruments[0].lot
                flag_ = True
                time.sleep(0.2)
            except:
                time.sleep(1.5)
                flag_ = False
        return cnt

    def get_price_now_figi(self, figi : str):
        return float(self.client.get_market_orderbook(figi=figi, depth=1).payload.last_price)

    def get_candles_figi(self, figi : str, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        dt_l = dt_from + date_time.timedelta(seconds=0)
        dt_r = datetime_split_day.datetime_per_day(dt_from, dt_to)
        candles = list()
        #print(f'candles figi start: {dt_from}, {dt_to}')
        while not compare_datetime.compare(dt_l, dt_to):
            #print(f'candles figi: {dt_l}, {dt_r}, {dt_to}')
            delta = date_time.timedelta(seconds=1)
            candles_day = self.get_candles_day_figi(figi=figi, dt_from=dt_l, dt_to=dt_r, interval=interval)
            candles += candles_day
            dt_l = dt_r + delta
            dt_r = datetime_split_day.datetime_per_day(dt_l, dt_to)
        #print(f'candles to return: {candles}')
        return candles

    def get_candles_day_figi(self, figi : str, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        flag = False
        candles_day = None
        while not flag:
            try:
                candles_day = self.client.get_market_candles(figi=figi, from_=dt_from, to=dt_to, interval=interval).payload.candles
                flag = True
                time.sleep(0.2)
            except:
                #print(f'error to load candles day: {dt_from} - {dt_to}')
                time.sleep(1.5)
        return candles_day

    def get_candle_now_figi(self, figi : str, interval : tinvest.CandleResolution):
        dt_now = datetime.now(tz=date_time.timezone.utc)
        dt_l = deepcopy(dt_now)
        if interval[-3:] == 'min':
            interval_minutes = int(interval[:-3])
            flag = False
            candle = None
            while not flag:
                candle = self.get_candles_figi(figi=figi, dt_from=datetime_split_day.datetime_begin_of_day(dt_l),
                                               dt_to=dt_now, interval=interval)
                if len(candle) > 0:
                    flag = True
                    candle = candle[-1]
                    break
                #print(f'error to get candle now {figi}')
                dt_l = datetime_split_day.datetime_begin_of_day(dt_l) - date_time.timedelta(seconds=1)
                time.sleep(1)
            return candle


class Tinvest_class_async:
    def __init__(self):
        self.client = tinvest.AsyncClient(self.get_Token())

    def get_Token(self):
        TOKEN = "t.WVpg6thNk00O9Vd8P4vrne6om7zDgWaGIsKH6TqdRKgT2giER_3Lqp7w9DI7NYdjPWF4AXkj6MRNP5G51zp2lQ"
        S_TOKEN = "t.gJWIDbsjDOGnbAl2y-pm5kzEIxljV-kWYb1To6Skr4STriOvfDp4q4xwvFzuLzaXxWZt2UzRXysejROedAS1TQ"
        return TOKEN

    async def get_figi_from_ticker(self, ticker : str):
        flag_ = False
        fg = ''
        while not flag_:
            try:
                instr = await self.client.get_market_search_by_ticker(ticker)
                fg = instr.payload.instruments[0].figi
                flag_ = True
                await asyncio.sleep(0.2)
            except:
                await asyncio.sleep(0.8)
                print('error', 'get_figi')
                flag_ = False
        return fg

    async def get_cnt_lot_from_ticker(self, ticker : str):
        flag_ = False
        cnt = 0
        while not flag_:
            try:
                instr = await self.client.get_market_search_by_ticker(ticker)
                cnt = instr.payload.instruments[0].lot
                flag_ = True
                await asyncio.sleep(0.2)
            except:
                await asyncio.sleep(0.8)
                print('error', f'get_lot: {ticker}')
                flag_ = False
        return cnt

    async def get_price_now_figi(self, figi : str):
        orderbook = await self.client.get_market_orderbook(figi=figi, depth=1)
        return float(orderbook.payload.last_price)

    async def get_candles_figi(self, figi : str, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        dt_l = dt_from + date_time.timedelta(seconds=0)
        dt_r = datetime_split_day.datetime_per_day(dt_from, dt_to)
        candles = list()
        while (dt_to.day - dt_l.day) > 0 or (dt_to.year - dt_l.year) > 0 or (dt_to.month - dt_l.month) > 0 or (
                dt_to.hour - dt_l.hour) > 0 or (dt_to.second - dt_l.second) > 1:
            delta = date_time.timedelta(seconds=1)
            candles_day = await self.get_candles_day_figi(figi=figi, dt_from=dt_l, dt_to=dt_r, interval=interval)
            candles += candles_day
            dt_l = dt_r + delta
            dt_r = datetime_split_day.datetime_per_day(dt_l, dt_to)
        return candles

    async def get_candles_day_figi(self, figi : str, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        flag = False
        candles_day = None
        while not flag:
            try:
                candles_day = await self.client.get_market_candles(figi=figi, from_=dt_from, to=dt_to, interval=interval)
                candles_day = candles_day.payload.candles
                flag = True
                await asyncio.sleep(0.2)
            except:
                await asyncio.sleep(0.8)
                print('error', f'get_day: {figi}')
        return candles_day

    async def get_candle_now_figi(self, figi : str, interval : tinvest.CandleResolution):
        dt_now = datetime.now(tz=date_time.timezone.utc)
        if interval[-3:] == 'min':
            interval_minutes = int(interval[:-3])
            t_d = date_time.timedelta(minutes=interval_minutes)
            t_d_2 = date_time.timedelta(milliseconds=1)
            flag = False
            candle = None
            while not flag:
                dt_now = datetime.now(tz=date_time.timezone.utc)
                candle = await self.get_candles_figi(figi=figi, dt_from=dt_now - t_d + t_d_2, dt_to=dt_now + t_d - t_d_2, interval=interval)
                if len(candle) == 0:
                    t_d += date_time.timedelta(minutes=interval_minutes)
                    await asyncio.sleep(0.8)
                else:
                    candle = candle[0]
                    break
            return candle
