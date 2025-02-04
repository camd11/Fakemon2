# Item System Documentation

## Overview

The item system provides functionality for creating, managing, and using various items in the game. Items can heal Pokemon, restore PP, cure status conditions, boost stats, and catch wild Pokemon.

## Core Components

### Item Types

```python
class ItemType(Enum):
    HEALING   # Restores HP
    POKEBALL  # For catching Pokemon
    HELD      # Can be held by Pokemon
    STATUS    # Cures status conditions
    PP        # Restores move PP
    BOOST     # Temporarily boosts stats
```

### Item Effects

Items have effects defined by the `ItemEffect` class:
```python
@dataclass
class ItemEffect:
    type: ItemType          # Type of effect
    value: int             # Effect magnitude
    duration: Optional[int] # For temporary effects
    conditions: Optional[Dict[str, Any]] # Usage conditions
```

## Available Items

### Healing Items
- **Potion**: Restores 20 HP
- **Super Potion**: Restores 50 HP
- **Hyper Potion**: Restores 120 HP
- **Max Potion**: Fully restores HP

### PP Restoration
- **Ether**: Restores 10 PP
- **Max Ether**: Fully restores PP

### Status Cures
- **Antidote**: Cures poison
- **Awakening**: Wakes up sleeping Pokemon
- **Burn Heal**: Heals burns
- **Ice Heal**: Thaws frozen Pokemon
- **Full Heal**: Cures all status conditions

### Stat Boosts
- **X Attack**: Raises Attack
- **X Defense**: Raises Defense
- **X Speed**: Raises Speed

### Pokeballs
- **Poke Ball**: Basic catch rate (1x)
- **Great Ball**: Better catch rate (1.5x)
- **Ultra Ball**: Best catch rate (2x)

## Usage Conditions

Items have specific conditions that determine when they can be used:

1. **Healing Items**
   - Can only be used when Pokemon's HP is not full
   - Healing cannot exceed max HP

2. **PP Restoration**
   - Can only be used when at least one move has less than max PP
   - Restoration cannot exceed max PP

3. **Status Cures**
   - Can only be used when Pokemon has a status condition
   - Full Heal works on any status condition

4. **Stat Boosts**
   - Can be used at any time during battle
   - Effects last for specified duration
   - Multiple boosts of same type stack

5. **Pokeballs**
   - Cannot be used in trainer battles
   - Catch rate affected by Pokemon's HP and status

## Implementation Details

### Item Factory

The `ItemFactory` service manages item creation and data:

```python
class ItemFactory:
    def create_item(self, item_id: str) -> Optional[Item]
    def get_all_items(self) -> List[Item]
    def get_items_by_type(self, item_type: ItemType) -> List[Item]
    def get_items_by_max_price(self, max_price: int) -> List[Item]
    def get_purchasable_items(self, money: int) -> List[Item]
```

### Data Storage

Items are defined in `src/data/items.json` with the following structure:
```json
{
    "item_id": {
        "name": "Item Name",
        "description": "Item description",
        "effect": {
            "type": "EFFECT_TYPE",
            "value": 123,
            "duration": null,
            "conditions": {}
        },
        "price": 100,
        "single_use": true
    }
}
```

## Testing

The item system has comprehensive tests:

1. **Core Item Tests**
   - Item creation and properties
   - Effect application
   - Usage conditions
   - Edge cases

2. **ItemFactory Tests**
   - Data loading
   - Item creation
   - Filtering methods
   - Invalid cases

## Future Enhancements

1. **Battle Integration**
   - Add item use during battle
   - Implement stat boost effects
   - Add catch mechanics

2. **Inventory System**
   - Item storage limits
   - Sorting and categorization
   - Quick use shortcuts

3. **Shop System**
   - Variable pricing
   - Special deals
   - Rare items

## Best Practices

1. **Adding New Items**
   - Add entry to items.json
   - Define clear effect type and value
   - Set appropriate conditions
   - Add tests for new functionality

2. **Modifying Items**
   - Update effect values carefully
   - Consider balance implications
   - Test with different Pokemon stats
   - Verify conditions work as expected

3. **Error Handling**
   - Check item existence before use
   - Validate effect values
   - Handle invalid targets gracefully
   - Provide clear error messages
