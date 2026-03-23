import json
import asyncio
from threading import Thread

import pandas 
import requests
import websockets
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


app = Dash(__name__)
app.layout = html.Div([
        html.H2("BTC/USDT 一分钟K线"),
        dcc.Graph(id='live-candlestick'),
        dcc.Interval(id='interval', interval=2000, n_intervals=0) 
    ])

df = None

# Fill old data from last 30 minutes
def initialize_df(symbol="BTCUSDT",interval="1m",limit=30):
    global df
    df = requests.get("https://api1.binance.com/api/v3/klines",params={
        "symbol":symbol,
        "interval":interval,
        "limit":limit
    })

    df = pandas.DataFrame(df.json(), columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","num_trades",
        "taker_base_vol","taker_quote_vol","ignore"
    ]).drop(columns=["volume","close_time","qav","num_trades","taker_base_vol","taker_quote_vol","ignore"])
    df["open_time"] = pandas.to_datetime(df["open_time"], unit="ms")
    df = df.iloc[0:-1]

initialize_df()

# Once websocket receive data, update dataframe
async def binance_ws(symbol="btcusdt", interval="1m"):
    url = f"wss://stream.binance.com:443/ws/{symbol}@kline_{interval}"
    async with websockets.connect(url) as ws:
        while True:
            data = await ws.recv()
            kline = json.loads(data)['k']
            
            event_time = pandas.to_datetime(kline['t'], unit='ms')
            new_row = {
                'open_time': pandas.to_datetime(kline['t'], unit='ms'),
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c'])
            }
            
            global df
            if df.iloc[-1]['open_time'] == event_time:
                df.iloc[-1] = pandas.Series(new_row)
            else:
                df = pandas.concat([df, pandas.DataFrame([new_row])], ignore_index=True)

            if len(df) > 30: 
                df = df.iloc[-30:]

def start_ws_loop():
    asyncio.new_event_loop().run_until_complete(binance_ws())

ws_thread = Thread(target=start_ws_loop, daemon=True)
ws_thread.start()

# Update chart every 2s
@app.callback(
    Output("live-candlestick", "figure"),
    Input("interval", "n_intervals")
)
def update_chart(n):
    global df

    fig = go.Figure(data=[go.Candlestick(
        x=df['open_time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        yaxis_title="Price (USDT)",
        xaxis_title="Date"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)