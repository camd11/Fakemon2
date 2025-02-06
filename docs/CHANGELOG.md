# Changelog

## [Unreleased]

### Added
- Test debugging guide with comprehensive strategies and examples
- Ability system enhancements:
  - Added weather immunity abilities
  - Added weather resistance abilities
  - Added proper interaction with battle mechanics
  - Added comprehensive ability tests
  - Added docs/TEST_DEBUGGING.md with sections on:
    - Managing test output and verbosity
    - Handling randomness in tests
    - Test design principles
    - Common pitfalls and solutions
    - Debugging process guidelines
- Weather system implementation
  - Added Weather enum with CLEAR, RAIN, SUN, SANDSTORM, and HAIL types
  - Implemented weather effects on move damage (1.5x boost/0.5x reduction)
  - Added weather-based damage for Sandstorm and Hail
  - Implemented weather duration system
- Comprehensive weather system tests
  - Added tests for weather effects on moves
  - Added tests for weather damage and immunities
  - Added tests for weather duration
  - Improved test reliability with critical hit handling

### Changed
- Modified battle system to integrate weather effects and abilities
- Improved test reliability and maintainability
  - Enhanced critical hit tests with better probability handling
  - Added proper resource management (PP, HP) in tests
  - Improved test assertions to handle random factors
  - Standardized debug logging format
  - Added optional debug mode to reduce test output
  - Reduced test trials with wider acceptable ranges
- Improved damage calculation to handle weather multipliers
- Enhanced battle message system for weather effects
- Updated critical hit mechanics
  - Changed critical hit multiplier from 1.5x to 2.0x
  - Fixed stat restoration logic for critical hits
  - Reordered damage calculation (weather before critical)

### Fixed
- Fixed accuracy calculation system
  - Properly handle accuracy and evasion stat stages separately
  - Fixed accuracy formula to use correct multipliers (e.g. +1 stage = 4/3)
  - Fixed evasion formula to properly reduce hit chance (e.g. +1 stage = 0.6)
  - Added comprehensive test coverage for all accuracy scenarios
  - Corrected evasion stage multipliers:
    - +1 stage = 0.6 hit chance (harder to hit)
    - -1 stage = 1.67 hit chance (easier to hit)
  - Fixed stat stage calculation to use proper denominators
- Fixed weather duration handling to properly maintain state
- Fixed circular imports between battle and ability systems
- Fixed ability-weather interaction in damage calculations
- Fixed damage calculation order for weather effects
- Improved test reliability for random elements (critical hits)
- Fixed critical hit damage calculation and stat handling
  - Corrected assumption about weather/critical hit interaction
  - Updated test to expect 2x damage regardless of weather
  - Added detailed documentation about damage calculation order
  - Fixed critical hit probability calculation using float division
- Fixed accuracy calculation and stat modifiers
  - Properly convert move accuracy to decimal before applying modifiers
  - Correctly handle accuracy and evasion stat modifiers
  - Fixed accuracy test assertions for proper comparison
- Fixed debug logging conditionals to reduce test output

## [0.1.0] - 2025-02-05

### Added
- Initial battle system implementation
- Basic Pokemon stats and moves
- Type effectiveness system
- Status effects (Sleep, Freeze, Burn, Poison, Paralysis)
- Ability system with status immunities and resistances
