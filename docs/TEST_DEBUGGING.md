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

## 5. Documentation

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
