"""Tests for Pokemon abilities."""

import pytest
from src.core.ability import Ability, AbilityType
from src.core.battle import Battle
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
    trials = 100
    
    for trial in range(trials):
        print(f"\nTrial {trial}:")
        print(f"Before turn - Defender status: {defender.status}")
        battle.execute_turn(burn_move, defender)
        print(f"After turn - Defender status: {defender.status}")
        if defender.status == StatusEffect.BURN:
            burn_count += 1
            print(f"Burn detected! Count now: {burn_count}")
        print(f"Resetting status from: {defender.status}")
        defender.set_status(None)  # Reset status for next trial
        burn_move.restore_pp()  # Restore PP for next trial
        print(f"After reset - Defender status: {defender.status}")
    
    # With 50% resistance, expect around 50% success rate
    # Allow for some random variation (40-60%)
    success_rate = burn_count / trials
    assert 0.40 <= success_rate <= 0.60  # Wider range to account for random variation

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
