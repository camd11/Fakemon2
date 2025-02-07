"""Tests for weather effects in battle system.

Note on Test Ranges:
These tests use deliberately lenient ranges to prevent flaky failures while still
catching significant implementation errors. For example:

- Weather damage ratios (1.25-3.0):
  * Expected ratio is 2.0x for critical hits
  * Random factor is 0.85-1.00
  * Wide range catches only egregious errors
  * Would catch if weather/crit interaction was wrong

- Weather boost/reduction:
  * Boosted moves: >1.1x base damage
  * Reduced moves: <0.9x base damage
  * Very lenient bounds to avoid flaky tests
  * Would catch if weather had no effect
  * Would catch if effect was reversed

- Critical hit attempts (200):
  * High attempt count ensures we get a critical hit
  * 1/24 chance should hit within 200 tries
  * Prevents random test failures
  * Still validates core mechanics

- Non-critical attempts (20):
  * Fewer trials since success rate is high
  * Only need one non-critical hit
  * Allows for normal random variation
"""

import pytest
from src.core.battle import Battle, Weather
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect, StatusEffect
from src.core.types import Type, TypeEffectiveness
from src.core.ability import Ability, AbilityType

@pytest.mark.parametrize("weather,boosted_type,reduced_type", [
    (Weather.RAIN, Type.WATER, Type.FIRE),
    (Weather.SUN, Type.FIRE, Type.WATER)
])
def test_weather_move_effects(weather, boosted_type, reduced_type):
    """Test that weather boosts and reduces appropriate move types."""
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
    
    # Create moves
    boosted_move = Move(
        name=f"{boosted_type.name} Move",
        type_=boosted_type,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=250  # Enough PP for all attempts
    )
    
    reduced_move = Move(
        name=f"{reduced_type.name} Move",
        type_=reduced_type,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=250  # Enough PP for all attempts
    )
    
    attacker.moves = [boosted_move, reduced_move]
    
    # Test in clear weather first
    battle = Battle(attacker, defender, chart)
    
    # Get base damage values (non-critical hits)
    base_boosted_damage = None
    # Try to get non-critical hit (1/24 chance to crit, so try up to 20 times)
    for _ in range(20):
        result = battle.execute_turn(boosted_move, defender)
        if not result.critical_hit:
            base_boosted_damage = result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    assert base_boosted_damage is not None, f"Failed to get non-critical {boosted_type.name} damage"
    
    base_reduced_damage = None
    # Try to get non-critical hit (1/24 chance to crit, so try up to 20 times)
    for _ in range(20):
        result = battle.execute_turn(reduced_move, defender)
        if not result.critical_hit:
            base_reduced_damage = result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    assert base_reduced_damage is not None, f"Failed to get non-critical {reduced_type.name} damage"
    
    # Test in weather
    battle = Battle(attacker, defender, chart, weather=weather)
    
    # Test boosted move (1.5x damage)
    # Try to get non-critical hit (1/24 chance to crit, so try up to 20 times)
    for _ in range(20):
        result = battle.execute_turn(boosted_move, defender)
        if not result.critical_hit:
            # Allow for much wider random variation
            assert result.damage_dealt > base_boosted_damage * 1.1  # Very lenient lower bound
            break
        defender.current_hp = defender.stats.hp  # Reset HP for next attempt
    
    # Test reduced move (0.5x damage)
    # Try to get non-critical hit (1/24 chance to crit, so try up to 20 times)
    for _ in range(20):
        result = battle.execute_turn(reduced_move, defender)
        if not result.critical_hit:
            # Allow for much wider random variation
            assert result.damage_dealt < base_reduced_damage * 0.9  # Very lenient upper bound
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

