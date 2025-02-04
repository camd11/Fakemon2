"""Factory for creating Item instances from data files."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..core.item import Item, ItemType, ItemEffect

class ItemFactory:
    """Factory for creating Item instances from data."""
    
    def __init__(self, data_dir: str = "src/data") -> None:
        """Initialize the factory with data from JSON files.
        
        Args:
            data_dir: Directory containing the data files
            
        Raises:
            FileNotFoundError: If the data directory or required files don't exist
        """
        self.data_dir = Path(data_dir)
        self._items_data: Dict = {}
        self._load_data()
        
    def _load_data(self) -> None:
        """Load item data from JSON file."""
        with open(self.data_dir / "items.json") as f:
            self._items_data = json.load(f)
            
    def create_item(self, item_id: str) -> Optional[Item]:
        """Create an item instance from its ID.
        
        Args:
            item_id: The ID of the item in the items data
            
        Returns:
            Item instance or None if item_id is not found
        """
        if item_id not in self._items_data:
            return None
            
        item_data = self._items_data[item_id]
        effect_data = item_data["effect"]
        
        # Create the effect
        effect = ItemEffect(
            type=ItemType[effect_data["type"]],
            value=effect_data["value"],
            duration=effect_data.get("duration"),
            conditions=effect_data.get("conditions")
        )
        
        return Item(
            name=item_data["name"],
            description=item_data["description"],
            effect=effect,
            price=item_data["price"],
            single_use=item_data["single_use"]
        )
        
    def get_all_items(self) -> List[Item]:
        """Get all available items.
        
        Returns:
            List of all items in the game
        """
        return [
            self.create_item(item_id)
            for item_id in self._items_data
        ]
        
    def get_items_by_type(self, item_type: ItemType) -> List[Item]:
        """Get all items of a specific type.
        
        Args:
            item_type: The type of items to get
            
        Returns:
            List of items matching the specified type
        """
        return [
            self.create_item(item_id)
            for item_id, data in self._items_data.items()
            if data["effect"]["type"] == item_type.name
        ]
        
    def get_items_by_max_price(self, max_price: int) -> List[Item]:
        """Get all items costing up to max_price.
        
        Args:
            max_price: The maximum price to include
            
        Returns:
            List of items within the price range
        """
        return [
            self.create_item(item_id)
            for item_id, data in self._items_data.items()
            if data["price"] <= max_price
        ]
        
    def get_purchasable_items(self, money: int) -> List[Item]:
        """Get all items that can be purchased with the given amount of money.
        
        Args:
            money: The amount of money available
            
        Returns:
            List of items that can be purchased
        """
        return self.get_items_by_max_price(money)
