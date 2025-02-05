"""Move implementation for Pokemon."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, List
from .types import Type
from .weather import Weather

class MoveCategory(Enum):
    """Categories of moves."""
    PHYSICAL = auto()  # Uses Attack and Defense stats
    SPECIAL = auto()   # Uses Special Attack and Special Defense stats
    STATUS = auto()    # No direct damage, applies effects

class StatusEffect(Enum):
    """Status effects that can be applied."""
    POISON = auto()    # Deals damage over time
    BURN = auto()      # Deals damage and reduces Attack
    PARALYSIS = auto() # May prevent moves and reduces Speed
    SLEEP = auto()     # Prevents moves completely
    FREEZE = auto()    # Prevents moves completely

@dataclass
class Effect:
    """Effect that can be applied by a move."""
    status: Optional[StatusEffect] = None
    status_chance: Optional[float] = None
    status_duration: Optional[int] = None
    stat_changes: Optional[Dict[str, int]] = None
    stat_chance: Optional[float] = None

class Move:
    """A move that can be used in battle."""
    
    def __init__(
        self,
        name: str,
        type_: Type,
        category: MoveCategory,
        power: int,
        accuracy: int,
        pp: int,
        status_effect: Optional[StatusEffect] = None,
        status_chance: Optional[float] = None,
        status_duration: Optional[int] = None,
        stat_changes: Optional[Dict[str, int]] = None,
        stat_chance: Optional[float] = None,
        weather_multipliers: Optional[Dict[Weather, float]] = None,
        effects: Optional[List[Effect]] = None
    ) -> None:
        """Initialize a move.
        
        Args:
            name: Name of the move
            type_: Type of the move
            category: Physical, Special, or Status
            power: Base power (0 for status moves)
            accuracy: Base accuracy (0-100)
            pp: Power points (number of times move can be used)
            status_effect: Status effect to apply
            status_chance: Chance to apply status (0-1)
            status_duration: How many turns status lasts
            stat_changes: Dict of stat name to stage change
            stat_chance: Chance to apply stat changes (0-1)
            weather_multipliers: Dict of weather to damage multiplier
        """
        self.name = name
        self.type = type_
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.max_pp = pp
        self.current_pp = pp
        self.status_effect = status_effect
        self.status_chance = status_chance
        self.status_duration = status_duration
        self.stat_changes = stat_changes or {}
        self.stat_chance = stat_chance
        self.effects = effects or []

        # Set default weather multipliers based on move type
        if weather_multipliers is None:
            weather_multipliers = {}
            if type_ == Type.FIRE:
                weather_multipliers[Weather.SUN] = 1.5
                weather_multipliers[Weather.RAIN] = 0.5
            elif type_ == Type.WATER:
                weather_multipliers[Weather.RAIN] = 1.5
                weather_multipliers[Weather.SUN] = 0.5
        self.weather_multipliers = weather_multipliers

    def use(self) -> bool:
        """Use this move, consuming PP.
        
        Returns:
            bool: True if move was used successfully, False if no PP remaining
        """
        if self.current_pp <= 0:
            return False
        self.current_pp -= 1
        return True

    def restore_pp(self, amount: int = -1) -> int:
        """Restore PP to this move.
        
        Args:
            amount: Amount of PP to restore, or -1 to restore all PP
            
        Returns:
            int: Amount of PP actually restored
        """
        old_pp = self.current_pp
        # If amount is -1, restore all PP
        if amount == -1:
            amount = self.max_pp - self.current_pp
        self.current_pp = min(self.max_pp, self.current_pp + amount)
        return self.current_pp - old_pp

    @property
    def is_damaging(self) -> bool:
        """Whether this move deals direct damage."""
        return self.category != MoveCategory.STATUS and self.power > 0

    def get_weather_multiplier(self, weather: Weather) -> float:
        """Get damage multiplier for current weather.
        
        Args:
            weather: Current weather condition
            
        Returns:
            float: Damage multiplier (1.0 if no effect)
        """
        return self.weather_multipliers.get(weather, 1.0)
