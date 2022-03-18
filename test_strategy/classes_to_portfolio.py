import tinvest
from collections import deque
from datetime import datetime
import work_with_tinvest
from work_with_tinvest import get_information_stock
from copy import deepcopy


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

    def sell(self, sell_cost : float, dt : datetime = None, cnt_sell : int = -1, commission : float = 0.04):
        to_return = dict()
        to_return['percent'] = 0.0
        to_return['plus'] = 0.0
        to_return['commision'] = 0.0
        to_return['cost'] = 0.0
        to_return['datetime'] = None
        if cnt_sell == -1:
            cnt_sell = self.cnt_buy
        if cnt_sell > self.cnt_buy or cnt_sell <= 0:
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
        return to_return

    def buy(self, buy_price : float, cnt_buy : int, dt : datetime = None):
        to_return = dict()
        to_return['cost'] = 0.0
        to_return['datetime'] = None
        if self.cnt_buy > 0:
            return to_return
        to_return['cost'] = buy_price * cnt_buy * self.cnt_in_lot
        to_return['datetime'] = dt
        self.cnt_buy = deepcopy(cnt_buy)
        self.buy_price = deepcopy(buy_price)
        self.operations.append(Operation(type_op='buy', cost_op=buy_price, ticker=self.ticker, dt=dt))
        return to_return

    def get_operations(self, type_op : str):
        to_return = list()
        for op in self.operations:
            if op.tupe_op == type_op:
                to_return.append(op)
        return to_return

    def price_now(self):
        return self.portfolio.price_now_figi(figi=self.figi)

    def get_candles(self, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        return self.portfolio.get_candles_figi(figi=self.figi, dt_from=dt_from, dt_to=dt_to, interval=interval)

class Portfolio:
    def __init__(self, spis : list):
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

    def price_now_figi(self, figi : str):
        return self.Tinvest_cls.get_price_now_figi(figi=figi)

    def get_candles_figi(self, figi : str, dt_from : datetime, dt_to : datetime, interval : tinvest.CandleResolution):
        return self.Tinvest_cls.get_candles_figi(dt_from=dt_from, dt_to=dt_to, interval=interval)
