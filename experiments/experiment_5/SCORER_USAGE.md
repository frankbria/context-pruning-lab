# Weighted Scorecard System

## Overview

The weighted scorecard compares context management strategies using a normalized scoring system (0-1000). Each metric is weighted by importance and normalized to allow fair comparison.

## Weights

| Metric | Weight | Priority | Why? |
|--------|--------|----------|------|
| **Correctness** | 50% | Highest | Does the solution work? Most important. |
| **Tokens Efficiency** | 25% | Second | Lower token usage = lower cost |
| **Turns Efficiency** | 15% | Third | Fewer turns = faster completion |
| **Compaction Management** | 5% | Fourth | Strategy-specific context handling |
| **Files Efficiency** | 5% | Fifth | Efficient code exploration |

## Normalization

All metrics normalized to 0-1 scale (higher = better):

### Correctness (0-1)
- Direct: success_rate
- 1.0 = perfect success, 0.0 = total failure

### Efficiency Metrics (tokens, turns, files)
- Formula: `score = target / (actual + target)`
- actual < target → score > 0.5 (better than baseline)
- actual = target → score = 0.5 (baseline)
- actual > target → score < 0.5 (worse than baseline)

### Compaction Score (strategy-dependent)

**Discrete Baseline**:
- Target: 2-4 compactions (sweet spot)
- Peak score at 3 compactions
- Penalty for too few (<2) or too many (>4)

**Continuous Pruning**:
- Target: 0 compactions (perfect)
- Penalty for any compactions (strategy failing)

## Usage

### As a module:
```python
from scorer import WeightedScorer

# Score strategies
scorer = WeightedScorer()
scores = scorer.compare_strategies(results_by_strategy)

# Print comparison
scorer.print_comparison(scores, show_breakdown=True)
```

### From command line:
```bash
# Score and print comparison
python scorer.py results/experiment_5/swe_bench_exp_TIMESTAMP.json

# Score and save to file
python scorer.py results.json scores_output.json
```

## Output Format

### Console Output
```
WEIGHTED SCORECARD COMPARISON
════════════════════════════════════════════════════════════════════════════════

DISCRETE_BASELINE
────────────────────────────────────────────────────────────────────────────────
  Total Score: 745.2 / 1000

  Raw Metrics (averaged across 2 problems):
    Success Rate: 100.0%
    Avg Tokens:   2,500,000
    Avg Turns:    45.0
    Avg Compactions: 2.5
    Avg Files Read:  40.0

  Normalized Scores (0-1, higher = better):
    Correctness:  1.000
    Tokens Efficiency: 0.444
    Turns Efficiency:  0.471
    Compaction:   0.875
    Files:        0.500

  Weighted Contributions (weights × scores):
    Correctness    : 0.5000
    Tokens         : 0.1111
    Turns          : 0.0706
    Compaction     : 0.0438
    Files          : 0.0250

════════════════════════════════════════════════════════════════════════════════
WINNER: DISCRETE_BASELINE
Score: 745.2 / 1000
Margin: +42.3 points over runner-up
════════════════════════════════════════════════════════════════════════════════
```

### JSON Output
```json
{
  "discrete_baseline": {
    "total_score": 745.2,
    "raw_metrics": {
      "success_rate": 1.0,
      "avg_tokens": 2500000,
      "avg_turns": 45.0,
      "avg_compactions": 2.5,
      "avg_files": 40.0
    },
    "normalized_scores": {
      "correctness": 1.000,
      "tokens": 0.444,
      "turns": 0.471,
      "compaction": 0.875,
      "files": 0.500
    },
    "breakdown": {
      "correctness": 0.5000,
      "tokens": 0.1111,
      "turns": 0.0706,
      "compaction": 0.0438,
      "files": 0.0250
    }
  }
}
```

## Configuration

Adjust weights and targets in `WeightedScoreConfig`:

```python
config = WeightedScoreConfig(
    # Weights (must sum to 1.0)
    correctness_weight=0.50,
    tokens_efficiency_weight=0.25,
    turns_efficiency_weight=0.15,
    compaction_weight=0.05,
    files_weight=0.05,

    # Normalization targets
    target_tokens=2_000_000,  # 2M tokens = baseline
    target_turns=40,          # 40 turns = baseline
    target_files=40           # 40 files = baseline
)

scorer = WeightedScorer(config)
```

## Interpretation

### Total Score (0-1000)
- **900-1000**: Excellent - near perfect on all metrics
- **800-900**: Very good - strong performance
- **700-800**: Good - solid performance with room for improvement
- **600-700**: Acceptable - meets baseline but has issues
- **<600**: Poor - significant problems

### Comparing Strategies
- **Margin >100**: Clear winner
- **Margin 50-100**: Significant advantage
- **Margin 20-50**: Moderate advantage
- **Margin <20**: Very close, within noise

## Examples

### Scenario 1: Continuous Pruning Wins
```
CONTINUOUS_PRUNING: 823.5 / 1000
  - High correctness (100%)
  - Lower tokens (2M vs 3M)
  - More turns (50 vs 45) but acceptable
  - No compactions (perfect for strategy)

DISCRETE_BASELINE: 745.2 / 1000
  - High correctness (100%)
  - Higher tokens (3M)
  - Fewer turns (45)
  - 3 compactions (good for strategy)

WINNER: CONTINUOUS_PRUNING (+78.3)
Reason: Token efficiency outweighs turn difference
```

### Scenario 2: Discrete Baseline Wins
```
DISCRETE_BASELINE: 812.4 / 1000
  - High correctness (100%)
  - Moderate tokens (2.5M)
  - Moderate turns (45)
  - 3 compactions (perfect for strategy)

CONTINUOUS_PRUNING: 687.1 / 1000
  - Lower correctness (80%) ← key issue
  - Lower tokens (2M)
  - Many turns (60)
  - 2 compactions (strategy failing)

WINNER: DISCRETE_BASELINE (+125.3)
Reason: Correctness deficit dominates (50% weight)
```

## SWE-bench Integration

When experiment completes, run:
```bash
# Find latest results
ls -lt results/experiment_5/swe_bench_exp_*.json | head -1

# Score them
python experiments/experiment_5/scorer.py \
  results/experiment_5/swe_bench_exp_TIMESTAMP.json \
  results/experiment_5/scores_TIMESTAMP.json
```

## Future Enhancements

1. **Time-series scoring**: Track quality degradation across turns
2. **Per-turn snapshots**: Score at each compaction event
3. **LLM-as-judge**: Add code quality assessment
4. **Cost metrics**: Include API cost in scoring
5. **Multi-problem aggregation**: Statistical significance testing
