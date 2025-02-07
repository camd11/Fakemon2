"""Tests for move accuracy in battle system.

Note on Test Ranges:
These tests use deliberately lenient ranges to prevent flaky failures while still
catching significant implementation errors. For example:

- Basic accuracy test (10-90% range):
  * Testing 50% accuracy move
  * 20 trials with wide range
  * Would catch if accuracy was 0% or 100%
  * Allows for normal random variation

- Baseline accuracy test (40-100% range):
  * Testing 75% accuracy move
  * 20 trials with wide range
  * Would catch if accuracy was too low
  * Allows for normal random variation

- Boosted accuracy (60-100% range):
  * Should be near 100% after boost
  * Must be higher than baseline
  * Would catch if boost didn't work
  * Allows for normal random variation

- Reduced accuracy (10-65% range):
  * Expected ~37.5% after evasion
  * Wide range due to combined randomness
  * Would catch if evasion had no effect
  * Still validates core mechanics
"""

import pytest
from src.core.battle import Battle
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect, StatusEffect
from src.core.types import Type, TypeEffectiveness
from src.core.ability import Ability, AbilityType

def test_basic_accuracy():
    """Test that moves can miss based on their accuracy."""
    # Create type chart with neutral effectiveness
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
    
    # Test multiple times to verify ~50% accuracy
    hits = 0
    trials = 20  # Double from 10 trials, still wide range
    
    for _ in range(trials):
        # Reset defender's HP and create fresh move for each trial
        defender = Pokemon(
            name="Defender",
            types=(Type.NORMAL,),
            base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
            level=50
        )
        inaccurate_move = Move(
            name="Inaccurate Move",
            type_=Type.NORMAL,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=50,
            pp=1
        )
        attacker.moves = [inaccurate_move]
        battle = Battle(attacker, defender, chart, debug=False)  # Disable debug for multiple trials
        
        result = battle.execute_turn(inaccurate_move, defender)
        if not result.move_missed:
            hits += 1
            
    # Allow for much wider random variation (10-90% success rate with 20 trials)
    assert 10 <= (hits / trials) * 100 <= 90

def test_perfect_accuracy():
    """Test that moves with perfect accuracy (None) never miss."""
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
    
    # Create move with perfect accuracy
    perfect_move = Move(
        name="Swift",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=None,  # Perfect accuracy
        pp=250  # Enough PP for all attempts
    )
    
    # Test with max evasion
    evasion_boost = Move(
        name="Double Team",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(stat_changes={"evasion": 6})]  # Max evasion
    )
    
    attacker.moves = [perfect_move]
    defender.moves = [evasion_boost]
    battle = Battle(attacker, defender, chart)
    
    # Max out evasion
    battle.execute_turn(evasion_boost, defender)
    
    # Should never miss despite max evasion
    for _ in range(20):
        result = battle.execute_turn(perfect_move, defender)
        assert not result.move_missed, "Perfect accuracy move should never miss"
        defender.current_hp = defender.stats.hp  # Reset HP

def test_multi_stage_accuracy():
    """Test accuracy changes with multiple stat stages."""
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
    test_move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=75,
        pp=250
    )
    
    accuracy_boost = Move(
        name="Lock On",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(stat_changes={"accuracy": 2})]  # +2 stages
    )
    
    evasion_boost = Move(
        name="Double Team",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(stat_changes={"evasion": 2})]  # +2 stages
    )
    
    attacker.moves = [test_move, accuracy_boost]
    defender.moves = [evasion_boost]
    battle = Battle(attacker, defender, chart)
    
    # Test baseline first
    hits = 0
    trials = 20
    
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    baseline_accuracy = hits / trials
    
    # Test with +2 accuracy
    battle.execute_turn(accuracy_boost, attacker)
    
    hits = 0
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    boosted_accuracy = hits / trials
    assert boosted_accuracy > baseline_accuracy, "Multiple accuracy stages should improve hit rate more than single stage"
    
    # Test with +2 evasion
    attacker = Pokemon(  # Fresh Pokemon
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50,
        moves=[test_move]
    )
    
    defender = Pokemon(  # Fresh Pokemon
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50,
        moves=[evasion_boost]
    )
    
    battle = Battle(attacker, defender, chart)
    battle.execute_turn(evasion_boost, defender)
    
    hits = 0
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    reduced_accuracy = hits / trials
    assert reduced_accuracy < baseline_accuracy, "Multiple evasion stages should reduce hit rate more than single stage"

