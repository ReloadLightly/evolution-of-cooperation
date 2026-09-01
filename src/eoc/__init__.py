"""Evolution of Cooperation — Axelrod-style iterated Prisoner's Dilemma."""

from eoc.actions import Action
from eoc.game import Game, Match, Payoff
from eoc.player import Player
from eoc.tournament import Tournament, TournamentResult
from eoc.ecology import Ecology
from eoc.evolve import GeneticAlgorithm
from eoc.evolve_m1 import MemoryOneGA
from eoc.genomes import Lookup70, MemoryOne
from eoc.lattice import Lattice

__all__ = [
    "Action", "Game", "Match", "Payoff", "Player",
    "Tournament", "TournamentResult", "Ecology",
    "Lookup70", "MemoryOne", "GeneticAlgorithm", "MemoryOneGA", "Lattice",
]
__version__ = "0.1.0"
