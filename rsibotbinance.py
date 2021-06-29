# https://www.youtube.com/watch?v=GdlFhF6gjKo
# https://github.com/hackingthemarkets/binance-tutorials/blob/master/rsibot/bot.py

import websocket
import json
import pprint
import talib
import numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05
closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(
            side=side, quantity=quantity, symbol=symbol, type=order_type)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position
    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)
        print("len closes")
        print(len(closes))
        print("period config")
        print(RSI_PERIOD)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            print("np_closes")
            print(np_closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            print("RSI_OVERBOUGHT")
            print(RSI_OVERBOUGHT)
            print(last_rsi > RSI_OVERBOUGHT)

            if last_rsi > RSI_OVERBOUGHT:  # 70
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(
                        SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")

            print("the current rsi is {}".format(last_rsi))
            print("RSI_OVERSOLD")
            print(RSI_OVERSOLD)
            print(last_rsi < RSI_OVERSOLD)

            if last_rsi < RSI_OVERSOLD:  # 30
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Buy! Buy! Buy!")
                    # put binance order logic here
                    order_succeeded = order(
                        SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)

ws.run_forever()
