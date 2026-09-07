# Noise, Opponent Composition, and Fitness Sampling in Evolved Cooperation

**Roland Löchli** · Working manuscript and executable research artifact

`evolution-of-cooperation` · E1 and E2 completed · Exploratory results

## Abstract

When does evolutionary search discover forgiveness in the iterated Prisoner's
Dilemma, and how sensitive are its findings to the way fitness is sampled? We
study stochastic memory-one strategies represented by five cooperation
probabilities. E1 crosses action errors (0% or 5%) with the presence of an
unconditional cooperator in an otherwise fixed opponent field. E2 repeats this
design with one versus five training matches per opponent, using five paired
evolution seeds and fresh held-out evaluation. Increasing training repetitions
raises mean held-out payoff in all four E2 conditions, with substantial variation
across seeds. The clearest pattern occurs under 5% errors without an unconditional
cooperator: payoff increases in all five pairs, averaging 0.079 points per turn,
while self-cooperation falls from 53.8% to 41.8%. Noise does not increase mean
conditional forgiveness at either repetition count. These small-budget results
show why payoff, forgiveness, and realized cooperation must be reported separately.
They do not establish a universal strategy ranking or an equal-compute advantage.
Code, complete trajectories, match data, and a reusable vector figure accompany
the manuscript.

## 1. Introduction

Axelrod's account of cooperation emphasizes that the appropriate balance between
retaliation and forgiveness depends on the opponent environment [1, pp. 119-120].
Forgiveness can interrupt continuing retaliation, but an overly forgiving
strategy can be exploited. An evolutionary experiment should therefore discover
behavior under an explicit environment rather than reward a predetermined ideal
of cooperation.

Our question is: **how do action errors, opponent composition, and training
fitness sampling affect the behavior and performance of evolved strategies?**
The current contribution is a controlled, readable computational experiment with
saved, inspectable strategies. We expose the full path from strategy probabilities
to actions, payoffs, selection, and held-out results. E2 asks whether E1's findings
persist when each fitness estimate averages more matches.

## 2. Related work and scope

Axelrod's book provides the substantive motivation [1]. His later work applies
genetic algorithms to evolving strategies represented by three-round lookup
tables [2]. Our repository includes a Lookup70 implementation for educational
reconstruction, but the experiments reported here use a five-probability
memory-one representation. They are contemporary extensions, not exact
replications of Axelrod's tournament field or genetic algorithm.

