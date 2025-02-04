"""Tests for abilities."""

import pytest
from src.core.ability import (
    Ability,
    AbilityType,
    HazardType,
    IMMUNITY,
    LIMBER,
    WATER_VEIL,
    VITAL_SPIRIT,
    MAGMA_ARMOR,
    DRIZZLE,
    DROUGHT,
    SAND_STREAM,
    SNOW_WARNING,
    GUTS,
    SWIFT_SWIM,
    CHLOROPHYLL,
    SAND_RUSH,
    SLUSH_RUSH,
    SPIKES_SETTER,
    TOXIC_SPIKES_SETTER,
    STEALTH_ROCK_SETTER
)
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import StatusEffect
from src.core.battle import Battle, Weather

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon."""
    return Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

def test_status_immunity():
    """Test that status immunity abilities prevent status effects."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=IMMUNITY
    )
    
    # Should not be able to apply any status
    assert not pokemon.set_status(StatusEffect.POISON)
    assert not pokemon.set_status(StatusEffect.BURN)
    assert not pokemon.set_status(StatusEffect.PARALYSIS)
    assert not pokemon.set_status(StatusEffect.SLEEP)
    assert not pokemon.set_status(StatusEffect.FREEZE)
    assert pokemon.status is None

def test_weather_ability():
    """Test that weather abilities set weather conditions."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=DROUGHT
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    assert battle.weather == Weather.SUN
    assert battle.weather_duration is None  # Weather from abilities lasts indefinitely

def test_stat_boost_ability():
    """Test that stat boost abilities modify stats."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=SWIFT_SWIM
    )
    
    # Speed should be doubled in rain
    normal_speed = pokemon.stats.speed
    speed_in_rain = normal_speed * pokemon.get_stat_multiplier("speed", Weather.RAIN)
    assert speed_in_rain == normal_speed * 2.0
    
    # Speed should be normal in other weather
    speed_in_sun = normal_speed * pokemon.get_stat_multiplier("speed", Weather.SUN)
    assert speed_in_sun == normal_speed

def test_spikes_damage():
    """Test that Spikes deal correct damage."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=SPIKES_SETTER
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Set up 3 layers of spikes
    battle.enemy_hazards[HazardType.SPIKES] = 3
    initial_hp = defender.current_hp
    
    # Apply hazards
    messages = battle.apply_hazards(defender, is_player=False)
    
    # Should deal 1/4 max HP damage with 3 layers
    assert defender.current_hp == initial_hp - (defender.stats.hp // 4)
    assert any("hurt by spikes" in msg for msg in messages)

def test_toxic_spikes_effect():
    """Test that Toxic Spikes apply poison correctly."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=TOXIC_SPIKES_SETTER
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test single layer (regular poison)
    battle.enemy_hazards[HazardType.TOXIC_SPIKES] = 1
    messages = battle.apply_hazards(defender, is_player=False)
    assert defender.status == StatusEffect.POISON
    assert defender.status_duration == 5
    assert any("was poisoned" in msg for msg in messages)
    
    # Reset defender
    defender.set_status(None)
    
    # Test double layer (toxic poison)
    battle.enemy_hazards[HazardType.TOXIC_SPIKES] = 2
    messages = battle.apply_hazards(defender, is_player=False)
    assert defender.status == StatusEffect.POISON
    assert defender.status_duration is None  # Toxic is permanent
    assert any("badly poisoned" in msg for msg in messages)

def test_stealth_rock_damage():
    """Test that Stealth Rock deals type-based damage."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=STEALTH_ROCK_SETTER
    )
    
    # Test 4x weakness (Flying/Ice type)
    flying_ice = Pokemon(
        name="Flying/Ice",
        types=(Type.FLYING, Type.ICE),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    battle = Battle(attacker, flying_ice, TypeEffectiveness())
    battle.enemy_hazards[HazardType.STEALTH_ROCK] = True
    
    initial_hp = flying_ice.current_hp
    messages = battle.apply_hazards(flying_ice, is_player=False)
    
    # Should deal 1/2 max HP damage (1/8 * 4)
    assert flying_ice.current_hp == initial_hp - (flying_ice.stats.hp // 2)
    assert any("hurt by stealth rocks" in msg for msg in messages)
    
    # Test immunity (Ground type)
    ground = Pokemon(
        name="Ground",
        types=(Type.GROUND,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    initial_hp = ground.current_hp
    messages = battle.apply_hazards(ground, is_player=False)
    
    # Should deal 1/8 max HP damage (neutral)
    assert ground.current_hp == initial_hp - (ground.stats.hp // 8)

def test_flying_immunity():
    """Test that Flying types are immune to ground hazards."""
    flying = Pokemon(
        name="Flying",
        types=(Type.FLYING,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    battle = Battle(flying, flying, TypeEffectiveness())
    
    # Set up all hazards
    battle.enemy_hazards[HazardType.SPIKES] = 3
    battle.enemy_hazards[HazardType.TOXIC_SPIKES] = 2
    
    # Apply hazards
    initial_hp = flying.current_hp
    messages = battle.apply_hazards(flying, is_player=False)
    
    # Should not take damage or get poisoned
    assert flying.current_hp == initial_hp
    assert flying.status is None
    assert not any("spikes" in msg.lower() for msg in messages)
    assert not any("poison" in msg.lower() for msg in messages)
