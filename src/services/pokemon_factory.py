"""Factory for creating Pokemon instances from data files."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Type
from ..core.pokemon import Pokemon, Stats
from ..core.move import Move, MoveCategory, Effect, StatusEffect
from ..core.types import Type, TypeEffectiveness

class PokemonFactory:
    """Factory for creating Pokemon instances from data."""
    
    def __init__(self, data_dir: str = "src/data") -> None:
        """Initialize the factory with data from JSON files.
        
        Args:
            data_dir: Directory containing the data files
        """
        self.data_dir = Path(data_dir)
        self._pokemon_data: Dict = {}
        self._moves_data: Dict = {}
        self._type_chart: TypeEffectiveness = TypeEffectiveness()
        self._load_data()
        
    def _load_data(self) -> None:
        """Load all data from JSON files."""
        # Load Pokemon data
        with open(self.data_dir / "pokemon.json") as f:
            self._pokemon_data = json.load(f)
            
        # Load moves data
        with open(self.data_dir / "moves.json") as f:
            self._moves_data = json.load(f)
            
        # Load and set up type effectiveness
        with open(self.data_dir / "types.json") as f:
            type_data = json.load(f)
            self._type_chart.load_from_json(type_data)
            
    def create_move(self, move_id: str) -> Optional[Move]:
        """Create a move instance from its ID.
        
        Args:
            move_id: The ID of the move in the moves data
            
        Returns:
            Move instance or None if move_id is not found
        """
        if move_id not in self._moves_data:
            return None
            
        move_data = self._moves_data[move_id]
        effects = []
        
        for effect_data in move_data["effects"]:
            status = (StatusEffect[effect_data["status"].upper()]
                     if effect_data["status"] else None)
            effects.append(Effect(
                status=status,
                status_chance=effect_data["status_chance"],
                stat_changes=effect_data["stat_changes"]
            ))
            
        return Move(
            name=move_data["name"],
            type_=Type[move_data["type"].upper()],
            category=MoveCategory[move_data["category"].upper()],
            power=move_data["power"],
            accuracy=move_data["accuracy"],
            pp=move_data["pp"],
            effects=effects
        )
        
    def create_pokemon(
        self,
        pokemon_id: str,
        level: int,
        moves: List[str] = None
    ) -> Optional[Pokemon]:
        """Create a Pokemon instance from its ID.
        
        Args:
            pokemon_id: The ID of the Pokemon in the pokemon data
            level: The level to create the Pokemon at
            moves: Optional list of move IDs. If None, uses starting_moves
            
        Returns:
            Pokemon instance or None if pokemon_id is not found
        """
        if pokemon_id not in self._pokemon_data:
            return None
            
        pokemon_data = self._pokemon_data[pokemon_id]
        
        # Create base stats
        base_stats = Stats(**pokemon_data["base_stats"])
        
        # Get types
        types = tuple(Type[t.upper()] for t in pokemon_data["types"])
        
        # Get moves
        if moves is None:
            moves = pokemon_data["starting_moves"]
        move_instances = []
        for move_id in moves[:4]:  # Limit to 4 moves
            move = self.create_move(move_id)
            if move:
                move_instances.append(move)
                
        return Pokemon(
            name=pokemon_data["name"],
            types=types,
            base_stats=base_stats,
            level=level,
            moves=move_instances
        )
        
    def create_random_pokemon(
        self,
        level: int,
        exclude_ids: List[str] = None
    ) -> Pokemon:
        """Create a random Pokemon at the specified level.
        
        Args:
            level: The level to create the Pokemon at
            exclude_ids: Optional list of Pokemon IDs to exclude
            
        Returns:
            A random Pokemon instance
        """
        import random
        
        available_ids = list(self._pokemon_data.keys())
        if exclude_ids:
            available_ids = [pid for pid in available_ids if pid not in exclude_ids]
            
        pokemon_id = random.choice(available_ids)
        pokemon_data = self._pokemon_data[pokemon_id]
        
        # Randomly select moves from possible moves
        num_moves = random.randint(1, min(4, len(pokemon_data["possible_moves"])))
        moves = random.sample(pokemon_data["possible_moves"], num_moves)
        
        return self.create_pokemon(pokemon_id, level, moves)
        
    @property
    def type_chart(self) -> TypeEffectiveness:
        """Get the type effectiveness chart."""
        return self._type_chart
