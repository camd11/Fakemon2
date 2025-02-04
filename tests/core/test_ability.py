"""Tests for abilities."""

import pytest
from src.core.ability import (
    Ability,
    AbilityType,
    TerrainType,
    AuraType,
    FormChangeType,
    IllusionType,
    IMMUNITY,
    LIMBER,
    WATER_VEIL,
    VITAL_SPIRIT,
    MAGMA_ARMOR,
    DRIZZLE,
    DROUGHT,
    SAND_STREAM,
    SNOW_WARNING,
    GUTS,
    SWIFT_SWIM,
    CHLOROPHYLL,
    SAND_RUSH,
    SLUSH_RUSH,
    GRASSY_SURGE,
    MISTY_SURGE,
    ELECTRIC_SURGE,
    PSYCHIC_SURGE,
    FAIRY_AURA,
    DARK_AURA,
    AURA_BREAK,
    STANCE_CHANGE,
    BATTLE_BOND,
    POWER_CONSTRUCT,
    ILLUSION,
    IMPOSTER,
    MIMICRY
)
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory, StatusEffect
from src.core.battle import Battle, Weather

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon."""
    return Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

def test_status_immunity():
    """Test that status immunity abilities prevent status effects."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=IMMUNITY
    )
    
    # Should not be able to apply any status
    assert not pokemon.set_status(StatusEffect.POISON)
    assert not pokemon.set_status(StatusEffect.BURN)
    assert not pokemon.set_status(StatusEffect.PARALYSIS)
    assert not pokemon.set_status(StatusEffect.SLEEP)
    assert not pokemon.set_status(StatusEffect.FREEZE)
    assert pokemon.status is None

def test_weather_ability():
    """Test that weather abilities set weather conditions."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=DROUGHT
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    assert battle.weather == Weather.SUN
    assert battle.weather_duration is None  # Weather from abilities lasts indefinitely

def test_stat_boost_ability():
    """Test that stat boost abilities modify stats."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=SWIFT_SWIM
    )
    
    # Speed should be doubled in rain
    normal_speed = pokemon.stats.speed
    speed_in_rain = normal_speed * pokemon.get_stat_multiplier("speed", Weather.RAIN)
    assert speed_in_rain == normal_speed * 2.0
    
    # Speed should be normal in other weather
    speed_in_sun = normal_speed * pokemon.get_stat_multiplier("speed", Weather.SUN)
    assert speed_in_sun == normal_speed

def test_terrain_setting():
    """Test that terrain abilities set terrain."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    assert battle.terrain == TerrainType.GRASSY
    assert battle.terrain_duration == 5  # Terrain lasts 5 turns

def test_terrain_move_boost():
    """Test that terrain boosts appropriate moves."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.GRASS,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    grass_move = Move(
        name="Grass Move",
        type_=Type.GRASS,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without terrain
    battle.terrain = None
    attacker.moves = [grass_move]
    result = battle.execute_turn(grass_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Grassy Terrain
    battle.terrain = TerrainType.GRASSY
    result = battle.execute_turn(grass_move, defender)
    
    # Should deal 30% more damage
    assert result.damage_dealt == int(base_damage * 1.3)

def test_terrain_healing():
    """Test that Grassy Terrain heals grounded Pokemon."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    
    # Damage Pokemon
    pokemon.take_damage(50)  # Half HP
    initial_hp = pokemon.current_hp
    
    # End turn should trigger healing
    result = battle.end_turn()
    
    # Should heal 1/16 max HP
    assert pokemon.current_hp == initial_hp + (pokemon.stats.hp // 16)
    assert any("healed by the grassy terrain" in msg for msg in result.messages)

def test_terrain_status_prevention():
    """Test that Misty Terrain prevents status conditions."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=MISTY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    
    # Should not be able to apply status to grounded Pokemon
    assert not pokemon.set_status(StatusEffect.POISON)
    assert not pokemon.set_status(StatusEffect.BURN)
    assert not pokemon.set_status(StatusEffect.PARALYSIS)
    assert not pokemon.set_status(StatusEffect.SLEEP)
    assert not pokemon.set_status(StatusEffect.FREEZE)
    assert pokemon.status is None

def test_terrain_dragon_reduction():
    """Test that Misty Terrain reduces Dragon move power."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.DRAGON,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=MISTY_SURGE
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    dragon_move = Move(
        name="Dragon Move",
        type_=Type.DRAGON,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without terrain
    battle.terrain = None
    attacker.moves = [dragon_move]
    result = battle.execute_turn(dragon_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Misty Terrain
    battle.terrain = TerrainType.MISTY
    result = battle.execute_turn(dragon_move, defender)
    
    # Should deal 50% less damage
    assert result.damage_dealt == int(base_damage * 0.5)

def test_terrain_duration():
    """Test that terrain fades after 5 turns."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GRASSY_SURGE
    )
    
    battle = Battle(pokemon, pokemon, TypeEffectiveness())
    
    # Terrain should last 5 turns
    for i in range(4):
        result = battle.end_turn()
        assert battle.terrain == TerrainType.GRASSY
        assert battle.terrain_duration == 4 - i
        
    # On 5th turn, terrain should fade
    result = battle.end_turn()
    assert battle.terrain is None
    assert any("terrain faded" in msg for msg in result.messages)

