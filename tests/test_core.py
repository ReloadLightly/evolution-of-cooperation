from eoc.actions import Action
from eoc.ecology import Ecology
from eoc.game import Game, Match, Payoff
from eoc.strategies import AlwaysCooperate, AlwaysDefect, Pavlov, TitForTat, TitForTwoTats
from eoc.tournament import Tournament


def test_payoffs():
    g = Game()
    assert g.play_round(Action.C, Action.C) == (3, 3)
    assert g.play_round(Action.D, Action.C) == (5, 0)
    assert g.play_round(Action.C, Action.D) == (0, 5)
    assert g.play_round(Action.D, Action.D) == (1, 1)


def test_tft_vs_allc():
    m = Match(TitForTat(), AlwaysCooperate(), turns=10, seed=0)
    s1, s2 = m.play()
    assert s1 == 30 and s2 == 30
    assert m.cooperation_rates() == (1.0, 1.0)


def test_tft_vs_alld():
    m = Match(TitForTat(), AlwaysDefect(), turns=10, seed=0)
    s1, s2 = m.play()
    # TFT cooperates once then defects: S + 9P = 0+9=9; ALLD: T + 9P = 5+9=14
    assert s1 == 9 and s2 == 14


def test_tft_self():
    m = Match(TitForTat(), TitForTat(), turns=50, seed=0)
    s1, s2 = m.play()
    assert s1 == s2 == 150


def test_tf2t_forgives_once():
    m = Match(TitForTwoTats(), AlwaysDefect(), turns=5, seed=0)
    s1, s2 = m.play()
    assert s1 == 3 and s2 == 13


def test_pavlov_vs_alld():
    m = Match(Pavlov(), AlwaysDefect(), turns=6, seed=0)
    s1, _ = m.play()
    assert s1 == 0 + 1 + 0 + 1 + 0 + 1


def test_tournament_runs():
    t = Tournament(
        [TitForTat(), AlwaysDefect(), AlwaysCooperate()],
        turns=20,
        repetitions=2,
        seed=1,
    )
    r = t.play()
    assert set(r.players) == {"Tit For Tat", "Always Defect", "Always Cooperate"}
    assert r.ranking()[0][0] in {"Tit For Tat", "Always Defect", "Always Cooperate"}


def test_ecology_alld_dominates_mixed_short_or_invades_poorly():
    eco = Ecology(
        [TitForTat(), AlwaysDefect()],
        turns=200,
        seed=0,
        initial_shares={"Tit For Tat": 0.01, "Always Defect": 0.99},
    )
    eco.run(generations=20)
    assert eco.shares["Tit For Tat"] < 0.05


def test_ecology_tft_holds_majority():
    eco = Ecology(
        [TitForTat(), AlwaysDefect()],
        turns=200,
        seed=0,
        initial_shares={"Tit For Tat": 0.6, "Always Defect": 0.4},
    )
    eco.run(generations=30)
    assert eco.shares["Tit For Tat"] > 0.9
