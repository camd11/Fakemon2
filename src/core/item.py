"""Item system implementation."""

from enum import Enum, auto
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass
from .move import StatusEffect

class ItemType(Enum):
    """Types of items in the game."""
    HEALING = auto()  # Restores HP
    POKEBALL = auto()  # For catching Pokemon
    HELD = auto()     # Can be held by Pokemon
    STATUS = auto()   # Cures status conditions
    PP = auto()       # Restores move PP
    BOOST = auto()    # Temporarily boosts stats

@dataclass
class ItemEffect:
    """Represents the effect of using an item."""
    type: ItemType
    value: int  # Amount of effect (e.g., HP restored, catch rate bonus)
    duration: Optional[int] = None  # For temporary effects, None means instant
    conditions: Optional[Dict[str, Any]] = None  # Special conditions for effect
    cures_status: Optional[Set[StatusEffect]] = None  # Status effects this item cures

class Item:
    """Represents an item in the game."""
    
    def __init__(
        self,
        name: str,
        description: str,
        effect: ItemEffect,
        price: int,
        single_use: bool = True
    ) -> None:
        """Initialize an item.
        
        Args:
            name: The name of the item
            description: A description of what the item does
            effect: The ItemEffect that defines the item's behavior
            price: The cost of the item in shops
            single_use: Whether the item is consumed on use
        """
        self.name = name
        self.description = description
        self.effect = effect
        self.price = price
        self.single_use = single_use
        
    def can_use(self, target: Any) -> bool:
        """Check if the item can be used on the target.
        
        Args:
            target: The target to check (usually a Pokemon)
            
        Returns:
            bool: True if the item can be used, False otherwise
        """
        # First check type-specific conditions
        if self.effect.type == ItemType.HEALING:
            if hasattr(target, "current_hp") and hasattr(target, "stats"):
                if target.current_hp >= target.stats.hp:
                    return False
                    
        elif self.effect.type == ItemType.PP:
            if hasattr(target, "moves"):
                if not any(move.current_pp < move.max_pp for move in target.moves):
                    return False
                    
        elif self.effect.type == ItemType.STATUS:
            if hasattr(target, "status"):
                if target.status is None:
                    return False
                # Check if this item can cure the current status
                if self.effect.cures_status and target.status not in self.effect.cures_status:
                    return False
                    
        elif self.effect.type == ItemType.POKEBALL:
            if self.effect.conditions and "is_trainer_battle" in self.effect.conditions:
                if self.effect.conditions["is_trainer_battle"]:
                    return False
                    
        # Then check additional conditions if any exist
        if self.effect.conditions:
            for condition, value in self.effect.conditions.items():
                if condition == "is_trainer_battle":
                    continue  # Already handled above
                if hasattr(target, condition):
                    if getattr(target, condition) != value:
                        return False
                        
        return True
        
    def use(self, target: Any) -> bool:
        """Use the item on a target.
        
        Args:
            target: The target to use the item on (usually a Pokemon)
            
        Returns:
            bool: True if the item was used successfully, False otherwise
        """
        if not self.can_use(target):
            return False
            
        # Apply effect based on type
        if self.effect.type == ItemType.HEALING:
            if hasattr(target, "current_hp") and hasattr(target, "stats"):
                target.current_hp = min(
                    target.current_hp + self.effect.value,
                    target.stats.hp
                )
                
        elif self.effect.type == ItemType.PP:
            if hasattr(target, "moves"):
                for move in target.moves:
                    move.current_pp = min(
                        move.current_pp + self.effect.value,
                        move.max_pp
                    )
                    
        elif self.effect.type == ItemType.STATUS:
            if hasattr(target, "status"):
                if not self.effect.cures_status or target.status in self.effect.cures_status:
                    target.status = None
                
        elif self.effect.type == ItemType.BOOST:
            # Temporary stat boosts handled by battle system
            pass
            
        return True
        
    def __str__(self) -> str:
        """Return a string representation of the item."""
        return f"{self.name} - {self.description}"
        
    def __eq__(self, other: object) -> bool:
        """Check if two items are equal."""
        if not isinstance(other, Item):
            return NotImplemented
        return (
            self.name == other.name
            and self.description == other.description
            and self.effect.type == other.effect.type
            and self.effect.value == other.effect.value
            and self.price == other.price
            and self.single_use == other.single_use
        )

# Define common status-curing items
FULL_HEAL = Item(
    name="Full Heal",
    description="Cures all status conditions.",
    effect=ItemEffect(
        type=ItemType.STATUS,
        value=0,  # Not used for status items
        cures_status={
            StatusEffect.POISON,
            StatusEffect.BURN,
            StatusEffect.PARALYSIS,
            StatusEffect.SLEEP,
            StatusEffect.FREEZE
        }
    ),
    price=600,
    single_use=True
)

ANTIDOTE = Item(
    name="Antidote",
    description="Cures poison.",
    effect=ItemEffect(
        type=ItemType.STATUS,
        value=0,
        cures_status={StatusEffect.POISON}
    ),
    price=100,
    single_use=True
)

BURN_HEAL = Item(
    name="Burn Heal",
    description="Heals burned Pokemon.",
    effect=ItemEffect(
        type=ItemType.STATUS,
        value=0,
        cures_status={StatusEffect.BURN}
    ),
    price=250,
    single_use=True
)

PARALYZE_HEAL = Item(
    name="Paralyze Heal",
    description="Cures paralysis.",
    effect=ItemEffect(
        type=ItemType.STATUS,
        value=0,
        cures_status={StatusEffect.PARALYSIS}
    ),
    price=200,
    single_use=True
)

AWAKENING = Item(
    name="Awakening",
    description="Wakes up sleeping Pokemon.",
    effect=ItemEffect(
        type=ItemType.STATUS,
        value=0,
        cures_status={StatusEffect.SLEEP}
    ),
    price=250,
    single_use=True
)

ICE_HEAL = Item(
    name="Ice Heal",
    description="Thaws frozen Pokemon.",
    effect=ItemEffect(
        type=ItemType.STATUS,
        value=0,
        cures_status={StatusEffect.FREEZE}
    ),
    price=250,
    single_use=True
)
