"""Classic IPD strategies from Axelrod and the later literature."""

from __future__ import annotations

from eoc.actions import Action
from eoc.player import Player


class TitForTat(Player):
    """Cooperate first, then copy the opponent's previous move.

    Submitted by Anatol Rapoport. Winner of both of Axelrod's tournaments.
    Properties: nice, provocable, forgiving, clear.
    """

    name = "Tit For Tat"
    classifier = {**Player.classifier, "memory_depth": 1, "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        if not opponent.history:
            return Action.C
        return opponent.history[-1]


class TitForTwoTats(Player):
    """Defect only after two consecutive opponent defections.

    More forgiving than TFT. Axelrod noted it would have won the first
    tournament had it been entered.
    """

    name = "Tit For Two Tats"
    classifier = {**Player.classifier, "memory_depth": 2, "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        if len(opponent.history) < 2:
            return Action.C
        if opponent.history[-1] is Action.D and opponent.history[-2] is Action.D:
            return Action.D
        return Action.C


class TwoTitsForTat(Player):
    """Punish a defection with two defections."""

    name = "Two Tits For Tat"
    classifier = {**Player.classifier, "memory_depth": 2, "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        if not opponent.history:
            return Action.C
        if Action.D in opponent.history[-2:]:
            return Action.D
        return Action.C


class SuspiciousTitForTat(Player):
    """TFT that defects on the first move."""

    name = "Suspicious Tit For Tat"
    classifier = {**Player.classifier, "memory_depth": 1, "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        if not opponent.history:
            return Action.D
        return opponent.history[-1]


class GenerousTitForTat(Player):
    """TFT that sometimes forgives a defection (default p=0.1)."""

    name = "Generous Tit For Tat"

    def __init__(self, forgiveness: float = 0.1) -> None:
        super().__init__()
        self.forgiveness = forgiveness
        self.name = f"Generous Tit For Tat ({forgiveness})"
        self.classifier = {**Player.classifier, "memory_depth": 1, "stochastic": True}

    def strategy(self, opponent: Player) -> Action:
        if not opponent.history:
            return Action.C
        if opponent.history[-1] is Action.C:
            return Action.C
        if self.rng.random() < self.forgiveness:
            return Action.C
        return Action.D

    def clone(self) -> Player:
        return GenerousTitForTat(self.forgiveness)


class AlwaysCooperate(Player):
    name = "Always Cooperate"
    classifier = {**Player.classifier, "memory_depth": 0, "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        return Action.C


class AlwaysDefect(Player):
    name = "Always Defect"
    classifier = {**Player.classifier, "memory_depth": 0, "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        return Action.D


class Random(Player):
    """Cooperate with fixed probability (default 0.5)."""

    def __init__(self, p: float = 0.5) -> None:
        super().__init__()
        self.p = p
        self.name = f"Random ({p})"
        self.classifier = {**Player.classifier, "memory_depth": 0, "stochastic": True}

    def strategy(self, opponent: Player) -> Action:
        return Action.C if self.rng.random() < self.p else Action.D

    def clone(self) -> Player:
        return Random(self.p)


class Grudger(Player):
    """Cooperate until the opponent defects once, then defect forever.

    Also known as Friedman. Submitted by James W. Friedman.
    """

    name = "Grudger"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        if Action.D in opponent.history:
            return Action.D
        return Action.C


class Pavlov(Player):
    """Win-Stay, Lose-Shift.

    Repeat the last action if it earned R or T; otherwise switch.
    """

    name = "Pavlov (Win-Stay Lose-Shift)"
    classifier = {**Player.classifier, "memory_depth": 1, "stochastic": False}

    def strategy(self, opponent: Player) -> Action:
        if not self.history:
            return Action.C
        mine, theirs = self.history[-1], opponent.history[-1]
        won = (mine is Action.C and theirs is Action.C) or (
            mine is Action.D and theirs is Action.C
        )
        return mine if won else mine.flip()


class Joss(Player):
    """TFT that defects with probability (1-p) after opponent cooperates.

    Johann Joss, first tournament. Default p=0.9 (sneaks 10% of the time).
    """

    def __init__(self, p: float = 0.9) -> None:
        super().__init__()
        self.p = p
        self.name = f"Joss ({p})"
        self.classifier = {**Player.classifier, "memory_depth": 1, "stochastic": True}

    def strategy(self, opponent: Player) -> Action:
        if not opponent.history:
            return Action.C
        if opponent.history[-1] is Action.D:
            return Action.D
        return Action.C if self.rng.random() < self.p else Action.D

    def clone(self) -> Player:
        return Joss(self.p)


class Davis(Player):
    """Cooperate for the first 10 rounds, then play Grudger.

    Morton Davis, first tournament (8th place).
    """

    name = "Davis"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def __init__(self, rounds_of_grace: int = 10) -> None:
        super().__init__()
        self.rounds_of_grace = rounds_of_grace

    def strategy(self, opponent: Player) -> Action:
        if len(opponent.history) < self.rounds_of_grace:
            return Action.C
        if Action.D in opponent.history:
            return Action.D
        return Action.C


class Feld(Player):
    """TFT that cooperates after C with a linearly falling probability.

    Scott Feld, first tournament.
    """

    name = "Feld"

    def __init__(self, start: float = 1.0, end: float = 0.5, expected_turns: int = 200) -> None:
        super().__init__()
        self.start = start
        self.end = end
        self.expected_turns = expected_turns
        self.classifier = {**Player.classifier, "memory_depth": 1, "stochastic": True}

    def strategy(self, opponent: Player) -> Action:
        if not opponent.history:
            return Action.C
        if opponent.history[-1] is Action.D:
            return Action.D
        t = len(self.history)
        frac = min(t / max(self.expected_turns - 1, 1), 1.0)
        p = self.start + (self.end - self.start) * frac
        return Action.C if self.rng.random() < p else Action.D


class Tullock(Player):
    """Cooperate for 11 rounds, then cooperate 10% less often than the opponent.

    Gordon Tullock, first tournament.
    """

    name = "Tullock"
    classifier = {**Player.classifier, "memory_depth": 10, "stochastic": True}

    def strategy(self, opponent: Player) -> Action:
        if len(opponent.history) < 11:
            return Action.C
        window = opponent.history[-10:]
        opp_c = sum(1 for a in window if a is Action.C) / 10.0
        p = max(0.0, opp_c - 0.10)
        return Action.C if self.rng.random() < p else Action.D


class Grofman(Player):
    """Cooperate unless the last moves differed, then cooperate with p=2/7.

    Bernard Grofman, first tournament.
    """

    name = "Grofman"
    classifier = {**Player.classifier, "memory_depth": 1, "stochastic": True}

    def strategy(self, opponent: Player) -> Action:
        if not self.history or not opponent.history:
            return Action.C
        if self.history[-1] == opponent.history[-1]:
            return Action.C
        return Action.C if self.rng.random() < (2 / 7) else Action.D


class Shubik(Player):
    """Retaliation length grows by one after each new provocation.

    Martin Shubik, first tournament.
    """

    name = "Shubik"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def __init__(self) -> None:
        super().__init__()
        self._retaliation_length = 0
        self._retaliation_remaining = 0

    def reset(self) -> None:
        super().reset()
        self._retaliation_length = 0
        self._retaliation_remaining = 0

    def strategy(self, opponent: Player) -> Action:
        if self._retaliation_remaining > 0:
            self._retaliation_remaining -= 1
            return Action.D
        if opponent.history and opponent.history[-1] is Action.D:
            self._retaliation_length += 1
            self._retaliation_remaining = self._retaliation_length - 1
            return Action.D
        return Action.C


class Tester(Player):
    """Probe with an early defection; exploit ALLC, otherwise revert to TFT.

    David Gladstein, second tournament.
    """

    name = "Tester"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def __init__(self) -> None:
        super().__init__()
        self._mode = "probe"

    def reset(self) -> None:
        super().reset()
        self._mode = "probe"

    def strategy(self, opponent: Player) -> Action:
        n = len(self.history)
        if n == 0:
            return Action.C
        if n == 1:
            return Action.D
        if self._mode == "probe":
            if opponent.history[-1] is Action.D:
                self._mode = "tft"
                return Action.C
            self._mode = "exploit"
            return Action.D
        if self._mode == "exploit":
            return Action.D
        return opponent.history[-1]


class Prober(Player):
    """D, C, C then exploit if opponent never punished the opening D."""

    name = "Prober"
    classifier = {**Player.classifier, "memory_depth": float("inf"), "stochastic": False}

    def __init__(self) -> None:
        super().__init__()
        self._exploiting = False
        self._decided = False

    def reset(self) -> None:
        super().reset()
        self._exploiting = False
        self._decided = False

    def strategy(self, opponent: Player) -> Action:
        n = len(self.history)
        if n == 0:
            return Action.D
        if n == 1:
            return Action.C
        if n == 2:
            return Action.C
        if not self._decided:
            self._exploiting = opponent.history[1] is Action.C
            self._decided = True
        if self._exploiting:
            return Action.D
        return opponent.history[-1]


BASIC_STRATEGIES = [
    TitForTat,
    TitForTwoTats,
    TwoTitsForTat,
    SuspiciousTitForTat,
    GenerousTitForTat,
    AlwaysCooperate,
    AlwaysDefect,
    Random,
    Grudger,
    Pavlov,
    Joss,
    Davis,
    Feld,
    Tullock,
    Grofman,
    Shubik,
    Tester,
    Prober,
]


def demo_population() -> list[Player]:
    """A readable mix used by the default experiments."""
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
        SuspiciousTitForTat(),
        TwoTitsForTat(),
        Davis(),
        Tester(),
        Prober(),
        Grofman(),
        Shubik(),
    ]
