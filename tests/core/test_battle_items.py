"""Tests for battle item effects."""

import json
from src.core.pokemon import Pokemon
from src.core.stats import Stats
from src.core.types import Type, TypeEffectiveness
from src.core.battle import Battle
from src.core.move import Move, MoveCategory, StatusEffect
from src.core.weather import Weather
from src.core.item import (
    CHARCOAL, MYSTIC_WATER, MIRACLE_SEED, MAGNET, NEVER_MELT_ICE,
    BLACK_BELT, POISON_BARB, SOFT_SAND, SHARP_BEAK, TWISTED_SPOON,
    SILVER_POWDER, HARD_STONE, SPELL_TAG, DRAGON_FANG, METAL_COAT,
    SILK_SCARF, FOCUS_SASH, LEFTOVERS, ORAN_BERRY, LUM_BERRY,
    MUSCLE_BAND, WISE_GLASSES, FULL_HEAL, ANTIDOTE, BURN_HEAL,
    PARALYZE_HEAL, AWAKENING, ICE_HEAL
)

def load_type_effectiveness():
    """Load type effectiveness data from JSON."""
    with open('src/data/types.json') as f:
        type_data = json.load(f)
    type_chart = TypeEffectiveness()
    type_chart.load_from_json(type_data)
    return type_chart

def test_type_boost_damage():
    """Test that type-enhancing items boost move damage."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.FIRE,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
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

    battle = Battle(attacker, defender, load_type_effectiveness())

    # Test without item
    attacker.moves = [fire_move]
    result = battle.execute_turn(fire_move, defender)
    base_damage = result.damage_dealt

    # Test with Charcoal
    attacker.equip_item(CHARCOAL)
    result = battle.execute_turn(fire_move, defender)
    boosted_damage = result.damage_dealt

    # Should deal 20% more damage
    assert boosted_damage == int(base_damage * 1.2)

def test_type_boost_wrong_type():
    """Test that type-enhancing items don't boost wrong type moves."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.WATER,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create test move
    water_move = Move(
        name="Water Move",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )

    battle = Battle(attacker, defender, load_type_effectiveness())

    # Test without item
    attacker.moves = [water_move]
    result = battle.execute_turn(water_move, defender)
    base_damage = result.damage_dealt

    # Test with wrong type item (Charcoal)
    attacker.equip_item(CHARCOAL)
    result = battle.execute_turn(water_move, defender)

    # Damage should be unchanged
    assert result.damage_dealt == base_damage

