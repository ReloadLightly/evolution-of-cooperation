"""Prisoner's Dilemma payoffs and a single iterated match."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from eoc.actions import Action
from eoc.player import Player


@dataclass(frozen=True)
class Payoff:
    temptation: float = 5.0
    reward: float = 3.0
    punishment: float = 1.0
    sucker: float = 0.0

    def score(self, mine: Action, theirs: Action) -> float:
        if mine is Action.C and theirs is Action.C:
            return self.reward
        if mine is Action.C and theirs is Action.D:
            return self.sucker
        if mine is Action.D and theirs is Action.C:
            return self.temptation
        return self.punishment


class Game:
    def __init__(self, payoff: Payoff | None = None) -> None:
        self.payoff = payoff or Payoff()

    def play_round(self, a: Action, b: Action) -> tuple[float, float]:
        return self.payoff.score(a, b), self.payoff.score(b, a)


class Match:
    def __init__(
        self,
        player1: Player,
        player2: Player,
        turns: int = 200,
        noise: float = 0.0,
        game: Game | None = None,
        seed: int | None = None,
    ) -> None:
        if turns < 1:
            raise ValueError("turns must be >= 1")
        if not 0.0 <= noise <= 1.0:
            raise ValueError("noise must be in [0, 1]")
        self.player1 = player1
        self.player2 = player2
        self.turns = turns
        self.noise = noise
        self.game = game or Game()
        self.seed = seed
        self.history: list[tuple[Action, Action]] = []
        self.scores: tuple[float, float] = (0.0, 0.0)

    def play(self) -> tuple[float, float]:
        self.player1.reset()
        self.player2.reset()
        self.player1.expected_turns = self.turns
        self.player2.expected_turns = self.turns
        if self.seed is not None:
            self.player1.seed(self.seed)
            self.player2.seed(self.seed + 1)
        total1 = total2 = 0.0
        self.history = []
        for _ in range(self.turns):
            a = self.player1.strategy(self.player2)
            b = self.player2.strategy(self.player1)
            if self.noise:
                if self.player1.rng.random() < self.noise:
                    a = a.flip()
                if self.player2.rng.random() < self.noise:
                    b = b.flip()
            s1, s2 = self.game.play_round(a, b)
            total1 += s1
            total2 += s2
            self.player1.update(a, b)
            self.player2.update(b, a)
            self.history.append((a, b))
        self.scores = (total1, total2)
        return self.scores

    def cooperation_rates(self) -> tuple[float, float]:
        if not self.history:
            return 0.0, 0.0
        n = len(self.history)
        c1 = sum(1 for a, _ in self.history if a is Action.C) / n
        c2 = sum(1 for _, b in self.history if b is Action.C) / n
        return c1, c2

    def transcript(self) -> Iterable[str]:
        for a, b in self.history:
            yield f"{a}{b}"
