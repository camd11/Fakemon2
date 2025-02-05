"""Tests for item usage in battles."""

import pytest
from src.core.battle import Battle, BattleAction, TurnResult
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory
from src.core.item import Item, ItemType, ItemEffect

@pytest.fixture
def type_chart():
    """Create a type chart for testing."""
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0},
        "fire": {"fire": 0.5},
        "water": {"water": 0.5}
    })
    return chart

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon for battle."""
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

@pytest.fixture
def battle(test_pokemon, type_chart):
    """Create a battle instance for testing."""
    player_pokemon = test_pokemon
    enemy_pokemon = Pokemon(
        name="Enemy Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        moves=[
            Move(
                name="Enemy Move",
                type_=Type.NORMAL,
                category=MoveCategory.PHYSICAL,
                power=40,
                accuracy=100,
                pp=35
            )
        ]
    )
    return Battle(player_pokemon, enemy_pokemon, type_chart)

def test_use_healing_item(battle):
    """Test using a healing item in battle."""
    initial_hp = battle.player_pokemon.current_hp
    potion = Item(
        name="Potion",
        description="Restores 20 HP",
        effect=ItemEffect(type=ItemType.HEALING, value=20),
        price=100
    )
    
    result = battle.use_item(potion, battle.player_pokemon)
    assert result.success is True
    assert result.messages == [f"{battle.player_pokemon.name} was healed for 20 HP!"]
    assert battle.player_pokemon.current_hp == initial_hp + 20

def test_use_pp_restore_item(battle):
    """Test using a PP restore item in battle."""
    initial_pp = battle.player_pokemon.moves[0].current_pp
    ether = Item(
        name="Ether",
        description="Restores 10 PP",
        effect=ItemEffect(type=ItemType.PP, value=10),
        price=200
    )
    
    result = battle.use_item(ether, battle.player_pokemon)
    assert result.success is True
    assert result.messages == [f"{battle.player_pokemon.name}'s move PP was restored!"]
    assert battle.player_pokemon.moves[0].current_pp == initial_pp + 10

def test_use_status_cure_item(battle):
    """Test using a status cure item in battle."""
    battle.player_pokemon.status = "POISON"
    antidote = Item(
        name="Antidote",
        description="Cures poison",
        effect=ItemEffect(type=ItemType.STATUS, value=1),
        price=100
    )
    
    result = battle.use_item(antidote, battle.player_pokemon)
    assert result.success is True
    assert result.messages == [f"{battle.player_pokemon.name} was cured of poison!"]
    assert battle.player_pokemon.status is None

def test_use_stat_boost_item(battle):
    """Test using a stat boost item in battle."""
    x_attack = Item(
        name="X Attack",
        description="Raises Attack",
        effect=ItemEffect(
            type=ItemType.BOOST,
            value=1,
            duration=5,
            conditions={"Attack": 1}
        ),
        price=500
    )
    
    result = battle.use_item(x_attack, battle.player_pokemon)
    assert result.success is True
    assert result.messages == [f"{battle.player_pokemon.name}'s Attack rose!"]
    assert battle.player_pokemon.get_stat_multiplier("attack") > 1.0

def test_use_pokeball_in_trainer_battle(battle):
    """Test using a Pokeball in a trainer battle."""
    pokeball = Item(
        name="Poke Ball",
        description="Catches wild Pokemon",
        effect=ItemEffect(
            type=ItemType.POKEBALL,
            value=1,
            conditions={"is_trainer_battle": True}
        ),
        price=200
    )
    
    result = battle.use_item(pokeball, battle.enemy_pokemon)
    assert result.success is False
    assert result.messages == ["Can't use Poke Ball in a trainer battle!"]

def test_use_item_on_fainted_pokemon(battle):
    """Test using an item on a fainted Pokemon."""
    battle.player_pokemon.current_hp = 0
    potion = Item(
        name="Potion",
        description="Restores 20 HP",
        effect=ItemEffect(type=ItemType.HEALING, value=20),
        price=100
    )
    
    result = battle.use_item(potion, battle.player_pokemon)
    assert result.success is False
    assert result.messages == ["Can't use items on fainted Pokemon!"]

def test_use_item_at_full_hp(battle):
    """Test using a healing item at full HP."""
    battle.player_pokemon.current_hp = battle.player_pokemon.stats.hp
    potion = Item(
        name="Potion",
        description="Restores 20 HP",
        effect=ItemEffect(type=ItemType.HEALING, value=20),
        price=100
    )
    
    result = battle.use_item(potion, battle.player_pokemon)
    assert result.success is False
    assert result.messages == [f"{battle.player_pokemon.name} is already at full HP!"]
