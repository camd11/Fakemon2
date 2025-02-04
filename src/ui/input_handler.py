"""Input handling and validation for the game."""

from typing import Optional, Tuple, Union
from ..core.battle import BattleAction

class InputHandler:
    """Handles and validates user input."""
    
    @staticmethod
    def get_enter() -> bool:
        """Wait for user to press enter.
        
        Returns:
            bool: True if enter was pressed
        """
        input()
        return True
        
    @staticmethod
    def get_starter_choice(num_starters: int) -> Optional[int]:
        """Get user's starter Pokemon choice.
        
        Args:
            num_starters: Number of available starters
            
        Returns:
            int: Index of chosen starter (0-based) or None if invalid
        """
        try:
            choice = int(input(f"Enter starter number (1-{num_starters}): "))
            if 1 <= choice <= num_starters:
                return choice - 1
        except ValueError:
            pass
        return None
        
    @staticmethod
    def get_battle_action() -> Optional[Tuple[BattleAction, dict]]:
        """Get user's battle action choice.
        
        Returns:
            Tuple of (BattleAction, kwargs) or None if invalid input
        """
        try:
            choice = int(input("Choose action (1-4): "))
            if choice == 1:  # Fight
                move_choice = InputHandler.get_move_choice()
                if move_choice is not None:
                    return BattleAction.FIGHT, {"move_index": move_choice}
                    
            elif choice == 2:  # Pokemon
                # TODO: Implement Pokemon switching
                print("Pokemon switching not implemented yet")
                return None
                
            elif choice == 3:  # Item
                item_choice = InputHandler.get_item_choice()
                if item_choice:
                    return BattleAction.ITEM, {"item_name": item_choice}
                    
            elif choice == 4:  # Run
                return BattleAction.RUN, {}
                
        except ValueError:
            pass
            
        return None
        
    @staticmethod
    def get_move_choice() -> Optional[int]:
        """Get user's move choice.
        
        Returns:
            int: Index of chosen move (0-based) or None if invalid
        """
        try:
            choice = int(input("Choose move (1-4): "))
            if 1 <= choice <= 4:
                return choice - 1
        except ValueError:
            pass
        return None
        
    @staticmethod
    def get_item_choice() -> Optional[str]:
        """Get user's item choice.
        
        Returns:
            str: Name of chosen item or None if invalid
        """
        print("\nAvailable items:")
        print("1. Pokeball")
        try:
            choice = int(input("Choose item (1): "))
            if choice == 1:
                return "pokeball"
        except ValueError:
            pass
        return None
        
    @staticmethod
    def confirm_action(prompt: str) -> bool:
        """Get user confirmation for an action.
        
        Args:
            prompt: The confirmation prompt to display
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        response = input(f"{prompt} (y/n): ").lower()
        return response == 'y' or response == 'yes'
