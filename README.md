# The Evolution of Cooperation

A small, readable reconstruction of Robert Axelrod's *The Evolution of Cooperation* (1984): the iterated Prisoner's Dilemma, the computer tournaments, and the ecological dynamics that show how reciprocity can get started, thrive, and resist invasion among egoists.

This is an educational implementation, not a replacement for the [Axelrod-Python](https://github.com/Axelrod-Python/Axelrod) library (200+ strategies, noise, Moran processes, spatial lattices). Use that when you need the full research toolkit. Use this when you want the book's argument in a few hundred lines of Python you can actually read.

## What the book is about

The one-shot Prisoner's Dilemma has a dominant strategy: defect. Mutual defection is the unique Nash equilibrium, even though mutual cooperation would make both players better off.

Axelrod's move is to iterate the game. If the same pair meets again with high enough probability — a long *shadow of the future* — a strategy can condition on history. Cooperation then becomes possible without a central authority.

He tested that claim two ways.

1. **Tournaments.** Game theorists submitted programs. Each pair played 200 rounds with Axelrod's payoffs (`T=5, R=3, P=1, S=0`). Anatol Rapoport's **Tit for Tat** won both the 14-strategy first tournament and the 63-strategy second tournament.
2. **Ecology.** Treat tournament scores as fitness. Strategies that do well against the *current* mix become a larger share of the next mix (replicator dynamics). Nice, retaliatory, forgiving rules spread; exploiters shrink as their victims disappear.

TFT's four properties, as Axelrod extracted them:

| Property | Meaning |
|---|---|
| Nice | Never defect first |
| Provocable | Answer a defection with a defection |
| Forgiving | Return to cooperation as soon as the other does |
| Clear | Be simple enough that the other player can learn the pattern |

Two further maxims from the book: *don't be envious* (maximize your own score, not the gap), and *don't be too clever* (complex probing usually backfires).

The book then applies the same logic to trench-warfare live-and-let-live, biological reciprocity (the chapter with W. D. Hamilton), and institutions that lengthen the shadow of the future.

Later work — much of it Axelrod's own *The Complexity of Cooperation* — adds noise, spatial structure, tags/"green beards", and automatically evolved strategies. This repo implements the 1984 core plus noise (pure TFT can lock into mutual defection; Generous TFT and Pavlov recover) and invasion from rarity.

## Payoffs

```
                 Other C          Other D
    You C          R = 3            S = 0
    You D          T = 5            P = 1
```

Constraints: `T > R > P > S` and `2R > T + S` (mutual cooperation beats taking turns exploiting).

## Install

```bash
git clone https://github.com/ReloadLightly/evolution-of-cooperation.git
cd evolution-of-cooperation
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```python
from eoc.game import Match
from eoc.strategies import TitForTat, AlwaysDefect
from eoc.tournament import Tournament
from eoc.strategies import demo_population

m = Match(TitForTat(), AlwaysDefect(), turns=10)
print(m.play())  # (9.0, 14.0) — TFT is suckered once, then defects

result = Tournament(demo_population(), turns=200, repetitions=5, seed=42).play()
print(result.as_table())
```

```bash
python experiments/run_all.py   # tournament, ecology, noise, shadow, invasion
pytest
```

## Repository layout

```
src/eoc/
  actions.py       C / D
  game.py          Payoffs + Match (optional noise)
  player.py        Strategy interface
  strategies/      TFT, TFTT, GTFT, ALLC, ALLD, Grudger, Pavlov,
                   Joss, Davis, Feld, Tullock, Grofman, Shubik,
                   Tester, Prober, …
  tournament.py    Round-robin, including self-play
  ecology.py       Discrete replicator / Axelrod's ecological tournament
  visualize.py     Population-share and ranking plots
experiments/run_all.py
tests/test_core.py
```

## Experiments

`experiments/run_all.py` writes text + figures into `artifacts/`.

1. **Round-robin tournament.** Nice strategies occupy the top ranks. TFT is consistently near the top; ALLD wins individual matches against nice rules but finishes poorly because it never collects `R` against them for long, and it scores only `P` against itself.
2. **Ecological dynamics.** Starting from a uniform mix, exploiters boom while suckers last, then crash as Always-Cooperate shrinks. Reciprocators take over.
3. **Noise.** At 5% implementation error, TFT vs TFT collapses toward defection (one accidental D is copied forever). Generous TFT (`p≈0.3` forgiveness) and Pavlov (win-stay lose-shift) restore cooperation.
4. **Shadow of the future.** With 1–2 rounds, Always Defect wins. As the match lengthens, reciprocators pull ahead.
5. **Invasion.** In a well-mixed 200-round ecology the critical TFT frequency against ALLD is only about 1/397, so even a 1% minority takes over. Clustering is the binding constraint when matches are short or the future is heavily discounted.

## Implementing your own strategy

```python
from eoc.actions import Action
from eoc.player import Player

class MyRule(Player):
    name = "My Rule"
    def strategy(self, opponent: Player) -> Action:
        if not opponent.history:
            return Action.C
        return opponent.history[-1]
```

Drop an instance into `Tournament(...)` or `Ecology(...)`.

## What this does *not* claim

Tit for Tat is not a universal champion. Rankings are an artifact of the field of opponents ("kingmaker" strategies in Axelrod's phrase). Under noise, Generous TFT and win-stay lose-shift beat raw TFT. Zero-determinant strategies, extortion, and trained finite-state machines change the picture again. The durable lesson of the book is not "always play TFT". It is that **reciprocity plus a long enough future is sufficient for cooperation to be evolutionarily viable among self-interested agents**.

## References

- Axelrod, R. (1980). Effective choice in the Prisoner's Dilemma. *Journal of Conflict Resolution*.
- Axelrod, R. (1980). More effective choice in the Prisoner's Dilemma. *Journal of Conflict Resolution*.
- Axelrod, R. & Hamilton, W. D. (1981). The evolution of cooperation. *Science*.
- Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books.
- Axelrod, R. (1997). *The Complexity of Cooperation*. Princeton.
- [Axelrod-Python](https://github.com/Axelrod-Python/Axelrod) — the research-grade library.
