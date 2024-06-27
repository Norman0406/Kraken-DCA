class SMA:
    def __init__(self, sma_length=20):
        self._sma_values = [0.0, 0.0, 0.0]
        self._sma_length = sma_length

    @property
    def initialized(self):
        return self._sma_values[2] > 0

    @property
    def values(self):
        return self._sma_values

    def update(self, result) -> bool:
        api_ohlc_length = len(result) - 1
        sma_temp = 0.0
        # we leave out the last one because that candle isn't closed yet
        for count in range(1, self._sma_length + 1):
            sma_temp += float(result[api_ohlc_length - count][4])  # [4] is close price
        sma_temp = sma_temp / self._sma_length

        self._sma_values[2] = self._sma_values[1]
        self._sma_values[1] = self._sma_values[0]
        self._sma_values[0] = sma_temp

        return self._sma_values[2] > 0

    def down_then_up(self):
        # return true if the price went down and then up
        return (self._sma_values[0] > self._sma_values[1]) and (
            self._sma_values[1] < self._sma_values[2]
        )

    def up_then_down(self):
        # return true if the price went up and then down
        return (self._sma_values[0] < self._sma_values[1]) and (
            self._sma_values[1] > self._sma_values[2]
        )

    def dip(self):
        # Return the amount the price went up or down before it went down or up again. > 0: price went up, < 0: price went down
        return self._sma_values[1] - self._sma_values[2]

    def print(self):
        print(
            f"SMA {self._sma_length}: {self._sma_values[2]} / {self._sma_values[1]} / {self._sma_values[0]}: {self.dip()}"
        )
