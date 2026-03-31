import json

import pandas
import requests
import websocket

import event

class Gateway():
    def __init__(self, engine)->None:
        self.main_engine = engine

    def on_set_gateway(self)->None:
        pass

class BinanceGateway(Gateway):
    def __init__(self, main_engine)->None:
        super().__init__(main_engine)

        self.base_http_url = str()
        self.base_wss_url = str()

        self.__gateway_initialize()
        self.ws_client = websocket.WebSocketApp(url=f"{self.base_wss_url}/ws", 
                                                on_message=self.__on_ws_message, 
                                                on_open=self.__on_ws_open, 
                                                on_close=self.__on_ws_close)
        
        self.ws_action_total = 0
        self.ws_action_dict = dict()
    
    def __gateway_initialize(self)->None:
        base_http_urls = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com",
            "https://api4.binance.com",
        ]

        for url in base_http_urls:
            rsp = requests.get(url=f"{url}/api/v3/ping")
            if rsp.status_code == 200:
                self.base_http_url = url
                break

        base_wss_urls = [
            "wss://stream.binance.com:9443",
            "wss://stream.binance.com:443"
        ]

        for url in base_wss_urls:
            ws = websocket.WebSocket()
            ws.connect(url=f"{url}/ws")
            ws.send("ping")

            if ws.status == 101:
                self.base_wss_url = url
                break

        if (self.base_http_url not in base_http_urls) or (self.base_wss_url not in base_wss_urls):
            print("\033[31m[!] Gateway initialization failed, check your internet connection\033[0m")

    def get_history(self, symbol:str, interval:str, start_time:str|None=None, end_time:str|None=None, time_zone:int|str=0, limit:int=500) -> pandas.DataFrame:
        df = pandas.DataFrame()
        rsp = requests.get(url=f"{self.base_http_url}/api/v3/klines", params={
            "symbol" : symbol,
            "interval" : interval,
            "startTime" : start_time,
            "endTime" : end_time,
            "timeZone" : time_zone,
            "limit" : limit
        })

        if rsp.status_code==200 and isinstance(rsp.json(), list) == True:
            df = pandas.DataFrame(rsp.json(), columns=[
                "open_time","open","high","low","close","volume",
                "close_time","qav","num_trades",
                "taker_base_vol","taker_quote_vol","ignore"
            ]).drop(columns=["qav","num_trades","taker_base_vol","taker_quote_vol","ignore"])
            df["open_time"] = pandas.to_datetime(df["open_time"], unit="ms")
            df["close_time"] = pandas.to_datetime(df["close_time"], unit="ms")

            print(f"[+] Get history data from Binance size: [{df.shape[0]},{df.shape[1]}]")

        elif isinstance(rsp.json(), dict) == True:
            print(f"\033[31m[!] Get history data from Binance with error: {rsp.json().get("msg","unknow error")}\033[0m")
        else:
            print(f"\033[31m[!] Get history data from Binance with error: HTTP respond code {rsp.status_code}\033[0m")

        return df
    
    def subscribe_stream(self, symbol:str, stream:str, unsub:bool=False)->None:
        method = "SUBSCRIBE" if unsub == False else "UNSUBSCRIBE"
        params = [f"{symbol}@{stream}"]
        self.ws_action_total += 1
        id = self.ws_action_total

        msg = {
            "method" : method,
            "params" : params,
            "id" : id
        }
        self.ws_action_dict[id] = {
            "method" : method,
            "params" : params
        }
        self.ws_client.send(json.dumps(msg))

    def list_subscriptions(self)->None:
        method = "LIST_SUBSCRIPTIONS"
        self.ws_action_total += 1
        id = self.ws_action_total

        msg = {
            "method": method,
            "id" : id
        }
        self.ws_action_dict[id] = {
            "method" : method
        }
        self.ws_client.send(json.dumps(msg))

    def on_bar(self, data:dict)->None:
        print(f"[+] Binance gateway received a kline ({data["k"]["s"]}) with new price {data["k"]["c"]}")
        
        symbol = data["s"]
        interval = data["k"]["i"]
        open = data["k"]["o"]
        high = data["k"]["h"]
        low = data["k"]["l"]
        close = data["k"]["c"]
        volume = data["k"]["v"]
        time = data["E"]

        kline_event = event.Kline_Update_Event("Kline_Update_Event", symbol, interval, open, high, low, close, volume, time)
        self.main_engine.put_event(kline_event)

    def __on_ws_open(self, wsapp)->None:
        print(f"[+] Start websocket listener for Binance gateway")

    def __on_ws_message(self, wsapp, message)->None:
        msg = json.loads(message)

        id = msg.get("id",None)
        result = msg.get("result", None)

        if id in self.ws_action_dict.keys():
            if result == None:
                print(f"[+] Binance gateway {str(self.ws_action_dict[id]["method"]).lower()} a stream: {list(self.ws_action_dict[id]["params"])[0]}")
            else:
                streams = str()
                for stream in result:
                    streams = streams + f"{stream} "
                print(f"[+] Binance gateway's subscription: {streams}")
            self.ws_action_dict.pop(id, None)
        elif id != None:
            print(f"\033[31m[!] Binance gateway received unkonwn messgae with id: {id}\033[0m")

        if msg.get("e",None) == "kline":
            self.on_bar(msg)

    def __on_ws_close(self, wsapp, status_code, message)->None:
        print(f"[+] Close websocket listener for Binance with status code {status_code}")

    def on_set_gateway(self)->None:
        self.ws_client.run_forever()      