def test_weather_immunity_ability():
    """Test that weather immunity abilities prevent weather damage."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    # Create Pokemon with weather immunity ability
    immune_pokemon = Pokemon(
        name="Immune",
        types=(Type.NORMAL,),  # Not naturally immune
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    # Add ability that grants immunity to both sandstorm and hail
    immune_pokemon.ability = Ability(
        name="Weather Shield",
        type_=AbilityType.WEATHER_IMMUNITY,
        weather_types=(Weather.SANDSTORM, Weather.HAIL)
    )
    
    # Create regular Pokemon for comparison
    normal_pokemon = Pokemon(
        name="Normal",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Test in both weather types
    for weather in (Weather.SANDSTORM, Weather.HAIL):
        battle = Battle(immune_pokemon, normal_pokemon, chart, weather=weather)
        
        # Record initial HP
        immune_hp = immune_pokemon.current_hp
        normal_hp = normal_pokemon.current_hp
        
        # End turn to trigger weather damage
        result = battle.end_turn()
        
        # Immune Pokemon should take no damage despite not having type immunity
        assert immune_pokemon.current_hp == immune_hp, f"Pokemon with immunity ability took {weather.name} damage"
        
        # Normal Pokemon should take damage (1/16 of max HP)
        assert normal_pokemon.current_hp == normal_hp - (normal_pokemon.stats.hp // 16)
        assert any(f"buffeted by the {weather.name.lower()}" in msg for msg in result.messages)

def test_weather_resistance_ability():
    """Test that weather resistance abilities reduce weather damage."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    # Create Pokemon with weather resistance ability
    resistant_pokemon = Pokemon(
        name="Resistant",
        types=(Type.NORMAL,),  # Not naturally immune
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    # Add ability that reduces both sandstorm and hail damage by 50%
    resistant_pokemon.ability = Ability(
        name="Weather Guard",
        type_=AbilityType.WEATHER_RESISTANCE,
        weather_types=(Weather.SANDSTORM, Weather.HAIL),
        resistance_multiplier=0.5  # 50% reduction
    )
    
    # Create regular Pokemon for comparison
    normal_pokemon = Pokemon(
        name="Normal",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Test in both weather types
    for weather in (Weather.SANDSTORM, Weather.HAIL):
        battle = Battle(resistant_pokemon, normal_pokemon, chart, weather=weather)
        
        # Record initial HP
        resistant_hp = resistant_pokemon.current_hp
        normal_hp = normal_pokemon.current_hp
        
        # End turn to trigger weather damage
        result = battle.end_turn()
        
        # Calculate expected damage
        base_damage = resistant_pokemon.stats.hp // 16
        reduced_damage = int(base_damage * 0.5)  # 50% reduction
        
        # Resistant Pokemon should take reduced damage
        assert resistant_pokemon.current_hp == resistant_hp - reduced_damage, \
            f"Pokemon with resistance ability took wrong {weather.name} damage"
        
        # Normal Pokemon should take full damage
        assert normal_pokemon.current_hp == normal_hp - base_damage
        assert any(f"buffeted by the {weather.name.lower()}" in msg for msg in result.messages)

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
        pp=250  # Enough PP for all attempts
    )
    attacker.moves = [water_move]
    
    # Test in sun to reduce water damage
    battle = Battle(attacker, defender, chart, weather=Weather.SUN)
    
    # Get non-critical hit damage first
    non_crit_damage = None
    # Try to get non-critical hit (1/24 chance to crit, so try up to 20 times)
    for _ in range(20):
        result = battle.execute_turn(water_move, defender)
        if not result.critical_hit:
            non_crit_damage = result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP
    assert non_crit_damage is not None, "Failed to get non-critical hit"
    
    # Then get critical hit damage
    crit_damage = None
    # Try to get critical hit (1/24 chance, try up to 200 times)
    for _ in range(200):
        result = battle.execute_turn(water_move, defender)
        if result.critical_hit:
            crit_damage = result.damage_dealt
            break
        defender.current_hp = defender.stats.hp  # Reset HP
    assert crit_damage is not None, "Failed to get critical hit in 200 attempts"
    
    # Critical hits should do ~2x damage regardless of weather
    # Allow for much wider random variation
    assert crit_damage is not None and non_crit_damage is not None
    actual_ratio = crit_damage / non_crit_damage
    assert 1.25 <= actual_ratio <= 3.0, f"Expected ~2x damage (with random factor), got {actual_ratio}x"

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
