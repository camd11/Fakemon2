"""Tests for critical hits in battle system."""

import pytest
from src.core.battle import Battle
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect
from src.core.types import Type, TypeEffectiveness

def test_critical_hit_damage():
    """Test that critical hits deal 1.5x damage and ignore stat reductions."""
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Create physical and special moves
    physical_move = Move(
        name="Physical Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=100
    )
    
    special_move = Move(
        name="Special Move",
        type_=Type.NORMAL,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=100
    )
    
    attacker.moves = [physical_move, special_move]
    
    # Test physical critical hits
    battle = Battle(attacker, defender, chart)
    
    # Get base damage
    base_damage = None
    physical_move = Move(
        name="Physical Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=250  # Enough PP for all attempts
    )
    attacker.moves = [physical_move]
    battle = Battle(attacker, defender, chart)
    
    # Try to get a non-critical hit
    for _ in range(10):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(physical_move, defender)
        if not result.critical_hit and result.damage_dealt > 0:
            base_damage = result.damage_dealt
            break
            
    assert base_damage is not None, "Failed to get non-critical hit damage"

    # Test critical hit mechanics
    critical_damage = None
    
    # Try to get a critical hit (1/24 chance, try more times to be reliable)
    for _ in range(200):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(physical_move, defender)
        if result.critical_hit and result.damage_dealt > 0:
            critical_damage = result.damage_dealt
            break
    
    assert critical_damage is not None, "Failed to get a critical hit in 200 attempts"
    # Critical hits should do exactly 1.5x damage
    # Allow for random damage factor (0.85-1.00) on both base and crit damage
    # Max ratio: 1.5 * (1.00/0.85) ≈ 1.76
    # Min ratio: 1.5 * (0.85/1.00) ≈ 1.28
    assert 1.28 <= critical_damage / base_damage <= 1.76, f"Expected ~1.5x damage (with random factor), got {critical_damage/base_damage}x"
    
    # Test special critical hits
    # Get base damage
    base_damage = None
    special_move = Move(
        name="Special Move",
        type_=Type.NORMAL,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=250  # Enough PP for all attempts
    )
    attacker.moves = [special_move]
    battle = Battle(attacker, defender, chart)
    
    # Try to get a non-critical hit
    for _ in range(10):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(special_move, defender)
        if not result.critical_hit and result.damage_dealt > 0:
            base_damage = result.damage_dealt
            break
            
    assert base_damage is not None, "Failed to get non-critical hit damage"
    
    # Test critical hit mechanics
    critical_damage = None
    
    # Try to get a critical hit (1/24 chance, try more times to be reliable)
    for _ in range(200):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(special_move, defender)
        if result.critical_hit and result.damage_dealt > 0:
            critical_damage = result.damage_dealt
            break
    
    assert critical_damage is not None, "Failed to get a critical hit in 200 attempts"
    # Allow for random damage factor (0.85-1.00) on both base and crit damage
    # Max ratio: 1.5 * (1.00/0.85) ≈ 1.76
    # Min ratio: 1.5 * (0.85/1.00) ≈ 1.28
    assert 1.28 <= critical_damage / base_damage <= 1.76, f"Expected ~1.5x damage (with random factor), got {critical_damage/base_damage}x"

def test_critical_hit_stat_ignore():
    """Test that critical hits ignore attack reductions and defense boosts."""
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Create moves
    attack_move = Move(
        name="Attack Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=100
    )
    
    attack_lower = Move(
        name="Attack Lower",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30,
        effects=[Effect(stat_changes={"attack": -2})]  # Harshly lower attack
    )
    
    defense_boost = Move(
        name="Defense Boost",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30,
        effects=[Effect(stat_changes={"defense": 2})]  # Sharply raise defense
    )
    
    attacker.moves = [attack_move, attack_lower]
    defender.moves = [defense_boost]
    
    # Get normal damage with lowered attack vs boosted defense
    reduced_damage = None
    battle = Battle(attacker, defender, chart)
    
    # Apply stat changes
    battle.execute_turn(attack_lower, attacker)
    battle.execute_turn(defense_boost, defender)
    
    # Try to get a non-critical hit
    for _ in range(10):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(attack_move, defender)
        if not result.critical_hit and result.damage_dealt > 0:
            reduced_damage = result.damage_dealt
            break
            
    assert reduced_damage is not None, "Failed to get non-critical hit damage"
    
    # Try to get a critical hit
    critical_damage = None
    for _ in range(200):  # Increased attempts to match other tests
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(attack_move, defender)
        if result.critical_hit and result.damage_dealt > 0:
            critical_damage = result.damage_dealt
            break
    
    assert critical_damage is not None, "Failed to get a critical hit in 200 attempts"
    # Critical hits ignore stat changes and do ~1.5x base damage, with random factor
    # Since attack was halved and defense was doubled, critical hit should do ~4x damage
    # (2x from restoring halved attack, 2x from removing doubled defense, 1.5x from crit)
    # With random factor (0.85-1.00), expect ratio between 3.4x and 5x
    assert 3.4 <= critical_damage / reduced_damage <= 5, f"Expected ~4x reduced damage (with random factor), got {critical_damage/reduced_damage}x"

def test_critical_hit_rate():
    """Test that critical hits occur at roughly 1/24 rate."""
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    attacker = Pokemon(
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    defender = Pokemon(
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=1000  # Lots of PP for multiple trials
    )
    
    attacker.moves = [move]
    battle = Battle(attacker, defender, chart)
    
    # Test large number of hits
    crits = 0
    trials = 1000
    
    for _ in range(trials):
        defender.current_hp = defender.stats.hp  # Reset HP each time
        result = battle.execute_turn(move, defender)
        if result.critical_hit:
            crits += 1
    
    # Should be roughly 1/24 rate (4.17%)
    # Allow for random variation (3-6%)
    crit_rate = (crits / trials) * 100
    assert 3 <= crit_rate <= 6, f"Critical hit rate was {crit_rate}% (expected ~4.17%)"
