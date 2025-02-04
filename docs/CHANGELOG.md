# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup and documentation
  - Design document with architecture and implementation plans
  - Project structure and guidelines
  - Comprehensive test suite with 52 tests
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
  - Rich-based battle view
  - Input handling and validation
  - Game phase transitions
- Initial game content
  - Classic starter Pokemon (Bulbasaur, Charmander, Squirtle)
  - Basic moves (Tackle, Scratch, elemental moves, etc.)
  - Status moves and effects
- Testing infrastructure
  - pytest configuration with coverage reporting
  - Core domain tests
  - Service layer integration tests
  - Mock battle scenarios and game progression tests

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
