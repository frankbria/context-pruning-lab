# Sprint 5 Redux: Strategy Comparison Ready

**Status**: Experiment Running
**Date**: 2025-11-04
**Progress**: 25% complete (40/160+ API calls)

---

## What's Running

Testing **discrete_baseline** vs **continuous_pruning** on 2 SWE-bench problems:

```python
Configuration:
- Problems: 2 (from SWE-bench Lite)
- Strategies: discrete_baseline, continuous_pruning
- Context target: 156,250 tokens
- Compaction threshold: 125,000 tokens (80%)
- Files per problem: 40 (full content)
- Max turns: 50
- Expected runtime: 60-90 minutes
- Expected cost: $60-90
```

---

## Progress Update

### Completed So Far
✅ Infrastructure validated (Sprint 5 Redux Phase 1)
✅ Compaction triggered successfully (134,123 → 45,775 tokens)
✅ Weighted scorecard system implemented
✅ Documentation complete

### Currently Running
🔄 Problem 1 with discrete_baseline (~80% complete)
⏳ Problem 1 with continuous_pruning (pending)
⏳ Problem 2 with discrete_baseline (pending)
⏳ Problem 2 with continuous_pruning (pending)

---

## When Experiment Completes

### Step 1: Find Results
```bash
# Results will be saved to:
results/experiment_5/swe_bench_exp_TIMESTAMP.json

# Find latest:
ls -lt results/experiment_5/swe_bench_exp_*.json | head -1
```

### Step 2: Run Weighted Scorecard
```bash
# Score and compare strategies
python experiments/experiment_5/scorer.py \
  results/experiment_5/swe_bench_exp_TIMESTAMP.json \
  results/experiment_5/scores_TIMESTAMP.json
```

### Step 3: Interpret Results

The scorecard will output:

```
WEIGHTED SCORECARD COMPARISON
════════════════════════════════════════════════════════════════════════════════

STRATEGY_NAME
────────────────────────────────────────────────────────────────────────────────
  Total Score: XXX.X / 1000

  Raw Metrics:
    Success Rate: X%
    Avg Tokens:   X,XXX,XXX
    Avg Turns:    XX.X
    Avg Compactions: X.X
    Avg Files Read:  XX.X

  Normalized Scores (0-1):
    Correctness:  X.XXX
    Tokens Efficiency: X.XXX
    Turns Efficiency:  X.XXX
    Compaction:   X.XXX
    Files:        X.XXX

  Weighted Contributions:
    Correctness    : X.XXXX (50% weight)
    Tokens         : X.XXXX (25% weight)
    Turns          : X.XXXX (15% weight)
    Compaction     : X.XXXX (5% weight)
    Files          : X.XXXX (5% weight)

════════════════════════════════════════════════════════════════════════════════
WINNER: [STRATEGY_NAME]
Score: XXX.X / 1000
Margin: +XX.X points
════════════════════════════════════════════════════════════════════════════════
```

---

## Expected Outcomes

### Scenario A: Continuous Pruning Wins
**If continuous_pruning scores higher:**

✅ **Validates hypothesis** - Continuous pruning prevents degradation
✅ Lower token usage (more efficient context management)
✅ Maintains quality across all turns
✅ No compaction events (perfect pruning)

**Next steps:**
1. Scale to 20 problems for statistical significance
2. Analyze per-turn quality degradation patterns
3. Measure degradation delta between strategies
4. Publish findings

### Scenario B: Discrete Baseline Wins
**If discrete_baseline scores higher:**

⚠️ **Hypothesis challenged** - Need to investigate why

Possible reasons:
- Continuous pruning too aggressive (losing important context)
- More turns needed (slower but not necessarily worse)
- Compaction events indicate pruning strategy failing
- Lower correctness rate (solution quality issues)

**Next steps:**
1. Analyze where continuous pruning failed
2. Tune pruning aggressiveness
3. Check which context items were pruned incorrectly
4. Re-test with adjusted parameters

### Scenario C: Very Close (< 20 points)
**If scores within 20 points:**

🤔 **Inconclusive** - Need more data

**Next steps:**
1. Run on 10-20 more problems
2. Statistical significance testing
3. Look for patterns in which strategy wins when
4. Consider hybrid approach

---

## Metrics to Watch

### Primary (Correctness - 50% weight)
- **Success rate**: Did both strategies solve the problems?
- **Critical**: If one strategy has significantly lower success, it loses

### Secondary (Efficiency - 40% weight)
- **Token usage**: Which used fewer tokens? (Lower = better, saves cost)
- **Turn count**: Which completed faster? (Lower = better, saves time)

### Tertiary (Context Management - 10% weight)
- **Compaction events**:
  - Discrete baseline: Should have 2-4 (optimal)
  - Continuous pruning: Should have 0 (perfect pruning)
