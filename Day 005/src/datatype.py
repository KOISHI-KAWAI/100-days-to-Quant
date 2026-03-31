



class Kline():
    def __init__(self, **kwargs) -> None:
        self.time = kwargs.get("time", None)
        self.start = kwargs.get("strat", None)
        self.end = kwargs.get("end", None)

        self.symbol = kwargs.get("symbol", None)
        self.interval = kwargs.get("interval", None)
        
        self.open = kwargs.get("open", None)
        self.high = kwargs.get("high", None)
        self.low = kwargs.get("low", None)
        self.close = kwargs.get("clsoe", None)

        self.volume = kwargs.get("volume", None)