"""Tests for Pokemon abilities."""

import pytest
from src.core.ability import (
    Ability,
    AbilityType,
    IMMUNITY,
    LIMBER,
    WATER_VEIL,
    VITAL_SPIRIT,
    MAGMA_ARMOR
)
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type
from src.core.move import StatusEffect

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon."""
    return Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

def test_ability_prevents_status():
    """Test that abilities correctly report which statuses they prevent."""
    assert IMMUNITY.prevents_status(StatusEffect.POISON)
    assert IMMUNITY.prevents_status(StatusEffect.BURN)
    assert IMMUNITY.prevents_status(StatusEffect.PARALYSIS)
    assert IMMUNITY.prevents_status(StatusEffect.SLEEP)
    assert IMMUNITY.prevents_status(StatusEffect.FREEZE)
    
    assert LIMBER.prevents_status(StatusEffect.PARALYSIS)
    assert not LIMBER.prevents_status(StatusEffect.POISON)
    
    assert WATER_VEIL.prevents_status(StatusEffect.BURN)
    assert not WATER_VEIL.prevents_status(StatusEffect.SLEEP)
    
    assert VITAL_SPIRIT.prevents_status(StatusEffect.SLEEP)
    assert not VITAL_SPIRIT.prevents_status(StatusEffect.FREEZE)
    
    assert MAGMA_ARMOR.prevents_status(StatusEffect.FREEZE)
    assert not MAGMA_ARMOR.prevents_status(StatusEffect.BURN)

def test_immunity_ability(test_pokemon):
    """Test that Immunity prevents all status conditions."""
    test_pokemon.ability = IMMUNITY
    
    # Try to apply each status
    assert not test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status is None
    
    assert not test_pokemon.set_status(StatusEffect.BURN)
    assert test_pokemon.status is None
    
    assert not test_pokemon.set_status(StatusEffect.PARALYSIS)
    assert test_pokemon.status is None
    
    assert not test_pokemon.set_status(StatusEffect.SLEEP)
    assert test_pokemon.status is None
    
    assert not test_pokemon.set_status(StatusEffect.FREEZE)
    assert test_pokemon.status is None

def test_limber_ability(test_pokemon):
    """Test that Limber prevents paralysis but not other statuses."""
    test_pokemon.ability = LIMBER
    
    # Should prevent paralysis
    assert not test_pokemon.set_status(StatusEffect.PARALYSIS)
    assert test_pokemon.status is None
    
    # Should allow other statuses
    assert test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status == StatusEffect.POISON

def test_water_veil_ability(test_pokemon):
    """Test that Water Veil prevents burns but not other statuses."""
    test_pokemon.ability = WATER_VEIL
    
    # Should prevent burn
    assert not test_pokemon.set_status(StatusEffect.BURN)
    assert test_pokemon.status is None
    
    # Should allow other statuses
    assert test_pokemon.set_status(StatusEffect.SLEEP)
    assert test_pokemon.status == StatusEffect.SLEEP

def test_vital_spirit_ability(test_pokemon):
    """Test that Vital Spirit prevents sleep but not other statuses."""
    test_pokemon.ability = VITAL_SPIRIT
    
    # Should prevent sleep
    assert not test_pokemon.set_status(StatusEffect.SLEEP)
    assert test_pokemon.status is None
    
    # Should allow other statuses
    assert test_pokemon.set_status(StatusEffect.FREEZE)
    assert test_pokemon.status == StatusEffect.FREEZE

def test_magma_armor_ability(test_pokemon):
    """Test that Magma Armor prevents freezing but not other statuses."""
    test_pokemon.ability = MAGMA_ARMOR
    
    # Should prevent freeze
    assert not test_pokemon.set_status(StatusEffect.FREEZE)
    assert test_pokemon.status is None
    
    # Should allow other statuses
    assert test_pokemon.set_status(StatusEffect.BURN)
    assert test_pokemon.status == StatusEffect.BURN

def test_ability_and_type_immunity(test_pokemon):
    """Test that both ability and type immunities work together."""
    # Give a Fire type Pokemon Water Veil
    test_pokemon.types = (Type.FIRE,)
    test_pokemon.ability = WATER_VEIL
    
    # Should be immune to burn from both type and ability
    assert not test_pokemon.set_status(StatusEffect.BURN)
    assert test_pokemon.status is None
    
    # Should allow other statuses
    assert test_pokemon.set_status(StatusEffect.SLEEP)
    assert test_pokemon.status == StatusEffect.SLEEP

def test_no_ability(test_pokemon):
    """Test that Pokemon with no ability can receive any status."""
    test_pokemon.ability = None
    
    # Should be able to receive any status
    assert test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status == StatusEffect.POISON
    
    # Clear status
    test_pokemon.set_status(None)
    
    assert test_pokemon.set_status(StatusEffect.BURN)
    assert test_pokemon.status == StatusEffect.BURN
