import tinvest
from decimal import Decimal
from datetime import datetime


def update_candle(candle: tinvest.Candle, price_now):
    price_now = Decimal(price_now)
    candle.c = price_now
    if price_now > candle.h:
        candle.h = price_now
    if price_now < candle.l:
        candle.l = price_now
    return candle


def make_candle(close, open, high, low, dt: datetime, figi: str):
    pass
