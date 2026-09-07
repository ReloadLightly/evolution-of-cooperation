from eoc.evolve_m1 import MemoryOneGA
from eoc.game import Match
from eoc.genomes import MemoryOne
from eoc.strategies import AlwaysDefect, TitForTat


def test_memory_one_named_distance():
    assert MemoryOne.tit_for_tat().nearest_named()[0] == "TFT"
    assert MemoryOne.pavlov().nearest_named()[0] == "Pavlov"
    assert MemoryOne.generous_tft(0.1).generosity() == 0.1


def test_short_m1_evolution_runs():
    ga = MemoryOneGA(population_size=6, turns=16, noise=0.05, seed=0, field_reps=1)
    result = ga.run(generations=3, seed_tft=False)
    assert len(result.history) == 3
    assert all(0.0 <= p <= 1.0 for p in result.champion.vector)


def test_planted_tft_beats_alld_on_clean_field():
    ga = MemoryOneGA(population_size=6, turns=30, noise=0.0, seed=1, field_reps=1)
    ga.initialize(seed_tft=True)
    for i in range(1, 6):
        ga.population[i].genome = MemoryOne.always_defect()
    ga.evaluate()
    assert ga.population[0].genome.nearest_named()[0] == "TFT"
    assert ga.population[0].fitness > ga.population[-1].fitness


def test_champion_playable():
    ga = MemoryOneGA(population_size=4, turns=12, seed=2)
    result = ga.run(generations=2)
    Match(result.champion, TitForTat(), turns=8, seed=0).play()
    Match(result.champion, AlwaysDefect(), turns=8, seed=0).play()


def test_repeated_run_replays_without_accumulating_history():
    ga = MemoryOneGA(population_size=4, turns=12, seed=5)
    first = ga.run(generations=3)
    second = ga.run(generations=3)
    assert first.history == second.history
    assert first.champion.vector == second.champion.vector
    assert len(first.history) == 3


def test_nearest_named_distance_and_conditional_generosity():
    strategy = MemoryOne(1, 1, 0.2, 1, 0.1)
    name, distance = strategy.nearest_named()
    assert name == 'GTFT(0.1)'
    assert abs(distance - 0.1) < 1e-12
    assert strategy.generosity() == 0.2


def test_controlled_field_only_adds_allc_and_pairs_initial_population():
    from eoc.fields import controlled_forgiveness_field
    absent = controlled_forgiveness_field(False)
    present = controlled_forgiveness_field(True)
    assert [p.name for p in absent] == [p.name for p in present[:-1]]
    assert present[-1].name == 'Always Cooperate'
    populations = []
    for noise in (0., .05):
        for include in (False, True):
            ga = MemoryOneGA(field=controlled_forgiveness_field(include), noise=noise, seed=3)
            ga.initialize()
            populations.append([ind.genome.vector for ind in ga.population])
    assert all(pop == populations[0] for pop in populations)


def test_held_out_evaluator_passes_noise_and_preserves_genome():
    import runpy
    from pathlib import Path
    evaluate = runpy.run_path(str(Path(__file__).parents[1] / 'experiments/run_forgiveness.py'))['evaluate']
    strategy = MemoryOne.always_cooperate()
    clean = evaluate(strategy, [MemoryOne.always_cooperate()], noise=0., turns=8, seeds=[10])
    flipped = evaluate(strategy, [MemoryOne.always_cooperate()], noise=1., turns=8, seeds=[10])
    assert clean[0]['score_per_turn'] == 3
    assert clean[0]['mutual_cooperation'] == 1
    assert flipped[0]['score_per_turn'] == 1
    assert flipped[0]['cooperation'] == 0
    assert strategy.vector == (1, 1, 1, 1, 1)
    assert strategy.history == []
