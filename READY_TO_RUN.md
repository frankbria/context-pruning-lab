# Ready to Run: Sprint 5 Redux Validation

**Status**: ✅ All infrastructure complete
**Date**: 2025-11-04
**Next**: Run validation experiments

---

## What We Fixed

### Sprint 5 Problem
```
Configuration: 40K context, 32K threshold
Tasks: Simple puzzles (reverse_string, fibonacci)
Result: 0/20 tasks triggered compaction
Conclusion: Invalid - tested nothing
```

### Sprint 5 Redux Solution
```
Configuration: 156K context, 125K threshold
Tasks: Real SWE-bench (psf/requests, sympy, django)
Result: Expected 2-4 compactions per task
Conclusion: Valid - tests actual hypothesis
```

---

## What's Built

1. ✅ **Configuration Fixed** - 156K context, 125K threshold
2. ✅ **Real SWE-bench Integration** - 300 problems loaded
3. ✅ **Codebase Tools** - Read files from cloned repos
4. ✅ **Experiment Runner** - Full automation
5. ✅ **Validation Tests** - All infrastructure working

---

## How to Run

### Quick Test (1 problem, ~10 min, ~$1-2)
```bash
# Edit experiment_runner.py to use n_problems=1
uv run python experiments/experiment_5/experiment_runner.py
```

### Validation Run (3 problems, ~30 min, ~$5-10)
```bash
# Default: 3 problems, discrete_baseline only
uv run python experiments/experiment_5/experiment_runner.py
```

### Full Experiment (20 problems, ~4 hours, ~$30-50)
```bash
# Edit experiment_runner.py:
# - n_problems=20
# - strategies=["continuous_pruning", "discrete_baseline"]
uv run python experiments/experiment_5/experiment_runner.py
```

---

## What to Look For

### Success Criteria

**Per Problem (Discrete Baseline)**:
- ✅ Context grows to 125K+ tokens
- ✅ Compaction triggers 2-3 times
- ✅ Metrics recorded correctly
- ✅ Can measure quality before/after compaction

**Example Output**:
```
[1/3] psf__requests-1963
✓ SUCCESS
  Turns: 18
  Tokens: 142,530
  Context max: 138,450
  Compactions: 3
  ✓ COMPACTION TRIGGERED at 126,340 tokens
  Files read: 12
```

### If Compaction Doesn't Trigger

**Problem**: Context not reaching 125K
**Solutions**:
1. Increase max_turns (currently 20, try 30-50)
2. Make agent read more files (currently 5, try 10-15)
3. Add more conversation turns
4. Check logs - is agent reading files?

### If It Works

**You'll see**:
- Compaction triggers at ~125K tokens ✅
- Context drops to ~38K after compaction ✅
- Can track compaction events ✅
- Have data for degradation analysis ✅

**This means**: We're finally testing the actual research hypothesis!

---

## Expected Results

### Problem: psf__requests-1963

**Discrete Baseline**:
```
Turn 1: 5K tokens (problem description)
Turn 3: 35K tokens (read 3 files)
Turn 6: 78K tokens (read 3 more files)
Turn 9: 118K tokens (agent analysis)
Turn 11: 126K → COMPACTION #1 → 38K
Turn 14: 82K tokens (read 2 more files)
Turn 17: 127K → COMPACTION #2 → 39K
Turn 20: 95K tokens (final)

Result: 2 compactions, can measure degradation
```

**Continuous Pruning** (when we add it):
```
Turn 1: 5K tokens
Turn 3: 32K (pruned after each turn)
Turn 6: 41K (steady state)
Turn 9: 38K (oscillating)
Turn 11: 44K (no compaction)
Turn 14: 42K (maintained)
Turn 17: 39K (stable)
Turn 20: 43K (steady)

Result: 0 compactions, maintains quality
```

---

## Files Generated

### During Run
```
results/experiment_5/
└── swe_bench_exp_20251104_HHMMSS.json

Contains:
- Problem metadata
- Success/failure status
- Token counts
- Context sizes
- Compaction events
- File reading stats
- Timing data
```

### Cloned Repos (First Run)
```
data/swe_bench/codebases/
├── psf__requests-1963/     (~30MB)
├── sympy__sympy-11400/     (~150MB)
└── django__django-10914/   (~80MB)

Note: Subsequent runs reuse these
```

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### "No module named 'datasets'"
```bash
uv pip install datasets gitpython
```

### Cloning takes too long
- First run: 5-10 min to clone repos
- Subsequent runs: < 1 min (reuses clones)
- Be patient on first run!

### Agent not reading files
- Check: Is `files_to_read` list populated?
- Check: Do files exist in cloned repo?
- Solution: Verify with test_validation.py first

---

## Cost Estimates

### Per Problem
- API calls: ~15-30 turns
- Tokens per turn: ~3K-8K
- Total: ~50K-150K tokens
- Cost: ~$1-5 per problem

### Full Experiment (20 problems)
- Total tokens: ~1M-3M
- Cost: ~$30-100
- Time: 3-6 hours
- Worth it: Getting real validation data

---

## Next Session Plan

### Session 1 (Today/Tomorrow - 1 hour)
1. Run quick test (1 problem)
2. Verify compaction triggers
3. Check output format
4. Fix any bugs

### Session 2 (Following Day - 2 hours)
1. Run validation (3 problems)
2. Confirm metrics correct
3. Analyze compaction history
4. Verify degradation measurable

### Session 3 (Weekend - 4 hours)
1. Add continuous_pruning strategy
2. Run 20 problems both strategies
3. Analyze degradation comparison
4. Write up results

---

## Success Looks Like

✅ **Compaction triggers** at ~125K tokens (not 0 like Sprint 5)
✅ **2-3 compactions per problem** (baseline)
✅ **Metrics recorded** properly
✅ **Can measure degradation** across compaction cycles
✅ **Real data** from real coding problems

**Then we can finally answer**: Does continuous pruning prevent degradation better than discrete compaction?

---

## Command to Run

```bash
# Validation run (recommended first)
uv run python experiments/experiment_5/experiment_runner.py

# Check results
ls -lah results/experiment_5/

# Analyze output
cat results/experiment_5/swe_bench_exp_*.json | jq '.results.discrete_baseline[0]'
```

---

**Status**: 🚀 Ready to execute
**All systems**: ✅ GO
**Research validity**: ✅ Finally testing the right thing

Run it and let's get real data!
