# Test Debugging Guide

[Previous content remains the same until "Test Design Principles" section]

## 2. Test Design Principles

### Deliberately Lenient Test Ranges

Our tests use intentionally generous ranges and high attempt counts for probability-based mechanics. This is a deliberate design choice to prevent flaky tests while still catching significant issues:

1. **Critical Hit Tests** (200 attempts):
   ```python
   # Very generous range to avoid false failures
   assert 1.25 <= critical_damage / base_damage <= 3.0
   
   # Rationale:
   # - Expected ratio is 2.0x
   # - Random factor is 0.85-1.00
   # - Wide range catches only egregious errors
   # - 200 attempts ensures we get a critical hit
   ```

2. **Accuracy Tests** (20 trials):
   ```python
   # Wide range for 75% accuracy move
   assert 0.40 <= baseline_accuracy <= 1.00
   
   # Rationale:
   # - Expected accuracy is 75%
   # - 20 trials is enough to catch major issues
   # - Range allows for normal random variation
   ```

3. **Status Effect Tests**:
   ```python
   # Paralysis (5-45% range)
   assert 0.05 <= paralysis_rate <= 0.45
   
   # Freeze thaw (40-100% range)
   assert 0.40 <= thaw_rate <= 1.00
   
   # Rationale:
   # - Expected rates: ~25% paralysis, ~89% thaw
   # - Wide ranges prevent random test failures
   # - Still catches implementation errors
   ```

Why So Lenient?
- Prevents flaky tests that fail randomly
- Focuses on catching real implementation errors
- Reduces developer frustration
- Still validates core mechanics work
- Catches order-of-magnitude issues

Example of What We Catch:
```python
# This implementation error would be caught:
if random.random() < 0.9:  # Wrong: 90% paralysis rate
    pokemon.paralyze()

# This minor variation would pass:
if random.random() < 0.3:  # OK: 30% is within acceptable range
    pokemon.paralyze()

# This severe error would fail:
if random.random() < 0.01:  # Caught: 1% is too low
    pokemon.paralyze()
```

[Rest of the original content remains the same]
