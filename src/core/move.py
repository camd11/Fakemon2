"""Move implementation for Pokemon battles."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
from .types import Type

class MoveCategory(Enum):
    """Categories of moves determining which stats are used in damage calculation."""
    PHYSICAL = auto()  # Uses Attack and Defense
    SPECIAL = auto()   # Uses Special Attack and Special Defense
    STATUS = auto()    # No direct damage

class StatusEffect(Enum):
    """Status conditions that can be inflicted by moves."""
    BURN = auto()      # Reduces Attack, deals damage over time
    FREEZE = auto()    # Cannot move
    PARALYSIS = auto() # May not move, reduced Speed
    POISON = auto()    # Deals damage over time
    SLEEP = auto()     # Cannot move
    CONFUSION = auto() # May hurt self

@dataclass
class Effect:
    """Represents additional effects a move may have."""
    status: Optional[StatusEffect] = None
    status_chance: float = 0.0
    stat_changes: dict[str, int] = None  # e.g., {"attack": -1} for lowering attack
    
    def __post_init__(self):
        """Initialize empty stat_changes if None."""
        if self.stat_changes is None:
            self.stat_changes = {}

class Move:
    """A move that can be used in battle."""
    
    def __init__(
        self,
        name: str,
        type_: Type,
        category: MoveCategory,
        power: int,
        accuracy: int,
        pp: int,
        effects: List[Effect] = None
    ) -> None:
        """Initialize a move.
        
        Args:
            name: Name of the move
            type_: Type of the move
            category: Physical, Special, or Status
            power: Base power (0 for status moves)
            accuracy: Accuracy percentage (0-100)
            pp: Power points (number of times move can be used)
            effects: List of additional effects the move may have
        """
        self.name = name
        self.type = type_
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.max_pp = pp
        self.current_pp = pp
        self.effects = effects or []
        
    def use(self) -> bool:
        """Use the move, consuming one PP.
        
        Returns:
            bool: True if the move was used successfully, False if out of PP
        """
        if self.current_pp <= 0:
            return False
        self.current_pp -= 1
        return True
        
    def restore_pp(self, amount: int = None) -> None:
        """Restore PP to the move.
        
        Args:
            amount: Amount of PP to restore. If None, fully restore PP.
        """
        if amount is None:
            self.current_pp = self.max_pp
        else:
            self.current_pp = min(self.max_pp, self.current_pp + amount)
            
    @property
    def is_damaging(self) -> bool:
        """Check if the move deals direct damage."""
        return self.category in (MoveCategory.PHYSICAL, MoveCategory.SPECIAL)
