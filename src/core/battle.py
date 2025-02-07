"""Battle system implementation."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple
import random
from .pokemon import Pokemon
from .move import Move, MoveCategory, StatusEffect
from .types import Type, TypeEffectiveness, Weather
from .item import Item, ItemType

class BattleAction(Enum):
    """Possible actions a player can take in battle."""
    FIGHT = auto()
    SWITCH = auto()
    ITEM = auto()
    RUN = auto()

@dataclass
class ItemResult:
    """Result of using an item in battle."""
    success: bool = False
    messages: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists."""
        if self.messages is None:
            self.messages = []

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
        type_chart: TypeEffectiveness,
        is_trainer_battle: bool = True,
        weather: Weather = Weather.CLEAR,
        weather_duration: int = 0,
        debug: bool = False
    ) -> None:
        """Initialize a battle.
        
        Args:
            player_pokemon: The player's active Pokemon
            enemy_pokemon: The enemy Pokemon
            type_chart: Type effectiveness data
            is_trainer_battle: Whether this is a trainer battle
            weather: Current weather condition
            weather_duration: Number of turns weather will last
            debug: Whether to enable debug logging
        """
        self.player_pokemon = player_pokemon
        self.enemy_pokemon = enemy_pokemon
        self.type_chart = type_chart
        self.weather = weather
        self.weather_duration = weather_duration
        self.turn_count = 0
        self.is_trainer_battle = is_trainer_battle
        self.debug = debug
        
    def can_move(self, pokemon: Pokemon) -> Tuple[bool, Optional[str]]:
        """Check if a Pokemon can move this turn."""
        if pokemon.status == StatusEffect.PARALYSIS:
            # 25% chance to be fully paralyzed
            if random.random() < 0.25:  # Exact 25% chance
                return False, f"{pokemon.name} is fully paralyzed!"
        elif pokemon.status == StatusEffect.SLEEP:
            # Cannot move while sleeping
            return False, f"{pokemon.name} is fast asleep!"
        elif pokemon.status == StatusEffect.FREEZE:
            # Cannot move while frozen
            return False, f"{pokemon.name} is frozen solid!"
        return True, None
        
    def execute_turn(self, move: Move, target: Pokemon) -> TurnResult:
        """Execute a turn using the selected move."""
        result = TurnResult()
        
        # Check if Pokemon can move
        attacker = self.player_pokemon if target == self.enemy_pokemon else self.enemy_pokemon
        
        # Fire moves thaw the user
        if move.type == Type.FIRE and attacker.status == StatusEffect.FREEZE:
            attacker.set_status(None)
            result.messages.append(f"{attacker.name} thawed out!")
        
        can_move, message = self.can_move(attacker)
        if not can_move:
            result.messages.append(message)
            return result
        
        # Check if move can be used
        if self.debug:
            print(f"Checking if move {move.name} can be used (PP: {move.current_pp}/{move.max_pp})")
        can_use = move.use()
        if not can_use:
            result.messages.append(f"{move.name} has no PP left!")
            if self.debug:
                print(f"Move {move.name} cannot be used - no PP left")
            return result
            
        # Accuracy check for non-status moves
        if move.category != MoveCategory.STATUS:
            # Get base accuracy and stat modifiers
            base_accuracy = 1.0 if move.accuracy is None else move.accuracy / 100
            accuracy_multiplier = attacker.get_stat_multiplier("accuracy")
            evasion_multiplier = target.get_stat_multiplier("evasion")
            
            # Get ability modifiers
            ability_accuracy = 1.0
            ability_evasion = 1.0
            
            if attacker.ability:
                accuracy_boost = attacker.ability.modifies_accuracy()
                if accuracy_boost is not None:
                    ability_accuracy = accuracy_boost
                    
            if target.ability:
                evasion_boost = target.ability.modifies_evasion()
                if evasion_boost is not None:
                    ability_evasion = evasion_boost
            
            # Calculate final accuracy:
            # - Base accuracy is a percentage (0-1)
            # - Accuracy multiplier increases hit chance
            # - Evasion multiplier is already inverted (higher = harder to hit)
            # - Apply ability modifiers (evasion boost means lower accuracy)
            final_accuracy = base_accuracy * accuracy_multiplier * evasion_multiplier * ability_accuracy * (1.0 / ability_evasion)
            
            # Perfect accuracy moves never miss (override after all modifiers)
            if move.accuracy is None:
                final_accuracy = 1.0
            
            # Random roll (0-1) must be <= accuracy to hit
            if random.random() >= final_accuracy:
                result.move_missed = True
                result.messages.append(f"{move.name} missed!")
                return result
            
        # Calculate and deal damage for damaging moves
        if move.is_damaging:
            # Critical hit check (1/24 chance = ~4.17%)
            crit_roll = random.random()
            # Critical hit chance is exactly 1/24 (approximately 4.17%)
            CRIT_CHANCE = 0.0417
            result.critical_hit = crit_roll < CRIT_CHANCE
            if self.debug:
                print(f"\nCRITICAL HIT CHECK:")
                print(f"Critical hit roll: {crit_roll:.3f} (threshold: {1/24:.3f})")
                print(f"Critical hit: {result.critical_hit}")
            
            # Get type effectiveness
            result.effectiveness = self.type_chart.get_multiplier(move.type, target.types)
            
            # Calculate and apply damage
            if self.debug:
                print(f"\nDamage calculation for {move.name}:")
                print(f"Passing critical_hit={result.critical_hit} to damage calculation")
            damage = self._calculate_damage(move, attacker, target, result.critical_hit)
            if self.debug:
                print(f"Raw damage calculated: {damage}")
            result.damage_dealt = target.take_damage(damage)
            if self.debug:
                print(f"Damage dealt after take_damage: {result.damage_dealt}")
            
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
            if effect.status:
                # Convert status chance to decimal first
                status_chance = effect.status_chance / 100
                
                # Apply resistance if any
                if target.ability:
                    resistance = target.ability.modifies_status_chance(effect.status)
                    if resistance is not None:
                        status_chance *= resistance
                
                # Random check
                if random.random() <= status_chance:
                    # Set duration based on status type
                    duration = None
                    if effect.status == StatusEffect.SLEEP:
                        duration = random.randint(1, 3)  # Initial duration 1-3 turns
                    elif effect.status == StatusEffect.FREEZE:
                        duration = None  # Freeze has no duration
                    else:
                        duration = 5  # Initial duration 5 turns
                    
                    if target.set_status(effect.status, duration=duration):
                        result.status_applied = effect.status
                        # Custom message for sleep
                        if effect.status == StatusEffect.SLEEP:
                            result.messages.append(f"{target.name} fell asleep!")
                        else:
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
        """Calculate damage for a damaging move."""
        if self.debug:
            print(f"\n_calculate_damage called with critical={critical}")
            
        # Get attack and defense stats
        if move.category == MoveCategory.PHYSICAL:
            attack = attacker.stats.attack * attacker.get_stat_multiplier("attack")
            defense = defender.stats.defense * defender.get_stat_multiplier("defense")
            base_attack = attacker.stats.attack
            base_defense = defender.stats.defense
        else:  # Special
            attack = attacker.stats.special_attack * attacker.get_stat_multiplier("special_attack")
            defense = defender.stats.special_defense * defender.get_stat_multiplier("special_defense")
            base_attack = attacker.stats.special_attack
            base_defense = defender.stats.special_defense
            
        if critical:
            # For critical hits:
            # - Use the better of current attack or base attack
            # - Always use base defense (ignore defense boosts)
            attack = max(attack, base_attack)  # Keep positive changes
            defense = base_defense  # Ignore defense boosts
            
        # Calculate base damage
        level_factor = (2 * attacker.level / 5 + 2)
        damage = (level_factor * move.power * attack / defense / 50 + 2)
        
        # Apply STAB
        if move.type in attacker.types:
            damage *= 1.5
        
        # Apply type effectiveness
        damage *= self.type_chart.get_multiplier(move.type, defender.types)
        
        # Apply weather effects
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
        
        # Apply critical hit multiplier last
        if critical:
            damage *= 2.0
        
        # Apply random factor (85-100%)
        damage *= random.randint(85, 100) / 100
        
        # Round after all multipliers
        return max(1, int(damage))  # Minimum 1 damage
        
    @property
    def is_over(self) -> bool:
        """Check if the battle is over."""
        return self.player_pokemon.is_fainted or self.enemy_pokemon.is_fainted
        
    def use_item(self, item: Item, target: Pokemon) -> ItemResult:
        """Use an item on a target Pokemon."""
        result = ItemResult()
        
        # Check if target is fainted
        if target.is_fainted:
            result.messages.append("Can't use items on fainted Pokemon!")
            return result
            
        # Check if item can be used
        if not item.can_use(target):
            if item.effect.type == ItemType.HEALING:
                result.messages.append(f"{target.name} is already at full HP!")
            elif item.effect.type == ItemType.PP:
                result.messages.append(f"{target.name}'s moves are at full PP!")
            elif item.effect.type == ItemType.STATUS:
                result.messages.append(f"{target.name} has no status condition!")
            elif item.effect.type == ItemType.POKEBALL:
                result.messages.append("Can't use Poke Ball in a trainer battle!")
            return result
            
        # Handle status items separately to store status before clearing
        if item.effect.type == ItemType.STATUS:
            old_status = target.status.lower() if isinstance(target.status, str) else "status condition"
            if item.use(target):
                result.success = True
                result.messages.append(f"{target.name} was cured of {old_status}!")
            return result
            
        # Use other items
        if item.use(target):
            result.success = True
            
            # Add appropriate message
            if item.effect.type == ItemType.HEALING:
                result.messages.append(f"{target.name} was healed for {item.effect.value} HP!")
            elif item.effect.type == ItemType.PP:
                result.messages.append(f"{target.name}'s move PP was restored!")
            elif item.effect.type == ItemType.BOOST:
                # Get stat name from conditions or default to Attack
                stat_name = next(iter(item.effect.conditions)) if item.effect.conditions else "Attack"
                # Apply stat boost
                target.modify_stat(stat_name.lower(), item.effect.value)
                result.messages.append(f"{target.name}'s {stat_name} rose!")
                
        return result
        
    def apply_weather_effects(self) -> TurnResult:
        """Apply end-of-turn weather effects."""
        result = TurnResult()
        
        if self.weather == Weather.CLEAR:
            return result
            
        # Apply damage for sandstorm/hail first
        if self.weather in (Weather.SANDSTORM, Weather.HAIL):
            for pokemon in (self.player_pokemon, self.enemy_pokemon):
                # Check for weather immunity first
                if pokemon.ability and pokemon.ability.prevents_weather_damage(self.weather):
                    continue
                
                # Skip type immunities
                if (self.weather == Weather.SANDSTORM and
                    any(t in (Type.ROCK, Type.GROUND, Type.STEEL) for t in pokemon.types)):
                    continue
                    
                if self.weather == Weather.HAIL and Type.ICE in pokemon.types:
                    continue
                    
                # Calculate base damage (1/16 max HP)
                damage = pokemon.stats.hp // 16
                
                # Apply resistance if any
                if pokemon.ability:
                    resistance = pokemon.ability.modifies_weather_damage(self.weather)
                    if resistance is not None:
                        damage = int(damage * resistance)
                damage_dealt = pokemon.take_damage(damage)
                
                # Add damage message first
                weather_name = "sandstorm" if self.weather == Weather.SANDSTORM else "hail"
                if damage_dealt > 0:
                    result.messages.append(f"{pokemon.name} is buffeted by the {weather_name}!")
        
        # Then add weather status message
        if self.weather == Weather.RAIN:
            result.messages.append("Rain continues to fall.")
        elif self.weather == Weather.SUN:
            result.messages.append("The sunlight is strong.")
        elif self.weather == Weather.SANDSTORM:
            result.messages.append("The sandstorm rages!")
        elif self.weather == Weather.HAIL:
            result.messages.append("Hail continues to fall!")
                
        return result
        
    def end_turn(self) -> TurnResult:
        """End the current turn and apply any effects."""
        result = TurnResult()
        
        # Apply weather effects first
        weather_result = self.apply_weather_effects()
        result.messages.extend(weather_result.messages)
        
        # Then apply status effects
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            # Store current status
            current_status = pokemon.status
            
            # Check for freeze thaw (20% chance) before updating duration
            if current_status == StatusEffect.FREEZE:
                if random.random() < 0.20:  # 20% chance
                    pokemon.set_status(None)
                    result.messages.append(f"{pokemon.name} thawed out!")
                    continue
            
            # Check status duration
            status_message = pokemon.update_status()
            if status_message:
                result.messages.append(status_message)
            # Apply status damage if status wasn't cleared
            elif current_status == StatusEffect.POISON:
                damage = pokemon.stats.hp // 8
                pokemon.take_damage(damage)
                result.messages.append(f"{pokemon.name} is hurt by poison!")
            elif current_status == StatusEffect.BURN:
                damage = pokemon.stats.hp // 8
                pokemon.take_damage(damage)
                result.messages.append(f"{pokemon.name} is hurt by its burn!")
        
        # Check weather duration at end of turn
        if self.weather != Weather.CLEAR:
            if self.weather_duration > 0:
                self.weather_duration -= 1  # Decrement after this turn's effects
                
                # Only clear weather after duration hits 0 and turn is complete
                if self.weather_duration == 0:
                    weather_name = self.weather.name.lower()
                    if weather_name == "sun":
                        weather_name = "harsh sunlight"
                    result.messages.append(f"The {weather_name} subsided.")
                    # Weather persists until turn is fully complete
                    self.weather = Weather.CLEAR
                
        return result
        
    @property
    def winner(self) -> Optional[Pokemon]:
        """Get the winning Pokemon if the battle is over."""
        if not self.is_over:
            return None
        return self.enemy_pokemon if self.player_pokemon.is_fainted else self.player_pokemon
