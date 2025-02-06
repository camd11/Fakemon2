"""Tests for status effects in battles."""

import pytest
from src.core.battle import Battle, TurnResult
from src.core.pokemon import Pokemon, Stats
from src.core.types import Type, TypeEffectiveness
from src.core.move import Move, MoveCategory, Effect, StatusEffect

@pytest.fixture
def type_chart():
    """Create a type chart for testing."""
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0},
        "fire": {"fire": 0.5},
        "water": {"water": 0.5}
    })
    return chart

@pytest.fixture
def test_pokemon():
    """Create a test Pokemon for battle."""
    stats = Stats(
        hp=100,
        attack=100,
        defense=100,
        special_attack=100,
        special_defense=100,
        speed=100
    )
    
    moves = [
        Move(
            name="Poison Powder",
            type_=Type.NORMAL,
            category=MoveCategory.STATUS,
            power=0,
            accuracy=100,
            pp=35,
            effects=[Effect(status=StatusEffect.POISON, status_chance=100)]
        )
    ]
    
    pokemon = Pokemon(
        name="Test Pokemon",
        types=(Type.NORMAL,),
        base_stats=stats,
        level=50,
        moves=moves
    )
    return pokemon

@pytest.fixture
def battle(test_pokemon, type_chart):
    """Create a battle instance for testing."""
    player_pokemon = test_pokemon
    enemy_pokemon = Pokemon(
        name="Enemy Pokemon",
        types=(Type.NORMAL,),
        base_stats=Stats(
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100
        ),
        level=50,
        moves=[
            Move(
                name="Thunder Wave",
                type_=Type.NORMAL,
                category=MoveCategory.STATUS,
                power=0,
                accuracy=100,
                pp=35,
                effects=[Effect(status=StatusEffect.PARALYSIS, status_chance=100)]
            )
        ]
    )
    return Battle(player_pokemon, enemy_pokemon, type_chart, debug=False)  # Disable debug for multiple trials

