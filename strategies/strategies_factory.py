from typing import List
from strategies.simple_dca import SimpleDCA
from strategies.sma_20 import Sma20
from strategies.strategy import Strategy


def make_strategy(json) -> Strategy:
    type = json["type"]

    if type == SimpleDCA.TYPE:
        return SimpleDCA(json)
    if type == Sma20.TYPE:
        return Sma20(json)

    raise RuntimeError(f"Unknown strategy {type}")


def make_strategies(json) -> List[Strategy]:
    strategies = []
    for entry in json["strategies"]:
        strategies.append(make_strategy(entry))
    return strategies
