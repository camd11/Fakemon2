"""Ability implementation for Pokemon."""

from enum import Enum, auto
from typing import Optional
from .move import StatusEffect

class AbilityType(Enum):
    """Types of abilities that can affect battle."""
    STATUS_IMMUNITY = auto()  # Complete immunity to specific status effects
    STATUS_RESISTANCE = auto()  # Reduced chance of status effects

class Ability:
    """An ability that provides special effects in battle."""
    
    def __init__(
        self,
        name: str,
        type_: AbilityType,
        status_effects: Optional[tuple[StatusEffect, ...]] = None,
        resistance_multiplier: float = 0.5  # 50% chance reduction for resistances
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
        # Store resistance multiplier directly (e.g., 0.5 means 50% chance)
        self.resistance_multiplier = resistance_multiplier
        
    def prevents_status(self, status: StatusEffect) -> bool:
        """Check if this ability prevents a status effect.
        
        Args:
            status: The status effect to check
            
        Returns:
            bool: True if the ability prevents this status
        """
        return (
            self.type == AbilityType.STATUS_IMMUNITY and
            status in self.status_effects
        )
        
    def modifies_status_chance(self, status: StatusEffect) -> Optional[float]:
        """Get the status chance multiplier for this ability.
        
        Args:
            status: The status effect to check
            
        Returns:
            Optional[float]: Multiplier to apply to status chance, or None if no effect
        """
        if (
            self.type == AbilityType.STATUS_RESISTANCE and
            status in self.status_effects
        ):
            return self.resistance_multiplier
        return None
