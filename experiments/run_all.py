#!/usr/bin/env python3
"""Run the core experiments from Axelrod's book and write artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eoc.ecology import Ecology
from eoc.game import Match
from eoc.strategies import (
    AlwaysCooperate,
    AlwaysDefect,
    GenerousTitForTat,
    Grudger,
    Joss,
    Pavlov,
    Random,
    TitForTat,
    demo_population,
)
from eoc.tournament import Tournament
from eoc.visualize import plot_ecology, plot_tournament_bars

OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)


def experiment_tournament() -> dict:
    players = demo_population()
    t = Tournament(players, turns=200, repetitions=5, seed=42)
    result = t.play()
    table = result.as_table()
    (OUT / "tournament.txt").write_text(table + "\n")
    plot_tournament_bars(result, OUT / "tournament.png", "Round-robin tournament (Axelrod payoffs)")
    print(table)
    ranking = result.ranking()
    return {
        "ranking": [{"name": n, "total": s} for n, s in ranking],
        "cooperation": result.cooperation,
        "turns": result.turns,
        "repetitions": result.repetitions,
    }


def experiment_ecology() -> dict:
    players = demo_population()
    eco = Ecology(players, turns=80, seed=7)
    eco.run(generations=150)
    plot_ecology(eco, OUT / "ecology.png", "Ecological tournament — replicator dynamics")
    final = eco.final_shares()
    lines = ["Final population shares after 150 generations:\n"]
    for name, share in final:
        lines.append(f"  {name:<32} {100 * share:6.2f}%")
    text = "\n".join(lines) + "\n"
    (OUT / "ecology.txt").write_text(text)
    print(text)
    return {"final_shares": [{"name": n, "share": s} for n, s in final]}


def experiment_noise() -> dict:
    """Under noise, pure TFT can lock into mutual defection; GTFT / Pavlov recover."""
    pairs = [
        ("TFT vs TFT, noise=0", TitForTat(), TitForTat(), 0.0),
        ("TFT vs TFT, noise=0.05", TitForTat(), TitForTat(), 0.05),
        ("GTFT vs GTFT, noise=0.05", GenerousTitForTat(0.3), GenerousTitForTat(0.3), 0.05),
        ("Pavlov vs Pavlov, noise=0.05", Pavlov(), Pavlov(), 0.05),
        ("TFT vs ALLD, noise=0.05", TitForTat(), AlwaysDefect(), 0.05),
    ]
    rows = []
    for label, a, b, noise in pairs:
        scores = []
        coops = []
        for seed in range(20):
            m = Match(a.clone(), b.clone(), turns=200, noise=noise, seed=seed)
            s1, s2 = m.play()
            c1, c2 = m.cooperation_rates()
            scores.append((s1, s2))
            coops.append((c1, c2))
        mean_s = sum(s[0] for s in scores) / len(scores)
        mean_c = sum(c[0] for c in coops) / len(coops)
        rows.append({"label": label, "mean_score": mean_s, "mean_coop": mean_c})
    lines = ["Noise experiment (20 seeds × 200 turns)\n"]
    for r in rows:
        lines.append(
            f"  {r['label']:<32} score={r['mean_score']:7.1f}  coop={100 * r['mean_coop']:5.1f}%"
        )
    text = "\n".join(lines) + "\n"
    (OUT / "noise.txt").write_text(text)
    print(text)
    return {"rows": rows}


def experiment_shadow() -> dict:
    """Short games favor defection; a long shadow of the future favors reciprocity."""
    turns_list = [1, 2, 5, 10, 25, 50, 100, 200]
    def players_factory():
        return [
            TitForTat(),
            GenerousTitForTat(0.1),
            AlwaysDefect(),
            AlwaysCooperate(),
            Grudger(),
            Pavlov(),
            Joss(0.9),
            Random(0.5),
        ]
    rows = []
    for turns in turns_list:
        t = Tournament(players_factory(), turns=turns, repetitions=8, seed=1)
        result = t.play()
        winner = result.ranking()[0][0]
        n_matches = len(result.players) * result.repetitions
        avgs = {n: result.scores[n] / n_matches / turns for n in result.players}
        rows.append({"turns": turns, "winner": winner, "avg_per_turn": avgs})
    lines = ["Shadow of the future — winner by match length\n"]
    for r in rows:
        lines.append(f"  turns={r['turns']:<4} winner={r['winner']}")
    text = "\n".join(lines) + "\n"
    (OUT / "shadow.txt").write_text(text)
    print(text)
    return {"rows": rows}


def experiment_invasion() -> dict:
    results = []
    for p in (0.01, 0.05, 0.10, 0.25, 0.50):
        eco = Ecology(
            [TitForTat(), AlwaysDefect()],
            turns=200,
            seed=3,
            initial_shares={"Tit For Tat": p, "Always Defect": 1 - p},
        )
        eco.run(generations=80)
        final_tft = eco.shares["Tit For Tat"]
        results.append({"initial_tft": p, "final_tft": final_tft})
    lines = [
        "Invasion of ALLD by TFT (well-mixed replicator, 80 generations, 200-turn matches)\n"
        "With a long shadow of the future the critical frequency is only ~1/397.\n"
        "Clustering matters much more when matches are short or heavily discounted.\n"
    ]
    for r in results:
        lines.append(
            f"  initial TFT={100 * r['initial_tft']:5.1f}%  →  final TFT={100 * r['final_tft']:6.2f}%"
        )
    text = "\n".join(lines) + "\n"
    (OUT / "invasion.txt").write_text(text)
    print(text)
    return {"rows": results}


def experiment_nice() -> dict:
    t = Tournament(demo_population(), turns=200, repetitions=3, seed=11)
    result = t.play()
    nice = {
        "Tit For Tat",
        "Tit For Two Tats",
        "Always Cooperate",
        "Grudger",
        "Pavlov (Win-Stay Lose-Shift)",
        "Davis",
        "Shubik",
        "Generous Tit For Tat (0.1)",
        "Two Tits For Tat",
        "Grofman",
    }
    ranking = result.ranking()
    top_half = [n for n, _ in ranking[: len(ranking) // 2]]
    nice_in_top = sum(1 for n in top_half if n in nice)
    text = (
        "Niceness check: strategies that never defect first tend to occupy the top half.\n"
        f"  Top half ({len(top_half)}): {top_half}\n"
        f"  Nice strategies in top half: {nice_in_top}/{len(top_half)}\n"
    )
    (OUT / "niceness.txt").write_text(text)
    print(text)
    return {"top_half": top_half, "nice_in_top": nice_in_top}


def main() -> None:
    summary = {
        "tournament": experiment_tournament(),
        "ecology": experiment_ecology(),
        "noise": experiment_noise(),
        "shadow": experiment_shadow(),
        "invasion": experiment_invasion(),
        "niceness": experiment_nice(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote artifacts to {OUT}")


if __name__ == "__main__":
    main()
