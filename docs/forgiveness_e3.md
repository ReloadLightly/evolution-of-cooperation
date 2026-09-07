# E3: selection through the evolving population

## Protocol fixed before the full run

Does adding selection through interaction with the evolving population increase
cooperation between population members, and what happens to performance against
the fixed opponent field? E2's five-match training improved held-out payoff under
5% errors without ALLC while self-cooperation decreased. E3 follows up on exactly
that condition. This is an exploratory, sequential experiment, not a public
preregistration. Complete this bounded comparison; do not run E4.

Primary hypothesis: mixed selection increases cooperation between distinct
members of the final population. The hypothesis does not determine acceptance,
champion selection, stopping, or interpretation.

## Fixed design

Five paired evolution seeds, 0–4, each run in this order:

| Regime | Training fitness | field_weight |
|---|---|---|
| fixed | Mean payoff against the seven fixed opponents | 1.0 |
| mixed | 0.5 × mean field payoff + 0.5 × mean peer payoff | 0.5 |

Both use `controlled_forgiveness_field(False)` (TFT, ALLD, Grudger, Joss(0.9),
Random(0.5), Tester, Pavlov), action-error probability 0.05, population 20,
35 evaluated populations including generation 0, and 80 rounds per match.
There are five training matches per fixed opponent. Initialize randomly without
planted TFT; use mutation sigma 0.06, crossover probability 0.7, two elites, and
tournament size 3. Retain the five memory-one probabilities and payoffs
T=5, R=3, P=1, S=0. Fitness uses total match payoff; reported payoff is per turn.
The champion is the best individual in the final training population.

Pair initialization and variation RNG seeds. Selection can cause populations
and chosen parents to diverge. Match seeds never consume the variation RNG.

## Peer scoring and training seeds

Mixed selection evaluates every unordered pair `i <= j` five times, using
separate clones. Distinct pairs credit both players; a diagonal match credits
only the first player's score once to that individual. The second clone's score
is discarded. This preserves the existing diagonal counting convention.
Each individual's peer mean divides its total by its actual scored-match count:
`20 * 5 = 100` at the full settings, including five diagonal scores. Field means
divide by `7 * 5 = 35`. Combine these normalized means with 50/50 weights;
do not pool the unequal numbers of matches.

The field seed remains exactly `s + i * 1_000_003 + o * 97 + r`, where `s` is
the evolution seed, `i` the current population position, `o` the opponent index,
and `r` the zero-based repetition. Thus fixed runs can reproduce E2.

E3 peer seeds use base `100_000_000_000 + s * 1_000_000`, plus
`2 * ((j * (j + 1) // 2 + i) * 5 + r)` for `i <= j`. This triangular pair
index is unique. Match gives the second player seed + 1; spacing by two keeps
these streams distinct within this schedule. Positions are those before the
evaluation's fitness sort. Seeds are fixed by position and repetition across
generations. This is not a seed-refresh treatment. The engine's default
`peer_reps=1, peer_seed=None` retains the historical `s + 17*i + 31*j` schedule.

Training matches per evaluated population: fixed `20*7*5=700`; mixed adds
`20*21/2*5=1,050`. Actual executed-match counters must verify 24,500 matches per
fixed run and 61,250 per mixed run. Mixed uses 36,750 extra matches per run,
2.5 times the training match budget (+150%). All ten runs total 428,750 matches,
34,300,000 rounds. Record training and evaluation wall time separately.
This fixes population and generations, not compute.

## Held-out evaluation

Save every final population genome in final fitness order, including duplicates.
Evaluate all 190 off-diagonal unordered pairs (`i < j`) for 20 fresh matches
each at noise 0.05, with 80 rounds. The primary outcome averages realized
cooperation equally across both players and all 3,800 matches. Also report mutual
cooperation (fraction of CC rounds) and mean payoff across both players. Distinct
members may have identical genomes; no diagonal matches enter these outcomes.

Evaluate each champion separately against the common seven-opponent field, its
own copy, and ALLC as a diagnostic, for 20 matches per opponent at noise 0.05.
Champion self-cooperation uses the focal (first) player, consistent with E2;
raw records retain both players. Evaluate TFT, GTFT(q=0.1), Pavlov, and ALLD on
the same field schedule, once per evolution seed. Held-out results never enter
evolution, champion choice, or stopping.

Held-out match seeds are `3_000_000_000_000 + s*100_000_000 + d*10_000_000
+ 2*(k*100 + r)`: domain `d=0` for population pairs, `1` for the common field,
`2` for champion self-play, `3` for ALLC. For population pairs,
`k=j*(j-1)//2+i`; for field evaluation, `k` is the opponent index; otherwise
`k=0`. Repetitions are zero based. Corresponding seeds are shared across regimes
and field baselines. These namespaces are disjoint from training and E1/E2.
CLI limits (seeds < 1000, population <= 100, evaluation repetitions <= 100)
keep namespace allocations disjoint, including second-player seeds. Full E3 uses
only the fixed settings above; reduced CLI budgets are for smoke/replay checks.

## Analysis, artifacts, and verification

Treat each evolution seed as one replication. Compute mixed-minus-fixed
differences within each seed before reporting all five differences, their mean,
and sample SD. Report primary population cooperation, secondary population mutual
cooperation, population payoff, champion field payoff, champion self-cooperation,
ALLC diagnostics, and all five champion probabilities. Do not compare mixed and
fixed raw training fitness as a common performance outcome.

The runner writes parameters, seed schedules, source/protocol hashes, base commit,
generation histories, full-precision champions, all final genomes, raw held-out
population/champion/baseline matches, per-run metrics, paired differences, measured
cost, a console log, and a generated summary under `results/forgiveness_e3/`.
One restrained two-panel figure shows the five paired cooperation and field-payoff
differences; retain reusable SVG/PDF and plotting source.

Verify repetition counting, diagonal semantics, normalization, weights, legacy
behavior, seed separation, and deterministic replay in tests. Run a small smoke
experiment before ten full runs. Afterward compare every fixed champion and all
35 history records to E2's five-match/noisy/ALLC-absent run of the same seed.
Replay seed 0 mixed training and all its held-out measurements exactly. Record
verification and analyze actual results without requiring improvement.

## Limits

Five seeds and one field, noise level, representation, and search budget support
exploratory descriptions only. Matches are repeated measurements, not independent
evolutionary runs. Including a clone in training means E3 estimates the effect
of this complete peer-selection regime; it cannot isolate interaction with
distinct members from clone selection. Fixed position seeds, extra compute, and
finite matches remain limitations. E3 does not identify long-term stability,
mechanisms, equal-compute superiority, or spatial invasion success.

## Commands

```bash
python3.12 -u experiments/run_forgiveness_e3.py --seeds 0 --generations 5 --eval-reps 3 --output artifacts/forgiveness_e3_short
python3.12 examples/inspect_memory_one.py --results results/forgiveness_e3/champions.json --run 1 --turns 20
python3.12 -u experiments/run_forgiveness_e3.py --output results/forgiveness_e3
```

Use a new or empty output directory. Records are ordered by seed, then fixed and
mixed; record 1 is seed 0 mixed. The runner uses only the standard library.

Exact E2 history reproduction uses Python 3.12.13, matching E2. An initial
Python 3.10.12 execution reproduced the fixed champions but showed last-bit
differences in recorded mean fitness. Those outputs are retained locally under
`artifacts/forgiveness_e3_python310/`; the verified published run uses 3.12.13.
No scientific settings or seed schedules were changed in this runtime correction.
