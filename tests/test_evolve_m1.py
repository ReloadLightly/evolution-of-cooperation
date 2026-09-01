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
