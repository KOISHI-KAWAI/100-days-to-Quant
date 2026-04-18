import talib
import pandas
import pandas_ta as ta

ON_DEBUG = True

def indicators_talib(df:pandas.DataFrame):
    close = df["Close"].to_numpy(dtype=float)
    high = df["High"].to_numpy(dtype=float)
    low = df["Low"].to_numpy(dtype=float)
    volume = df["Volume"].to_numpy(dtype=float)

    # Trend indicators
    df["SMA_7"] = talib.SMA(close, timeperiod=7)
    df["MACD_DIF"],df["MACD_DEA"],df["MACD_hist"] = talib.MACD(close, fastperiod=3, slowperiod=6, signalperiod=3)

    # Volatility indicators
    df["BOLL_UP"], df["BOLL_MB"], df["BOLL_LOW"] = talib.BBANDS(close)

    # Momentum indicators
    df["RSI"] = talib.RSI(close)

    df["KDJ_K"],df["KDJ_D"] = talib.STOCH(high,low,close)
    df["KDJ_J"] = 3*df["KDJ_K"] - 2*df["KDJ_D"]

    # Volume indicators
    df["BOV"] = talib.OBV(close, volume)

    print("[+] Features enginering with Talib:")
    print(df.tail(),end="\n\n")

def indicators_pandas(df:pandas.DataFrame):
    # Trend indicators
    df.ta.sma(close="Close", length=7, append=True)
    df.ta.macd(close="Close", fast=3, slow=6, signal=3, append=True)

    # Vaolatility indicators
    df.ta.bbands(close="Close", append=True)

    # Momentum indicators
    df.ta.rsi(close="Close", append=True)
    df.ta.kdj(high="High", low="Low", close="Close", append=True)

    # Volume indicators
    df.ta.obv(close="Close", volume="Volume", append=True)

    print("[+] Features enginering with Talib:")
    print(df.tail(),end="\n\n")

if ON_DEBUG == True:
    # Data from Day 001
    data = pandas.read_excel("./AAPL.xlsx").drop(["Stock Splits","Dividends"], axis=1)
    
    indicators_talib(data)
    indicators_pandas(data)