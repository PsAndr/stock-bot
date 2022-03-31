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
from can_buy import can_buy
import standart_strategy
import asyncio

asyncio.run(standart_strategy.main_program())
exit(0)
'''
TOKEN = "t.WVpg6thNk00O9Vd8P4vrne6om7zDgWaGIsKH6TqdRKgT2giER_3Lqp7w9DI7NYdjPWF4AXkj6MRNP5G51zp2lQ"
S_TOKEN = "t.gJWIDbsjDOGnbAl2y-pm5kzEIxljV-kWYb1To6Skr4STriOvfDp4q4xwvFzuLzaXxWZt2UzRXysejROedAS1TQ"
client = tinvest.SyncClient(TOKEN)

tz = get_localzone()
spis = []
token = ''
with open('token.txt', 'r') as f:
    token = f.read()
    token = token.replace('\n', ' ')
g = Github('ghp_' + token)

repo = g.get_user().get_repo("stock-bot")
contents = repo.get_contents("save.txt")


def save_elem(l):
    global repo
    global contents
    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents("save.txt")
    s = ''
    for i in l:
        if (type(i) == list):
            for j in i:
                s += str(j) + ' '
            s += '\n'
        else:
            s += str(i) + '\n'
    repo.update_file(contents.path, "save", s, contents.sha, branch='main')


def load_elem():
    global repo
    global contents
    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents("save.txt")

    l = []
    s = contents.decoded_content.decode()
    f = s.split('\n')

    for i in f:
        if len(i.split()) > 0:
            l.append(list(map(float, i.split())))

    return l


def logs_github(to_logs: list, len_logs: int = 200):
    global repo
    global contents
    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents("logs.txt")

    s = contents.decoded_content.decode()
    l = to_logs + ['']
    l += s.split('\n')

    if (len(l) > len_logs):
        l = l[:len_logs]
    s2 = ''

    for i in l:
        if type(i) == list:
            if i == []:
                continue
            for j in i:
                if type(j) == list:
                    for k in j:
                        s2 += str(k) + ' '
                else:
                    s2 += str(j) + ' '
                s2 += '\n'
        else:
            s2 += str(i) + '\n'

    repo.update_file(contents.path, "upd_logs", s2, contents.sha, branch='main')


with open('stock_spis.txt', 'r') as stock_spis:
    spis = list(stock_spis.read().split())

buy_cnt = [0] * len(spis)
buy_price = [0] * len(spis)
cnt_stock_lot = [1] * len(spis)
lastClose = [0] * len(spis)
TR = [deque()] * len(spis)
lastFinal_upperband = [0] * len(spis)
lastFinal_lowerband = [0] * len(spis)
lastBBlower = [0] * len(spis)
lastBBupper = [0] * len(spis)
lastSupertrend = [False] * len(spis)

lasts = [1] * len(spis)
lastm = [1] * len(spis)

my_plus = 0
list_print = []

try:
    buy_cnt, buy_price, my_plus = load_elem()
    my_plus = my_plus[0]
except:
    buy_cnt, buy_price, my_plus = load_elem()
    my_plus = my_plus[0]

print(buy_cnt)
print(buy_price)

while len(buy_cnt) < len(spis):
    buy_cnt.append(0)
    buy_price.append(0)


def fun(ind, el):
    global my_plus
    global TR
    global lastClose
    global list_print
    global lastBBupper
    global lastBBlower

    ticker = TA_Handler(
        symbol=el,
        screener="russia",
        exchange="MOEX",
        interval=Interval.INTERVAL_15_MINUTES
    )

    flag = True
    while flag:
        try:
            analysis = ticker.get_analysis()
            flag = False
        except:
            flag = True
            time.sleep(0.5)

    if not can_buy(el):
        return

    BBlower = analysis.indicators["BB.lower"]
    BBupper = analysis.indicators["BB.upper"]
    Close = analysis.indicators["close"]
    High = analysis.indicators["high"]
    Low = analysis.indicators["low"]

    if (lastClose[ind] == 0):
        lastClose[ind] = Close
        return

    TR[ind].append(max(High - Low, abs(High - lastClose[ind]), abs(Low - lastClose[ind])))

    if (len(TR[ind]) < 10):
        lastClose[ind] = Close
        lastBBlower[ind] = BBlower
        lastBBupper[ind] = BBupper
        return

    if (len(TR[ind]) > 10):
        TR[ind].popleft()

    ATR = numpy.mean(TR[ind])
    final_upperband = (High + Low) / 2 + 3 * ATR
    final_lowerband = (High + Low) / 2 - 3 * ATR

    if (lastFinal_upperband[ind] == 0):
        if (Close > lastFinal_upperband[ind]):
            supertrend = True
        # if current close price crosses below lowerband
        elif (Close < lastFinal_lowerband[ind]):
            supertrend = False
        lastFinal_upperband[ind] = final_upperband
        lastFinal_lowerband[ind] = final_lowerband
        lastSupertrend[ind] = supertrend

    if (Close > lastFinal_upperband[ind]):
        supertrend = True
    # if current close price crosses below lowerband
    elif (Close < lastFinal_lowerband[ind]):
        supertrend = False
    # else, the trend continues
    else:
        supertrend = lastSupertrend[ind]
        if (supertrend == True and final_lowerband < lastFinal_lowerband[ind]):
            final_lowerband = lastFinal_lowerband[ind]
        if (supertrend == False and final_upperband > lastFinal_upperband[ind]):
            final_upperband = lastFinal_upperband[ind]

    if (Close > BBlower and lastClose[ind] < lastBBlower[ind] and supertrend == True):
        ''''''and not (datetime.now(tz).hour - datetime.now(tz).utcoffset().total_seconds() / 3600 == 20 and datetime.now(tz).minute >= 30):''''''
        instr = client.get_market_search_by_ticker(el)
        fg = instr.payload.instruments[0].figi
        try:
            orderbook = (float)(client.get_market_orderbook(figi=fg, depth='1').payload.last_price)
        except:
            list_print[ind].append([el, 'error to get orderbook'])
        list_print[ind].append([el, 'buy', orderbook])
        # request to buy
        ''''''
        try:
            price_buy = comm(el, 1, 'Buy', Close, ind)
            buy_cnt[ind] = 1
            buy_price[ind] = price_buy
            list_print[ind].append([el, 'buy', price_buy])
        except:
            list_print[ind].append([el, 'error buy(1)'])
        ''''''
    random_el = 1

    if ((Close < BBupper and lastClose[ind] > lastBBupper[ind])):
        #or (datetime.now(tz).hour - datetime.now(tz).utcoffset().total_seconds() / 3600 == 20 and datetime.now(tz).minute >= 30)) and (buy_cnt[ind] > 0):
        instr = client.get_market_search_by_ticker(el)
        fg = instr.payload.instruments[0].figi
        try:
            orderbook = (float)(client.get_market_orderbook(figi=fg, depth='1').payload.last_price)
        except:
            list_print[ind].append([el, 'error to get orderbook'])
        list_print[ind].append([el, 'sell', orderbook])
        list_print[ind].append([buy_cnt[ind], (buy_cnt[ind] * orderbook * cnt_stock_lot[ind] - buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]) / (buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]), '\n'])
        list_print[ind].append([my_plus])
    # request to sell
        ''''''
        try:
            sell_price = comm(el, 1, 'Sell', Close, ind)
            my_plus += buy_cnt[ind] * sell_price * cnt_stock_lot[ind] - buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]
            list_print[ind].append([el, 'sell', sell_price])
            list_print[ind].append([buy_cnt[ind], (buy_cnt[ind] * sell_price * cnt_stock_lot[ind] - buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]) / (buy_cnt[ind] * buy_price[ind] * cnt_stock_lot[ind]), '\n'])
            list_print[ind].append([my_plus])  
            buy_cnt[ind] = 0
            buy_price[ind] = 0
        except:
            list_print[ind].append([el, 'error sell'])
        ''''''
    random_el = 1

    lastFinal_upperband[ind] = final_upperband
    lastFinal_lowerband[ind] = final_lowerband
    lastSupertrend[ind] = supertrend
    lastClose[ind] = Close
    lastBBlower[ind] = BBlower
    lastBBupper[ind] = BBupper

    # print(ans)


def comm(el, lots, operation, pr, ind):
    global list_print
    orderbook = pr
    instr = client.get_market_search_by_ticker(el)
    fg = instr.payload.instruments[0].figi
    try:
        orderbook = (float)(client.get_market_orderbook(figi=fg, depth='1').payload.last_price)
    except:
        list_print[ind].append([el, 'error to get orderbook'])
    request = tinvest.MarketOrderRequest(lots=lots, operation=operation)

    try:
        resp = client.post_orders_market_order(fg, request)
    except:
        random_el = 1

    return orderbook


def check_stocks():
    global list_print
    list_print = []
    procs = []

    for ind, el in enumerate(spis):
        proc = threading.Thread(target=fun, args=(ind, el))
        list_print.append([])
        proc.start()
        procs.append(proc)

    for proc in procs:
        proc.join()
    for i in list_print:
        for j in i:
            for k in j:
                print(k, end=' ')
            print()

    logs_github([datetime.now(tz)] + list_print)


def get_stock_in_lot():
    global spis
    global cnt_stock_lot
    for ind, el in enumerate(spis):
        instr = client.get_market_search_by_ticker(el).payload.instruments[0].lot
        cnt_stock_lot[ind] = instr


def ddos():
    global buy_cnt
    global buy_price
    global my_plus
    global repo
    global contents
    while True:
        tm = time.time()
        while (time.time() - tm <= 15 * 60 or datetime.now(tz).minute > 57 or (
                datetime.now(tz).minute > 13 and datetime.now(tz).minute < 16) or (
                       datetime.now(tz).minute > 28 and datetime.now(tz).minute < 31) or (
                       datetime.now(tz).minute > 43 and datetime.now(tz).minute < 46)):
            time.sleep(1)
            continue
        try:
            repo = g.get_user().get_repo("stock-bot")
            contents = repo.get_contents("save.txt")
            save_elem([buy_cnt, buy_price, my_plus])
            print('save complete')
        except:
            print("error to save")
            time.sleep(15 * 60)


proc = threading.Thread(target=ddos, args=())
proc.start()


def inf_f():
    while True:
        n = datetime.now(tz).minute
        tm = time.time()

        if not datetime.now(tz).hour - datetime.now(tz).utcoffset().total_seconds() / 3600 == 3:
            if n == 14:
                check_stocks()
            if n == 29:
                check_stocks()
            if n == 44:
                check_stocks()
            if n == 59:
                check_stocks()

        print('step end', time.time() - tm, datetime.now(tz))

        time_sleep = 58 - datetime.now(tz).second
        if time_sleep <= 0:
            time_sleep += 60
        time_sleep -= 1
        time_correct = 1000000 - datetime.now(tz).microsecond
        time_sleep += time_correct / 1000000
        time.sleep(time_sleep)


get_stock_in_lot()
print(cnt_stock_lot)
inf_f()'''
