"""First-tournament rules that were missing from the basic set."""

from __future__ import annotations

from eoc.actions import Action
from eoc.player import Player


class Downing(Player):
    """Leslie Downing — estimate P(C|C) and P(C|D), pick the better action."""

    name = "Downing"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def __init__(self) -> None:
        super().__init__()
        self._cc = self._cd = self._dc = self._dd = 0

    def reset(self) -> None:
        super().reset()
        self._cc = self._cd = self._dc = self._dd = 0

    def update(self, own: Action, opponent: Action) -> None:
        if self.history:
            prev = self.history[-1]
            if prev is Action.C and opponent is Action.C:
                self._cc += 1
            elif prev is Action.C and opponent is Action.D:
                self._cd += 1
            elif prev is Action.D and opponent is Action.C:
                self._dc += 1
            else:
                self._dd += 1
        super().update(own, opponent)

    def strategy(self, opponent: Player) -> Action:
        if not self.history:
            return Action.C
        after_c = self._cc + self._cd
        after_d = self._dc + self._dd
        p_c_given_c = self._cc / after_c if after_c else 0.9
        p_c_given_d = self._dc / after_d if after_d else 0.1
        e_c = p_c_given_c * 3.0 + (1 - p_c_given_c) * 0.0
        e_d = p_c_given_d * 5.0 + (1 - p_c_given_d) * 1.0
        return Action.C if e_c >= e_d else Action.D


class Graaskamp(Player):
    name = "Graaskamp"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def __init__(self) -> None:
        super().__init__()
        self._defect_rest = False

    def reset(self) -> None:
        super().reset()
        self._defect_rest = False

    def strategy(self, opponent: Player) -> Action:
        n = len(self.history)
        if self._defect_rest:
            return Action.D
        if n == 50:
            return Action.D
        if n == 56:
            window = opponent.history[-20:] if len(opponent.history) >= 20 else opponent.history
            if window:
                rate = sum(1 for a in window if a is Action.C) / len(window)
                if 0.4 <= rate <= 0.6:
                    self._defect_rest = True
                    return Action.D
        if not opponent.history:
            return Action.C
        return opponent.history[-1]


class SteinAndRapoport(Player):
    name = "Stein and Rapoport"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def __init__(self) -> None:
        super().__init__()
        self._defect_rest = False

    def reset(self) -> None:
        super().reset()
        self._defect_rest = False

    def strategy(self, opponent: Player) -> Action:
        n = len(self.history)
        horizon = self.expected_turns
        if horizon is not None and n >= horizon - 2:
            return Action.D
        if self._defect_rest:
            return Action.D
        if n >= 15 and n % 15 == 0:
            window = opponent.history[-15:]
            rate = sum(1 for a in window if a is Action.C) / 15.0
            if 0.4 <= rate <= 0.6:
                self._defect_rest = True
                return Action.D
        if not opponent.history:
            return Action.C
        return opponent.history[-1]


class Anonymous(Player):
    name = "Anonymous"
    classifier = {**Player.classifier, "memory_depth": 10, "stochastic": True}

    def __init__(self) -> None:
        super().__init__()
        self.p = 0.3

    def reset(self) -> None:
        super().reset()
        self.p = 0.3

    def strategy(self, opponent: Player) -> Action:
        n = len(opponent.history)
        if n > 0 and n % 10 == 0:
            window = opponent.history[-10:]
            rate = sum(1 for a in window if a is Action.C) / 10.0
            self.p = min(0.7, max(0.3, 0.5 * self.p + 0.5 * rate))
        return Action.C if self.rng.random() < self.p else Action.D
