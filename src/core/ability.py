"""Ability implementation for Pokemon."""

from enum import Enum, auto
from typing import Optional, Set, Tuple, Dict
from .move import StatusEffect
from .types import Type
from .weather import Weather
from .stats import Stats

class AbilityType(Enum):
    """Types of abilities that can affect battle."""
    STATUS_IMMUNITY = auto()  # Prevents specific status effects
    WEATHER = auto()          # Weather-related effects
    STAT_BOOST = auto()       # Boosts stats in certain conditions
    BATTLE_ENTRY = auto()     # Triggers when entering battle
    HAZARD = auto()          # Sets entry hazards
    TERRAIN = auto()         # Sets terrain effects
    AURA = auto()           # Provides aura effects
    FORM_CHANGE = auto()    # Changes Pokemon form
    ILLUSION = auto()       # Changes Pokemon appearance
    DISGUISE = auto()       # Protects from damage
    PROTEAN = auto()        # Changes type based on moves
    COLOR_CHANGE = auto()   # Changes type based on damage
    TRACE = auto()          # Copies opponent's ability
    MOLD_BREAKER = auto()   # Ignores other abilities
    SIMPLE = auto()         # Doubles stat stage changes
    UNAWARE = auto()        # Ignores opponent's stat changes
    OTHER = auto()           # Other effects

class UnawareType(Enum):
    """Types of unaware effects."""
    IGNORE = auto()      # Ignores opponent's stat changes

class SimpleType(Enum):
    """Types of simple effects."""
    DOUBLE = auto()      # Doubles stat stage changes

class MoldBreakerType(Enum):
    """Types of mold breaker effects."""
    IGNORE = auto()      # Ignores other abilities

class TraceType(Enum):
    """Types of trace effects."""
    COPY = auto()      # Copies opponent's ability

class ColorChangeType(Enum):
    """Types of color change effects."""
    DAMAGE = auto()    # Changes type to match damaging move
    WEATHER = auto()   # Changes type based on weather

class ProteanType(Enum):
    """Types of protean effects."""
    MOVE = auto()      # Changes type to match move
    STAB = auto()      # Boosts STAB moves

class DisguiseType(Enum):
    """Types of disguise effects."""
    ALL = auto()      # Protects from all damage
    PHYSICAL = auto() # Protects from physical moves
    WEAKNESS = auto() # Only takes super effective damage

class IllusionType(Enum):
    """Types of illusion effects."""
    DISGUISE = auto()    # Appears as another Pokemon
    TRANSFORM = auto()   # Copies opponent's Pokemon
    MIMIC = auto()       # Changes type based on terrain

class FormChangeType(Enum):
    """Types of form changes."""
    STANCE = auto()      # Changes based on move used
    BATTLE_BOND = auto() # Changes after defeating Pokemon
    CONSTRUCT = auto()   # Changes at low HP

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
        aura_effect: Optional[AuraType] = None,
        form_change: Optional[FormChangeType] = None,
        form_stats: Optional[Dict[str, Stats]] = None,  # Stats for each form
        form_types: Optional[Dict[str, Tuple[Type, ...]]] = None,  # Types for each form
        illusion_effect: Optional[IllusionType] = None,
        disguise_type: Optional[DisguiseType] = None,  # Type of disguise protection
        disguise_hp: Optional[int] = None,  # Extra HP for disguise
        protean_type: Optional[ProteanType] = None,  # Type of protean effect
        color_change_type: Optional[ColorChangeType] = None,  # Type of color change effect
        trace_type: Optional[TraceType] = None,  # Type of trace effect
        mold_breaker_type: Optional[MoldBreakerType] = None,  # Type of mold breaker effect
        simple_type: Optional[SimpleType] = None,  # Type of simple effect
        unaware_type: Optional[UnawareType] = None  # Type of unaware effect
    ) -> None:
        """Initialize an ability."""
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
        self.form_change = form_change
        self.form_stats = form_stats or {}
        self.form_types = form_types or {}
        self.illusion_effect = illusion_effect
        self.disguise_type = disguise_type
        self.disguise_hp = disguise_hp
        self.protean_type = protean_type
        self.color_change_type = color_change_type
        self.trace_type = trace_type
        self.mold_breaker_type = mold_breaker_type
        self.simple_type = simple_type
        self.unaware_type = unaware_type
        
    def prevents_status(self, status: StatusEffect) -> bool:
        """Check if this ability prevents a specific status effect."""
        return status in self.immune_statuses

# Define unaware abilities
UNAWARE = Ability(
    name="Unaware",
    type_=AbilityType.UNAWARE,
    description="Ignores opponent's stat changes when calculating damage.",
    unaware_type=UnawareType.IGNORE
)

# Define simple abilities
SIMPLE = Ability(
    name="Simple",
    type_=AbilityType.SIMPLE,
    description="Doubles all stat stage changes.",
    simple_type=SimpleType.DOUBLE
)

