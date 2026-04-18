import json
import sqlite3

import pandas
import yfinance
import tushare
import requests
import websocket

ON_DEBUG = True

# Yahoo finance module
def func1():
    ticker = yfinance.Ticker("AAPL")
    df = ticker.history(period="1mo", interval="1d")

    print("[+] Get Kline from yfinance:")
    print(df.head(), end="\n\n")

    # Save the dataframe
    df.to_excel("./AAPL.xlsx", index=False)

    conn = sqlite3.connect("./AAPL.sqlite")
    df.to_sql("kline", conn, if_exists="replace", index=False)
    conn.close()

# Tushare module
def func2():
    pro = tushare.pro_api("<Your Token>")
    df = pro.daily(ts_code='000001.SZ', start_date='20260301', end_date='20260401')

    print("[+] Get Kline from tushare:")
    print(df.head(), end="\n\n")

# Binance HTTP API
def func3():
    req = requests.Request(method="GET", url="https://api.binance.com/api/v3/klines", params={
        "symbol":"BTCUSDT",
        "interval":"1d",
        "limit":30
    })

    sess = requests.session()
    rsp = sess.send(sess.prepare_request(req))
    df = pandas.DataFrame(rsp.json())

    print("[+] Get Kline from HTTP Binance:")
    print(df.head(), end="\n\n")

    # Or, do it with requests quick api
    rsp = requests.get(url="https://api.binance.com/api/v3/klines", params={
        "symbol":"BTCUSDT",
        "interval":"1d",
        "limit":30
    })
    df = pandas.DataFrame(rsp.json()) 

    print("[+] Get Kline from HTTP Binance (Quick API):")
    print(df.head(), end="\n\n")

# Binance WSS API
def on_open(wsapp):
    wsapp.send(json.dumps({
        "method":"SUBSCRIBE",
        "params":["btcusdt@kline_1m"],
        "id":1
    }))

    print("[+] Websocket opened")

def on_message(wsapp, message):
    msg = json.loads(message)
    print(f"\x20\x20\x20[-] Received kline: {msg.get("k")["c"]}")

def func4():
    ws = websocket.WebSocketApp(url="wss://stream.binance.com:9443/ws",
                                on_open=on_open,
                                on_message=on_message)
    ws.run_forever()

# SQLite database
def func5():
    conn = sqlite3.connect("./AAPL.sqlite")
    df = pandas.read_sql("SELECT * FROM kline", conn)
    
    print("[+] Get Kline from SQLite3:")
    print(df.head(), end="\n\n")

    # Or do it with sqlite3 cursor
    cursor = conn.cursor()

    res = cursor.execute("SELECT * FROM kline")
    df = pandas.DataFrame(res.fetchall())

    print("[+] Get Kline from SQLite3:")
    print(df.head(), end="\n\n")

# Local excel file
def func6():
    df = pandas.read_excel("./AAPL.xlsx")

    print("[+] Get Kline from local file:")
    print(df.head(),end="\n\n")


if ON_DEBUG == True:
    func1()