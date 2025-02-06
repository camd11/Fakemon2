"""Ability implementation for Pokemon."""

from enum import Enum, auto
from typing import Optional, Union
from .move import StatusEffect
from .types import Weather

class AbilityType(Enum):
    """Types of abilities that can affect battle."""
    STATUS_IMMUNITY = auto()  # Complete immunity to specific status effects
    STATUS_RESISTANCE = auto()  # Reduced chance of status effects
    WEATHER_IMMUNITY = auto()  # Complete immunity to weather damage
    WEATHER_RESISTANCE = auto()  # Reduced weather damage

class Ability:
    """An ability that provides special effects in battle."""
    
    def __init__(
        self,
        name: str,
        type_: AbilityType,
        status_effects: Optional[tuple[StatusEffect, ...]] = None,
        weather_types: Optional[tuple[Weather, ...]] = None,
        resistance_multiplier: float = 0.5  # 50% reduction for resistances
    ) -> None:
        """Initialize an ability.
        
        Args:
            name: Name of the ability
            type_: Type of ability effect
            status_effects: Status effects this ability affects (for immunity/resistance)
            resistance_multiplier: For STATUS_RESISTANCE, multiplier to apply to status chance
        """
        self.name = name
        self.type = type_
        self.status_effects = status_effects or tuple()
        self.weather_types = weather_types or tuple()
        # Store resistance multiplier directly (e.g., 0.5 means 50% reduction)
        self.resistance_multiplier = resistance_multiplier
        
    def prevents_status(self, status: StatusEffect) -> bool:
        """Check if this ability prevents a status effect.
        
        Args:
            status: The status effect to check
            
        Returns:
            bool: True if the ability prevents this status
        """
        # Check for immunity regardless of primary ability type
        return status in self.status_effects and self.type == AbilityType.STATUS_IMMUNITY
        
    def modifies_status_chance(self, status: StatusEffect) -> Optional[float]:
        """Get the status chance multiplier for this ability.
        
        Args:
            status: The status effect to check
            
        Returns:
            Optional[float]: Multiplier to apply to status chance, or None if no effect
        """
        # For STATUS_RESISTANCE abilities, apply resistance to all listed effects
        if self.type == AbilityType.STATUS_RESISTANCE and status in self.status_effects:
            return self.resistance_multiplier
            
        # For STATUS_IMMUNITY abilities:
        # - No resistance if the status is immune (in status_effects)
        # - Apply resistance to all other statuses
        if self.type == AbilityType.STATUS_IMMUNITY and status not in self.status_effects:
            return self.resistance_multiplier
            
        return None
        
    def prevents_weather_damage(self, weather: Weather) -> bool:
        """Check if this ability prevents damage from a weather condition.
        
        Args:
            weather: The weather condition to check
            
        Returns:
            bool: True if the ability prevents weather damage
        """
        return weather in self.weather_types and self.type == AbilityType.WEATHER_IMMUNITY
        
    def modifies_weather_damage(self, weather: Weather) -> Optional[float]:
        """Get the weather damage multiplier for this ability.
        
        Args:
            weather: The weather condition to check
            
        Returns:
            Optional[float]: Multiplier to apply to weather damage, or None if no effect
        """
        if self.type == AbilityType.WEATHER_RESISTANCE and weather in self.weather_types:
            return self.resistance_multiplier
        return None
