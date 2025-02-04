# Fakemon2 Design Document

## Overview
Fakemon2 is a terminal-based roguelike game inspired by Pokemon and Slay the Spire. Players progress through 200 levels of increasingly difficult Pokemon battles, starting with a single starter Pokemon and 5 Pokeballs.

## Core Principles
- YAGNI (You Aren't Gonna Need It): Implement only what's necessary for current functionality
- KISS (Keep It Simple, Stupid): Maintain clear, straightforward implementations
- DRY (Don't Repeat Yourself): Utilize abstraction and inheritance appropriately
- SOLID: Follow object-oriented design principles for maintainable code

## Architecture

### Domain Layer (core/)
Core business logic and entity classes.

#### Pokemon Class
```python
class Pokemon:
    - stats: Stats            # HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed
    - current_hp: int
    - level: int
    - experience: int
    - moves: List[Move]      # Max 4 moves
    - types: List[Type]      # 1-2 types
    - status: Status         # Current status condition
    - held_item: Optional[Item]  # For future item system
```

#### Move Class
```python
class Move:
    - name: str
    - type: Type
    - power: int
    - accuracy: int
    - pp: int
    - category: MoveCategory  # Physical/Special/Status
    - effects: List[Effect]
```

#### Battle System
```python
class Battle:
    - player_pokemon: Pokemon
    - enemy_pokemon: Pokemon
    - weather: Weather
    - turn_count: int
    
    + execute_turn(action: Action) -> TurnResult
    + calculate_damage(move: Move, attacker: Pokemon, defender: Pokemon) -> int
    + check_battle_end() -> Optional[BattleResult]
```

### Service Layer (services/)
Manages game state and business operations.

#### BattleManager
- Controls battle flow
- Applies game rules
- Manages turn order
- Handles status effects

#### PokemonFactory
- Creates Pokemon instances from data
- Scales Pokemon to appropriate level
- Handles move learning

#### GameStateManager
- Tracks player progress
- Manages inventory
- Handles save/load (future feature)

### Data Layer (data/)
JSON files storing game data:
- pokemon.json: Base stats, types, learnable moves
- moves.json: Move properties and effects
- types.json: Type effectiveness chart
- items.json: Item effects (future feature)

### UI Layer (ui/)
Terminal-based interface:
```
+------------------------+
|Enemy: Charizard Lv.45  |
|HP: 143/143            |
|                       |
|Your: Blastoise Lv.43  |
|HP: 126/140           |
|                       |
|Actions:              |
|1. Fight  2. Switch   |
|3. Item   4. Run      |
+------------------------+
```

## Implementation Phases

### Phase 1: Core Battle System
1. Basic Data Structure Setup
   - Create core classes (Pokemon, Move)
   - Implement basic JSON data files
   - Set up factory classes
   Tests:
   - Pokemon creation
   - Move creation
   - Data loading

2. Battle Mechanics
   - Implement turn system
   - Add damage calculation
   - Add type effectiveness
   Tests:
   - Damage calculation
   - Type effectiveness
   - Turn execution

3. Status Effects
   - Add status conditions
   - Implement weather effects
   Tests:
   - Status application
   - Status effects
   - Weather effects

### Phase 2: Game Progression
1. Level System
   - Add experience system
   - Implement level scaling
   - Add move learning
   Tests:
   - Experience gain
   - Level up mechanics
   - Move learning

2. Roguelike Elements
   - Add random Pokemon generation
   - Implement level progression
   - Add catching mechanics
   Tests:
   - Pokemon generation
   - Catch rate calculation
   - Level progression

### Phase 3: Item System (Future)
1. Basic Items
   - Create Item class
   - Add inventory system
   - Implement basic items
   Tests:
   - Item effects
   - Inventory management

2. Equipment System
   - Add held items
   - Implement equipment effects
   Tests:
   - Equipment bonuses
   - Equipment restrictions

## Project Structure
```
fakemon2/
├── docs/
│   ├── DESIGN.md
│   └── CHANGELOG.md
├── src/
│   ├── core/
│   │   ├── pokemon.py
│   │   ├── move.py
│   │   ├── battle.py
│   │   └── types.py
│   ├── services/
│   │   ├── battle_manager.py
│   │   ├── pokemon_factory.py
│   │   └── game_state.py
│   ├── data/
│   │   ├── pokemon.json
│   │   ├── moves.json
│   │   └── types.json
│   └── ui/
│       ├── battle_view.py
│       ├── input_handler.py
│       └── logger.py
├── tests/
│   ├── core/
│   ├── services/
│   └── ui/
├── main.py
└── requirements.txt
```

## Development Guidelines
1. Write tests before implementing features
2. Update documentation with significant changes
3. Follow PEP 8 style guide
4. Use type hints for better code clarity
5. Keep methods small and focused
6. Document public APIs

## Testing Strategy
- Unit tests for all core functionality
- Integration tests for service layer
- System tests for game flow
- Test coverage target: 80%+

## Future Considerations
1. Save/Load system
2. More complex battle mechanics
3. Additional status effects
4. Special battle conditions
5. Achievement system
6. Browser-based UI conversion

This document will be updated as development progresses and new features are implemented.