# Define mold breaker abilities
MOLD_BREAKER = Ability(
    name="Mold Breaker",
    type_=AbilityType.MOLD_BREAKER,
    description="Moves can be used regardless of abilities.",
    mold_breaker_type=MoldBreakerType.IGNORE
)

TERAVOLT = Ability(
    name="Teravolt",
    type_=AbilityType.MOLD_BREAKER,
    description="Moves can be used regardless of abilities.",
    mold_breaker_type=MoldBreakerType.IGNORE
)

TURBOBLAZE = Ability(
    name="Turboblaze",
    type_=AbilityType.MOLD_BREAKER,
    description="Moves can be used regardless of abilities.",
    mold_breaker_type=MoldBreakerType.IGNORE
)

# Define trace abilities
TRACE = Ability(
    name="Trace",
    type_=AbilityType.TRACE,
    description="Copies the opponent's ability when entering battle.",
    trace_type=TraceType.COPY
)

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

# Define color change abilities
COLOR_CHANGE = Ability(
    name="Color Change",
    type_=AbilityType.COLOR_CHANGE,
    description="Changes type to match the type of move that hit it.",
    color_change_type=ColorChangeType.DAMAGE
)

FORECAST = Ability(
    name="Forecast",
    type_=AbilityType.COLOR_CHANGE,
    description="Changes type based on weather.",
    color_change_type=ColorChangeType.WEATHER
)

# Define protean abilities
PROTEAN = Ability(
    name="Protean",
    type_=AbilityType.PROTEAN,
    description="Changes type to match move being used.",
    protean_type=ProteanType.MOVE
)

LIBERO = Ability(
    name="Libero",
    type_=AbilityType.PROTEAN,
    description="Changes type to match move being used.",
    protean_type=ProteanType.MOVE
)

ADAPTABILITY = Ability(
    name="Adaptability",
    type_=AbilityType.PROTEAN,
    description="Powers up moves that match the Pokemon's type.",
    protean_type=ProteanType.STAB
)

# Define disguise abilities
DISGUISE = Ability(
    name="Disguise",
    type_=AbilityType.DISGUISE,
    description="Takes no damage from first hit.",
    disguise_type=DisguiseType.ALL,
    disguise_hp=1
)

ICE_FACE = Ability(
    name="Ice Face",
    type_=AbilityType.DISGUISE,
    description="Takes no damage from first physical hit.",
    disguise_type=DisguiseType.PHYSICAL,
    disguise_hp=1
)

WONDER_GUARD = Ability(
    name="Wonder Guard",
    type_=AbilityType.DISGUISE,
    description="Only takes damage from super effective moves.",
    disguise_type=DisguiseType.WEAKNESS
)

# Define illusion abilities
ILLUSION = Ability(
    name="Illusion",
    type_=AbilityType.ILLUSION,
    description="Makes Pokemon appear as another Pokemon.",
    illusion_effect=IllusionType.DISGUISE
)

IMPOSTER = Ability(
    name="Imposter",
    type_=AbilityType.ILLUSION,
    description="Transforms into the opponent's Pokemon.",
    illusion_effect=IllusionType.TRANSFORM
)

MIMICRY = Ability(
    name="Mimicry",
    type_=AbilityType.ILLUSION,
    description="Changes type based on terrain.",
    illusion_effect=IllusionType.MIMIC
)

# Define form change abilities
STANCE_CHANGE = Ability(
    name="Stance Change",
    type_=AbilityType.FORM_CHANGE,
    description="Changes form based on move used.",
    form_change=FormChangeType.STANCE,
    form_stats={
        "blade": Stats(60, 140, 50, 140, 50, 60),  # Offensive form
        "shield": Stats(60, 50, 140, 50, 140, 60),  # Defensive form
        "normal": Stats(60, 50, 140, 50, 140, 60)  # Default form
    },
    form_types={
        "blade": (Type.STEEL, Type.GHOST),
        "shield": (Type.STEEL, Type.GHOST)
    }
)

BATTLE_BOND = Ability(
    name="Battle Bond",
    type_=AbilityType.FORM_CHANGE,
    description="Changes form after defeating a Pokemon.",
    form_change=FormChangeType.BATTLE_BOND,
    form_stats={
        "normal": Stats(72, 95, 67, 103, 71, 122),  # Base form
        "bond": Stats(72, 95, 67, 140, 71, 122)     # Bond form with higher special attack
    },
    form_types={
        "normal": (Type.WATER, Type.DARK),
        "bond": (Type.WATER, Type.DARK)
    }
)

POWER_CONSTRUCT = Ability(
    name="Power Construct",
    type_=AbilityType.FORM_CHANGE,
    description="Changes form at low HP.",
    form_change=FormChangeType.CONSTRUCT,
    form_stats={
        "cell": Stats(54, 100, 71, 61, 85, 109),    # Cell form
        "complete": Stats(200, 100, 121, 61, 85, 85) # Complete form with higher HP
    },
    form_types={
        "cell": (Type.DRAGON, Type.GROUND),
        "complete": (Type.DRAGON, Type.GROUND)
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
