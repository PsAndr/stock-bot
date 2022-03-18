import tinvest
import time
import asyncio


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
