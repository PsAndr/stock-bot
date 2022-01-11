from tradingview_ta import TA_Handler, Interval, Exchange
import time

spis = ['IRAO', 'VTBR', 'SBER', 'GAZP', 'RUAL', 'DSKY', 'MTSS', 'FIVE', 'MVID']
lasts = {'IRAO' : -1, 'VTBR' : -1, 'SBER' : -1, 'GAZP' : -1, 'RUAL' : -1, 'DSKY' : -1, 'MTSS' : -1, 'FIVE' : -1, 'MVID' : -1}
lastm = {'IRAO' : -1, 'VTBR' : -1, 'SBER' : -1, 'GAZP' : -1, 'RUAL' : -1, 'DSKY' : -1, 'MTSS' : -1, 'FIVE' : -1, 'MVID' : -1}
order = {'IRAO' : 'buy', 'VTBR' : 'buy', 'SBER' : 'buy', 'GAZP' : 'buy', 'RUAL' : 'buy', 'DSKY' : 'buy', 'MTSS' : 'buy', 'FIVE' : 'buy', 'MVID' : 'buy'}
buy = {'IRAO' : 0, 'VTBR' : 0, 'SBER' : 0, 'GAZP' : 0, 'RUAL' : 0, 'DSKY' : 0, 'MTSS' : 0, 'FIVE' : 0, 'MVID' : 0}
ans = {'IRAO' : 0, 'VTBR' : 0, 'SBER' : 0, 'GAZP' : 0, 'RUAL' : 0, 'DSKY' : 0, 'MTSS' : 0, 'FIVE' : 0, 'MVID' : 0}
while 1 == 1:
    for el in spis:
        ticker = TA_Handler(
            symbol=el,
            screener="russia",
            exchange="MOEX",
                interval=Interval.INTERVAL_30_MINUTES
        )
        analysis = ticker.get_analysis()
        rsi = analysis.indicators["RSI"]
        mm = analysis.indicators["MACD.macd"]
        ms = analysis.indicators["MACD.signal"]
        sk = analysis.indicators["Stoch.K"]
        sd = analysis.indicators["Stoch.D"]
        close = analysis.indicators["close"]
        
        if (sk - sd > 0 and lasts[el] < 0) and (mm - ms > 0) and order[el] == 'buy':
            order[el] = 'sell'
            buy[el] = close
            print(el, 'buy', close)
            #request to buy
        if (mm - ms > 0 and lastm[el] < 0) and (sk - sd > 0) and order[el] == 'buy':
            order[el] = 'sell'
            buy[el] = close
            print(el, 'buy', close)
            #request to buy
        if (sk - sd <= 0) and order[el] == 'sell':
            order[el] = 'buy'
            ans[el] += (buy[el] - close) / close * 100
            print(el, 'sell', close)
            #request to sell
        
        lasts[el] = sk - sd
        lastm[el] = mm - ms
    print('1step')
    time.sleep(1800)
    



