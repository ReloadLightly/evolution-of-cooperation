#!/usr/bin/env python3
"""E1: controlled noise x ALLC pilot. Standard library only; no API calls."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
from statistics import mean, stdev
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eoc.evolve_m1 import MemoryOneGA, format_vector
from eoc.fields import controlled_forgiveness_field
from eoc.game import Match
from eoc.genomes import MemoryOne


def references():
    return {"TFT": MemoryOne.tit_for_tat(),
            "GTFT(0.1)": MemoryOne.generous_tft(0.1),
            "Pavlov": MemoryOne.pavlov(),
            "ALLD": MemoryOne.always_defect()}


def evaluate(strategy, opponents, *, noise, turns, seeds):
    """Return one raw row per opponent and held-out match seed."""
    rows = []
    for opponent in opponents:
        for seed in seeds:
            match = Match(strategy.clone(), opponent.clone(), turns=turns,
                          noise=noise, seed=seed)
            score, opponent_score = match.play()
            cooperation, opponent_cooperation = match.cooperation_rates()
            rows.append({"opponent": opponent.name, "match_seed": seed,
                         "score_per_turn": score / turns,
                         "opponent_score_per_turn": opponent_score / turns,
                         "cooperation": cooperation,
                         "opponent_cooperation": opponent_cooperation,
                         "mutual_cooperation": sum(str(a) == str(b) == "C"
                                                   for a, b in match.history) / turns})
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(runs, scores, output):
    lines = ["# E1: controlled forgiveness pilot", "",
             "Descriptive means and sample SD across independent evolution seeds. "
             "Evaluation matches within a run are not independent evolutionary replications.", "",
             "| Training noise | ALLC | pCD mean (SD) | pCC mean | Common-field payoff/turn | Self cooperation |",
             "|---|---|---|---|---|---|"]
    for noise in (0.0, 0.05):
        for include in (False, True):
            group = [r for r in runs if r["train_noise"] == noise and r["include_allc"] == include]
            selected = [r for r in scores if r["train_noise"] == noise and r["include_allc"] == include
                        and r["eval_noise"] == noise and r["strategy"] == "evolved"]
            generosity = [r["champion"][2] for r in group]
            sd = stdev(generosity) if len(generosity) > 1 else 0.0
            lines.append(f"| {noise:.0%} | {'present' if include else 'absent'} | "
                         f"{mean(generosity):.3f} ({sd:.3f}) | "
                         f"{mean(r['champion'][1] for r in group):.3f} | "
                         f"{mean(r['score_per_turn'] for r in selected if r['evaluation_set'] == 'common_field'):.3f} | "
                         f"{mean(r['cooperation'] for r in selected if r['evaluation_set'] == 'self'):.1%} |")
    lines += ["", "All payoff and cooperation columns above use matched training/evaluation noise.",
              "Common-field evaluation always uses the same seven opponents, excluding ALLC.",
              "Self cooperation is evaluated against a separate copy of the same strategy.", "",
              "## Paired differences in pCD", "",
              "Differences are computed within seed before averaging.", ""]
    indexed = {(r['seed'], r['train_noise'], r['include_allc']): r for r in runs}
    seeds = sorted({r['seed'] for r in runs})
    for include in (False, True):
        deltas = [indexed[s, .05, include]['champion'][2] - indexed[s, 0., include]['champion'][2] for s in seeds]
        lines.append(f"- Noise effect with ALLC {'present' if include else 'absent'}: {mean(deltas):+.3f}; seed differences {', '.join(f'{d:+.3f}' for d in deltas)}.")
    for noise in (0., .05):
        deltas = [indexed[s, noise, True]['champion'][2] - indexed[s, noise, False]['champion'][2] for s in seeds]
        lines.append(f"- ALLC presence effect at noise {noise:.0%}: {mean(deltas):+.3f}; seed differences {', '.join(f'{d:+.3f}' for d in deltas)}.")
    lines += ["", "## Held-out baselines", "",
              "Mean payoff/turn against the common seven-opponent field. "
              "Evolved results pool all four training conditions; raw CSV retains each condition.", "",
              "| Strategy | Evaluation noise 0% | Evaluation noise 5% |",
              "|---|---|---|"]
    for label in ["evolved", *references()]:
        values = [mean(r['score_per_turn'] for r in scores if r['strategy'] == label
                       and r['eval_noise'] == noise and r['evaluation_set'] == 'common_field') for noise in (0., .05)]
        lines.append(f"| {label} | {values[0]:.3f} | {values[1]:.3f} |")
    lines += ["", "Small-budget exploratory experiment; no universal claim that noise selects forgiveness.",
              "pCD describes a conditional action probability, not the frequency of visiting CD or overall cooperation.",
              "See [experiment design](../../docs/forgiveness_e1.md) for the design and limitations.", ""]
    (output / "summary.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(5)))
    parser.add_argument("--generations", type=int, default=35)
    parser.add_argument("--population", type=int, default=20)
    parser.add_argument("--turns", type=int, default=80)
    parser.add_argument("--eval-reps", type=int, default=20)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/forgiveness_live")
    args = parser.parse_args()
    if args.generations < 1 or args.population < 2 or args.turns < 1 or args.eval_reps < 1:
        parser.error("positive generations, turns and eval-reps; population >= 2")
    if len(set(args.seeds)) != len(args.seeds) or any(s < 0 or s >= 1_000_000 for s in args.seeds):
        parser.error("seeds must be unique integers in [0, 1000000)")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(f"output is not empty: {output}; choose a new directory")
    output.mkdir(parents=True, exist_ok=True)
    source_files = sorted((ROOT / "src/eoc").rglob("*.py")) + [Path(__file__).resolve()]
    manifest = {"experiment": "E1", "python": platform.python_version(),
                "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
                "seeds": args.seeds, "generations": args.generations, "population": args.population,
                "turns": args.turns, "eval_reps": args.eval_reps,
                "train_noise": [0., .05], "include_allc": [False, True],
                "mutation_sigma": .06, "elite": 2, "crossover_rate": .7,
                "tournament_k": 3, "field_reps": 1, "field_weight": 1., "seed_tft": False,
                "evaluation_seed_start": 1_000_000_000_000,
                "note": "Source hashes identify working-tree code; base_commit may precede these edits."}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    runs, scores = [], []
    with (output / "run.log").open("w") as log_file:
        def log(message):
            print(message, flush=True)
            log_file.write(message + "\n")
            log_file.flush()
        for seed in args.seeds:
            # Shared across treatments and baselines; disjoint from training seeds.
            evaluation_seeds = [1_000_000_000_000 + seed * args.eval_reps + r for r in range(args.eval_reps)]
            for noise in (0., .05):
                for include in (False, True):
                    tag = {"seed": seed, "train_noise": noise, "include_allc": include}
                    log(f"\n=== seed={seed} noise={noise:.0%} ALLC={include} ===")
                    ga = MemoryOneGA(field=controlled_forgiveness_field(include), seed=seed,
                                     population_size=args.population, turns=args.turns,
                                     noise=noise, mutation_sigma=.06, elite=2, field_weight=1.)
                    result = ga.run(generations=args.generations, seed_tft=False, log=log)
                    run = {**tag, "champion": result.champion.vector,
                           "history": [asdict(record) for record in result.history]}
                    runs.append(run)
                    (output / "champions.json").write_text(json.dumps(runs, indent=2) + "\n")
                    log("CHAMPION " + format_vector(result.champion))
                    for label, strategy in {"evolved": result.champion, **references()}.items():
                        for eval_noise in (0., .05):
                            sets = {"common_field": controlled_forgiveness_field(False),
                                    "ALLC": [MemoryOne.always_cooperate()], "self": [strategy.clone()]}
                            for set_name, opponents in sets.items():
                                rows = evaluate(strategy, opponents, noise=eval_noise,
                                                turns=args.turns, seeds=evaluation_seeds)
                                scores.extend({**tag, "strategy": label, "eval_noise": eval_noise,
                                               "evaluation_set": set_name, **row} for row in rows)
                    log("Held-out evaluation complete.")
    write_csv(output / "evaluation.csv", scores)
    summarize(runs, scores, output)
    print((output / "summary.md").read_text())
    print(f"Saved {len(runs)} runs and {len(scores)} match records to {output}")


if __name__ == "__main__":
    main()
