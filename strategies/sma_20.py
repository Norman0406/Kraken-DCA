from typing import Optional
from logger import create_logger
from sma import SMA
from strategies.strategy import Buy, Strategy

logger = create_logger("Sma20")


class Sma20(Strategy):
    TYPE = "sma_20"

    def __init__(self, json):
        self._sma = SMA()
        self._amount = float(json["amount"])
        self._min_dip_percentage = float(json["minDipPercentage"])

    def update(self, ohlc_data) -> Optional[Buy]:
        if self._sma.update(ohlc_data):
            if self._sma.down_then_up():
                self._sma.print()

                dip = abs(self._sma.dip())
                dip_percentage = dip / self._sma.values[0]

                logger.debug(f"Dip: {dip}")
                logger.debug(f"Dip percentage: {dip_percentage}")

                if dip_percentage > self._min_dip_percentage:
                    return Buy(self._amount)

            elif self._sma.up_then_down():
                self._sma.print()

        return None
