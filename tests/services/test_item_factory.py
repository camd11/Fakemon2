"""Tests for the ItemFactory service."""

import pytest
from src.services.item_factory import ItemFactory
from src.core.item import Item, ItemType, ItemEffect

@pytest.fixture
def item_factory():
    """Create an ItemFactory instance for testing."""
    return ItemFactory()

def test_item_factory_initialization(item_factory):
    """Test ItemFactory initialization and data loading."""
    assert item_factory._items_data is not None
    assert len(item_factory._items_data) > 0

def test_create_healing_item(item_factory):
    """Test creating a healing item."""
    potion = item_factory.create_item("potion")
    
    assert isinstance(potion, Item)
    assert potion.name == "Potion"
    assert potion.effect.type == ItemType.HEALING
    assert potion.effect.value == 20
    assert potion.price == 300
    assert potion.single_use is True

def test_create_pp_restore_item(item_factory):
    """Test creating a PP restore item."""
    ether = item_factory.create_item("ether")
    
    assert isinstance(ether, Item)
    assert ether.name == "Ether"
    assert ether.effect.type == ItemType.PP
    assert ether.effect.value == 10
    assert ether.price == 1200

def test_create_status_cure_item(item_factory):
    """Test creating a status cure item."""
    antidote = item_factory.create_item("antidote")
    
    assert isinstance(antidote, Item)
    assert antidote.name == "Antidote"
    assert antidote.effect.type == ItemType.STATUS
    assert antidote.effect.value == 1
    assert antidote.price == 100

def test_create_boost_item(item_factory):
    """Test creating a stat boost item."""
    x_attack = item_factory.create_item("x_attack")
    
    assert isinstance(x_attack, Item)
    assert x_attack.name == "X Attack"
    assert x_attack.effect.type == ItemType.BOOST
    assert x_attack.effect.value == 1
    assert x_attack.effect.duration == 5
    assert x_attack.price == 500

def test_create_pokeball(item_factory):
    """Test creating a Pokeball."""
    pokeball = item_factory.create_item("poke_ball")
    
    assert isinstance(pokeball, Item)
    assert pokeball.name == "Poke Ball"
    assert pokeball.effect.type == ItemType.POKEBALL
    assert pokeball.effect.value == 1
    assert pokeball.effect.conditions == {"is_trainer_battle": False}
    assert pokeball.price == 200

def test_create_nonexistent_item(item_factory):
    """Test creating an item that doesn't exist."""
    item = item_factory.create_item("nonexistent_item")
    assert item is None

def test_get_all_items(item_factory):
    """Test getting all available items."""
    items = item_factory.get_all_items()
    
    assert len(items) > 0
    assert all(isinstance(item, Item) for item in items)
    assert any(item.name == "Potion" for item in items)
    assert any(item.name == "Ultra Ball" for item in items)

def test_get_items_by_type(item_factory):
    """Test getting items filtered by type."""
    healing_items = item_factory.get_items_by_type(ItemType.HEALING)
    
    assert len(healing_items) > 0
    assert all(item.effect.type == ItemType.HEALING for item in healing_items)
    assert any(item.name == "Potion" for item in healing_items)
    assert any(item.name == "Super Potion" for item in healing_items)

def test_get_items_by_max_price(item_factory):
    """Test getting items filtered by maximum price."""
    cheap_items = item_factory.get_items_by_max_price(300)
    
    assert len(cheap_items) > 0
    assert all(item.price <= 300 for item in cheap_items)
    assert any(item.name == "Antidote" for item in cheap_items)

def test_get_purchasable_items(item_factory):
    """Test getting items that can be purchased."""
    money = 1000
    items = item_factory.get_purchasable_items(money)
    
    assert len(items) > 0
    assert all(item.price <= money for item in items)
    assert any(item.name == "Potion" for item in items)
    assert not any(item.price > money for item in items)

def test_invalid_data_dir():
    """Test initialization with invalid data directory."""
    with pytest.raises(FileNotFoundError):
        ItemFactory(data_dir="nonexistent_dir")

def test_data_validation(item_factory):
    """Test that all loaded items have required fields."""
    items = item_factory.get_all_items()
    
    for item in items:
        assert item.name
        assert item.description
        assert item.effect.type in ItemType
        assert isinstance(item.effect.value, (int, float))
        assert isinstance(item.price, int)
        assert isinstance(item.single_use, bool)
