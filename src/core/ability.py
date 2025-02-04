"""Ability implementation for Pokemon."""

from enum import Enum, auto
from typing import Optional, Set, Tuple, Dict
from .move import StatusEffect
from .types import Type
from .battle import Weather

class AbilityType(Enum):
    """Types of abilities that can affect battle."""
    STATUS_IMMUNITY = auto()  # Prevents specific status effects
    WEATHER = auto()          # Weather-related effects
    STAT_BOOST = auto()       # Boosts stats in certain conditions
    BATTLE_ENTRY = auto()     # Triggers when entering battle
    HAZARD = auto()          # Sets entry hazards
    TERRAIN = auto()         # Sets terrain effects
    AURA = auto()           # Provides aura effects
    OTHER = auto()           # Other effects

class AuraType(Enum):
    """Types of aura effects."""
    FAIRY = auto()  # Powers up Fairy moves
    DARK = auto()   # Powers up Dark moves
    BREAK = auto()  # Reverses other aura effects

class TerrainType(Enum):
    """Types of terrain that can be set."""
    GRASSY = auto()    # Heals grounded Pokemon, boosts Grass moves
    MISTY = auto()     # Prevents status conditions, weakens Dragon moves
    ELECTRIC = auto()  # Prevents sleep, boosts Electric moves
    PSYCHIC = auto()   # Boosts Psychic moves, prevents priority moves

class HazardType(Enum):
    """Types of entry hazards that can be set."""
    SPIKES = auto()         # Damages grounded Pokemon
    TOXIC_SPIKES = auto()   # Poisons grounded Pokemon
    STEALTH_ROCK = auto()   # Damages Pokemon based on type effectiveness

class Ability:
    """An ability that can affect battle mechanics."""
    
    def __init__(
        self,
        name: str,
        type_: AbilityType,
        description: str,
        immune_statuses: Optional[Set[StatusEffect]] = None,
        weather_effect: Optional[Weather] = None,
        stat_boost: Optional[Tuple[str, float, Optional[Weather]]] = None,
        boost_condition: Optional[str] = None,
        hazard_type: Optional[HazardType] = None,
        hazard_damage: Optional[int] = None,  # Base damage or number of layers
        hazard_status: Optional[StatusEffect] = None,  # For toxic spikes
        terrain_effect: Optional[TerrainType] = None,
        aura_effect: Optional[AuraType] = None
    ) -> None:
        """Initialize an ability.
        
        Args:
            name: Name of the ability
            type_: Type of ability effect
            description: Description of what the ability does
            immune_statuses: Set of status effects this ability prevents
            weather_effect: Weather condition to set
            stat_boost: (stat_name, multiplier, required_weather)
            boost_condition: Condition for stat boost (e.g., "status")
            hazard_type: Type of entry hazard to set
            hazard_damage: Base damage or number of layers for hazard
            hazard_status: Status effect for hazard (e.g., poison)
        """
        self.name = name
        self.type = type_
        self.description = description
        self.immune_statuses = immune_statuses or set()
        self.weather_effect = weather_effect
        self.stat_boost = stat_boost
        self.boost_condition = boost_condition
        self.hazard_type = hazard_type
        self.hazard_damage = hazard_damage
        self.hazard_status = hazard_status
        self.terrain_effect = terrain_effect
        self.aura_effect = aura_effect
        
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

# Define aura abilities
FAIRY_AURA = Ability(
    name="Fairy Aura",
    type_=AbilityType.AURA,
    description="Powers up Fairy-type moves for all Pokemon.",
    aura_effect=AuraType.FAIRY
)

DARK_AURA = Ability(
    name="Dark Aura",
    type_=AbilityType.AURA,
    description="Powers up Dark-type moves for all Pokemon.",
    aura_effect=AuraType.DARK
)

AURA_BREAK = Ability(
    name="Aura Break",
    type_=AbilityType.AURA,
    description="Reverses the effects of other auras.",
    aura_effect=AuraType.BREAK
)

# Define terrain-setting abilities
GRASSY_SURGE = Ability(
    name="Grassy Surge",
    type_=AbilityType.TERRAIN,
    description="Sets Grassy Terrain when entering battle.",
    terrain_effect=TerrainType.GRASSY
)

MISTY_SURGE = Ability(
    name="Misty Surge",
    type_=AbilityType.TERRAIN,
    description="Sets Misty Terrain when entering battle.",
    terrain_effect=TerrainType.MISTY
)

ELECTRIC_SURGE = Ability(
    name="Electric Surge",
    type_=AbilityType.TERRAIN,
    description="Sets Electric Terrain when entering battle.",
    terrain_effect=TerrainType.ELECTRIC
)

PSYCHIC_SURGE = Ability(
    name="Psychic Surge",
    type_=AbilityType.TERRAIN,
    description="Sets Psychic Terrain when entering battle.",
    terrain_effect=TerrainType.PSYCHIC
)

# Define stat-boosting abilities
GUTS = Ability(
    name="Guts",
    type_=AbilityType.STAT_BOOST,
    description="Boosts Attack when status-afflicted.",
    stat_boost=("attack", 1.5, None),
    boost_condition="status"
)

SWIFT_SWIM = Ability(
    name="Swift Swim",
    type_=AbilityType.STAT_BOOST,
    description="Doubles Speed in rain.",
    stat_boost=("speed", 2.0, Weather.RAIN)
)

CHLOROPHYLL = Ability(
    name="Chlorophyll",
    type_=AbilityType.STAT_BOOST,
    description="Doubles Speed in sun.",
    stat_boost=("speed", 2.0, Weather.SUN)
)

SAND_RUSH = Ability(
    name="Sand Rush",
    type_=AbilityType.STAT_BOOST,
    description="Doubles Speed in sandstorm.",
    stat_boost=("speed", 2.0, Weather.SANDSTORM)
)

SLUSH_RUSH = Ability(
    name="Slush Rush",
    type_=AbilityType.STAT_BOOST,
    description="Doubles Speed in hail.",
    stat_boost=("speed", 2.0, Weather.HAIL)
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

# Define status immunity abilities
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

# Define entry hazard abilities
SPIKES_SETTER = Ability(
    name="Spikes Setter",
    type_=AbilityType.HAZARD,
    description="Sets spikes that damage grounded Pokemon.",
    hazard_type=HazardType.SPIKES,
    hazard_damage=3  # Up to 3 layers of spikes
)

TOXIC_SPIKES_SETTER = Ability(
    name="Toxic Spikes Setter",
    type_=AbilityType.HAZARD,
    description="Sets toxic spikes that poison grounded Pokemon.",
    hazard_type=HazardType.TOXIC_SPIKES,
    hazard_damage=2,  # Up to 2 layers (poison vs toxic)
    hazard_status=StatusEffect.POISON
)

STEALTH_ROCK_SETTER = Ability(
    name="Stealth Rock Setter",
    type_=AbilityType.HAZARD,
    description="Sets floating rocks that damage Pokemon based on type effectiveness.",
    hazard_type=HazardType.STEALTH_ROCK,
    hazard_damage=8  # Base damage (1/8 max HP, modified by type effectiveness)
)
