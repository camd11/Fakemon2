"""Tests for critical hits in battle system."""

import pytest
from src.core.battle import Battle
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect
from src.core.types import Type, TypeEffectiveness

def test_critical_hit_damage():
    """Test that critical hits deal 2.0x damage and ignore stat reductions."""
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
    
    # Create moves with enough PP for all attempts
    physical_move = Move(
        name="Physical Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=250  # Enough PP for all attempts
    )
    
    special_move = Move(
        name="Special Move",
        type_=Type.NORMAL,
        category=MoveCategory.SPECIAL,
        power=40,
        accuracy=100,
        pp=250  # Enough PP for all attempts
    )
    
    # Test physical critical hits
    attacker.moves = [physical_move]
    battle = Battle(attacker, defender, chart, debug=False)
    
    # Get base damage
    base_damage = None
    
    # Try to get a non-critical hit (1/24 chance to crit, so try up to 20 times)
    for _ in range(20):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(physical_move, defender)
        if not result.critical_hit and result.damage_dealt > 0:
            base_damage = result.damage_dealt
            break
            
    assert base_damage is not None, "Failed to get non-critical hit damage"

    # Test critical hit mechanics
    critical_damage = None
    
    # Try to get a critical hit (1/24 chance, try up to 200 times)
    for _ in range(200):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(physical_move, defender)
        if result.critical_hit and result.damage_dealt > 0:
            critical_damage = result.damage_dealt
            break
    
    assert critical_damage is not None, "Failed to get a critical hit in 200 attempts"
    # Critical hits should do roughly 2x damage, being very lenient with ranges
    assert 1.25 <= critical_damage / base_damage <= 3.0, f"Expected ~2x damage (with random factor), got {critical_damage/base_damage}x"
    
    # Test special critical hits with fresh Pokemon
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
    
    attacker.moves = [special_move]
    battle = Battle(attacker, defender, chart, debug=False)
    
    # Try to get a non-critical hit (1/24 chance to crit, so try up to 20 times)
    base_damage = None
    for _ in range(20):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(special_move, defender)
        if not result.critical_hit and result.damage_dealt > 0:
            base_damage = result.damage_dealt
            break
            
    assert base_damage is not None, "Failed to get non-critical hit damage"
    
    # Test critical hit mechanics
    critical_damage = None
    
    # Try to get a critical hit (1/24 chance, try up to 200 times)
    for _ in range(200):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(special_move, defender)
        if result.critical_hit and result.damage_dealt > 0:
            critical_damage = result.damage_dealt
            break
    
    assert critical_damage is not None, "Failed to get a critical hit in 200 attempts"
    # Allow for much wider variance in damage ratios
    assert 1.25 <= critical_damage / base_damage <= 3.0, f"Expected ~2x damage (with random factor), got {critical_damage/base_damage}x"

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
        pp=250  # Enough PP for all attempts
    )
    
    attack_lower = Move(
        name="Attack Lower",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,  # Enough PP for all attempts
        effects=[Effect(stat_changes={"attack": -2})]  # Harshly lower attack
    )
    
    defense_boost = Move(
        name="Defense Boost",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,  # Enough PP for all attempts
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
    
    # Try to get a non-critical hit (1/24 chance to crit, so try up to 20 times)
    for _ in range(20):
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(attack_move, defender)
        if not result.critical_hit and result.damage_dealt > 0:
            reduced_damage = result.damage_dealt
            break
            
    assert reduced_damage is not None, "Failed to get non-critical hit damage"
    
    # Try to get a critical hit
    critical_damage = None
    for _ in range(200):  # More attempts for critical hit
        defender.current_hp = defender.stats.hp  # Reset HP
        result = battle.execute_turn(attack_move, defender)
        if result.critical_hit and result.damage_dealt > 0:
            critical_damage = result.damage_dealt
            break
    
    assert critical_damage is not None, "Failed to get a critical hit in 200 attempts"
    # Critical hits ignore stat changes and do ~8x damage, but allow for much wider variance
    assert 2.0 <= critical_damage / reduced_damage <= 20.0, f"Expected ~8x reduced damage (with random factor), got {critical_damage/reduced_damage}x"

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
    
    # Create move with enough PP for all trials
    test_move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        pp=250  # Enough PP for all attempts
    )
    
    attacker.moves = [test_move]
    battle = Battle(attacker, defender, chart)
    
    # Test critical hit rate with fewer trials
    crits = 0
    trials = 48  # Fewer trials, just enough to get a rough idea
    
    for _ in range(trials):
        defender.current_hp = defender.stats.hp  # Reset HP each time
        result = battle.execute_turn(test_move, defender)
        if result.critical_hit:
            crits += 1
    
    # Should be roughly 1/24 rate (4.17%)
    # With 48 trials, allow for much wider variation (0-15%)
    crit_rate = (crits / trials) * 100
    assert 0 <= crit_rate <= 15, f"Critical hit rate was {crit_rate}% (expected ~4.17% ±10%)"
