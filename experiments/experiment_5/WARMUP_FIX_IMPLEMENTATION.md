# Warmup Fix Implementation - ContinuousPruner

**Date**: 2025-11-04
**Status**: ✅ IMPLEMENTED - Testing in progress
**Issue**: BUG-004 - ContinuousPruner removes all context from turn 1

---

## Problem Summary

**Root Cause**: ContinuousPruner was removing 100% of context every turn because:
1. **No warmup period**: Pruning started immediately at turn 1
2. **Too aggressive**: 95% pruning rate removed almost everything
3. **Protection broken**: New items scored 0.55 importance, needed ≥0.95 to be protected
4. **Result**: Agent had zero memory, random flailing, no continuity

**Evidence**:
```
ContinuousPruner[5]: tokens_before=4197, tokens_after=0, removed=4197, items_in_context=0
ContinuousPruner[10]: tokens_before=4938, tokens_after=0, removed=4938, items_in_context=0
```

Every interaction: **100% of tokens removed, 0 items in context**

---

## Solution Implemented

**Approach**: Option 3 + 4C (Gradual Ramp + Recent Protection)

### Three-Phase Strategy

**Phase 1 - Warmup (Turns 1-5)**:
- Pruning rate: 10% (minimal)
- Purpose: Let agent build working memory
- Expected context: ~18K tokens by turn 5

**Phase 2 - Ramp (Turns 6-15)**:
- Pruning rate: Linear increase from 10% → 60%
- Purpose: Smooth transition to steady state
- Expected context: ~40-60K tokens by turn 15

**Phase 3 - Steady State (Turns 16+)**:
- Pruning rate: 60% (not 95%!)
- Purpose: Maintain stable context around target
- Expected context: ~80-100K tokens stabilized

### Additional Protection

**Recent Protection**: Always protect last 3 interactions
- Guarantees agent has immediate working memory
- Prevents pruning of current context
- Works regardless of importance scores

---

## Code Changes

### File: `pruner.py`

#### 1. Updated `__init__` Method (Lines 201-222)

**Added Parameters**:
```python
warmup_interactions: int = 5      # No pruning for first 5 turns
ramp_interactions: int = 10       # Gradual increase over next 10 turns
recent_protection: int = 3        # Always protect last 3 interactions
min_pruning_rate: float = 0.10    # Start at 10% during warmup
target_pruning_rate: float = 0.60 # Cap at 60% (not 95%!)
```

**Why These Values**:
- warmup=5: Standard 5-10% of 50-turn tasks (research best practice)
- ramp=10: Gives smooth 10-turn transition
- recent=3: Protects current + 2 previous interactions
- min_rate=0.10: Gentle start, allows 90% token retention
- target_rate=0.60: Aggressive but not insane (vs 0.95 which was catastrophic)

#### 2. New Method: `get_current_pruning_rate()` (Lines 317-347)

**Purpose**: Calculate pruning rate based on current phase

**Logic**:
```python
if interaction_count <= warmup_interactions:
    return min_pruning_rate  # 10% during warmup

if interaction_count <= warmup_interactions + ramp_interactions:
    # Linear ramp from min to target
    progress = (count - warmup) / ramp
    return min_rate + (progress * (target_rate - min_rate))

return target_pruning_rate  # 60% at steady state
```

**Example Outputs**:
```
Turn 1-5:   10% (warmup)
Turn 6:     15% (ramp start)
Turn 10:    33% (ramp mid)
Turn 15:    60% (ramp end)
Turn 16+:   60% (steady state)
```

#### 3. Updated `add_interaction()` Method (Lines 389-418)

**Changed**:
```python
# BEFORE:
adaptive_rate = self.calculate_adaptive_rate()  # Returns 0.90-1.10

# AFTER:
pruning_rate = self.get_current_pruning_rate()  # Returns 0.10-0.60
```

