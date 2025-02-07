"""Tests for Pokemon abilities."""

import pytest
from src.core.ability import Ability, AbilityType
from src.core.battle import Battle, Weather
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory, Effect, StatusEffect

def test_status_immunity_ability():
    """Test that status immunity abilities prevent status effects."""
    # Create an ability that prevents poison
    immunity = Ability(
        name="Immunity",
        type_=AbilityType.STATUS_IMMUNITY,
        status_effects=(StatusEffect.POISON,)
    )
    
    # Create a Pokemon with the immunity ability
    pokemon = Pokemon(
        name="Immune Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        ability=immunity
    )
    
    # Try to apply poison
    assert not pokemon.set_status(StatusEffect.POISON)
    assert pokemon.status is None
    
    # Should still be able to apply other status effects
    assert pokemon.set_status(StatusEffect.SLEEP)
    assert pokemon.status == StatusEffect.SLEEP

def test_status_resistance_ability():
    """Test that status resistance abilities reduce status chance."""
    # Create type chart with all 1.0 multipliers to avoid type resistances
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0, "fire": 1.0},
        "fire": {"normal": 1.0, "fire": 1.0}
    })
    
    # Create an ability that resists burn (50% chance reduction)
    resistance = Ability(
        name="Burn Guard",
        type_=AbilityType.STATUS_RESISTANCE,
        status_effects=(StatusEffect.BURN,),
        resistance_multiplier=0.5  # 50% chance reduction
    )
    
    # Create Pokemon
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),  # Normal type to avoid STAB
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),  # Not Fire-type to avoid type immunity
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        ability=resistance
    )
    
    # Create burn move with 100% chance
    burn_move = Move(
        name="Will-O-Wisp",
        type_=Type.FIRE,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=15,
        effects=[Effect(status=StatusEffect.BURN, status_chance=100)]
    )
    attacker.moves = [burn_move]
    
    # Create battle
    battle = Battle(attacker, defender, chart)
    
    # Test multiple times to verify reduced chance
    burn_count = 0
    trials = 100  # More trials for reliable results
    
    for trial in range(trials):
        burn_move.restore_pp()
        battle.execute_turn(burn_move, defender)
        if defender.status == StatusEffect.BURN:
            burn_count += 1
        defender.set_status(None)  # Reset status for next trial
    
    # With 50% resistance, expect around 50% success rate
    # Allow for reasonable variation with more trials
    success_rate = burn_count / trials
    assert 0.40 <= success_rate <= 0.60, f"Expected ~50% success rate (±10%), got {success_rate*100:.1f}%"

def test_multiple_status_resistances():
    """Test that abilities can reduce chance of multiple status effects."""
    # Create type chart with all 1.0 multipliers to avoid type resistances
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0, "fire": 1.0},
        "fire": {"normal": 1.0, "fire": 1.0}
    })
    
    # Create an ability that resists both burn and paralysis (50% chance reduction)
    resistance = Ability(
        name="Status Guard",
        type_=AbilityType.STATUS_RESISTANCE,
        status_effects=(StatusEffect.BURN, StatusEffect.PARALYSIS),
        resistance_multiplier=0.5  # 50% chance reduction
    )
    
    # Create Pokemon
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        ability=resistance
    )
    
    # Create status moves with 100% chance
    burn_move = Move(
        name="Will-O-Wisp",
        type_=Type.FIRE,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=15,
        effects=[Effect(status=StatusEffect.BURN, status_chance=100)]
    )
    
    paralyze_move = Move(
        name="Thunder Wave",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=15,
        effects=[Effect(status=StatusEffect.PARALYSIS, status_chance=100)]
    )
    
    attacker.moves = [burn_move, paralyze_move]
    
    # Create battle
    battle = Battle(attacker, defender, chart)
    
    # Test both status effects
    for move in [burn_move, paralyze_move]:
        status_count = 0
        trials = 100  # More trials for reliable results
        expected_status = move.effects[0].status
        
        for _ in range(trials):
            move.restore_pp()
            battle.execute_turn(move, defender)
            if defender.status == expected_status:
                status_count += 1
            defender.set_status(None)  # Reset status for next trial
        
        # With 50% resistance, expect around 50% success rate
        # Allow for reasonable variation with more trials
        success_rate = status_count / trials
        assert 0.40 <= success_rate <= 0.60, f"Expected ~50% success rate (±10%) for {expected_status.name}, got {success_rate*100:.1f}%"

