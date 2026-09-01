#!/usr/bin/env python3
"""Evolve Memory-1 with and without noise."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eoc.evolve_m1 import MemoryOneGA, format_vector
from eoc.fields import representative_eight
from eoc.game import Match
from eoc.genomes import MemoryOne
from eoc.strategies import AlwaysCooperate, AlwaysDefect, Joss, TitForTat
OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)

def probe(champ):
    lines = [format_vector(champ)]
    for label, opp in [("TFT", TitForTat()), ("ALLC", AlwaysCooperate()), ("ALLD", AlwaysDefect()), ("Joss", Joss(0.9)), ("self", champ.clone())]:
        scores, coops = [], []
        for seed in range(4):
            m = Match(champ.clone(), opp.clone(), turns=80, seed=seed)
            s1, _ = m.play()
            c1, _ = m.cooperation_rates()
            scores.append(s1); coops.append(c1)
        lines.append(f"  vs {label:<6} score={sum(scores)/len(scores):6.1f}  coop={100*sum(coops)/len(coops):5.1f}%")
    return "\n".join(lines)

def run_case(title, noise, field_weight, log):
    log(f"\n=== {title} ===")
    ga = MemoryOneGA(field=representative_eight(), population_size=18, turns=50, noise=noise, mutation_sigma=0.08, elite=2, seed=9, field_weight=field_weight, coevolve=field_weight < 1.0)
    result = ga.run(generations=20, seed_tft=False, log=log)
    log(probe(result.champion))
    return result.champion

def main():
    lines = []
    def log(msg):
        print(msg); lines.append(msg)
    run_case("Memory-1 vs eight-strategy field, noise=0", 0.0, 1.0, log)
    run_case("Memory-1 vs eight-strategy field, noise=0.05", 0.05, 1.0, log)
    run_case("Memory-1 coevolve, noise=0.05", 0.05, 0.0, log)
    (OUT / "memory_one_log.txt").write_text("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
