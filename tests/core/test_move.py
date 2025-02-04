"""Tests for Move class functionality."""

import pytest
from src.core.move import Move, MoveCategory, Effect, StatusEffect
from src.core.types import Type

@pytest.fixture
def basic_move() -> Move:
    """Create a basic move for testing."""
    return Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=35
    )

@pytest.fixture
def status_move() -> Move:
    """Create a status move with effects for testing."""
    return Move(
        name="Test Status",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30,
        effects=[
            Effect(
                status=StatusEffect.PARALYSIS,
                status_chance=30,
                stat_changes={"speed": -1}
            )
        ]
    )

def test_move_creation(basic_move):
    """Test basic move creation."""
    assert basic_move.name == "Test Move"
    assert basic_move.type == Type.NORMAL
    assert basic_move.category == MoveCategory.PHYSICAL
    assert basic_move.power == 40
    assert basic_move.accuracy == 100
    assert basic_move.max_pp == 35
    assert basic_move.current_pp == 35
    assert len(basic_move.effects) == 0

def test_move_pp_management(basic_move):
    """Test PP usage and restoration."""
    # Test using PP
    assert basic_move.current_pp == 35
    assert basic_move.use()  # Should return True and decrease PP
    assert basic_move.current_pp == 34
    
    # Test using all PP
    for _ in range(34):
        basic_move.use()
    assert basic_move.current_pp == 0
    
    # Test trying to use move with no PP
    assert not basic_move.use()  # Should return False
    assert basic_move.current_pp == 0
    
    # Test partial PP restore
    basic_move.restore_pp(10)
    assert basic_move.current_pp == 10
    
    # Test full PP restore
    basic_move.restore_pp()
    assert basic_move.current_pp == basic_move.max_pp

def test_status_move_effects(status_move):
    """Test status move effect properties."""
    assert len(status_move.effects) == 1
    effect = status_move.effects[0]
    
    assert effect.status == StatusEffect.PARALYSIS
    assert effect.status_chance == 30
    assert effect.stat_changes == {"speed": -1}

def test_move_is_damaging():
    """Test is_damaging property for different move categories."""
    physical_move = Move(
        name="Physical",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=35
    )
    assert physical_move.is_damaging
    
    special_move = Move(
        name="Special",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=35
    )
    assert special_move.is_damaging
    
    status_move = Move(
        name="Status",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30
    )
    assert not status_move.is_damaging

def test_effect_initialization():
    """Test Effect class initialization and defaults."""
    # Test with minimal parameters
    effect = Effect()
    assert effect.status is None
    assert effect.status_chance == 0.0
    assert effect.stat_changes == {}
    
    # Test with all parameters
    effect = Effect(
        status=StatusEffect.BURN,
        status_chance=50.0,
        stat_changes={"attack": -1, "speed": -1}
    )
    assert effect.status == StatusEffect.BURN
    assert effect.status_chance == 50.0
    assert effect.stat_changes == {"attack": -1, "speed": -1}

def test_move_with_multiple_effects():
    """Test move with multiple effects."""
    move = Move(
        name="Multi Effect",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=20,
        effects=[
            Effect(status=StatusEffect.BURN, status_chance=10),
            Effect(stat_changes={"attack": -1}),
            Effect(stat_changes={"defense": -1})
        ]
    )
    
    assert len(move.effects) == 3
    assert move.effects[0].status == StatusEffect.BURN
    assert move.effects[1].stat_changes == {"attack": -1}
    assert move.effects[2].stat_changes == {"defense": -1}