Nowak and Sigmund study probabilistic strategies and demonstrate circumstances
in which win-stay, lose-shift (Pavlov) outperforms TFT [3]. That work motivates
including Pavlov alongside TFT and Generous TFT as reference behaviors. Its
results do not imply that our particular opponent field must select any of them.
The present related-work discussion is focused; a submission would require a
broader comparison with research on noisy evolutionary optimization and strategy
search. The code also complements the broader
[Axelrod-Python](https://github.com/Axelrod-Python/Axelrod) ecosystem.

## 3. Model and evolutionary method

### 3.1. Game and action errors

Matches contain 80 simultaneous rounds. C denotes cooperation and D defection.
The row player's stage payoff is:

| My action / opponent action | C | D |
|---|---|---|
| C | 3 | 0 |
| D | 5 | 1 |

Each player's sampled action flips independently with probability
$\epsilon \in \{0, 0.05\}$. Both players observe realized actions. The noise model
represents action errors, not private observation errors.

### 3.2. Strategy representation

A genome is $p=(p_0,p_{CC},p_{CD},p_{DC},p_{DD})\in[0,1]^5$.

| Parameter | Probability of cooperating... |
|---|---|
| $p_0$ | On the first move |
| $p_{CC}$ | After mutual cooperation |
| $p_{CD}$ | After I cooperated and the opponent defected |
| $p_{DC}$ | After I defected and the opponent cooperated |
| $p_{DD}$ | After mutual defection |

TFT is `(1, 1, 0, 1, 0)`; Generous TFT(q=0.1) is `(1, 1, 0.1, 1, 0.1)`;
Pavlov is `(1, 1, 0, 0, 1)`; ALLD is `(0, 0, 0, 0, 0)`.
We use $p_{CD}$ as a conditional forgiveness measure. It is not an overall
cooperation rate: realized behavior depends on the other probabilities and the
states actually visited.

### 3.3. Search and fitness

The population contains 20 randomly initialized genomes, with no planted TFT.
We evaluate 35 populations: generation 0 followed by 34 breeding steps. Selection
uses tournaments of size 3. Two elites survive; offspring use blend crossover
with probability 0.7 and Gaussian mutation with standard deviation 0.06, clipped
to $[0,1]$. The same evolution seed pairs initial populations and variation RNGs
across conditions. Fitness differences can then change the selected parents.

For opponent set $O$ and $K$ training matches per opponent, training fitness is
mean total match payoff:

$$
\widehat F_K(p)=\frac{1}{|O|K}\sum_{o\in O}\sum_{r=1}^{K}\sum_{t=1}^{80}u(a_t,b_t).
$$

The seven common opponents are TFT, ALLD, Grudger, Joss(0.9), Random(0.5), Tester,
and Pavlov. ALLC is appended in the presence condition. Opponents have equal
weight within a field; adding ALLC changes common-opponent weights from 1/7 to
1/8. The comparison estimates a change in composition. Fitness uses no peer
interaction or self-play. The reported champion is the best individual in the
final evaluated population, selected without consulting held-out results.

## 4. Experimental design

### 4.1. Questions and hypotheses

- **H1:** action errors increase evolved $p_{CD}$, helping interrupt retaliation.
- **H2:** ALLC creates opportunities for exploitation and may reduce selection
  pressure for cooperative behavior.
- **H3 (E2):** five-match fitness improves final-champion held-out payoff relative
  to one-match fitness under the same opponent distribution and noise.

These are empirical predictions, not acceptance criteria. E2 was chosen after
observing E1; it is an exploratory follow-up, not a preregistered confirmation.

### 4.2. Conditions, sampling, and cost

E1 crosses noise {0%, 5%} and ALLC {absent, present}, using one training match
per opponent. E2 adds training repetitions {1, 5}. Both use five paired evolution
seeds (0-4). E1 has 20 runs; E2 has 40 runs, including a rerun of E1's 20
one-match configurations. Those reruns are not new independent evolutionary seeds.

The five-match arm includes each one-match arm's first match seed. Training seeds
are reused by population position across generations, as in E1. E2 varies sample
count, not seed refresh policy. More sampling is intended to reduce estimation
noise; estimator variance itself is not directly measured here.

**Table 1. E2 training cost across all seeds and conditions.** Population size and
generations are fixed; the comparison does not hold compute fixed.

| Training matches per opponent | Training matches | Training rounds |
|---|---|---|
| 1 | 105,000 | 8,400,000 |
| 5 | 525,000 | 42,000,000 |

### 4.3. Held-out evaluation and analysis

Each champion is evaluated at both noise levels against the common seven
opponents, ALLC separately, and its own copy. TFT, GTFT(q=0.1), Pavlov, and ALLD
use the same evaluation schedule. Twenty match seeds per evolution seed are
shared across conditions and baselines. E2's seeds start at $2\times10^{12}$,
disjoint from E1's evaluation and from training.

The primary E2 outcome is the paired five-minus-one difference in held-out
payoff per turn against the corresponding training field at matched noise.
Self-play is excluded from this payoff. Secondary outcomes are common-field
payoff, $p_{CD}$, $p_{CC}$, and self-cooperation. We report paired means and
sample standard deviations across evolution seeds, retaining all five differences.
Matches within a seed are repeated measurements, not independent replications.

Full protocols: [E1](docs/forgiveness_e1.md) and [E2](docs/forgiveness_e2.md).

## 5. Results

### 5.1. E1: noise did not increase mean forgiveness

With one-match training, mean $p_{CD}$ falls from 0.254 to 0.180 without ALLC
and from 0.350 to 0.151 with ALLC when noise is introduced. These means conceal
mixed signs across seeds. The [E1 results](results/forgiveness_e1/summary.md)
contain all paired differences, baseline scores, and variability.

### 5.2. E2: extra sampling improves mean payoff, with uneven paired effects

**Table 2. E2 paired changes from one to five training matches.** Payoff uses
fresh matches against the corresponding training field at matched noise.
Parentheses give sample SD across five paired evolution seeds; pp denotes
percentage points. Positive-pair counts refer to payoff, not cooperation.

| Noise | ALLC | Payoff/turn change (SD) | Positive payoff pairs | $p_{CD}$ change | Self-cooperation change |
|---|---|---|---|---|---|
| 0% | absent | +0.004 (0.255) | 3/5 | +0.012 | -6.7 pp |
| 0% | present | +0.022 (0.050) | 3/5 | -0.085 | -4.4 pp |
| 5% | absent | +0.079 (0.060) | 5/5 | -0.037 | -12.0 pp |
| 5% | present | +0.029 (0.055) | 4/5 | -0.071 | -0.4 pp |

The noisy, ALLC-absent condition has the most consistent paired payoff increase:
mean payoff rises from 1.741 to 1.820, while self-cooperation falls from 53.8% to
41.8%. Clean, ALLC-absent results vary strongly across seeds; their near-zero
mean should not be interpreted as a precise null effect.

![Paired seed differences in held-out payoff and conditional forgiveness](figures/e2_paired_effects.svg)

**Figure 1.** Five-minus-one training-repetition differences. Each dot represents
one paired evolution seed; horizontal bars mark means. Panel A uses the matching
training opponent distribution and evaluation noise. Panel B measures the genome's
conditional cooperation probability after CD. Five-match training consumes five
times as many training matches. [Vector PDF](figures/e2_paired_effects.pdf) ·
[Plot source](experiments/plot_forgiveness_e2.py) ·
[Figure data](results/forgiveness_e2/paired_differences.csv).

### 5.3. E2: the negative mean noise effect on forgiveness persists

With five-match training, mean $p_{CD}$ falls from 0.267 to 0.143 without ALLC
and from 0.265 to 0.081 with ALLC as noise rises. The respective paired mean
noise effects are -0.124 and -0.184. All five seeds show a negative noise effect
in the ALLC-present, five-match condition. H1 is not supported in these fields
and budgets; this does not establish that noise generally suppresses forgiveness.

One actual E2 champion (seed 0, five matches, 5% noise, ALLC present) is
approximately `(0.6373, 0.0000, 0.0611, 0.0000, 0.7958)`. It always intends to
defect after mutual cooperation and often cooperates after mutual defection.
This is an inspectable behavioral rule, not merely a fitness score. The full
precision vector and its trajectory are stored in
[champions.json](results/forgiveness_e2/champions.json).

### 5.4. Reference strategies and evidence

Under E2's fresh noisy evaluation on the common seven opponents, TFT scores
1.809, GTFT(q=0.1) 1.812, Pavlov 1.718, and ALLD 1.761 per turn. These are
context-specific references; comparisons must use the same evaluation field and
noise. Five seeds do not support declaring a general winner.

E2 contains 1,400 generation records, 14,400 champion evaluation matches, and
7,200 baseline evaluation matches. [Full results](results/forgiveness_e2/summary.md)
· [Per-run metrics](results/forgiveness_e2/run_metrics.csv)
· [Raw champion matches](results/forgiveness_e2/evaluation.csv)
· [Raw baseline matches](results/forgiveness_e2/baselines.csv).

## 6. Discussion

The results distinguish performance against a fixed opponent field from
cooperation among copies of the evolved strategy. More training sampling can
improve the former while reducing the latter. This is compatible with the
fitness objective: selection rewards individual payoff against the field and
contains no direct reward for cooperative self-play.

E2 suggests that E1's negative mean noise effect on conditional forgiveness was
not solely a consequence of using one training match. It does not establish the
mechanism responsible. Opponent composition, representation, repeated training
seeds, and the search budget remain plausible influences. The conditional nature
of forgiveness in Axelrod's discussion motivates examining these environments;
the pilot does not test the book's broader social or political claims.

## 7. Limitations

Five evolution seeds and 35 evaluated populations provide exploratory evidence.
We do not estimate asymptotic performance, report significance claims, or equate
repeated match observations with independent searches. Five-match training costs
five times more; no equal-compute advantage is established. Fixed position-indexed
training seeds may permit adaptation to sampled matches. We have not measured
fitness-estimator variance or tested refreshed training seeds.

The opponent field is deliberately small and is not a representative sample of
all possible strategies. Adding ALLC changes normalized opponent weights. The
five-probability representation limits available behavior; $p_{CD}$ alone does
not capture generosity, state occupancy, or overall cooperation. Nearest-reference
names describe L1 vector distance, not behavioral equivalence. Earlier
[legacy summaries](artifacts/README.md) are retained with explicit provenance
limits and are not treated as verified replication evidence.

## 8. Conclusion and next experiment

Under the tested conditions, averaging more training matches modestly improves
mean held-out payoff while leaving the negative mean noise effect on forgiveness
intact. Higher payoff can coexist with less cooperation. The next substantive
step, E3, is a paired comparison of fixed-field and mixed field/peer selection,
using the existing coevolution engine to test whether peer interaction changes
that relationship. E3 has not yet been run.

## References

1. Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books.
2. Axelrod, R. (1987). The evolution of strategies in the iterated Prisoner's
   Dilemma. In L. Davis (Ed.), *Genetic Algorithms and Simulated Annealing*,
   pp. 32-41. Morgan Kaufmann.
   [Author's later adapted chapter](https://www.cse.unr.edu/~simingl/papers/DSA/Evolving%20New%20Strategies%20Iterated%20Prisoner%20Dilemma.pdf).
3. Nowak, M., & Sigmund, K. (1993). A strategy of win-stay, lose-shift that
   outperforms tit-for-tat in the Prisoner's Dilemma game. *Nature*, 364, 56-58.
   [doi:10.1038/364056a0](https://doi.org/10.1038/364056a0).

[BibTeX bibliography](references.bib). Cite this computational artifact using
`ReloadLightly/evolution-of-cooperation`, the experiment ID, and the exact commit.
This working manuscript has not been submitted or peer reviewed.

## Appendix A. Reproducibility and learning from the code

The experiment and inspection scripts require only Python 3.10+ standard library;
no API keys or paid services. From the repository root, inspect a saved E2 strategy:

```bash
python3 examples/inspect_memory_one.py --results results/forgiveness_e2/champions.json --run 7 --turns 20
```

Watch a small E2 run live, then inspect the newly evolved five-match champion:

```bash
RUN_DIR="artifacts/forgiveness_e2_live_$(date +%Y%m%d_%H%M%S)"
python3 -u experiments/run_forgiveness_e2.py --seeds 0 --generations 5 --eval-reps 3 --output "$RUN_DIR"
python3 examples/inspect_memory_one.py --results "$RUN_DIR/champions.json" --run 7
```

For the complete 40-run E2 experiment:

```bash
python3 -u experiments/run_forgiveness_e2.py --output artifacts/forgiveness_e2_live_full
```

Each output directory must be new or empty. Records are ordered by seed, then
training repetitions (1, 5), noise (0, 0.05), and ALLC (absent, present).
The [E1 runner](experiments/run_forgiveness.py) and E1 outputs remain unchanged.

Follow the execution through
[`MemoryOne.strategy()`](src/eoc/genomes.py),
[`Match.play()`](src/eoc/game.py),
[`MemoryOneGA.evaluate()` and `breed()`](src/eoc/evolve_m1.py), and the
[E2 runner](experiments/run_forgiveness_e2.py).

For tests and figure generation:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python experiments/plot_forgiveness_e2.py
```

**Validation:** 41 tests pass. All 20 E2 one-match champions and complete histories
exactly reproduce E1. A five-match run replays its champion, all 35 generation
records, and 360 evaluation matches exactly. Source/protocol hashes match the
executed files; the [E2 manifest](results/forgiveness_e2/manifest.json) records
parameters, Python version, and the base commit. The base commit may precede local
edits; hashes identify the code actually run.

## Appendix B. Manuscript development and experiment sequence

The README is the canonical manuscript narrative. Tables point to saved data;
Figure 1 is available as PDF/SVG/PNG; references are maintained in BibTeX. The
[manuscript map](docs/manuscript.md) identifies what can be transferred into an
article document when the evidence warrants submission. The
[experiment roadmap](docs/ROADMAP.md) keeps E3 coevolution and E4 spatial
cooperation separate from the completed E1/E2 results.
