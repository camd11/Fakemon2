"""Tests for battle system functionality."""

import pytest
from src.core.battle import Battle, Weather, TurnResult
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect, StatusEffect
from src.core.types import Type, TypeEffectiveness

@pytest.fixture
def type_chart() -> TypeEffectiveness:
    """Create a type chart for testing."""
    chart = TypeEffectiveness()
    test_data = {
        "fire": {
            "grass": 2.0,
            "water": 0.5,
            "fire": 0.5
        },
        "water": {
            "fire": 2.0,
            "grass": 0.5,
            "water": 0.5
        },
        "grass": {
            "fire": 0.5,
            "water": 2.0,
            "grass": 0.5
        }
    }
    chart.load_from_json(test_data)
    return chart

@pytest.fixture
def basic_stats() -> Stats:
    """Create basic stats for testing."""
    return Stats(
        hp=100,
        attack=100,
        defense=100,
        special_attack=100,
        special_defense=100,
        speed=100
    )

@pytest.fixture
def fire_pokemon(basic_stats) -> Pokemon:
    """Create a fire-type Pokemon for testing."""
    return Pokemon(
        name="Test Fire",
        types=(Type.FIRE,),
        base_stats=basic_stats,
        level=50,
        moves=[
            Move(
                name="Fire Attack",
                type_=Type.FIRE,
                category=MoveCategory.SPECIAL,
                power=40,
                accuracy=100,
                pp=35
            )
        ]
    )

@pytest.fixture
def grass_pokemon(basic_stats) -> Pokemon:
    """Create a grass-type Pokemon for testing."""
    return Pokemon(
        name="Test Grass",
        types=(Type.GRASS,),
        base_stats=basic_stats,
        level=50,
        moves=[
            Move(
                name="Grass Attack",
                type_=Type.GRASS,
                category=MoveCategory.PHYSICAL,
                power=40,
                accuracy=100,
                pp=35
            )
        ]
    )

def test_battle_initialization(fire_pokemon, grass_pokemon, type_chart):
    """Test battle initialization."""
    battle = Battle(fire_pokemon, grass_pokemon, type_chart)
    
    assert battle.player_pokemon == fire_pokemon
    assert battle.enemy_pokemon == grass_pokemon
    assert battle.weather == Weather.CLEAR
    assert battle.turn_count == 0
    assert not battle.is_over

def test_battle_damage_calculation(fire_pokemon, grass_pokemon, type_chart):
    """Test damage calculation in battle."""
    battle = Battle(fire_pokemon, grass_pokemon, type_chart)
    
    # Fire move vs Grass Pokemon (super effective)
    result = battle.execute_turn(fire_pokemon.moves[0], grass_pokemon)
    assert result.damage_dealt > 0
    assert result.effectiveness == 2.0
    
    # Grass move vs Fire Pokemon (not very effective)
    battle = Battle(grass_pokemon, fire_pokemon, type_chart)
    result = battle.execute_turn(grass_pokemon.moves[0], fire_pokemon)
    assert result.damage_dealt > 0
    assert result.effectiveness == 0.5

def test_battle_status_effects(basic_stats, type_chart):
    """Test status effect application in battle."""
    # Create Pokemon with status move
    status_pokemon = Pokemon(
        name="Status User",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=50,
        moves=[
            Move(
                name="Status Move",
                type_=Type.NORMAL,
                category=MoveCategory.STATUS,
                power=0,
                accuracy=100,
                pp=30,
                effects=[Effect(
                    status=StatusEffect.PARALYSIS,
                    status_chance=100  # 100% chance for testing
                )]
            )
        ]
    )
    
    target_pokemon = Pokemon(
        name="Target",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=50
    )
    
    battle = Battle(status_pokemon, target_pokemon, type_chart)
    result = battle.execute_turn(status_pokemon.moves[0], target_pokemon)
    
    assert result.status_applied == StatusEffect.PARALYSIS
    assert target_pokemon.status == StatusEffect.PARALYSIS

def test_battle_stat_changes(basic_stats, type_chart):
    """Test stat modifications in battle."""
    # Create Pokemon with stat-changing move
    stat_pokemon = Pokemon(
        name="Stat Changer",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=50,
        moves=[
            Move(
                name="Stat Move",
                type_=Type.NORMAL,
                category=MoveCategory.STATUS,
                power=0,
                accuracy=100,
                pp=30,
                effects=[Effect(
                    stat_changes={"attack": -1, "defense": -1}
                )]
            )
        ]
    )
    
    target_pokemon = Pokemon(
        name="Target",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=50
    )
    
    battle = Battle(stat_pokemon, target_pokemon, type_chart)
    result = battle.execute_turn(stat_pokemon.moves[0], target_pokemon)
    
    assert len(result.stat_changes) == 2
    assert target_pokemon.stat_stages["attack"] == -1
    assert target_pokemon.stat_stages["defense"] == -1

def test_battle_weather_effects(fire_pokemon, grass_pokemon, type_chart):
    """Test weather effects on battle."""
    battle = Battle(fire_pokemon, grass_pokemon, type_chart)
    
    # Test rain
    battle.weather = Weather.RAIN
    result = battle.execute_turn(fire_pokemon.moves[0], grass_pokemon)
    rain_damage = result.damage_dealt
    
    # Test sun
    battle.weather = Weather.SUN
    result = battle.execute_turn(fire_pokemon.moves[0], grass_pokemon)
    sun_damage = result.damage_dealt
    
    # Fire moves should be weaker in rain and stronger in sun
    assert rain_damage < sun_damage

def test_battle_end_conditions(fire_pokemon, grass_pokemon, type_chart):
    """Test battle end conditions."""
    battle = Battle(fire_pokemon, grass_pokemon, type_chart)
    
    # Faint the enemy Pokemon
    grass_pokemon.current_hp = 1
    battle.execute_turn(fire_pokemon.moves[0], grass_pokemon)
    
    assert battle.is_over
    assert battle.winner == fire_pokemon
    assert grass_pokemon.is_fainted
