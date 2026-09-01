"""Actions in the Prisoner's Dilemma."""

from __future__ import annotations

from enum import Enum


class Action(Enum):
    """Cooperate (C) or Defect (D)."""

    C = 0
    D = 1

    def __str__(self) -> str:
        return "C" if self is Action.C else "D"

    def __repr__(self) -> str:
        return str(self)

    def flip(self) -> Action:
        return Action.D if self is Action.C else Action.C


C = Action.C
D = Action.D
