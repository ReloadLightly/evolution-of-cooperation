"""Ecological / evolutionary dynamics (Axelrod ch. 3).

After a generation of round-robin play, each strategy's share of the
population is updated in proportion to the points it earned:

    p_i(t+1) = p_i(t) * s_i(t) / mean_s(t)

This is discrete replicator dynamics. Strategies that do well against
the *current* mix become a larger part of the next mix — exactly the
'ecological tournament' Axelrod ran for 1000 generations on the second
tournament field.
"""

from __future__ import annotations

from dataclasses import dataclass

from eoc.game import Game, Match
from eoc.player import Player


@dataclass
class Generation:
    generation: int
    shares: dict[str, float]
    scores: dict[str, float]
    mean_score: float


class Ecology:
    """Replicator dynamics over a set of strategy *types*."""

    def __init__(
        self,
        players: list[Player],
        turns: int = 200,
        noise: float = 0.0,
        game: Game | None = None,
        seed: int = 0,
        initial_shares: dict[str, float] | None = None,
    ) -> None:
        self.prototypes = {p.name: p for p in players}
        if len(self.prototypes) != len(players):
            raise ValueError("player names must be unique")
        self.turns = turns
        self.noise = noise
        self.game = game or Game()
        self.seed = seed
        n = len(players)
        if initial_shares is None:
            self.shares = {p.name: 1.0 / n for p in players}
        else:
            total = sum(initial_shares[p.name] for p in players)
            self.shares = {p.name: initial_shares[p.name] / total for p in players}
        self.history: list[Generation] = []
        self._cached_matrix: dict[tuple[str, str], float] | None = None

    def _pairwise_payoff_matrix(self, gen: int) -> dict[tuple[str, str], float]:
        # Without noise the match scores of deterministic (and seeded stochastic)
        # pairs do not depend on the generation index. Cache once.
        if self.noise == 0.0 and self._cached_matrix is not None:
            return self._cached_matrix
        names = list(self.prototypes)
        matrix: dict[tuple[str, str], float] = {}
        # One seeded match per pair is enough for deterministic rules;
        # stochastic rules get 3 repetitions.
        for i, ni in enumerate(names):
            for j, nj in enumerate(names):
                pi = self.prototypes[ni]
                pj = self.prototypes[nj]
                reps = 3 if (pi.classifier.get("stochastic") or pj.classifier.get("stochastic")) else 1
                total = 0.0
                for r in range(reps):
                    a = pi.clone()
                    b = pj.clone()
                    seed = self.seed + gen * 1_000_003 + i * 97 + j * 13 + r
                    s1, _ = Match(
                        a, b, turns=self.turns, noise=self.noise, game=self.game, seed=seed
                    ).play()
                    total += s1
                matrix[(ni, nj)] = total / reps
        if self.noise == 0.0:
            self._cached_matrix = matrix
        return matrix

    def step(self, gen: int) -> Generation:
        names = list(self.prototypes)
        matrix = self._pairwise_payoff_matrix(gen)
        scores: dict[str, float] = {}
        for ni in names:
            # Expected score against the current population mix
            scores[ni] = sum(matrix[(ni, nj)] * self.shares[nj] for nj in names)
        mean = sum(scores[n] * self.shares[n] for n in names)
        if mean <= 0:
            new_shares = dict(self.shares)
        else:
            new_shares = {n: self.shares[n] * scores[n] / mean for n in names}
            z = sum(new_shares.values())
            new_shares = {n: v / z for n, v in new_shares.items()}
        record = Generation(gen, dict(self.shares), scores, mean)
        self.shares = new_shares
        self.history.append(record)
        return record

    def run(self, generations: int = 200) -> list[Generation]:
        for g in range(generations):
            self.step(g)
        return self.history

    def final_shares(self) -> list[tuple[str, float]]:
        return sorted(self.shares.items(), key=lambda kv: kv[1], reverse=True)
