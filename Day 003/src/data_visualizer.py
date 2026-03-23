import pandas
import talib
import mplfinance as mpf
import matplotlib.pyplot as plt


def matplotlib_drawer(df):
    fig, axes = plt.subplots(2,1)

    # Draw price, sma series
    axes[0].plot(df["Date"],df["Close"],label="Price")
    axes[0].plot(df["Date"],df["SMA_7"],label="SMA(7)")
    axes[0].plot(df["Date"],df["SMA_30"],label="SMA(30)")

    axes[0].set_title("AAPL's Price & SMA")
    axes[0].legend()

    # Draw volume as bar plot
    axes[1].bar(df["Date"],df["Close"])
    axes[1].set_title("AAPL's Volume")

    plt.show()

def mplfinance_drawer(df):
    # Draw sma series with K lines
    sma_plots = [
        mpf.make_addplot(df["SMA_7"], label="SMA(7)", panel=0, width=1),
        mpf.make_addplot(df["SMA_30"], label="SMA(30)", panel=0, width=1)
    ]

    # Draw extra MACD indicators in another axis(panel)
    macd_hist_pos = df["MACD_hist"].copy()
    macd_hist_neg = df["MACD_hist"].copy()
    macd_hist_pos[macd_hist_pos < 0] = 0
    macd_hist_neg[macd_hist_neg > 0] = 0

    macd_plots = [
        mpf.make_addplot(macd_hist_pos, type="bar", panel=2, color='green'),
        mpf.make_addplot(macd_hist_neg, type="bar", panel=2, color='red'),
        mpf.make_addplot(df["MACD"], label="Fast", panel=2, color="orange", width=1),
        mpf.make_addplot(df["MACD_signal"], label="Slow", panel=2, color="blue", width=1),
    ]

    mpf.plot(df, type="candle", volume=True, volume_panel=1, addplot=sma_plots+macd_plots, style="yahoo")


if __name__ == "__main__":
    # File from Day 002: AAPL.xlsx
    df = pandas.read_excel("AAPL.xlsx")

    # Generate some indicators
    df["SMA_7"] = talib.SMA(df["Close"],timeperiod=7)
    df["SMA_30"] = talib.SMA(df["Close"],timeperiod=30)
    df["MACD"], df["MACD_signal"], df["MACD_hist"] = talib.MACD(df["Close"])

    matplotlib_drawer(df)

    # Mplfinance require date as index
    df.index = pandas.to_datetime(df["Date"])
    mplfinance_drawer(df.dropna())

    


