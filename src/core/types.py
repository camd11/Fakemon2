"""Type system implementation for Pokemon battles."""

from enum import Enum, auto
from typing import Dict, Tuple

class Type(Enum):
    """Pokemon and move types."""
    NORMAL = auto()
    FIRE = auto()
    WATER = auto()
    ELECTRIC = auto()
    GRASS = auto()
    ICE = auto()
    FIGHTING = auto()
    POISON = auto()
    GROUND = auto()
    FLYING = auto()
    PSYCHIC = auto()
    BUG = auto()
    ROCK = auto()
    GHOST = auto()
    DRAGON = auto()
    DARK = auto()
    STEEL = auto()
    FAIRY = auto()

class TypeEffectiveness:
    """Handles type effectiveness calculations for moves."""
    
    def __init__(self) -> None:
        """Initialize the type effectiveness chart."""
        # Type effectiveness chart will be loaded from JSON
        self._effectiveness_chart: Dict[Type, Dict[Type, float]] = {}
        
    def load_from_json(self, json_data: dict) -> None:
        """Load type effectiveness data from JSON.
        
        Args:
            json_data: Dictionary containing type effectiveness data
        """
        self._effectiveness_chart.clear()
        for attacker_str, defenders in json_data.items():
            attacker = Type[attacker_str.upper()]
            self._effectiveness_chart[attacker] = {}
            for defender_str, multiplier in defenders.items():
                defender = Type[defender_str.upper()]
                self._effectiveness_chart[attacker][defender] = float(multiplier)

    def get_multiplier(self, attack_type: Type, defender_types: Tuple[Type, ...]) -> float:
        """Calculate type effectiveness multiplier for an attack against a Pokemon.
        
        Args:
            attack_type: The type of the attacking move
            defender_types: Tuple of the defending Pokemon's types
            
        Returns:
            float: The type effectiveness multiplier (0.0, 0.25, 0.5, 1.0, 2.0, or 4.0)
        """
        if not defender_types:
            return 1.0
            
        multiplier = 1.0
        for defender_type in defender_types:
            if attack_type in self._effectiveness_chart and defender_type in self._effectiveness_chart[attack_type]:
                multiplier *= self._effectiveness_chart[attack_type][defender_type]
                
        return multiplier
