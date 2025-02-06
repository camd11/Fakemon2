"""Pokemon implementation for battles."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from .types import Type
from .move import Move, StatusEffect
from .ability import Ability, AbilityType

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
        ability: Optional[Ability] = None,
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
        self.ability = ability
        self.held_item = held_item
        
        # Calculate actual stats based on level
        self.stats = self._calculate_stats()
        self.current_hp = self.stats.hp
        
        # Battle state
        self.status: Optional[StatusEffect] = None
        self.status_duration: Optional[int] = None
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
        # Stat calculation formula:
        # HP = ((2 * Base * Level)/100) + Level + 10
        # Other = ((2 * Base * Level)/100) + 5
        # Simplified version without IVs/EVs
        hp = int((2 * self.base_stats.hp * self.level) / 100 + self.level + 10)
        attack = int((2 * self.base_stats.attack * self.level) / 100 + 5)
        defense = int((2 * self.base_stats.defense * self.level) / 100 + 5)
        special_attack = int((2 * self.base_stats.special_attack * self.level) / 100 + 5)
        special_defense = int((2 * self.base_stats.special_defense * self.level) / 100 + 5)
        speed = int((2 * self.base_stats.speed * self.level) / 100 + 5)
        
        return Stats(hp, attack, defense, special_attack, special_defense, speed)
        
    def get_stat_multiplier(self, stat: str) -> float:
        """Get the current multiplier for a stat based on its stage and status.
        
        Args:
            stat: The stat to get the multiplier for
            
        Returns:
            float: The multiplier to apply to the stat
        """
        multiplier = 1.0
        
        # Stage multiplier
        stage = self.stat_stages[stat]
        if stat in ("accuracy", "evasion"):
            # Accuracy/Evasion use different formula:
            # For accuracy:
            # +1: 3/3 = 1.0
            # +2: 4/3 ≈ 1.33
            # +3: 5/3 ≈ 1.67
            # +4: 6/3 = 2.0
            # +5: 7/3 ≈ 2.33
            # +6: 8/3 ≈ 2.67
            # -1: 3/4 = 0.75
            # -2: 3/5 = 0.60
            # -3: 3/6 = 0.50
            # -4: 3/7 ≈ 0.43
            # -5: 3/8 = 0.375
            # -6: 3/9 = 0.333
            if stat == "accuracy":
                if stage >= 0:
                    multiplier *= (3 + stage) / 3
                else:
                    multiplier *= 3 / (3 + abs(stage))
            else:  # evasion
                # For evasion, invert the formula so higher stages = lower hit chance
                if stage >= 0:
                    multiplier *= 3 / (3 + stage)  # +1 stage = 3/4 = 0.75 hit chance
                else:
                    multiplier *= (3 + abs(stage)) / 3  # -1 stage = 4/3 ≈ 1.33 hit chance
        else:
            multiplier *= max(2, 2 + stage) / max(2, 2 - stage)
            
        # Status effects
        if self.status == StatusEffect.PARALYSIS and stat == "speed":
            multiplier *= 0.25
        elif self.status == StatusEffect.BURN and stat == "attack":
            multiplier *= 0.5
            
        return multiplier
        
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
        print(f"\nTaking damage - {self.name}:")
        print(f"  Current HP: {self.current_hp}")
        print(f"  Damage amount: {amount}")
        self.current_hp = max(0, self.current_hp - amount)
        print(f"  New HP: {self.current_hp}")
        damage_dealt = old_hp - self.current_hp
        print(f"  Actual damage dealt: {damage_dealt}")
        return damage_dealt
        
    def set_status(self, status: Optional[StatusEffect], duration: Optional[int] = None) -> bool:
        """Set a status effect on the Pokemon.
        
        Args:
            status: The status effect to apply, or None to clear
            duration: How many turns the status should last. Use None for indefinite
                     duration (freeze) or to clear status. Sleep lasts 1-3 turns,
                     other status effects typically last 5 turns.
            
        Returns:
            bool: True if the status was applied, False if it couldn't be
        """
        # Store old status for message
        old_status = self.status
        
        # Can't apply a new status if already has one
        if old_status is not None and status is not None:
            return False
            
        # Check type and ability immunities
        if status is not None:
            # Type immunities
            if status == StatusEffect.BURN and Type.FIRE in self.types:
                return False  # Fire-types can't be burned
            elif status == StatusEffect.FREEZE and Type.ICE in self.types:
                return False  # Ice-types can't be frozen
            elif status == StatusEffect.PARALYSIS and Type.ELECTRIC in self.types:
                return False  # Electric-types can't be paralyzed
            elif status == StatusEffect.POISON and (Type.POISON in self.types or Type.STEEL in self.types):
                return False  # Poison/Steel-types can't be poisoned
                
            # Ability immunities (only check AbilityType.STATUS_IMMUNITY)
            if self.ability and self.ability.type == AbilityType.STATUS_IMMUNITY and self.ability.prevents_status(status):
                return False  # Ability prevents this status
            
        # Clear old status
        self.status = None
        self.status_duration = None
        
        # Apply new status if any
        if status is not None:
            self.status = status
            self.status_duration = duration
        
        # Reset stat stages if status was cleared
        if status is None:
            self.stat_stages = {
                "attack": 0,
                "defense": 0,
                "special_attack": 0,
                "special_defense": 0,
                "speed": 0,
                "accuracy": 0,
                "evasion": 0
            }
            
        return True
        
    def update_status(self) -> Optional[str]:
        """Update status duration and return any status clear message.
        
        Returns:
            Optional[str]: Message if status was cleared, None otherwise
        """
        # No status to update
        if self.status is None:
            return None
            
        # No duration set
        if self.status_duration is None:
            return None
            
        # Decrease duration
        self.status_duration -= 1
        
        # Check if duration reached 0
        if self.status_duration <= 0:
            old_status = self.status
            # Clear status without resetting stat stages
            self.status = None
            self.status_duration = None
            return f"{self.name}'s {old_status.name.lower()} faded!"
        return None
        
    def reset_stats(self) -> None:
        """Reset all stat stages to 0."""
        self.stat_stages = {
            "attack": 0,
            "defense": 0,
            "special_attack": 0,
            "special_defense": 0,
            "speed": 0,
            "accuracy": 0,
            "evasion": 0
        }
        
    @property
    def is_fainted(self) -> bool:
        """Check if the Pokemon has fainted."""
        return self.current_hp <= 0
