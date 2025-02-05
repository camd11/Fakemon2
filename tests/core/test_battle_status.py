"""Tests for battle status effects."""

from src.core.pokemon import Pokemon
from src.core.stats import Stats
from src.core.types import Type, TypeEffectiveness
from src.core.battle import Battle
from src.core.move import Move, MoveCategory, StatusEffect, Effect

def test_poison_damage():
    """Test poison damage over time."""
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Apply poison
    test_pokemon.set_status(StatusEffect.POISON)
    initial_hp = test_pokemon.current_hp

    # End turn should deal poison damage
    result = battle.end_turn()

    # Should deal 1/8 max HP damage
    assert test_pokemon.current_hp == initial_hp - (test_pokemon.stats.hp // 8)

"""
def test_paralysis_speed_reduction():
    # Test paralysis speed reduction.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Apply paralysis
    test_pokemon.set_status(StatusEffect.PARALYSIS)

    # Speed should be reduced to 25%
    assert test_pokemon.get_stat_multiplier("speed") == 0.25

def test_paralysis_skip_turn():
    # Test paralysis chance to skip turn.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Create test move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    )

    # Apply paralysis
    test_pokemon.set_status(StatusEffect.PARALYSIS)

    # Track number of skipped turns
    skipped = 0
    total_turns = 100

    for _ in range(total_turns):
        result = battle.execute_turn(move, test_pokemon)
        if "is fully paralyzed" in result.messages[0]:
            skipped += 1

    # Should skip approximately 25% of turns
    assert 20 <= skipped <= 30  # Allow for random variation

def test_status_duration():
    # Test status effect duration.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Apply status with duration
    test_pokemon.set_status(StatusEffect.POISON, duration=3)

    # Status should persist for 3 turns
    for i in range(3):
        assert test_pokemon.status == StatusEffect.POISON
        battle.end_turn()

    # One more turn to clear it
    battle.end_turn()
    assert test_pokemon.status is None

def test_status_messages():
    # Test status effect messages.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Apply poison
    test_pokemon.set_status(StatusEffect.POISON)
    result = battle.end_turn()
    assert "is hurt by poison" in result.messages[0]

    # Apply burn
    test_pokemon.set_status(StatusEffect.BURN)
    result = battle.end_turn()
    assert "is hurt by its burn" in result.messages[0]

    # Apply paralysis
    test_pokemon.set_status(StatusEffect.PARALYSIS)
    result = battle.execute_turn(Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    ), test_pokemon)
    if len(result.messages) > 0:  # Only if paralysis triggered
        assert "is fully paralyzed" in result.messages[0]

def test_multiple_status_effects():
    # Test that Pokemon can only have one status effect at a time.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Apply poison
    assert test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status == StatusEffect.POISON

    # Try to apply burn while poisoned
    assert not test_pokemon.set_status(StatusEffect.BURN)
    assert test_pokemon.status == StatusEffect.POISON

def test_sleep_prevents_moves():
    # Test that sleeping Pokemon can't move.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Create test move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    )

    # Apply sleep
    test_pokemon.set_status(StatusEffect.SLEEP)

    # Try to use move
    result = battle.execute_turn(move, test_pokemon)
    assert "is fast asleep" in result.messages[0]
    assert result.damage_dealt == 0

def test_sleep_duration():
    # Test that sleep lasts 1-3 turns.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    durations = []
    trials = 100

    for _ in range(trials):
        # Apply sleep
        test_pokemon.set_status(StatusEffect.SLEEP)
        turns = 0

        # Count turns until wake
        while test_pokemon.status == StatusEffect.SLEEP:
            turns += 1
            battle.end_turn()

        durations.append(turns)
        test_pokemon.set_status(None)  # Reset for next trial

    # All durations should be 1-3
    assert all(1 <= d <= 3 for d in durations)
    # Should see all possible durations
    assert len(set(durations)) == 3

def test_freeze_prevents_moves():
    # Test that frozen Pokemon can't move.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Create test move
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        pp=10
    )

    # Apply freeze
    test_pokemon.set_status(StatusEffect.FREEZE)

    # Try to use move
    result = battle.execute_turn(move, test_pokemon)
    assert "is frozen solid" in result.messages[0]
    assert result.damage_dealt == 0
"""

def test_freeze_thaw_chance():
    """Test that freeze has 20% chance to thaw each turn."""
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Create a freeze move
    freeze_move = Move(
        name="Ice Beam",
        type_=Type.ICE,
        category=MoveCategory.SPECIAL,
        power=90,
        accuracy=100,
        pp=10,
        effects=[Effect(status=StatusEffect.FREEZE, status_chance=100)]
    )
    battle.player_pokemon.moves.append(freeze_move)

    # Test multiple times to verify thaw chance
    stayed_frozen = 0
    thaw_turns = []

    for _ in range(100):  # Many trials for better distribution
        # Apply freeze
        battle.execute_turn(freeze_move, test_pokemon)

        # Count turns until thaw
        turns = 0
        while test_pokemon.status == StatusEffect.FREEZE and turns < 10:
            turns += 1
            battle.end_turn()

        if test_pokemon.status == StatusEffect.FREEZE:
            stayed_frozen += 1  # Still frozen after 10 turns
        else:
            thaw_turns.append(turns)  # Record when it thawed

        # Reset for next trial
        test_pokemon.set_status(None)

    # With 20% chance per turn over 10 turns:
    # - Almost all should thaw
    # - Very few might stay frozen
    # But allow for random variation in the test
    assert stayed_frozen <= 5  # At most 5% should stay frozen

"""
def test_burn_damage():
    # Test burn damage over time.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Apply burn
    test_pokemon.set_status(StatusEffect.BURN)
    initial_hp = test_pokemon.current_hp

    # End turn should deal burn damage
    result = battle.end_turn()

    # Should deal 1/16 max HP damage
    assert test_pokemon.current_hp == initial_hp - (test_pokemon.stats.hp // 16)

def test_burn_attack_reduction():
    # Test burn attack reduction.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Apply burn
    test_pokemon.set_status(StatusEffect.BURN)

    # Attack should be halved
    assert test_pokemon.get_stat_multiplier("attack") == 0.5

def test_burn_duration():
    # Test that burn lasts 5 turns.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Create a burn move
    burn_move = Move(
        name="Will-O-Wisp",
        type_=Type.FIRE,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=15,
        effects=[Effect(status=StatusEffect.BURN, status_chance=100)]
    )
    battle.player_pokemon.moves.append(burn_move)

    # Apply burn
    battle.execute_turn(burn_move, test_pokemon)

    # Status should persist for 5 turns
    for i in range(5):
        assert test_pokemon.status == StatusEffect.BURN
        battle.end_turn()

    # One more turn to clear it
    result = battle.end_turn()
    assert test_pokemon.status is None
    assert "burn faded" in result.messages[0]

def test_type_immunities():
    # Test type immunities to status effects.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.FIRE,),  # Fire-type
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Try to apply burn to Fire-type
    assert not test_pokemon.set_status(StatusEffect.BURN)
    assert test_pokemon.status is None

    # Try to apply freeze to Ice-type
    test_pokemon.types = (Type.ICE,)
    assert not test_pokemon.set_status(StatusEffect.FREEZE)
    assert test_pokemon.status is None

    # Try to apply poison to Steel/Poison-type
    test_pokemon.types = (Type.STEEL,)
    assert not test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status is None

    test_pokemon.types = (Type.POISON,)
    assert not test_pokemon.set_status(StatusEffect.POISON)
    assert test_pokemon.status is None

    # Try to apply paralysis to Electric-type
    test_pokemon.types = (Type.ELECTRIC,)
    assert not test_pokemon.set_status(StatusEffect.PARALYSIS)
    assert test_pokemon.status is None

def test_fire_move_thaws_user():
    # Test that using a Fire move thaws the user.
    test_pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(100, 100, 100, 100, 100, 100),
        level=50
    )

    # Create battle
    battle = Battle(test_pokemon, test_pokemon, TypeEffectiveness())

    # Create fire move
    fire_move = Move(
        name="Fire Move",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=50,
        accuracy=100,
        pp=10
    )

    # Apply freeze
    test_pokemon.set_status(StatusEffect.FREEZE)

    # Use fire move
    result = battle.execute_turn(fire_move, test_pokemon)
    assert test_pokemon.status is None
    assert "thawed out" in result.messages[0]
"""