**Enhanced Debug Logging**:
```python
# Now shows phase (WARMUP, RAMP, STEADY) in logs
logging.info(f"ContinuousPruner[{count}] {phase}: "
            f"tokens_before={before}, "
            f"tokens_after={after}, "
            f"removed={removed}, "
            f"items_in_context={len(context)}, "
            f"pruning_rate={rate:.3f}")
```

**Logging Frequency**:
- Every turn during warmup (turns 1-5)
- Every 5 turns after warmup
- Purpose: Track phase transitions and context growth

#### 4. Updated `_prune_context()` Method (Lines 474-523)

**Added Recent Protection**:
```python
# Calculate recent threshold
recent_threshold = self.interaction_count - self.recent_protection

# NEW: Three-way protection
protected_items = [
    i for i in self.context
    if i.tier == "CORE"                          # Never prune CORE
    or i.importance >= 0.95                      # High importance
    or i.interaction_number > recent_threshold   # NEW: Recent items
]

prunable_items = [
    i for i in self.context
    if i.tier != "CORE"
    and i.importance < 0.95
    and i.interaction_number <= recent_threshold  # NEW: Must be old
]
```

**Protection Logic**:
- Turn 10, recent_protection=3: Protect turns 8, 9, 10
- Turn 20, recent_protection=3: Protect turns 18, 19, 20
- Guarantees agent always has last 3 conversations in memory

**Rebuild Context**:
```python
# BEFORE:
self.context = core_items + items_to_keep

# AFTER:
self.context = protected_items + items_to_keep
```

Changed to use `protected_items` (includes CORE + high importance + recent)

---

## Expected Behavior After Fix

### Context Growth Pattern

```
Turn | Phase       | Rate | Tokens Before | Tokens After | Net Growth
-----|-------------|------|---------------|--------------|------------
1    | WARMUP      | 10%  | 0             | ~4,000       | +3,600
2    | WARMUP      | 10%  | 4,000         | ~8,000       | +3,600
3    | WARMUP      | 10%  | 8,000         | ~12,000      | +3,600
4    | WARMUP      | 10%  | 12,000        | ~16,000      | +3,600
5    | WARMUP      | 10%  | 16,000        | ~20,000      | +3,600
6    | RAMP        | 15%  | 20,000        | ~23,400      | +3,400
10   | RAMP        | 33%  | 40,000        | ~42,680      | +2,680
15   | RAMP        | 60%  | 60,000        | ~61,600      | +1,600
20   | STEADY      | 60%  | 80,000        | ~81,600      | +1,600
30   | STEADY      | 60%  | 90,000        | ~91,600      | +1,600
40   | STEADY      | 60%  | 95,000        | ~96,600      | +1,600
```

**Key Properties**:
1. ✅ Context grows during warmup (not wiped)
2. ✅ Smooth transition through ramp
3. ✅ Stabilizes around 80-100K tokens
4. ✅ Agent maintains working memory throughout

### Agent Behavior Expected

**Turn 1-5 (Warmup)**:
- Agent reads problem description
- Begins exploring codebase
- **Can remember** what problem is about
- **Can remember** which files already read
- Coherent strategy developing

**Turn 6-15 (Ramp)**:
- Agent continues exploration
- Starts identifying solution approach
- Context growing but with gentle pruning
- **Still has memory** of early exploration
- Building towards solution

**Turn 16+ (Steady State)**:
- Agent implements solution
- Context stable around target
- Old/irrelevant context pruned
- Recent context always preserved
- **Continuous memory** of recent work

---

## Validation Criteria

### ✅ Fix is Working If:

1. **Context Size > 0**
   - context_size_final > 0
   - context_size_max > 0
   - NOT seeing 0 tokens after every turn

2. **Context Shows Growth**
   - Warmup phase: Increasing from 0 → ~20K
   - Ramp phase: Growing to ~60K
   - Steady phase: Stabilizing ~80-100K

