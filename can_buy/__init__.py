from tradingview_ta import TA_Handler, Interval, Exchange
import tinvest

def can_buy(el : str):
    client = tinvest.SyncClient(TOKEN)
    instr = client.get_market_search_by_ticker(el)
    fg = instr.payload.instruments[0].figi
    orderbook = client.get_market_orderbook(figi=fg, depth='1').payload.trade_status
    return orderbook == client.get_market_orderbook(figi=fg, depth='1').payload.trade_status.normal_trading
