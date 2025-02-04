# Fakemon2

A Pokemon-inspired roguelike RPG where you battle through 200 levels of increasingly difficult Pokemon encounters. The game features a complete battle system with type effectiveness, status effects, and catching mechanics.

## Features

- Complete Pokemon battle system
- Roguelike progression through 200 levels
- Terminal-based UI with rich formatting
- Catching system with party management
- Classic starter Pokemon
- Type effectiveness and status effects
- Future plans for item system and browser-based UI

## Requirements

- Python 3.10+
- Dependencies listed in requirements.txt

## Installation

### Local Development

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/your-username/Fakemon2.git
cd Fakemon2
```

3. Set up the upstream remote:
```bash
git remote add upstream https://github.com/original-username/Fakemon2.git
```

4. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

### Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "Description of changes"
```

3. Keep your fork up to date:
```bash
git fetch upstream
git rebase upstream/main
```

4. Push your changes:
```bash
git push origin feature-name
```

5. Create a Pull Request on GitHub

## Running the Game

From the project root directory:
```bash
python src/main.py
```

## How to Play

1. Choose a starter Pokemon (Bulbasaur, Charmander, or Squirtle)
2. Battle through increasingly difficult Pokemon
3. Use your moves strategically, considering:
   - Type effectiveness
   - PP management
   - Status effects
4. Catch wild Pokemon to build your team (5 Pokeballs to start)
5. Progress through 200 levels to win

### Battle Controls

- 1: Fight (then choose a move 1-4)
- 2: Pokemon (switch Pokemon - future feature)
- 3: Item (use Pokeball)
- 4: Run (disabled in roguelike mode)

## Project Structure

- `src/core/`: Core game mechanics and entities
- `src/services/`: Game state and business logic
- `src/data/`: Game data in JSON format
- `src/ui/`: Terminal user interface
- `docs/`: Design documentation and changelog
- `tests/`: Test suite (future addition)

## Development Status

### Completed Features
- Core battle system with type effectiveness and status effects
- Pokemon management with stats and moves
- Basic roguelike progression system
- Terminal-based UI using Rich library
- Comprehensive test suite (52 tests, 90%+ coverage for core/services)

### Current Focus
- UI layer testing implementation
- Item system design and development
- Battle system enhancements

See [DESIGN.md](docs/DESIGN.md) for detailed architecture and current status.
Changes are tracked in [CHANGELOG.md](docs/CHANGELOG.md).

## Development Workflow

### Setting Up Development Environment

1. Install Python dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run tests to verify setup:
```bash
python3 -m pytest
```

3. Start the game:
```bash
python3 src/main.py
```

### Development Process

1. Check current issues and project board
2. Create a new branch for your feature
3. Write tests first (TDD approach)
4. Implement the feature
5. Ensure tests pass and coverage maintains
6. Update documentation
7. Create pull request

### Code Organization

- `src/core/`: Core game mechanics (Pokemon, moves, battles)
- `src/services/`: Game state and business logic
- `src/data/`: JSON data files
- `src/ui/`: Terminal interface components
- `tests/`: Test suite organized by component
- `docs/`: Design docs and changelog

### Testing

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

### Documentation

Keep these up to date when making changes:
1. Update docstrings for new code
2. Modify DESIGN.md for architectural changes
3. Add significant changes to CHANGELOG.md
4. Update JSON schemas if data structure changes

## Roadmap

### Phase 1 (Current)
- ✅ Core battle system
- ✅ Basic game progression
- ✅ Terminal UI
- 🔄 UI testing
- 🔄 Item system

### Phase 2 (Planned)
- Advanced battle mechanics
- Save/Load system
- More Pokemon and moves
- Achievement system

### Phase 3 (Future)
- Browser-based UI
- Online features
- Custom Pokemon creation

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

## Getting Help

1. Check existing tests for examples
2. Review DESIGN.md for architecture
3. Examine JSON files for data structures
4. Look for similar implementations in codebase

## Contributing

### Guidelines

1. Follow the existing code style and conventions
2. Write clear commit messages
3. Include tests for new features
4. Update documentation as needed
5. Ensure all tests pass before submitting PR

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public methods
- Keep methods focused and small
- Use meaningful variable names

### Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md following the Keep a Changelog format
3. The PR will be merged once you have the sign-off of a maintainer

### Setting Up for Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Check code style:
```bash
black .
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pokemon is a trademark of Nintendo/Game Freak
- This is a fan project for educational purposes
