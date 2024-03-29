import asyncio
import time

import tinvest
from collections import deque
from datetime import datetime
import work_with_tinvest
from work_with_tinvest import get_information_stock
from copy import deepcopy
import work_with_github


class Operation:
    def __init__(self, type_op : str, cost_op : float, ticker : str, dt : datetime):
        self.type_op = type_op
        self.cost_op = cost_op
        self.ticker = ticker
        self.dt = dt


class Stock:
    def __init__(self, cnt_in_lot : int, ticker : str, figi : str, portfolio):
        self.cnt_buy = 0
        self.ticker = ticker
        self.figi = figi
        self.cnt_in_lot = cnt_in_lot
        self.buy_price = 0.0
        self.plus = 0.0
        self.last_price = 0.0
        self.now_price = 0.0
        self.max_cost = 0.0
        self.operations = deque()
        self.portfolio = portfolio
        self.stop_loss = 0.0
        self.total_plus_percent = 0.0

    def __deepcopy__(self, memodict):
        my_copy = type(self)(cnt_in_lot=deepcopy(self.cnt_in_lot), ticker=deepcopy(self.ticker), figi=deepcopy(self.figi), portfolio=self.portfolio)
        my_copy.cnt_buy = deepcopy(self.cnt_buy)
        my_copy.buy_price = deepcopy(self.buy_price)
        my_copy.plus = deepcopy(self.plus)
        my_copy.max_cost = deepcopy(self.max_cost)
        my_copy.operations = deepcopy(self.operations)
        my_copy.last_price = deepcopy(self.last_price)
        my_copy.now_price = deepcopy(self.now_price)
        my_copy.stop_loss = deepcopy(self.stop_loss)
        my_copy.total_plus_percent = deepcopy(self.total_plus_percent)
        return my_copy

    def sell(self, sell_cost : float, dt : datetime = None, cnt_sell : int = -1, to_log_flag : bool = True):
        to_return = dict()
        to_return['ticker'] = self.ticker
        to_return['percent'] = 0.0
        to_return['plus'] = 0.0
        to_return['commision'] = 0.0
        to_return['sell price'] = sell_cost
        to_return['cost'] = 0.0
        to_return['datetime'] = None
        to_return['type'] = 'sell'
        commission = deepcopy(self.portfolio.commission)
        if cnt_sell == -1:
            cnt_sell = self.cnt_buy
        if cnt_sell > self.cnt_buy or cnt_sell <= 0:
            if to_log_flag:
                self.to_log_operation(to_return)
            return to_return
        commission /= 100
        minus_from_comm = self.buy_price * self.cnt_in_lot * commission + sell_cost * self.cnt_in_lot * commission
        a = self.cnt_in_lot * sell_cost * cnt_sell
        b = self.cnt_in_lot * self.buy_price * self.cnt_buy
        self.total_plus_percent += ((a - b) / b) * 100.0
        to_return['plus'] = a - b - minus_from_comm
        to_return['commision'] = minus_from_comm
        to_return['percent'] = ((a - b) / b) * 100.0
        to_return['cost'] = sell_cost * cnt_sell * self.cnt_in_lot
        to_return['datetime'] = dt
        to_return['total plus percent'] = self.total_plus_percent
        self.stop_loss = 0.0
        self.cnt_buy -= cnt_sell
        if self.cnt_buy == 0:
            self.buy_price = 0.0
            self.max_cost = 0.0
        self.plus += to_return['plus']
        self.operations.append(Operation(type_op='sell', cost_op=sell_cost, ticker=self.ticker, dt=dt))
        if to_log_flag:
            self.to_log_operation(to_return)
            self.to_log_github(to_return)
        return to_return

    def buy(self, buy_price : float, cnt_buy : int, dt : datetime = None, to_log_flag : bool = True):
        to_return = dict()
        to_return['ticker'] = self.ticker
        to_return['buy price'] = buy_price
        to_return['cost'] = 0.0
        to_return['datetime'] = None
        to_return['type'] = 'buy'
        if self.cnt_buy > 0:
            if to_log_flag:
                self.to_log_operation(to_return)
            return to_return
        to_return['cost'] = buy_price * cnt_buy * self.cnt_in_lot
        to_return['datetime'] = dt
        self.cnt_buy = deepcopy(cnt_buy)
        self.buy_price = deepcopy(buy_price)
        self.operations.append(Operation(type_op='buy', cost_op=buy_price, ticker=self.ticker, dt=dt))
        if to_log_flag:
            self.to_log_operation(to_return)
            self.to_log_github(to_return)
        return to_return

    def get_operations(self, type_op : str):
        to_return = list()
        for op in self.operations:
            if op.tupe_op == type_op:
                to_return.append(op)
        return to_return

    def price_now(self):
        pr_nw = self.portfolio.price_now_figi(figi=self.figi)
        self.upd_last_price()
        self.now_price = pr_nw
        return pr_nw

    def upd_last_price(self):
        self.last_price = deepcopy(self.now_price)

    def get_candles(self, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        return self.portfolio.get_candles_figi(figi=self.figi, dt_from=dt_from, dt_to=dt_to, interval=interval)

    def candle_now(self, interval : tinvest.CandleResolution):
        candle = self.portfolio.get_candle_now_figi(figi=self.figi, interval=interval)
        price_now = self.price_now()
        candle = work_with_tinvest.work_with_candle.update_candle(candle=candle, price_now=price_now)
        return candle

    def can_buy(self):
        el = self.portfolio.can_buy_figi(figi=self.figi)
        time.sleep(0.5)
        return el

    @staticmethod
    def to_log_operation(*args):
        args = args[0]
        for key in args:
            print('{0}: {1}'.format(key, args[key]))
        print('________________________')

    @staticmethod
    def to_log_github(dct: dict):
        s = work_with_github.convert_dict_to_str.convert(dct) + '________________________\n'
        work_with_github.save_logs.save('standart_strategy/logs.txt', s)


class Stock_async:
    def __init__(self, cnt_in_lot : int, ticker : str, figi : str, portfolio):
        self.cnt_buy = 0
        self.ticker = ticker
        self.figi = figi
        self.cnt_in_lot = cnt_in_lot
        self.buy_price = 0.0
        self.plus = 0.0
        self.max_cost = 0.0
        self.operations = deque()
        self.portfolio = portfolio

    def __deepcopy__(self, memodict):
        my_copy = type(self)(cnt_in_lot=deepcopy(self.cnt_in_lot), ticker=deepcopy(self.ticker), figi=deepcopy(self.figi), portfolio=self.portfolio)
        my_copy.cnt_buy = deepcopy(self.cnt_buy)
        my_copy.buy_price = deepcopy(self.buy_price)
        my_copy.plus = deepcopy(self.plus)
        my_copy.max_cost = deepcopy(self.max_cost)
        my_copy.operations = deepcopy(self.operations)
        return my_copy

    def sell(self, sell_cost : float, dt : datetime = None, cnt_sell : int = -1, to_log_flag : bool = True):
        to_return = dict()
        to_return['ticker'] = self.ticker
        to_return['percent'] = 0.0
        to_return['plus'] = 0.0
        to_return['commision'] = 0.0
        to_return['cost'] = 0.0
        to_return['datetime'] = None
        to_return['type'] = 'sell'
        commission = deepcopy(self.portfolio.commission)
        if cnt_sell == -1:
            cnt_sell = self.cnt_buy
        if cnt_sell > self.cnt_buy or cnt_sell <= 0:
            if to_log_flag:
                self.to_log_operation(to_return)
            return to_return
        commission /= 100
        minus_from_comm = self.buy_price * self.cnt_in_lot * commission + sell_cost * self.cnt_in_lot * commission
        a = self.cnt_in_lot * sell_cost * cnt_sell
        b = self.cnt_in_lot * self.buy_price * self.cnt_buy
        to_return['plus'] = a - b - minus_from_comm
        to_return['commision'] = minus_from_comm
        to_return['percent'] = ((a - b) / b) * 100.0
        to_return['cost'] = sell_cost * cnt_sell * self.cnt_in_lot
        to_return['datetime'] = dt
        self.cnt_buy -= cnt_sell
        if self.cnt_buy == 0:
            self.buy_price = 0.0
            self.max_cost = 0.0
        self.plus += to_return['plus']
        self.operations.append(Operation(type_op='sell', cost_op=sell_cost, ticker=self.ticker, dt=dt))
        if to_log_flag:
            self.to_log_operation(to_return)
        return to_return

    def buy(self, buy_price : float, cnt_buy : int, dt : datetime = None, to_log_flag : bool = True):
        to_return = dict()
        to_return['ticker'] = self.ticker
        to_return['cost'] = 0.0
        to_return['datetime'] = None
        to_return['type'] = 'buy'
        if self.cnt_buy > 0:
            if to_log_flag:
                self.to_log_operation(to_return)
            return to_return
        to_return['cost'] = buy_price * cnt_buy * self.cnt_in_lot
        to_return['datetime'] = dt
        self.cnt_buy = deepcopy(cnt_buy)
        self.buy_price = deepcopy(buy_price)
        self.operations.append(Operation(type_op='buy', cost_op=buy_price, ticker=self.ticker, dt=dt))
        if to_log_flag:
            self.to_log_operation(to_return)
        return to_return

    def get_operations(self, type_op : str):
        to_return = list()
        for op in self.operations:
            if op.tupe_op == type_op:
                to_return.append(op)
        return to_return

    async def price_now(self):
        return await self.portfolio.price_now_figi(figi=self.figi)

    async def get_candles(self, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        return await self.portfolio.get_candles_figi(figi=self.figi, dt_from=dt_from, dt_to=dt_to, interval=interval)

    async def candle_now(self, interval : tinvest.CandleResolution):
        candle = await self.portfolio.get_candle_now_figi(figi=self.figi, interval=interval)
        candle.c = await self.price_now()
        return candle

    @staticmethod
    def to_log_operation(*args):
        args = args[0]
        for key in args:
            print('{0}: {1}'.format(key, args[key]))
        print('________________________')


class Portfolio:
    def __init__(self, spis : list, commission : float = 0.04):
        self.commission = deepcopy(commission)
        self.Tinvest_cls = get_information_stock.Tinvest_class()
        self.stock_mass = list()
        for tic in spis:
            dic = self.get_figi_lot_from_ticker_stock(ticker=tic)
            figi = dic['figi']
            lot = dic['lot']
            self.stock_mass.append(Stock(ticker=tic, cnt_in_lot=lot, figi=figi, portfolio=self))

    def get_figi_lot_from_ticker_stock(self, ticker : str):
        figi = self.Tinvest_cls.get_figi_from_ticker(ticker=ticker)
        cnt_lot = self.Tinvest_cls.get_cnt_lot_from_ticker(ticker=ticker)
        return {'figi': figi, 'lot': cnt_lot}

    def get_stock_by_ticker(self, ticker: str):
        stock = None
        for st in self.stock_mass:
            if st.ticker == ticker:
                stock = st
        return stock

    def get_stock_by_figi(self, figi : str):
        stock = None
        for st in self.stock_mass:
            if st.figi == figi:
                stock = st
        return stock

    def price_now_figi(self, figi : str):
        return self.Tinvest_cls.get_price_now_figi(figi=figi)

    def get_candles_figi(self, figi : str, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        return self.Tinvest_cls.get_candles_figi(figi=figi, dt_from=dt_from, dt_to=dt_to, interval=interval)

    def get_candle_now_figi(self, figi : str, interval : tinvest.CandleResolution):
        return self.Tinvest_cls.get_candle_now_figi(figi=figi, interval=interval)

    def can_buy_figi(self, figi: str):
        return self.Tinvest_cls.can_buy_figi(figi=figi)

    def get_list_cnt_buy(self):
        to_return = list()
        for st in self.stock_mass:
            to_return.append(st.cnt_buy)
        return to_return

    def get_list_buy_price(self):
        to_return = list()
        for st in self.stock_mass:
            to_return.append(st.buy_price)
        return to_return

    def update_cnt_buy_ticker(self, dc: dict):
        for st in self.stock_mass:
            if st.ticker in dc:
                st.cnt_buy = dc[st.ticker]

    def update_buy_price_ticker(self, dc: dict):
        for st in self.stock_mass:
            if st.ticker in dc:
                st.buy_price = dc[st.ticker]

    def get_list_stop_loss(self):
        to_return = list()
        for st in self.stock_mass:
            to_return.append(st.stop_loss)
        return to_return

    def update_stop_loss_ticker(self, dc: dict):
        for st in self.stock_mass:
            if st.ticker in dc:
                st.stop_loss = dc[st.ticker]


class Portfolio_async:
    def __init__(self, spis : list, commission : float = 0.04):
        self.commission = deepcopy(commission)
        self.Tinvest_cls = get_information_stock.Tinvest_class_async()
        self.Tinvest_cls_to_init = get_information_stock.Tinvest_class()
        self.stock_mass = list()
        self.__int_stocks__(spis=spis)

    async def stop_work(self):
        await self.Tinvest_cls.client.close()

    def __int_stocks__(self, spis : list):
        for tic in spis:
            dic = self.get_figi_lot_from_ticker_stock(ticker=tic)
            figi = dic['figi']
            lot = dic['lot']
            self.stock_mass.append(Stock_async(ticker=tic, cnt_in_lot=lot, figi=figi, portfolio=self))

    def get_figi_lot_from_ticker_stock(self, ticker : str):
        figi = self.Tinvest_cls_to_init.get_figi_from_ticker(ticker=ticker)
        cnt_lot = self.Tinvest_cls_to_init.get_cnt_lot_from_ticker(ticker=ticker)
        return {'figi': figi, 'lot': cnt_lot}

    def get_stock_by_ticker(self, ticker : str):
        stock = None
        for st in self.stock_mass:
            if st.ticker == ticker:
                stock = st
        return stock

    def get_stock_by_figi(self, figi : str):
        stock = None
        for st in self.stock_mass:
            if st.figi == figi:
                stock = st
        return stock

    async def price_now_figi(self, figi : str):
        return await self.Tinvest_cls.get_price_now_figi(figi=figi)

    async def get_candles_figi(self, figi : str, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        return await self.Tinvest_cls.get_candles_figi(figi=figi, dt_from=dt_from, dt_to=dt_to, interval=interval)

    async def get_candle_now_figi(self, figi : str, interval : tinvest.CandleResolution):
        return await self.Tinvest_cls.get_candle_now_figi(figi=figi, interval=interval)
