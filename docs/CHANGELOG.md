# Changelog

## [2024-02-04] Burn Status Implementation
- Added burn status effect implementation
  - Deals 1/16 max HP damage per turn
  - Halves physical attack power
  - Lasts 5 turns like other status effects
- Added comprehensive tests for burn mechanics
  - Damage calculation
  - Attack reduction
  - Duration handling
  - Status messages

## [2024-02-04] Status Effect Duration Fixes
- Fixed sleep duration to properly last 1-3 turns
- Fixed poison duration to properly last 5 turns
- Fixed status effect duration handling to decrement first, then check if duration <= 0
- Increased freeze thaw chance to 20% per turn
- Added safety limit to prevent infinite loops in tests
- All status effect tests passing with good coverage

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
