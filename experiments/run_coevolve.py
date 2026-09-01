#!/usr/bin/env python3
"""Compare field-only, mixed, and pure coevolution."""

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


def probe(champion: Lookup70, turns: int = 80) -> list[dict]:
    rows = []
    opponents = [
        ("Tit For Tat", TitForTat()),
        ("Always Cooperate", AlwaysCooperate()),
        ("Always Defect", AlwaysDefect()),
        ("Joss (0.9)", Joss(0.9)),
        ("self", champion.clone()),
    ]
    for label, opp in opponents:
        scores, coops = [], []
        for seed in range(4):
            m = Match(champion.clone(), opp.clone(), turns=turns, seed=seed)
            s1, _ = m.play()
            c1, _ = m.cooperation_rates()
            scores.append(s1)
            coops.append(c1)
        rows.append(
            {"opponent": label, "score": sum(scores) / len(scores), "coop": sum(coops) / len(coops)}
        )
    return rows


def format_probe(rows: list[dict]) -> str:
    return "\n".join(
        f"  vs {r['opponent']:<28} score={r['score']:6.1f}  coop={100 * r['coop']:5.1f}%"
        for r in rows
    )


def run_regime(name: str, field_weight: float, seed: int, log) -> dict:
    log(f"\n=== {name} (field_weight={field_weight}) ===")
    ga = GeneticAlgorithm(
        field=representative_eight(),
        population_size=20,
        turns=60,
        mutation_rate=0.02,
        elite=2,
        seed=seed,
        field_weight=field_weight,
        coevolve=field_weight < 1.0,
    )
    result = ga.run(generations=25, seed_tft=False, log=log)
    rows = probe(result.champion, turns=80)
    log(describe(result.champion))
    log(format_probe(rows))
    return {
        "regime": name,
        "field_weight": field_weight,
        "tft_agreement": result.champion.tft_agreement(),
        "coop_bias": result.champion.cooperation_bias(),
        "probe": rows,
        "bits": result.champion.bits,
    }


def main() -> None:
    lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    reports = [
        run_regime("field-only", 1.0, seed=7, log=log),
        run_regime("mixed-0.5", 0.5, seed=7, log=log),
        run_regime("coevolve", 0.0, seed=7, log=log),
    ]
    summary = ["\n=== probe summary ==="]
    summary.append(f"{'regime':<14}{'TFT-agr':>10}{'vs TFT':>10}{'vs ALLC':>10}{'vs ALLD':>10}{'vs self':>10}")
    for r in reports:
        by_opp = {p["opponent"]: p for p in r["probe"]}
        summary.append(
            f"{r['regime']:<14}"
            f"{100 * r['tft_agreement']:9.1f}%"
            f"{by_opp['Tit For Tat']['score']:10.1f}"
            f"{by_opp['Always Cooperate']['score']:10.1f}"
            f"{by_opp['Always Defect']['score']:10.1f}"
            f"{by_opp['self']['score']:10.1f}"
        )
    text = "\n".join(summary)
    print(text)
    lines.append(text)
    (OUT / "coevolve_log.txt").write_text("\n".join(lines) + "\n")
    (OUT / "coevolve_summary.json").write_text(json.dumps(reports, indent=2))
    print(f"\nWrote {OUT / 'coevolve_log.txt'}")


if __name__ == "__main__":
    main()
