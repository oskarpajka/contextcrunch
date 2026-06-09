from __future__ import annotations

from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.strategies.filler import FillerStrategy
from contextcrunch.strategies.contraction import ContractionStrategy
from contextcrunch.strategies.verbose import VerboseStrategy
from contextcrunch.strategies.synonym import SynonymStrategy
from contextcrunch.strategies.restructuring import RestructuringStrategy
from contextcrunch.strategies.whitespace import WhitespaceStrategy
from contextcrunch.strategies.normalize import NormalizeStrategy
from contextcrunch.strategies.article import ArticleRemovalStrategy
from contextcrunch.strategies.abbreviation import AbbreviationStrategy


STRATEGIES: dict[int, list[BaseStrategy]] = {
    1: [
        NormalizeStrategy(),
        WhitespaceStrategy(),
        FillerStrategy(),
        VerboseStrategy(),
        ArticleRemovalStrategy(),
    ],
    2: [
        ContractionStrategy(),
        SynonymStrategy(),
        RestructuringStrategy(),
    ],
    3: [
        AbbreviationStrategy(),
    ],
}


def get_strategies(level: str) -> list[BaseStrategy]:
    tiers: list[int]
    match level:
        case "safe":
            tiers = [1]
        case "balanced":
            tiers = [1, 2]
        case "aggressive":
            tiers = [1, 2, 3]
        case _:
            tiers = [1]

    result: list[BaseStrategy] = []
    for tier in tiers:
        result.extend(STRATEGIES.get(tier, []))
    return result


__all__ = [
    "BaseStrategy",
    "FillerStrategy",
    "ContractionStrategy",
    "VerboseStrategy",
    "SynonymStrategy",
    "RestructuringStrategy",
    "WhitespaceStrategy",
    "NormalizeStrategy",
    "ArticleRemovalStrategy",
    "AbbreviationStrategy",
    "STRATEGIES",
    "get_strategies",
]