def test_status_immunity_with_burn():
    """Test that a Pokemon with burn immunity cannot be burned."""
    # Create type chart with all 1.0 multipliers to avoid type resistances
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0, "fire": 1.0},
        "fire": {"normal": 1.0, "fire": 1.0}
    })
    
    # Create an ability that prevents burn
    burn_immunity = Ability(
        name="Burn Guard",
        type_=AbilityType.STATUS_IMMUNITY,
        status_effects=(StatusEffect.BURN,)
    )
    
    # Create Pokemon
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        ability=burn_immunity
    )
    
    # Create burn move with 100% chance
    burn_move = Move(
        name="Will-O-Wisp",
        type_=Type.FIRE,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=15,
        effects=[Effect(status=StatusEffect.BURN, status_chance=100)]
    )
    
    attacker.moves = [burn_move]
    
    # Create battle
    battle = Battle(attacker, defender, chart)
    
    # Test burn immunity
    for _ in range(10):  # 10 trials should be enough for immunity
        burn_move.restore_pp()
        battle.execute_turn(burn_move, defender)
        assert defender.status is None, "Pokemon should be immune to burn"
        defender.set_status(None)

def test_status_resistance_with_paralysis():
    """Test that a Pokemon with paralysis resistance has reduced chance of being paralyzed."""
    # Create type chart with all 1.0 multipliers to avoid type resistances
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0, "fire": 1.0},
        "fire": {"normal": 1.0, "fire": 1.0}
    })
    
    # Create an ability that resists paralysis
    paralysis_resistance = Ability(
        name="Static Guard",
        type_=AbilityType.STATUS_RESISTANCE,
        status_effects=(StatusEffect.PARALYSIS,),
        resistance_multiplier=0.5  # 50% chance reduction
    )
    
    # Create Pokemon
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        ability=paralysis_resistance
    )
    
    # Create paralysis move with 100% chance
    paralyze_move = Move(
        name="Thunder Wave",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=15,
        effects=[Effect(status=StatusEffect.PARALYSIS, status_chance=100)]
    )
    
    attacker.moves = [paralyze_move]
    
    # Create battle
    battle = Battle(attacker, defender, chart)
    
    # Test paralysis resistance
    paralysis_count = 0
    trials = 100  # More trials for reliable results
    
    for _ in range(trials):
        paralyze_move.restore_pp()
        battle.execute_turn(paralyze_move, defender)
        if defender.status == StatusEffect.PARALYSIS:
            paralysis_count += 1
        defender.set_status(None)  # Reset status for next trial
    
    # With 50% resistance, expect around 50% success rate
    # Allow for reasonable variation with more trials
    success_rate = paralysis_count / trials
    assert 0.40 <= success_rate <= 0.60, f"Expected ~50% success rate (±10%), got {success_rate*100:.1f}%"

def test_multiple_status_immunities():
    """Test that abilities can prevent multiple status effects."""
    # Create an ability that prevents both burn and freeze
    immunity = Ability(
        name="Temperature Control",
        type_=AbilityType.STATUS_IMMUNITY,
        status_effects=(StatusEffect.BURN, StatusEffect.FREEZE)
    )
    
    # Create a Pokemon with the immunity ability
    pokemon = Pokemon(
        name="Temperature Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        ability=immunity
    )
    
    # Try to apply burn and freeze
    assert not pokemon.set_status(StatusEffect.BURN)
    assert not pokemon.set_status(StatusEffect.FREEZE)
    assert pokemon.status is None
    
    # Should still be able to apply other status effects
    assert pokemon.set_status(StatusEffect.PARALYSIS)
    assert pokemon.status == StatusEffect.PARALYSIS

