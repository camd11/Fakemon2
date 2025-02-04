"""Tests for battle items."""

import pytest
from src.core.item import (
    Item,
    ItemType,
    ItemEffect,
    HeldItemTrigger,
    CHARCOAL,
    MYSTIC_WATER,
    MIRACLE_SEED,
    MAGNET,
    NEVER_MELT_ICE,
    BLACK_BELT,
    POISON_BARB,
    SOFT_SAND,
    SHARP_BEAK,
    TWISTED_SPOON,
    SILVER_POWDER,
    HARD_STONE,
    SPELL_TAG,
    DRAGON_FANG,
    METAL_COAT,
    SILK_SCARF
)
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory
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

def test_type_boost_damage():
    """Test that type-enhancing items boost move damage."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.FIRE,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    fire_move = Move(
        name="Fire Move",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without item
    attacker.moves = [fire_move]
    result = battle.execute_turn(fire_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Charcoal
    attacker.equip_item(CHARCOAL)
    result = battle.execute_turn(fire_move, defender)
    boosted_damage = result.damage_dealt
    
    # Should deal 20% more damage
    assert boosted_damage == int(base_damage * 1.2)

def test_type_boost_wrong_type():
    """Test that type-enhancing items don't boost wrong types."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.WATER,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    water_move = Move(
        name="Water Move",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without item
    attacker.moves = [water_move]
    result = battle.execute_turn(water_move, defender)
    base_damage = result.damage_dealt
    
    # Test with wrong type item (Charcoal)
    attacker.equip_item(CHARCOAL)
    result = battle.execute_turn(water_move, defender)
    
    # Damage should be unchanged
    assert result.damage_dealt == base_damage

def test_type_boost_stacks():
    """Test that type boost stacks with other multipliers."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.WATER,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.FIRE,),  # Weak to water
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    water_move = Move(
        name="Water Move",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without item
    attacker.moves = [water_move]
    result = battle.execute_turn(water_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Mystic Water in rain
    attacker.equip_item(MYSTIC_WATER)
    battle.weather = Weather.RAIN
    result = battle.execute_turn(water_move, defender)
    
    # Should stack: STAB (1.5) * Super Effective (2.0) * Rain (1.5) * Item (1.2)
    expected_multiplier = 1.5 * 2.0 * 1.5 * 1.2
    assert result.damage_dealt == int(base_damage * expected_multiplier)

def test_all_type_items():
    """Test that all type-enhancing items work correctly."""
    type_items = {
        (CHARCOAL, Type.FIRE),
        (MYSTIC_WATER, Type.WATER),
        (MIRACLE_SEED, Type.GRASS),
        (MAGNET, Type.ELECTRIC),
        (NEVER_MELT_ICE, Type.ICE),
        (BLACK_BELT, Type.FIGHTING),
        (POISON_BARB, Type.POISON),
        (SOFT_SAND, Type.GROUND),
        (SHARP_BEAK, Type.FLYING),
        (TWISTED_SPOON, Type.PSYCHIC),
        (SILVER_POWDER, Type.BUG),
        (HARD_STONE, Type.ROCK),
        (SPELL_TAG, Type.GHOST),
        (DRAGON_FANG, Type.DRAGON),
        (METAL_COAT, Type.STEEL),
        (SILK_SCARF, Type.NORMAL)
    }
    
    for item, move_type in type_items:
        attacker = Pokemon(
            name="Attacker",
            types=(move_type,),
            base_stats=Stats(100, 100, 100, 100, 100, 100),
            level=50
        )
        
        defender = Pokemon(
            name="Defender",
            types=(Type.NORMAL,),
            base_stats=Stats(100, 100, 100, 100, 100, 100),
            level=50
        )
        
        # Create test move
        test_move = Move(
            name=f"{move_type.name} Move",
            type_=move_type,
            category=MoveCategory.SPECIAL,
            power=100,
            accuracy=100,
            pp=10
        )
        
        battle = Battle(attacker, defender, TypeEffectiveness())
        
        # Test without item
        attacker.moves = [test_move]
        result = battle.execute_turn(test_move, defender)
        base_damage = result.damage_dealt
        
        # Test with type item
        attacker.equip_item(item)
        result = battle.execute_turn(test_move, defender)
        
        # Should deal 20% more damage
        assert result.damage_dealt == int(base_damage * 1.2)
