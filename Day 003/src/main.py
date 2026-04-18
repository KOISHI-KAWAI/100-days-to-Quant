import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas
import yfinance
import talib

ON_DEBUG = True

def matplotlib_visualizer(df:pandas.DataFrame):
    fig, axes = plt.subplots(2,1)

    axes[0].plot(df["Date"],df["Close"],label="Price")
    axes[0].plot(df["Date"],df["SMA_7"],label="SMA(7)")
    axes[1].bar(df["Date"],df["Volume"])

    axes[0].set_title("AAPL's Price & SMA")
    axes[0].legend()

    plt.show()

def mplfinance_visualizer(df:pandas.DataFrame):
    sma_plots = [
        mpf.make_addplot(df["SMA_7"], label="SMA(7)", panel=0, width=1)
    ]

    obv_plots = [
        mpf.make_addplot(df["OBV"], label="OBV", panel=2, width=1),
    ]

    mpf.plot(df, type="candle", volume=True, volume_panel=1, addplot=sma_plots+obv_plots, style="yahoo")

if ON_DEBUG == True:
    data = pandas.read_excel("./AAPL.xlsx")
    data.index = data["Date"]
    data["SMA_7"] = talib.SMA(data["Close"].to_numpy(), timeperiod=7)
    data["OBV"] = talib.OBV(data["Close"].to_numpy(),data["Volume"].to_numpy(dtype=float))

    # matplotlib_visualizer(data)
    # mplfinance_visualizer(data)