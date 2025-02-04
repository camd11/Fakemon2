# Fakemon2

A Pokemon-inspired roguelike RPG where you battle through 200 levels of increasingly difficult Pokemon encounters. The game features a complete battle system with type effectiveness, status effects, and catching mechanics.

## Project Status

- Core battle system: ✅ Complete with 100% test coverage
- Service layer: ✅ Complete with 90%+ test coverage
- UI layer: 🔄 In progress (Input handling complete, Battle view testing ongoing)
- Item system: 📝 Planned for next sprint

See [DEVELOPMENT_STATUS.md](docs/DEVELOPMENT_STATUS.md) for detailed progress tracking.

## Features

- Complete Pokemon battle system
- Roguelike progression through 200 levels
- Terminal-based UI with rich formatting
- Catching system with party management
- Classic starter Pokemon
- Type effectiveness and status effects

## Requirements

- Python 3.10+
- Dependencies listed in requirements.txt

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/Fakemon2.git
cd Fakemon2
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests to verify setup:
```bash
python3 -m pytest
```

5. Start the game:
```bash
python3 src/main.py
```

## Project Structure

```
fakemon2/
├── docs/                 # Documentation
│   ├── DESIGN.md        # Architecture and implementation details
│   ├── CHANGELOG.md     # Version history and changes
│   └── DEVELOPMENT_STATUS.md  # Current progress and next steps
├── src/
│   ├── core/            # Core game mechanics
│   │   ├── pokemon.py   # Pokemon class and stats
│   │   ├── move.py      # Move system
│   │   ├── battle.py    # Battle mechanics
│   │   └── types.py     # Type system
│   ├── services/        # Game services
│   │   ├── battle_manager.py    # Battle flow control
│   │   ├── pokemon_factory.py   # Entity creation
│   │   └── game_state.py        # Game progression
│   ├── data/            # Game data in JSON format
│   └── ui/              # Terminal interface
├── tests/               # Test suite
│   ├── core/            # Core mechanics tests
│   ├── services/        # Service layer tests
│   └── ui/              # UI component tests
└── requirements.txt     # Python dependencies
```

## Testing

Run different test configurations:
```bash
# Run all tests with coverage
python3 -m pytest

# Run specific test file
python3 -m pytest tests/core/test_pokemon.py

# Run tests matching pattern
python3 -m pytest -k "battle"
```

Coverage reports are generated in `htmlcov/`.

## Current Test Coverage

- Core domain: 98-100%
- Services: 90-100%
- UI: Input handler 100%, Battle view in progress
- Overall: 67% (including unimplemented features)

## Next Steps

1. Complete UI Layer Testing
   - Finish battle view tests
   - Add integration tests
   - Target 80%+ coverage

2. Implement Item System
   - Create Item class
   - Add inventory management
   - Implement reward system

3. Enhance Battle System
   - Complete weather effects
   - Add status effect duration
   - Improve message system

See [DEVELOPMENT_STATUS.md](docs/DEVELOPMENT_STATUS.md) for detailed task list.

## Common Development Tasks

### Adding a New Pokemon
1. Add entry to `src/data/pokemon.json`
2. Update type effectiveness if needed
3. Add new moves if required
4. Update tests
5. Verify in game

### Implementing New Features
1. Start with core domain in `src/core/`
2. Add necessary data files
3. Implement service layer integration
4. Add UI components
5. Write comprehensive tests
6. Update documentation

### Debugging
1. Check test coverage for affected area
2. Use Rich library's console.print for debugging
3. Verify JSON data integrity
4. Check game state transitions

## Contributing

1. Create a new branch for your feature
2. Write tests first (TDD approach)
3. Implement the feature
4. Ensure tests pass and coverage maintains
5. Update documentation
6. Create pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pokemon is a trademark of Nintendo/Game Freak
- This is a fan project for educational purposes