def test_aura_boost():
    """Test that aura abilities boost appropriate moves."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.FAIRY,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=FAIRY_AURA
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    
    # Create test move
    fairy_move = Move(
        name="Fairy Move",
        type_=Type.FAIRY,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without aura
    battle.active_auras.clear()
    attacker.moves = [fairy_move]
    result = battle.execute_turn(fairy_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Fairy Aura
    battle.active_auras.add(AuraType.FAIRY)
    result = battle.execute_turn(fairy_move, defender)
    
    # Should deal 33% more damage
    assert result.damage_dealt == int(base_damage * 1.33)

def test_aura_break():
    """Test that Aura Break reverses aura effects."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.FAIRY,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=FAIRY_AURA
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=AURA_BREAK
    )
    
    # Create test move
    fairy_move = Move(
        name="Fairy Move",
        type_=Type.FAIRY,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Test without aura break
    battle.aura_break_active = False
    attacker.moves = [fairy_move]
    result = battle.execute_turn(fairy_move, defender)
    base_damage = result.damage_dealt
    
    # Test with Aura Break
    battle.aura_break_active = True
    result = battle.execute_turn(fairy_move, defender)
    
    # Should deal 25% less damage instead of 33% more
    assert result.damage_dealt == int(base_damage * 0.75)

def test_multiple_auras():
    """Test that multiple auras work independently."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.FAIRY, Type.DARK),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=FAIRY_AURA
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=DARK_AURA
    )
    
    battle = Battle(attacker, defender, TypeEffectiveness())
    
    # Create test moves
    fairy_move = Move(
        name="Fairy Move",
        type_=Type.FAIRY,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    dark_move = Move(
        name="Dark Move",
        type_=Type.DARK,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    # Test Fairy move
    attacker.moves = [fairy_move]
    result = battle.execute_turn(fairy_move, defender)
    fairy_damage = result.damage_dealt
    
    # Test Dark move
    attacker.moves = [dark_move]
    result = battle.execute_turn(dark_move, defender)
    dark_damage = result.damage_dealt
    
    # Both moves should be boosted by 33%
    assert fairy_damage == int(fairy_damage * 1.33)
    assert dark_damage == int(dark_damage * 1.33)

def test_stance_change():
    """Test that Stance Change works correctly."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.STEEL, Type.GHOST),
        base_stats=Stats(60, 50, 150, 50, 150, 60),  # Shield form stats
        level=50,
        ability=STANCE_CHANGE,
        current_form="shield"
    )
    
    # Create test moves
    attack_move = Move(
        name="Attack Move",
        type_=Type.STEEL,
        category=MoveCategory.PHYSICAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    shield_move = Move(
        name="King's Shield",
        type_=Type.GHOST,
        category=MoveCategory.PHYSICAL,
        power=0,
        accuracy=100,
        pp=10
    )
    
    # Test form change to blade form
    msg = pokemon.check_form_change("move_used", move_type=Type.STEEL)
    assert msg == "Test Pokemon transformed into its blade form!"
    assert pokemon.current_form == "blade"
    assert pokemon.stats.attack == 150  # Blade form has higher attack
    
    # Test form change back to shield form
    msg = pokemon.check_form_change("move_used", move_type=Type.GHOST)
    assert msg == "Test Pokemon transformed into its shield form!"
    assert pokemon.current_form == "shield"
    assert pokemon.stats.defense == 150  # Shield form has higher defense

def test_battle_bond():
    """Test that Battle Bond works correctly."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.WATER, Type.DARK),
        base_stats=Stats(72, 95, 67, 103, 71, 122),  # Normal form stats
        level=50,
        ability=BATTLE_BOND,
        current_form="normal"
    )
    
    # Test form change after defeating Pokemon
    msg = pokemon.check_form_change("pokemon_defeated")
    assert msg == "Test Pokemon transformed into its bond form!"
    assert pokemon.current_form == "bond"
    assert pokemon.stats.special_attack == 145  # Bond form has higher special attack

def test_power_construct():
    """Test that Power Construct works correctly."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.DRAGON, Type.GROUND),
        base_stats=Stats(54, 100, 71, 61, 85, 109),  # Cell form stats
        level=50,
        ability=POWER_CONSTRUCT,
        current_form="cell"
    )
    
    # Damage Pokemon to 50% HP
    pokemon.take_damage(pokemon.stats.hp // 2)
    
    # Test form change at low HP
    assert pokemon.current_form == "complete"  # Should have changed automatically
    assert pokemon.stats.hp == 216  # Complete form has higher HP
    
    # HP percentage should be preserved
    assert pokemon.current_hp == pokemon.stats.hp // 2

def test_disguise_all():
    """Test that Disguise protects from all damage once."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.GHOST,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=DISGUISE
    )
    
    # First hit should be nullified
    initial_hp = pokemon.current_hp
    damage_dealt = pokemon.take_damage(50)
    assert damage_dealt == 0  # No damage dealt
    assert pokemon.current_hp == initial_hp  # HP unchanged
    assert pokemon.disguise_hp is None  # Disguise broken
    
    # Second hit should deal damage normally
    damage_dealt = pokemon.take_damage(50)
    assert damage_dealt == 50  # Full damage dealt
    assert pokemon.current_hp == initial_hp - 50  # HP reduced

def test_ice_face():
    """Test that Ice Face protects from physical damage once."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.ICE,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=ICE_FACE
    )
    
    # Physical hit should be nullified
    initial_hp = pokemon.current_hp
    damage_dealt = pokemon.take_damage(50, move_category=MoveCategory.PHYSICAL)
    assert damage_dealt == 0  # No damage dealt
    assert pokemon.current_hp == initial_hp  # HP unchanged
    assert pokemon.disguise_hp is None  # Disguise broken
    
    # Special hit should deal damage normally
    damage_dealt = pokemon.take_damage(50, move_category=MoveCategory.SPECIAL)
    assert damage_dealt == 50  # Full damage dealt
    assert pokemon.current_hp == initial_hp - 50  # HP reduced
    
    # Second physical hit should deal damage normally
    damage_dealt = pokemon.take_damage(50, move_category=MoveCategory.PHYSICAL)
    assert damage_dealt == 50  # Full damage dealt
    assert pokemon.current_hp == initial_hp - 100  # HP reduced

