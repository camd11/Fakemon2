# Design Documentation

## Ability System

### Overview
The ability system provides Pokemon with special effects that can influence battle mechanics. The initial implementation focuses on status effect manipulation (immunities and resistances), with plans to expand to other ability types.

### Core Components

#### Ability Class
```python
class Ability:
    def __init__(self, name: str, type_: AbilityType, status_effects: Optional[tuple[StatusEffect, ...]] = None, resistance_multiplier: float = 0.5):
        self.name = name
        self.type = type_
        self.status_effects = status_effects or tuple()
        self.resistance_multiplier = resistance_multiplier
```

The Ability class is designed to be:
- Immutable: All attributes are set at initialization
- Type-safe: Uses enums for ability types and status effects
- Flexible: Optional parameters allow for different ability configurations

#### Ability Types
```python
class AbilityType(Enum):
    STATUS_IMMUNITY = auto()   # Prevents specific status effects
    STATUS_RESISTANCE = auto() # Reduces chance of status effects
```

Ability types are implemented as enums to:
- Ensure type safety
- Make code more maintainable
- Allow for easy extension with new ability types

### Integration with Battle System

#### Status Effect Application
1. Move Effect Processing
```python
# In Battle.execute_turn
for effect in move.effects:
    if effect.status:
        status_chance = effect.status_chance
        if target.ability:
            resistance = target.ability.modifies_status_chance(effect.status)
            if resistance is not None:
                status_chance *= resistance
```

2. Status Application Check
```python
# In Pokemon.set_status
def set_status(self, status: Optional[StatusEffect], duration: Optional[int] = None) -> bool:
    if self.ability and self.ability.prevents_status(status):
        return False
    # ... rest of status application logic
```

### Design Decisions

1. Separation of Concerns
   - Ability class handles ability-specific logic
   - Pokemon class integrates abilities into status management
   - Battle class coordinates ability effects during combat

2. Immutable Design
   - Abilities are configured at creation
   - No runtime modification of ability properties
   - Ensures predictable behavior

3. Type Safety
   - Extensive use of enums and type hints
   - Clear interfaces between components
   - Reduces potential for runtime errors

4. Extensibility
   - Enum-based ability types
   - Modular effect handling
   - Easy to add new ability types and effects

### Testing Strategy

1. Unit Tests
   - Individual ability functionality
   - Status effect interactions
   - Edge cases

2. Integration Tests
   - Battle system interaction
   - Multiple ability interactions
   - Complex scenarios

3. Test Categories
   ```python
   def test_status_immunity_ability():
       """Verify complete immunity to specific status effects."""
       
   def test_multiple_status_immunities():
       """Verify immunity to multiple status effects."""
       
   def test_status_resistance_ability():
       """Verify reduced chance of status effects."""
   ```

### Future Considerations

1. Additional Ability Types
   - Weather effects
   - Stat modifications
   - Turn order manipulation
   - Move type modifications

2. Performance Optimization
   - Caching ability checks
   - Optimizing status calculations
   - Reducing redundant checks

3. Error Handling
   - Validation of ability configurations
   - Graceful handling of edge cases
   - Comprehensive error messages

4. Extensibility
   ```python
   class AbilityType(Enum):
       STATUS_IMMUNITY = auto()
       STATUS_RESISTANCE = auto()
       # Future additions:
       WEATHER_EFFECT = auto()
       STAT_MODIFIER = auto()
       TURN_MODIFIER = auto()
   ```

### Implementation Guidelines

1. Adding New Abilities
   - Extend AbilityType enum
   - Implement new ability logic in Ability class
   - Add corresponding battle system integration
   - Create comprehensive tests

2. Modifying Existing Abilities
   - Ensure backward compatibility
   - Update affected battle mechanics
   - Extend test coverage
   - Document changes

3. Battle Integration
   - Check ability effects at appropriate points
   - Handle multiple ability interactions
   - Maintain clear execution flow

4. Error Handling
   ```python
   def modifies_status_chance(self, status: StatusEffect) -> Optional[float]:
       """Get status chance modifier, with validation."""
       if not isinstance(status, StatusEffect):
           raise ValueError(f"Invalid status type: {type(status)}")
       if self.type != AbilityType.STATUS_RESISTANCE:
           return None
       return self.resistance_multiplier
   ```

### Current Implementation Status

1. Status Effect Handling
    - Complete immunity to specific status effects
    - 50% resistance to specific status effects
    - Proper probability calculations verified
    - Separate handling for status vs. non-status moves

2. Ability Types
    - STATUS_IMMUNITY: Completely blocks specified status effects
    - STATUS_RESISTANCE: Reduces chance of specified status effects by 50%
    - Each type thoroughly tested with multiple scenarios

3. Battle Integration
    - Full integration with battle system
    - Proper handling of PP and status management
    - Clear separation between immunity and resistance effects

### Best Practices

1. Code Organization
   - Keep ability logic in Ability class
   - Use battle system for coordination
   - Maintain clear separation of concerns

2. Testing
   - Test each ability type separately
   - Include edge cases
   - Verify battle system integration

3. Documentation
   - Clear docstrings
   - Example usage
   - Implementation notes

4. Error Handling
   - Validate input parameters
   - Provide clear error messages
   - Handle edge cases gracefully