def test_type_boost_stacks():
    """Test that type boost stacks with other multipliers."""
    # First test with a non-STAB move to get true base damage
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),  # Normal type won't get STAB with water move
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    defender = Pokemon(
        name="Defender",
        types=(Type.FIRE,),  # Weak to water
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create test move
    water_move = Move(
        name="Water Move",
        type_=Type.WATER,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )

    battle = Battle(attacker, defender, load_type_effectiveness())

    # Get base damage (includes super effective)
    attacker.moves = [water_move]
    result = battle.execute_turn(water_move, defender)
    base_damage = result.damage_dealt
    assert result.effectiveness == 2.0  # Verify water is super effective vs fire

    # Test with STAB
    attacker = Pokemon(
        name="Attacker",
        types=(Type.WATER,),  # Now will get STAB
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )
    battle = Battle(attacker, defender, load_type_effectiveness())
    result = battle.execute_turn(water_move, defender)
    stab_damage = result.damage_dealt
    assert stab_damage == int(base_damage * 1.5)  # Just STAB multiplier since base includes super effective

    # Test with rain
    battle = Battle(attacker, defender, load_type_effectiveness())
    battle.weather = Weather.RAIN
    result = battle.execute_turn(water_move, defender)
    rain_damage = result.damage_dealt
    assert rain_damage == int(base_damage * 1.5 * 1.5)  # STAB and Rain

    # Test with item
    battle = Battle(attacker, defender, load_type_effectiveness())
    attacker.equip_item(MYSTIC_WATER)
    result = battle.execute_turn(water_move, defender)
    item_damage = result.damage_dealt
    assert item_damage == int(base_damage * 1.5 * 1.2)  # STAB and Item

    # Test with all multipliers
    battle = Battle(attacker, defender, load_type_effectiveness())
    attacker.equip_item(MYSTIC_WATER)
    battle.weather = Weather.RAIN
    result = battle.execute_turn(water_move, defender)
    final_damage = result.damage_dealt

    # Each multiplier should stack multiplicatively
    expected_multiplier = 1.5 * 1.5 * 1.2  # STAB * Rain * Item (base already includes super effective)
    assert final_damage == int(base_damage * expected_multiplier)

def test_all_type_items():
    """Test that all type-enhancing items work correctly."""
    type_items = [
        (CHARCOAL, Type.FIRE),
        (MYSTIC_WATER, Type.WATER),
        (MIRACLE_SEED, Type.GRASS),
        (MAGNET, Type.ELECTRIC),
        (NEVER_MELT_ICE, Type.ICE),
        (BLACK_BELT, Type.FIGHTING),
        (POISON_BARB, Type.POISON),
        (SOFT_SAND, Type.GROUND),
        (SHARP_BEAK, Type.FLYING),
        (TWISTED_SPOON, Type.PSYCHIC),
        (SILVER_POWDER, Type.BUG),
        (HARD_STONE, Type.ROCK),
        (SPELL_TAG, Type.GHOST),
        (DRAGON_FANG, Type.DRAGON),
        (METAL_COAT, Type.STEEL),
        (SILK_SCARF, Type.NORMAL)
    ]

    for item, move_type in type_items:
        attacker = Pokemon(
            name="Attacker",
            types=(Type.NORMAL,),  # Use normal type to avoid STAB
            base_stats=Stats(100, 100, 100, 100, 100, 100),
            level=50
        )

        defender = Pokemon(
            name="Defender",
            types=(Type.NORMAL,),
            base_stats=Stats(100, 100, 100, 100, 100, 100),
            level=50
        )

        # Create test move
        test_move = Move(
            name=f"{move_type.name} Move",
            type_=move_type,
            category=MoveCategory.SPECIAL,
            power=100,
            accuracy=100,
            pp=10
        )

        battle = Battle(attacker, defender, load_type_effectiveness())

        # Test without item
        attacker.moves = [test_move]
        result = battle.execute_turn(test_move, defender)
        base_damage = result.damage_dealt

        # Test with type item
        attacker.equip_item(item)
        result = battle.execute_turn(test_move, defender)

        # Should deal 20% more damage
        assert result.damage_dealt == int(base_damage * 1.2)

def test_focus_sash_survival():
    """Test Focus Sash preventing KO."""
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    test_pokemon.equip_item(FOCUS_SASH)

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, load_type_effectiveness())

    # Create powerful move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=999,
        accuracy=100,
        pp=10
    )

    # Execute turn with lethal damage
    result = battle.execute_turn(move, test_pokemon)

    # Should survive with 1 HP
    assert test_pokemon.current_hp == 1

def test_held_item_single_use():
    """Test that single-use items can only be used once."""
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    test_pokemon.equip_item(FOCUS_SASH)

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, load_type_effectiveness())

    # Create powerful move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=999,
        accuracy=100,
        pp=10
    )

    # First hit should trigger Focus Sash
    result = battle.execute_turn(move, test_pokemon)
    assert test_pokemon.current_hp == 1

    # Second hit should KO
    result = battle.execute_turn(move, test_pokemon)
    assert test_pokemon.current_hp == 0

