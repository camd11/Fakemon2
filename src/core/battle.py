"""Battle system implementation."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple
import random
from .pokemon import Pokemon
from .move import Move, MoveCategory, StatusEffect
from .types import Type, TypeEffectiveness
from .item import Item, ItemType, HeldItemTrigger
from .ability import AbilityType, HazardType, TerrainType, AuraType

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
        terrain: Optional[TerrainType] = None,
        terrain_duration: int = 5
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
        self.weather = weather
        self.weather_duration = weather_duration
        self.turn_count = 0
        self.is_trainer_battle = is_trainer_battle
        
        # Track hazards for each side
        self.player_hazards = {
            HazardType.SPIKES: 0,  # Number of layers
            HazardType.TOXIC_SPIKES: 0,  # Number of layers
            HazardType.STEALTH_ROCK: False  # Present or not
        }
        self.enemy_hazards = {
            HazardType.SPIKES: 0,
            HazardType.TOXIC_SPIKES: 0,
            HazardType.STEALTH_ROCK: False
        }
        
        # Track terrain
        self.terrain = terrain
        self.terrain_duration = terrain_duration
        
        # Track active auras
        self.active_auras = set()  # Set of active AuraTypes
        self.aura_break_active = False  # Whether Aura Break is active
        
        # Check for weather, terrain, and aura abilities
        self._check_weather_abilities()
        self._check_terrain_abilities()
        self._check_aura_abilities()
        
    def _check_weather_abilities(self) -> None:
        """Check and apply weather effects from Pokemon abilities."""
        # Check both Pokemon for weather abilities
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if pokemon.ability and pokemon.ability.type == AbilityType.WEATHER:
                if pokemon.ability.weather_effect:
                    self.weather = pokemon.ability.weather_effect
                    self.weather_duration = None  # Weather from abilities lasts indefinitely
        
    def apply_hazards(self, pokemon: Pokemon, is_player: bool) -> List[str]:
        """Apply entry hazard effects when a Pokemon switches in.
        
        Args:
            pokemon: The Pokemon switching in
            is_player: Whether this is the player's Pokemon
            
        Returns:
            List[str]: Messages about hazard effects
        """
        messages = []
        hazards = self.enemy_hazards if is_player else self.player_hazards
        
        # Skip if Pokemon is Flying type or has Levitate
        is_grounded = Type.FLYING not in pokemon.types
        
        # Apply Stealth Rock damage
        if hazards[HazardType.STEALTH_ROCK]:
            # Calculate damage based on type effectiveness
            effectiveness = 1.0
            for type_ in pokemon.types:
                effectiveness *= self.type_chart.get_multiplier(Type.ROCK, (type_,))
            damage = int(pokemon.stats.hp * effectiveness / 8)
            pokemon.take_damage(damage)
            messages.append(f"{pokemon.name} was hurt by stealth rocks!")
            
        # Apply Spikes damage (only to grounded Pokemon)
        if is_grounded and hazards[HazardType.SPIKES] > 0:
            # Damage increases with layers: 1/8, 1/6, 1/4
            denominators = [8, 6, 4]
            damage = pokemon.stats.hp // denominators[hazards[HazardType.SPIKES] - 1]
            pokemon.take_damage(damage)
            messages.append(f"{pokemon.name} was hurt by spikes!")
            
        # Apply Toxic Spikes effect (only to grounded Pokemon)
        if is_grounded and hazards[HazardType.TOXIC_SPIKES] > 0:
            # Second layer causes toxic instead of regular poison
            if hazards[HazardType.TOXIC_SPIKES] >= 2:
                if pokemon.set_status(StatusEffect.POISON, duration=None):  # Toxic is permanent
                    messages.append(f"{pokemon.name} was badly poisoned!")
            else:
                if pokemon.set_status(StatusEffect.POISON, duration=5):
                    messages.append(f"{pokemon.name} was poisoned!")
                    
        return messages
        
    def _check_aura_abilities(self) -> None:
        """Check and apply aura effects from Pokemon abilities."""
        # Reset aura tracking
        self.active_auras.clear()
        self.aura_break_active = False
        
        # Check both Pokemon for aura abilities
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if pokemon.ability and pokemon.ability.type == AbilityType.AURA:
                if pokemon.ability.aura_effect == AuraType.BREAK:
                    self.aura_break_active = True
                else:
                    self.active_auras.add(pokemon.ability.aura_effect)
                    
    def _check_terrain_abilities(self) -> None:
        """Check and apply terrain effects from Pokemon abilities."""
        # Check both Pokemon for terrain abilities
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if pokemon.ability and pokemon.ability.type == AbilityType.TERRAIN:
                if pokemon.ability.terrain_effect:
                    self.terrain = pokemon.ability.terrain_effect
                    self.terrain_duration = 5  # Terrain lasts 5 turns
        
    def can_move(self, pokemon: Pokemon) -> Tuple[bool, Optional[str]]:
        """Check if a Pokemon can move this turn.
        
        Args:
            pokemon: The Pokemon trying to move
            
        Returns:
            Tuple[bool, Optional[str]]: Whether the Pokemon can move and any message
        """
        if pokemon.status == StatusEffect.PARALYSIS:
            # 25% chance to be fully paralyzed (using randint for better distribution)
            if random.randint(1, 4) == 1:
                return False, f"{pokemon.name} is fully paralyzed!"
        elif pokemon.status == StatusEffect.SLEEP:
            # Cannot move while sleeping
            return False, f"{pokemon.name} is fast asleep!"
        elif pokemon.status == StatusEffect.FREEZE:
            # Cannot move while frozen
            return False, f"{pokemon.name} is frozen solid!"
        return True, None
        
    def execute_turn(self, move: Move, target: Pokemon) -> TurnResult:
        """Execute a turn using the selected move.
        
        Args:
            move: The move to use
            target: The target Pokemon
            
        Returns:
            TurnResult: The result of the turn
        """
        result = TurnResult()
        
        # No need to set sleep duration here since we set it when applying the status
        
        # Check if Pokemon can move (use the Pokemon making the move)
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
        if not move.use():
            result.messages.append(f"{move.name} has no PP left!")
            return result
            
        # Accuracy check using the attacking Pokemon's accuracy and target's evasion
        accuracy = move.accuracy * attacker.get_stat_multiplier("accuracy")
        evasion = target.get_stat_multiplier("evasion")
        if random.random() * 100 > accuracy / evasion:
            result.move_missed = True
            result.messages.append(f"{move.name} missed!")
            return result
            
        # Calculate and deal damage for damaging moves
        if move.is_damaging:
            # Fire moves thaw the user
            if move.type == Type.FIRE and attacker.status == StatusEffect.FREEZE:
                attacker.set_status(None)
                result.messages.append(f"{attacker.name} thawed out!")
                
            # Critical hit check (1/24 chance)
            result.critical_hit = random.random() < 1/24
            
            # Get type effectiveness
            result.effectiveness = self.type_chart.get_multiplier(move.type, target.types)
            
            # Calculate damage using the correct attacker
            damage = self._calculate_damage(move, attacker, target, result.critical_hit)
            result.damage_dealt = target.take_damage(damage)
            
            # Add damage message
            if result.critical_hit:
                result.messages.append("A critical hit!")
            if result.effectiveness > 1:
                result.messages.append("It's super effective!")
                # Check for super effective held items
                effect = target.check_held_item(HeldItemTrigger.SUPER_EFFECTIVE, move_effectiveness=result.effectiveness)
                if effect and effect.type == ItemType.BERRY:
                    target.heal(effect.value)
                    result.messages.append(f"{target.name}'s {target.held_item.name} restored some HP!")
            elif result.effectiveness < 1:
                result.messages.append("It's not very effective...")
                
            # Check for low HP held items
            if target.current_hp > 0:  # Only if not fainted
                hp_percent = target.current_hp / target.stats.hp
                effect = target.check_held_item(HeldItemTrigger.LOW_HP, hp_percent=hp_percent)
                if effect:
                    if effect.type == ItemType.BERRY:
                        target.heal(effect.value)
                        result.messages.append(f"{target.name}'s {target.held_item.name} restored some HP!")
                    elif effect.type == ItemType.HELD and target.held_item.name == "Focus Sash":
                        if target.current_hp == 1:
                            result.messages.append(f"{target.name} hung on using its Focus Sash!")
            
        # Apply move effects
        for effect in move.effects:
            # Status effects
            if effect.status and random.random() * 100 <= effect.status_chance:
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
        """Calculate damage for a damaging move.
        
        Args:
            move: The move being used
            attacker: The attacking Pokemon
            defender: The defending Pokemon
            critical: Whether the move is a critical hit
            
        Returns:
            int: The amount of damage to deal
        """
        # Get attack and defense stats with current weather
        if move.category == MoveCategory.PHYSICAL:
            attack = attacker.stats.attack * attacker.get_stat_multiplier("attack", self.weather)
            defense = defender.stats.defense * defender.get_stat_multiplier("defense", self.weather)
        else:  # Special
            attack = attacker.stats.special_attack * attacker.get_stat_multiplier("special_attack", self.weather)
            defense = defender.stats.special_defense * defender.get_stat_multiplier("special_defense", self.weather)
            
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
        
        # Apply speed-based ability boosts for turn order
        attacker_speed = attacker.stats.speed * attacker.get_stat_multiplier("speed", self.weather)
        
        # Apply weather boost
        damage *= move.get_weather_multiplier(self.weather)
        
        # Apply type-enhancing item boost
        if attacker.held_item and attacker.held_item.effect.type == ItemType.TYPE_BOOST:
            if attacker.held_item.trigger == HeldItemTrigger.PASSIVE:
                damage *= (1 + attacker.held_item.effect.value / 100)  # Convert percentage to multiplier
                
        # Apply terrain boost
        if self.terrain:
            # Skip if Pokemon is not grounded
            is_grounded = Type.FLYING not in attacker.types
            
            if is_grounded:
                if self.terrain == TerrainType.GRASSY and move.type == Type.GRASS:
                    damage *= 1.3  # 30% boost to Grass moves
                elif self.terrain == TerrainType.ELECTRIC and move.type == Type.ELECTRIC:
                    damage *= 1.3  # 30% boost to Electric moves
                elif self.terrain == TerrainType.PSYCHIC and move.type == Type.PSYCHIC:
                    damage *= 1.3  # 30% boost to Psychic moves
                elif self.terrain == TerrainType.MISTY and move.type == Type.DRAGON:
                    damage *= 0.5  # 50% reduction to Dragon moves
                    
        # Apply aura boost
        if self.active_auras:
            aura_multiplier = 0.33  # 33% boost
            if self.aura_break_active:
                aura_multiplier = -0.25  # 25% reduction instead
                
            if AuraType.FAIRY in self.active_auras and move.type == Type.FAIRY:
                damage *= (1 + aura_multiplier)
            elif AuraType.DARK in self.active_auras and move.type == Type.DARK:
                damage *= (1 + aura_multiplier)
                
        return int(damage)
        
    @property
    def is_over(self) -> bool:
        """Check if the battle is over."""
        return self.player_pokemon.is_fainted or self.enemy_pokemon.is_fainted
        
    def use_item(self, item: Item, target: Pokemon) -> ItemResult:
        """Use an item on a target Pokemon.
        
        Args:
            item: The item to use
            target: The target Pokemon
            
        Returns:
            ItemResult: The result of using the item
        """
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
        """Apply end-of-turn weather effects.
        
        Returns:
            TurnResult: The result of applying weather effects
        """
        result = TurnResult()
        
        # Check passive held items
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if pokemon.is_fainted:
                continue
                
            effect = pokemon.check_held_item(HeldItemTrigger.PASSIVE)
            if effect:
                if effect.type == ItemType.HELD:
                    # Leftovers healing
                    heal_amount = min(
                        pokemon.stats.hp // 16,  # 1/16 max HP
                        pokemon.stats.hp - pokemon.current_hp
                    )
                    if heal_amount > 0:
                        pokemon.heal(heal_amount)
                        result.messages.append(
                            f"{pokemon.name} restored a little HP due to its {pokemon.held_item.name}!"
                        )
        
        if self.weather == Weather.CLEAR:
            return result
            
        # Add weather message
        if self.weather == Weather.RAIN:
            result.messages.append("Rain continues to fall.")
        elif self.weather == Weather.SUN:
            result.messages.append("The sunlight is strong.")
        elif self.weather == Weather.SANDSTORM:
            result.messages.append("The sandstorm rages!")
        elif self.weather == Weather.HAIL:
            result.messages.append("Hail continues to fall!")
            
        # Apply damage for sandstorm/hail
        if self.weather in (Weather.SANDSTORM, Weather.HAIL):
            for pokemon in (self.player_pokemon, self.enemy_pokemon):
                # Skip Rock/Ground/Steel types in sandstorm
                if (self.weather == Weather.SANDSTORM and 
                    any(t in (Type.ROCK, Type.GROUND, Type.STEEL) for t in pokemon.types)):
                    continue
                    
                # Skip Ice types in hail
                if self.weather == Weather.HAIL and Type.ICE in pokemon.types:
                    continue
                    
                # Deal 1/16 max HP damage
                damage = pokemon.stats.hp // 16
                pokemon.current_hp = max(0, pokemon.current_hp - damage)
                
                # Add damage message
                weather_name = "sandstorm" if self.weather == Weather.SANDSTORM else "hail"
                result.messages.append(f"{pokemon.name} is buffeted by the {weather_name}!")
                
        return result
        
    def end_turn(self) -> TurnResult:
        """End the current turn and apply any effects.
        
        Returns:
            TurnResult: The result of ending the turn
        """
        result = TurnResult()
        
        # Apply status effects
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if pokemon.is_fainted:
                continue
                
            # Store current status
            current_status = pokemon.status
            
            # Check for status-triggered items
            if current_status:
                effect = pokemon.check_held_item(HeldItemTrigger.STATUS)
                if effect:
                    if effect.type == ItemType.BERRY:
                        if effect.cures_status and current_status in effect.cures_status:
                            pokemon.set_status(None)
                            result.messages.append(
                                f"{pokemon.name}'s {pokemon.held_item.name} cured its {current_status.name.lower()}!"
                            )
                            continue
            
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
            # Apply damage over time effects if status wasn't cleared
            elif current_status == StatusEffect.POISON:
                damage = pokemon.stats.hp // 8
                pokemon.take_damage(damage)
                result.messages.append(f"{pokemon.name} is hurt by poison!")
            elif current_status == StatusEffect.BURN:
                damage = pokemon.stats.hp // 16  # Burn does less damage than poison
                pokemon.take_damage(damage)
                result.messages.append(f"{pokemon.name} is hurt by its burn!")
                
        # Apply weather effects
        weather_result = self.apply_weather_effects()
        result.messages.extend(weather_result.messages)
        
        # Apply terrain healing
        if self.terrain == TerrainType.GRASSY:
            for pokemon in (self.player_pokemon, self.enemy_pokemon):
                if pokemon.is_fainted:
                    continue
                    
                # Skip if Pokemon is not grounded
                if Type.FLYING in pokemon.types:
                    continue
                    
                # Heal 1/16 max HP
                heal_amount = min(
                    pokemon.stats.hp // 16,
                    pokemon.stats.hp - pokemon.current_hp
                )
                if heal_amount > 0:
                    pokemon.heal(heal_amount)
                    result.messages.append(
                        f"{pokemon.name} was healed by the grassy terrain!"
                    )
        
        # Decrease weather duration
        if self.weather_duration > 0:
            self.weather_duration -= 1
            if self.weather_duration == 0:
                weather_name = self.weather.name.lower()
                if weather_name == "sun":
                    weather_name = "harsh sunlight"
                result.messages.append(f"The {weather_name} subsided.")
                self.weather = Weather.CLEAR
                
        # Decrease terrain duration
        if self.terrain_duration > 0:
            self.terrain_duration -= 1
            if self.terrain_duration == 0:
                terrain_name = self.terrain.name.lower()
                result.messages.append(f"The {terrain_name} terrain faded!")
                self.terrain = None
                
        return result
        
    @property
    def winner(self) -> Optional[Pokemon]:
        """Get the winning Pokemon if the battle is over."""
        if not self.is_over:
            return None
        return self.enemy_pokemon if self.player_pokemon.is_fainted else self.player_pokemon
