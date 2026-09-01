from eoc.game import Match
from eoc.fields import first_tournament_field
from eoc.strategies import AlwaysCooperate, AlwaysDefect, Downing, Graaskamp, SteinAndRapoport, TitForTat


def test_downing_cooperates_with_allc():
    s1, s2 = Match(Downing(), AlwaysCooperate(), turns=20, seed=0).play()
    assert s1 == s2 == 60


def test_downing_learns_to_defect_against_alld():
    s1, s2 = Match(Downing(), AlwaysDefect(), turns=20, seed=0).play()
    assert s1 == 0 + 0 + 18
    assert s2 == 5 + 5 + 18


def test_stein_defects_at_the_end():
    m = Match(SteinAndRapoport(), TitForTat(), turns=10, seed=0)
    m.play()
    assert str(m.history[-1][0]) == "D"
    assert str(m.history[-2][0]) == "D"


def test_graaskamp_starts_like_tft():
    s1, s2 = Match(Graaskamp(), TitForTat(), turns=20, seed=0).play()
    assert s1 == s2 == 60


def test_first_tournament_field_size():
    field = first_tournament_field()
    names = [p.name for p in field]
    assert "Tit For Tat" in names and "Downing" in names and "Anonymous" in names
    assert len(field) >= 12
    assert len(names) == len(set(names))