def test_max_min_stages():
    """Test accuracy/evasion at maximum/minimum stages."""
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
    test_move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=75,
        pp=250
    )
    
    max_accuracy = Move(
        name="Lock On",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(stat_changes={"accuracy": 6})]  # Max stages
    )
    
    min_accuracy = Move(
        name="Sand Attack",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(stat_changes={"accuracy": -6})]  # Min stages
    )
    
    attacker.moves = [test_move, max_accuracy, min_accuracy]
    battle = Battle(attacker, defender, chart)
    
    # Test max accuracy (+6 stages)
    battle.execute_turn(max_accuracy, attacker)
    
    hits = 0
    trials = 20
    
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    max_hit_rate = hits / trials
    assert max_hit_rate >= 0.90, "Max accuracy stages should result in very high hit rate"
    
    # Test min accuracy (-6 stages)
    attacker = Pokemon(  # Fresh Pokemon
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50,
        moves=[test_move, min_accuracy]
    )
    
    defender = Pokemon(  # Fresh Pokemon
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    battle = Battle(attacker, defender, chart)
    battle.execute_turn(min_accuracy, attacker)
    
    hits = 0
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    min_hit_rate = hits / trials
    assert min_hit_rate <= 0.30, "Min accuracy stages should result in very low hit rate"

def test_paralysis_accuracy():
    """Test accuracy when combined with paralysis."""
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
    test_move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=75,
        pp=250
    )
    
    paralyze = Move(
        name="Thunder Wave",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(status=StatusEffect.PARALYSIS, status_chance=100)]
    )
    
    accuracy_boost = Move(
        name="Lock On",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(stat_changes={"accuracy": 2})]  # +2 stages
    )
    
    attacker.moves = [test_move, accuracy_boost]
    defender.moves = [paralyze]
    battle = Battle(attacker, defender, chart)
    
    # First boost accuracy
    battle.execute_turn(accuracy_boost, attacker)
    
    # Then paralyze
    battle.execute_turn(paralyze, attacker)
    
    # Test hit rate with both paralysis and boosted accuracy
    hits = 0
    moves = 0
    trials = 48  # More trials to account for paralysis
    
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not "fully paralyzed" in result.messages:
            moves += 1
            if not result.move_missed:
                hits += 1
        defender.current_hp = defender.stats.hp
    
    # Calculate hit rate only for turns where paralysis didn't prevent movement
    hit_rate = hits / moves if moves > 0 else 0
    
    # Should still have boosted accuracy when not fully paralyzed
    assert hit_rate >= 0.60, "Accuracy boost should still apply when not fully paralyzed"

def test_accuracy_ability():
    """Test that accuracy-boosting abilities increase hit rate."""
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
    
    # Create move with low accuracy
    test_move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=75,
        pp=250
    )
    
    attacker.moves = [test_move]
    battle = Battle(attacker, defender, chart)
    
    # Test baseline accuracy first
    hits = 0
    trials = 20
    
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    baseline_accuracy = hits / trials
    
    # Test with accuracy-boosting ability
    attacker = Pokemon(  # Fresh Pokemon
        name="Attacker",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50,
        moves=[test_move]
    )
    
    # Add accuracy-boosting ability (20% boost)
    attacker.ability = Ability(
        name="Keen Eye",
        type_=AbilityType.ACCURACY_BOOST,
        accuracy_multiplier=1.2
    )
    
    battle = Battle(attacker, defender, chart)
    
    hits = 0
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    boosted_accuracy = hits / trials
    assert boosted_accuracy > baseline_accuracy, "Accuracy-boosting ability should improve hit rate"

def test_evasion_ability():
    """Test that evasion-boosting abilities decrease opponent's hit rate."""
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
    
    # Create move with moderate accuracy
    test_move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=75,
        pp=250
    )
    
    attacker.moves = [test_move]
    battle = Battle(attacker, defender, chart)
    
    # Test baseline accuracy first
    hits = 0
    trials = 20
    
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    baseline_accuracy = hits / trials
    
    # Test with evasion-boosting ability
    defender = Pokemon(  # Fresh Pokemon
        name="Defender",
        types=(Type.NORMAL,),
        base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
        level=50
    )
    
    # Add evasion-boosting ability (20% boost)
    defender.ability = Ability(
        name="Sand Veil",
        type_=AbilityType.EVASION_BOOST,
        evasion_multiplier=1.2
    )
    
    battle = Battle(attacker, defender, chart)
    
    hits = 0
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    reduced_accuracy = hits / trials
    assert reduced_accuracy < baseline_accuracy, "Evasion-boosting ability should reduce hit rate"

def test_ability_stat_stacking():
    """Test that abilities stack properly with stat changes."""
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
    test_move = Move(
        name="Test Move",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=75,
        pp=250
    )
    
    accuracy_boost = Move(
        name="Lock On",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=250,
        effects=[Effect(stat_changes={"accuracy": 1})]
    )
    
    # Add accuracy-boosting ability (20% boost)
    attacker.ability = Ability(
        name="Keen Eye",
        type_=AbilityType.ACCURACY_BOOST,
        accuracy_multiplier=1.2
    )
    
    attacker.moves = [test_move, accuracy_boost]
    battle = Battle(attacker, defender, chart)
    
    # Test with both ability and stat boost
    battle.execute_turn(accuracy_boost, attacker)  # Boost accuracy stat
    
    hits = 0
    trials = 20
    
    for _ in range(trials):
        result = battle.execute_turn(test_move, defender)
        if not result.move_missed:
            hits += 1
        defender.current_hp = defender.stats.hp
    
    combined_accuracy = hits / trials
    assert combined_accuracy >= 0.80, "Ability and stat boost should stack for high accuracy"

