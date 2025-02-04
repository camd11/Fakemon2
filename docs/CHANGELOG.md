# Changelog

## [2024-02-04] Mold Breaker Abilities
- Added mold breaker system:
  - Mold Breaker: Ignores other Pokemon's abilities
  - Teravolt: Ignores other Pokemon's abilities
  - Turboblaze: Ignores other Pokemon's abilities
- Enhanced Pokemon class to handle ability ignoring
- Added comprehensive tests for mold breaker functionality

## [2024-02-04] Trace Abilities
- Added trace system:
  - Trace: Copies opponent's ability when entering battle
- Enhanced Pokemon class to handle ability copying and restoration
- Enhanced Battle class to handle trace triggers
- Added comprehensive tests for trace functionality

## [2024-02-04] Color Change Abilities
- Added color change system:
  - Color Change: Changes type to match damaging move
  - Forecast: Changes type based on weather
- Enhanced Pokemon class to handle type changes
- Enhanced Battle class to handle weather type changes
- Added comprehensive tests for color change functionality

## [2024-02-04] Protean Abilities
- Added protean system:
  - Protean: Changes type to match move being used
  - Libero: Changes type to match move being used
  - Adaptability: Powers up STAB moves (2.0x instead of 1.5x)
- Enhanced Pokemon class to handle type changes
- Enhanced Battle class to handle protean triggers
- Added comprehensive tests for protean functionality

## [2024-02-04] Disguise Abilities
- Added disguise system:
  - Disguise: Takes no damage from first hit
  - Ice Face: Takes no damage from first physical hit
  - Wonder Guard: Only takes super effective damage
- Enhanced Pokemon class to handle disguise protection
- Enhanced Battle class to handle disguise triggers
- Added comprehensive tests for disguise functionality

## [2024-02-04] Illusion Abilities
- Added illusion system:
  - Illusion: Makes Pokemon appear as another Pokemon
  - Imposter: Transforms into opponent's Pokemon
  - Mimicry: Changes type based on terrain
- Enhanced Pokemon class to handle illusions
- Enhanced Battle class to handle illusion triggers
- Added comprehensive tests for illusion functionality

## [2024-02-04] Form Change Abilities
- Added form change system:
  - Stance Change: Changes form based on move used
  - Battle Bond: Changes form after defeating Pokemon
  - Power Construct: Changes form at low HP
- Enhanced Pokemon class to handle form changes
- Enhanced Battle class to handle form change triggers
- Added comprehensive tests for form change functionality

## [2024-02-04] Aura Abilities
- Added aura system:
  - Fairy Aura: Powers up Fairy moves by 33%
  - Dark Aura: Powers up Dark moves by 33%
  - Aura Break: Reverses aura effects to -25%
- Enhanced Battle class to handle aura effects
- Added comprehensive tests for aura functionality

## [2024-02-04] Terrain Abilities
- Added terrain system:
  - Grassy Terrain: Heals grounded Pokemon, boosts Grass moves
  - Misty Terrain: Prevents status conditions, weakens Dragon moves
  - Electric Terrain: Prevents sleep, boosts Electric moves
  - Psychic Terrain: Boosts Psychic moves, prevents priority moves
- Added terrain-setting abilities:
  - Grassy Surge: Sets Grassy Terrain
  - Misty Surge: Sets Misty Terrain
  - Electric Surge: Sets Electric Terrain
  - Psychic Surge: Sets Psychic Terrain
- Enhanced Battle class to handle terrain effects
- Added comprehensive tests for terrain functionality

## [2024-02-04] Type-Enhancing Items
- Added type-enhancing items:
  - Charcoal: Powers up Fire moves
  - Mystic Water: Powers up Water moves
  - Miracle Seed: Powers up Grass moves
  - And many more for each type
- Enhanced Battle class to handle type boosts
- Added comprehensive tests for type boost functionality

## [2024-02-04] Entry Hazard Abilities
- Added entry hazard system:
  - Spikes: Damages grounded Pokemon (up to 3 layers)
  - Toxic Spikes: Poisons grounded Pokemon (up to 2 layers)
  - Stealth Rock: Damages Pokemon based on type effectiveness
- Enhanced Battle class to handle hazards
- Added comprehensive tests for hazard functionality

## [2024-02-04] Weather-Boosted Moves
- Added weather boost system for moves:
  - Water moves boosted in rain, reduced in sun
  - Fire moves boosted in sun, reduced in rain
- Enhanced Move class with weather multiplier calculation
- Enhanced Battle class to apply weather boosts
- Added comprehensive tests for weather boost functionality

## [2024-02-04] Held Items
- Added held item system:
  - Leftovers: Restores HP each turn
  - Oran Berry: Restores HP at low health
  - Lum Berry: Cures any status condition
  - Focus Sash: Survives a one-hit KO
  - Muscle Band: Boosts physical moves
  - Wise Glasses: Boosts special moves
- Enhanced Pokemon class with held item support
- Enhanced Battle class to handle held item effects
- Added comprehensive tests for held item functionality

## [2024-02-04] Stat-Boosting Abilities
- Added stat-boosting abilities:
  - Guts: Boosts Attack when status-afflicted
  - Swift Swim: Doubles Speed in rain
  - Chlorophyll: Doubles Speed in sun
  - Sand Rush: Doubles Speed in sandstorm
  - Slush Rush: Doubles Speed in hail
- Enhanced Pokemon class to handle ability-based stat boosts
- Added comprehensive tests for stat boost functionality

## [2024-02-04] Weather Abilities
- Added weather-related abilities:
  - Drizzle: Summons rain
  - Drought: Summons sun
  - Sand Stream: Summons sandstorm
  - Snow Warning: Summons hail
- Enhanced Battle class to handle weather abilities
- Added comprehensive tests for weather ability functionality

## [2024-02-04] Status-Curing Items
- Added status-curing items:
  - Full Heal: Cures all status conditions
  - Antidote: Cures poison
  - Burn Heal: Cures burn
  - Paralyze Heal: Cures paralysis
  - Awakening: Cures sleep
  - Ice Heal: Cures freeze
- Enhanced Item class to support specific status curing
- Added comprehensive tests for status item functionality

## [2024-02-04] Status Effect Abilities
- Added ability system with status-related abilities:
  - Immunity: Prevents all status conditions
  - Limber: Prevents paralysis
  - Water Veil: Prevents burns
  - Vital Spirit: Prevents sleep
  - Magma Armor: Prevents freezing
- Added ability support to Pokemon class
- Added comprehensive tests for ability functionality

## [2024-02-04] Status Effect Type Immunities
- Added type-based immunity system for status effects:
  - Fire types immune to burn
  - Steel types immune to poison
  - Electric types immune to paralysis
  - Ice types immune to freeze
- Added comprehensive tests for type immunities

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
