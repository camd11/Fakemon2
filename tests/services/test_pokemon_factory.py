"""Tests for PokemonFactory service."""

import pytest
from src.services.pokemon_factory import PokemonFactory
from src.core.pokemon import Pokemon
from src.core.move import Move, MoveCategory, StatusEffect
from src.core.types import Type

@pytest.fixture
def factory() -> PokemonFactory:
    """Create a PokemonFactory instance for testing."""
    return PokemonFactory()

def test_pokemon_creation(factory):
    """Test creating a Pokemon from data."""
    pokemon = factory.create_pokemon("charmander", 5)
    
    assert pokemon is not None
    assert pokemon.name == "Charmander"
    assert Type.FIRE in pokemon.types
    assert pokemon.level == 5
    assert len(pokemon.moves) == 2  # Should have starting moves
    
    # Verify stats are calculated correctly
    assert pokemon.stats.hp > 0
    assert pokemon.stats.attack > 0
    assert pokemon.stats.defense > 0
    assert pokemon.stats.special_attack > 0
    assert pokemon.stats.special_defense > 0
    assert pokemon.stats.speed > 0

def test_move_creation(factory):
    """Test creating a Move from data."""
    move = factory.create_move("ember")
    
    assert move is not None
    assert move.name == "Ember"
    assert move.type == Type.FIRE
    assert move.category == MoveCategory.SPECIAL
    assert move.power == 40
    assert move.accuracy == 100
    assert move.max_pp == 25
    
    # Check effect
    assert len(move.effects) == 1
    effect = move.effects[0]
    assert effect.status == StatusEffect.BURN
    assert effect.status_chance == 10

def test_random_pokemon_creation(factory):
    """Test creating random Pokemon."""
    pokemon = factory.create_random_pokemon(level=10)
    
    assert pokemon is not None
    assert 1 <= len(pokemon.types) <= 2
    assert pokemon.level == 10
    assert len(pokemon.moves) > 0
    assert len(pokemon.moves) <= 4

def test_pokemon_creation_with_invalid_id(factory):
    """Test creating Pokemon with invalid ID."""
    pokemon = factory.create_pokemon("nonexistent", 5)
    assert pokemon is None

def test_move_creation_with_invalid_id(factory):
    """Test creating move with invalid ID."""
    move = factory.create_move("nonexistent")
    assert move is None

def test_random_pokemon_with_exclusions(factory):
    """Test creating random Pokemon with exclusions."""
    excluded = ["charmander", "squirtle"]
    pokemon = factory.create_random_pokemon(level=5, exclude_ids=excluded)
    
    assert pokemon is not None
    assert pokemon.name not in ["Charmander", "Squirtle"]

def test_pokemon_with_custom_moves(factory):
    """Test creating Pokemon with specific moves."""
    moves = ["tackle", "growl"]
    pokemon = factory.create_pokemon("bulbasaur", 5, moves=moves)
    
    assert pokemon is not None
    assert len(pokemon.moves) == 2
    assert pokemon.moves[0].name == "Tackle"
    assert pokemon.moves[1].name == "Growl"

def test_type_chart_loading(factory):
    """Test type effectiveness data is loaded correctly."""
    # Test some basic type matchups
    chart = factory.type_chart
    
    assert chart.get_multiplier(Type.FIRE, (Type.GRASS,)) == 2.0
    assert chart.get_multiplier(Type.WATER, (Type.FIRE,)) == 2.0
    assert chart.get_multiplier(Type.GRASS, (Type.WATER,)) == 2.0
    
    assert chart.get_multiplier(Type.FIRE, (Type.WATER,)) == 0.5
    assert chart.get_multiplier(Type.WATER, (Type.GRASS,)) == 0.5
    assert chart.get_multiplier(Type.GRASS, (Type.FIRE,)) == 0.5
