import threading

import event

class MainEngine():
    def __init__(self):
        self.threads_pool = dict()

        self.event_engine = event.EventEngine()
        self.__set_event_engine(self.event_engine)

        self.strategy_engine = strategy.StrategyEngine()

        self.gateway = None

    def set_gateway(self, gateway, name:str):
        self.gateway = gateway

        t = threading.Thread(target=gateway.on_set_gateway)
        self.threads_pool[name] = t
        t.start()

    def __set_event_engine(self, engine):
        self.event_engine = engine

        t = threading.Thread(target=engine.on_set_engine)
        self.threads_pool["event_engine"] = t
        t.start()

    def put_event(self, event):
        if event.name == "Kline_Update_Event":
            event.bind_handler(self.strategy_engine.on_bar)
            self.event_engine.register(event)