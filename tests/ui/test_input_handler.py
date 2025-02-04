"""Tests for InputHandler UI component."""

import pytest
from unittest.mock import patch
from src.ui.input_handler import InputHandler
from src.core.battle import BattleAction

def test_get_enter():
    """Test enter key detection."""
    with patch('builtins.input', return_value=''):
        assert InputHandler.get_enter() is True

def test_get_starter_choice_valid():
    """Test valid starter selection."""
    with patch('builtins.input', return_value='2'):
        choice = InputHandler.get_starter_choice(3)
        assert choice == 1  # 0-based index

def test_get_starter_choice_invalid():
    """Test invalid starter selections."""
    # Test out of range choice
    with patch('builtins.input', return_value='4'):
        assert InputHandler.get_starter_choice(3) is None
        
    # Test non-numeric input
    with patch('builtins.input', return_value='invalid'):
        assert InputHandler.get_starter_choice(3) is None
        
    # Test zero (invalid) input
    with patch('builtins.input', return_value='0'):
        assert InputHandler.get_starter_choice(3) is None

def test_get_battle_action_fight():
    """Test fight action selection."""
    # Mock input sequence: choose fight (1) then move 1
    with patch('builtins.input', side_effect=['1', '1']):
        action, kwargs = InputHandler.get_battle_action()
        assert action == BattleAction.FIGHT
        assert kwargs == {"move_index": 0}

def test_get_battle_action_pokemon():
    """Test Pokemon switch action selection."""
    with patch('builtins.input', return_value='2'):
        result = InputHandler.get_battle_action()
        assert result is None  # Not implemented yet

def test_get_battle_action_item():
    """Test item action selection."""
    # Mock input sequence: choose item (3) then pokeball (1)
    with patch('builtins.input', side_effect=['3', '1']):
        action, kwargs = InputHandler.get_battle_action()
        assert action == BattleAction.ITEM
        assert kwargs == {"item_name": "pokeball"}

def test_get_battle_action_run():
    """Test run action selection."""
    with patch('builtins.input', return_value='4'):
        action, kwargs = InputHandler.get_battle_action()
        assert action == BattleAction.RUN
        assert kwargs == {}

def test_get_battle_action_invalid():
    """Test invalid battle action handling."""
    # Test invalid action number
    with patch('builtins.input', return_value='5'):
        assert InputHandler.get_battle_action() is None
        
    # Test non-numeric input
    with patch('builtins.input', return_value='invalid'):
        assert InputHandler.get_battle_action() is None

def test_get_move_choice_valid():
    """Test valid move selection."""
    with patch('builtins.input', return_value='1'):
        assert InputHandler.get_move_choice() == 0  # 0-based index

def test_get_move_choice_invalid():
    """Test invalid move selections."""
    # Test out of range
    with patch('builtins.input', return_value='5'):
        assert InputHandler.get_move_choice() is None
        
    # Test non-numeric
    with patch('builtins.input', return_value='invalid'):
        assert InputHandler.get_move_choice() is None
        
    # Test zero (invalid)
    with patch('builtins.input', return_value='0'):
        assert InputHandler.get_move_choice() is None

def test_get_item_choice_valid():
    """Test valid item selection."""
    with patch('builtins.input', return_value='1'):
        assert InputHandler.get_item_choice() == "pokeball"

def test_get_item_choice_invalid():
    """Test invalid item selections."""
    # Test invalid item number
    with patch('builtins.input', return_value='2'):
        assert InputHandler.get_item_choice() is None
        
    # Test non-numeric input
    with patch('builtins.input', return_value='invalid'):
        assert InputHandler.get_item_choice() is None

def test_confirm_action():
    """Test action confirmation."""
    # Test positive confirmations
    for response in ['y', 'Y', 'yes', 'YES']:
        with patch('builtins.input', return_value=response):
            assert InputHandler.confirm_action("Test?") is True
            
    # Test negative confirmations
    for response in ['n', 'N', 'no', 'NO', '', 'invalid']:
        with patch('builtins.input', return_value=response):
            assert InputHandler.confirm_action("Test?") is False

def test_input_sequence():
    """Test a complete battle input sequence."""
    # Mock a sequence: Fight -> Move 1 -> Item -> Pokeball -> Run
    inputs = ['1', '1',  # Fight with move 1
             '3', '1',   # Use Pokeball
             '4']        # Run
             
    with patch('builtins.input', side_effect=inputs):
        # Fight
        action, kwargs = InputHandler.get_battle_action()
        assert action == BattleAction.FIGHT
        assert kwargs["move_index"] == 0
        
        # Item
        action, kwargs = InputHandler.get_battle_action()
        assert action == BattleAction.ITEM
        assert kwargs["item_name"] == "pokeball"
        
        # Run
        action, kwargs = InputHandler.get_battle_action()
        assert action == BattleAction.RUN
