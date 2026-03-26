import datetime
import collections

import numpy
import talib
import pandas
import mplfinance as mpf

class Event():
    def __init__(self, 
                 event_time:datetime.datetime, 
                 event_name:str, 
                 event_type:str):
        
        self.event_time = event_time
        self.event_name = event_name
        self.event_type = event_type

class MarketEvent(Event):
    def __init__(self, event_type:str, **kwargs):
        if "event_time" not in kwargs.keys():
            kwargs["event_time"] = datetime.datetime.now()
        if "event_name" not in kwargs.keys():
            kwargs["event_name"] = "MarketEvent"

        super().__init__(kwargs["event_time"], kwargs["event_name"], event_type)

        if self.event_type == "NewCandleLine":
            self.event = self.NewCandleLineEvent(kwargs["candle"])

    class NewCandleLineEvent():
        def __init__(self, candle:dict):
            self.date = candle["Date"]
            self.open = candle["Open"]
            self.high = candle["High"]
            self.low = candle["Low"]
            self.close = candle["Close"]
            self.volume = candle["Volume"]            

class Market():
    def __init__(self, queue:collections.deque):
        self.queue = queue

        # Start market listener, but here simulate with dataframe enqueue
        self.candles_df = pandas.read_excel("AAPL.xlsx")

        for idx in range(0, self.candles_df.shape[0]):
            event = MarketEvent("NewCandleLine", candle=self.candles_df.iloc[idx])
            self.queue.append(event)

class Strategy():
    def __init__(self, queue:collections.deque):
        self.queue = queue
        self.status = None
        self.candles_df = pandas.DataFrame(columns=["Date","Open","High","Low","Close","Volume","Signal"])

    def build_indicator(self, indicator:str, **kwargs):
        # Manual computation could be faster
        if indicator == "SMA":
            if len(self.candles_df) >= kwargs["period"]:
                self.candles_df[f"SMA_{kwargs['period']}"] = talib.SMA(self.candles_df["Close"], timeperiod=kwargs["period"])

    def build_signal(self):
        if len(self.candles_df) >= 30:
            if self.candles_df.loc[len(self.candles_df)-1, "SMA_7"] >= self.candles_df.loc[len(self.candles_df)-1, "SMA_30"] and self.status != "buy":
                self.status = "buy"
                self.candles_df.loc[len(self.candles_df)-1, "Signal"] = 1 
            elif self.candles_df.loc[len(self.candles_df)-1, "SMA_7"] < self.candles_df.loc[len(self.candles_df)-1, "SMA_30"] and self.status != "sell":
                self.status = "sell"
                self.candles_df.loc[len(self.candles_df)-1, "Signal"] = -1 

    def signal_visualize(self):
        ind_plots = [
            mpf.make_addplot(self.candles_df["SMA_7"], color="orange"),
            mpf.make_addplot(self.candles_df["SMA_30"], color="blue")
        ]

        buy_marker_y = numpy.where(self.candles_df["Signal"] == 1, self.candles_df["Low"]*0.90, numpy.nan)
        sell_marker_y = numpy.where(self.candles_df["Signal"] == -1, self.candles_df["High"]*1.10, numpy.nan)
        sig_plots = [
            mpf.make_addplot(buy_marker_y, type="scatter", marker="^", markersize=100, color="green"),
            mpf.make_addplot(sell_marker_y, type="scatter", marker="v", markersize=100, color="red")
        ]

        self.candles_df.index = pandas.to_datetime(self.candles_df["Date"])
        mpf.plot(self.candles_df, type="candle", style="yahoo", addplot=ind_plots+sig_plots)

    def handle_market_event(self, event:MarketEvent):
        if event.event_type == "NewCandleLine":
            self.candles_df.loc[len(self.candles_df)] = {
                "Date": event.event.date,
                "Open": event.event.open,
                "High": event.event.high,
                "Low": event.event.low,
                "Close": event.event.close,
                "Volume": event.event.volume,
                "Signal": 0
                }
            
            self.build_indicator("SMA", period=7)
            self.build_indicator("SMA", period=30)
            
            self.build_signal()

if __name__ == "__main__":
    events_queue = collections.deque()
    market = Market(events_queue)
    strategy = Strategy(events_queue)

    while len(events_queue) > 0:
        event = events_queue.popleft()
        strategy.handle_market_event(event)

    strategy.signal_visualize()



