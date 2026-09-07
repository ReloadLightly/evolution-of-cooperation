# E3 execution and verification notes

The protocol was written before full execution. The published ten-run dataset
uses Python 3.12.13, matching E2. No scientific settings were changed after
observing outcomes.

- 55 tests passed under both Python 3.10.12 and 3.12.13. E3 tests cover peer
  repetitions, actual counts, diagonal score crediting, normalization, weights,
  legacy defaults, paired initialization, seed separation, and deterministic replay.
- A smoke run (seed 0, both regimes, population 4, three evaluated populations,
  12 rounds, two evaluation repetitions) passed before full execution. Its
  counters reported 420 fixed and 570 mixed training matches, as expected.
- All five published fixed champions and all 175 corresponding history records
  exactly match E2's five-match, noisy, ALLC-absent configurations.
- All 200 final genomes and 350 history records are saved. The verifier checked
  38,000 off-diagonal population matches, 1,800 champion matches, and 2,800
  reference matches. It recomputed every per-run metric and paired difference.
- Seed 0 mixed replay reproduced its champion, 35 history records, 20 genomes,
  3,800 population matches, 180 champion matches, and 560 reference matches
  exactly. Replay took 19.04 seconds, including 61,250 training matches.
- Source/protocol hashes and all recorded match counts passed verification.
  The [machine-readable report](verification.json) records exact evidence hashes.
- The documented short run (seed 0, five evaluated populations, three evaluation
  repetitions) and round-by-round strategy inspection commands completed.
- The SVG/PDF/PNG figure was regenerated from published paired differences and
  visually checked. Local manuscript, protocol, and result links resolve. E1/E2
  output files and runners remain unchanged from the base commit.

An initial complete execution used the shell's Python 3.10.12. All five fixed
champions matched E2, but some recorded population mean fitness values differed
in their last floating-point bits. Those outputs were preserved locally in the
ignored `artifacts/forgiveness_e3_python310/` directory. The full protocol was
rerun with the already available Python 3.12.13 to obtain exact history equality.
Both executions' final-population JSON, raw held-out CSVs, and paired-difference
CSV are byte-identical. This correction adds no independent evolutionary seeds.

The published comparison contains 428,750 training matches and took 95.98 seconds
including evaluation/output (22.59 fixed training seconds, 63.28 mixed training
seconds). The earlier runtime-mismatch execution took 212.35 seconds and another
428,750 training matches. The verification replay adds 61,250 training matches.
Thus full executions plus exact replay used 918,750 training matches, excluding
the smaller smoke runs, short-command check, and unit tests. Rerun/verification
cost is separate from the experimental 2.5× mixed-versus-fixed match comparison.

To repeat the full saved-data checks and exact mixed replay:

```bash
python3.12 -u experiments/verify_forgiveness_e3.py
```

This updates `verification.json` and `replay.log`; wall times will differ.
