import time

import engine
import gateway

if __name__ == "__main__":
    binance_gateway = gateway.BinanceGateway()
    main_engine = engine.main_engine

    main_engine.start()
    main_engine.set_gateway(binance_gateway, "Binance")
    main_engine.start_gateway()

    binance_gateway.add_subscription("btcusdt", "kline_1m")
    binance_gateway.add_subscription("ethusdt", "kline_1m")

    binance_gateway.list_subscription()

    time.sleep(5)
    binance_gateway.add_subscription("btcusdt", "kline_1m", True)
    binance_gateway.add_subscription("ethusdt", "kline_1m", True)

    main_engine.stop_gateway()
    main_engine.start_gateway()
    binance_gateway.add_subscription("btcusdt", "kline_1m")
    binance_gateway.list_subscription()

    time.sleep(5)
    main_engine.stop()