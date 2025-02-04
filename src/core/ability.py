"""Ability implementation for Pokemon."""

from enum import Enum, auto
from typing import Optional, Set
from .move import StatusEffect

from .battle import Weather

class AbilityType(Enum):
    """Types of abilities that can affect battle."""
    STATUS_IMMUNITY = auto()  # Prevents specific status effects
    WEATHER = auto()          # Weather-related effects
    STAT_BOOST = auto()       # Boosts stats in certain conditions
    BATTLE_ENTRY = auto()     # Triggers when entering battle
    OTHER = auto()            # Other effects

class Ability:
    """An ability that can affect battle mechanics."""
    
    def __init__(
        self,
        name: str,
        type_: AbilityType,
        description: str,
        immune_statuses: Optional[Set[StatusEffect]] = None,
        weather_effect: Optional[Weather] = None
    ) -> None:
        """Initialize an ability.
        
        Args:
            name: Name of the ability
            type_: Type of ability effect
            description: Description of what the ability does
            immune_statuses: Set of status effects this ability prevents
        """
        self.name = name
        self.type = type_
        self.description = description
        self.immune_statuses = immune_statuses or set()
        self.weather_effect = weather_effect
        
    def prevents_status(self, status: StatusEffect) -> bool:
        """Check if this ability prevents a specific status effect.
        
        Args:
            status: The status effect to check
            
        Returns:
            bool: True if the ability prevents this status, False otherwise
        """
        return status in self.immune_statuses

# Define common status-related abilities
IMMUNITY = Ability(
    name="Immunity",
    type_=AbilityType.STATUS_IMMUNITY,
    description="Prevents all status conditions.",
    immune_statuses={
        StatusEffect.POISON,
        StatusEffect.BURN,
        StatusEffect.PARALYSIS,
        StatusEffect.SLEEP,
        StatusEffect.FREEZE
    }
)

# Define weather-related abilities
DRIZZLE = Ability(
    name="Drizzle",
    type_=AbilityType.WEATHER,
    description="Summons rain when entering battle.",
    weather_effect=Weather.RAIN
)

DROUGHT = Ability(
    name="Drought",
    type_=AbilityType.WEATHER,
    description="Summons harsh sunlight when entering battle.",
    weather_effect=Weather.SUN
)

SAND_STREAM = Ability(
    name="Sand Stream",
    type_=AbilityType.WEATHER,
    description="Summons a sandstorm when entering battle.",
    weather_effect=Weather.SANDSTORM
)

SNOW_WARNING = Ability(
    name="Snow Warning",
    type_=AbilityType.WEATHER,
    description="Summons hail when entering battle.",
    weather_effect=Weather.HAIL
)

LIMBER = Ability(
    name="Limber",
    type_=AbilityType.STATUS_IMMUNITY,
    description="Prevents paralysis.",
    immune_statuses={StatusEffect.PARALYSIS}
)

WATER_VEIL = Ability(
    name="Water Veil",
    type_=AbilityType.STATUS_IMMUNITY,
    description="Prevents burns.",
    immune_statuses={StatusEffect.BURN}
)

VITAL_SPIRIT = Ability(
    name="Vital Spirit",
    type_=AbilityType.STATUS_IMMUNITY,
    description="Prevents sleep.",
    immune_statuses={StatusEffect.SLEEP}
)

MAGMA_ARMOR = Ability(
    name="Magma Armor",
    type_=AbilityType.STATUS_IMMUNITY,
    description="Prevents freezing.",
    immune_statuses={StatusEffect.FREEZE}
)
