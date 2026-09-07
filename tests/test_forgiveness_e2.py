"""Regression checks for the two measurements introduced by E2."""
import runpy
from pathlib import Path

import pytest

from eoc.evolve_m1 import MemoryOneGA
from eoc.game import Match
from eoc.genomes import MemoryOne
from eoc.strategies import AlwaysCooperate, AlwaysDefect


def test_multiple_training_matches_average_each_repetition():
    strategy = MemoryOne(.7, .8, .2, .6, .1)
    opponents = [AlwaysCooperate(), AlwaysDefect()]
    ga = MemoryOneGA(field=opponents, turns=20, noise=.05, seed=3, field_reps=5)
    # Explicit contract: opponent 0 uses seeds 3..7; opponent 1 uses 100..104.
    first = [Match(strategy.clone(), opponents[0].clone(), turns=20, noise=.05, seed=s).play()[0]
             for s in range(3, 8)]
    second = [Match(strategy.clone(), opponents[1].clone(), turns=20, noise=.05, seed=s).play()[0]
              for s in range(100, 105)]
    assert ga._score_against_field(strategy, tag=0) == pytest.approx(sum(first + second) / 10)
    one = MemoryOneGA(field=opponents, turns=20, noise=.05, seed=3, field_reps=1)
    assert one._score_against_field(strategy, tag=0) == (first[0] + second[0]) / 2


def test_heldout_fitness_respects_opponent_weights_and_excludes_self():
    metrics = runpy.run_path(str(Path(__file__).parents[1] / 'experiments/run_forgiveness_e2.py'))['run_metrics']
    run = {'seed': 0, 'field_reps': 5, 'train_noise': .05, 'include_allc': True,
           'champion': (1, 1, 0, 1, 0), 'history': [{'best_fitness': 80}],
           'training_matches': 100, 'training_seconds': .1}
    rows = [{'eval_noise': .05, 'evaluation_set': 'common_field', 'score_per_turn': 1} for _ in range(14)]
    rows += [{'eval_noise': .05, 'evaluation_set': 'ALLC', 'score_per_turn': 5} for _ in range(2)]
    rows += [{'eval_noise': .05, 'evaluation_set': 'self', 'score_per_turn': 3, 'cooperation': 1}]
    rows += [{'eval_noise': 0., 'evaluation_set': 'common_field', 'score_per_turn': 5}]
    result = metrics(run, rows, turns=80)
    assert result['heldout_payoff'] == 1.5  # (7 x 1 + 5) / 8, not (1 + 5) / 2.
    assert result['common_payoff'] == 1
    assert result['self_cooperation'] == 1
    run['include_allc'] = False
    assert metrics(run, rows, turns=80)['heldout_payoff'] == 1
