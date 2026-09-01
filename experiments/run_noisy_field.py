#!/usr/bin/env python3
"""Round-robin and GA on the fuller first-tournament field, with and without noise."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eoc.evolve import GeneticAlgorithm, describe
from eoc.fields import first_tournament_field, representative_eight
from eoc.game import Match
from eoc.genomes import Lookup70
from eoc.strategies import AlwaysCooperate, AlwaysDefect, Joss, TitForTat
from eoc.tournament import Tournament

OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)


def tournament_block(noise: float) -> str:
    t = Tournament(first_tournament_field(), turns=80, repetitions=2, noise=noise, seed=11)
    return f"\n=== first-tournament field, noise={noise} ===\n" + t.play().as_table() + "\n"


def probe(champion: Lookup70) -> str:
    lines = [describe(champion)]
    for opp in (TitForTat(), AlwaysCooperate(), AlwaysDefect(), Joss(0.9), champion.clone()):
        label = "self" if opp.name == champion.name else opp.name
        scores, coops = [], []
        for seed in range(4):
            m = Match(champion.clone(), opp.clone(), turns=80, seed=seed)
            s1, _ = m.play()
            c1, _ = m.cooperation_rates()
            scores.append(s1)
            coops.append(c1)
        lines.append(
            f"  vs {label:<28} score={sum(scores)/len(scores):6.1f}  coop={100*sum(coops)/len(coops):5.1f}%"
        )
    return "\n".join(lines) + "\n"


def evolve(name, field, noise, log):
    log(f"\n=== GA vs {name}, noise={noise} ===")
    ga = GeneticAlgorithm(
        field=field, population_size=16, turns=50, noise=noise,
        mutation_rate=0.02, elite=2, seed=13, field_weight=1.0,
    )
    result = ga.run(generations=20, seed_tft=False, log=log)
    log(probe(result.champion))


def main() -> None:
    lines = []
    def log(msg):
        print(msg)
        lines.append(msg)
    log(tournament_block(0.0))
    log(tournament_block(0.05))
    evolve("representative_eight", representative_eight(), 0.0, log)
    evolve("first_tournament_field", first_tournament_field(), 0.05, log)
    (OUT / "noisy_field.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
