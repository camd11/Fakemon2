# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup and documentation
  - Comprehensive UI component documentation
  - Implementation details and testing guides
- Item system implementation (91% test coverage)
  - Core Item class with effects and conditions
  - ItemFactory service for data management
  - JSON data for all game items
  - Support for healing, PP restore, status cures, and more
  - Design document with architecture and implementation plans
  - Project structure and guidelines
  - Comprehensive test suite with 76 tests
  - Development status tracking
- Core battle system implementation (100% test coverage)
  - Pokemon class with stats, moves, and battle state
  - Move class with effects and PP system
  - Type system with effectiveness calculations
  - Battle mechanics including damage calculation
- Data management (100% test coverage)
  - JSON data files for Pokemon, moves, and type effectiveness
  - Factory system for creating game entities
- Game state management (90%+ test coverage)
  - Battle manager for handling battle flow
  - Game state tracking and progression
  - Basic catching mechanics
- Terminal UI
  - Rich-based battle view (100% test coverage)
  - Input handling and validation (100% test coverage)
  - Game phase transitions
- Initial game content
  - Classic starter Pokemon (Bulbasaur, Charmander, Squirtle)
  - Basic moves (Tackle, Scratch, elemental moves, etc.)
  - Status moves and effects
- Testing infrastructure
  - pytest configuration with coverage reporting
  - Core domain tests with 98%+ coverage
  - Service layer integration tests
  - UI component tests
  - Mock battle scenarios and game progression tests

### Changed
- Improved test coverage across all core components
- Enhanced battle system reliability
- Refined terminal UI rendering with comprehensive test suite
- Optimized game state management
- Completed UI layer testing with 100% coverage
- Added item system integration with core game mechanics

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Battle system edge cases
- Type effectiveness calculations
- Move PP management
- Message history handling

### Security
- N/A

## [0.1.0] - 2025-02-04

### Added
- Initial project structure
- Basic game mechanics
- Test infrastructure
