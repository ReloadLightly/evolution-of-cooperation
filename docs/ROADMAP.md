# Experiment sequence

The repo already contains tournaments, ecological dynamics, Lookup70 genetic
search, coevolution, a spatial lattice, and noisy memory-one search. The legacy
text artifacts are exploratory summaries, not a verified historical replication.

Proceed one experiment at a time. Each step should produce runnable code, saved
strategies, measured results, and a short interpretation.

| Step | Question | Status |
|---|---|---|
| E1 | How do noise and ALLC availability affect evolved forgiveness? | Controlled pilot; see [design](forgiveness_e1.md) and [results](../results/forgiveness_e1/summary.md) |
| E2 | Do E1's findings survive less noisy fitness estimates? | Next: compare one versus multiple training matches per opponent with fresh held-out evaluation; report extra compute explicitly |
| E3 | Does adding peer interaction change the evolved strategies? | Later: fixed field versus a defined mixed field/peer regime, using the existing coevolution engine |
| E4 | Can saved evolved strategies establish and maintain spatial cooperation? | Later: place inspected E3 strategies into the existing lattice and compare identical starting grids |

E1 uses the existing five-probability representation. Subsequent steps depend on
what the preceding results show. Increasing the engine's complexity is not itself
a milestone. Older modules remain available for historical and educational work.
