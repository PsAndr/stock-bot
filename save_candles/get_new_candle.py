from tradingview_ta import TA_Handler, Interval, Exchange

def get_candle(ticker : str, screener : str = 'russia', exchange : str = 'MOEX', interval : Interval = Interval.INTERVAL_15_MINUTES, indicators : list = ["BB.lower", "BB.upper", "close", "high", "low"]):
    tic = TA_Handler(
        symbol=ticker,
        screener=screener,
        exchange=exchange,
        interval=interval
    )
    answer = []
    analysis = tic.get_analysis()
    for i in indicators:
        answer.append(analysis.indicators[i])
    return answer
