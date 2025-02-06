# Changelog

## [Unreleased]

### Added
- Test debugging guide with comprehensive strategies and examples
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
- Modified battle system to integrate weather effects
- Improved test reliability and maintainability
  - Enhanced critical hit tests with better probability handling
  - Added proper resource management (PP, HP) in tests
  - Improved test assertions to handle random factors
  - Standardized debug logging format
- Improved damage calculation to handle weather multipliers
- Enhanced battle message system for weather effects

### Fixed
- Fixed weather duration handling to properly maintain state
- Fixed damage calculation order for weather effects
- Improved test reliability for random elements (critical hits)

## [0.1.0] - 2025-02-05

### Added
- Initial battle system implementation
- Basic Pokemon stats and moves
- Type effectiveness system
- Status effects (Sleep, Freeze, Burn, Poison, Paralysis)
- Ability system with status immunities and resistances
