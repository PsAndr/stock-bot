import tinvest
import datetime as date_time
from datetime import datetime
import time
import asyncio

def get(tic : str, dt_min : datetime, dt_max : datetime, interval_ : tinvest.CandleResolution, candles : list, index : int, client):
    tz = date_time.timezone.utc
    flag_ = False
    fg = ''
    while not flag_:
        try:
            instr = client.get_market_search_by_ticker(tic)
            fg = instr.payload.instruments[0].figi
            flag_ = True
        except:
            time.sleep(1)
            flag_ = False
    flag_ = False
    candle = tinvest.Candles
    while not flag_:
        try:
            candle = client.get_market_candles(figi=fg, from_=dt_min, to=dt_max, interval=interval_)
            candle = candle.payload.candles
            flag_ = True
        except:
            time.sleep(1.5)
            continue

    while True:
        if candles[-1] != index:
            time.sleep(0.01)
            continue
        candles.pop()
        candles += candle
        candles.append(index + 1)
        #print(index)
        return
