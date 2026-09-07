"""Scoring contracts and held-out measurements for the bounded E3 experiment."""
import runpy
from pathlib import Path

import pytest

from eoc.evolve_m1 import MemoryOneGA
from eoc.game import Match
from eoc.genomes import MemoryOne

E3 = runpy.run_path(str(Path(__file__).parents[1] / 'experiments/run_forgiveness_e3.py'))


@pytest.mark.parametrize('reps', [0, -1, 1.5, True])
def test_invalid_peer_repetitions(reps):
    with pytest.raises(ValueError, match='peer_reps'):
        MemoryOneGA(peer_reps=reps)


def test_repeated_peers_count_normalize_and_credit_diagonal_once(monkeypatch):
    calls = []

    class ScoredMatch:
        def __init__(self, first, second, **kwargs):
            assert first is not second
            calls.append(kwargs['seed'])

        def play(self):
            return 10., 100.

    monkeypatch.setattr('eoc.evolve_m1.Match', ScoredMatch)
    ga = MemoryOneGA(population_size=3, peer_reps=5, peer_seed=E3['PEER_START'])
    ga.initialize()
    rng_state = ga.rng.getstate()
    # Player zero receives only first-player scores. Player two has ten
    # second-player scores and five first-player diagonal scores: 1050 / 15.
    assert ga._peer_scores() == [10., 40., 70.]
    assert ga.peer_matches == 6 * 5
    assert len(calls) == len(set(calls)) == 30
    assert sorted(calls) == list(range(E3['PEER_START'], E3['PEER_START'] + 60, 2))
    assert ga.rng.getstate() == rng_state
    first_calls = calls[:]
    ga._peer_scores()
    assert calls[30:] == first_calls  # No generation-dependent seed refresh.


def test_legacy_peer_default_matches_explicit_historical_schedule():
    ga = MemoryOneGA(population_size=3, turns=19, noise=.05, seed=4)
    ga.initialize()
    totals = [0., 0., 0.]
    for i in range(3):
        for j in range(i, 3):
            a, b = Match(ga.population[i].genome.clone(), ga.population[j].genome.clone(),
                         turns=19, noise=.05, seed=4 + 17 * i + 31 * j).play()
            totals[i] += a
            if i != j:
                totals[j] += b
    assert ga._peer_scores() == [v / 3 for v in totals]


def test_five_peers_average_explicit_stochastic_matches():
    ga = MemoryOneGA(population_size=2, turns=17, noise=.05, seed=3,
                     peer_reps=5, peer_seed=E3['PEER_START'])
    ga.initialize()
    totals = [0., 0.]
    for i, j, index in [(0, 0, 0), (0, 1, 1), (1, 1, 2)]:
        for r in range(5):
            a, b = Match(ga.population[i].genome.clone(), ga.population[j].genome.clone(),
                         turns=17, noise=.05, seed=E3['PEER_START'] + 2 * (index * 5 + r)).play()
            totals[i] += a
            if i != j:
                totals[j] += b
    assert ga._peer_scores() == [v / 10 for v in totals]


@pytest.mark.parametrize('weight', [0., .5, 1.])
def test_normalized_field_peer_weighting(monkeypatch, weight):
    ga = MemoryOneGA(population_size=2, field_weight=weight)
    ga.initialize()
    original = ga.population[:]
    peer_calls, field_calls = [], []

    def peers():
        peer_calls.append(True)
        return [100., 20.]

    def field(genome, tag):
        field_calls.append(tag)
        return [40., 80.][tag]

    monkeypatch.setattr(ga, '_peer_scores', peers)
    monkeypatch.setattr(ga, '_score_against_field', field)
    ga.evaluate()
    assert [ind.fitness for ind in original] == [weight * 40 + (1-weight) * 100,
                                               weight * 80 + (1-weight) * 20]
    assert len(peer_calls) == (weight < 1)
    assert len(field_calls) == (2 if weight > 0 else 0)


