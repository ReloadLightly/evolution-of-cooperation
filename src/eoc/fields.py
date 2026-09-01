"""Reusable opponent sets used as fitness environments.

`axelrod_like_field` is not a bit-perfect replica of the 1980 first
tournament — several of those programs were underspecified. It is the
same kind of mix Axelrod used to score evolved rules in 1987: nice
reciprocators, grim punishers, probe-and-exploit rules, and noise.
"""

from __future__ import annotations

from eoc.player import Player
from eoc.strategies import (
    AlwaysCooperate,
    AlwaysDefect,
    Davis,
    GenerousTitForTat,
    Grofman,
    Grudger,
    Joss,
    Pavlov,
    Prober,
    Random,
    Shubik,
    SuspiciousTitForTat,
    Tester,
    TitForTat,
    TitForTwoTats,
    TwoTitsForTat,
)


def axelrod_like_field() -> list[Player]:
    """A compact mixed field in the spirit of the early tournaments."""
    return [
        TitForTat(),
        TitForTwoTats(),
        GenerousTitForTat(0.1),
        AlwaysCooperate(),
        AlwaysDefect(),
        Random(0.5),
        Grudger(),
        Pavlov(),
        Joss(0.9),
        Tester(),
        Prober(),
        Shubik(),
        Davis(),
        Grofman(),
        TwoTitsForTat(),
        SuspiciousTitForTat(),
    ]


def representative_eight() -> list[Player]:
    """Smaller scoring set for a fast GA generation."""
    return [
        TitForTat(),
        AlwaysCooperate(),
        AlwaysDefect(),
        Grudger(),
        Joss(0.9),
        Random(0.5),
        Tester(),
        Pavlov(),
    ]
