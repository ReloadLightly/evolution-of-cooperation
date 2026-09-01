from eoc.lattice import Lattice, make_grid, plant_cluster
from eoc.strategies import AlwaysDefect, TitForTat


def test_lone_tft_dies_in_alld_sea():
    grid = make_grid(7, 7, AlwaysDefect)
    grid[3][3] = TitForTat()
    lat = Lattice(grid, turns=20, seed=0)
    assert lat.counts()["Tit For Tat"] == 1
    lat.step()
    assert lat.counts().get("Tit For Tat", 0) == 0


def test_tft_cluster_grows_in_alld_sea():
    grid = make_grid(11, 11, AlwaysDefect)
    plant_cluster(grid, TitForTat, row=4, col=4, height=3, width=3)
    lat = Lattice(grid, turns=20, seed=1)
    start = lat.counts()["Tit For Tat"]
    for _ in range(4):
        lat.step()
    assert lat.counts()["Tit For Tat"] > start


def test_uniform_grid_is_stable():
    grid = make_grid(5, 5, TitForTat)
    lat = Lattice(grid, turns=10, seed=0)
    lat.step()
    assert lat.counts() == {"Tit For Tat": 25}


def test_ascii_and_wrap():
    grid = make_grid(3, 3, AlwaysDefect)
    grid[0][0] = TitForTat()
    lat = Lattice(grid, wrap=True, turns=5)
    assert len(lat.neighbors(0, 0)) == 4
    text = lat.as_ascii()
    assert "T" in text and "D" in text
