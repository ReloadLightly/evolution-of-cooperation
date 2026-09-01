# Sequence

Genetic algorithms are the destination. The other two experiments are not equal in how much they unlock that destination.

```
1. Representation          genomes that *are* players
2. Evaluation field        a reusable opponent set (± noise)
3. GA vs a fixed field     Axelrod 1987, experiment 1
4. Coevolution             Axelrod 1987, experiment 2
5. Noisy first-tournament  a sharper field, not a new engine
6. Spatial lattice         a different geometry, after we have evolved rules
```

## Why this order

A GA is three pieces: a genome, a fitness function, and operators (select / cross / mutate). We already have matches, tournaments, and noise. What we did *not* have is a strategy that can be crossed and mutated.

**The noisy first-tournament replica is the fitness function**, not a side quest. Axelrod did not evolve strategies in a vacuum — he scored them against a sample of the second-tournament field. Until that field exists as a callable, "evolve strategies" has nothing principled to select on.

**The spatial lattice is a detour if GA is the goal.** It answers a different question (can a cluster of cooperators grow when meetings are local?). It wants evolved or hand-written rules to *place* on the grid. Build it after the GA is producing those rules.

**Coevolution comes after a fixed-field GA**, not before. Against a fixed field the population is climbing a stable landscape and you can watch it rediscover TFT-like reciprocity. In coevolution the landscape moves; interesting, but harder to debug. Get the operators working on a stationary target first.

## Representations, in the order we will use them

1. **Lookup-70** (Axelrod 1987). Deterministic rule based on the last three rounds of both players, plus six "phantom" bits that stand in for the opening. Search space `2^70`. This is the historically correct first genome.
2. **Memory-1** (four probabilities + an opening). Tiny, stochastic, and the representation behind Generous TFT, Pavlov, and later zero-determinant strategies. Good as a second genome once Lookup-70 works.
3. Finite-state machines, later, if Lookup-70 saturates.

## What "done" looks like for the GA

- Random 70-bit strings, scored against a fixed field, evolve toward niceness + reciprocity.
- An encoded Tit-for-Tat beats the random initial population immediately (sanity check that fitness is not noise).
- Evolved champions, replayed against ALLD / ALLC / TFT / Joss, are inspectable — not just a fitness number.
