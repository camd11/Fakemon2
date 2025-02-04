"""Tests for BattleView UI component."""

import pytest
from unittest.mock import Mock, patch, create_autospec, call
from rich.console import Console
from rich.panel import Panel
from rich.table import Table, Column
from rich.text import Text
from rich.layout import Layout as RichLayout
from src.ui.battle_view import BattleView
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type
from src.core.move import Move, MoveCategory

# Create a Layout class that mimics rich.layout.Layout's behavior
class Layout:
    def __init__(self, renderable=None, name=None, size=None):
        self.renderable = renderable
        self.name = name
        self.size = size
        self._children = []
        
    def split_column(self, *layouts):
        self._children.extend(layouts)
        
    def split_row(self, *layouts):
        self._children.extend(layouts)
        
    def update(self, renderable):
        self.renderable = renderable
        
    def __getitem__(self, key):
        return self
        
    def __str__(self):
        return str(self.renderable) if self.renderable else ""

# Create a Table class that mimics rich.table.Table's behavior
class MockTable(Table):
    def __init__(self, *args, **kwargs):
        self.show_header = kwargs.get('show_header', True)
        self.show_edge = kwargs.get('show_edge', True)
        self.pad_edge = kwargs.get('pad_edge', True)
        self.title = kwargs.get('title')
        self.columns = []
        self.rows = []
        self._rendered_content = []
        
    def add_column(self, header, style=None, justify=None):
        self.columns.append({
            'header': header,
            'style': style,
            'justify': justify
        })
        
    def add_row(self, *args):
        self.rows.append(args)
        if all(isinstance(arg, Text) for arg in args):
            # Join each Text object's _text list into a string
            texts = [" ".join(arg._text) for arg in args]
            self._rendered_content.append(" ".join(texts))
        else:
            self._rendered_content.append(f"{args[0]}: {args[1]}")
        
    def __str__(self):
        if not self._rendered_content:
            return ""
        return "\n".join(self._rendered_content)
        
    def __repr__(self):
        return self.__str__()

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

@pytest.fixture
def dual_type_pokemon(test_pokemon):
    """Create a Pokemon with dual types for testing."""
    test_pokemon.types = (Type.FIRE, Type.FLYING)
    return test_pokemon

@pytest.fixture
def multi_move_pokemon(test_pokemon):
    """Create a Pokemon with multiple moves."""
    test_pokemon.moves = [
        Move(name="Move 1", type_=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35),
        Move(name="Move 2", type_=Type.FIRE, category=MoveCategory.SPECIAL, power=90, accuracy=85, pp=15),
        Move(name="Move 3", type_=Type.WATER, category=MoveCategory.STATUS, power=0, accuracy=100, pp=20)
    ]
    return test_pokemon

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

@patch('src.ui.battle_view.Table', MockTable)
def test_pokemon_panel_creation(battle_view, test_pokemon):
    """Test Pokemon information panel creation."""
    panel = battle_view._create_pokemon_panel(test_pokemon, "Test")
    
    assert isinstance(panel, Panel)
    content = str(panel.renderable)
    assert test_pokemon.name in content
    assert str(test_pokemon.level) in content
    assert str(test_pokemon.current_hp) in content
    assert str(test_pokemon.stats.hp) in content

@patch('src.ui.battle_view.Table', MockTable)
def test_pokemon_panel_with_dual_types(battle_view, dual_type_pokemon):
    """Test Pokemon panel rendering with dual types."""
    panel = battle_view._create_pokemon_panel(dual_type_pokemon, "Test")
    content = str(panel.renderable)
    
    assert "Types: FIRE, FLYING" in content
    assert all(t.name in content for t in dual_type_pokemon.types)

@patch('src.ui.battle_view.Table', MockTable)
def test_pokemon_panel_move_table(battle_view, multi_move_pokemon):
    """Test move table rendering in Pokemon panel."""
    panel = battle_view._create_pokemon_panel(multi_move_pokemon, "Test")
    content = str(panel.renderable)
    
    # Verify all moves are displayed with PP
    for move in multi_move_pokemon.moves:
        assert f"• {move.name}" in content
        assert f"PP: {move.current_pp}/{move.max_pp}" in content

@patch('src.ui.battle_view.Layout')
def test_render_battle(mock_layout, battle_view, test_pokemon):
    """Test battle state rendering."""
    # Setup mock layout with proper split behavior
    layout_instance = Mock(spec=Layout)
    layout_instance.split_column = Mock()
    layout_instance.split_row = Mock()
    layout_instance.__getitem__ = Mock(return_value=layout_instance)
    layout_instance.update = Mock()
    mock_layout.return_value = layout_instance
    
    messages = ["Test message 1", "Test message 2"]
    battle_view.render_battle(test_pokemon, test_pokemon, messages)
    
    # Verify layout creation and message handling
    layout_instance.split_column.assert_called_once()
    assert len(battle_view._message_history) == len(messages)
    assert all(msg in battle_view._message_history for msg in messages)

