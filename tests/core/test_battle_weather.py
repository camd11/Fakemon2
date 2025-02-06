"""Tests for weather effects in battle system."""

import pytest
from src.core.battle import Battle, Weather
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect
from src.core.types import Type, TypeEffectiveness

def test_rain_boost():
    """Test that rain boosts water moves and weakens fire moves."""
    # Create type chart with neutral effectiveness
    chart = TypeEffectiveness()
    chart.load_from_json({
        "water": {"normal": 1.0},
        "fire": {"normal": 1.0},
        "normal": {"normal": 1.0}
    })
    
    # Create Pokemon
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Create water and fire moves
    water_move = Move(
        name="Water Gun",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=25
    )
    
    fire_move = Move(
        name="Ember",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=25
    )
    
    attacker.moves = [water_move, fire_move]
    
    # Test in clear weather first
    battle = Battle(attacker, defender, chart)
    
    # Get base damage values
    water_result = battle.execute_turn(water_move, defender)
    base_water_damage = water_result.damage_dealt
    
    fire_result = battle.execute_turn(fire_move, defender)
    base_fire_damage = fire_result.damage_dealt
    
    # Test in rain
    battle = Battle(attacker, defender, chart, weather=Weather.RAIN)
    
    # Water moves should do 1.5x damage
    water_result = battle.execute_turn(water_move, defender)
    assert water_result.damage_dealt > base_water_damage * 1.35  # Allow for random variation (1.5x nominal)
    
    # Fire moves should do 0.5x damage
    fire_result = battle.execute_turn(fire_move, defender)
    assert fire_result.damage_dealt < base_fire_damage * 0.65  # Allow for random variation (0.5x nominal)

def test_sun_boost():
    """Test that sun boosts fire moves and weakens water moves."""
    # Create type chart with neutral effectiveness
    chart = TypeEffectiveness()
    chart.load_from_json({
        "water": {"normal": 1.0},
        "fire": {"normal": 1.0},
        "normal": {"normal": 1.0}
    })
    
    # Create Pokemon
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Create water and fire moves
    water_move = Move(
        name="Water Gun",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=25
    )
    
    fire_move = Move(
        name="Ember",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=25
    )
    
    attacker.moves = [water_move, fire_move]
    
    # Test in clear weather first
    battle = Battle(attacker, defender, chart)
    
    # Get base damage values
    water_result = battle.execute_turn(water_move, defender)
    base_water_damage = water_result.damage_dealt
    
    fire_result = battle.execute_turn(fire_move, defender)
    base_fire_damage = fire_result.damage_dealt
    
    # Test in sun
    battle = Battle(attacker, defender, chart, weather=Weather.SUN)

    # Fire moves should do 1.5x damage (retry if critical hit)
    fire_result = battle.execute_turn(fire_move, defender)
    attempts = 0
    while fire_result.critical_hit and attempts < 10:
        battle = Battle(attacker, defender, chart, weather=Weather.SUN)
        fire_result = battle.execute_turn(fire_move, defender)
        attempts += 1
    assert not fire_result.critical_hit, "Got critical hit after 10 attempts"
    assert fire_result.damage_dealt > base_fire_damage * 1.35  # Allow for random variation (1.5x nominal)

    # Water moves should do 0.5x damage (retry if critical hit)
    water_result = battle.execute_turn(water_move, defender)
    attempts = 0
    while water_result.critical_hit and attempts < 10:
        battle = Battle(attacker, defender, chart, weather=Weather.SUN)
        water_result = battle.execute_turn(water_move, defender)
        attempts += 1
    assert not water_result.critical_hit, "Got critical hit after 10 attempts"
    assert water_result.damage_dealt < base_water_damage * 0.65  # Allow for random variation (0.5x nominal)

def test_sandstorm_damage():
    """Test that sandstorm damages non-Rock/Ground/Steel types."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0},
        "rock": {"normal": 1.0},
        "ground": {"normal": 1.0},
        "steel": {"normal": 1.0}
    })
    
    # Create Pokemon pairs to test immunity vs damage
    normal_pokemon = Pokemon(
        name="Normal",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    rock_pokemon = Pokemon(
        name="Rock",
        types=(Type.ROCK,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Test in sandstorm
    battle = Battle(normal_pokemon, rock_pokemon, chart, weather=Weather.SANDSTORM)
    
    # Record initial HP
    normal_hp = normal_pokemon.current_hp
    rock_hp = rock_pokemon.current_hp
    
    # End turn to trigger weather damage
    result = battle.end_turn()
    
    # Normal Pokemon should take damage (1/16 of max HP)
    assert normal_pokemon.current_hp == normal_hp - (normal_pokemon.stats.hp // 16)
    assert "buffeted by the sandstorm" in result.messages[0]
    
    # Rock Pokemon should not take damage
    assert rock_pokemon.current_hp == rock_hp

def test_hail_damage():
    """Test that hail damages non-Ice types."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0},
        "ice": {"normal": 1.0}
    })
    
    # Create Pokemon pairs to test immunity vs damage
    normal_pokemon = Pokemon(
        name="Normal",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    ice_pokemon = Pokemon(
        name="Ice",
        types=(Type.ICE,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Test in hail
    battle = Battle(normal_pokemon, ice_pokemon, chart, weather=Weather.HAIL)
    
    # Record initial HP
    normal_hp = normal_pokemon.current_hp
    ice_hp = ice_pokemon.current_hp
    
    # End turn to trigger weather damage
    result = battle.end_turn()
    
    # Normal Pokemon should take damage (1/16 of max HP)
    assert normal_pokemon.current_hp == normal_hp - (normal_pokemon.stats.hp // 16)
    assert "buffeted by the hail" in result.messages[0]
    
    # Ice Pokemon should not take damage
    assert ice_pokemon.current_hp == ice_hp

def test_weather_duration():
    """Test that weather effects expire after their duration."""
    # Create basic Pokemon and type chart for battle
    chart = TypeEffectiveness()
    chart.load_from_json({"normal": {"normal": 1.0}})
    
    pokemon1 = Pokemon(
        name="Pokemon1",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    pokemon2 = Pokemon(
        name="Pokemon2",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Test each weather type
    for weather in [Weather.RAIN, Weather.SUN, Weather.SANDSTORM, Weather.HAIL]:
        # Set weather with 2 turn duration
        battle = Battle(pokemon1, pokemon2, chart, weather=weather, weather_duration=2)
        
        # First turn - weather should be active
        result = battle.end_turn()
        assert battle.weather == weather
        assert any(weather.name.lower() in msg.lower() for msg in result.messages)
        
        # Second turn - weather should be active during the turn but clear at the end
        result = battle.end_turn()
        assert any(weather.name.lower() in msg.lower() for msg in result.messages)
        assert any("subsided" in msg for msg in result.messages)
        assert battle.weather == Weather.CLEAR  # Weather clears at end of its final turn
        
        # Third turn - weather should already be clear
        result = battle.end_turn()
        assert battle.weather == Weather.CLEAR
        # No subsided message since weather already cleared last turn