3. **Debug Logs Show Phases**
   ```
   ContinuousPruner[1] WARMUP: tokens_before=0, tokens_after=4000, ...
   ContinuousPruner[5] WARMUP: tokens_before=16000, tokens_after=19600, ...
   ContinuousPruner[10] RAMP: tokens_before=40000, tokens_after=42680, ...
   ContinuousPruner[15] RAMP: tokens_before=60000, tokens_after=61600, ...
   ContinuousPruner[20] STEADY: tokens_before=80000, tokens_after=81600, ...
   ```

4. **Conversation Shows Coherence**
   - Agent remembers problem description
   - Agent tracks which files already read
   - Agent builds on previous analysis
   - No random file reading
   - Clear strategy progression

### ❌ Fix Failed If:

1. **Context Still Zero**
   - context_size = 0 throughout
   - Debug logs show tokens_after=0
   - items_in_context=0

2. **No Phase Progression**
   - All logs show same pruning rate
   - No WARMUP/RAMP/STEADY labels
   - Rate stuck at one value

3. **Conversation Still Broken**
   - Agent forgets problem between turns
   - Random file exploration
   - No coherent strategy
   - Repeats same questions

---

## Testing Status

### Test 1: Single Problem Validation (IN PROGRESS)

**Command**: `test_fixes.py` with continuous_pruning
**Started**: 2025-11-04 21:45 UTC
**Expected Runtime**: 10-15 minutes
**Expected Cost**: ~$10-15

**What We're Watching For**:
1. Context growth during warmup (turns 1-5)
2. Phase transitions in debug logs (WARMUP → RAMP → STEADY)
3. Non-zero context sizes throughout
4. Coherent conversation showing memory continuity

**Results**: PENDING

### Test 2: 2-Problem Comparison (PLANNED)

After Test 1 validates fix:
- Run 2 problems (same as before)
- Compare continuous vs discrete
- Expect: Continuous still better, but not 15x (maybe 2-3x)
- Expect: Both show coherent agent behavior

### Test 3: Longer Task Validation (PLANNED)

- Run complex 50+ turn problem
- Validate logistic growth curve
- Confirm steady state stabilization
- Check for any drift or instability

---

## Performance Expectations

### Token Usage

**OLD (Broken)**:
- ~139K tokens per problem
- **But context was empty!** (15x "efficiency" was a bug)

**NEW (Fixed)**:
- Expect: ~500-800K tokens per problem
- Continuous should use 2-3x fewer tokens than discrete
- NOT 15x - that was because it was broken

### Context Efficiency

**Target Comparison vs Discrete Baseline**:
- Discrete: Accumulates to 125K, compacts to 47K (spiky)
- Continuous: Grows to ~90K, maintains stable (smooth)

**Advantages of Continuous (When Fixed)**:
1. ✅ Smoother context evolution (no spikes)
2. ✅ Better retention (gradual vs sudden drops)
3. ✅ No threshold crossings (stays below limit)
4. ✅ More predictable token usage

**Expected Improvement**: 2-3x fewer tokens vs discrete (not 15x)

---

## Rollback Plan

If fix doesn't work:

**Option A - Increase Warmup**:
- Try warmup=10 (longer building period)
- May need more turns to establish working memory

**Option B - Lower Target Rate**:
- Try target_rate=0.50 or 0.40
- Less aggressive pruning at steady state

**Option C - Increase Recent Protection**:
- Try recent_protection=5
- Keep more recent interactions

**Option D - Disable Pruning Until Threshold**:
- Only prune after reaching 80% of target
- More like discrete but with gradual pruning

---

## References

- Research Report: `claudedocs/research_context_management_20251104.md`
- Bug Analysis: `experiments/experiment_5/BUGS_FOUND.md`
- Original Results: `experiments/experiment_5/SPRINT_5_REDUX_RESULTS.md`

---

**Status**: ✅ Code changes complete, test running
**Next**: Review test results and validate fix works
**Then**: Run full 2-problem comparison with fixed implementation
