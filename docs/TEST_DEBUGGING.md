# Test Debugging Guide

This guide outlines strategies for effectively debugging tests in the Fakemon project, with practical examples from our battle system tests.

## 1. Managing Test Output

### Controlling Verbosity

- Use pytest's verbosity levels wisely:
  ```ini
  # pytest.ini
  addopts = 
      -v  # Basic verbosity - shows test names and results
      # --verbose  # More detailed - can be overwhelming with debug logs
  ```

- For temporary debugging, you can override verbosity:
  ```bash
  pytest -vv specific_test.py  # More verbose for a specific test
  ```

### Debug Logging Strategy

1. **Conditional Logging**: Use debug mode to control output
   ```python
   class Battle:
       def __init__(self, debug: bool = False):
           self.debug = debug
           
       def execute_turn(self):
           if self.debug:
               print("Detailed debug info")
           # ... battle logic
   ```

2. **Focused Debugging**: Only log relevant information
   ```python
   # Good - specific to what we're testing
   if self.debug:
       print(f"Attack: {attack} multiplier={multiplier}")
   
   # Bad - too much noise
   print(f"All stats: {pokemon.stats}")
   ```

3. **Clear Section Headers**: Make log sections easily scannable
   ```python
   if self.debug:
       print("\nSTATS BEFORE CRITICAL HIT:")
       # ... stats logging
       print("\nSTATS AFTER CRITICAL HIT:")
       # ... stats logging
   ```

## 2. Test Design Principles

### Handling Randomness

As seen in `test_battle_critical.py`, tests involving random elements need special consideration:

1. **Balance Trial Count vs Output**:
   ```python
   # Too verbose - many trials with debug on
   battle = Battle(debug=True)
   for _ in range(200):  # Lots of debug output
       if get_critical_hit():
           break

   # Better - fewer trials with debug, more without
   battle = Battle(debug=False)
   for _ in range(100):  # No debug spam
       if get_critical_hit():
           break
   ```

2. **Resource Management**:
   ```python
   move = Move(
       name="Test Move",
       pp=250  # Enough PP for all attempts
   )
   ```

3. **Valid Ranges vs Exact Values**:
   ```python
   # Bad - too precise for random factors
   assert critical_damage == base_damage * 2.0

   # Good - accounts for random range (0.85-1.00)
   assert 1.70 <= critical_damage / base_damage <= 2.35
   ```

### Test Validity Checklist

Before debugging, verify test fundamentals:

1. **Preconditions**:
   - Are all required objects properly initialized?
   - Are stat values reasonable for what's being tested?
   - Is there enough PP/HP/etc. for all test operations?

2. **Assumptions**:
   - Does the test assume specific random outcomes?
   - Are timing/ordering assumptions valid?
   - Are stat calculations working as expected?

3. **Assertions**:
   - Do they account for all valid outcomes?
   - Are ranges appropriate for random factors?
   - Are error messages clear and helpful?

## 3. Common Pitfalls

1. **Resource Exhaustion**
   ```python
   # Problem: PP runs out before critical hit occurs
   move = Move(pp=50)  # Too low for 200 attempts
   
   # Solution: Increase PP or reset move between attempts
   move = Move(pp=250)  # Enough for all attempts
   ```

2. **State Management**
   ```python
   # Problem: State carries between attempts
   for _ in range(trials):
       battle.execute_turn(move, defender)  # HP keeps decreasing
   
   # Solution: Reset state each attempt
   for _ in range(trials):
       defender.current_hp = defender.stats.hp  # Reset HP
       battle.execute_turn(move, defender)
   ```

3. **Overly Strict Assertions**
   ```python
   # Problem: Doesn't account for valid variations
   assert damage == expected_damage
   
   # Solution: Allow for valid range
   assert min_damage <= damage <= max_damage
   ```

## 4. Debugging Process

1. **Isolate the Issue**:
   ```bash
   # Run specific test with debug mode
   battle = Battle(debug=True)
   pytest tests/core/test_battle_critical.py::test_critical_hit_damage -v
   ```