def test_leftovers_healing():
    """Test Leftovers healing at end of turn."""
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Damage Pokemon first
    test_pokemon.current_hp = 50  # Set to exactly half HP

    test_pokemon.equip_item(LEFTOVERS)

    # Create a dummy Pokemon for the other side
    dummy_pokemon = Pokemon(
        name="Dummy",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle with different Pokemon
    battle = Battle(test_pokemon, dummy_pokemon, load_type_effectiveness())

    # End turn should trigger Leftovers
    result = battle.end_turn()
    print("Leftovers messages:", result.messages)  # Debug print
    print("Final HP:", test_pokemon.current_hp)  # Debug print

    # Should heal 1/16 max HP
    assert any("restored 6 HP with Leftovers" in msg for msg in result.messages)
    assert test_pokemon.current_hp == 56  # 50 + 6 (1/16 of 100)

def test_oran_berry_healing():
    """Test Oran Berry healing at low HP."""
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Set HP to just above the threshold
    defender.current_hp = 30  # 30% HP
    defender.equip_item(ORAN_BERRY)

    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle with separate attacker and defender
    battle = Battle(attacker, defender, load_type_effectiveness())

    # Create move that will put Pokemon below threshold
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=10,  # Small damage to ensure we don't KO
        accuracy=100,
        pp=10
    )

    # Execute turn to damage defender
    result = battle.execute_turn(move, defender)
    print("Oran Berry messages:", result.messages)  # Debug print
    print("Current HP:", defender.current_hp)  # Debug print
    print("Max HP:", defender.stats.hp)  # Debug print
    print("HP Percent:", defender.current_hp / defender.stats.hp)  # Debug print

    # Should have triggered Oran Berry and healed 10 HP
    assert defender.current_hp > 0
    assert any("restored 10 HP using its Oran Berry" in msg for msg in result.messages)

def test_lum_berry_status():
    """Test Lum Berry curing status conditions."""
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    test_pokemon.equip_item(LUM_BERRY)

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, load_type_effectiveness())

    # Apply status effect
    test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status == StatusEffect.POISON

    # End turn should trigger Lum Berry
    result = battle.end_turn()

    # Status should be cured
    assert test_pokemon.status is None
    assert any("cured its poison using Lum Berry" in msg for msg in result.messages)

def test_muscle_band_boost():
    """Test Muscle Band boosting physical moves."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create physical move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=100,
        accuracy=100,
        pp=10
    )

    battle = Battle(attacker, defender, load_type_effectiveness())

    # Test without item
    attacker.moves = [move]
    result = battle.execute_turn(move, defender)
    base_damage = result.damage_dealt

    # Test with Muscle Band
    attacker.equip_item(MUSCLE_BAND)
    result = battle.execute_turn(move, defender)

    # Should deal 10% more damage
    assert result.damage_dealt == int(base_damage * 1.1)

def test_wise_glasses_boost():
    """Test Wise Glasses boosting special moves."""
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create special move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.SPECIAL,
        power=100,
        accuracy=100,
        pp=10
    )

    battle = Battle(attacker, defender, load_type_effectiveness())

    # Test without item
    attacker.moves = [move]
    result = battle.execute_turn(move, defender)
    base_damage = result.damage_dealt

    # Test with Wise Glasses
    attacker.equip_item(WISE_GLASSES)
    result = battle.execute_turn(move, defender)

    # Should deal 10% more damage
    assert result.damage_dealt == int(base_damage * 1.1)

def test_status_curing_items():
    """Test items that cure status conditions."""
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Test each status-curing item
    status_items = [
        (FULL_HEAL, {StatusEffect.POISON, StatusEffect.BURN, StatusEffect.PARALYSIS, StatusEffect.SLEEP, StatusEffect.FREEZE}),
        (ANTIDOTE, {StatusEffect.POISON}),
        (BURN_HEAL, {StatusEffect.BURN}),
        (PARALYZE_HEAL, {StatusEffect.PARALYSIS}),
        (AWAKENING, {StatusEffect.SLEEP}),
        (ICE_HEAL, {StatusEffect.FREEZE})
    ]

    for item, curable_statuses in status_items:
        for status in StatusEffect:
            # Reset Pokemon
            test_pokemon.status = None
            test_pokemon.held_item = None

            # Apply status
            test_pokemon.set_status(status)
            assert test_pokemon.status == status

            # Use item
            test_pokemon.equip_item(item)
            if status in curable_statuses:
                assert test_pokemon.held_item.use(test_pokemon)
                assert test_pokemon.status is None
            else:
                assert not test_pokemon.held_item.use(test_pokemon)
                assert test_pokemon.status == status
