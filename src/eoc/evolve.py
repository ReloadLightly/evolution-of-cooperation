"""Genetic algorithm over Lookup70 genomes.

Axelrod 1987 experiment 1: 70-bit lookup tables scored against a fixed
field. Fitness is mean score per match. Operators: elitism, tournament
selection, single-point crossover, bit-flip mutation.

Coevolution (experiment 2): set coevolve=True to also score each genome
against the rest of the current population.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Sequence

from eoc.fields import representative_eight
from eoc.game import Game, Match
from eoc.genomes import Lookup70
from eoc.player import Player


@dataclass
class Individual:
    genome: Lookup70
    fitness: float = 0.0


@dataclass
class GenerationRecord:
    generation: int
    best_fitness: float
    mean_fitness: float
    best_tft_agreement: float
    best_coop_bias: float
    best_label: str
    best_bits: list[int]


@dataclass
class EvolveResult:
    history: list[GenerationRecord]
    champion: Lookup70
    population: list[Individual]


class GeneticAlgorithm:
    def __init__(
        self,
        field: Sequence[Player] | None = None,
        population_size: int = 20,
        turns: int = 80,
        noise: float = 0.0,
        crossover_rate: float = 0.7,
        mutation_rate: float = 0.01,
        elite: int = 2,
        tournament_k: int = 3,
        coevolve: bool = False,
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
        self.mutation_rate = mutation_rate
        self.elite = min(elite, population_size)
        self.tournament_k = tournament_k
        self.coevolve = coevolve
        self.seed = seed
        self.game = game or Game()
        self.field_reps = field_reps
        self.rng = random.Random(seed)
        self.population: list[Individual] = []
        self.history: list[GenerationRecord] = []

    def _spawn(self) -> Lookup70:
        return Lookup70.random(self.rng)

    def initialize(self, seed_tft: bool = True) -> None:
        self.population = [Individual(self._spawn()) for _ in range(self.population_size)]
        if seed_tft and self.population_size >= 1:
            self.population[0] = Individual(Lookup70.tit_for_tat())

    def _score_against_field(self, genome: Lookup70, tag: int) -> float:
        total = 0.0
        n = 0
        for i, opp in enumerate(self.field):
            for r in range(self.field_reps):
                a = genome.clone()
                b = opp.clone()
                seed = self.seed + tag * 1_000_003 + i * 97 + r
                s1, _ = Match(
                    a, b, turns=self.turns, noise=self.noise, game=self.game, seed=seed
                ).play()
                total += s1
                n += 1
        return total / n if n else 0.0

    def _score_against_peers(self, index: int) -> float:
        total = 0.0
        n = 0
        me = self.population[index].genome
        for j, other in enumerate(self.population):
            if j == index:
                continue
            a = me.clone()
            b = other.genome.clone()
            seed = self.seed + 17 * index + 31 * j
            s1, _ = Match(
                a, b, turns=self.turns, noise=self.noise, game=self.game, seed=seed
            ).play()
            total += s1
            n += 1
        return total / n if n else 0.0

    def evaluate(self) -> None:
        for i, ind in enumerate(self.population):
            field_score = self._score_against_field(ind.genome, tag=i)
            if self.coevolve:
                peer = self._score_against_peers(i)
                ind.fitness = 0.5 * field_score + 0.5 * peer
            else:
                ind.fitness = field_score
        self.population.sort(key=lambda ind: ind.fitness, reverse=True)

    def _record(self, generation: int) -> GenerationRecord:
        best = self.population[0]
        mean = sum(ind.fitness for ind in self.population) / len(self.population)
        rec = GenerationRecord(
            generation=generation,
            best_fitness=best.fitness,
            mean_fitness=mean,
            best_tft_agreement=best.genome.tft_agreement(),
            best_coop_bias=best.genome.cooperation_bias(),
            best_label=best.genome.name,
            best_bits=list(best.genome.bits),
        )
        self.history.append(rec)
        return rec

    def _tournament_pick(self) -> Lookup70:
        k = min(self.tournament_k, len(self.population))
        picks = self.rng.sample(self.population, k)
        winner = max(picks, key=lambda ind: ind.fitness)
        return Lookup70(winner.genome.bits)

    def _crossover(self, a: Lookup70, b: Lookup70) -> tuple[Lookup70, Lookup70]:
        if self.rng.random() > self.crossover_rate:
            return Lookup70(a.bits), Lookup70(b.bits)
        point = self.rng.randrange(1, 70)
        c1 = a.bits[:point] + b.bits[point:]
        c2 = b.bits[:point] + a.bits[point:]
        return Lookup70(c1), Lookup70(c2)

    def _mutate(self, genome: Lookup70) -> Lookup70:
        bits = list(genome.bits)
        for i in range(70):
            if self.rng.random() < self.mutation_rate:
                bits[i] = 1 - bits[i]
        return Lookup70(bits)

    def breed(self) -> None:
        elite = [
            Individual(Lookup70(ind.genome.bits, label=ind.genome.name))
            for ind in self.population[: self.elite]
        ]
        children: list[Individual] = []
        while len(elite) + len(children) < self.population_size:
            p1 = self._tournament_pick()
            p2 = self._tournament_pick()
            c1, c2 = self._crossover(p1, p2)
            children.append(Individual(self._mutate(c1)))
            if len(elite) + len(children) < self.population_size:
                children.append(Individual(self._mutate(c2)))
        self.population = elite + children

    def run(
        self,
        generations: int = 40,
        seed_tft: bool = False,
        log: Callable[[str], None] | None = None,
    ) -> EvolveResult:
        self.initialize(seed_tft=seed_tft)
        for g in range(generations):
            self.evaluate()
            rec = self._record(g)
            if log:
                log(
                    f"gen {g:3d}  best={rec.best_fitness:7.2f}  "
                    f"mean={rec.mean_fitness:7.2f}  "
                    f"TFT-agree={100 * rec.best_tft_agreement:5.1f}%  "
                    f"coop-table={100 * rec.best_coop_bias:5.1f}%"
                )
            if g < generations - 1:
                self.breed()
        champion = Lookup70(self.population[0].genome.bits, label="evolved-champion")
        return EvolveResult(history=self.history, champion=champion, population=self.population)


def describe(genome: Lookup70) -> str:
    return (
        f"{genome.name}  TFT-agree={100 * genome.tft_agreement():.1f}%  "
        f"coop-table={100 * genome.cooperation_bias():.1f}%"
    )
