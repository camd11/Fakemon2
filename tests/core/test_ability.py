"""Tests for abilities."""

import pytest
from src.core.ability import (
    Ability,
    AbilityType,
    TerrainType,
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
    GRASSY_SURGE,
    MISTY_SURGE,
    ELECTRIC_SURGE,
    PSYCHIC_SURGE
)
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory, StatusEffect
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

def test_terrain_setting():
    """Test that terrain abilities set terrain."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    assert battle.terrain == TerrainType.GRASSY
    assert battle.terrain_duration == 5  # Terrain lasts 5 turns

def test_terrain_move_boost():
    """Test that terrain boosts appropriate moves."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.GRASS,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    grass_move = Move(
        name="Grass Move",
        type_=Type.GRASS,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without terrain
    battle.terrain = None
    attacker.moves = [grass_move]
    result = battle.execute_turn(grass_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Grassy Terrain
    battle.terrain = TerrainType.GRASSY
    result = battle.execute_turn(grass_move, defender)
    
    # Should deal 30% more damage
    assert result.damage_dealt == int(base_damage * 1.3)

def test_terrain_healing():
    """Test that Grassy Terrain heals grounded Pokemon."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    
    # Damage Pokemon
    pokemon.take_damage(50)  # Half HP
    initial_hp = pokemon.current_hp
    
    # End turn should trigger healing
    result = battle.end_turn()
    
    # Should heal 1/16 max HP
    assert pokemon.current_hp == initial_hp + (pokemon.stats.hp // 16)
    assert any("healed by the grassy terrain" in msg for msg in result.messages)

def test_terrain_status_prevention():
    """Test that Misty Terrain prevents status conditions."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=MISTY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    
    # Should not be able to apply status to grounded Pokemon
    assert not pokemon.set_status(StatusEffect.POISON)
    assert not pokemon.set_status(StatusEffect.BURN)
    assert not pokemon.set_status(StatusEffect.PARALYSIS)
    assert not pokemon.set_status(StatusEffect.SLEEP)
    assert not pokemon.set_status(StatusEffect.FREEZE)
    assert pokemon.status is None

def test_terrain_dragon_reduction():
    """Test that Misty Terrain reduces Dragon move power."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.DRAGON,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=MISTY_SURGE
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    dragon_move = Move(
        name="Dragon Move",
        type_=Type.DRAGON,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without terrain
    battle.terrain = None
    attacker.moves = [dragon_move]
    result = battle.execute_turn(dragon_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Misty Terrain
    battle.terrain = TerrainType.MISTY
    result = battle.execute_turn(dragon_move, defender)
    
    # Should deal 50% less damage
    assert result.damage_dealt == int(base_damage * 0.5)

def test_terrain_duration():
    """Test that terrain fades after 5 turns."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    
    # Terrain should last 5 turns
    for i in range(4):
        result = battle.end_turn()
        assert battle.terrain == TerrainType.GRASSY
        assert battle.terrain_duration == 4 - i
        
    # On 5th turn, terrain should fade
    result = battle.end_turn()
    assert battle.terrain is None
    assert any("terrain faded" in msg for msg in result.messages)
