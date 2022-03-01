from save_candles import save
from save_candles import datetime_to_list
from save_candles import get_new_candle
import threading
from datetime import datetime
import tzlocal
import can_buy
import time

def start_save(list_tickers : list):
    threading.Thread(target=threading_save, args=(list_tickers)).start()
    return

def threading_save(list_tickers : list):
    tz = tzlocal.get_localzone()
    while True:
        minute = datetime.now(tz).minute
        second = datetime.now(tz).second
        if (minute + 1) % 5 == 0 and second >= 58:
            for ticker in list_tickers:
                if can_buy.can_buy(ticker) or True:
                    candle = get_new_candle.get_candle(ticker)
                    dt = datetime(datetime.now(tz).year, datetime.now(tz).month,
                                  datetime.now(tz).day, datetime.now(tz).hour, minute - 14, 0)
                    save.save_new_candle(dt, candle, ticker, minutes_of_candle=5)
        time_sleep = 58 - datetime.now(tz).second
        if time_sleep <= 0:
            time_sleep += 60
        time_sleep -= 1
        time_correct = 1000000 - datetime.now(tz).microsecond
        time_sleep += time_correct / 1000000
        print('step end', datetime.now(tz))
        time.sleep(time_sleep)