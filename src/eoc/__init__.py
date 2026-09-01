"""Evolution of Cooperation — Axelrod-style iterated Prisoner's Dilemma."""

from eoc.actions import Action
from eoc.game import Game, Match, Payoff
from eoc.player import Player
from eoc.tournament import Tournament, TournamentResult
from eoc.ecology import Ecology

__all__ = [
    "Action",
    "Game",
    "Match",
    "Payoff",
    "Player",
    "Tournament",
    "TournamentResult",
    "Ecology",
]

__version__ = "0.1.0"
