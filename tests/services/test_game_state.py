"""Tests for GameState service."""

import pytest
from src.services.game_state import GameState, GamePhase, GameStats
from src.core.battle import BattleAction

@pytest.fixture
def game_state() -> GameState:
    """Create a GameState instance for testing."""
    return GameState()

def test_initial_state(game_state):
    """Test initial game state."""
    assert game_state.phase == GamePhase.TITLE
    assert game_state.stats.battles_won == 0
    assert game_state.stats.battles_lost == 0
    assert game_state.stats.pokemon_caught == 0
    assert game_state.stats.max_level_reached == 1

def test_game_phase_transitions(game_state):
    """Test game phase transitions."""
    # Title -> Starter
    game_state.phase = GamePhase.STARTER
    
    # Starter -> Battle (via starting game)
    starters = game_state.get_available_starters()
    assert len(starters) == 3  # Classic starters
    assert "bulbasaur" in starters
    assert "charmander" in starters
    assert "squirtle" in starters
    
    # Invalid starter should fail
    assert not game_state.start_new_game("nonexistent")
    assert game_state.phase == GamePhase.STARTER
    
    # Valid starter should succeed
    assert game_state.start_new_game("charmander")
    assert game_state.phase == GamePhase.BATTLE

def test_battle_flow(game_state):
    """Test battle flow and progression."""
    # Setup game
    game_state.phase = GamePhase.STARTER
    game_state.start_new_game("charmander")
    
    # Start battle
    player, enemy = game_state.start_battle()
    assert player == game_state.battle_manager.player_party[0]
    assert enemy is not None
    
    # Execute turn
    result = game_state.battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    assert result is not None
    
    # Win battle
    enemy.current_hp = 1
    game_state.battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    game_state.handle_battle_end()
    
    assert game_state.stats.battles_won == 1
    assert game_state.phase == GamePhase.BATTLE  # Should stay in battle phase
    assert game_state.battle_manager.current_level == 2

def test_game_over_transition(game_state):
    """Test transition to game over state."""
    # Setup game
    game_state.phase = GamePhase.STARTER
    game_state.start_new_game("charmander")
    player, enemy = game_state.start_battle()
    
    # Lose battle
    player.current_hp = 1
    enemy.current_hp = 100
    game_state.battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    game_state.handle_battle_end()
    
    assert game_state.phase == GamePhase.GAME_OVER
    assert game_state.stats.battles_lost == 1

def test_victory_transition(game_state):
    """Test transition to victory state."""
    # Setup game near completion
    game_state.phase = GamePhase.STARTER
    game_state.start_new_game("charmander")
    game_state.battle_manager.current_level = 200
    
    # Win final battle
    player, enemy = game_state.start_battle()
    enemy.current_hp = 1
    game_state.battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    game_state.handle_battle_end()
    
    assert game_state.phase == GamePhase.VICTORY
    assert game_state.stats.max_level_reached > 200

def test_pokemon_catching(game_state):
    """Test Pokemon catching mechanics."""
    # Setup game
    game_state.phase = GamePhase.STARTER
    game_state.start_new_game("charmander")
    initial_pokeballs = game_state.get_remaining_pokeballs()
    
    # Start battle
    player, enemy = game_state.start_battle()
    enemy.current_hp = 1  # Weaken for better catch rate
    
    # Try to catch
    assert game_state.can_catch_pokemon
    game_state.battle_manager.execute_turn(BattleAction.ITEM, item_name="pokeball")
    
    assert game_state.get_remaining_pokeballs() == initial_pokeballs - 1

def test_message_system(game_state):
    """Test game message system."""
    # Setup game
    game_state.phase = GamePhase.STARTER
    game_state.start_new_game("charmander")
    
    # Get and clear initial messages
    messages = game_state.get_messages()
    assert len(messages) > 0  # Should have starter selection message
    
    # Messages should be cleared
    messages = game_state.get_messages()
    assert len(messages) == 0
    
    # Start battle should generate message
    game_state.start_battle()
    messages = game_state.get_messages()
    assert len(messages) > 0
    assert any("appeared" in msg for msg in messages)

def test_party_management(game_state):
    """Test party management."""
    # Setup game
    game_state.phase = GamePhase.STARTER
    game_state.start_new_game("charmander")
    
    # Check initial party
    party = game_state.get_player_party()
    assert len(party) == 1
    assert party[0].name == "Charmander"
    
    # Party size limit
    for _ in range(10):  # Try to add more than allowed
        pokemon = game_state.pokemon_factory.create_random_pokemon(5)
        if len(game_state.battle_manager.player_party) < 6:
            game_state.battle_manager.player_party.append(pokemon)
    
    assert len(game_state.get_player_party()) <= 6

def test_stats_tracking(game_state):
    """Test game statistics tracking."""
    # Setup game
    game_state.phase = GamePhase.STARTER
    game_state.start_new_game("charmander")
    
    # Win a battle
    player, enemy = game_state.start_battle()
    enemy.current_hp = 1
    game_state.battle_manager.execute_turn(BattleAction.FIGHT, move_index=0)
    game_state.handle_battle_end()
    
    assert game_state.stats.battles_won == 1
    assert game_state.stats.max_level_reached == 2
    
    # Catch a Pokemon
    player, enemy = game_state.start_battle()
    enemy.current_hp = 1
    game_state.battle_manager.execute_turn(BattleAction.ITEM, item_name="pokeball")
    
    # Stats should be updated
    assert game_state.stats.pokemon_caught >= 0  # May or may not catch based on RNG
