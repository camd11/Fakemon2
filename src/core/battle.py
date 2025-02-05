"""Battle implementation for Pokemon."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Dict, Set, Tuple
from .types import Type, TypeEffectiveness
from .move import Move, MoveCategory, StatusEffect
from .weather import Weather
from .ability import AbilityType, TerrainType, AuraType
from .item import HeldItemTrigger, ItemEffect, ItemType

class BattleAction(Enum):
    """Actions that can be taken in battle."""
    FIGHT = auto()
    SWITCH = auto()
    ITEM = auto()
    RUN = auto()

@dataclass
class TurnResult:
    """Result of a battle turn."""
    messages: List[str]
    damage_dealt: int = 0
    effectiveness: float = 1.0
    status_applied: Optional[StatusEffect] = None
    stat_changes: Dict[str, int] = None
    critical_hit: bool = False

    def __post_init__(self):
        """Initialize default values."""
        if self.stat_changes is None:
            self.stat_changes = {}

class Battle:
    """A battle between two Pokemon."""
    
    def __init__(
        self,
        pokemon1: 'Pokemon',
        pokemon2: 'Pokemon',
        type_chart: TypeEffectiveness
    ) -> None:
        """Initialize a battle.
        
        Args:
            pokemon1: First Pokemon
            pokemon2: Second Pokemon
            type_chart: Type effectiveness data
        """
        self.player_pokemon = pokemon1
        self.enemy_pokemon = pokemon2
        self.type_chart = type_chart
        self.weather = Weather.CLEAR
        self.turn_count = 0
        self.is_over = False
        self.winner = None
        self.weather_duration: Optional[int] = None
        self.terrain: Optional[TerrainType] = None
        self.terrain_duration: Optional[int] = None
        self.active_auras: Set[AuraType] = set()
        self.aura_break_active = False
        self.hazards1: Dict[str, int] = {}  # Hazards on pokemon1's side
        self.hazards2: Dict[str, int] = {}  # Hazards on pokemon2's side
        
        # Set initial weather from abilities
        for pokemon in (pokemon1, pokemon2):
            if pokemon.ability and pokemon.ability.type == AbilityType.WEATHER:
                self.weather = pokemon.ability.weather_effect
                self.weather_duration = None  # Weather from abilities lasts indefinitely
                break
                
        # Set initial terrain from abilities
        for pokemon in (pokemon1, pokemon2):
            if pokemon.ability and pokemon.ability.type == AbilityType.TERRAIN:
                self.terrain = pokemon.ability.terrain_effect
                self.terrain_duration = 5  # Terrain lasts 5 turns
                break
                
        # Set initial auras from abilities
        for pokemon in (pokemon1, pokemon2):
            if pokemon.ability and pokemon.ability.type == AbilityType.AURA:
                if pokemon.ability.aura_effect == AuraType.BREAK:
                    self.aura_break_active = True
                else:
                    self.active_auras.add(pokemon.ability.aura_effect)
                    
    def execute_turn(self, move: Move, target: 'Pokemon') -> TurnResult:
        """Execute a turn of battle.
        
        Args:
            move: The move being used
            target: The target Pokemon
            
        Returns:
            BattleResult: The result of the turn
        """
        messages = []
        damage = 0
        effectiveness = self.type_chart.get_effectiveness(move.type, target.types)
        
        # Calculate damage
        if move.category != MoveCategory.STATUS:
            # Get base power
            power = move.power
            
            # Calculate damage
            damage = self._calculate_damage(move, target, power)
            
        # Get the Pokemon using the move
        attacker = self.player_pokemon if target == self.enemy_pokemon else self.enemy_pokemon

        # Check if move can be used
        if move.type == Type.FIRE and attacker.status == StatusEffect.FREEZE:
            attacker.set_status(None)
            messages.append(f"{attacker.name} thawed out!")
        else:
            if attacker.status == StatusEffect.SLEEP:
                messages.append(f"{attacker.name} is fast asleep!")
                return TurnResult(messages)
            elif attacker.status == StatusEffect.FREEZE:
                messages.append(f"{attacker.name} is frozen solid!")
                return TurnResult(messages)
            elif attacker.status == StatusEffect.PARALYSIS:
                import random
                if random.random() < 0.25:  # 25% chance to be fully paralyzed
                    messages.append(f"{attacker.name} is fully paralyzed!")
                    return TurnResult(messages)

        # Apply damage
        if damage > 0:
            # Check Focus Sash before damage
            focus_sash_active = False
            if target.held_item and target.current_hp == target.stats.hp:
                item_effect = target.check_held_item(HeldItemTrigger.LETHAL_DAMAGE)
                if item_effect and item_effect.prevents_ko and damage >= target.current_hp:
                    damage = target.current_hp - 1
                    focus_sash_active = True
                    messages.append(f"{target.name} hung on using its Focus Sash!")

            actual_damage = target.take_damage(
                damage,
                move_category=move.category,
                move_type=move.type,
                effectiveness=effectiveness
            )
            messages.append(f"{target.name} took {actual_damage} damage!")

            # Check Oran Berry after damage
            if target.held_item and target.current_hp > 0:
                hp_percent = target.current_hp / target.stats.hp
                print(f"Debug - HP%: {hp_percent}, Has item: {target.held_item.name}")  # Debug print
                if hp_percent <= 0.25:  # 25% HP threshold
                    item_effect = target.check_held_item(HeldItemTrigger.LOW_HP, hp_percent=hp_percent)
                    print(f"Debug - Item effect: {item_effect}")  # Debug print
                    if (item_effect and item_effect.type == ItemType.BERRY and
                        target.held_item.name == "Oran Berry"):
                        print("Debug - Attempting to use Oran Berry")  # Debug print
                        healed = target.held_item.use(target)  # Use the item properly
                        print(f"Debug - Healed amount: {healed}")  # Debug print
                        if healed:
                            messages.append(f"{target.name} restored {healed} HP using its Oran Berry!")
                            target.held_item = None  # Consume the berry
            
        # Apply effects
        status_applied = None
        stat_changes = {}

        # Apply move effects
        for effect in move.effects:
            # Apply status effect
            if effect.status and effect.status_chance:
                # Set duration based on status type
                duration = None
                if effect.status == StatusEffect.SLEEP:
                    import random
                    duration = random.randint(1, 3)  # Sleep lasts 1-3 turns
                elif effect.status in (StatusEffect.POISON, StatusEffect.BURN, StatusEffect.PARALYSIS):
                    duration = 5  # These last 5 turns
                elif effect.status == StatusEffect.FREEZE:
                    duration = None  # Freeze lasts until thawed

                if target.set_status(effect.status, duration, attacker=self.player_pokemon, terrain=self.terrain):
                    status_applied = effect.status
                    messages.append(f"{target.name} was {effect.status.name.lower()}ed!")

            # Apply stat changes
            if effect.stat_changes:
                for stat, stages in effect.stat_changes.items():
                    if target.modify_stat(stat, stages):
                        stat_changes[stat] = stages
                        if stages > 0:
                            messages.append(f"{target.name}'s {stat} rose!")
                        else:
                            messages.append(f"{target.name}'s {stat} fell!")

        # Apply direct status effect (for backward compatibility)
        if move.status_effect and move.status_chance:
            # Set duration based on status type
            duration = None
            if move.status_effect == StatusEffect.SLEEP:
                import random
                duration = random.randint(1, 3)  # Sleep lasts 1-3 turns
            elif move.status_effect in (StatusEffect.POISON, StatusEffect.BURN, StatusEffect.PARALYSIS):
                duration = 5  # These last 5 turns
            elif move.status_effect == StatusEffect.FREEZE:
                duration = None  # Freeze lasts until thawed

            if target.set_status(move.status_effect, duration, attacker=self.player_pokemon, terrain=self.terrain):
                status_applied = move.status_effect
                messages.append(f"{target.name} was {move.status_effect.name.lower()}ed!")

        # Apply direct stat changes (for backward compatibility)
        if move.stat_changes:
            for stat, stages in move.stat_changes.items():
                if target.modify_stat(stat, stages):
                    stat_changes[stat] = stages
                    if stages > 0:
                        messages.append(f"{target.name}'s {stat} rose!")
                    else:
                        messages.append(f"{target.name}'s {stat} fell!")

        self.turn_count += 1
        if target.is_fainted:
            self.is_over = True
            self.winner = self.player_pokemon if target == self.enemy_pokemon else self.enemy_pokemon

        return TurnResult(messages, damage, effectiveness, status_applied, stat_changes)
        
        
    def end_turn(self) -> TurnResult:
        """Process end of turn effects.
        
        Returns:
            BattleResult: Messages from end of turn effects
        """
        messages = []

        # Process status effects and held items
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if not pokemon.is_fainted:
                # Check Lum Berry before status damage
                if pokemon.held_item and pokemon.status:
                    item_effect = pokemon.check_held_item(HeldItemTrigger.STATUS)
                    if item_effect and item_effect.type == ItemType.BERRY and item_effect.cures_status:
                        old_status = pokemon.status
                        pokemon.set_status(None)
                        messages.append(f"{pokemon.name} cured its {old_status.name.lower()} using Lum Berry!")
                        continue  # Skip status damage since it was cured

                # Status damage
                if pokemon.status == StatusEffect.POISON:
                    damage = pokemon.stats.hp // 8
                    actual_damage = pokemon.take_damage(damage)
                    messages.append(f"{pokemon.name} took {actual_damage} damage from poison!")
                elif pokemon.status == StatusEffect.SLEEP:
                    messages.append(f"{pokemon.name} is fast asleep!")
                    # Check if sleep should end
                    if pokemon.status_duration is not None:
                        pokemon.status_duration -= 1
                        if pokemon.status_duration <= 0:
                            pokemon.set_status(None)
                            messages.append(f"{pokemon.name} woke up!")
                elif pokemon.status == StatusEffect.FREEZE:
                    messages.append(f"{pokemon.name} is frozen solid!")
                    # 20% chance to thaw each turn
                    import random
                    if random.random() < 0.20:  # Increased from 1%
                        pokemon.set_status(None)
                        messages.append(f"{pokemon.name} thawed out!")
                elif pokemon.status == StatusEffect.BURN:
                    damage = pokemon.stats.hp // 16
                    actual_damage = pokemon.take_damage(damage)
                    messages.append(f"{pokemon.name} took {actual_damage} damage from its burn!")
                    
                # Status duration
                if pokemon.status_duration is not None:
                    pokemon.status_duration -= 1
                    if pokemon.status_duration <= 0:
                        old_status = pokemon.status
                        pokemon.set_status(None)
                        if old_status == StatusEffect.SLEEP:
                            messages.append(f"{pokemon.name} woke up!")
                        elif old_status == StatusEffect.BURN:
                            messages.append(f"{pokemon.name}'s burn healed!")
                        elif old_status == StatusEffect.POISON:
                            messages.append(f"{pokemon.name} was cured of its poison!")
                        elif old_status == StatusEffect.PARALYSIS:
                            messages.append(f"{pokemon.name} was cured of paralysis!")
                
        # Process weather effects
        weather_result = self.apply_weather_effects()
        messages.extend(weather_result.messages)

        # Process weather duration
        if self.weather != Weather.CLEAR and self.weather_duration is not None:
            self.weather_duration -= 1
            if self.weather_duration <= 0:
                old_weather = self.weather
                self.weather = Weather.CLEAR
                self.weather_duration = 0
                if old_weather == Weather.SANDSTORM:
                    messages.append("The sandstorm subsided.")
                elif old_weather == Weather.HAIL:
                    messages.append("The hail stopped.")
                elif old_weather == Weather.RAIN:
                    messages.append("The rain stopped.")
                elif old_weather == Weather.SUN:
                    messages.append("The harsh sunlight faded.")

        # Process terrain and held items
        if self.terrain and self.terrain_duration is not None:
            # Decrease duration
            self.terrain_duration -= 1
            if self.terrain_duration <= 0:
                self.terrain = None
                self.terrain_duration = None
                messages.append("The terrain faded!")

        # Process healing effects
        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if not pokemon.is_fainted:
                # Grassy terrain healing
                if self.terrain == TerrainType.GRASSY:
                    heal_amount = pokemon.stats.hp // 16
                    actual_heal = pokemon.heal(heal_amount)
                    if actual_heal > 0:
                        messages.append(f"{pokemon.name} restored {actual_heal} HP from the grassy terrain!")
                
                # Leftovers healing
                if pokemon.held_item and self.terrain != TerrainType.GRASSY:
                    item_effect = pokemon.check_held_item(HeldItemTrigger.END_TURN)
                    if item_effect and item_effect.type == ItemType.HELD:
                        heal_amount = pokemon.stats.hp // 16  # Leftovers heals 1/16 max HP
                        healed = pokemon.heal(heal_amount)
                        if healed > 0:
                            messages.append(f"{pokemon.name} restored {healed} HP with Leftovers!")
        return TurnResult(messages)
        
    def handle_faint(self, pokemon: 'Pokemon') -> List[str]:
        """Handle a Pokemon fainting.
        
        Args:
            pokemon: The fainted Pokemon
            
        Returns:
            List[str]: Messages about the faint
        """
        messages = [f"{pokemon.name} fainted!"]
        
        # Restore traced ability
        if pokemon.traced_ability:
            restore_message = pokemon.restore_ability()
            if restore_message:
                messages.append(restore_message)
                
        return messages

    def _calculate_damage(self, move: Move, target: 'Pokemon', power: int) -> int:
        """Calculate damage for a move.
        
        Args:
            move: The move being used
            target: The target Pokemon
            power: Base power after modifiers
            
        Returns:
            int: The amount of damage that would be dealt
        """
        # Get attack and defense stats
        if move.category == MoveCategory.PHYSICAL:
            attack = self.player_pokemon.stats.attack
            defense = target.stats.defense
        else:
            attack = self.player_pokemon.stats.special_attack
            defense = target.stats.special_defense
            
        # Apply stat stage multipliers
        attack *= self.player_pokemon.get_stat_multiplier(
            "attack" if move.category == MoveCategory.PHYSICAL else "special_attack",
            self.weather,
            target
        )
        defense *= target.get_stat_multiplier(
            "defense" if move.category == MoveCategory.PHYSICAL else "special_defense",
            self.weather,
            self.player_pokemon
        )
        
        # Calculate base damage
        damage = ((2 * self.player_pokemon.level / 5 + 2) * power * attack / defense / 50 + 2)

        # Calculate all multipliers first
        multiplier = 1.0

        # STAB multiplier
        multiplier *= self.player_pokemon.get_stab_multiplier(move)

        # Type effectiveness
        effectiveness = self.type_chart.get_effectiveness(move.type, target.types)
        multiplier *= effectiveness

        # Weather multiplier
        if self.weather in move.weather_multipliers:
            multiplier *= move.weather_multipliers[self.weather]

        # Type-enhancing item boost
        if self.player_pokemon.held_item:
            item_effect = self.player_pokemon.held_item.effect
            if item_effect.type == ItemType.TYPE_BOOST and move.type == item_effect.boost_type:
                multiplier *= (1 + item_effect.value / 100)  # Convert percentage to multiplier
            elif item_effect.type == ItemType.STAT_BOOST:
                if move.category == MoveCategory.PHYSICAL and self.player_pokemon.held_item.name == "Muscle Band":
                    multiplier *= (1 + item_effect.value / 100)
                elif move.category == MoveCategory.SPECIAL and self.player_pokemon.held_item.name == "Wise Glasses":
                    multiplier *= (1 + item_effect.value / 100)

        # Terrain boost
        if (self.terrain == TerrainType.GRASSY and move.type == Type.GRASS or
            self.terrain == TerrainType.ELECTRIC and move.type == Type.ELECTRIC or
            self.terrain == TerrainType.PSYCHIC and move.type == Type.PSYCHIC):
            multiplier *= 1.3
        elif self.terrain == TerrainType.MISTY and move.type == Type.DRAGON:
            multiplier *= 0.5

        # Aura boost
        if move.type == Type.FAIRY and AuraType.FAIRY in self.active_auras:
            if self.aura_break_active:
                multiplier *= 0.75  # 25% reduction
            else:
                multiplier *= 1.33  # 33% boost
        elif move.type == Type.DARK and AuraType.DARK in self.active_auras:
            if self.aura_break_active:
                multiplier *= 0.75  # 25% reduction
            else:
                multiplier *= 1.33  # 33% boost

        # Apply all multipliers at once
        damage = int(damage * multiplier)
        
        return damage

    def apply_weather_effects(self) -> TurnResult:
        """Apply end of turn weather effects.
        
        Returns:
            TurnResult: Messages from weather effects
        """
        messages = []

        # Weather message first
        if self.weather == Weather.SANDSTORM:
            messages.append("The sandstorm rages!")
            for pokemon in (self.player_pokemon, self.enemy_pokemon):
                if not any(t in (Type.ROCK, Type.GROUND, Type.STEEL) for t in pokemon.types):
                    damage = pokemon.stats.hp // 16
                    actual_damage = pokemon.take_damage(damage)
                    messages.append(f"{pokemon.name} is buffeted by the sandstorm!")
        elif self.weather == Weather.HAIL:
            messages.append("The hail continues to fall!")
            for pokemon in (self.player_pokemon, self.enemy_pokemon):
                if Type.ICE not in pokemon.types:
                    damage = pokemon.stats.hp // 16
                    actual_damage = pokemon.take_damage(damage)
                    messages.append(f"{pokemon.name} is pelted by hail!")
        elif self.weather == Weather.RAIN:
            messages.append("Rain continues to fall!")
        elif self.weather == Weather.SUN:
            messages.append("The sunlight is strong!")
                    
        return TurnResult(messages)
