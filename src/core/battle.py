"""Battle system implementation."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple
import random
from .pokemon import Pokemon
from .move import Move, MoveCategory, StatusEffect
from .types import Type, TypeEffectiveness

class Weather(Enum):
    """Weather conditions that can affect battle."""
    CLEAR = auto()
    RAIN = auto()
    SUN = auto()
    SANDSTORM = auto()
    HAIL = auto()

class BattleAction(Enum):
    """Possible actions a player can take in battle."""
    FIGHT = auto()
    SWITCH = auto()
    ITEM = auto()
    RUN = auto()

@dataclass
class TurnResult:
    """Result of a turn in battle."""
    damage_dealt: int = 0
    move_missed: bool = False
    critical_hit: bool = False
    effectiveness: float = 1.0
    status_applied: Optional[StatusEffect] = None
    stat_changes: List[Tuple[str, int]] = None
    messages: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists."""
        if self.stat_changes is None:
            self.stat_changes = []
        if self.messages is None:
            self.messages = []

class Battle:
    """Handles battle mechanics between two Pokemon."""
    
    def __init__(
        self,
        player_pokemon: Pokemon,
        enemy_pokemon: Pokemon,
        type_chart: TypeEffectiveness
    ) -> None:
        """Initialize a battle.
        
        Args:
            player_pokemon: The player's active Pokemon
            enemy_pokemon: The enemy Pokemon
            type_chart: Type effectiveness data
        """
        self.player_pokemon = player_pokemon
        self.enemy_pokemon = enemy_pokemon
        self.type_chart = type_chart
        self.weather = Weather.CLEAR
        self.turn_count = 0
        
    def execute_turn(self, move: Move, target: Pokemon) -> TurnResult:
        """Execute a turn using the selected move.
        
        Args:
            move: The move to use
            target: The target Pokemon
            
        Returns:
            TurnResult: The result of the turn
        """
        result = TurnResult()
        
        # Check if move can be used
        if not move.use():
            result.messages.append(f"{move.name} has no PP left!")
            return result
            
        # Accuracy check
        accuracy = move.accuracy * self.player_pokemon.get_stat_multiplier("accuracy")
        evasion = target.get_stat_multiplier("evasion")
        if random.random() * 100 > accuracy / evasion:
            result.move_missed = True
            result.messages.append(f"{move.name} missed!")
            return result
            
        # Calculate and deal damage for damaging moves
        if move.is_damaging:
            # Critical hit check (1/24 chance)
            result.critical_hit = random.random() < 1/24
            
            # Get type effectiveness
            result.effectiveness = self.type_chart.get_multiplier(move.type, target.types)
            
            # Calculate damage
            damage = self._calculate_damage(move, self.player_pokemon, target, result.critical_hit)
            result.damage_dealt = target.take_damage(damage)
            
            # Add damage message
            if result.critical_hit:
                result.messages.append("A critical hit!")
            if result.effectiveness > 1:
                result.messages.append("It's super effective!")
            elif result.effectiveness < 1:
                result.messages.append("It's not very effective...")
            
        # Apply move effects
        for effect in move.effects:
            # Status effects
            if effect.status and random.random() * 100 <= effect.status_chance:
                target.status = effect.status
                result.status_applied = effect.status
                result.messages.append(f"{target.name} was {effect.status.name.lower()}ed!")
                
            # Stat changes
            for stat, stages in effect.stat_changes.items():
                if target.modify_stat(stat, stages):
                    direction = "raised" if stages > 0 else "lowered"
                    result.stat_changes.append((stat, stages))
                    result.messages.append(
                        f"{target.name}'s {stat.replace('_', ' ')} was {direction}!"
                    )
                    
        return result
        
    def _calculate_damage(
        self,
        move: Move,
        attacker: Pokemon,
        defender: Pokemon,
        critical: bool
    ) -> int:
        """Calculate damage for a damaging move.
        
        Args:
            move: The move being used
            attacker: The attacking Pokemon
            defender: The defending Pokemon
            critical: Whether the move is a critical hit
            
        Returns:
            int: The amount of damage to deal
        """
        # Get attack and defense stats
        if move.category == MoveCategory.PHYSICAL:
            attack = attacker.stats.attack * attacker.get_stat_multiplier("attack")
            defense = defender.stats.defense * defender.get_stat_multiplier("defense")
        else:  # Special
            attack = attacker.stats.special_attack * attacker.get_stat_multiplier("special_attack")
            defense = defender.stats.special_defense * defender.get_stat_multiplier("special_defense")
            
        # Critical hits ignore stat reductions and multiply by 1.5
        if critical:
            if attack < attacker.stats.attack:
                attack = attacker.stats.attack
            if defense > defender.stats.defense:
                defense = defender.stats.defense
            attack *= 1.5
            
        # Calculate base damage
        # ((2 * Level / 5 + 2) * Power * Attack / Defense / 50 + 2)
        damage = ((2 * attacker.level / 5 + 2) * move.power * attack / defense / 50 + 2)
        
        # Apply STAB (Same Type Attack Bonus)
        if move.type in attacker.types:
            damage *= 1.5
            
        # Apply type effectiveness
        damage *= self.type_chart.get_multiplier(move.type, defender.types)
        
        # Apply random factor (85-100%)
        damage *= random.randint(85, 100) / 100
        
        # Weather effects
        if self.weather == Weather.RAIN:
            if move.type == Type.WATER:
                damage *= 1.5
            elif move.type == Type.FIRE:
                damage *= 0.5
        elif self.weather == Weather.SUN:
            if move.type == Type.FIRE:
                damage *= 1.5
            elif move.type == Type.WATER:
                damage *= 0.5
                
        return int(damage)
        
    @property
    def is_over(self) -> bool:
        """Check if the battle is over."""
        return self.player_pokemon.is_fainted or self.enemy_pokemon.is_fainted
        
    @property
    def winner(self) -> Optional[Pokemon]:
        """Get the winning Pokemon if the battle is over."""
        if not self.is_over:
            return None
        return self.enemy_pokemon if self.player_pokemon.is_fainted else self.player_pokemon
