import json
import sqlite3
import threading

import pandas
import yfinance
import requests
import websocket


def get_data_from_yfinance(symbol,period="1mo",interval="1d",start_date=None,end_date=None):
    ticker = yfinance.Ticker(ticker=symbol)

    df = ticker.history(period=period,interval=interval,start=start_date,end=end_date)
    df = pandas.DataFrame(df).drop(columns=["Dividends","Stock Splits"])

    return df

def get_data_from_binance_http(symbol,period=30,interval="1d",start_date=None,end_date=None):
    base_url = "https://api1.binance.com"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": period
    }
    if start_date!=None:
        params["startTime"] = start_date
    if end_date!=None:
        params["endTime"] = end_date

    def _check_connection():    #Check for connection, in case base url in maintenance
        rsp = requests.get(url=f"{base_url}/api/v3/ping")
        if rsp.status_code != 200:
            print(f"\033[!] Cannot reach binance api gateway {base_url}, try another base url instaed\033")
            quit(-1)
    _check_connection()

    rsp = requests.get(url=f"{base_url}/api/v3/klines",params=params)
    df = pandas.DataFrame(rsp.json(), columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","num_trades",
        "taker_base_vol","taker_quote_vol","ignore"
    ]).drop(columns=["close_time","qav","num_trades","taker_base_vol","taker_quote_vol","ignore"])
    df["open_time"] = pandas.to_datetime(df["open_time"], unit="ms")

    return df

def get_data_from_binance_websocket(symbol,interval="1d"):
    def on_message(wsapp,message):
        data = json.loads(message)

        print(f"\x20\x20\x20[-] Todays' {symbol.upper()} real time price: {data["k"]["c"]}")

    def on_open(wsapp):
        threading.Timer(10,ws.close).start() #Close connection after 10s

    ws = websocket.WebSocketApp(f"wss://stream.binance.com:443/ws/{symbol}@kline_{interval}", on_open=on_open, on_message=on_message)
    ws.run_forever()

    return 
    
def get_data_from_database(db_path="MSFT.sqlite"):
    conn = sqlite3.connect(db_path)
    df = pandas.read_sql("SELECT * FROM MSFT",conn)
    
    return df

def get_data_from_local(xlsx_path="GOOG.xlsx"):
    df = pandas.read_excel(xlsx_path)

    return df
            

if __name__ == "__main__":
    print(f"[+] Read AAPL price and volume from last 30 days")
    df_AAPL =  get_data_from_yfinance(symbol="AAPL",period="1mo")
    print(df_AAPL.head())

    print(f"[+] Read BTC-USDT price and volume from last 30 days")
    df_BTCUSDT = get_data_from_binance_http(symbol="BTCUSDT",period=30)
    print(df_BTCUSDT.head())

    print(f"[+] Read ETH-USDT price in real time")
    get_data_from_binance_websocket(symbol="ethusdt",interval="1d")

    print(f"[+] Read MSFT price and volume from last 30 days")
    df_MSFT = get_data_from_database("MSFT.sqlite")
    print(df_MSFT.head())

    print(f"[+] Read MSFT price and volume from last 30 days")
    df_GOOG = get_data_from_local("MSFT.xlsx")
    print(df_GOOG.head())












