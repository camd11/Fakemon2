"""Tests for weather effects in battle system."""

import pytest
from src.core.battle import Battle, Weather
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect, StatusEffect
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
    
    # Get base damage values (non-critical hits)
    base_water_damage = None
    for _ in range(10):
        water_result = battle.execute_turn(water_move, defender)
        if not water_result.critical_hit:
            base_water_damage = water_result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    assert base_water_damage is not None, "Failed to get non-critical water damage"
    
    base_fire_damage = None
    for _ in range(10):
        fire_result = battle.execute_turn(fire_move, defender)
        if not fire_result.critical_hit:
            base_fire_damage = fire_result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    assert base_fire_damage is not None, "Failed to get non-critical fire damage"
    
    # Test in rain
    battle = Battle(attacker, defender, chart, weather=Weather.RAIN)
    
    # Test water boost (1.5x damage)
    for _ in range(10):
        water_result = battle.execute_turn(water_move, defender)
        if not water_result.critical_hit:
            assert water_result.damage_dealt > base_water_damage * 1.35  # Allow for random variation (1.5x nominal)
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    
    # Test fire reduction (0.5x damage)
    for _ in range(10):
        fire_result = battle.execute_turn(fire_move, defender)
        if not fire_result.critical_hit:
            assert fire_result.damage_dealt < base_fire_damage * 0.65  # Allow for random variation (0.5x nominal)
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt

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
    
    # Get base damage values (non-critical hits)
    base_water_damage = None
    for _ in range(10):
        water_result = battle.execute_turn(water_move, defender)
        if not water_result.critical_hit:
            base_water_damage = water_result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    assert base_water_damage is not None, "Failed to get non-critical water damage"
    
    base_fire_damage = None
    for _ in range(10):
        fire_result = battle.execute_turn(fire_move, defender)
        if not fire_result.critical_hit:
            base_fire_damage = fire_result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    assert base_fire_damage is not None, "Failed to get non-critical fire damage"
    
    # Test in sun
    battle = Battle(attacker, defender, chart, weather=Weather.SUN)
    
    # Test fire boost (1.5x damage)
    for _ in range(10):
        fire_result = battle.execute_turn(fire_move, defender)
        if not fire_result.critical_hit:
            assert fire_result.damage_dealt > base_fire_damage * 1.35  # Allow for random variation (1.5x nominal)
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    
    # Test water reduction (0.5x damage)
    for _ in range(10):
        water_result = battle.execute_turn(water_move, defender)
        if not water_result.critical_hit:
            assert water_result.damage_dealt < base_water_damage * 0.65  # Allow for random variation (0.5x nominal)
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt

def test_sandstorm_immunities():
    """Test that Rock/Ground/Steel types are immune to sandstorm damage."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0},
        "rock": {"normal": 1.0},
        "ground": {"normal": 1.0},
        "steel": {"normal": 1.0}
    })
    
    # Create Pokemon for each immune type
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
    
    ground_pokemon = Pokemon(
        name="Ground",
        types=(Type.GROUND,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    steel_pokemon = Pokemon(
        name="Steel",
        types=(Type.STEEL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Test each type in sandstorm
    for immune_pokemon in [rock_pokemon, ground_pokemon, steel_pokemon]:
        battle = Battle(normal_pokemon, immune_pokemon, chart, weather=Weather.SANDSTORM)
        
        # Record initial HP
        normal_hp = normal_pokemon.current_hp
        immune_hp = immune_pokemon.current_hp
        
        # End turn to trigger weather damage
        result = battle.end_turn()
        
        # Normal Pokemon should take damage (1/16 of max HP)
        assert normal_pokemon.current_hp == normal_hp - (normal_pokemon.stats.hp // 16)
        assert "buffeted by the sandstorm" in result.messages[0]
        
        # Immune Pokemon should not take damage
        assert immune_pokemon.current_hp == immune_hp

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

def test_weather_message_order():
    """Test that weather messages appear in correct order (damage before status)."""
    chart = TypeEffectiveness()
    chart.load_from_json({"normal": {"normal": 1.0}})
    
    # Create Pokemon with poison status
    pokemon1 = Pokemon(
        name="Pokemon1",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    pokemon1.set_status(StatusEffect.POISON)
    
    pokemon2 = Pokemon(
        name="Pokemon2",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Test in sandstorm
    battle = Battle(pokemon1, pokemon2, chart, weather=Weather.SANDSTORM)
    
    # End turn to trigger weather and status effects
    result = battle.end_turn()
    
    # Weather damage message should come before poison message
    damage_msg_index = next(i for i, msg in enumerate(result.messages) if "buffeted by the sandstorm" in msg)
    poison_msg_index = next(i for i, msg in enumerate(result.messages) if "hurt by poison" in msg)
    assert damage_msg_index < poison_msg_index

def test_weather_damage_order():
    """Test that weather effects are applied before critical hits."""
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
    
    # Create water move with lots of PP for multiple attempts
    water_move = Move(
        name="Water Gun",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=1000  # Lots of PP for multiple trials
    )
    attacker.moves = [water_move]
    
    # Test in sun to reduce water damage
    battle = Battle(attacker, defender, chart, weather=Weather.SUN)
    
    # Get non-critical hit damage first
    non_crit_damage = None
    for _ in range(10):
        result = battle.execute_turn(water_move, defender)
        if not result.critical_hit:
            non_crit_damage = result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP
    assert non_crit_damage is not None, "Failed to get non-critical hit"
    
    # Then get critical hit damage (1/24 chance, try many more times to be reliable)
    crit_damage = None
    for _ in range(1000):  # Much more attempts to ensure we get a critical hit
        result = battle.execute_turn(water_move, defender)
        if result.critical_hit:
            crit_damage = result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP
    assert crit_damage is not None, "Failed to get critical hit in 1000 attempts"
    
    # Critical hits should do ~2x damage regardless of weather
    # Allow for random damage factor (0.85-1.00) on both base and crit damage
    # Max ratio: 2.0 * (1.00/0.85) ≈ 2.35
    # Min ratio: 2.0 * (0.85/1.00) ≈ 1.70
    assert crit_damage is not None and non_crit_damage is not None
    actual_ratio = crit_damage / non_crit_damage
    assert 1.70 <= actual_ratio <= 2.35, f"Expected ~2x damage (with random factor), got {actual_ratio}x"

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
