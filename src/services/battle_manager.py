"""Battle management and game rules implementation."""

from typing import List, Optional, Tuple
from ..core.battle import Battle, BattleAction, TurnResult
from ..core.pokemon import Pokemon
from ..core.move import Move
from .pokemon_factory import PokemonFactory

class BattleManager:
    """Manages battle flow and game rules."""
    
    def __init__(self, pokemon_factory: PokemonFactory) -> None:
        """Initialize the battle manager.
        
        Args:
            pokemon_factory: Factory for creating Pokemon
        """
        self.pokemon_factory = pokemon_factory
        self.current_battle: Optional[Battle] = None
        self.player_party: List[Pokemon] = []
        self.pokeballs: int = 5  # Starting number of Pokeballs
        self.current_level: int = 1
        
    def start_game(self, starter_id: str) -> bool:
        """Start a new game with the chosen starter Pokemon.
        
        Args:
            starter_id: ID of the chosen starter Pokemon
            
        Returns:
            bool: True if game started successfully, False if starter_id invalid
        """
        starter = self.pokemon_factory.create_pokemon(starter_id, 5)  # Start at level 5
        if not starter:
            return False
            
        self.player_party = [starter]
        self.pokeballs = 5
        self.current_level = 1
        return True
        
    def start_battle(self) -> Tuple[Pokemon, Pokemon]:
        """Start a new battle with a random enemy Pokemon.
        
        Returns:
            Tuple[Pokemon, Pokemon]: (player's active Pokemon, enemy Pokemon)
        """
        # Create enemy Pokemon at appropriate level
        enemy_level = 5 + self.current_level - 1  # Level scales with progress
        enemy = self.pokemon_factory.create_random_pokemon(enemy_level)
        
        # Start battle
        self.current_battle = Battle(
            self.player_party[0],  # Currently only using first Pokemon
            enemy,
            self.pokemon_factory.type_chart
        )
        
        return self.player_party[0], enemy
        
    def execute_turn(self, action: BattleAction, **kwargs) -> Optional[TurnResult]:
        """Execute a turn in the current battle.
        
        Args:
            action: The action to take
            **kwargs: Additional arguments based on action:
                - FIGHT: move_index: int
                - SWITCH: pokemon_index: int
                - ITEM: item_name: str
                - RUN: no additional args
                
        Returns:
            TurnResult if action was executed, None if invalid action
        """
        if not self.current_battle:
            return None
            
        if action == BattleAction.FIGHT:
            move_index = kwargs.get("move_index", 0)
            if move_index < 0 or move_index >= len(self.current_battle.player_pokemon.moves):
                return None
            move = self.current_battle.player_pokemon.moves[move_index]
            return self.current_battle.execute_turn(move, self.current_battle.enemy_pokemon)
            
        elif action == BattleAction.SWITCH:
            # Not implemented yet - will be needed when we support multiple Pokemon
            return None
            
        elif action == BattleAction.ITEM:
            item_name = kwargs.get("item_name")
            if item_name == "pokeball" and self.pokeballs > 0:
                return self._try_catch_pokemon()
            return None
            
        elif action == BattleAction.RUN:
            # In roguelike style, running isn't allowed
            return None
            
        return None
        
    def _try_catch_pokemon(self) -> TurnResult:
        """Attempt to catch the enemy Pokemon.
        
        Returns:
            TurnResult with catch attempt results
        """
        if not self.current_battle:
            return TurnResult(messages=["No active battle!"])
            
        # Simple catch mechanic for now:
        # Catch rate = (1 - current_hp/max_hp) * 100
        enemy = self.current_battle.enemy_pokemon
        catch_rate = (1 - enemy.current_hp / enemy.stats.hp) * 100
        
        import random
        caught = random.random() * 100 < catch_rate
        
        self.pokeballs -= 1
        
        if caught and len(self.player_party) < 6:
            self.player_party.append(enemy)
            return TurnResult(messages=[
                f"Used a Pokeball! ({self.pokeballs} remaining)",
                f"Caught {enemy.name}!"
            ])
        else:
            return TurnResult(messages=[
                f"Used a Pokeball! ({self.pokeballs} remaining)",
                f"Oh no! {enemy.name} broke free!"
            ])
            
    def handle_battle_end(self) -> Tuple[bool, List[str]]:
        """Handle the end of a battle and determine rewards.
        
        Returns:
            Tuple[bool, List[str]]: (player won, list of result messages)
        """
        if not self.current_battle or not self.current_battle.is_over:
            return False, ["Battle is not over!"]
            
        messages = []
        player_won = self.current_battle.winner == self.current_battle.player_pokemon
        
        if player_won:
            self.current_level += 1
            messages.extend([
                f"Won the battle!",
                f"Advanced to level {self.current_level}!"
            ])
            
            # Future: Add item rewards here
            
        else:
            messages.append("Lost the battle! Game Over!")
            
        self.current_battle = None
        return player_won, messages
        
    @property
    def game_completed(self) -> bool:
        """Check if the game has been completed (reached level 200)."""
        return self.current_level > 200
