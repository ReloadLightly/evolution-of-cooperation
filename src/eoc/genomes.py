"""Evolvable strategy representations.

Lookup70
    Axelrod 1987 / The Complexity of Cooperation ch. 1.
    70 bits: 6 phantom bits (a fictional last-three-rounds used on
    opening moves) + 64-bit lookup table over the 4^3 possible
    three-round histories of (my move, their move).

MemoryOne
    Stochastic memory-1: cooperate with probability p0 on the first
    move and with (p_CC, p_CD, p_DC, p_DD) thereafter.
"""

from __future__ import annotations

import random

from eoc.actions import Action
from eoc.player import Player


def _bit(action: Action) -> int:
    return 0 if action is Action.C else 1


def _action(bit: int) -> Action:
    return Action.C if bit == 0 else Action.D


def pairs_to_index(pairs: list[tuple[Action, Action]]) -> int:
    """Pack three (mine, theirs) pairs into an integer 0..63.

    Oldest pair first. Newest pair occupies the lowest two bits:
    bit 1 = my last move, bit 0 = their last move. So Tit-for-Tat
    is exactly "play bit 0 of the index."
    """
    if len(pairs) != 3:
        raise ValueError("need exactly three pairs")
    idx = 0
    for mine, theirs in pairs:
        idx = (idx << 2) | (_bit(mine) << 1) | _bit(theirs)
    return idx


class Lookup70(Player):
    """Deterministic three-round lookup table. Genome is 70 bits."""

    name = "Lookup70"
    classifier = {**Player.classifier, "memory_depth": 3, "stochastic": False}

    def __init__(self, bits: list[int] | None = None, label: str | None = None) -> None:
        super().__init__()
        if bits is None:
            bits = [0] * 70
        if len(bits) != 70 or any(b not in (0, 1) for b in bits):
            raise ValueError("bits must be a length-70 list of 0/1")
        self.bits = list(bits)
        self.phantom = self._decode_phantom(self.bits[:6])
        self.table = list(self.bits[6:])
        self.name = label or f"Lookup70({self.hex_id()})"

    @staticmethod
    def _decode_phantom(bits6: list[int]) -> list[tuple[Action, Action]]:
        pairs = []
        for i in range(3):
            mine = _action(bits6[2 * i])
            theirs = _action(bits6[2 * i + 1])
            pairs.append((mine, theirs))
        return pairs

    def hex_id(self) -> str:
        value = 0
        for b in self.bits:
            value = (value << 1) | b
        return f"{value:017x}"

    def window(self, opponent: Player) -> list[tuple[Action, Action]]:
        actual = list(zip(self.history, opponent.history))
        n = len(actual)
        if n >= 3:
            return actual[-3:]
        return self.phantom[n:] + actual

    def strategy(self, opponent: Player) -> Action:
        idx = pairs_to_index(self.window(opponent))
        return _action(self.table[idx])

    def clone(self) -> Player:
        return Lookup70(self.bits, label=self.name)

    @classmethod
    def random(cls, rng: random.Random | None = None, label: str | None = None) -> Lookup70:
        rng = rng or random.Random()
        return cls([rng.randrange(2) for _ in range(70)], label=label)

    @classmethod
    def tit_for_tat(cls) -> Lookup70:
        phantom = [0, 0, 0, 0, 0, 0]
        table = [idx & 1 for idx in range(64)]
        return cls(phantom + table, label="Lookup70(TFT)")

    @classmethod
    def always_cooperate(cls) -> Lookup70:
        return cls([0] * 70, label="Lookup70(ALLC)")

    @classmethod
    def always_defect(cls) -> Lookup70:
        return cls([1] * 70, label="Lookup70(ALLD)")

    def cooperation_bias(self) -> float:
        return sum(1 for b in self.table if b == 0) / 64.0

    def tft_agreement(self) -> float:
        return sum(1 for idx, bit in enumerate(self.table) if bit == (idx & 1)) / 64.0


class MemoryOne(Player):
    """Stochastic memory-1 strategy."""

    name = "Memory-1"
    classifier = {**Player.classifier, "memory_depth": 1, "stochastic": True}

    def __init__(
        self,
        p0: float = 1.0,
        p_cc: float = 1.0,
        p_cd: float = 0.0,
        p_dc: float = 1.0,
        p_dd: float = 0.0,
        label: str | None = None,
    ) -> None:
        super().__init__()
        self.p0 = _clip(p0)
        self.p_cc = _clip(p_cc)
        self.p_cd = _clip(p_cd)
        self.p_dc = _clip(p_dc)
        self.p_dd = _clip(p_dd)
        self.vector = (self.p0, self.p_cc, self.p_cd, self.p_dc, self.p_dd)
        self.name = label or f"Memory-1{self.vector}"

    def _draw(self, p: float) -> Action:
        return Action.C if self.rng.random() < p else Action.D

    def strategy(self, opponent: Player) -> Action:
        if not self.history:
            return self._draw(self.p0)
        mine, theirs = self.history[-1], opponent.history[-1]
        if mine is Action.C and theirs is Action.C:
            return self._draw(self.p_cc)
        if mine is Action.C and theirs is Action.D:
            return self._draw(self.p_cd)
        if mine is Action.D and theirs is Action.C:
            return self._draw(self.p_dc)
        return self._draw(self.p_dd)

    def clone(self) -> Player:
        return MemoryOne(*self.vector, label=self.name)

    @classmethod
    def tit_for_tat(cls) -> MemoryOne:
        return cls(1, 1, 0, 1, 0, label="Memory-1(TFT)")

    @classmethod
    def pavlov(cls) -> MemoryOne:
        return cls(1, 1, 0, 0, 1, label="Memory-1(Pavlov)")

    @classmethod
    def always_cooperate(cls) -> MemoryOne:
        return cls(1, 1, 1, 1, 1, label="Memory-1(ALLC)")

    @classmethod
    def always_defect(cls) -> MemoryOne:
        return cls(0, 0, 0, 0, 0, label="Memory-1(ALLD)")

    @classmethod
    def generous_tft(cls, p: float = 0.1) -> MemoryOne:
        return cls(1, 1, p, 1, p, label=f"Memory-1(GTFT {p})")

    @classmethod
    def random_vector(cls, rng: random.Random | None = None) -> MemoryOne:
        rng = rng or random.Random()
        return cls(*(rng.random() for _ in range(5)))


def _clip(p: float) -> float:
    return max(0.0, min(1.0, float(p)))
