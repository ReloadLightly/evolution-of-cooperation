# Experiment sequence

The repo already contains tournaments, ecological dynamics, Lookup70 genetic
search, coevolution, a spatial lattice, and noisy memory-one search. The legacy
text artifacts are exploratory summaries, not a verified historical replication.

Proceed one experiment at a time. Each step should produce runnable code, saved
strategies, measured results, and a short interpretation.

| Step | Question | Status |
|---|---|---|
| E1 | How do noise and ALLC availability affect evolved forgiveness? | Controlled pilot; see [design](forgiveness_e1.md) and [results](../results/forgiveness_e1/summary.md) |
| E2 | Do E1's findings survive more training matches per opponent? | Completed: one versus five matches, 40 runs; [design](forgiveness_e2.md), [results](../results/forgiveness_e2/summary.md) |
| E3 | Does adding peer interaction change the evolved strategies? | Completed: ten fixed/mixed runs at 5% errors without ALLC; cooperation decreased in all five pairs (mean −27.28 pp). [Protocol](forgiveness_e3.md), [results](../results/forgiveness_e3/summary.md), [verification](../results/forgiveness_e3/verification.json) |
| E4 | Can saved evolved strategies establish and maintain spatial cooperation? | Later: place inspected E3 strategies into the existing lattice and compare identical starting grids |

E1 uses the existing five-probability representation. Subsequent steps depend on
what the preceding results show. Increasing the engine's complexity is not itself
a milestone. Older modules remain available for historical and educational work.

The [README](../README.md) follows a research-paper structure; the [manuscript map](manuscript.md) links narrative, tables, figures and bibliography.

E3 stops at the fixed 35 evaluated populations. Its mixed regime includes clone
training and uses 2.5× the training matches; the results are exploratory and do
not establish a general coevolution effect. E4 is a separate future experiment,
not part of this completed update.
