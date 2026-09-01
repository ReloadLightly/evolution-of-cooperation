"""Base player / strategy interface."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from eoc.actions import Action

if TYPE_CHECKING:
    pass


class Player:
    """Abstract strategy. Subclass and implement ``strategy``.

    Each instance keeps its own action history and the opponent's history
    for the current match. Call ``reset()`` between matches.
    """

    name: str = "Player"
    classifier: dict = {
        "memory_depth": float("inf"),
        "stochastic": False,
        "makes_use_of": set(),
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self) -> None:
        self.history: list[Action] = []
        self.cooperations: int = 0
        self.defections: int = 0
        self.rng = random.Random()

    def reset(self) -> None:
        self.history = []
        self.cooperations = 0
        self.defections = 0

    def seed(self, value: int) -> None:
        self.rng = random.Random(value)

    def update(self, own: Action, opponent: Action) -> None:
        """Record the realized actions after a round (post-noise)."""
        self.history.append(own)
        if own is Action.C:
            self.cooperations += 1
        else:
            self.defections += 1

    def strategy(self, opponent: Player) -> Action:
        raise NotImplementedError

    def clone(self) -> Player:
        """Return a fresh instance of the same class (used by ecology)."""
        return self.__class__()

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name
