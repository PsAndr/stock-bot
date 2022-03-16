import tinvest
from collections import deque
from datetime import datetime

class Operation:
    def __init__(self, type_op : str, cost_op : float, ticker : str, dt : datetime):
        self.type_op = type_op
        self.cost_op = cost_op
        self.ticker = ticker
        self.dt = dt


class Stock:
    def __init__(self, cnt_in_lot : int, ticker : str, figi : str):
        self.cnt_buy = 0
        self.ticker = ticker
        self.figi = figi
        self.cnt_in_lot = cnt_in_lot
        self.buy_price = 0.0
        self.plus = 0.0
        self.max_cost = 0.0
        self.operations = deque()

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
        minus_from_comm = self.buy_price * commission + sell_cost * commission
        a = self.cnt_in_lot * sell_cost * cnt_sell
        b = self.cnt_in_lot * self.buy_price * self.cnt_buy
        to_return['plus'] = a - b - minus_from_comm
        to_return['commision'] = minus_from_comm
        to_return['percent'] = b / (a - b) * 100.0
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
        self.cnt_buy = cnt_buy
        self.buy_price = buy_price
        self.operations.append(Operation(type_op='buy', cost_op=buy_price, ticker=self.ticker, dt=dt))
        return to_return

    def get_operations(self, type_op : str):
        to_return = list()
        for op in self.operations:
            if op.tupe_op == type_op:
                to_return.append(op)
        return to_return

class Portfolio:
    def __init__(self):
        pass