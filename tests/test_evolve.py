from eoc.evolve import GeneticAlgorithm
from eoc.fields import representative_eight
from eoc.game import Match
from eoc.genomes import Lookup70
from eoc.strategies import AlwaysDefect, TitForTat


def test_planted_tft_is_best_against_the_field():
    ga = GeneticAlgorithm(
        field=representative_eight(),
        population_size=8,
        turns=40,
        seed=2,
        field_reps=1,
    )
    ga.initialize(seed_tft=True)
    for i in range(1, len(ga.population)):
        ga.population[i].genome = Lookup70.always_defect()
    ga.evaluate()
    assert ga.population[0].genome.tft_agreement() == 1.0
    assert ga.population[0].fitness > ga.population[-1].fitness


def test_short_evolution_does_not_crash():
    ga = GeneticAlgorithm(population_size=6, turns=20, seed=0, field_reps=1)
    result = ga.run(generations=3, seed_tft=False, log=None)
    assert result.champion.bits
    assert len(result.history) == 3


def test_pure_coevolution_runs():
    ga = GeneticAlgorithm(
        population_size=5,
        turns=12,
        seed=3,
        field_weight=0.0,
        coevolve=True,
        field_reps=1,
    )
    result = ga.run(generations=2, seed_tft=False)
    assert len(result.history) == 2
    assert result.champion.bits


def test_alld_beats_allc_in_peer_scoring():
    ga = GeneticAlgorithm(population_size=6, turns=20, seed=0, field_weight=0.0)
    ga.initialize(seed_tft=False)
    ga.population[0].genome = Lookup70.always_defect()
    for i in range(1, 6):
        ga.population[i].genome = Lookup70.always_cooperate()
    ga.evaluate()
    assert ga.population[0].genome.cooperation_bias() == 0.0
    assert ga.population[0].fitness > ga.population[-1].fitness


def test_champion_is_playable():
    ga = GeneticAlgorithm(population_size=4, turns=15, seed=5, field_reps=1)
    result = ga.run(generations=2, seed_tft=True)
    Match(result.champion, TitForTat(), turns=10, seed=0).play()
    Match(result.champion, AlwaysDefect(), turns=10, seed=0).play()
