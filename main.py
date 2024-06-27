from authentication import Authentication
from client import Client
from settings import Settings
from strategies.strategies_factory import make_strategies
from trading_bot import TradingBot
from logger import logger


def main():
    logger.info("Starting up")

    settings = Settings("settings.json")
    authentication = Authentication("authentication.json")

    client = Client(authentication=authentication, settings=settings)
    trading_bot = TradingBot(
        client=client,
        strategies=make_strategies(settings.data),
        trade_interval=settings.trade_interval,
        dummy_mode=settings.dummy_mode,
    )

    trading_bot.run()

    logger.info("Finished")


if __name__ == "__main__":
    main()
