# Legacy result summaries

The existing `.txt` files predate the E1 repair. They are retained unchanged as
historical project notes, not independently verified reproduction records.

In particular, the prior memory-one checkout lacked `nearest_named()` and
`generosity()`, so its evolutionary runner could not produce these summaries
unchanged. Both old probe scripts also evaluated without noise even when training
used 5% errors. The old `no_sucker_field()` changes multiple opponents, so that
comparison does not isolate the effect of removing ALLC.

The repaired legacy runners now use explicit matched evaluation noise; rerunning
them overwrites their respective old `.txt` outputs and should not be expected to
reproduce the earlier numbers. Use the new E1 runner for preserved, controlled
results: [E1 results](../results/forgiveness_e1/summary.md).
