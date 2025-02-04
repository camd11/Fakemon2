"""Game state management and progression tracking."""

from typing import List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
from ..core.pokemon import Pokemon
from .battle_manager import BattleManager
from .pokemon_factory import PokemonFactory

class GamePhase(Enum):
    """Current phase of the game."""
    TITLE = auto()        # Title screen
    STARTER = auto()      # Starter selection
    BATTLE = auto()       # In battle
    GAME_OVER = auto()    # Game over screen
    VICTORY = auto()      # Beat level 200

@dataclass
class GameStats:
    """Statistics tracking for the current game."""
    battles_won: int = 0
    battles_lost: int = 0
    pokemon_caught: int = 0
    max_level_reached: int = 1
    critical_hits: int = 0
    super_effective_hits: int = 0

class GameState:
    """Manages overall game state and progression."""
    
    def __init__(self) -> None:
        """Initialize a new game state."""
        self.pokemon_factory = PokemonFactory()
        self.battle_manager = BattleManager(self.pokemon_factory)
        self.phase = GamePhase.TITLE
        self.stats = GameStats()
        self._messages: List[str] = []
        
    def start_new_game(self, starter_id: str) -> bool:
        """Start a new game with the chosen starter Pokemon.
        
        Args:
            starter_id: ID of the chosen starter Pokemon
            
        Returns:
            bool: True if game started successfully
        """
        if self.phase != GamePhase.STARTER:
            return False
            
        success = self.battle_manager.start_game(starter_id)
        if success:
            self._messages.append(f"You chose {starter_id.title()} as your starter!")
            self.phase = GamePhase.BATTLE
            
        return success
        
    def get_available_starters(self) -> List[str]:
        """Get list of available starter Pokemon.
        
        Returns:
            List[str]: IDs of available starter Pokemon
        """
        # For now, return the classic starters
        return ["bulbasaur", "charmander", "squirtle"]
        
    def start_battle(self) -> Tuple[Pokemon, Pokemon]:
        """Start a new battle.
        
        Returns:
            Tuple[Pokemon, Pokemon]: (player's Pokemon, enemy Pokemon)
        """
        if self.phase != GamePhase.BATTLE:
            raise ValueError("Cannot start battle in current phase")
            
        player, enemy = self.battle_manager.start_battle()
        self._messages.append(f"A wild {enemy.name} appeared!")
        return player, enemy
        
    def handle_battle_end(self) -> None:
        """Handle the end of a battle and update game state."""
        if self.phase != GamePhase.BATTLE:
            return
            
        won, messages = self.battle_manager.handle_battle_end()
        self._messages.extend(messages)
        
        if won:
            self.stats.battles_won += 1
            self.stats.max_level_reached = max(
                self.stats.max_level_reached,
                self.battle_manager.current_level
            )
            
            if self.battle_manager.game_completed:
                self.phase = GamePhase.VICTORY
                self._messages.append("Congratulations! You've completed all 200 levels!")
        else:
            self.stats.battles_lost += 1
            self.phase = GamePhase.GAME_OVER
            
    def get_player_party(self) -> List[Pokemon]:
        """Get the player's current party.
        
        Returns:
            List[Pokemon]: The player's Pokemon party
        """
        return self.battle_manager.player_party
        
    def get_remaining_pokeballs(self) -> int:
        """Get the number of Pokeballs remaining.
        
        Returns:
            int: Number of Pokeballs
        """
        return self.battle_manager.pokeballs
        
    def get_current_level(self) -> int:
        """Get the current game level.
        
        Returns:
            int: Current level (1-200)
        """
        return self.battle_manager.current_level
        
    def get_messages(self) -> List[str]:
        """Get and clear the current message queue.
        
        Returns:
            List[str]: List of game messages
        """
        messages = self._messages.copy()
        self._messages.clear()
        return messages
        
    @property
    def can_catch_pokemon(self) -> bool:
        """Check if the player can attempt to catch Pokemon.
        
        Returns:
            bool: True if player has Pokeballs and party isn't full
        """
        return (self.battle_manager.pokeballs > 0 and
                len(self.battle_manager.player_party) < 6)
                
    def save_game(self) -> dict:
        """Create a save state of the current game.
        
        Returns:
            dict: Save state data
        """
        # TODO: Implement save state serialization
        raise NotImplementedError("Save/Load not yet implemented")
        
    def load_game(self, save_data: dict) -> bool:
        """Load a saved game state.
        
        Args:
            save_data: Save state data
            
        Returns:
            bool: True if game was loaded successfully
        """
        # TODO: Implement save state deserialization
        raise NotImplementedError("Save/Load not yet implemented")
