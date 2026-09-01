"""Genetic algorithm over Memory-1 genomes.

Five probabilities (p0, pCC, pCD, pDC, pDD). Blend crossover and
Gaussian mutation. Noise is the point: TFT can lock into mutual D;
generosity (pCD > 0) or Pavlov (pDD ~ 1) can recover.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Sequence

from eoc.fields import representative_eight
from eoc.game import Game, Match
from eoc.genomes import MemoryOne
from eoc.player import Player


@dataclass
class Individual:
    genome: MemoryOne
    fitness: float = 0.0


@dataclass
class GenerationRecord:
    generation: int
    best_fitness: float
    mean_fitness: float
    best_vector: tuple[float, float, float, float, float]
    best_nearest: str
    best_generosity: float


@dataclass
class EvolveResult:
    history: list[GenerationRecord]
    champion: MemoryOne
    population: list[Individual]


class MemoryOneGA:
    def __init__(
        self,
        field: Sequence[Player] | None = None,
        population_size: int = 20,
        turns: int = 80,
        noise: float = 0.0,
        crossover_rate: float = 0.7,
        mutation_sigma: float = 0.08,
        elite: int = 2,
        tournament_k: int = 3,
        coevolve: bool = False,
        field_weight: float | None = None,
        seed: int = 0,
        game: Game | None = None,
        field_reps: int = 1,
    ) -> None:
        if population_size < 2:
            raise ValueError("population_size must be >= 2")
        self.field = list(field) if field is not None else representative_eight()
        self.population_size = population_size
        self.turns = turns
        self.noise = noise
        self.crossover_rate = crossover_rate
        self.mutation_sigma = mutation_sigma
        self.elite = min(elite, population_size)
        self.tournament_k = tournament_k
        self.coevolve = coevolve
        if field_weight is None:
            self.field_weight = 0.0 if coevolve else 1.0
        else:
            if not 0.0 <= field_weight <= 1.0:
                raise ValueError("field_weight must be in [0, 1]")
            self.field_weight = field_weight
        self.seed = seed
        self.game = game or Game()
        self.field_reps = field_reps
        self.rng = random.Random(seed)
        self.population: list[Individual] = []
        self.history: list[GenerationRecord] = []

    def initialize(self, seed_tft: bool = False) -> None:
        self.population = [
            Individual(MemoryOne.random_vector(self.rng)) for _ in range(self.population_size)
        ]
        if seed_tft:
            self.population[0] = Individual(MemoryOne.tit_for_tat())

    def _score_against_field(self, genome: MemoryOne, tag: int) -> float:
        total = n = 0.0, 0
        total = 0.0
        n = 0
        for i, opp in enumerate(self.field):
            for r in range(self.field_reps):
                s1, _ = Match(
                    genome.clone(),
                    opp.clone(),
                    turns=self.turns,
                    noise=self.noise,
                    game=self.game,
                    seed=self.seed + tag * 1_000_003 + i * 97 + r,
                ).play()
                total += s1
                n += 1
        return total / n if n else 0.0

    def _peer_scores(self) -> list[float]:
        n = len(self.population)
        totals = [0.0] * n
        counts = [0] * n
        for i in range(n):
            for j in range(i, n):
                s1, s2 = Match(
                    self.population[i].genome.clone(),
                    self.population[j].genome.clone(),
                    turns=self.turns,
                    noise=self.noise,
                    game=self.game,
                    seed=self.seed + 17 * i + 31 * j,
                ).play()
                totals[i] += s1
                counts[i] += 1
                if i != j:
                    totals[j] += s2
                    counts[j] += 1
        return [totals[i] / counts[i] for i in range(n)]

    def evaluate(self) -> None:
        peer = self._peer_scores() if self.field_weight < 1.0 else None
        for i, ind in enumerate(self.population):
            if self.field_weight <= 0.0:
                ind.fitness = peer[i] if peer else 0.0
            elif self.field_weight >= 1.0:
                ind.fitness = self._score_against_field(ind.genome, tag=i)
            else:
                field_score = self._score_against_field(ind.genome, tag=i)
                ind.fitness = self.field_weight * field_score + (1.0 - self.field_weight) * peer[i]
        self.population.sort(key=lambda ind: ind.fitness, reverse=True)

    def _record(self, generation: int) -> GenerationRecord:
        best = self.population[0]
        mean = sum(ind.fitness for ind in self.population) / len(self.population)
        nearest, _ = best.genome.nearest_named()
        rec = GenerationRecord(
            generation=generation,
            best_fitness=best.fitness,
            mean_fitness=mean,
            best_vector=best.genome.vector,
            best_nearest=nearest,
            best_generosity=best.genome.generosity(),
        )
        self.history.append(rec)
        return rec

    def _tournament_pick(self) -> MemoryOne:
        k = min(self.tournament_k, len(self.population))
        winner = max(self.rng.sample(self.population, k), key=lambda ind: ind.fitness)
        return MemoryOne(*winner.genome.vector, label=winner.genome.name)

    def _crossover(self, a: MemoryOne, b: MemoryOne) -> tuple[MemoryOne, MemoryOne]:
        if self.rng.random() > self.crossover_rate:
            return MemoryOne(*a.vector), MemoryOne(*b.vector)
        w = self.rng.random()
        c1 = tuple(w * x + (1 - w) * y for x, y in zip(a.vector, b.vector))
        c2 = tuple((1 - w) * x + w * y for x, y in zip(a.vector, b.vector))
        return MemoryOne(*c1), MemoryOne(*c2)

    def _mutate(self, genome: MemoryOne) -> MemoryOne:
        vec = [max(0.0, min(1.0, p + self.rng.gauss(0.0, self.mutation_sigma))) for p in genome.vector]
        return MemoryOne(*vec)

    def breed(self) -> None:
        elite = [Individual(MemoryOne(*ind.genome.vector, label=ind.genome.name)) for ind in self.population[: self.elite]]
        children: list[Individual] = []
        while len(elite) + len(children) < self.population_size:
            c1, c2 = self._crossover(self._tournament_pick(), self._tournament_pick())
            children.append(Individual(self._mutate(c1)))
            if len(elite) + len(children) < self.population_size:
                children.append(Individual(self._mutate(c2)))
        self.population = elite + children

    def run(self, generations: int = 40, seed_tft: bool = False, log: Callable[[str], None] | None = None) -> EvolveResult:
        self.initialize(seed_tft=seed_tft)
        for g in range(generations):
            self.evaluate()
            rec = self._record(g)
            if log:
                v = rec.best_vector
                log(
                    f"gen {g:3d}  best={rec.best_fitness:7.2f}  mean={rec.mean_fitness:7.2f}  "
                    f"near={rec.best_nearest:<9}  "
                    f"p=({v[0]:.2f},{v[1]:.2f},{v[2]:.2f},{v[3]:.2f},{v[4]:.2f})  "
                    f"genr={rec.best_generosity:.2f}"
                )
            if g < generations - 1:
                self.breed()
        champ = self.population[0].genome
        return EvolveResult(
            history=self.history,
            champion=MemoryOne(*champ.vector, label="evolved-m1"),
            population=self.population,
        )


def format_vector(g: MemoryOne) -> str:
    nearest, dist = g.nearest_named()
    return (
        f"{g.name}  p=({g.p0:.2f},{g.p_cc:.2f},{g.p_cd:.2f},{g.p_dc:.2f},{g.p_dd:.2f})  "
        f"nearest={nearest} (L1={dist:.2f})  generosity={g.generosity():.2f}"
    )