def test_weather_immunity_ability():
    """Test that weather immunity abilities prevent weather damage."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    # Create an ability that prevents sandstorm damage
    sand_immunity = Ability(
        name="Sand Veil",
        type_=AbilityType.WEATHER_IMMUNITY,
        weather_types=(Weather.SANDSTORM,)
    )
    
    # Create Pokemon with and without immunity
    normal_pokemon = Pokemon(
        name="Normal Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    immune_pokemon = Pokemon(
        name="Immune Pokemon",
        types=(Type.NORMAL,),  # Not Rock/Ground/Steel to avoid type immunity
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50,
        ability=sand_immunity
    )
    
    # Test in sandstorm
    battle = Battle(normal_pokemon, immune_pokemon, chart, weather=Weather.SANDSTORM)
    
    # Record initial HP
    normal_hp = normal_pokemon.current_hp
    immune_hp = immune_pokemon.current_hp
    
    # End turn to trigger weather damage
    result = battle.end_turn()
    
    # Normal Pokemon should take damage
    assert normal_pokemon.current_hp == normal_hp - (normal_pokemon.stats.hp // 16)
    assert "buffeted by the sandstorm" in result.messages[0]
    
    # Immune Pokemon should not take damage despite not being Rock/Ground/Steel type
    assert immune_pokemon.current_hp == immune_hp

def test_weather_resistance_ability():
    """Test that weather resistance abilities reduce weather damage."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    # Create an ability that halves sandstorm damage
    sand_resistance = Ability(
        name="Sand Resistance",
        type_=AbilityType.WEATHER_RESISTANCE,
        weather_types=(Weather.SANDSTORM,),
        resistance_multiplier=0.5  # Half damage
    )
    
    # Create Pokemon with resistance
    pokemon = Pokemon(
        name="Resistant Pokemon",
        types=(Type.NORMAL,),  # Not Rock/Ground/Steel to avoid immunity
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50,
        ability=sand_resistance
    )
    
    # Create a normal Pokemon for comparison
    normal_pokemon = Pokemon(
        name="Normal Pokemon",
        types=(Type.NORMAL,),  # Not Rock/Ground/Steel to avoid immunity
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )

    # Test in sandstorm
    battle = Battle(normal_pokemon, pokemon, chart, weather=Weather.SANDSTORM)
    initial_hp = pokemon.current_hp

    # End turn to trigger weather damage
    battle.end_turn()

    # Should take half damage (1/32 instead of 1/16 max HP)
    expected_damage = pokemon.stats.hp // 32
    assert pokemon.current_hp == initial_hp - expected_damage, f"Expected {initial_hp - expected_damage} HP (initial {initial_hp} - {expected_damage}), got {pokemon.current_hp}"

def test_multiple_weather_immunities():
    """Test that abilities can prevent damage from multiple weather types."""
    # Create type chart
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    # Create an ability that prevents both sandstorm and hail damage
    weather_immunity = Ability(
        name="Weather Protection",
        type_=AbilityType.WEATHER_IMMUNITY,
        weather_types=(Weather.SANDSTORM, Weather.HAIL)
    )
    
    # Create Pokemon with immunity
    pokemon = Pokemon(
        name="Weather Immune Pokemon",
        types=(Type.NORMAL,),  # Not Rock/Ground/Steel/Ice to avoid type immunity
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50,
        ability=weather_immunity
    )
    
    # Test in both weather conditions
    for weather in (Weather.SANDSTORM, Weather.HAIL):
        battle = Battle(pokemon, pokemon, chart, weather=weather)
        initial_hp = pokemon.current_hp
        
        # End turn to trigger weather damage
        battle.end_turn()
        
        # Should not take damage from either weather type
        assert pokemon.current_hp == initial_hp