def test_paired_initialization_replay_counts_and_field_regression():
    from eoc.fields import controlled_forgiveness_field
    common = dict(field=controlled_forgiveness_field(False), population_size=4,
                  turns=12, noise=.05, seed=2, mutation_sigma=.06, field_reps=5)
    fixed = MemoryOneGA(**common)
    mixed = MemoryOneGA(**common, field_weight=.5, peer_reps=5, peer_seed=E3['PEER_START'])
    fixed.initialize()
    mixed.initialize()
    assert [i.genome.vector for i in fixed.population] == [i.genome.vector for i in mixed.population]
    assert fixed.rng.getstate() == mixed.rng.getstate()
    a = mixed.run(generations=3)
    b = mixed.run(generations=3)
    assert a.history == b.history
    assert a.champion.vector == b.champion.vector
    assert [i.genome.vector for i in a.population] == [i.genome.vector for i in b.population]
    assert mixed.field_matches == 4 * 7 * 5 * 3
    assert mixed.peer_matches == 10 * 5 * 3  # Counters reset on run().
    legacy = fixed.run(generations=3)
    repeated_peers_unused = MemoryOneGA(**common, peer_reps=5, peer_seed=E3['PEER_START'])
    assert repeated_peers_unused.run(generations=3).history == legacy.history
    assert repeated_peers_unused.peer_matches == 0


def test_population_evaluation_excludes_diagonals_and_averages_both_players():
    # ALLC vs ALLD exposes any accidental focal-player-only aggregation.
    vectors = [MemoryOne.always_cooperate().vector, MemoryOne.always_defect().vector]
    rows = E3['evaluate_population'](vectors, seed=0, turns=20, reps=3)
    assert len(rows) == 3
    assert all((r['i'], r['j']) == (0, 1) for r in rows)
    assert len({r['match_seed'] for r in rows}) == 3
    assert all(r['mean_cooperation'] == (r['cooperation'] + r['opponent_cooperation']) / 2 for r in rows)
    assert all(r['mean_payoff'] == (r['score_per_turn'] + r['opponent_score_per_turn']) / 2 for r in rows)
    assert rows == E3['evaluate_population'](vectors, seed=0, turns=20, reps=3)
    assert [r['match_seed'] for r in rows] == E3['heldout_seeds'](0, 0, 0, 20)[:3]


def test_e3_seed_namespaces_disjoint_and_corresponding_field_seeds_shared():
    field = {s + i * 1_000_003 + o * 97 + r
             for s in range(5) for i in range(20) for o in range(7) for r in range(5)}
    peer = {E3['PEER_START'] + s * 1_000_000 + 2 * (k * 5 + r)
            for s in range(5) for k in range(210) for r in range(5)}
    heldout = [v for s in range(5) for d, count in [(0, 190), (1, 7), (2, 1), (3, 1)]
               for k in range(count) for v in E3['heldout_seeds'](s, d, k, 20)]
    assert len(peer) == 5 * 210 * 5
    assert len(heldout) == len(set(heldout))
    assert not field & peer and not field & set(heldout) and not peer & set(heldout)
    assert not set(heldout) & {s + 1 for s in heldout}
    assert min(heldout) == 3_000_000_000_000
    a = E3['evaluate_field'](MemoryOne.tit_for_tat(), 0, 5, 2)
    b = E3['evaluate_champion'](MemoryOne.always_defect(), 0, 5, 2)
    assert [r['match_seed'] for r in a] == [r['match_seed'] for r in b if r['evaluation_set'] == 'common_field']


def test_metrics_and_paired_differences_keep_outcomes_separate():
    run = dict(seed=0, regime='fixed', field_weight=1., field_matches=1,
               peer_matches=0, training_matches=1, training_seconds=.1,
               champion=(.1, .2, .3, .4, .5))
    pop = [dict(mean_cooperation=.6, mutual_cooperation=.4, mean_payoff=2.)]
    champ = [dict(evaluation_set='common_field', score_per_turn=1.5),
             dict(evaluation_set='self', cooperation=.2),
             dict(evaluation_set='ALLC', score_per_turn=5., cooperation=0.)]
    fixed = E3['run_metrics'](run, pop, champ, .2)
    assert fixed['champion_field_payoff'] == 1.5
    assert fixed['champion_self_cooperation'] == .2
    mixed = {**fixed, 'regime': 'mixed', 'population_cooperation': .8}
    pair = E3['paired_differences']([fixed, mixed])[0]
    assert pair['delta_population_cooperation'] == pytest.approx(.2)
    assert pair['delta_champion_field_payoff'] == 0.
    assert fixed['pDD'] == .5
