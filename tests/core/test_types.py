"""Tests for type system functionality."""

import pytest
from src.core.types import Type, TypeEffectiveness

@pytest.fixture
def type_chart() -> TypeEffectiveness:
    """Create a type chart with some basic effectiveness data."""
    chart = TypeEffectiveness()
    test_data = {
        "fire": {
            "grass": 2.0,
            "water": 0.5,
            "fire": 0.5,
            "rock": 0.5,
            "ice": 2.0,
            "steel": 2.0
        },
        "water": {
            "fire": 2.0,
            "grass": 0.5,
            "water": 0.5,
            "ground": 2.0,
            "rock": 2.0
        },
        "grass": {
            "fire": 0.5,
            "water": 2.0,
            "grass": 0.5,
            "ground": 2.0,
            "rock": 2.0
        },
        "electric": {
            "water": 2.0,
            "grass": 0.5,
            "electric": 0.5,
            "ground": 0.0,
            "flying": 2.0
        }
    }
    chart.load_from_json(test_data)
    return chart

def test_type_enum_values():
    """Test that all required types are present in the Type enum."""
    expected_types = {
        "NORMAL", "FIRE", "WATER", "ELECTRIC", "GRASS", "ICE",
        "FIGHTING", "POISON", "GROUND", "FLYING", "PSYCHIC",
        "BUG", "ROCK", "GHOST", "DRAGON", "DARK", "STEEL", "FAIRY"
    }
    
    actual_types = {t.name for t in Type}
    assert actual_types == expected_types

def test_basic_effectiveness(type_chart):
    """Test basic type effectiveness calculations."""
    # Super effective
    assert type_chart.get_multiplier(Type.FIRE, (Type.GRASS,)) == 2.0
    assert type_chart.get_multiplier(Type.WATER, (Type.FIRE,)) == 2.0
    
    # Not very effective
    assert type_chart.get_multiplier(Type.FIRE, (Type.WATER,)) == 0.5
    assert type_chart.get_multiplier(Type.GRASS, (Type.FIRE,)) == 0.5
    
    # No effect (immunity)
    assert type_chart.get_multiplier(Type.ELECTRIC, (Type.GROUND,)) == 0.0

def test_dual_type_effectiveness(type_chart):
    """Test effectiveness calculations against dual-type Pokemon."""
    # Test multiplicative effect (2.0 * 2.0 = 4.0)
    multiplier = type_chart.get_multiplier(Type.WATER, (Type.FIRE, Type.ROCK))
    assert multiplier == 4.0
    
    # Test mixed effectiveness (2.0 * 0.5 = 1.0)
    multiplier = type_chart.get_multiplier(Type.GRASS, (Type.WATER, Type.FIRE))
    assert multiplier == 1.0
    
    # Test with immunity (anything * 0 = 0)
    multiplier = type_chart.get_multiplier(Type.ELECTRIC, (Type.WATER, Type.GROUND))
    assert multiplier == 0.0

def test_missing_type_combinations(type_chart):
    """Test handling of missing type combinations."""
    # Default to neutral effectiveness (1.0) for undefined matchups
    assert type_chart.get_multiplier(Type.FIRE, (Type.GHOST,)) == 1.0
    assert type_chart.get_multiplier(Type.DARK, (Type.FAIRY,)) == 1.0

def test_same_type_effectiveness(type_chart):
    """Test effectiveness when attacking same type."""
    assert type_chart.get_multiplier(Type.FIRE, (Type.FIRE,)) == 0.5
    assert type_chart.get_multiplier(Type.WATER, (Type.WATER,)) == 0.5
    assert type_chart.get_multiplier(Type.GRASS, (Type.GRASS,)) == 0.5

def test_empty_type_effectiveness(type_chart):
    """Test effectiveness calculation with no defender types."""
    assert type_chart.get_multiplier(Type.FIRE, ()) == 1.0
    assert type_chart.get_multiplier(Type.WATER, ()) == 1.0

def test_type_chart_loading():
    """Test loading type effectiveness data."""
    chart = TypeEffectiveness()
    test_data = {
        "fire": {
            "grass": 2.0,
            "water": 0.5
        }
    }
    
    # Test loading data
    chart.load_from_json(test_data)
    assert chart.get_multiplier(Type.FIRE, (Type.GRASS,)) == 2.0
    
    # Test clearing and reloading data
    new_data = {
        "water": {
            "fire": 2.0
        }
    }
    chart.load_from_json(new_data)
    assert chart.get_multiplier(Type.FIRE, (Type.GRASS,)) == 1.0  # Old data should be cleared
    assert chart.get_multiplier(Type.WATER, (Type.FIRE,)) == 2.0  # New data should be loaded
