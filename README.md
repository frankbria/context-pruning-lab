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

## Documentation

📘 **[Technical Specification](TECHNICAL_SPECIFICATION.md)** - Comprehensive Phase I research specification
📄 **[Specification Summary](SPEC_SUMMARY.md)** - Quick reference guide

## Project Structure

```
context-pruning-lab/
├── README.md                           # This file
├── TECHNICAL_SPECIFICATION.md          # Formal research specification
├── SPEC_SUMMARY.md                     # Quick reference guide
├── requirements.txt                    # Minimal dependencies
├── pruner.py                          # Core algorithm
├── test_pruner.py                     # Unit tests
├── demo.py                            # Interactive demo
└── experiments/
    ├── experiment_1_linear_growth.py  # Stability validation
    ├── experiment_2_convergence.py    # Adaptive rate testing (to be implemented)
    ├── experiment_3_preservation.py   # Information preservation (to be implemented)
    └── experiment_4_code_quality.py   # Code generation benchmark (to be implemented)
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

### Adaptive Pruning Strategy

```python
def prune_after_interaction(new_user_msg, new_agent_response):
    # 1. Add new content
    tokens_added = add_to_context(new_user_msg, new_agent_response)

    # 2. Score all items
    for item in context:
        item.importance = calculate_importance(item)

    # 3. Calculate adaptive pruning rate (90-110% based on utilization)
    pruning_rate = calculate_adaptive_rate(current_utilization, core_usage)
    target_remove = tokens_added * pruning_rate

    # 4. Remove lowest-scored items (excluding CORE tier)
    remove_lowest_scored(target_remove, exclude_core=True)

    # Result: Context self-regulates to steady state
```

**Key Features**:
- **Adaptive Rate**: Adjusts from 90-110% based on context utilization
- **CORE Budget**: Protected tier never exceeds 25% of target capacity
- **Multi-Factor Scoring**: Combines recency, access frequency, type, and manual pins

## Research Approach

**Phase I: Concept Validation** (Current)
- Prove continuous pruning is functional and superior to discrete compaction
- Run four validation experiments (see Technical Specification)
- Benchmark against rule-based discrete compaction simulator

**Phase II: Production Implementation** (Future)
- MCP server integration with Claude Code
- Full WARM/COLD tier implementation
- LLM-based baseline comparison
- Real-world user testing

## Experiments

**See [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) for complete experimental design.**

### Experiment 1: Stability Validation
**Status**: Implemented, needs adaptive rate updates
**Goal**: Prove no linear growth, verify steady-state convergence

### Experiment 2: Convergence Testing
**Status**: To be implemented
**Goal**: Validate adaptive pruning rate self-regulates from varied initial states

### Experiment 3: Information Preservation
**Status**: To be implemented
**Goal**: Demonstrate >90% CORE decision recall vs. <70% for discrete baseline

### Experiment 4: Code Quality Benchmark (PRIMARY)
**Status**: To be implemented, **P0 critical**
**Goal**: Equal or better code generation on SWE-bench-Lite Extended tasks
**Benchmark**: 50 extended multi-turn coding tasks

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
