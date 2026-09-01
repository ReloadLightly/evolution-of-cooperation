"""Smallest possible reconstruction of Axelrod's argument."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eoc.game import Match
from eoc.strategies import AlwaysCooperate, AlwaysDefect, TitForTat
from eoc.tournament import Tournament

players = [TitForTat(), AlwaysCooperate(), AlwaysDefect()]
result = Tournament(players, turns=200, repetitions=1, seed=0).play()
print(result.as_table())
print()

m = Match(TitForTat(), AlwaysDefect(), turns=5)
print("TFT vs ALLD, 5 turns:", m.play(), "transcript:", " ".join(m.transcript()))
