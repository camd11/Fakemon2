"""Tests for Pokemon class functionality."""

import pytest
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type
from src.core.move import Move, MoveCategory

@pytest.fixture
def basic_stats() -> Stats:
    """Create basic stats for testing."""
    return Stats(
        hp=45,
        attack=49,
        defense=49,
        special_attack=65,
        special_defense=65,
        speed=45
    )

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

def test_pokemon_creation(basic_stats):
    """Test basic Pokemon creation."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=5
    )
    
    assert pokemon.name == "Test Pokemon"
    assert pokemon.types == (Type.NORMAL,)
    assert pokemon.level == 5
    assert pokemon.current_hp == pokemon.stats.hp
    assert len(pokemon.moves) == 0

def test_pokemon_stat_calculation(basic_stats):
    """Test that stats are calculated correctly based on level."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=5
    )
    
    # At level 5, stats should be calculated using the formula:
    # HP = ((2 * Base + IV + (EV/4)) * Level/100) + Level + 10
    # Others = ((2 * Base + IV + (EV/4)) * Level/100) + 5
    # With no IVs/EVs:
    expected_hp = int((2 * 45 * 5 / 100) + 5 + 10)  # Base HP = 45
    expected_attack = int((2 * 49 * 5 / 100) + 5)   # Base Attack = 49
    
    assert pokemon.stats.hp == expected_hp
    assert pokemon.stats.attack == expected_attack

def test_pokemon_move_management(basic_stats, basic_move):
    """Test adding and using moves."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=5,
        moves=[basic_move]
    )
    
    assert len(pokemon.moves) == 1
    assert pokemon.moves[0].name == "Test Move"
    assert pokemon.moves[0].current_pp == 35

def test_pokemon_damage_handling(basic_stats):
    """Test taking damage and healing."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=5
    )
    
    initial_hp = pokemon.current_hp
    damage_dealt = pokemon.take_damage(10)
    
    assert damage_dealt == 10
    assert pokemon.current_hp == initial_hp - 10
    
    healed = pokemon.heal(5)
    assert healed == 5
    assert pokemon.current_hp == initial_hp - 5

def test_pokemon_stat_stages(basic_stats):
    """Test stat stage modifications."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=basic_stats,
        level=5
    )
    
    # Test raising attack
    assert pokemon.modify_stat("attack", 1)
    assert pokemon.stat_stages["attack"] == 1
    multiplier = pokemon.get_stat_multiplier("attack")
    assert multiplier > 1
    
    # Test lowering defense
    assert pokemon.modify_stat("defense", -1)
    assert pokemon.stat_stages["defense"] == -1
    multiplier = pokemon.get_stat_multiplier("defense")
    assert multiplier < 1
    
    # Test stat stage limits
    for _ in range(10):  # Try to go beyond +6
        pokemon.modify_stat("attack", 1)
    assert pokemon.stat_stages["attack"] <= 6
    
    for _ in range(10):  # Try to go beyond -6
        pokemon.modify_stat("defense", -1)
    assert pokemon.stat_stages["defense"] >= -6

def test_pokemon_type_validation(basic_stats):
    """Test type validation during Pokemon creation."""
    # Test valid number of types
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL, Type.FLYING),
        base_stats=basic_stats,
        level=5
    )
    assert len(pokemon.types) == 2
    
    # Test too many types
    with pytest.raises(ValueError):
        Pokemon(
            name="Invalid Pokemon",
            types=(Type.NORMAL, Type.FLYING, Type.FIRE),
            base_stats=basic_stats,
            level=5
        )
    
    # Test no types
    with pytest.raises(ValueError):
        Pokemon(
            name="Invalid Pokemon",
            types=(),
            base_stats=basic_stats,
            level=5
        )

def test_pokemon_move_limit(basic_stats, basic_move):
    """Test move limit enforcement."""
    moves = [basic_move] * 5  # Try to add 5 moves
    
    with pytest.raises(ValueError):
        Pokemon(
            name="Test Pokemon",
            types=(Type.NORMAL,),
            base_stats=basic_stats,
            level=5,
            moves=moves
        )
