"""Reusable opponent sets used as fitness environments."""

from __future__ import annotations

from eoc.player import Player
from eoc.strategies import (
    AlwaysCooperate,
    AlwaysDefect,
    Anonymous,
    Davis,
    Downing,
    Feld,
    GenerousTitForTat,
    Graaskamp,
    Grofman,
    Grudger,
    Joss,
    Pavlov,
    Prober,
    Random,
    Shubik,
    SteinAndRapoport,
    SuspiciousTitForTat,
    Tester,
    TitForTat,
    TitForTwoTats,
    Tullock,
    TwoTitsForTat,
)


def representative_eight() -> list[Player]:
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


def no_sucker_field() -> list[Player]:
    """Eight-strategy mix without Always-Cooperate."""
    return [
        TitForTat(),
        TitForTwoTats(),
        GenerousTitForTat(0.1),
        AlwaysDefect(),
        Grudger(),
        Joss(0.9),
        Tester(),
        Pavlov(),
    ]


def axelrod_like_field() -> list[Player]:
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


def first_tournament_field() -> list[Player]:
    return [
        TitForTat(),
        SteinAndRapoport(),
        Grudger(),
        Davis(),
        Graaskamp(),
        Downing(),
        Feld(),
        Joss(0.9),
        Tullock(),
        Grofman(),
        Shubik(),
        Anonymous(),
        Random(0.5),
        AlwaysCooperate(),
        AlwaysDefect(),
    ]