def test_perfect_accuracy_vs_abilities():
    """Test that perfect accuracy moves ignore evasion abilities."""
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
    
    # Create move with perfect accuracy
    perfect_move = Move(
        name="Swift",
        type_=Type.NORMAL,
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=None,  # Perfect accuracy
        pp=250
    )
    
    # Add evasion-boosting ability
    defender.ability = Ability(
        name="Sand Veil",
        type_=AbilityType.EVASION_BOOST,
        evasion_multiplier=1.2
    )
    
    attacker.moves = [perfect_move]
    battle = Battle(attacker, defender, chart)
    
    # Should never miss despite evasion ability
    for _ in range(20):
        result = battle.execute_turn(perfect_move, defender)
        assert not result.move_missed, "Perfect accuracy move should ignore evasion ability"
        defender.current_hp = defender.stats.hp

def test_baseline_accuracy():
    """Test the baseline accuracy of a move."""
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
    
    # First test baseline accuracy
    hits = 0
    trials = 20  # Double from 10 trials, still wide range
    
    for _ in range(trials):
        # Reset defender's HP and create fresh move for each trial
        defender = Pokemon(
            name="Defender",
            types=(Type.NORMAL,),
            base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
            level=50
        )
        normal_move = Move(
            name="Normal Move",
            type_=Type.NORMAL,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=75,  # Lower accuracy to better show effects
            pp=1
        )
        attacker.moves = [normal_move]
        battle = Battle(attacker, defender, chart, debug=False)  # Disable debug for multiple trials
        
        result = battle.execute_turn(normal_move, defender)
        if not result.move_missed:
            hits += 1
    
    baseline_accuracy = hits / trials
    
    # Test with increased accuracy
    hits = 0
    for _ in range(trials):
        # Reset defender's HP and create fresh moves for each trial
        defender = Pokemon(
            name="Defender",
            types=(Type.NORMAL,),
            base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
            level=50
        )
        normal_move = Move(
            name="Normal Move",
            type_=Type.NORMAL,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=75,
            pp=1
        )
        accuracy_boost = Move(
            name="Lock On",
            type_=Type.NORMAL,
            category=MoveCategory.STATUS,
            power=0,
            accuracy=100,
            pp=1,
            effects=[Effect(stat_changes={"accuracy": 1})]
        )
        attacker.moves = [normal_move, accuracy_boost]
        battle = Battle(attacker, defender, chart, debug=False)  # Disable debug for multiple trials
        
        battle.execute_turn(accuracy_boost, attacker)  # Boost accuracy
        result = battle.execute_turn(normal_move, defender)
        if not result.move_missed:
            hits += 1
    
    boosted_accuracy = hits / trials
    assert boosted_accuracy > baseline_accuracy
    
    # Test with increased evasion
    hits = 0
    for _ in range(trials):
        # Reset both Pokemon's stats for each trial
        attacker = Pokemon(
            name="Attacker",
            types=(Type.NORMAL,),
            base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
            level=50
        )
        normal_move = Move(
            name="Normal Move",
            type_=Type.NORMAL,
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=75,
            pp=1
        )
        evasion_boost = Move(
            name="Double Team",
            type_=Type.NORMAL,
            category=MoveCategory.STATUS,
            power=0,
            accuracy=100,
            pp=1,
            effects=[Effect(stat_changes={"evasion": 1})]
        )
        attacker.moves = [normal_move]
        defender.moves = [evasion_boost]
        # Reset defender's HP and create fresh battle
        defender = Pokemon(
            name="Defender",
            types=(Type.NORMAL,),
            base_stats=Stats(hp=100, attack=100, defense=100,
                        special_attack=100, special_defense=100, speed=100),
            level=50
        )
        # First trial with debug to see multipliers
        debug = _ == 0  # Only debug first trial
        battle = Battle(attacker, defender, chart, debug=debug)
        
        battle.execute_turn(evasion_boost, defender)  # Boost evasion
        if debug:
            print(f"\nEvasion multiplier: {defender.get_stat_multiplier('evasion')}")
            print(f"Accuracy multiplier: {attacker.get_stat_multiplier('accuracy')}")
        result = battle.execute_turn(normal_move, defender)
        if not result.move_missed:
            hits += 1
    
    reduced_accuracy = hits / trials
    # Calculate expected accuracy ranges
    # Base accuracy: 75%
    # After accuracy boost (+1 stage): 75% * (2/1) = 150% (capped at 100%)
    # After evasion boost (+1 stage): 75% * (1/2) = 37.5%
    
    # Allow for much wider random variation with 20 trials
    assert 0.40 <= baseline_accuracy <= 1.00, f"Expected baseline accuracy around 75% (±35%), got {baseline_accuracy*100:.1f}%"
    assert 0.60 <= boosted_accuracy <= 1.00, f"Expected boosted accuracy around 100% (capped), got {boosted_accuracy*100:.1f}%"
    assert 0.10 <= reduced_accuracy <= 0.65, f"Expected reduced accuracy around 37.5% (±27.5%), got {reduced_accuracy*100:.1f}%"
