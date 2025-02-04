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
    return Battle(player_pokemon, enemy_pokemon, type_chart)

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
    total_turns = 20
    
    for _ in range(total_turns):
        result = battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
        if "Test Pokemon is fully paralyzed!" in result.messages:
            skipped_turns += 1
        
        # Reset for next turn
        battle.enemy_pokemon.current_hp = battle.enemy_pokemon.stats.hp
    
    # Paralysis should prevent moves ~25% of the time
    assert 0.15 <= skipped_turns / total_turns <= 0.35

def test_status_duration(battle):
    """Test that status effects last until cured."""
    # Apply poison
    battle.execute_turn(battle.player_pokemon.moves[0], battle.enemy_pokemon)
    
    # Status should persist for 5 turns
    for _ in range(5):
        assert battle.enemy_pokemon.status == StatusEffect.POISON
        battle.end_turn()
    
    # Status should be cleared after duration
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
    for _ in range(20):  # Run multiple trials
        # Apply sleep
        battle.execute_turn(sleep_move, battle.enemy_pokemon)
        
        # Count turns until wake up
        turns = 0
        while battle.enemy_pokemon.status == StatusEffect.SLEEP:
            turns += 1
            battle.end_turn()
            
        durations.add(turns)
        
        # Reset for next trial
        battle.enemy_pokemon.set_status(None)
    
    # Sleep should last 1-3 turns
    assert durations.issubset({1, 2, 3})
    assert len(durations) > 1  # Should get different durations
