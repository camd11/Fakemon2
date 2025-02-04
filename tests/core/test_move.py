"""Tests for moves."""

import pytest
from src.core.move import Move, MoveCategory, Effect, StatusEffect
from src.core.types import Type
from src.core.battle import Weather

def test_move_initialization():
    """Test that moves are initialized correctly."""
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    )
    
    assert move.name == "Test Move"
    assert move.type == Type.NORMAL
    assert move.category == MoveCategory.PHYSICAL
    assert move.power == 50
    assert move.accuracy == 100
    assert move.max_pp == 10
    assert move.current_pp == 10
    assert move.effects == []

def test_move_pp_usage():
    """Test that PP is consumed correctly."""
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=2
    )
    
    # Should be able to use twice
    assert move.use()
    assert move.current_pp == 1
    assert move.use()
    assert move.current_pp == 0
    
    # Should fail on third use
    assert not move.use()
    assert move.current_pp == 0

def test_move_pp_restore():
    """Test that PP can be restored."""
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    )
    
    # Use move twice
    move.use()
    move.use()
    assert move.current_pp == 8
    
    # Restore partial PP
    move.restore_pp(1)
    assert move.current_pp == 9
    
    # Restore full PP
    move.restore_pp()
    assert move.current_pp == 10
    
    # Shouldn't restore beyond max
    move.restore_pp(5)
    assert move.current_pp == 10

def test_move_effects():
    """Test that move effects are handled correctly."""
    effect = Effect(
        status=StatusEffect.BURN,
        status_chance=100.0,
        stat_changes={"attack": -1}
    )
    
    move = Move(
        name="Test Move",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=50,
        accuracy=100,
        pp=10,
        effects=[effect]
    )
    
    assert len(move.effects) == 1
    assert move.effects[0].status == StatusEffect.BURN
    assert move.effects[0].status_chance == 100.0
    assert move.effects[0].stat_changes == {"attack": -1}

def test_move_is_damaging():
    """Test that moves are correctly identified as damaging or not."""
    physical = Move(
        name="Physical",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    )
    assert physical.is_damaging
    
    special = Move(
        name="Special",
        type_=Type.NORMAL,
        category=MoveCategory.SPECIAL,
        power=50,
        accuracy=100,
        pp=10
    )
    assert special.is_damaging
    
    status = Move(
        name="Status",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=10
    )
    assert not status.is_damaging

def test_weather_boost_water():
    """Test that Water moves are boosted in rain and reduced in sun."""
    move = Move(
        name="Water Move",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=50,
        accuracy=100,
        pp=10
    )
    
    # Should be boosted in rain
    assert move.get_weather_multiplier(Weather.RAIN) == 1.5
    
    # Should be reduced in sun
    assert move.get_weather_multiplier(Weather.SUN) == 0.5
    
    # Should be normal in other weather
    assert move.get_weather_multiplier(Weather.CLEAR) == 1.0
    assert move.get_weather_multiplier(Weather.SANDSTORM) == 1.0
    assert move.get_weather_multiplier(Weather.HAIL) == 1.0

def test_weather_boost_fire():
    """Test that Fire moves are boosted in sun and reduced in rain."""
    move = Move(
        name="Fire Move",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=50,
        accuracy=100,
        pp=10
    )
    
    # Should be boosted in sun
    assert move.get_weather_multiplier(Weather.SUN) == 1.5
    
    # Should be reduced in rain
    assert move.get_weather_multiplier(Weather.RAIN) == 0.5
    
    # Should be normal in other weather
    assert move.get_weather_multiplier(Weather.CLEAR) == 1.0
    assert move.get_weather_multiplier(Weather.SANDSTORM) == 1.0
    assert move.get_weather_multiplier(Weather.HAIL) == 1.0

def test_weather_boost_other():
    """Test that other move types are unaffected by weather."""
    move = Move(
        name="Normal Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    )
    
    # Should be normal in all weather
    assert move.get_weather_multiplier(Weather.CLEAR) == 1.0
    assert move.get_weather_multiplier(Weather.RAIN) == 1.0
    assert move.get_weather_multiplier(Weather.SUN) == 1.0
    assert move.get_weather_multiplier(Weather.SANDSTORM) == 1.0
    assert move.get_weather_multiplier(Weather.HAIL) == 1.0
