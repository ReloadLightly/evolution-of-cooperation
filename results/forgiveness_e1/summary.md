# E1: controlled forgiveness pilot

Descriptive means and sample SD across independent evolution seeds. Evaluation matches within a run are not independent evolutionary replications.

| Training noise | ALLC | pCD mean (SD) | pCC mean | Common-field payoff/turn | Self cooperation |
|---|---|---|---|---|---|
| 0% | absent | 0.254 (0.156) | 0.832 | 1.949 | 84.9% |
| 0% | present | 0.350 (0.280) | 0.628 | 1.947 | 68.0% |
| 5% | absent | 0.180 (0.126) | 0.604 | 1.750 | 53.9% |
| 5% | present | 0.151 (0.154) | 0.202 | 1.807 | 36.5% |

All payoff and cooperation columns above use matched training/evaluation noise.
Common-field evaluation always uses the same seven opponents, excluding ALLC.
Self cooperation is evaluated against a separate copy of the same strategy.

## Paired differences in pCD

Differences are computed within seed before averaging.

- Noise effect with ALLC absent: -0.074; seed differences +0.005, -0.089, -0.372, -0.224, +0.308.
- Noise effect with ALLC present: -0.199; seed differences +0.210, +0.033, -0.414, -0.620, -0.204.
- ALLC presence effect at noise 0%: +0.096; seed differences +0.056, -0.253, +0.029, +0.439, +0.209.
- ALLC presence effect at noise 5%: -0.029; seed differences +0.262, -0.132, -0.012, +0.042, -0.303.

## Held-out baselines

Mean payoff/turn against the common seven-opponent field. Evolved results pool all four training conditions; raw CSV retains each condition.

| Strategy | Evaluation noise 0% | Evaluation noise 5% |
|---|---|---|
| evolved | 1.855 | 1.786 |
| TFT | 2.113 | 1.770 |
| GTFT(0.1) | 2.169 | 1.807 |
| Pavlov | 2.038 | 1.696 |
| ALLD | 1.603 | 1.739 |

Small-budget exploratory experiment; no universal claim that noise selects forgiveness.
pCD describes a conditional action probability, not the frequency of visiting CD or overall cooperation.
See [experiment design](../../docs/forgiveness_e1.md) for the design and limitations.
