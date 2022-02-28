from tradingview_ta import TA_Handler, Interval, Exchange
import tinvest

def can_buy(el : str):
    TOKEN = "t.WVpg6thNk00O9Vd8P4vrne6om7zDgWaGIsKH6TqdRKgT2giER_3Lqp7w9DI7NYdjPWF4AXkj6MRNP5G51zp2lQ"
    S_TOKEN = "t.gJWIDbsjDOGnbAl2y-pm5kzEIxljV-kWYb1To6Skr4STriOvfDp4q4xwvFzuLzaXxWZt2UzRXysejROedAS1TQ"
    client = tinvest.SyncClient(TOKEN)
    instr = client.get_market_search_by_ticker(el)
    fg = instr.payload.instruments[0].figi
    orderbook = client.get_market_orderbook(figi=fg, depth='1').payload.trade_status
    return orderbook == client.get_market_orderbook(figi=fg, depth='1').payload.trade_status.normal_trading
