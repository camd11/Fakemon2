# Changelog

## [Unreleased]

### Added
- Status effect system with support for Poison, Paralysis, and Sleep
  - Poison deals 1/8 max HP damage per turn
  - Paralysis has 25% chance to skip turn and reduces speed to 1/4
  - Sleep prevents moves completely and lasts 1-3 turns randomly
  - Status duration tracking with automatic clearing
  - Status messages for application, damage, and clearing
  - Prevention of multiple status effects
  - Comprehensive test coverage in test_battle_status.py

### Changed
- Enhanced Pokemon class with status effect handling
- Updated Battle class to process status effects at end of turn
- Improved battle message system to include status effect notifications

### Fixed
- Status effect duration now properly decreases and clears
- Status messages now show in correct order during battle

## [Previous versions would go here]
