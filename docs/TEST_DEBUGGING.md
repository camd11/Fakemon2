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

1. **Layered Logging**: Structure logs in layers of detail
   ```python
   # Basic outcome
   print("CRITICAL HIT CHECK:")
   print(f"Critical hit roll: {roll} (threshold: {threshold})")
   print(f"Critical hit: {is_critical}")

   # Detailed calculations (when needed)
   print("\nCRITICAL HIT DAMAGE CALCULATION:")
   print(f"Base damage calculation:")
   print(f"  Level factor: {level_factor}")
   print(f"  Move power: {power}")
   ```

2. **Focused Debugging**: Only log relevant information
   ```python
   # Good - specific to what we're testing
   print(f"Attack: {attack} multiplier={multiplier}")
   
   # Bad - too much noise
   print(f"All stats: {pokemon.stats}")
   ```

3. **Clear Section Headers**: Make log sections easily scannable
   ```python
   print("\nSTATS BEFORE CRITICAL HIT:")
   # ... stats logging
   print("\nSTATS AFTER CRITICAL HIT:")
   # ... stats logging
   ```

## 2. Test Design Principles

### Handling Randomness

As seen in `test_battle_critical.py`, tests involving random elements need special consideration:

1. **Adequate Sample Size**:
   ```python
   # Too few attempts - unreliable
   for _ in range(50):
       if get_critical_hit():
           break

   # Better - accounts for 1/24 chance
   for _ in range(200):
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
   assert critical_damage == base_damage * 1.5

   # Good - accounts for random range (0.85-1.00)
   assert 1.28 <= critical_damage / base_damage <= 1.76
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
   # Run specific test with maximum verbosity
   pytest tests/core/test_battle_critical.py::test_critical_hit_damage -vv
   ```

2. **Add Strategic Logging**:
   - Start with high-level outcomes
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
    """Test that critical hits deal 1.5x damage and ignore stat reductions.
    
    Critical hit damage calculation:
    1. Base damage * 1.5 for critical hit
    2. Random factor (0.85-1.00) applied to both normal and crit hits
    3. Expected ratio range: 1.28-1.76
       - Min: 1.5 * (0.85/1.00) ≈ 1.28
       - Max: 1.5 * (1.00/0.85) ≈ 1.76
    """
```

This helps future developers understand the reasoning behind test parameters and assertion ranges.
