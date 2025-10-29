# Technical Specification Summary

**Document**: TECHNICAL_SPECIFICATION.md v1.0
**Created**: 2025-10-29
**Purpose**: Quick reference guide to the full technical specification

---

## At a Glance

**Research Question**: Can continuous importance-based pruning maintain AI agent context better than discrete compaction?

**Approach**:
- **Phase I**: Prove concept works and is better than baseline
- **Phase II**: Production implementation (deferred)

**Key Innovation**: Remove ~110% of added content after *every* interaction (adaptive rate) instead of waiting for catastrophic compaction.

---

## Critical Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| CORE Budget | ≤25% of target | Immutable critical decisions |
| Adaptive Pruning Rate | 0.90-1.10 | Self-regulating equilibrium |
| Target Utilization | 20-40% | Steady-state range |
| Token Estimation Error | ±20% (Phase I) | Acceptable for validation |

---

## Four Experiments

### Experiment 1: Stability (UPDATED)
- **Goal**: Prove no linear growth, steady-state convergence
- **Key Metrics**: Linear growth coefficient, oscillation σ, max utilization
- **Status**: Exists, needs adaptive rate updates

### Experiment 2: Convergence (NEW)
- **Goal**: Adaptive rate causes self-regulation
- **Key Metrics**: Convergence time from varied initial states
- **Status**: To be implemented

### Experiment 3: Information Preservation (NEW)
- **Goal**: Better CORE decision recall than discrete compaction
- **Key Metrics**: Recall accuracy, relative improvement
- **Status**: To be implemented

### Experiment 4: Code Quality (NEW, PRIMARY)
- **Goal**: Equal/better code generation with continuous pruning
- **Key Metrics**: Task completion, spec adherence, code quality
- **Benchmark**: SWE-bench-Lite Extended (50 tasks)
- **Status**: To be implemented, **P0 critical**

---

## Success Criteria (Phase I)

**Must achieve all**:
- ✅ Context stability: No linear growth, σ < 15% of target
- ✅ Information preservation: >90% CORE recall, ≥25% better than baseline
- ✅ Code quality: ≥90% of discrete baseline task completion rate
- ✅ System integrity: CORE budget never violated, adaptive rate functions correctly

---

## Implementation Priorities

### P0 (Blocking for Phase I)
1. Adaptive pruning rate implementation
2. CORE budget enforcement
3. Rule-based discrete compaction baseline
4. Experiment 4: Code quality benchmark
5. Experiment 1: Stability updates

### P1 (Important)
6. Experiment 2: Convergence
7. Experiment 3: Information preservation
8. Unprunable state fallback
9. Token estimation accuracy measurement
10. Comprehensive metrics collection

### P2 (Enhancements)
- Qualitative assessment tooling
- Extended task sets
- Visualization and reporting
- Performance profiling

### P3 (Phase II)
- LLM-based compaction baseline
- WARM/COLD tier implementation
- MCP server integration
- Adversarial testing

---

## Key Decisions Made

1. **Adaptive Rate (Not Fixed 110%)**: Enables self-regulation, handles varied initial conditions
2. **Rule-Based Baseline (Phase I)**: Fast, deterministic, "good enough" for concept validation
3. **SWE-bench-Lite Extended**: Best available benchmark for context-intensive coding tasks
4. **25% CORE Budget**: Empirically sufficient, validated in Experiment 3
5. **O(n²) Acceptable**: Not optimized, but fast enough for validation scale

---

## Open Questions

**Need resolution before implementation**:
- Q1: Optimal target utilization? (Currently 20-40%)
- Q2: Recency decay half-life? (Currently 10 interactions)
- Q5: SWE-bench task selection methodology?
- Q6: Conversation script design for extended tasks?

**Defer to empirical validation**:
- Q3: Is 25% CORE budget sufficient? (Test in Exp 3)
- Q4: Are pruning rate bounds appropriate? (Test in Exp 2)

---

## Quick Reference: Algorithm

```python
# After each interaction:
1. Add new content to context
2. Calculate importance scores for ALL items
3. pruning_rate = calculate_adaptive_rate(utilization, core_usage)
4. target_prune = tokens_added * pruning_rate  # 0.90-1.10 range
5. Remove lowest-scored items (exclude CORE tier)
6. Result: Context oscillates in steady state
```

**Importance Scoring**:
- 40% Recency (exponential decay, half-life=10)
- 20% Access frequency
- 30% Item type weight
- 10% Manual pins
- CORE tier always scores 1.0

---

## Document Structure

1. **Executive Summary** - Problem, hypothesis, scope
2. **Background** - Why this matters for AI coding agents
3. **System Architecture** - 4-tier system, adaptive algorithm, CORE budget
4. **Baseline** - Discrete compaction simulator (rule-based for Phase I)
5. **Evaluation** - 4-dimensional scorecard, benchmarks, metrics
6. **Experiments** - 4 experiments with clear acceptance criteria
7. **Priorities** - P0/P1/P2/P3 breakdown
8. **Success Criteria** - Quantitative and qualitative acceptance
9. **Open Questions** - Items needing clarification
10. **Appendices** - Benchmark research, design rationale, trade-offs

---

## Next Steps

1. **Review**: Stakeholder approval of specification
2. **Implement**: Execute P0 items
3. **Validate**: Run all four experiments
4. **Analyze**: Compare continuous vs. discrete baseline
5. **Decide**: Phase II go/no-go based on results

---

**Full Specification**: `/home/frankbria/projects/context-pruning-lab/TECHNICAL_SPECIFICATION.md`
