"""Tests for items."""

import pytest
from src.core.item import (
    Item,
    ItemType,
    ItemEffect,
    HeldItemTrigger,
    FULL_HEAL,
    ANTIDOTE,
    BURN_HEAL,
    PARALYZE_HEAL,
    AWAKENING,
    ICE_HEAL,
    LEFTOVERS,
    ORAN_BERRY,
    LUM_BERRY,
    MUSCLE_BAND,
    WISE_GLASSES,
    FOCUS_SASH
)
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory, StatusEffect
from src.core.battle import Battle

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon."""
    return Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

def test_equip_item(test_pokemon):
    """Test equipping and unequipping items."""
    # Should be able to equip item
    assert test_pokemon.equip_item(LEFTOVERS)
    assert test_pokemon.held_item == LEFTOVERS
    
    # Should not be able to equip second item
    assert not test_pokemon.equip_item(ORAN_BERRY)
    assert test_pokemon.held_item == LEFTOVERS
    
    # Should be able to unequip item
    item = test_pokemon.unequip_item()
    assert item == LEFTOVERS
    assert test_pokemon.held_item is None
    
    # Should be able to equip new item after unequipping
    assert test_pokemon.equip_item(ORAN_BERRY)
    assert test_pokemon.held_item == ORAN_BERRY

def test_leftovers_healing(test_pokemon):
    """Test passive healing from Leftovers."""
    test_pokemon.equip_item(LEFTOVERS)
    
    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())
    
    # Damage Pokemon
    test_pokemon.take_damage(50)  # Half HP
    initial_hp = test_pokemon.current_hp
    
    # End turn should trigger Leftovers
    result = battle.end_turn()
    
    # Should heal 1/16 max HP
    assert test_pokemon.current_hp == initial_hp + (test_pokemon.stats.hp // 16)
    assert any("restored a little HP" in msg for msg in result.messages)

def test_oran_berry_healing(test_pokemon):
    """Test low HP trigger for Oran Berry."""
    test_pokemon.equip_item(ORAN_BERRY)
    
    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())
    
    # Create test move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    # Damage Pokemon to trigger berry (25% HP threshold)
    test_pokemon.take_damage(int(test_pokemon.stats.hp * 0.8))  # Down to 20% HP
    initial_hp = test_pokemon.current_hp
    
    # Execute turn should trigger berry
    result = battle.execute_turn(move, test_pokemon)
    
    # Should heal 10 HP
    assert test_pokemon.current_hp == initial_hp + 10
    assert any("restored some HP" in msg for msg in result.messages)
    assert test_pokemon._used_held_item  # Should be consumed

def test_lum_berry_status_cure(test_pokemon):
    """Test status cure from Lum Berry."""
    test_pokemon.equip_item(LUM_BERRY)
    
    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())
    
    # Apply status
    test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status == StatusEffect.POISON
    
    # End turn should trigger berry
    result = battle.end_turn()
    
    # Status should be cured
    assert test_pokemon.status is None
    assert any("cured its poison" in msg for msg in result.messages)
    assert test_pokemon._used_held_item  # Should be consumed

def test_focus_sash_survival(test_pokemon):
    """Test Focus Sash preventing KO."""
    test_pokemon.equip_item(FOCUS_SASH)
    
    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())
    
    # Create powerful move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=999,
        accuracy=100,
        pp=10
    )
    
    # Execute turn with lethal damage
    result = battle.execute_turn(move, test_pokemon)
    
    # Should survive with 1 HP
    assert test_pokemon.current_hp == 1
    assert any("hung on using its Focus Sash" in msg for msg in result.messages)
    assert test_pokemon._used_held_item  # Should be consumed

def test_held_item_single_use(test_pokemon):
    """Test that single-use items can only be used once."""
    test_pokemon.equip_item(ORAN_BERRY)
    
    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())
    
    # Damage Pokemon twice
    test_pokemon.take_damage(int(test_pokemon.stats.hp * 0.8))  # Down to 20% HP
    initial_hp = test_pokemon.current_hp
    
    # First trigger should work
    effect = test_pokemon.check_held_item(HeldItemTrigger.LOW_HP, hp_percent=0.2)
    assert effect is not None
    assert test_pokemon._used_held_item
    
    # Second trigger should fail
    effect = test_pokemon.check_held_item(HeldItemTrigger.LOW_HP, hp_percent=0.2)
    assert effect is None

def test_held_item_wrong_trigger(test_pokemon):
    """Test that items don't trigger under wrong conditions."""
    test_pokemon.equip_item(ORAN_BERRY)
    
    # Check with wrong trigger type
    effect = test_pokemon.check_held_item(HeldItemTrigger.STATUS)
    assert effect is None
    
    # Check with HP above threshold
    effect = test_pokemon.check_held_item(HeldItemTrigger.LOW_HP, hp_percent=0.5)
    assert effect is None
    
    # Item should not be marked as used
    assert not test_pokemon._used_held_item
