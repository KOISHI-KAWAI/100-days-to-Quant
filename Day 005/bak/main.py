import engine
import gateway

if __name__ == "__main__":
    main_engine = engine.MainEngine()
    gateway = gateway.BinanceGateway(main_engine)

    main_engine.set_gateway(gateway, "Binance")