from typing import List, NamedTuple
from util import Authentication, Settings, make_api_call


class OrderBookEntry(NamedTuple):
    price: float
    volume: float


class OrderBook(NamedTuple):
    asks: List[OrderBookEntry]
    bids: List[OrderBookEntry]


class Client:
    def __init__(self, authentication: Authentication, settings: Settings):
        self._authentication = authentication
        self._settings = settings

        self.check_status()

    def check_status(self):
        result = make_api_call(
            authentication=self._authentication,
            path="/0/public/SystemStatus",
        )
        if result["status"] != "online":
            raise Exception("Kraken is not operational")

    def get_ohlc_data(self, interval):
        result = make_api_call(
            authentication=self._authentication,
            path="/0/public/OHLC",
            arguments={"pair": self._settings.trade_symbol, "interval": interval},
        )
        return result[self._settings.trade_symbol]

    def get_fee(self):
        result = make_api_call(
            authentication=self._authentication,
            path="/0/private/TradeVolume",
            arguments={
                "pair": self._settings.trade_symbol,
            },
        )
        fees_maker = result["fees_maker"]
        fees_for_pair = fees_maker[self._settings.trade_symbol]
        return float(fees_for_pair["fee"])

    def get_asset_pair(self):
        result = make_api_call(
            authentication=self._authentication,
            path="/0/public/AssetPairs",
            arguments={
                "pair": self._settings.trade_symbol,
            },
        )
        print(result)

    def get_balance(self):
        result = make_api_call(
            authentication=self._authentication,
            path="/0/private/Balance",
        )
        return float(result["CHF"])

    def get_order_book(self) -> OrderBook:
        result = make_api_call(
            authentication=self._authentication,
            path="/0/public/Depth",
            arguments={
                "pair": self._settings.trade_symbol,
            },
        )

        asks = [
            OrderBookEntry(float(ask[0]), float(ask[1]))
            for ask in result[self._settings.trade_symbol]["asks"]
        ]

        bids = [
            OrderBookEntry(float(bid[0]), float(bid[1]))
            for bid in result[self._settings.trade_symbol]["bids"]
        ]

        return OrderBook(asks=asks, bids=bids)

    def add_order(self, volume, price):
        if volume <= 0:
            raise Exception("Invalid volume")

        expires_in_seconds = 24 * 60 * 60  # expires in 24 hours
        result = make_api_call(
            authentication=self._authentication,
            path="/0/private/AddOrder",
            arguments={
                "pair": self._settings.trade_symbol,
                "type": "buy",
                "ordertype": "limit",
                "price": price,
                "oflags": "post",  # post-only order to avoid taker fees
                "volume": volume,
                "expiretm": f"%2b{expires_in_seconds}",
            },
        )
        print(result)
