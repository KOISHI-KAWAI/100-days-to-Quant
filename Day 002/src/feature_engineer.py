import os

import yfinance
import pandas
import talib


# Functino form Day 001: data_collector.py
def collect_data(symbol,period="1mo",interval="1d",start_date=None,end_date=None):
    if not os.path.exists(f"{symbol}.xlsx"):
        ticker = yfinance.Ticker(ticker=symbol)

        df = ticker.history(period=period,interval=interval,start=start_date,end=end_date)
        df = pandas.DataFrame(df).drop(columns=["Dividends","Stock Splits"])

        df["Date"] = df["Date"].tz_localize(None)   # Pandas do not support datetime with time zone
        df.to_excel(f"{symbol}.xlsx")

    df = pandas.read_excel(f"{symbol}.xlsx")

    return df

def compute_indicators(df, indicators:dict):
    for ind_name,ind_param in indicators.items():
        if ind_name.upper() == "SMA":
            if ind_param == None:
                ind_param = [30]
            
            print(f"[+] Build SMA indicator with parameters: SMA({ind_param[0]})")
            df[f"SMA_{ind_param[0]}"] = talib.SMA(df["Close"],timeperiod=ind_param[0])

        elif ind_name.upper() == "MACD":
            if ind_param == None:
                ind_param = [12,26,9]

            print(f"[+] Build MACD indicator with parameters: MACD({ind_param[0]},{ind_param[1]},{ind_param[2]})")
            df["MACD"], df["MACD_signal"], df["MACD_hist"] = talib.MACD(df["Close"], 
                                                                        fastperiod=ind_param[0], 
                                                                        slowperiod=ind_param[1], 
                                                                        signalperiod=ind_param[2])

        elif ind_name.upper() == "BOLL" or ind_name.upper() == "BBANDS":
            if ind_param == None:
                ind_param = [20,2,2,0]

            print(f"[+] Build BOLL Bands indicator with parameters: BBANDS({ind_param[0]},{ind_param[1]},{ind_param[2]},{ind_param[3]})")
            df['BOLL_upper'], df['BOLL_mid'], df['BOLL_lower'] = talib.BBANDS(df["Close"],
                                                                              timeperiod=ind_param[0], 
                                                                              nbdevup=ind_param[1], 
                                                                              nbdevdn=ind_param[2], 
                                                                              matype=ind_param[3])
            
        elif ind_name.upper() == "RSI":
            if ind_param == None:
                ind_param = [14]

            print(f"[+] Build RSI indicator with parameters: RSI({ind_param[0]})")
            df[f"RSI_{ind_param[0]}"] = talib.RSI(df["Close"],timeperiod=ind_param[0])

        elif ind_name.upper() == "KDJ":
            if ind_param == None:
                ind_param = [14,3,3]

            print(f"[+] Build KDJ indicator with parameters: KDJ({ind_param[0]},{ind_param[1]},{ind_param[2]})")
            df["KDJ_K"],df["KDJ_D"] = talib.STOCH(df["High"],df["Low"],df["Close"],
                                          fastk_period=ind_param[0],
                                          slowk_period=ind_param[1],
                                          slowd_period=ind_param[2])
            
        elif ind_name.upper() == "CCI":
            if ind_param == None:
                ind_param = [14]

            print(f"[+] Build CCI indicator with parameters: CCI({ind_param[0]})")
            df[f"CCI_{ind_param[0]}"] = talib.CCI(df["High"],df["Low"],df["Close"],
                                                  timeperiod=ind_param[0])

        elif ind_name.upper() == "OBV":
            print(f"[+] Build OBV indicator with parameters: OBV()")
            df["OBV"] = talib.OBV(df["Close"],df["Volume"])

    return df


if __name__ == "__main__":
    df = collect_data(symbol="AAPL", period="6mo")

    # SMA, MACD, BOLL, RSI, KDJ, CCI, OBV
    indicators = {
        "SMA"   : [7],
        "SMA"   : None,
        "MACD"  : None,
        "BOLL"  : None,
        "RSI"   : None,
        "KDJ"   : None,
        "CCI"   : None,
        "OBV"   : None
    }
    df = compute_indicators(df=df, indicators=indicators)

    print(df.dropna().head())
