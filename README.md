# Context Pruning Lab

**Experimental validation of continuous context pruning for LLM agents**

## The Problem

Traditional LLM conversation management waits until context is ~80% full, then performs batch compaction. This causes:
1. **Degradation**: Agent becomes "dumb" after 2-3 compaction cycles
2. **Loss of rationale**: WHY decisions were made gets lost
3. **Jarring resets**: Conversation "restarts" with compressed context
4. **Linear growth**: Context grows linearly until catastrophic failure

## The Solution: Continuous Pruning

Instead of waiting for crisis, prune **after every interaction**:

```
After each interaction:
1. Add new content (user message + agent response)
2. Score ALL context items for importance
3. Remove ~110% of what was just added (lowest-scored items)
4. Result: Context oscillates around target size, never explodes
```

**Benefits**:
- ✅ No degradation (gradual, not lossy compression)
- ✅ Critical info preserved (CORE tier never pruned)
- ✅ Steady state (context stays 20-30% full indefinitely)
- ✅ Smooth operation (no jarring resets)

## Project Structure

```
context-pruning-lab/
├── README.md                           # This file
├── requirements.txt                    # Minimal dependencies
├── pruner.py                          # Core algorithm
├── test_pruner.py                     # Unit tests
├── demo.py                            # Interactive demo
└── experiments/
    ├── experiment_1_linear_growth.py  # Prove no linear growth
    ├── experiment_2_oscillation.py    # Measure steady state
    └── experiment_3_degradation.py    # Compare vs batch compaction
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest test_pruner.py -v

# Run interactive demo
python demo.py

# Run experiments
python experiments/experiment_1_linear_growth.py
```

## Algorithm Overview

### Four-Tier Architecture

```
CORE TIER (Immutable, never pruned)
├─ Critical decisions with rationale
├─ Architectural choices
├─ Security constraints
└─ Project requirements
    ↓
HOT TIER (Active context, continuous pruning)
├─ Recent messages
├─ Current task
└─ Active files
    ↓
WARM TIER (Queryable archive)
├─ Related context
└─ Load on-demand
    ↓
COLD TIER (Long-term storage)
└─ Historical data
```

### Importance Scoring

Each context item scored 0.0-1.0 based on:
- **Recency** (40%): Exponential decay, half-life ~10 interactions
- **Access frequency** (20%): How often referenced
- **Item type** (30%): Some types more important (decisions > logs)
- **Manual pins** (10%): User/agent marked as critical

### Pruning Strategy

```python
def prune_after_interaction(new_user_msg, new_agent_response):
    # 1. Add new content
    tokens_added = add_to_context(new_user_msg, new_agent_response)

    # 2. Score all items
    for item in context:
        item.importance = calculate_importance(item)

    # 3. Remove 110% of what was added (target: net reduction)
    target_remove = tokens_added * 1.10
    remove_lowest_scored(target_remove)

    # Result: Context shrinks slightly each iteration
```

## Experiments

### Experiment 1: Linear Growth Prevention

**Hypothesis**: Context will NOT grow linearly like traditional chat.

**Test**: 1000 interactions, measure token count each iteration.

**Expected**: Oscillation between 20-30K tokens, never exceeding 40K.

### Experiment 2: Steady State Oscillation

**Hypothesis**: Context stabilizes in steady state after ~10 interactions.

**Test**: Measure variance in token count over 100 interactions.

**Expected**: Standard deviation < 3K tokens after stabilization.

### Experiment 3: Degradation Test

**Hypothesis**: Agent retains important information better than batch compaction.

**Test**: After 100 interactions, query agent about early decisions.

**Expected**: Continuous pruning recalls 90%+ of CORE decisions vs. 60% for batch.

## Integration with Claude Code

This algorithm will be integrated into the Codeframe Plugin Marketplace as a `before_compact` hook:

```javascript
// .claude/hooks/before_compact.js
export default async function beforeCompact(context) {
    const result = await callTool('mcp__codeframe__continuous_prune', {
        current_context: context,
        target_reduction: 0.30
    });
    return result.pruned_context;
}
```

See: [codeframe-claude-plugin](https://github.com/frankbria/codeframe-claude-plugin)

## Contributing

This is an experimental project. Contributions welcome:
- Algorithm improvements
- Additional experiments
- Performance optimizations
- Integration with other LLM frameworks

## License

MIT License - See LICENSE file

---

**Status**: Experimental - Algorithm validation in progress
**Last Updated**: 2025-10-29
