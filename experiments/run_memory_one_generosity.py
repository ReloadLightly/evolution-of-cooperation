#!/usr/bin/env python3
"""Noisy Memory-1 with and without ALLC in the field."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eoc.evolve_m1 import MemoryOneGA, format_vector
from eoc.fields import no_sucker_field, representative_eight
from eoc.game import Match
from eoc.genomes import MemoryOne
from eoc.strategies import AlwaysCooperate, AlwaysDefect, Joss, TitForTat
OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)

def probe(champ):
    lines = [format_vector(champ)]
    for label, opp in [("TFT", TitForTat()), ("ALLC", AlwaysCooperate()), ("ALLD", AlwaysDefect()), ("Joss", Joss(0.9)), ("self", champ.clone())]:
        scores, coops = [], []
        for seed in range(5):
            m = Match(champ.clone(), opp.clone(), turns=80, seed=seed)
            s1, _ = m.play(); c1, _ = m.cooperation_rates()
            scores.append(s1); coops.append(c1)
        lines.append(f"  vs {label:<6} score={sum(scores)/len(scores):6.1f}  coop={100*sum(coops)/len(coops):5.1f}%")
    return "\n".join(lines)

def run_case(title, field, field_weight, log):
    log(f"\n=== {title} ===")
    ga = MemoryOneGA(field=field, population_size=20, turns=80, noise=0.05, mutation_sigma=0.06, elite=2, seed=11, field_weight=field_weight, coevolve=field_weight < 1.0)
    result = ga.run(generations=35, seed_tft=False, log=log)
    log(probe(result.champion))
    return result.champion

def main():
    lines = []
    def log(msg):
        print(msg); lines.append(msg)
    run_case("sucker field, noise=0.05, field only", representative_eight(), 1.0, log)
    run_case("no-sucker field, noise=0.05, field only", no_sucker_field(), 1.0, log)
    run_case("no-sucker field, noise=0.05, mixed 0.5", no_sucker_field(), 0.5, log)
    (OUT / "memory_one_generosity.txt").write_text("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
