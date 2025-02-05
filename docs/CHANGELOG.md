# Changelog

## [Unreleased]

### Added
- New ability system with support for:
  - Status immunities
  - Status resistances
- Tests for ability system functionality
  - Status immunity tests
  - Multiple status immunities tests
  - Status resistance tests (in progress)

### Changed
- Modified battle system to integrate abilities
- Updated status effect application to consider abilities
- Separated accuracy checks for status moves vs. non-status moves
- Improved status chance calculation with resistance multipliers

### Fixed
- Accuracy checks no longer apply to status moves
- Status immunity properly prevents specific status effects
- Multiple status immunities working correctly

### Known Issues
- Status resistance not reducing status chance correctly
  - Expected ~50% success rate with resistance
  - Currently getting ~0.7% success rate
  - Investigation ongoing

## [Previous Versions]

### [0.1.0] - Initial Release
- Basic battle system
- Pokemon stats and types
- Move system with damage calculation
- Status effects
- Weather effects
- Items and inventory
