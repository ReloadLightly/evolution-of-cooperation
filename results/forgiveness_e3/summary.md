# E3: fixed-field versus mixed field/peer selection

Exploratory results at 5% errors without ALLC in training. Population cooperation averages both players in off-diagonal matches only. Payoff is per turn; cooperation and probabilities use fractions in [0, 1].

| Outcome | Fixed mean | Mixed mean |
|---|---|---|
| population_cooperation | 0.429170 | 0.156404 |
| population_mutual_cooperation | 0.257501 | 0.062607 |
| population_payoff | 2.030009 | 1.406606 |
| champion_field_payoff | 1.823268 | 1.778911 |
| champion_self_cooperation | 0.420125 | 0.147250 |
| champion_allc_payoff | 4.276250 | 4.499500 |
| champion_allc_cooperation | 0.262250 | 0.148125 |
| p0 | 0.530820 | 0.406573 |
| pCC | 0.234717 | 0.410009 |
| pCD | 0.142659 | 0.119277 |
| pDC | 0.132342 | 0.000934 |
| pDD | 0.600182 | 0.053928 |

## Paired mixed-minus-fixed differences

One replication per evolution seed. SD is sample SD across pairs, not across matches. All probabilities and differences retain full precision in CSV.

| Outcome | Seed 0 | Seed 1 | Seed 2 | Seed 3 | Seed 4 | Mean | Sample SD |
|---|---|---|---|---|---|---|---|
| population_cooperation | -0.244240 | -0.365816 | -0.300179 | -0.240946 | -0.212646 | -0.272765 | 0.060931 |
| population_mutual_cooperation | -0.158332 | -0.253796 | -0.206783 | -0.227681 | -0.127878 | -0.194894 | 0.051268 |
| population_payoff | -0.574388 | -0.843651 | -0.693755 | -0.495156 | -0.510061 | -0.623402 | 0.145907 |
| champion_field_payoff | -0.070982 | -0.042054 | -0.076161 | +0.037679 | -0.070268 | -0.044357 | 0.047767 |
| champion_self_cooperation | -0.208750 | -0.360000 | -0.298750 | -0.242500 | -0.254375 | -0.272875 | 0.058389 |
| champion_allc_payoff | +0.031250 | +0.551250 | +0.045000 | +0.383125 | +0.105625 | +0.223250 | 0.232173 |
| champion_allc_cooperation | -0.015000 | -0.283125 | -0.022500 | -0.197500 | -0.052500 | -0.114125 | 0.119928 |
| p0 | -0.524723 | -0.540722 | +0.094465 | +0.072250 | +0.277495 | -0.124247 | 0.381338 |
| pCC | +0.245382 | +0.113665 | +0.109255 | +0.000000 | +0.408158 | +0.175292 | 0.156545 |
| pCD | +0.045510 | -0.013054 | -0.214303 | +0.013071 | +0.051868 | -0.023382 | 0.109881 |
| pDC | +0.000000 | -0.462109 | +0.000000 | -0.117362 | -0.077570 | -0.131408 | 0.191700 |
| pDD | -0.451968 | -0.767848 | -0.645636 | -0.247807 | -0.618013 | -0.546254 | 0.201302 |

## Common-field reference payoff

| Strategy | Mean payoff/turn |
|---|---|
| TFT | 1.794411 |
| GTFT(0.1) | 1.816357 |
| Pavlov | 1.727357 |
| ALLD | 1.758768 |

## Measured cost

| Regime | Training matches | Training rounds | Training seconds | Held-out seconds |
|---|---|---|---|---|
| fixed | 122,500 | 9,800,000 | 22.586 | 4.297 |
| mixed | 306,250 | 24,500,000 | 63.281 | 4.566 |

Total runner wall time: 95.984 seconds; baseline evaluation: 0.557 seconds. Per-run held-out time includes population and champion evaluation.

Mixed training uses 2.5× the matches (+150%) at fixed population/generations. This is 36,750 extra matches per run at these settings. Raw mixed and fixed training fitness are different objectives.

Clone matches are included in mixed training but excluded from the primary outcome. This estimates the complete peer-selection regime, not a distinct-peer-only effect. 5 evolution seeds, fixed position seeds and one environment limit generalization.

See [protocol](../../docs/forgiveness_e3.md) and [manuscript](../../README.md).
