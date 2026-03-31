import queue
import datetime

class Event():
    def __init__(self, name:str, data:dict):
        self.name = name
        self.data = data

    def bind_handler(self, func:object):
        self.handler = func

class Kline_Update_Event(Event):
    def __init__(self, name: str, symbol:str, interval:str, open:float, high:float, low:float, close:float, volume:float, time:datetime.datetime):
        data = {
            "symbol" : symbol,
            "interval" : interval,
            "open" : open,
            "high" : high,
            "low" : low,
            "close" : close,
            "volume" : volume,
            "time" : time
        }
        
        super().__init__(name, data)

class EventEngine():
    def __init__(self):
        self.queue = queue.Queue()

    def register(self, event:Event):
        self.queue.put(event)

    def on_set_engine(self):
        while True:
            if self.queue.empty() == False:
                event = self.queue.get()
                print(f"[+] New event named: {event.name} arrive")
                event.handler(event.data)
                