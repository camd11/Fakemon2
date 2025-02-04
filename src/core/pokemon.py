"""Pokemon implementation for battles."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from .types import Type
from .move import Move, StatusEffect
from .ability import Ability, AbilityType
from .item import Item, HeldItemTrigger, ItemEffect

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
        held_item: Optional[Item] = None,
        ability: Optional[Ability] = None
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
        self._used_held_item = False  # Track if single-use held item was used
        self.ability = ability
        
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
        
    def get_stat_multiplier(self, stat: str, weather: Optional['Weather'] = None) -> float:
        """Get the current multiplier for a stat based on its stage, status, and ability.
        
        Args:
            stat: The stat to get the multiplier for
            weather: Current weather condition (for weather-based abilities)
            
        Returns:
            float: The multiplier to apply to the stat
        """
        multiplier = 1.0
        
        # Stage multiplier
        stage = self.stat_stages[stat]
        if stat in ("accuracy", "evasion"):
            multiplier *= (3 + max(-3, min(3, stage))) / 3
        else:
            multiplier *= max(2, 2 + stage) / max(2, 2 - stage)
            
        # Status effects
        if self.status == StatusEffect.PARALYSIS and stat == "speed":
            multiplier *= 0.25
        elif self.status == StatusEffect.BURN and stat == "attack":
            multiplier *= 0.5  # Burn halves physical attack
            
        # Ability boosts
        if self.ability and self.ability.type == AbilityType.STAT_BOOST:
            if self.ability.stat_boost and self.ability.stat_boost[0] == stat:
                boost_stat, boost_value, required_weather = self.ability.stat_boost
                
                # Weather-based abilities
                if required_weather is None or (weather and weather == required_weather):
                    # Status-based abilities (like Guts)
                    if self.ability.boost_condition == "status":
                        if self.status is not None:
                            multiplier *= boost_value
                    else:
                        multiplier *= boost_value
            
        return multiplier
        
    def equip_item(self, item: Item) -> bool:
        """Equip a held item.
        
        Args:
            item: The item to equip
            
        Returns:
            bool: True if item was equipped, False if already has item
        """
        if self.held_item is not None:
            return False
        self.held_item = item
        self._used_held_item = False
        return True
        
    def unequip_item(self) -> Optional[Item]:
        """Unequip the currently held item.
        
        Returns:
            Optional[Item]: The unequipped item, or None if no item held
        """
        item = self.held_item
        self.held_item = None
        self._used_held_item = False
        return item
        
    def check_held_item(self, trigger: HeldItemTrigger, **kwargs) -> Optional[ItemEffect]:
        """Check if held item should activate.
        
        Args:
            trigger: The trigger type to check
            **kwargs: Additional trigger parameters:
                - hp_percent: Current HP percentage for LOW_HP trigger
                - move_effectiveness: Move effectiveness for SUPER_EFFECTIVE trigger
                
        Returns:
            Optional[ItemEffect]: The item effect if triggered, None otherwise
        """
        if not self.held_item or self._used_held_item:
            return None
            
        if self.held_item.trigger != trigger:
            return None
            
        # Check trigger conditions
        if trigger == HeldItemTrigger.LOW_HP:
            hp_percent = kwargs.get("hp_percent", 1.0)
            if hp_percent > self.held_item.trigger_threshold:
                return None
                
        elif trigger == HeldItemTrigger.SUPER_EFFECTIVE:
            effectiveness = kwargs.get("move_effectiveness", 1.0)
            if effectiveness <= 1.0:
                return None
                
        # Mark single-use items as used
        if self.held_item.single_use:
            self._used_held_item = True
            
        return self.held_item.effect
        
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
        
    def set_status(self, status: Optional[StatusEffect], duration: Optional[int] = None) -> bool:
        """Set a status effect on the Pokemon.
        
        Args:
            status: The status effect to apply, or None to clear
            duration: How many turns the status should last, or None for indefinite
            
        Returns:
            bool: True if the status was applied, False if it couldn't be
        """
        # Store old status for message
        old_status = self.status
        
        # Can't apply a new status if already has one
        if old_status is not None and status is not None:
            return False
            
        # Check immunities
        if status is not None:
            # Check ability immunities
            if self.ability and self.ability.prevents_status(status):
                return False
                
            # Check type immunities
            if status == StatusEffect.BURN and Type.FIRE in self.types:
                return False
            elif status == StatusEffect.POISON and Type.STEEL in self.types:
                return False
            elif status == StatusEffect.PARALYSIS and Type.ELECTRIC in self.types:
                return False
            elif status == StatusEffect.FREEZE and Type.ICE in self.types:
                return False
            
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
        
    @property
    def is_fainted(self) -> bool:
        """Check if the Pokemon has fainted."""
        return self.current_hp <= 0
