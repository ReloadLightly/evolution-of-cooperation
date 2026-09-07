# E1: When does forgiveness evolve?

## Question and source

How do action errors and the availability of an unconditional cooperator affect
memory-one strategies evolved against a fixed opponent field?

Axelrod, *The Evolution of Cooperation*, chapter 6, pp. 119-120, argues that the
balance between forgiveness and retaliation depends on the opponent environment:
forgiveness can avoid continuing retaliation but permits exploitation. This pilot
is a contemporary operationalization, not a historical replication of either the
1984 book's tournaments or Axelrod's later genetic-algorithm experiment.

## Design fixed before the run

Four conditions: action-error probability 0 or 0.05, crossed with ALLC absent or
present. The common opponents, in order, are TFT, ALLD, Grudger, Joss(0.9),
Random(0.5), Tester, and Pavlov. ALLC is appended when present. Each opponent has
equal weight within a condition. Consequently, adding ALLC changes each common
opponent's weight from 1/7 to 1/8; this estimates a change in opponent composition,
not a fixed-weight additive reward. The shared opponents retain their match-seed
indices. The old `no_sucker_field()` changed multiple opponents and is not used.

- Five evolution seeds: 0, 1, 2, 3, 4, paired across the four conditions.
- 20 individuals, 35 evaluated populations (generation 0 plus 34 breeding steps).
- 80 rounds per match; payoffs T=5, R=3, P=1, S=0.
- Random initial five-probability vectors; no planted TFT.
- Blend crossover 0.7, Gaussian mutation sigma 0.06, two elites, tournament size 3.
- Fitness: mean total payoff against the training field; one match per opponent.
- Fixed-field evolution only. No peer scoring or coevolution in E1.
- Existing training match-seed schedule retained; it reuses seeds by population
  position across generations. This is a small-budget search with possible
  adaptation to sampled matches. Held-out evaluation addresses measurement of
  generalization; it does not remove this search limitation.
- Independent action flips with probability `noise` for each player each round.
  Both players observe realized actions. Strategy draws and error draws use each
  player's existing RNG. Equal seeds do not imply identical error events across
  different strategy implementations or clean/noisy conditions.

## Predictions and interpretation

Directional hypothesis H1: noise increases evolved pCD (cooperating after being
exploited). This is a hypothesis to test, not a required outcome. H2: adding ALLC
increases the payoff of exploiting unconditional cooperation and may reduce the
selection pressure for cooperative behavior. Neither prediction follows as a
universal theorem from Axelrod's discussion.

Primary descriptive outcome: paired within-seed difference in final pCD. Report
all five probabilities, especially pCC, alongside realized cooperation. A high
pCD alone cannot establish a generous reciprocal strategy. L1 distance to a named
reference is a descriptive label, not behavioral equivalence.

## Held-out evaluation

Each final champion and four baselines (TFT, GTFT with q=0.1, Pavlov, ALLD) are
measured at both 0% and 5% noise against the common seven opponents, ALLC
separately, and a separate copy of themselves. Twenty fresh match seeds are shared
across conditions and baselines within each evolution seed. They begin at 10^12,
which is disjoint from this pilot's training seeds. Evaluation never selects or
changes the champion. The champion is the best individual in the final evaluated
population, not the best held-out performer or an all-generation champion.

Store every match's payoff per turn, both cooperation rates and mutual cooperation.
Summaries first respect the evolution seed as the unit of replication. Five seeds
support exploration, not precise effect estimates. Cross-environment evaluation
is reported separately from matched training/evaluation noise.

## Outputs and reproducibility

`results/forgiveness_e1/` contains the manifest, complete generation log, full
precision champions and trajectories, raw held-out evaluation CSV, and generated
summary. The manifest records Python, parameters, base commit and SHA-256 hashes
of every source module and the runner. The source hashes identify executed code
when the base commit precedes local edits. The attached copyrighted book is not
included in the repository.

```bash
python experiments/run_forgiveness.py --output artifacts/forgiveness_live
python examples/inspect_memory_one.py --run 0
```

The runner refuses to overwrite a nonempty output directory. Use a new output
path for another run. A short learning run is:

```bash
python -u experiments/run_forgiveness.py --seeds 0 --generations 5 --eval-reps 3 --output artifacts/forgiveness_live_short
python examples/inspect_memory_one.py --results artifacts/forgiveness_live_short/champions.json --run 0
```

The scripts add `src` to the import path and require only Python 3.10+ standard
library. Tests additionally require pytest. No paid services, API keys or LLMs.

## Completion criteria

Repair regression tests pass; all 20 pilot runs complete; each vector stays in
[0,1]; all held-out rows are present; one full seed replays identically; conclusions
are written from the actual results. No required cooperation or fitness threshold.
