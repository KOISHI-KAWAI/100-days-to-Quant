import json
import threading

import contextlib
import websocket
import requests

import event
import datatype

class Gateway():
    def __init__(self) -> None:
        pass

    def on_set(self):
        pass

    def on_start(self):
        pass

    def on_stop(self):
        pass

class BinanceGateway(Gateway):
    def __init__(self) -> None:
        self.http_options = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com",
            "https://api4.binance.com"
        ]

        self.wss_options = [
            "wss://stream.binance.com:9443",
            "wss://stream.binance.com:443"
        ]

        self.ws_actions_id = {
            "SUBSCRIBE" : 1,
            "UNSUBSCRIBE" : 2,
            "LIST_SUBSCRIPTIONS" : 3
        }

        self.__check_connection()
        self.__ws_connected_event = threading.Event()

    def on_set(self):
        self.__ws_client = websocket.WebSocketApp(url=f"{self.wss_base}/ws",
                                                on_open=self.__on_ws_open,
                                                on_message=self.__on_ws_message,
                                                on_close=self.__on_ws_close)

    def on_start(self):
        self.__ws_client.run_forever()

    def on_stop(self):
        self.__ws_client.close()

    def add_subscription(self, symbol:str, stream:str, unsub:bool=False)->None:
        msg = {
            "method" : "SUBSCRIBE" if unsub == False else "UNSUBSCRIBE",
            "params" : [f"{symbol}@{stream}"],
            "id" : self.ws_actions_id["SUBSCRIBE"] if unsub == False else self.ws_actions_id["UNSUBSCRIBE"] 
        }
        
        self.__ws_connected_event.wait()
        self.__ws_client.send(json.dumps(msg))

    def list_subscription(self)->None:
        msg = {
            "method" : "LIST_SUBSCRIPTIONS",
            "id" : self.ws_actions_id["LIST_SUBSCRIPTIONS"]
        }

        self.__ws_connected_event.wait()
        self.__ws_client.send(json.dumps(msg))

    def __check_connection(self):
        self.http_base = str()
        self.wss_base = str()

        for url in self.http_options:
            rsp = requests.get(f"{url}/api/v3/ping")
            if rsp.status_code == 200:
                self.http_base = url
                break 
        
        for url in self.wss_options:
            with contextlib.closing(websocket.create_connection(f"{url}/ws")) as ws:
                if ws.status == 101:
                    self.wss_base = url
                    break

        if (self.http_base not in self.http_options) or (self.wss_base not in self.wss_options):
            print("\033[31m[!] Can not establishing connection between Binance Gateway\033[0m")
    
    def __on_ws_message(self, wsapp, message):
        message = json.loads(message)
        if message.get("id", None) != None:
            id = message.get("id")
            if id == self.ws_actions_id["SUBSCRIBE"]:
                print("\033[33m[+] Subscribe a new stream for Binance Gateway's websocket\033[0m")
            elif id == self.ws_actions_id["UNSUBSCRIBE"]:
                print("\033[33m[+] Unsubscribe a stream for Binance Gateway's websocket\033[0m")
            elif id == self.ws_actions_id["LIST_SUBSCRIPTIONS"]:
                print(f"\033[33m[+] Binance Gateway now subscribe following streams: {message.get("result")}\033[0m")
            else:
                print(f"\033[31m[!] Binance Gateway received an unkonwn message with id {id}\033[0m")

        if message.get("e", None) != None:
            event_type = message.get("e")
            if event_type == "kline":
                self.__on_kline(message)
            else:
                print(f"\031[31m[!] Binance Gateway received an unkown stream with type {event_type}\033[0m")

    def __on_ws_open(self, wsapp):
        self.__ws_connected_event.set()
        print("\033[33m[+] Websocket listener started for Binance Gateway\033[0m")

    def __on_ws_close(self, wsapp, code, message):
        self.__ws_connected_event.clear()
        print("\033[33m[+] Websocket listener closed for Binance Gateway\033[0m")

    def __on_kline(self, msg):
        kline = datatype.Kline(
            time=msg["E"],
            start=msg["k"]["t"],
            end=msg["k"]["T"],
            symbol=msg["k"]["s"],
            interval=msg["k"]["i"],
            open=msg["k"]["o"],
            high=msg["k"]["h"],
            low=msg["k"]["l"],
            close=msg["k"]["c"],
            volume=msg["k"]["v"]
        )
        
        kline_event = event.Kline_Update_Event(kline)
        event.event_engine.put_event(kline_event)
        print(f"[+] Binance Gateway putting event: {kline_event.type}")




