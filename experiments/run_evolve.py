#!/usr/bin/env python3
"""Evolve 70-bit lookup strategies against a fixed Axelrod-like field."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eoc.evolve import GeneticAlgorithm, describe
from eoc.fields import representative_eight
from eoc.game import Match
from eoc.genomes import Lookup70
from eoc.strategies import AlwaysCooperate, AlwaysDefect, Joss, TitForTat

OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)


def probe(champion: Lookup70) -> str:
    opponents = [
        TitForTat(),
        AlwaysCooperate(),
        AlwaysDefect(),
        Joss(0.9),
        Lookup70.tit_for_tat(),
    ]
    lines = [describe(champion), ""]
    for opp in opponents:
        scores = []
        coops = []
        for seed in range(5):
            m = Match(champion.clone(), opp.clone(), turns=80, seed=seed)
            s1, _ = m.play()
            c1, _ = m.cooperation_rates()
            scores.append(s1)
            coops.append(c1)
        mean_s = sum(scores) / len(scores)
        mean_c = sum(coops) / len(coops)
        lines.append(
            f"  vs {opp.name:<28} score={mean_s:6.1f}  coop={100 * mean_c:5.1f}%"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ga = GeneticAlgorithm(
        field=representative_eight(),
        population_size=24,
        turns=80,
        noise=0.0,
        crossover_rate=0.7,
        mutation_rate=0.02,
        elite=2,
        seed=7,
        field_reps=1,
        coevolve=False,
    )
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    result = ga.run(generations=30, seed_tft=False, log=log)
    report = probe(result.champion)
    print()
    print(report)
    (OUT / "evolve_log.txt").write_text("\n".join(log_lines) + "\n\n" + report)
    (OUT / "evolve_champion.json").write_text(
        json.dumps(
            {
                "bits": result.champion.bits,
                "tft_agreement": result.champion.tft_agreement(),
                "coop_bias": result.champion.cooperation_bias(),
                "history": [rec.__dict__ for rec in result.history],
            },
            indent=2,
        )
    )
    print(f"Wrote {OUT / 'evolve_log.txt'}")


if __name__ == "__main__":
    main()
