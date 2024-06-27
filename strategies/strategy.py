from typing import NamedTuple, Optional


class Buy(NamedTuple):
    amount: int


class Strategy:
    def update(self, ohlc_data) -> Optional[Buy]:
        raise NotImplementedError()
