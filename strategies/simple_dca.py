from typing import Optional
from logger import create_logger
from strategies.strategy import Buy, Strategy

logger = create_logger("SimpleDCA")


class SimpleDCA(Strategy):
    TYPE = "simple_dca"

    def __init__(self, json):
        self._amount = float(json["amount"])
        self._day = json["day"]
        self._hour = json["hour"]

    def update(self, ohlc_data) -> Optional[Buy]:
        return None
