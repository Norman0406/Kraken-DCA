from datetime import datetime
from logger import create_logger
import time
from client import Client
from strategies.strategy import Buy

logger = create_logger("TradingBot")


class TradingBot:
    def __init__(self, client: Client, strategies, trade_interval, dummy_mode):
        self._client = client
        self._strategies = strategies
        self._trade_interval = trade_interval
        self._waiting_time = self._trade_interval * 60
        self._dummy_mode = dummy_mode

    def run(self):
        logger.info("Starting main loop")
        is_running = True
        while is_running:
            try:
                now = datetime.now()

                try:
                    result = self._client.get_ohlc_data(self._trade_interval)

                    for strategy in self._strategies:
                        buy = strategy.update(result)
                        if buy:
                            logger.info(
                                f"Strategy {strategy.TYPE} wants to buy {buy.amount} CHF"
                            )
                            self._buy(buy)
                except Exception as error:
                    logger.exception(f"Error: {error}")

                diff = datetime.now() - now

                sleep_time = self._waiting_time - diff.seconds
                logger.debug(f"Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
            except KeyboardInterrupt:
                is_running = False

    def _buy(self, buy: Buy):
        if self._dummy_mode:
            logger.info(f"Dummy buy: {buy.amount}")
            return

        order_book = self._client.get_order_book()
        best_bid_price = self._get_best_bid_price(order_book)
        volume = self._get_volume(best_bid_price=best_bid_price, amount=buy.amount)
        balance = self._client.get_balance()

        if buy.amount > balance:
            raise RuntimeError("Insufficient funds")

        # TODO: safe this order in a local file, wait for order confirmation from websocket channel

        self._client.add_order(volume, best_bid_price)

    def _get_best_bid_price(self, order_book) -> float:
        return order_book.bids[0].price

    def _get_volume(self, best_bid_price, amount) -> float:
        fee_percentage = self._client.get_fee() / 100

        volume = round(amount / (best_bid_price * (1 + fee_percentage)), 8)
        amount = volume * best_bid_price

        return volume
