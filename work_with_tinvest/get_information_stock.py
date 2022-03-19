import tinvest
import time
import asyncio
import datetime as date_time
from work_with_datetime import datetime_split_day
from datetime import datetime


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
        while (dt_to.day - dt_l.day) > 0 or (dt_to.year - dt_l.year) > 0 or (dt_to.month - dt_l.month) > 0 or (
                dt_to.hour - dt_l.hour) > 0 or (dt_to.second - dt_l.second) > 1:
            delta = date_time.timedelta(seconds=1)
            candles_day = self.get_candles_day_figi(figi=figi, dt_from=dt_l, dt_to=dt_r, interval=interval)
            candles += candles_day
            dt_l = dt_r + delta
            dt_r = datetime_split_day.datetime_per_day(dt_l, dt_to)
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
                flag = False
                time.sleep(1.5)
        return candles_day


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
                time.sleep(0.2)
            except:
                time.sleep(1.5)
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
                time.sleep(0.2)
            except:
                time.sleep(1.5)
                flag_ = False
        return cnt

    async def get_price_now_figi(self, figi : str):
        orderbook = await self.client.get_market_orderbook(figi=figi, depth=1)
        return float(orderbook.payload.last_price)
