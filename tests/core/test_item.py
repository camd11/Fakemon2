"""Tests for items."""

import pytest
from src.core.item import (
    Item,
    ItemType,
    ItemEffect,
    FULL_HEAL,
    ANTIDOTE,
    BURN_HEAL,
    PARALYZE_HEAL,
    AWAKENING,
    ICE_HEAL
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

def test_full_heal_cures_all_status(test_pokemon):
    """Test that Full Heal cures any status condition."""
    # Test each status
    for status in [
        StatusEffect.POISON,
        StatusEffect.BURN,
        StatusEffect.PARALYSIS,
        StatusEffect.SLEEP,
        StatusEffect.FREEZE
    ]:
        # Apply status
        test_pokemon.set_status(status)
        assert test_pokemon.status == status
        
        # Use Full Heal
        assert FULL_HEAL.can_use(test_pokemon)
        assert FULL_HEAL.use(test_pokemon)
        assert test_pokemon.status is None

def test_antidote_cures_poison(test_pokemon):
    """Test that Antidote only cures poison."""
    # Should cure poison
    test_pokemon.set_status(StatusEffect.POISON)
    assert ANTIDOTE.can_use(test_pokemon)
    assert ANTIDOTE.use(test_pokemon)
    assert test_pokemon.status is None
    
    # Should not be usable on other statuses
    test_pokemon.set_status(StatusEffect.BURN)
    assert not ANTIDOTE.can_use(test_pokemon)
    assert not ANTIDOTE.use(test_pokemon)
    assert test_pokemon.status == StatusEffect.BURN

def test_burn_heal_cures_burn(test_pokemon):
    """Test that Burn Heal only cures burn."""
    # Should cure burn
    test_pokemon.set_status(StatusEffect.BURN)
    assert BURN_HEAL.can_use(test_pokemon)
    assert BURN_HEAL.use(test_pokemon)
    assert test_pokemon.status is None
    
    # Should not be usable on other statuses
    test_pokemon.set_status(StatusEffect.POISON)
    assert not BURN_HEAL.can_use(test_pokemon)
    assert not BURN_HEAL.use(test_pokemon)
    assert test_pokemon.status == StatusEffect.POISON

def test_paralyze_heal_cures_paralysis(test_pokemon):
    """Test that Paralyze Heal only cures paralysis."""
    # Should cure paralysis
    test_pokemon.set_status(StatusEffect.PARALYSIS)
    assert PARALYZE_HEAL.can_use(test_pokemon)
    assert PARALYZE_HEAL.use(test_pokemon)
    assert test_pokemon.status is None
    
    # Should not be usable on other statuses
    test_pokemon.set_status(StatusEffect.SLEEP)
    assert not PARALYZE_HEAL.can_use(test_pokemon)
    assert not PARALYZE_HEAL.use(test_pokemon)
    assert test_pokemon.status == StatusEffect.SLEEP

def test_awakening_cures_sleep(test_pokemon):
    """Test that Awakening only cures sleep."""
    # Should cure sleep
    test_pokemon.set_status(StatusEffect.SLEEP)
    assert AWAKENING.can_use(test_pokemon)
    assert AWAKENING.use(test_pokemon)
    assert test_pokemon.status is None
    
    # Should not be usable on other statuses
    test_pokemon.set_status(StatusEffect.FREEZE)
    assert not AWAKENING.can_use(test_pokemon)
    assert not AWAKENING.use(test_pokemon)
    assert test_pokemon.status == StatusEffect.FREEZE

def test_ice_heal_cures_freeze(test_pokemon):
    """Test that Ice Heal only cures freeze."""
    # Should cure freeze
    test_pokemon.set_status(StatusEffect.FREEZE)
    assert ICE_HEAL.can_use(test_pokemon)
    assert ICE_HEAL.use(test_pokemon)
    assert test_pokemon.status is None
    
    # Should not be usable on other statuses
    test_pokemon.set_status(StatusEffect.PARALYSIS)
    assert not ICE_HEAL.can_use(test_pokemon)
    assert not ICE_HEAL.use(test_pokemon)
    assert test_pokemon.status == StatusEffect.PARALYSIS

def test_status_items_require_status(test_pokemon):
    """Test that status items can't be used on Pokemon with no status."""
    # Pokemon starts with no status
    assert test_pokemon.status is None
    
    # None of the status items should be usable
    assert not FULL_HEAL.can_use(test_pokemon)
    assert not ANTIDOTE.can_use(test_pokemon)
    assert not BURN_HEAL.can_use(test_pokemon)
    assert not PARALYZE_HEAL.can_use(test_pokemon)
    assert not AWAKENING.can_use(test_pokemon)
    assert not ICE_HEAL.can_use(test_pokemon)
    
    # Using them should fail
    assert not FULL_HEAL.use(test_pokemon)
    assert not ANTIDOTE.use(test_pokemon)
    assert not BURN_HEAL.use(test_pokemon)
    assert not PARALYZE_HEAL.use(test_pokemon)
    assert not AWAKENING.use(test_pokemon)
    assert not ICE_HEAL.use(test_pokemon)
