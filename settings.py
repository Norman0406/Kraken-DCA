import json

from logger import create_logger

logger = create_logger("Settings")


class Settings:
    def __init__(self, json_file):
        logger.info(f"Reading settings from {json_file}")

        with open(json_file) as file:
            self._data = json.load(file)
            self.trade_symbol = self._data["settings"]["tradeSymbol"]
            self.trade_interval = self._data["settings"]["tradeInterval"]
            self.dummy_mode = self._data["settings"]["dummyMode"]

    @property
    def data(self):
        return self._data
