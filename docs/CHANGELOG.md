# Changelog

## [Unreleased]

### Added
- New ability system with support for:
  - Status immunities (complete blocking of specific effects)
  - Status resistances (50% chance reduction)
- Comprehensive test suite for abilities:
  - Single status immunity tests
  - Multiple status immunities tests
  - Single status resistance tests
  - Multiple status resistances tests
  - Specific burn immunity tests
  - Specific paralysis resistance tests
- Detailed debugging guidelines in DEVELOPMENT_STATUS.md

### Changed
- Modified battle system to integrate abilities
- Updated status effect application to consider abilities
- Separated accuracy checks for status moves vs. non-status moves
- Improved status chance calculation with resistance multipliers
- Updated DESIGN.md with complete ability system documentation

### Fixed
- Status resistance now correctly applies 50% reduction
- PP management in multi-trial tests
- Status effect cleanup between test trials
- Accuracy checks no longer interfere with status moves
- Status immunity properly prevents specific status effects
- Multiple status immunities working correctly

## [Previous Versions]

### [0.1.0] - Initial Release
- Basic battle system
- Pokemon stats and types
- Move system with damage calculation
- Status effects
- Weather effects
- Items and inventory
