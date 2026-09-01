# Sequence

```
1. Representation          genomes that are players          done
2. Evaluation field        a reusable opponent set           done
3. GA vs a fixed field     Axelrod 1987, experiment 1        done
4. Coevolution             Axelrod 1987, experiment 2        done
5. Noisy first-tournament  a sharper field, not a new engine
6. Spatial lattice         a different geometry, after we have evolved rules
```

Coevolution uses `field_weight` (1 = field only, 0 = peers only, 0.5 = mix)
and scores every genome against every current peer including a clone of itself.
