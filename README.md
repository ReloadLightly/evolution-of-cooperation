# The Evolution of Cooperation

A small, readable reconstruction of Robert Axelrod's *The Evolution of Cooperation* (1984): the iterated Prisoner's Dilemma, the computer tournaments, ecological dynamics, and evolved strategies.

This is an educational implementation, not a replacement for [Axelrod-Python](https://github.com/Axelrod-Python/Axelrod).

## Sequence of work

See [docs/ROADMAP.md](docs/ROADMAP.md). Short version:

1. Representation (Lookup70, Memory-1) — done
2. Evaluation field — done
3. GA vs a fixed field — done (this step)
4. Coevolution — next (`coevolve=True` already exists)
5. Noisy / fuller first-tournament field — sharper fitness, not a new engine
6. Spatial lattice — last; it wants evolved rules to place on the grid

## Install

```bash
git clone https://github.com/ReloadLightly/evolution-of-cooperation.git
cd evolution-of-cooperation
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python experiments/run_evolve.py
pytest
```

## Evolving a strategy

```python
from eoc.evolve import GeneticAlgorithm
from eoc.fields import representative_eight

ga = GeneticAlgorithm(field=representative_eight(), population_size=24, turns=80, seed=7)
result = ga.run(generations=30, seed_tft=False, log=print)
print(result.champion.tft_agreement(), result.champion.cooperation_bias())
```

Against a field that contains Always-Cooperate, evolved champions typically cooperate with TFT and farm ALLC. They do not converge to TFT. That is the 1987 result, not a bug.

Set `coevolve=True` for Axelrod's second experiment (fitness against the current population as well as the field).

## References

- Axelrod, R. (1984). *The Evolution of Cooperation*.
- Axelrod, R. (1987). The evolution of strategies in the iterated Prisoner's Dilemma.
- Axelrod, R. (1997). *The Complexity of Cooperation*.
