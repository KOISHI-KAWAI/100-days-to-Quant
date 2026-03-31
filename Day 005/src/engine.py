import threading

import event
import gateway

class MainEngine:
    def __init__(self) -> None:
        self.__threads_pool = dict()
        self.__event_engine = event.event_engine

    def start(self)->None:
        self.__start_event_engine()
        print("\033[33m[+] Main Engine started\033[0m")

    def stop(self)->None:
        self.stop_gateway()
        self.__event_engine.stop()

        for name in self.__threads_pool.keys():
            self.__threads_pool[name].join()
        self.__threads_pool.clear()

        print("\033[33m[+] Main Engine stoped\033[0m")

    def set_gateway(self, gateway:gateway.Gateway, name:str)->None:
        self.gateway = gateway
        self.gateway_name = name

        gateway.on_set()
        print(f"\033[33m[+] Gateway {self.gateway_name} setted\033[0m")

    def start_gateway(self)->None:
        try:
            thread = threading.Thread(target=self.gateway.on_start)
            self.__add_thread(thread, f"gateway_thread_{self.gateway_name}")
            thread.start()
            print(f"\033[33m[+] Gateway {self.gateway_name} started\033[0m")
        except Exception as e:
            print(f"\031[33m[!] Can not start gateway due to: {e}\033[0m")

    def stop_gateway(self)->None:
        self.gateway.on_stop()
        self.__threads_pool[f"gateway_thread_{self.gateway_name}"].join()
        self.__threads_pool.pop(f"gateway_thread_{self.gateway_name}")
        print(f"\033[33m[+] Gateway {self.gateway_name} stoped\033[0m")

    def __start_event_engine(self):
        try:
            thread = threading.Thread(target=self.__event_engine.start)
            self.__add_thread(thread, "event_engine_thread")
            thread.start()
        except Exception as e:
            print(f"\031[33m[!] Can not start Event Engine due to: {e}\033[0m")

    def __add_thread(self, thread, name):
        if name in self.__threads_pool.keys():
            print(f"\031[33m[!] Main engine try to override a thread named {name}\033[0m")
        else:
            self.__threads_pool[name] = thread

main_engine = MainEngine()
         





