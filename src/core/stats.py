"""Stats implementation for Pokemon."""

from dataclasses import dataclass

@dataclass
class Stats:
    """Base stats for a Pokemon."""
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
