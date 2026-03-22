import sqlite3

import yfinance
import pandas

conn = sqlite3.connect("./MSFT.sqlite")
cursor = conn.cursor()

def create_table():
    ticker = yfinance.Ticker(ticker="MSFT")
    df = ticker.history(period="1mo",interval="1d")
    df = pandas.DataFrame(df).drop(columns=["Dividends","Stock Splits"])

    df.to_sql("MSFT",conn,if_exists="replace",index=False)
    df.to_excel("MSFT.xlsx",index=False)

    conn.close()

if __name__ == "__main__":
    create_table()