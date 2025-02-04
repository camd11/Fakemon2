"""Pokemon implementation for battles."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from .types import Type
from .move import Move, StatusEffect

@dataclass
class Stats:
    """Base stats for a Pokemon."""
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

class Pokemon:
    """A Pokemon that can battle."""
    
    def __init__(
        self,
        name: str,
        types: Tuple[Type, ...],
        base_stats: Stats,
        level: int,
        moves: List[Move] = None,
        held_item: Optional[str] = None  # Placeholder for future item system
    ) -> None:
        """Initialize a Pokemon.
        
        Args:
            name: Name of the Pokemon
            types: Tuple of the Pokemon's types (1-2)
            base_stats: Base stats of the Pokemon
            level: Current level (1-100)
            moves: List of known moves (max 4)
            held_item: Name of held item (future feature)
        
        Raises:
            ValueError: If types is empty or has more than 2 types,
                      or if moves has more than 4 moves
        """
        if not types or len(types) > 2:
            raise ValueError("Pokemon must have 1-2 types")
        if moves and len(moves) > 4:
            raise ValueError("Pokemon can only know up to 4 moves")
            
        self.name = name
        self.types = types
        self.base_stats = base_stats
        self.level = max(1, min(100, level))
        self.moves = moves or []
        self.held_item = held_item
        
        # Calculate actual stats based on level
        self.stats = self._calculate_stats()
        self.current_hp = self.stats.hp
        
        # Battle state
        self.status: Optional[StatusEffect] = None
        self.stat_stages = {
            "attack": 0,
            "defense": 0,
            "special_attack": 0,
            "special_defense": 0,
            "speed": 0,
            "accuracy": 0,
            "evasion": 0
        }
        
    def _calculate_stats(self) -> Stats:
        """Calculate actual stats based on base stats and level.
        
        Returns:
            Stats: The calculated stats at the current level
        """
        # HP = ((2 * Base + IV + (EV/4)) * Level/100) + Level + 10
        # Other = ((2 * Base + IV + (EV/4)) * Level/100) + 5
        # Simplified version without IVs/EVs for now
        hp = int((2 * self.base_stats.hp * self.level / 100) + self.level + 10)
        attack = int((2 * self.base_stats.attack * self.level / 100) + 5)
        defense = int((2 * self.base_stats.defense * self.level / 100) + 5)
        special_attack = int((2 * self.base_stats.special_attack * self.level / 100) + 5)
        special_defense = int((2 * self.base_stats.special_defense * self.level / 100) + 5)
        speed = int((2 * self.base_stats.speed * self.level / 100) + 5)
        
        return Stats(hp, attack, defense, special_attack, special_defense, speed)
        
    def get_stat_multiplier(self, stat: str) -> float:
        """Get the current multiplier for a stat based on its stage.
        
        Args:
            stat: The stat to get the multiplier for
            
        Returns:
            float: The multiplier to apply to the stat
        """
        stage = self.stat_stages[stat]
        if stat in ("accuracy", "evasion"):
            return (3 + max(-3, min(3, stage))) / 3
        return max(2, 2 + stage) / max(2, 2 - stage)
        
    def modify_stat(self, stat: str, stages: int) -> bool:
        """Modify a stat stage.
        
        Args:
            stat: The stat to modify
            stages: Number of stages to modify by (-6 to +6)
            
        Returns:
            bool: True if the stat was modified, False if it couldn't be modified further
        """
        if stat not in self.stat_stages:
            return False
            
        old_stage = self.stat_stages[stat]
        new_stage = max(-6, min(6, old_stage + stages))
        self.stat_stages[stat] = new_stage
        return new_stage != old_stage
        
    def heal(self, amount: int) -> int:
        """Heal the Pokemon.
        
        Args:
            amount: Amount of HP to heal
            
        Returns:
            int: The amount of HP actually healed
        """
        old_hp = self.current_hp
        self.current_hp = min(self.stats.hp, self.current_hp + amount)
        return self.current_hp - old_hp
        
    def take_damage(self, amount: int) -> int:
        """Deal damage to the Pokemon.
        
        Args:
            amount: Amount of damage to deal
            
        Returns:
            int: The amount of damage actually dealt
        """
        old_hp = self.current_hp
        self.current_hp = max(0, self.current_hp - amount)
        return old_hp - self.current_hp
        
    @property
    def is_fainted(self) -> bool:
        """Check if the Pokemon has fainted."""
        return self.current_hp <= 0
