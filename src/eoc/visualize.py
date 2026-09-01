"""Matplotlib helpers for tournament tables and ecological trajectories."""

from __future__ import annotations

from pathlib import Path

from eoc.ecology import Ecology
from eoc.tournament import TournamentResult


def plot_ecology(ecology: Ecology, path: str | Path, title: str | None = None) -> Path:
    import matplotlib.pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    names = list(ecology.prototypes)
    gens = [g.generation for g in ecology.history]
    fig, ax = plt.subplots(figsize=(10, 6))
    for name in names:
        ys = [g.shares[name] for g in ecology.history]
        if max(ys) < 0.02 and ecology.shares.get(name, 0) < 0.02:
            continue
        ax.plot(gens, ys, label=name, linewidth=2)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Population share")
    ax.set_title(title or "Ecological dynamics (replicator)")
    ax.set_ylim(0, 1)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_tournament_bars(result: TournamentResult, path: str | Path, title: str | None = None) -> Path:
    import matplotlib.pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ranking = result.ranking()
    names = [n for n, _ in ranking][::-1]
    n_matches = len(result.players) * result.repetitions
    avgs = [result.scores[n] / n_matches for n in names]

    fig, ax = plt.subplots(figsize=(9, max(4, 0.35 * len(names) + 1)))
    colors = ["#2a9d8f" if "Tit For Tat" in n and "Suspicious" not in n else "#264653" for n in names]
    ax.barh(names, avgs, color=colors)
    ax.set_xlabel("Average score per match")
    ax.set_title(title or f"Tournament ({result.turns} turns × {result.repetitions} reps)")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path
