# E2: one versus five training matches

All payoff/cooperation columns use evaluation noise matching training noise. Held-out payoff uses the corresponding training field (seven or eight opponents).

| Noise | ALLC | Matches/opponent | pCD | Held-out payoff/turn | Self cooperation |
|---|---|---|---|---|---|
| 0% | absent | 1 | 0.254 | 1.964 | 85.4% |
| 0% | absent | 5 | 0.267 | 1.968 | 78.7% |
| 0% | present | 1 | 0.350 | 2.225 | 67.2% |
| 0% | present | 5 | 0.265 | 2.246 | 62.8% |
| 5% | absent | 1 | 0.180 | 1.741 | 53.8% |
| 5% | absent | 5 | 0.143 | 1.820 | 41.8% |
| 5% | present | 1 | 0.151 | 2.150 | 36.5% |
| 5% | present | 5 | 0.081 | 2.179 | 36.1% |

## Paired five-minus-one differences

Means and sample SD across evolution seeds. All individual differences are in paired_differences.csv.

| Noise | ALLC | Payoff difference (SD) | Positive payoff pairs | pCD difference | Self-cooperation difference |
|---|---|---|---|---|---|
| 0% | absent | +0.004 (0.255) | 3/5 | +0.012 | -6.7 pp |
| 0% | present | +0.022 (0.050) | 3/5 | -0.085 | -4.4 pp |
| 5% | absent | +0.079 (0.060) | 5/5 | -0.037 | -12.0 pp |
| 5% | present | +0.029 (0.055) | 4/5 | -0.071 | -0.4 pp |

## Noise effect on pCD

Within-seed pCD(noise=5%) minus pCD(noise=0%).

| Matches/opponent | ALLC | Mean noise effect | Individual seed differences |
|---|---|---|---|
| 1 | absent | -0.074 | +0.005, -0.089, -0.372, -0.224, +0.308 |
| 1 | present | -0.199 | +0.210, +0.033, -0.414, -0.620, -0.204 |
| 5 | absent | -0.124 | -0.464, -0.054, -0.037, +0.007, -0.073 |
| 5 | present | -0.184 | -0.242, -0.102, -0.054, -0.250, -0.274 |

## Baselines on the common seven opponents

| Strategy | Clean payoff/turn | Noisy payoff/turn |
|---|---|---|
| TFT | 2.115 | 1.809 |
| GTFT(0.1) | 2.174 | 1.812 |
| Pavlov | 2.041 | 1.718 |
| ALLD | 1.605 | 1.761 |

## Training cost

| Matches/opponent | Training matches | Training rounds | Measured training seconds |
|---|---|---|---|
| 1 | 105,000 | 8,400,000 | 19.81 |
| 5 | 525,000 | 42,000,000 | 85.53 |

Five-match training uses five times the match budget at fixed population/generations. This does not estimate superiority at equal compute. Five seeds support exploratory descriptions; matches within a seed are repeated measurements.

See [design](../../docs/forgiveness_e2.md) and [README interpretation](../../README.md).
