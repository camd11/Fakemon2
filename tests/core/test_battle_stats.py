"""Tests for stat changes in battle system."""

import pytest
from src.core.battle import Battle
from src.core.pokemon import Pokemon, Stats
from src.core.move import Move, MoveCategory, Effect
from src.core.types import Type, TypeEffectiveness

def test_stat_modification():
    """Test that moves can modify stats correctly."""
    # Create type chart with neutral effectiveness
    chart = TypeEffectiveness()
    chart.load_from_json({
        "normal": {"normal": 1.0}
    })
    
    # Create Pokemon
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
    
    # Create move that lowers defense by 1 stage
    stat_lower_move = Move(
        name="Tail Whip",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30,
        effects=[Effect(stat_changes={"defense": -1})]
    )
    
    attacker.moves = [stat_lower_move]
    battle = Battle(attacker, defender, chart)
    
    # Execute move and verify stat change
    result = battle.execute_turn(stat_lower_move, defender)
    
    assert len(result.stat_changes) == 1
    assert result.stat_changes[0] == ("defense", -1)
    assert "Defender's defense was lowered!" in result.messages
    assert defender.get_stat_multiplier("defense") == 2/3  # -1 stage = 2/3 multiplier

def test_stat_bounds():
    """Test that stat modifications respect minimum/maximum bounds."""
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
    
    # Create moves that modify stats by 2 stages
    sharp_increase = Move(
        name="Sharply Increase",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30,
        effects=[Effect(stat_changes={"attack": 2})]
    )
    
    harsh_decrease = Move(
        name="Harsh Decrease",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30,
        effects=[Effect(stat_changes={"defense": -2})]
    )
    
    attacker.moves = [sharp_increase, harsh_decrease]
    battle = Battle(attacker, defender, chart)
    
    # Test maximum stat increase (+6 stages)
    for _ in range(4):  # Try to go beyond +6 with 4 uses of +2
        result = battle.execute_turn(sharp_increase, attacker)
    
    # Should be capped at 4x (+6 stages)
    assert attacker.get_stat_multiplier("attack") == 4.0
    
    # Test minimum stat decrease (-6 stages)
    for _ in range(4):  # Try to go beyond -6 with 4 uses of -2
        result = battle.execute_turn(harsh_decrease, defender)
    
    # Should be capped at 0.25x (-6 stages)
    assert defender.get_stat_multiplier("defense") == 0.25

def test_multiple_stat_changes():
    """Test moves that modify multiple stats."""
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
    
    # Create move that modifies multiple stats
    multi_stat_move = Move(
        name="Multi Stat",
        type_=Type.NORMAL,
        category=MoveCategory.STATUS,
        power=0,
        accuracy=100,
        pp=30,
        effects=[Effect(stat_changes={
            "attack": 1,
            "defense": -1,
            "speed": 2
        })]
    )
    
    attacker.moves = [multi_stat_move]
    battle = Battle(attacker, defender, chart)
    
    # Execute move and verify all stat changes
    result = battle.execute_turn(multi_stat_move, defender)
    
    assert len(result.stat_changes) == 3
    assert ("attack", 1) in result.stat_changes
    assert ("defense", -1) in result.stat_changes
    assert ("speed", 2) in result.stat_changes
    
    assert "Defender's attack was raised!" in result.messages
    assert "Defender's defense was lowered!" in result.messages
    assert "Defender's speed was raised!" in result.messages
    
    assert defender.get_stat_multiplier("attack") == 1.5  # +1 stage
    assert defender.get_stat_multiplier("defense") == 2/3  # -1 stage
    assert defender.get_stat_multiplier("speed") == 2.0  # +2 stages