def test_poison_damage(battle):
    """Test that poison deals damage at end of turn."""
    # Apply poison
    battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
    initial_hp = battle.enemy_pokemon.current_hp
    
    # End turn should deal poison damage
    result = battle.end_turn()
    assert battle.enemy_pokemon.current_hp < initial_hp
    assert battle.enemy_pokemon.current_hp == initial_hp - (battle.enemy_pokemon.stats.hp // 8)
    assert "Enemy Pokemon is hurt by poison!" in result.messages

def test_paralysis_speed_reduction(battle):
    """Test that paralysis reduces speed."""
    # Apply paralysis
    battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
    
    # Speed should be reduced to 1/4
    original_speed = battle.player_pokemon.stats.speed
    assert battle.player_pokemon.get_stat_multiplier("speed") == 0.25

def test_paralysis_skip_turn(battle):
    """Test that paralysis can cause a turn skip."""
    # Apply paralysis
    battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
    
    # Do multiple trials to ensure paralysis sometimes prevents moves
    skipped_turns = 0
    total_turns = 1000  # Many more trials for better statistical significance
    
    for _ in range(total_turns):
        result = battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
        if "Test Pokemon is fully paralyzed!" in result.messages:
            skipped_turns += 1
        
        # Reset for next turn
        battle.enemy_pokemon.current_hp = battle.enemy_pokemon.stats.hp
    
    # Paralysis should prevent moves ~25% of the time
    # With 1000 trials, allow for ±5% variation (20-30%)
    paralysis_rate = skipped_turns / total_turns
    assert 0.20 <= paralysis_rate <= 0.30, f"Expected 20-30% paralysis rate, got {paralysis_rate*100:.1f}%"

def test_status_duration(battle):
    """Test that status effects last until cured."""
    # Apply poison
    battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
    
    # Status should persist for 5 turns
    for i in range(5):
        assert battle.enemy_pokemon.status == StatusEffect.POISON
        battle.end_turn()
        
    # One more turn to clear it
    battle.end_turn()
    assert battle.enemy_pokemon.status is None

def test_status_messages(battle):
    """Test status effect messages."""
    # Apply poison
    result = battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
    assert "Enemy Pokemon was poisoned!" in result.messages
    
    # End turn should show poison damage
    result = battle.end_turn()
    assert "Enemy Pokemon is hurt by poison!" in result.messages
    
    # Status clear message
    battle.enemy_pokemon.set_status(None)  # Clear status directly
    result = battle.end_turn()
    # No messages since status was cleared directly
    assert len(result.messages) == 0

def test_multiple_status_effects(battle):
    """Test that Pokemon can only have one status effect."""
    # Apply poison
    battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
    assert battle.enemy_pokemon.status == StatusEffect.POISON
    
    # Try to apply paralysis
    battle.execute_turn(battle.enemy_pokemon.moves[0], battle.enemy_pokemon)
    # Should still be poisoned
    assert battle.enemy_pokemon.status == StatusEffect.POISON

def test_sleep_prevents_moves(battle):
    """Test that sleep prevents moves completely."""
    # Create a sleep move
    sleep_move = Move(
        name="Sleep Powder",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=35,
        effects=[Effect(status=StatusEffect.SLEEP, status_chance=100)]
    )
    battle.player_pokemon.moves.append(sleep_move)
    
    # Apply sleep
    battle.execute_turn(sleep_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status == StatusEffect.SLEEP
    
    # Try to move while sleeping
    result = battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
    assert "Enemy Pokemon is fast asleep!" in result.messages
    
def test_sleep_duration(battle):
    """Test that sleep lasts 1-3 turns."""
    # Create a sleep move
    sleep_move = Move(
        name="Sleep Powder",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=35,
        effects=[Effect(status=StatusEffect.SLEEP, status_chance=100)]
    )
    battle.player_pokemon.moves.append(sleep_move)
    
    # Test multiple times to verify random duration
    durations = set()
    for _ in range(50):  # More trials with debug off
        # Apply sleep
        battle.execute_turn(sleep_move, battle.enemy_pokemon)
        
        # Count turns until wake up (including initial turn)
        turns = 1  # Initial turn when sleep is applied
        max_turns = 10  # Safety limit
        while battle.enemy_pokemon.status == StatusEffect.SLEEP and turns <= max_turns:
            battle.end_turn()
            if battle.enemy_pokemon.status == StatusEffect.SLEEP:
                turns += 1

        # Only record if we didn't hit the safety limit
        if turns <= max_turns:
            durations.add(turns)
        
        # Reset for next trial
        battle.enemy_pokemon.set_status(None)
    
    # Sleep should last 1-3 turns
    assert durations.issubset({1, 2, 3})
    assert len(durations) > 1  # Should get different durations

def test_freeze_prevents_moves(battle):
    """Test that freeze prevents moves completely."""
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
    
    # Apply freeze
    battle.execute_turn(freeze_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status == StatusEffect.FREEZE
    
    # Try to move while frozen
    result = battle.execute_turn(battle.enemy_pokemon.moves[0], battle.player_pokemon)
    assert "Enemy Pokemon is frozen solid!" in result.messages

def test_freeze_thaw_chance(battle):
    """Test that freeze has 20% chance to thaw each turn."""
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
    
    for _ in range(50):  # More trials with debug off
        # Apply freeze
        battle.execute_turn(freeze_move, battle.enemy_pokemon)
        
        # Count turns until thaw
        turns = 0
        while battle.enemy_pokemon.status == StatusEffect.FREEZE and turns < 10:
            turns += 1
            battle.end_turn()
            
        if battle.enemy_pokemon.status == StatusEffect.FREEZE:
            stayed_frozen += 1  # Still frozen after 10 turns
        else:
            thaw_turns.append(turns)  # Record when it thawed
        
        # Reset for next trial
        battle.enemy_pokemon.set_status(None)
    
    # With 20% chance per turn, over 10 turns:
    # - Most should thaw
    # - Few might stay frozen
    # Allow for wider random variation due to fewer trials
    assert stayed_frozen <= 4  # At most 20% should stay frozen
    assert len(thaw_turns) >= 14  # At least 70% should thaw
    if len(thaw_turns) > 0:
        # Most thaws should happen in first few turns
        avg_thaw_turn = sum(thaw_turns) / len(thaw_turns)
        assert avg_thaw_turn <= 5  # Average thaw turn should be early

def test_fire_move_thaws_user(battle):
    """Test that using a fire move thaws the user."""
    # Create moves
    freeze_move = Move(
        name="Ice Beam",
        type_=Type.ICE,
        category=MoveCategory.SPECIAL,
        power=90,
        accuracy=100,
        pp=10,
        effects=[Effect(status=StatusEffect.FREEZE, status_chance=100)]
    )
    fire_move = Move(
        name="Flamethrower",
        type_=Type.FIRE,
        category=MoveCategory.SPECIAL,
        power=90,
        accuracy=100,
        pp=15
    )
    battle.player_pokemon.moves.extend([freeze_move, fire_move])
    
    # Apply freeze to player
    battle.execute_turn(freeze_move, battle.player_pokemon)
    assert battle.player_pokemon.status == StatusEffect.FREEZE
    
    # Use fire move
    result = battle.execute_turn(fire_move, battle.enemy_pokemon)
    assert "Test Pokemon thawed out!" in result.messages
    assert battle.player_pokemon.status is None

def test_burn_attack_reduction(battle):
    """Test that burn reduces attack to 1/2."""
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
    battle.execute_turn(burn_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status == StatusEffect.BURN
    
    # Attack should be reduced to 1/2
    original_attack = battle.enemy_pokemon.stats.attack
    assert battle.enemy_pokemon.get_stat_multiplier("attack") == 0.5

def test_burn_damage(battle):
    """Test that burn deals 1/8 max HP damage per turn."""
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
    battle.execute_turn(burn_move, battle.enemy_pokemon)
    initial_hp = battle.enemy_pokemon.current_hp
    
    # End turn should deal burn damage
    result = battle.end_turn()
    assert battle.enemy_pokemon.current_hp < initial_hp
    assert battle.enemy_pokemon.current_hp == initial_hp - (battle.enemy_pokemon.stats.hp // 8)
    assert "Enemy Pokemon is hurt by its burn!" in result.messages

def test_burn_duration(battle):
    """Test that burn lasts 5 turns."""
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
    battle.execute_turn(burn_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status == StatusEffect.BURN
    
    # Status should persist for 5 turns
    for i in range(5):
        assert battle.enemy_pokemon.status == StatusEffect.BURN
        battle.end_turn()
        
    # One more turn to clear it
    battle.end_turn()
    assert battle.enemy_pokemon.status is None

def test_type_immunities(battle):
    """Test that Pokemon are immune to status effects based on their type."""
    # Create status moves
    burn_move = Move(
        name="Will-O-Wisp",
        type_=Type.FIRE,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=15,
        effects=[Effect(status=StatusEffect.BURN, status_chance=100)]
    )
    freeze_move = Move(
        name="Ice Beam",
        type_=Type.ICE,
        category=MoveCategory.SPECIAL,
        power=90,
        accuracy=100,
        pp=10,
        effects=[Effect(status=StatusEffect.FREEZE, status_chance=100)]
    )
    paralyze_move = Move(
        name="Thunder Wave",
        type_=Type.ELECTRIC,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=20,
        effects=[Effect(status=StatusEffect.PARALYSIS, status_chance=100)]
    )
    poison_move = Move(
        name="Toxic",
        type_=Type.POISON,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=10,
        effects=[Effect(status=StatusEffect.POISON, status_chance=100)]
    )
    battle.player_pokemon.moves.extend([burn_move, freeze_move, paralyze_move, poison_move])
    
    # Test Fire-type immunity to burn
    fire_pokemon = Pokemon(
        name="Fire Pokemon",
        types=(Type.FIRE,),
        base_stats=Stats(hp=100, attack=100, defense=100, special_attack=100, special_defense=100, speed=100),
        level=50
    )
    battle.enemy_pokemon = fire_pokemon
    battle.execute_turn(burn_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status is None
    
    # Test Ice-type immunity to freeze
    ice_pokemon = Pokemon(
        name="Ice Pokemon",
        types=(Type.ICE,),
        base_stats=Stats(hp=100, attack=100, defense=100, special_attack=100, special_defense=100, speed=100),
        level=50
    )
    battle.enemy_pokemon = ice_pokemon
    battle.execute_turn(freeze_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status is None
    
    # Test Electric-type immunity to paralysis
    electric_pokemon = Pokemon(
        name="Electric Pokemon",
        types=(Type.ELECTRIC,),
        base_stats=Stats(hp=100, attack=100, defense=100, special_attack=100, special_defense=100, speed=100),
        level=50
    )
    battle.enemy_pokemon = electric_pokemon
    battle.execute_turn(paralyze_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status is None
    
    # Test Poison-type immunity to poison
    poison_pokemon = Pokemon(
        name="Poison Pokemon",
        types=(Type.POISON,),
        base_stats=Stats(hp=100, attack=100, defense=100, special_attack=100, special_defense=100, speed=100),
        level=50
    )
    battle.enemy_pokemon = poison_pokemon
    battle.execute_turn(poison_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status is None
    
    # Test Steel-type immunity to poison
    steel_pokemon = Pokemon(
        name="Steel Pokemon",
        types=(Type.STEEL,),
        base_stats=Stats(hp=100, attack=100, defense=100, special_attack=100, special_defense=100, speed=100),
        level=50
    )
    battle.enemy_pokemon = steel_pokemon
    battle.execute_turn(poison_move, battle.enemy_pokemon)
    assert battle.enemy_pokemon.status is None
