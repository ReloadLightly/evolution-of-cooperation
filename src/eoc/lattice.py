"""Spatial iterated PD on a 2D lattice.

A single TFT dies in a sea of ALLD. A cluster that mostly meets itself
can expand, because the interior scores R against copies while the ALLD
sea only scores P.

Each generation every cell plays an IPD match against each neighbor,
then copies the highest-scoring strategy among itself and its neighbors
(Nowak–May imitate-the-best). The grid is a torus by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from eoc.game import Game, Match
from eoc.player import Player

Neighborhood = Literal["von_neumann", "moore"]

OFFSETS = {
    "von_neumann": ((-1, 0), (1, 0), (0, -1), (0, 1)),
    "moore": (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ),
}


def _wrap(i: int, n: int) -> int:
    return i % n


@dataclass
class LatticeRecord:
    generation: int
    counts: dict[str, int]
    mean_score: float
    flips: int


class Lattice:
    def __init__(
        self,
        grid: list[list[Player]],
        neighborhood: Neighborhood = "von_neumann",
        turns: int = 40,
        noise: float = 0.0,
        wrap: bool = True,
        game: Game | None = None,
        seed: int = 0,
    ) -> None:
        if not grid or not grid[0]:
            raise ValueError("grid must be non-empty")
        self.height = len(grid)
        self.width = len(grid[0])
        if any(len(row) != self.width for row in grid):
            raise ValueError("grid must be rectangular")
        self.grid = [[cell.clone() for cell in row] for row in grid]
        self.neighborhood = neighborhood
        self.turns = turns
        self.noise = noise
        self.wrap = wrap
        self.game = game or Game()
        self.seed = seed
        self.history: list[LatticeRecord] = []
        self._scores: list[list[float]] | None = None

    def neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        out = []
        for dr, dc in OFFSETS[self.neighborhood]:
            nr, nc = r + dr, c + dc
            if self.wrap:
                out.append((_wrap(nr, self.height), _wrap(nc, self.width)))
            elif 0 <= nr < self.height and 0 <= nc < self.width:
                out.append((nr, nc))
        return out

    def counts(self) -> dict[str, int]:
        tallies: dict[str, int] = {}
        for row in self.grid:
            for cell in row:
                tallies[cell.name] = tallies.get(cell.name, 0) + 1
        return tallies

    def snapshot(self) -> list[list[str]]:
        return [[cell.name for cell in row] for row in self.grid]

    def _pair_key(self, a, b):
        return (a, b) if a <= b else (b, a)

    def score_grid(self) -> list[list[float]]:
        totals = [[0.0] * self.width for _ in range(self.height)]
        nmatch = [[0] * self.width for _ in range(self.height)]
        played = set()
        tag = 0
        for r in range(self.height):
            for c in range(self.width):
                for nr, nc in self.neighbors(r, c):
                    key = self._pair_key((r, c), (nr, nc))
                    if key in played:
                        continue
                    played.add(key)
                    s1, s2 = Match(
                        self.grid[r][c].clone(),
                        self.grid[nr][nc].clone(),
                        turns=self.turns,
                        noise=self.noise,
                        game=self.game,
                        seed=self.seed + tag,
                    ).play()
                    tag += 1
                    totals[r][c] += s1
                    nmatch[r][c] += 1
                    totals[nr][nc] += s2
                    nmatch[nr][nc] += 1
        scores = [
            [totals[r][c] / nmatch[r][c] if nmatch[r][c] else 0.0 for c in range(self.width)]
            for r in range(self.height)
        ]
        self._scores = scores
        return scores

    def step(self) -> int:
        scores = self.score_grid()
        nxt = [[None] * self.width for _ in range(self.height)]
        flips = 0
        for r in range(self.height):
            for c in range(self.width):
                best_score = scores[r][c]
                best = self.grid[r][c]
                for nr, nc in self.neighbors(r, c):
                    if scores[nr][nc] > best_score + 1e-9:
                        best_score = scores[nr][nc]
                        best = self.grid[nr][nc]
                nxt[r][c] = best.clone()
                if nxt[r][c].name != self.grid[r][c].name:
                    flips += 1
        self.grid = nxt
        return flips

    def run(self, generations: int, log=None) -> list[LatticeRecord]:
        self.history = []
        for g in range(generations):
            scores = self.score_grid()
            flat = [s for row in scores for s in row]
            mean = sum(flat) / len(flat)
            rec = LatticeRecord(generation=g, counts=self.counts(), mean_score=mean, flips=0)
            self.history.append(rec)
            if log:
                parts = "  ".join(f"{k}={v}" for k, v in sorted(rec.counts.items()))
                log(f"gen {g:3d}  mean={mean:6.1f}  {parts}")
            if g < generations - 1:
                rec.flips = self.step()
        return self.history

    def as_ascii(self, codes=None) -> str:
        default = {
            "Tit For Tat": "T",
            "Always Defect": "D",
            "Always Cooperate": "C",
            "Grudger": "G",
            "Pavlov": "P",
            "Generous Tit For Tat": "g",
        }
        lookup = {**default, **(codes or {})}
        return "\n".join(
            "".join(lookup.get(cell.name, cell.name[:1]) for cell in row) for row in self.grid
        )


def make_grid(height: int, width: int, fill: Callable[[], Player]) -> list[list[Player]]:
    return [[fill() for _ in range(width)] for _ in range(height)]


def plant_cluster(grid, factory, row, col, height, width):
    for r in range(row, row + height):
        for c in range(col, col + width):
            grid[r][c] = factory()
    return grid
