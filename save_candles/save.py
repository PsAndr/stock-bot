import time
from tradingview_ta import TA_Handler, Interval, Exchange
from datetime import datetime
from github import Github
from tzlocal import get_localzone
from  save_candles import get_new_candle
from save_candles import datetime_to_list

def save_new_candle(dt : datetime, save_candle : list, ticker : str, count_candles_to_save : int = 10, minutes_of_candle : int = 15):
    token = ''
    with open('token.txt', 'r') as f:
        token = f.read()
        token = token.replace('\n', ' ')
    g = Github('ghp_' + token)

    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents("save_candle/save_candles.txt")

    s = contents.decoded_content.decode()
    l = []
    f = s.split('\n')
    #годы месяцы дни часы минуты секунды
    #print(datetime(2020, 1, 15, 12, 30, 14) - datetime(2020, 1, 15, 11, 30, 10))

    flag_ticker = False

    for i in f:
        if len(i) == 0:
            continue
        if i[-1] != ':':
            j = list(map(float, i.split()))
            delta_minute = (dt - datetime(int(j[0]), int(j[1]), int(j[2]), int(j[3]), int(j[4]), int(j[5]))).seconds / 60
            print(delta_minute)
            print(i)
            print()
            if delta_minute - (count_candles_to_save * minutes_of_candle) < 0:
                l.append(i)
        else:
            l.append(i)
            if i == ticker + ':':
                flag_ticker = True
                l += [datetime_to_list.convert(dt) + save_candle]

    if not flag_ticker:
        l += [ticker + ':']
        l += [datetime_to_list.convert(dt) + save_candle]

    s = ''

    for i in l:
        if type(i) == list:
            for j in i:
                s += str(j) + ' '
            s += '\n'
            continue
        s += str(i) + '\n'

    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents("save_candle/save_candles.txt")

    repo.update_file(contents.path, "save_candles", s, contents.sha, branch='main')