def test_wonder_guard():
    """Test that Wonder Guard only takes super effective damage."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.BUG,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=WONDER_GUARD
    )
    
    # Normal effectiveness should be nullified
    initial_hp = pokemon.current_hp
    damage_dealt = pokemon.take_damage(50, effectiveness=1.0)
    assert damage_dealt == 0  # No damage dealt
    assert pokemon.current_hp == initial_hp  # HP unchanged
    
    # Not very effective should be nullified
    damage_dealt = pokemon.take_damage(50, effectiveness=0.5)
    assert damage_dealt == 0  # No damage dealt
    assert pokemon.current_hp == initial_hp  # HP unchanged
    
    # Super effective should deal damage normally
    damage_dealt = pokemon.take_damage(50, effectiveness=2.0)
    assert damage_dealt == 50  # Full damage dealt
    assert pokemon.current_hp == initial_hp - 50  # HP reduced

def test_protean():
    """Test that Protean changes type to match move used."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=PROTEAN
    )
    
    # Create test move
    fire_move = Move(
        name="Fire Move",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    # Check type change
    msg = pokemon.check_protean(fire_move)
    assert msg == "Test Pokemon became FIRE-type!"
    assert pokemon.types == (Type.FIRE,)
    
    # Check STAB multiplier
    assert pokemon.get_stab_multiplier(fire_move) == 1.5

def test_adaptability():
    """Test that Adaptability boosts STAB moves."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.FIRE,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=ADAPTABILITY
    )
    
    # Create test moves
    fire_move = Move(
        name="Fire Move",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    water_move = Move(
        name="Water Move",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )
    
    # Check STAB multipliers
    assert pokemon.get_stab_multiplier(fire_move) == 2.0  # Boosted STAB
    assert pokemon.get_stab_multiplier(water_move) == 1.0  # No STAB

def test_transform():
    """Test that transform copies target's stats and moves."""
    target = Pokemon(
        name="Target",
        types=(Type.DRAGON,),
        base_stats=Stats(150, 150, 150, 150, 150, 150),
        level=50,
        moves=[
            Move(
                name="Dragon Move",
                type_=Type.DRAGON,
                category=MoveCategory.SPECIAL,
                power=100,
                accuracy=100,
                pp=10
            )
        ]
    )
    
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=IMPOSTER
    )
    
    # Transform into target
    msg = pokemon.transform(target)
    assert msg == "Test Pokemon transformed into Target!"
    
    # Stats should match target's
    assert pokemon.stats.attack == target.stats.attack
    assert pokemon.stats.defense == target.stats.defense
    assert pokemon.stats.special_attack == target.stats.special_attack
    assert pokemon.stats.special_defense == target.stats.special_defense
    assert pokemon.stats.speed == target.stats.speed
    
    # Types should match target's
    assert pokemon.transformed_types == target.types
    
    # Moves should match target's
    assert len(pokemon.transformed_moves) == len(target.moves)
    assert pokemon.transformed_moves[0].name == target.moves[0].name

