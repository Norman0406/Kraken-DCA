import base64
import hashlib
import hmac
import json
import time
from typing import List, NamedTuple
import urllib.request
from authentication import Authentication
from logger import create_logger
from settings import Settings

logger = create_logger("Client")

API_ENDPOINT = "https://api.kraken.com"
USER_AGENT = "kraken_dca_agent"


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

    def _make_api_call(self, path: str, arguments: dict = {}):
        logger.debug(
            f"Calling {path}"
            + (f" with arguments {arguments}" if len(arguments) > 0 else "")
        )

        nonce = str(int(time.time() * 1000))
        params = f"nonce={nonce}"

        for key, value in arguments.items():
            params += f"&{key}={value}"

        api_sha256 = hashlib.sha256(nonce.encode("utf8") + params.encode("utf8"))
        api_hmac = hmac.new(
            base64.b64decode(self._authentication.api_key_private),
            path.encode("utf8") + api_sha256.digest(),
            hashlib.sha512,
        )
        api_signature = base64.b64encode(api_hmac.digest())

        try:
            api_request = urllib.request.Request(
                f"{API_ENDPOINT}{path}", params.encode("utf8")
            )
            api_request.add_header("API-Key", self._authentication.api_key_public)
            api_request.add_header("API-Sign", api_signature)
            api_request.add_header("User-Agent", USER_AGENT)
            api_response = urllib.request.urlopen(api_request).read().decode()
            api_data = json.loads(api_response)
        except Exception as error:
            logger.exception(f"Failed: {error}")
            raise error
        else:
            error = api_data["error"]

            if len(error) == 0:
                return api_data["result"]
            else:
                logger.exception(f"Error: {error}")
                raise Exception(error)

    def check_status(self):
        result = self._make_api_call(
            path="/0/public/SystemStatus",
        )
        if result["status"] != "online":
            raise Exception("Kraken is not operational")

    def get_ohlc_data(self, interval):
        result = self._make_api_call(
            path="/0/public/OHLC",
            arguments={"pair": self._settings.trade_symbol, "interval": interval},
        )
        return result[self._settings.trade_symbol]

    def get_fee(self):
        result = self._make_api_call(
            path="/0/private/TradeVolume",
            arguments={
                "pair": self._settings.trade_symbol,
            },
        )
        fees_maker = result["fees_maker"]
        fees_for_pair = fees_maker[self._settings.trade_symbol]
        return float(fees_for_pair["fee"])

    def get_asset_pair(self):
        result = self._make_api_call(
            path="/0/public/AssetPairs",
            arguments={
                "pair": self._settings.trade_symbol,
            },
        )
        return result

    def get_balance(self):
        result = self._make_api_call(
            path="/0/private/Balance",
        )
        return float(result["CHF"])

    def get_order_book(self) -> OrderBook:
        result = self._make_api_call(
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
        result = self._make_api_call(
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
        return result
