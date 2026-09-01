"""Round-robin tournament in the style of Axelrod 1980."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from eoc.game import Game, Match
from eoc.player import Player


@dataclass
class PairResult:
    name1: str
    name2: str
    score1: float
    score2: float
    coop1: float
    coop2: float


@dataclass
class TournamentResult:
    players: list[str]
    scores: dict[str, float]
    cooperation: dict[str, float]
    wins: dict[str, int]
    pairwise: list[PairResult]
    turns: int
    repetitions: int

    def ranking(self) -> list[tuple[str, float]]:
        return sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)

    def mean_score(self, name: str) -> float:
        """Average score per match (not per turn)."""
        matches = len(self.players) * self.repetitions
        return self.scores[name] / matches

    def as_table(self) -> str:
        rows = self.ranking()
        lines = [
            f"{'Rank':<6}{'Strategy':<32}{'Total':>12}{'Avg/match':>12}{'Coop%':>8}{'Wins':>8}"
        ]
        lines.append("-" * 78)
        n_matches = len(self.players) * self.repetitions
        for i, (name, total) in enumerate(rows, 1):
            avg = total / n_matches
            coop = 100.0 * self.cooperation.get(name, 0.0)
            wins = self.wins.get(name, 0)
            lines.append(
                f"{i:<6}{name:<32}{total:>12.1f}{avg:>12.2f}{coop:>7.1f}%{wins:>8}"
            )
        return "\n".join(lines)


class Tournament:
    """Every player meets every player (including a clone of itself).

    Self-play is included, matching Axelrod: a strategy should do well
    with copies of itself. Scores are summed across repetitions.
    """

    def __init__(
        self,
        players: Sequence[Player],
        turns: int = 200,
        repetitions: int = 5,
        noise: float = 0.0,
        game: Game | None = None,
        seed: int | None = 0,
    ) -> None:
        self.players = list(players)
        self.turns = turns
        self.repetitions = repetitions
        self.noise = noise
        self.game = game or Game()
        self.seed = seed

    def play(self) -> TournamentResult:
        names = [p.name for p in self.players]
        totals: dict[str, float] = {n: 0.0 for n in names}
        coop_sum: dict[str, float] = {n: 0.0 for n in names}
        coop_n: dict[str, int] = {n: 0 for n in names}
        wins: dict[str, int] = {n: 0 for n in names}
        pairwise: list[PairResult] = []

        n = len(self.players)
        match_id = 0
        for i in range(n):
            for j in range(i, n):
                for r in range(self.repetitions):
                    p1 = self.players[i].clone()
                    p2 = self.players[j].clone()
                    seed = None
                    if self.seed is not None:
                        seed = self.seed + match_id * 1009 + r
                    match = Match(
                        p1,
                        p2,
                        turns=self.turns,
                        noise=self.noise,
                        game=self.game,
                        seed=seed,
                    )
                    s1, s2 = match.play()
                    c1, c2 = match.cooperation_rates()
                    n1, n2 = self.players[i].name, self.players[j].name

                    if i == j:
                        totals[n1] += s1
                        coop_sum[n1] += c1
                        coop_n[n1] += 1
                    else:
                        totals[n1] += s1
                        totals[n2] += s2
                        coop_sum[n1] += c1
                        coop_sum[n2] += c2
                        coop_n[n1] += 1
                        coop_n[n2] += 1
                        if s1 > s2:
                            wins[n1] += 1
                        elif s2 > s1:
                            wins[n2] += 1

                    pairwise.append(PairResult(n1, n2, s1, s2, c1, c2))
                    match_id += 1

        cooperation = {
            n: (coop_sum[n] / coop_n[n] if coop_n[n] else 0.0) for n in names
        }
        return TournamentResult(
            players=names,
            scores=totals,
            cooperation=cooperation,
            wins=wins,
            pairwise=pairwise,
            turns=self.turns,
            repetitions=self.repetitions,
        )
