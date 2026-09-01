#!/usr/bin/env python3
"""Spatial IPD: a lone reciprocator dies, a cluster of them grows."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eoc.lattice import Lattice, make_grid, plant_cluster
from eoc.strategies import AlwaysCooperate, AlwaysDefect, Grudger, TitForTat

OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)


def run_case(title, grid, generations, log):
    log(f"\n=== {title} ===")
    lat = Lattice(grid, neighborhood="von_neumann", turns=30, seed=2)
    log("start\n" + lat.as_ascii())
    lat.run(generations, log=log)
    log("end\n" + lat.as_ascii())
    return lat


def main():
    lines = []
    def log(msg):
        print(msg)
        lines.append(msg)

    lone = make_grid(13, 13, AlwaysDefect)
    lone[6][6] = TitForTat()
    run_case("lone TFT in ALLD sea (13x13)", lone, 4, log)

    cluster = make_grid(13, 13, AlwaysDefect)
    plant_cluster(cluster, TitForTat, row=5, col=5, height=3, width=3)
    run_case("3x3 TFT cluster in ALLD sea (13x13)", cluster, 12, log)

    mixed = make_grid(13, 13, AlwaysDefect)
    plant_cluster(mixed, TitForTat, row=2, col=2, height=3, width=3)
    plant_cluster(mixed, AlwaysCooperate, row=2, col=8, height=3, width=3)
    plant_cluster(mixed, Grudger, row=8, col=5, height=3, width=3)
    run_case("TFT + ALLC + Grudger clusters in ALLD", mixed, 10, log)

    (OUT / "lattice_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