- **Files read**: Similar for both (just efficiency metric)

---

## What We're Testing

### Research Question
**Does continuous pruning prevent quality degradation better than discrete compaction?**

### Hypothesis
After 2-3 discrete compaction cycles, solution quality degrades because:
1. Important context gets discarded
2. Agent loses track of earlier decisions
3. Coherence decreases across compaction boundaries

Continuous pruning should prevent this by:
1. Gradually removing less important items
2. Maintaining recent context always
3. Avoiding sudden large context losses

### How We'll Know
Compare weighted scores focusing on:
- **Correctness gap**: Does one strategy solve more problems?
- **Efficiency gap**: Does one use significantly fewer resources?
- **Compaction behavior**: Does continuous pruning prevent discrete compactions?

---

## Results Storage

### Experiment Results
```json
{
  "timestamp": "YYYYMMDD_HHMMSS",
  "metadata": {
    "max_turns": 50,
    "config": {
      "target_context_size": 156250,
      "compaction_threshold": 125000
    }
  },
  "results": {
    "discrete_baseline": [
      {
        "instance_id": "problem-1",
        "success": true,
        "turns": 41,
        "total_tokens": 3318261,
        "context_size_max": 134123,
        "compaction_events": 1,
        "compaction_triggered": true,
        "tokens_at_first_compaction": 134123,
        "files_read": 40,
        ...
      },
      ...
    ],
    "continuous_pruning": [...]
  }
}
```

### Score Results
```json
{
  "discrete_baseline": {
    "total_score": 745.2,
    "raw_metrics": {...},
    "normalized_scores": {...},
    "breakdown": {...}
  },
  "continuous_pruning": {
    "total_score": 823.5,
    "raw_metrics": {...},
    "normalized_scores": {...},
    "breakdown": {...}
  }
}
```

---

## Files Created This Session

### Implementation
- `experiments/experiment_5/scorer.py` - Weighted scorecard system
- `experiments/experiment_5/SCORER_USAGE.md` - Complete documentation

### Modified
- `experiments/experiment_5/experiment_runner.py` - Now tests both strategies
  - Line 412-414: Changed to test 2 problems with both strategies

### Documentation
- `COMPARISON_READY.md` (this file) - Experiment summary

---

## Timeline

### Completed (2025-11-04 AM)
- ✅ Fixed Sprint 5 configuration (32K → 156K context)
- ✅ Successfully triggered compaction (3 iterations)
- ✅ Validated infrastructure with real SWE-bench
- ✅ Documented breakthrough (EXPERIMENT_5_SUCCESS.md)

### In Progress (2025-11-04 PM)
- 🔄 Running 2-problem comparison experiment (25% complete)
- ⏳ Expected completion: ~60-75 minutes from start

### Next (After Completion)
- ⏳ Run weighted scorecard analysis
- ⏳ Interpret results
- ⏳ Decide on next steps (scale up or tune)

---

## Cost & Time

### Current Experiment
- **Problems**: 2
- **Strategies**: 2
- **Total runs**: 4
- **Expected tokens**: 8M-12M
- **Expected time**: 60-90 minutes
- **Expected cost**: $60-90

### If We Scale to Full Validation
- **Problems**: 20
- **Total runs**: 40
- **Expected tokens**: 80M-120M
- **Expected time**: 10-15 hours
- **Expected cost**: $600-900

**Worth it?** YES - This validates the core research hypothesis with real data.

---

## Key Success Criteria

### Minimum Viable Success
✅ Both strategies complete without errors
✅ Discrete baseline triggers 2+ compactions per problem
✅ Continuous pruning triggers <1 compaction per problem
✅ Weighted scores clearly differentiate strategies

### Ideal Success
✅ Clear winner (>50 point margin)
✅ Winner has higher correctness
✅ Winner uses fewer tokens
✅ Results are consistent across both problems
✅ Compaction behavior matches strategy expectations

---

## After Results

### Immediate Actions
1. ✅ Score with weighted scorecard
2. ✅ Analyze winner and margin
3. ✅ Check for consistency across problems
4. ✅ Identify any anomalies

### Documentation
1. ✅ Update SPRINT_5_REDUX_PLAN.md with results
2. ✅ Create SPRINT_5_REDUX_RESULTS.md
3. ✅ Document decision on next steps

### Code Changes
1. ✅ Commit scorer implementation
2. ✅ Commit experiment modifications
3. ✅ Push to GitHub

### Next Sprint Planning
Based on results:
- **If hypothesis validated**: Plan 20-problem validation
- **If hypothesis challenged**: Plan tuning experiments
- **If inconclusive**: Plan larger sample size

---

**Status**: ⏳ Waiting for experiment completion (~35-50 minutes remaining)
**Next Action**: Score results when complete
**Estimated Completion**: ~17:00-17:30 UTC
