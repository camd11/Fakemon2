"""Tests for weather effects in battles."""

import pytest
from src.core.battle import Battle, Weather, TurnResult
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory

@pytest.fixture
def type_chart():
    """Create a type chart for testing."""
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0},
        "fire": {"fire": 0.5, "water": 0.5},
        "water": {"water": 0.5, "fire": 2.0}
    })
    return chart

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon for battle."""
    stats = Stats(
        hp=100,
        attack=100,
        defense=100,
        special_attack=100,
        special_defense=100,
        speed=100
    )
    
    moves = [
        Move(
            name="Water Gun",
            type_=Type.WATER,
            category=MoveCategory.SPECIAL,
            power=40,
            accuracy=100,
            pp=35
        )
    ]
    
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.WATER,),
        base_stats=stats,
        level=50,
        moves=moves
    )
    return pokemon

@pytest.fixture
def battle(test_pokemon, type_chart):
    """Create a battle instance for testing."""
    player_pokemon = test_pokemon
    enemy_pokemon = Pokemon(
        name="Enemy Pokemon",
        types=(Type.FIRE,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        moves=[
            Move(
                name="Ember",
                type_=Type.FIRE,
                category=MoveCategory.SPECIAL,
                power=40,
                accuracy=100,
                pp=35
            )
        ]
    )
    return Battle(player_pokemon, enemy_pokemon, type_chart)

def test_rain_boosts_water_moves(battle):
    """Test that rain boosts Water-type moves."""
    battle.weather = Weather.RAIN
    battle.weather_duration = 5
    
    # Do multiple trials to account for random factors
    rain_damages = []
    clear_damages = []
    
    for _ in range(10):
        # Water move in rain
        result = battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
        if not result.critical_hit:  # Only count non-critical hits
            rain_damages.append(result.damage_dealt)
        
        # Reset Pokemon HP
        battle.enemy_pokemon.current_hp = battle.enemy_pokemon.stats.hp
        
        # Water move in clear weather
        battle.weather = Weather.CLEAR
        result = battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
        if not result.critical_hit:  # Only count non-critical hits
            clear_damages.append(result.damage_dealt)
            
        # Reset for next trial
        battle.weather = Weather.RAIN
        battle.enemy_pokemon.current_hp = battle.enemy_pokemon.stats.hp
    
    # Calculate average damages
    avg_rain = sum(rain_damages) / len(rain_damages)
    avg_clear = sum(clear_damages) / len(clear_damages)
    
    # Rain should do ~1.5x damage
    assert avg_rain > avg_clear
    assert abs(avg_rain / avg_clear - 1.5) < 0.1

def test_rain_weakens_fire_moves(battle):
    """Test that rain weakens Fire-type moves."""
    battle.weather = Weather.RAIN
    battle.weather_duration = 5
    
    # Fire move in rain should do 0.5x damage
    result = battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
    reduced_damage = result.damage_dealt
    
    # Reset battle and try without rain
    battle.weather = Weather.CLEAR
    result = battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
    
    assert reduced_damage < result.damage_dealt
    assert abs(reduced_damage / result.damage_dealt - 0.5) < 0.1  # Account for random factor

def test_sun_boosts_fire_moves(battle):
    """Test that sun boosts Fire-type moves."""
    battle.weather = Weather.SUN
    battle.weather_duration = 5
    
    # Do multiple trials to account for random factors
    sun_damages = []
    clear_damages = []
    
    for _ in range(10):
        # Fire move in sun
        result = battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
        if not result.critical_hit:  # Only count non-critical hits
            sun_damages.append(result.damage_dealt)
        
        # Reset Pokemon HP
        battle.player_pokemon.current_hp = battle.player_pokemon.stats.hp
        
        # Fire move in clear weather
        battle.weather = Weather.CLEAR
        result = battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
        if not result.critical_hit:  # Only count non-critical hits
            clear_damages.append(result.damage_dealt)
            
        # Reset for next trial
        battle.weather = Weather.SUN
        battle.player_pokemon.current_hp = battle.player_pokemon.stats.hp
    
    # Calculate average damages
    avg_sun = sum(sun_damages) / len(sun_damages)
    avg_clear = sum(clear_damages) / len(clear_damages)
    
    # Sun should do ~1.5x damage
    assert avg_sun > avg_clear
    assert abs(avg_sun / avg_clear - 1.5) < 0.1

def test_sun_weakens_water_moves(battle):
    """Test that sun weakens Water-type moves."""
    battle.weather = Weather.SUN
    battle.weather_duration = 5
    
    # Water move in sun should do 0.5x damage
    result = battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
    reduced_damage = result.damage_dealt
    
    # Reset battle and try without sun
    battle.weather = Weather.CLEAR
    result = battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
    
    assert reduced_damage < result.damage_dealt
    assert abs(reduced_damage / result.damage_dealt - 0.5) < 0.1  # Account for random factor

def test_sandstorm_damage(battle):
    """Test that sandstorm damages non-Rock/Ground/Steel types."""
    battle.weather = Weather.SANDSTORM
    battle.weather_duration = 5
    
    initial_hp = battle.player_pokemon.current_hp
    battle.apply_weather_effects()
    
    assert battle.player_pokemon.current_hp < initial_hp
    assert battle.player_pokemon.current_hp == initial_hp - (battle.player_pokemon.stats.hp // 16)

def test_hail_damage(battle):
    """Test that hail damages non-Ice types."""
    battle.weather = Weather.HAIL
    battle.weather_duration = 5
    
    initial_hp = battle.player_pokemon.current_hp
    battle.apply_weather_effects()
    
    assert battle.player_pokemon.current_hp < initial_hp
    assert battle.player_pokemon.current_hp == initial_hp - (battle.player_pokemon.stats.hp // 16)

def test_weather_duration(battle):
    """Test that weather effects expire after their duration."""
    battle.weather = Weather.RAIN
    battle.weather_duration = 2
    
    # Weather should last for 2 turns
    assert battle.weather == Weather.RAIN
    battle.end_turn()
    assert battle.weather == Weather.RAIN
    battle.end_turn()
    assert battle.weather == Weather.CLEAR
    assert battle.weather_duration == 0

def test_weather_messages(battle):
    """Test weather effect messages."""
    battle.weather = Weather.SANDSTORM
    battle.weather_duration = 5
    
    result = battle.apply_weather_effects()
    assert "The sandstorm rages!" in result.messages
    assert f"{battle.player_pokemon.name} is buffeted by the sandstorm!" in result.messages
    
    battle.weather_duration = 1
    result = battle.end_turn()
    assert "The sandstorm subsided." in result.messages
