"""Tests for the item system."""

import pytest
from src.core.item import Item, ItemType, ItemEffect
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type
from src.core.move import Move, MoveCategory

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon for item testing."""
    stats = Stats(
        hp=100,
        attack=100,
        defense=100,
        special_attack=100,
        special_defense=100,
        speed=100
    )
    
    moves = [
        Move(
            name="Test Move",
            type_=Type.NORMAL,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            pp=35
        )
    ]
    
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=stats,
        level=50,
        moves=moves
    )
    pokemon.current_hp = 50  # Set to half HP for healing tests
    pokemon.moves[0].current_pp = 20  # Set to reduced PP for PP restore tests
    return pokemon

def test_item_creation():
    """Test basic item creation."""
    effect = ItemEffect(type=ItemType.HEALING, value=20)
    item = Item(
        name="Potion",
        description="Restores 20 HP",
        effect=effect,
        price=100
    )
    
    assert item.name == "Potion"
    assert item.description == "Restores 20 HP"
    assert item.effect.type == ItemType.HEALING
    assert item.effect.value == 20
    assert item.price == 100
    assert item.single_use is True

def test_item_equality():
    """Test item equality comparison."""
    effect1 = ItemEffect(type=ItemType.HEALING, value=20)
    effect2 = ItemEffect(type=ItemType.HEALING, value=20)
    
    item1 = Item("Potion", "Restores 20 HP", effect1, 100)
    item2 = Item("Potion", "Restores 20 HP", effect2, 100)
    item3 = Item("Super Potion", "Restores 50 HP", 
                 ItemEffect(type=ItemType.HEALING, value=50), 200)
    
    assert item1 == item2
    assert item1 != item3
    assert item1 != "Not an item"

def test_healing_item(test_pokemon):
    """Test healing item functionality."""
    effect = ItemEffect(type=ItemType.HEALING, value=30)
    potion = Item("Potion", "Restores 30 HP", effect, 100)
    
    initial_hp = test_pokemon.current_hp
    assert potion.can_use(test_pokemon) is True
    assert potion.use(test_pokemon) is True
    assert test_pokemon.current_hp == min(initial_hp + 30, test_pokemon.stats.hp)

def test_healing_item_at_full_hp(test_pokemon):
    """Test healing item when Pokemon is at full HP."""
    effect = ItemEffect(type=ItemType.HEALING, value=30)
    potion = Item("Potion", "Restores 30 HP", effect, 100)
    
    test_pokemon.current_hp = test_pokemon.stats.hp
    assert potion.can_use(test_pokemon) is False
    assert potion.use(test_pokemon) is False
    assert test_pokemon.current_hp == test_pokemon.stats.hp

def test_pp_restore_item(test_pokemon):
    """Test PP restoring item functionality."""
    effect = ItemEffect(type=ItemType.PP, value=10)
    ether = Item("Ether", "Restores 10 PP", effect, 200)
    
    initial_pp = test_pokemon.moves[0].current_pp
    assert ether.can_use(test_pokemon) is True
    assert ether.use(test_pokemon) is True
    assert test_pokemon.moves[0].current_pp == min(initial_pp + 10, test_pokemon.moves[0].max_pp)

def test_pp_restore_at_max(test_pokemon):
    """Test PP restoring item when moves are at max PP."""
    effect = ItemEffect(type=ItemType.PP, value=10)
    ether = Item("Ether", "Restores 10 PP", effect, 200)
    
    test_pokemon.moves[0].current_pp = test_pokemon.moves[0].max_pp
    assert ether.can_use(test_pokemon) is False
    assert ether.use(test_pokemon) is False
    assert test_pokemon.moves[0].current_pp == test_pokemon.moves[0].max_pp

def test_pokeball_in_trainer_battle():
    """Test Pokeball usage in trainer battles."""
    effect = ItemEffect(
        type=ItemType.POKEBALL,
        value=1,
        conditions={"is_trainer_battle": True}
    )
    pokeball = Item("Poke Ball", "Catches wild Pokemon", effect, 200)
    
    # Create a dummy target that simulates a trainer battle context
    class DummyTarget:
        pass
    
    target = DummyTarget()
    assert pokeball.can_use(target) is False
    assert pokeball.use(target) is False

def test_status_cure_item(test_pokemon):
    """Test status condition curing item."""
    effect = ItemEffect(type=ItemType.STATUS, value=1)
    antidote = Item("Antidote", "Cures status conditions", effect, 100)
    
    # Simulate a status condition
    test_pokemon.status = "POISON"
    assert antidote.can_use(test_pokemon) is True
    assert antidote.use(test_pokemon) is True
    assert test_pokemon.status is None

def test_status_cure_no_status(test_pokemon):
    """Test status cure item when no status condition exists."""
    effect = ItemEffect(type=ItemType.STATUS, value=1)
    antidote = Item("Antidote", "Cures status conditions", effect, 100)
    
    test_pokemon.status = None
    assert antidote.can_use(test_pokemon) is False
    assert antidote.use(test_pokemon) is False
    assert test_pokemon.status is None

def test_boost_item():
    """Test stat boost item."""
    effect = ItemEffect(type=ItemType.BOOST, value=1, duration=5)
    x_attack = Item("X Attack", "Boosts Attack", effect, 500)
    
    # Boost items always return True for can_use and use
    # Actual boost effect is handled by battle system
    assert x_attack.can_use(None) is True
    assert x_attack.use(None) is True

def test_item_string_representation():
    """Test item string representation."""
    effect = ItemEffect(type=ItemType.HEALING, value=20)
    potion = Item("Potion", "Restores 20 HP", effect, 100)
    
    assert str(potion) == "Potion - Restores 20 HP"

def test_item_with_no_conditions():
    """Test item with no special conditions."""
    effect = ItemEffect(type=ItemType.HEALING, value=20)
    potion = Item("Potion", "Restores 20 HP", effect, 100)
    
    # Should always be usable on valid targets when no conditions are set
    assert potion.can_use("dummy target") is True

def test_invalid_target():
    """Test using item on invalid target."""
    effect = ItemEffect(type=ItemType.HEALING, value=20)
    potion = Item("Potion", "Restores 20 HP", effect, 100)
    
    # Using on target without required attributes
    class InvalidTarget:
        pass
    
    target = InvalidTarget()
    assert potion.use(target) is True  # Should still return True but do nothing
