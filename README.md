# The Evolution of Cooperation

A small, readable research and learning project about cooperation in the iterated
Prisoner's Dilemma, inspired by Robert Axelrod's *The Evolution of Cooperation*.
It contains tournaments, ecological dynamics, genetic strategy search,
coevolution, and spatial experiments. Historical reconstructions and contemporary
extensions are exploratory; the project does not claim exact historical replication.

## Research question

**When does forgiveness evolve, and when does an evolved strategy exploit its
opponents instead?** Axelrod's discussion of retaliation and forgiveness
(chapter 6, pp. 119-120) motivates the current experiment: the useful balance
between forgiveness and retaliation depends on the opponent environment.

## Current contribution: E1

E1 repairs the memory-one evolutionary runner and supplies a controlled,
replayable comparison of action errors and unconditional cooperation in the
opponent field. It evolves actual strategies, saves their full probability
vectors, and evaluates their behavior on fresh match seeds.

A strategy is five probabilities: `(p0, pCC, pCD, pDC, pDD)`. For example,
TFT is `(1, 1, 0, 1, 0)`. CC/CD/DC/DD describe the previous round from the
strategy's perspective: its own action first, then its opponent's action.
The genetic algorithm changes these probabilities using selection, blend
crossover, and Gaussian mutation.

| Probability | What the strategy decides |
|---|---|
| p0 | Cooperate on the first move |
| pCC | Cooperate after mutual cooperation |
| pCD | Cooperate after I cooperated and the opponent defected |
| pDC | Cooperate after I defected and the opponent cooperated |
| pDD | Cooperate after mutual defection |

## Hypotheses and experimental design

H1: action errors increase evolved pCD, helping escape continuing retaliation.
H2: an unconditional cooperator creates opportunities for exploitation and may
reduce selection pressure for cooperative behavior. Both are hypotheses, not
requirements imposed on the outcome.

E1 crosses 0%/5% action errors with Always-Cooperate (ALLC) absent/present. Seven
other opponents remain identical. The comparison uses five paired seeds, 20
individuals, 35 evaluated populations, and 80 rounds per match. It uses fixed-field
fitness, with no peer interaction or planted TFT. Fitness averages over seven or
eight opponents, so adding ALLC also renormalizes the opponent weights.

Each final champion and TFT, Generous TFT(q=0.1), Pavlov, and ALLD are evaluated
at both noise levels on 20 fresh match seeds per evolution seed. Evaluation uses
the common seven opponents, ALLC separately, and self-play. See the
[full design](docs/forgiveness_e1.md) for seed schedules, parameters and limitations.

## Results

**Completed: 20 evolutionary runs and 36,000 held-out match records.**
Means below use five evolution seeds. Payoff and self-cooperation use evaluation
noise matching training noise; common-field payoff always excludes ALLC.

| Training noise | ALLC | Evolved pCD | Common-field payoff/turn | Self cooperation |
|---|---|---|---|---|
| 0% | absent | 0.254 | 1.949 | 84.9% |
| 0% | present | 0.350 | 1.947 | 68.0% |
| 5% | absent | 0.180 | 1.750 | 53.9% |
| 5% | present | 0.151 | 1.807 | 36.5% |

Noise did **not** increase average evolved forgiveness in this pilot. The paired
mean pCD difference was -0.074 without ALLC and -0.199 with ALLC, with mixed signs
across seeds. Under noisy training, ALLC presence was associated with lower mean
pCC (0.604 to 0.202) and self-cooperation (53.9% to 36.5%). These describe this
small search budget and opponent field, not a universal law of cooperation.

An actual champion from seed 0, noise 5%, ALLC present is approximately
`(0.5748, 0.2507, 0.4206, 0.0000, 0.9457)`. It often defects after mutual
cooperation and tends to cooperate after mutual defection. Its nonzero pCD does
not make it a generally cooperative reciprocator. Inspect its play with the
command below; the stored vector retains full precision.

The held-out named baselines remain competitive: GTFT(q=0.1) scores 1.807 per
turn at 5% noise on the common field, versus 1.786 for evolved strategies pooled
across all four training conditions. This pooled comparison does not identify a
winning training condition.

[Results, variability and paired differences](results/forgiveness_e1/summary.md)
· [Champions and trajectories](results/forgiveness_e1/champions.json)
· [Raw match data](results/forgiveness_e1/evaluation.csv)
· [Run manifest](results/forgiveness_e1/manifest.json)

## Run and learn

Python 3.10+ is sufficient for these scripts; they use the standard library and
require no API keys or paid services. From the repository root:

```bash
# Inspect an already evolved strategy, round by round.
python3 examples/inspect_memory_one.py --run 3 --turns 20

# Watch a short run: one seed, four conditions, five evaluated generations each.
python3 -u experiments/run_forgiveness.py --seeds 0 --generations 5 --eval-reps 3 --output artifacts/forgiveness_live_short

# Inspect the strategy produced by that short run.
python3 examples/inspect_memory_one.py --results artifacts/forgiveness_live_short/champions.json --run 3

# Replay the full 20-run pilot into a new directory.
python3 -u experiments/run_forgiveness.py --output artifacts/forgiveness_live
```

Choose a new output directory for each run; existing results are never silently
overwritten. `--run` selects a zero-based saved record. Within each seed the order
is clean/ALLC absent, clean/ALLC present, noisy/ALLC absent, noisy/ALLC present.

Read the code in this order:

1. [`MemoryOne.strategy`](src/eoc/genomes.py): how the five probabilities choose an action.
2. [`Match.play`](src/eoc/game.py): how actions, errors, payoffs and histories interact.
3. [`MemoryOneGA`](src/eoc/evolve_m1.py): initialization, fitness, selection and reproduction.
4. [`run_forgiveness.py`](experiments/run_forgiveness.py): the four experimental conditions and held-out evaluation.
5. [`inspect_memory_one.py`](examples/inspect_memory_one.py): load a champion and examine its decisions.

For development and the older plotting examples:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

## Validation and limitations

39 tests pass. A second complete seed-0 run reproduces all four champions,
generation histories and held-out match records exactly in the recorded Python
environment. Source hashes identify the executed code.

Five seeds and one training match per opponent give noisy fitness estimates and
limited search. Training reuses position-indexed match seeds. Held-out evaluation
measures generalization but does not fix that search limitation. pCD is a
conditional probability; overall cooperation also depends on other probabilities
and the states actually visited. Nearest-reference names are L1 vector labels,
not guarantees of equivalent behavior. Older text summaries are retained as
[legacy artifacts](artifacts/README.md), with their provenance limits stated.

## Next experiment

E2 will test whether the findings survive multiple training matches per opponent.
The [step-by-step roadmap](docs/ROADMAP.md) then returns to coevolution and spatial
cooperation using saved, inspected strategies. Only E1 is completed in this update.

## References and citation

- Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books.
- Axelrod, R. (1987). The evolution of strategies in the iterated Prisoner's Dilemma.
  In L. Davis (Ed.), *Genetic Algorithms and Simulated Annealing*. Morgan Kaufmann.
- Axelrod, R. (1997). *The Complexity of Cooperation*. Princeton University Press.

When citing this computational artifact, identify `ReloadLightly/evolution-of-cooperation`,
the experiment ID, and the exact commit. This educational project complements
[Axelrod-Python](https://github.com/Axelrod-Python/Axelrod).
