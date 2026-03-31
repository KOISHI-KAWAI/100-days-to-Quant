import queue

import datatype

class Event():
    def __init__(self) -> None:
        self.type = None

class Kline_Update_Event(Event):
    def __init__(self, kline:datatype.Kline) -> None:
        super().__init__()

        self.type = "Kline_Update_Event"
        self.kline = kline

class EventEngine():
    def __init__(self) -> None:
        self.__running = True
        self.__event_queue = queue.Queue()

    def put_event(self, event:Event)->None:
        self.__event_queue.put(event)

    def push_event(self)->Event:
        event = self.__event_queue.get()
        return event
    
    def start(self):
        print(f"\033[33m[+] Event Engine stated\033[0m")
        while self.__running == True:
            if self.__event_queue.empty() == False:
                event = self.push_event()
                if event.type == "Kline_Update_Event":
                    print(f"[+] Event Engine pushing event: {event.type}")

    def stop(self):
        self.__running = False
        print("\033[33m[+] Event Engine stoped\033[0m")

event_engine = EventEngine()