2. **Add Strategic Logging**:
   - Enable debug mode only when needed
   - Add detailed calculations only where needed
   - Use clear section headers

3. **Verify Assumptions**:
   - Check stat values before/after changes
   - Verify damage calculations
   - Confirm random number distributions

4. **Refine the Test**:
   - Adjust attempt counts based on probability
   - Ensure sufficient resources (PP, HP)
   - Update assertions to allow valid variations

## 5. Cross-Referencing Tests

When debugging test failures, it's crucial to cross-reference related tests to validate assumptions. Here's a real example from our battle system:

### Case Study: Weather and Critical Hit Interaction

In `test_battle_weather.py`, we initially had an incorrect assumption:
```python
# Original incorrect test
def test_weather_damage_order():
    """Test that weather effects are applied before critical hits."""
    # ... test setup ...
    expected_ratio = 1.0  # Incorrectly assumed crit and weather should cancel out
    actual_ratio = crit_damage / non_crit_damage
    assert 0.9 <= actual_ratio <= 1.1
```

The test assumed that a critical hit in sun should do the same damage as a non-critical hit in clear weather. To debug this:

1. **Check Related Tests**:
   - Examined `test_battle_critical.py`
   - Found that critical hits should always do ~2x damage
   - Discovered standard ratio range (1.70-2.35) accounting for random factor

2. **Analyze Assumptions**:
   ```python
   # Walk through the damage calculation
   Non-critical in sun:
   - Base damage * 0.5 (sun weakens water) = X
   
   Critical in sun:
   - Base damage * 0.5 (sun weakens water) * 2.0 (crit) = 2X
   
   Expected ratio = 2X/X = 2.0 (before random factor)
   ```

3. **Validate Implementation**:
   - Confirmed battle.py correctly applies multipliers
   - Weather and critical hits are independent multipliers
   - Critical hits should always double damage

4. **Fix the Test**:
```python
def test_weather_damage_order():
    """Test that critical hits do 2x damage regardless of weather.
    
    Damage calculation order:
    1. Base damage
    2. Weather effects (e.g., 0.5x in sun for water moves)
    3. Critical hit multiplier (2.0x)
    4. Random factor (0.85-1.00)
    
    Expected ratio range: 1.70-2.35
    - Min: 2.0 * (0.85/1.00) ≈ 1.70
    - Max: 2.0 * (1.00/0.85) ≈ 2.35
    """
    # ... test setup ...
    assert 1.70 <= actual_ratio <= 2.35
```

This process revealed that the test's assumption was incorrect, not the implementation. By cross-referencing `test_battle_critical.py`, we understood that critical hits should maintain their 2x multiplier regardless of other damage modifiers.

### Key Takeaways

1. **Cross-Reference Related Tests**:
   - Look for similar tests that might provide insight
   - Check how related mechanics are tested
   - Verify assumptions against established patterns

2. **Walk Through the Logic**:
   - Break down calculations step by step
   - Consider how different mechanics should interact
   - Document your reasoning

3. **Question Assumptions**:
   - Don't assume the implementation is wrong
   - Validate test assumptions against design
   - Check if similar tests handle the case differently

4. **Document Insights**:
   - Add detailed docstrings explaining the logic
   - Include examples of calculations
   - Note why certain ranges or values are used

## 6. Documentation

Always document key insights:

```python
def test_critical_hit_damage():
    """Test that critical hits deal 2.0x damage and ignore stat reductions.
    
    Critical hit damage calculation:
    1. Base damage * 2.0 for critical hit
    2. Random factor (0.85-1.00) applied to both normal and crit hits
    3. Expected ratio range: 1.70-2.35
       - Min: 2.0 * (0.85/1.00) ≈ 1.70
       - Max: 2.0 * (1.00/0.85) ≈ 2.35
    """
```

This helps future developers understand the reasoning behind test parameters and assertion ranges.