def test_type_mimicry():
    """Test that type mimicry changes type based on terrain."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=MIMICRY
    )
    
    # Test each terrain type
    terrains = {
        TerrainType.GRASSY: Type.GRASS,
        TerrainType.MISTY: Type.FAIRY,
        TerrainType.ELECTRIC: Type.ELECTRIC,
        TerrainType.PSYCHIC: Type.PSYCHIC
    }
    
    for terrain, expected_type in terrains.items():
        msg = pokemon.check_type_mimicry(terrain)
        assert msg == f"Test Pokemon became {expected_type.name}-type!"
        assert pokemon.transformed_types == (expected_type,)
        
    # Test clearing terrain
    msg = pokemon.check_type_mimicry(None)
    assert msg == "Test Pokemon returned to its original type!"
    assert pokemon.transformed_types is None

def test_color_change():
    """Test that Color Change changes type to match damaging move."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=COLOR_CHANGE
    )
    
    # Take damage from different move types
    msg = pokemon.take_damage(50, move_type=Type.FIRE)
    assert msg == "Test Pokemon became FIRE-type!"
    assert pokemon.types == (Type.FIRE,)
    
    msg = pokemon.take_damage(50, move_type=Type.WATER)
    assert msg == "Test Pokemon became WATER-type!"
    assert pokemon.types == (Type.WATER,)

def test_forecast():
    """Test that Forecast changes type based on weather."""
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=FORECAST
    )
    
    # Test each weather type
    weather_types = {
        Weather.CLEAR: Type.NORMAL,
        Weather.SUN: Type.FIRE,
        Weather.RAIN: Type.WATER,
        Weather.SANDSTORM: Type.ROCK,
        Weather.HAIL: Type.ICE
    }
    
    for weather, expected_type in weather_types.items():
        msg = pokemon.check_weather_type(weather)
        assert msg == f"Test Pokemon became {expected_type.name}-type!"
        assert pokemon.types == (expected_type,)

def test_trace():
    """Test that Trace copies opponent's ability."""
    # Create Pokemon with Trace
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=TRACE
    )
    
    # Create opponent with Guts
    opponent = Pokemon(
        name="Opponent",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GUTS
    )
    
    # Test ability copying
    msg = pokemon.copy_ability(opponent)
    assert msg == "Test Pokemon traced Opponent's Guts!"
    assert pokemon.ability == GUTS
    
    # Test ability restoration
    msg = pokemon.restore_ability()
    assert msg == "Test Pokemon's Trace was restored!"
    assert pokemon.ability == TRACE
    
def test_trace_faint():
    """Test that traced ability is restored when Pokemon faints."""
    # Create Pokemon with Trace
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=TRACE
    )
    
    # Create opponent with Guts
    opponent = Pokemon(
        name="Opponent",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50,
        ability=GUTS
    )
    
    # Copy ability
    pokemon.copy_ability(opponent)
    assert pokemon.ability == GUTS
    
    # Create battle
    battle = Battle(pokemon, opponent, TypeEffectiveness())
    
    # Faint Pokemon
    pokemon.take_damage(pokemon.stats.hp)
    messages = battle.handle_faint(pokemon)
    
    # Check ability restoration
    assert any("Trace was restored" in msg for msg in messages)
    assert pokemon.ability == TRACE
