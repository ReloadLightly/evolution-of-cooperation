from eoc.game import Match
from eoc.genomes import Lookup70, MemoryOne, pairs_to_index
from eoc.actions import Action
from eoc.strategies import AlwaysCooperate, AlwaysDefect, TitForTat


def test_pairs_to_index_tft_bit():
    idx = pairs_to_index([(Action.C, Action.C), (Action.C, Action.C), (Action.C, Action.D)])
    assert idx & 1 == 1
    idx = pairs_to_index([(Action.D, Action.D), (Action.D, Action.D), (Action.D, Action.C)])
    assert idx & 1 == 0


def test_lookup_tft_matches_handwritten_vs_alld():
    a = Match(Lookup70.tit_for_tat(), AlwaysDefect(), turns=25, seed=0).play()
    b = Match(TitForTat(), AlwaysDefect(), turns=25, seed=0).play()
    assert a == b


def test_lookup_tft_matches_handwritten_vs_allc():
    a = Match(Lookup70.tit_for_tat(), AlwaysCooperate(), turns=25, seed=0).play()
    b = Match(TitForTat(), AlwaysCooperate(), turns=25, seed=0).play()
    assert a == b


def test_lookup_tft_self_play():
    s1, s2 = Match(Lookup70.tit_for_tat(), Lookup70.tit_for_tat(), turns=20, seed=0).play()
    assert s1 == s2 == 60


def test_lookup_alld():
    s1, s2 = Match(Lookup70.always_defect(), AlwaysCooperate(), turns=10, seed=0).play()
    assert s1 == 50 and s2 == 0


def test_memory_one_tft_vs_alld():
    a = Match(MemoryOne.tit_for_tat(), AlwaysDefect(), turns=20, seed=1).play()
    b = Match(TitForTat(), AlwaysDefect(), turns=20, seed=1).play()
    assert a == b


def test_memory_one_pavlov_oscillates_vs_alld():
    s1, _ = Match(MemoryOne.pavlov(), AlwaysDefect(), turns=6, seed=0).play()
    assert s1 == 0 + 1 + 0 + 1 + 0 + 1


def test_clone_preserves_bits():
    g = Lookup70.tit_for_tat()
    c = g.clone()
    assert c.bits == g.bits
    assert c is not g