def test_message_history_management(battle_view, test_pokemon):
    """Test battle message history management."""
    messages = [f"Message {i}" for i in range(6)]
    battle_view.render_battle(test_pokemon, test_pokemon, messages)
    
    assert len(battle_view._message_history) == 5  # Max 5 messages
    assert "Message 5" in battle_view._message_history
    assert "Message 0" not in battle_view._message_history

def test_message_history_less_than_max(battle_view, test_pokemon):
    """Test message history with fewer than max messages."""
    messages = ["Message 1", "Message 2"]
    battle_view.render_battle(test_pokemon, test_pokemon, messages)
    
    assert len(battle_view._message_history) == 2
    assert all(msg in battle_view._message_history for msg in messages)

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

@patch('src.ui.battle_view.Table', MockTable)
def test_game_over_screen(battle_view):
    """Test game over screen rendering."""
    stats = {
        "battles_won": 10,
        "max_level": 15
    }
    
    battle_view.show_game_over(stats)
    
    # Verify game over message and stats table setup
    calls = battle_view.console.print.call_args_list
    assert any("Game Over" in str(call) for call in calls)
    
    # Find the stats table in the output
    table_content = None
    for args in calls:
        if isinstance(args[0][0], MockTable):
            table_content = str(args[0][0])
            break
    
    assert table_content is not None
    assert "Battles Won: 10" in table_content
    assert "Max Level: 15" in table_content

def test_game_over_no_stats(battle_view):
    """Test game over screen without stats."""
    battle_view.show_game_over(None)
    
    calls = [str(call[0][0]) for call in battle_view.console.print.call_args_list]
    assert any("Game Over" in call for call in calls)
    assert any("Press ENTER" in call for call in calls)

@patch('src.ui.battle_view.Table', MockTable)
def test_victory_screen(battle_view):
    """Test victory screen rendering."""
    stats = {
        "battles_won": 200,
        "pokemon_caught": 20
    }
    
    battle_view.show_victory(stats)
    
    # Verify victory message and stats table setup
    calls = battle_view.console.print.call_args_list
    assert any("Congratulations" in str(call) for call in calls)
    
    # Find the stats table in the output
    table_content = None
    for args in calls:
        if isinstance(args[0][0], MockTable):
            table_content = str(args[0][0])
            break
    
    assert table_content is not None
    assert "Battles Won: 200" in table_content
    assert "Pokemon Caught: 20" in table_content

def test_victory_no_stats(battle_view):
    """Test victory screen without stats."""
    battle_view.show_victory(None)
    
    calls = [str(call[0][0]) for call in battle_view.console.print.call_args_list]
    assert any("Congratulations" in call for call in calls)
    assert any("Press ENTER" in call for call in calls)

def test_clear_screen(battle_view):
    """Test screen clearing."""
    battle_view.clear_screen()
    battle_view.console.clear.assert_called_once()

@patch('src.ui.battle_view.Layout')
def test_battle_layout_creation(mock_layout, battle_view, test_pokemon):
    """Test battle screen layout creation."""
    # Setup mock layout with proper split behavior
    layout_instance = Mock(spec=Layout)
    layout_instance.split_column = Mock()
    layout_instance.split_row = Mock()
    layout_instance.__getitem__ = Mock(return_value=layout_instance)
    layout_instance.update = Mock()
    mock_layout.return_value = layout_instance
    
    battle_view.render_battle(test_pokemon, test_pokemon)
    
    # Verify layout structure
    layout_instance.split_column.assert_called_once()

@patch('src.ui.battle_view.Layout')
def test_battle_action_menu(mock_layout, battle_view, test_pokemon):
    """Test battle action menu content."""
    # Setup mock layout with proper split behavior
    layout_instance = Mock(spec=Layout)
    layout_instance.split_column = Mock()
    layout_instance.split_row = Mock()
    layout_instance.__getitem__ = Mock(return_value=layout_instance)
    layout_instance.update = Mock()
    mock_layout.return_value = layout_instance
    
    def mock_update(panel):
        if isinstance(panel, Panel) and "Actions:" in str(panel.renderable):
            content = str(panel.renderable)
            assert "1. Fight" in content
            assert "2. Pokemon" in content
            assert "3. Item" in content
            assert "4. Run" in content
    
    layout_instance.update = Mock(side_effect=mock_update)
    
    battle_view.render_battle(test_pokemon, test_pokemon)
    
    # Verify action menu was updated
    assert layout_instance.update.called
