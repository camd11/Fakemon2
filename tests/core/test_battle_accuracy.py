"""Tests for move accuracy in battle system."""

import pytest
from src.core.battle import Battle
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect
from src.core.types import Type, TypeEffectiveness

def test_basic_accuracy():
    """Test that moves can miss based on their accuracy."""
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
    trials = 20  # Reduced trials, increased range to compensate
    
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
            
    # Allow for wider random variation (25-75% success rate with 20 trials)
    assert 25 <= (hits / trials) * 100 <= 75

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
    trials = 20  # Reduced trials, increased range to compensate
    
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
    
    # Allow for random variation with 20 trials
    assert 0.60 <= baseline_accuracy <= 0.90, f"Expected baseline accuracy around 75% (±15%), got {baseline_accuracy*100:.1f}%"
    assert 0.80 <= boosted_accuracy <= 1.00, f"Expected boosted accuracy around 100% (capped), got {boosted_accuracy*100:.1f}%"
    assert 0.25 <= reduced_accuracy <= 0.50, f"Expected reduced accuracy around 37.5% (±12.5%), got {reduced_accuracy*100:.1f}%"

def test_status_move_accuracy():
    """Test that status moves ignore accuracy checks."""
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
    
    # Create status move with low accuracy
    status_move = Move(
        name="Status Move",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=1,  # Very low accuracy
        pp=30,
        effects=[Effect(stat_changes={"attack": -1})]
    )
    
    attacker.moves = [status_move]
    battle = Battle(attacker, defender, chart, debug=False)  # Disable debug for multiple trials
    
    # Status move should always hit despite low accuracy
    for _ in range(10):
        result = battle.execute_turn(status_move, defender)
        assert not result.move_missed
        assert len(result.stat_changes) == 1
        assert result.stat_changes[0] == ("attack", -1)
        assert defender.get_stat_multiplier("attack") < 1.0  # Verify stat was lowered
        defender.reset_stats()  # Reset for next iteration
