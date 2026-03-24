import os

import yfinance
import pandas
import numpy
import mplfinance as mpf

def get_data(symbol, interval, period):
    if not os.path.exists(f"{symbol}.xlsx"):
        ticker = yfinance.Ticker(ticker=symbol)

        df = ticker.history(period=period,interval=interval)
        df = pandas.DataFrame(df).drop(columns=["Dividends","Stock Splits"])

        df["Date"] = df["Date"].tz_localize(None)
        df.to_excel(f"{symbol}.xlsx")

    df = pandas.read_excel(f"{symbol}.xlsx")

    return df

def build_signal(df):
    df = df.copy()
    
    df["Return"] = df["Close"].pct_change()
    df.index = pandas.to_datetime(df["Date"])

    # Buy signal after two days' increasement, sell signal after two days' decreasement
    df["Signal"] = 0

    status = None
    for idx in range(1,df.shape[0]):
        ret_today = df.iloc[idx]["Return"]
        ret_yesterday = df.iloc[idx-1]["Return"]

        if ret_today > 0 and ret_yesterday > 0 and status != "Buy":
            df.loc[df.index[idx], "Signal"] = 1
            status = "Buy"

        elif ret_today < 0 and ret_yesterday < 0 and status != "Sell":
            df.loc[df.index[idx], "Signal"] = -1
            status = "Sell"

    return df

def draw_signal(df):
    df["Buy_marker_y"] = numpy.where(df["Signal"] == 1, df["Low"]*0.98, numpy.nan)
    df["Sell_marker_y"] = numpy.where(df["Signal"] == -1, df["High"]*1.02, numpy.nan) 

    signal_plots = [
        mpf.make_addplot(df["Buy_marker_y"], type="scatter", marker="^", markersize=100),
        mpf.make_addplot(df["Sell_marker_y"], type="scatter", marker="v", markersize=100)
    ]

    mpf.plot(df, type="candle", style="yahoo", addplot=signal_plots)

if __name__ == "__main__":
    df = get_data(symbol="AAPL",interval="1d",period="2y")
    df = build_signal(df)
    draw_signal(df)

    








