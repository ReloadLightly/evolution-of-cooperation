# E2: sensitivity to training fitness sampling

## Question and decision fixed before execution

Do E1's findings change when fitness averages five matches per opponent instead
of one? Does the extra training sampling improve final-champion payoff on fresh
matches against the same opponent distribution?

E2 uses the existing `MemoryOneGA(field_reps=...)` implementation. No change is
made to the game, representation, operators, source modules, or E1 runner.
The one-match arm reruns E1's configurations, making exact champion/trajectory
comparison with the stored E1 records possible. E2 evaluation seeds are new.
This is an exploratory follow-up chosen after seeing E1, not an independent
confirmatory replication or public preregistration.

## Paired design

Cross training repetitions {1, 5}, noise {0, 0.05}, and ALLC {absent, present}.
Five paired evolution seeds {0,1,2,3,4}: 40 runs. Retain E1's 20 individuals,
35 evaluated populations, 80 turns, mutation sigma 0.06, crossover 0.7,
two elites, tournament size 3, and no planted TFT. Shared initial populations
and variation RNG seeds pair the arms. The five-match arm includes the one-match
arm's first match seed, then adds four repetitions. Subsequent populations may
diverge because fitness changes parent selection.

Fitness remains mean total payoff over all opponent/repetition combinations.
The seven common opponents remain fixed, with ALLC appended when present.
Adding ALLC changes equal opponent weights from 1/7 to 1/8, as in E1.

This is a fixed search-size comparison, **not** an equal-compute comparison.
Training matches per run = population x generations x opponents x field_reps:

| Opponents | One match | Five matches |
|---|---|---|
| Seven (ALLC absent) | 4,900 | 24,500 |
| Eight (ALLC present) | 5,600 | 28,000 |

Across all seeds and conditions: 105,000 versus 525,000 training matches
(630,000 total; 50,400,000 rounds). Wall time is descriptive and machine dependent.
The existing position-indexed training seed schedule remains fixed across
generations; E2 does not test resampling each generation or increasing the number
of independent evolutionary runs. More samples are expected to reduce sampling
error; the pilot does not directly estimate fitness-estimator variance.

## Outcomes and analysis

H3: five-match fitness improves final-champion held-out payoff against the
corresponding training opponent distribution at matched evaluation noise.
The primary outcome is the within-seed payoff/turn difference (five minus one),
reported separately in each of the four noise/ALLC conditions. Secondary outcomes:
common-seven-field payoff, pCD, pCC, and self-cooperation. Also report the
within-seed noise effect on pCD separately under each repetition count, to check
whether E1's direction survives. Signs may vary by seed; no required threshold.

Report the five paired differences and their mean/sample SD. Evaluation matches
are repeated measurements, not additional independent evolutionary replications.
No p-values or claims of demonstrated superiority are planned for five seeds.

## Held-out evaluation and references

Every final champion is evaluated at both 0% and 5% noise against the common
seven opponents, ALLC separately, and its own copy. Twenty match seeds per
evolution seed start at 2 x 10^12, disjoint from E1 evaluation (10^12) and this
pilot's training. The same fresh seeds are shared across arms/conditions.
TFT, GTFT(q=0.1), Pavlov and ALLD use that same schedule, evaluated once per seed
and evaluation-noise setting rather than redundantly for each training condition.

Held-out fitness uses the seven common-opponent scores, plus ALLC only when that
training condition includes it. Self-play is never part of this fitness measure.
Champions are selected solely by final-generation training fitness; held-out
results do not alter selection, stopping, budgets or inclusion of seeds.

## Outputs and verification

The runner writes full champions/trajectories, raw champion and baseline match
CSVs, per-run metrics, paired differences, a generated summary, complete console
log, and a source-hashed manifest. A plotting script reads paired differences and
exports PNG/PDF/SVG versions of the same figure. The figure connects each claim
to recorded data and can be reused in a manuscript.

Completion: all 40 runs and expected match records exist; the one-match champions
and histories exactly equal E1; one five-match run replays exactly; field_reps
averages the expected explicit seeded matches; source hashes match executed code;
interpretation reflects actual results.

```bash
python3 -u experiments/run_forgiveness_e2.py --output artifacts/forgiveness_e2_live
python3 examples/inspect_memory_one.py --results artifacts/forgiveness_e2_live/champions.json --run 7
```

For a short live run, add `--seeds 0 --generations 5 --eval-reps 3` and choose a
new output directory. Within each seed, records are ordered by field_reps (1 then
5), noise (0 then 0.05), ALLC (absent then present). Run 7 is the five-match,
noisy, ALLC-present champion from seed 0. Python 3.10+; standard-library runner.
