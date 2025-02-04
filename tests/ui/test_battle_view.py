"""Tests for BattleView UI component."""

import builtins
import pytest
from unittest.mock import Mock, patch, call, create_autospec, ANY
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from src.ui.battle_view import BattleView
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type
from src.core.move import Move, MoveCategory

@pytest.fixture
def mock_console():
    """Create a mock console for testing."""
    return Mock(spec=Console)

@pytest.fixture
def battle_view(mock_console):
    """Create a BattleView instance with mocked console."""
    view = BattleView()
    view.console = mock_console
    return view

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon for UI rendering."""
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
    
    return Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=stats,
        level=50,
        moves=moves
    )

def test_show_title_screen(battle_view):
    """Test title screen rendering."""
    battle_view.show_title_screen()
    
    battle_view.console.print.assert_called_once()
    args = battle_view.console.print.call_args[0][0]
    assert "FAKEMON 2" in args
    assert "Press ENTER to start" in args

def test_show_starter_selection(battle_view):
    """Test starter selection screen rendering."""
    starters = ["bulbasaur", "charmander", "squirtle"]
    battle_view.show_starter_selection(starters)
    
    # Verify each starter is displayed
    calls = battle_view.console.print.call_args_list
    assert len(calls) >= len(starters)
    for starter in starters:
        assert any(starter.title() in str(call) for call in calls)

def test_pokemon_panel_creation(battle_view, test_pokemon):
    """Test Pokemon information panel creation."""
    panel = battle_view._create_pokemon_panel(test_pokemon, "Test")
    
    assert isinstance(panel, Panel)
    content = panel.renderable
    assert test_pokemon.name in str(content)
    assert str(test_pokemon.level) in str(content)
    assert str(test_pokemon.current_hp) in str(content)
    assert str(test_pokemon.stats.hp) in str(content)

@patch('builtins.isinstance', return_value=True)
@patch('rich.layout.Layout')
def test_render_battle(mock_layout, mock_isinstance, battle_view, test_pokemon):
    """Test battle state rendering."""
    # Setup mock layout
    mock_layout_instance = Mock()
    mock_layout.return_value = mock_layout_instance
    mock_layout_instance.split_column = Mock()
    mock_layout_instance.split_row = Mock()
    
    messages = ["Test message 1", "Test message 2"]
    battle_view.render_battle(test_pokemon, test_pokemon, messages)
    
    # Verify layout creation
    mock_layout.assert_called()
    mock_layout_instance.split_column.assert_called()
    
    # Verify message handling
    assert len(battle_view._message_history) == len(messages)
    assert all(msg in battle_view._message_history for msg in messages)

def test_message_history_management(battle_view, test_pokemon):
    """Test battle message history management."""
    messages = [f"Message {i}" for i in range(6)]
    battle_view.render_battle(test_pokemon, test_pokemon, messages)
    
    assert len(battle_view._message_history) == 5  # Max 5 messages
    assert "Message 5" in battle_view._message_history
    assert "Message 0" not in battle_view._message_history

def test_hp_bar_rendering(battle_view, test_pokemon):
    """Test HP bar rendering at different health levels."""
    # Test full health
    panel = battle_view._create_pokemon_panel(test_pokemon, "Test")
    assert panel.border_style == "green"  # Full health = green border
    assert "=" * 20 in str(panel.renderable)  # Full HP bar
    
    # Test low health
    test_pokemon.current_hp = test_pokemon.stats.hp // 4
    panel = battle_view._create_pokemon_panel(test_pokemon, "Test")
    assert panel.border_style == "red"  # Low health = red border

@patch('rich.table.Table')
def test_game_over_screen(mock_table, battle_view):
    """Test game over screen rendering."""
    # Setup mock table
    mock_table_instance = Mock()
    mock_table_instance.add_column = Mock()
    mock_table_instance.add_row = Mock()
    mock_table.return_value = mock_table_instance
    
    stats = {
        "battles_won": 10,
        "max_level": 15
    }
    
    battle_view.show_game_over(stats)
    
    # Verify game over message and stats
    calls = [str(call[0][0]) for call in battle_view.console.print.call_args_list]
    assert any("Game Over" in call for call in calls)
    assert any("Battles Won: 10" in str(battle_view.console.print.call_args_list) for call in calls)
    assert any("Max Level: 15" in str(battle_view.console.print.call_args_list) for call in calls)

def test_victory_screen(battle_view):
    """Test victory screen rendering."""
    stats = {
        "battles_won": 200,
        "pokemon_caught": 20
    }
    
    battle_view.show_victory(stats)
    
    # Verify victory message and stats
    calls = [str(call[0][0]) for call in battle_view.console.print.call_args_list]
    assert any("Congratulations" in call for call in calls)
    assert any("200" in call for call in calls)
    assert any("20" in call for call in calls)

def test_clear_screen(battle_view):
    """Test screen clearing."""
    battle_view.clear_screen()
    battle_view.console.clear.assert_called_once()

@patch('builtins.isinstance', return_value=True)
@patch('rich.layout.Layout')
def test_battle_layout_creation(mock_layout, mock_isinstance, battle_view, test_pokemon):
    """Test battle screen layout creation."""
    # Setup mock layout
    mock_layout_instance = Mock()
    mock_layout_instance.split_column = Mock()
    mock_layout_instance.split_row = Mock()
    mock_layout.return_value = mock_layout_instance
    
    battle_view.render_battle(test_pokemon, test_pokemon)
    
    # Verify layout structure
    mock_layout.assert_called()
    mock_layout_instance.split_column.assert_called_once()
