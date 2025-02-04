"""Tests for BattleManager service."""

import pytest
from src.services.battle_manager import BattleManager
from src.services.pokemon_factory import PokemonFactory
from src.core.battle import BattleAction
from src.core.pokemon import Pokemon

@pytest.fixture
def battle_manager() -> BattleManager:
    """Create a BattleManager instance for testing."""
    factory = PokemonFactory()
    return BattleManager(factory)

def test_game_initialization(battle_manager):
    """Test starting a new game."""
    # Start with invalid starter
    assert not battle_manager.start_game("nonexistent")
    
    # Start with valid starter
    assert battle_manager.start_game("charmander")
    assert len(battle_manager.player_party) == 1
    assert battle_manager.player_party[0].name == "Charmander"
    assert battle_manager.pokeballs == 5
    assert battle_manager.current_level == 1

def test_battle_start(battle_manager):
    """Test starting a battle."""
    battle_manager.start_game("charmander")
    player, enemy = battle_manager.start_battle()
    
    assert player == battle_manager.player_party[0]
    assert enemy == battle_manager.current_battle.enemy_pokemon
    assert enemy.level == 5  # First enemy should be level 5

def test_battle_progression(battle_manager):
    """Test battle level progression."""
    battle_manager.start_game("charmander")
    
    # First battle
    player, enemy = battle_manager.start_battle()
    assert enemy.level == 5
    
    # Win battle and progress
    enemy.current_hp = 1
    result = battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    assert result is not None
    
    won, messages = battle_manager.handle_battle_end()
    assert won
    assert battle_manager.current_level == 2
    
    # Next battle should have higher level enemy
    player, enemy = battle_manager.start_battle()
    assert enemy.level == 6

def test_catching_mechanics(battle_manager):
    """Test Pokemon catching mechanics."""
    battle_manager.start_game("charmander")
    initial_pokeballs = battle_manager.pokeballs
    
    # Start battle
    player, enemy = battle_manager.start_battle()
    
    # Weaken enemy
    enemy.current_hp = 1
    
    # Try to catch
    result = battle_manager.execute_turn(BattleAction.ITEM, item_name="pokeball")
    assert result is not None
    assert battle_manager.pokeballs == initial_pokeballs - 1

def test_party_management(battle_manager):
    """Test party size limits and management."""
    battle_manager.start_game("charmander")
    
    # Add Pokemon to fill party
    for _ in range(5):  # Already have starter, so add 5 more
        pokemon = battle_manager.pokemon_factory.create_random_pokemon(5)
        if len(battle_manager.player_party) < 6:
            battle_manager.player_party.append(pokemon)
    
    assert len(battle_manager.player_party) == 6
    
    # Start battle and try to catch (should fail due to full party)
    player, enemy = battle_manager.start_battle()
    enemy.current_hp = 1
    result = battle_manager.execute_turn(BattleAction.ITEM, item_name="pokeball")
    
    # Even if catch rate would succeed, Pokemon shouldn't be added to full party
    assert len(battle_manager.player_party) == 6

def test_game_completion(battle_manager):
    """Test game completion conditions."""
    battle_manager.start_game("charmander")
    
    # Set to last level
    battle_manager.current_level = 200
    player, enemy = battle_manager.start_battle()
    
    # Win final battle
    enemy.current_hp = 1
    battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    won, messages = battle_manager.handle_battle_end()
    
    assert won
    assert battle_manager.game_completed
    assert battle_manager.current_level > 200

def test_battle_actions(battle_manager):
    """Test different battle actions."""
    battle_manager.start_game("charmander")
    player, enemy = battle_manager.start_battle()
    
    # Test fight action
    result = battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    assert result is not None
    assert result.damage_dealt > 0
    
    # Test item action (use Pokeball)
    result = battle_manager.execute_turn(BattleAction.ITEM, item_name="pokeball")
    assert result is not None
    
    # Test run action (should fail in roguelike mode)
    result = battle_manager.execute_turn(BattleAction.RUN)
    assert result is None

def test_invalid_actions(battle_manager):
    """Test handling of invalid battle actions."""
    battle_manager.start_game("charmander")
    player, enemy = battle_manager.start_battle()
    
    # Invalid move index
    result = battle_manager.execute_turn(BattleAction.FIGHT, move_index=10)
    assert result is None
    
    # Invalid item
    result = battle_manager.execute_turn(BattleAction.ITEM, item_name="invalid_item")
    assert result is None
    
    # No pokeballs left
    battle_manager.pokeballs = 0
    result = battle_manager.execute_turn(BattleAction.ITEM, item_name="pokeball")
    assert result is None

def test_battle_end_handling(battle_manager):
    """Test battle end handling and rewards."""
    battle_manager.start_game("charmander")
    initial_level = battle_manager.current_level
    
    # Start and win battle
    player, enemy = battle_manager.start_battle()
    enemy.current_hp = 1
    battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    won, messages = battle_manager.handle_battle_end()
    
    assert won
    assert battle_manager.current_level == initial_level + 1
    assert battle_manager.current_battle is None
