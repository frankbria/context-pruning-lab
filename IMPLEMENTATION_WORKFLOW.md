# Context Pruning Lab: Sprint-Based Implementation Workflow

**Project Name:** Context Pruning Lab - Phase I Concept Validation
**Version:** 1.0
**Date:** 2025-10-29
**Project Duration:** 12 weeks (6 sprints × 2 weeks)
**Team Size:** 1 developer (research engineer)
**Methodology:** Agile with research-focused validation gates

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Sprint Overview](#sprint-overview)
3. [Detailed Sprint Breakdown](#detailed-sprint-breakdown)
4. [Dependency Map](#dependency-map)
5. [Resource Requirements](#resource-requirements)
6. [Testing Strategy](#testing-strategy)
7. [Milestone Schedule](#milestone-schedule)
8. [Risk Management](#risk-management)
9. [Success Metrics](#success-metrics)
10. [Appendix: Gantt Chart](#appendix-gantt-chart)

---

## Executive Summary

### Project Overview

The Context Pruning Lab project aims to validate a novel continuous context pruning approach for AI coding agents. Traditional discrete compaction strategies cause progressive degradation in agent performance. This research proposes continuous importance-based pruning after every interaction as a superior alternative.

**Research Hypothesis:** Continuous pruning can maintain context more effectively than discrete compaction, enabling sustained high-quality code generation over extended development sessions.

### Timeline

- **Start Date:** Week 1, Day 1 (Sprint 1)
- **End Date:** Week 12, Day 5 (Sprint 6)
- **Total Duration:** 12 weeks
- **Sprint Duration:** 2 weeks each
- **Number of Sprints:** 6

### Key Deliverables

1. **Adaptive Pruning Algorithm** with CORE budget enforcement (Sprint 1-2)
2. **Discrete Compaction Baseline** simulator (Sprint 2)
3. **SWE-bench Extended Infrastructure** for code quality benchmarking (Sprint 3-4)
4. **Four Validation Experiments** with comprehensive metrics (Sprint 1-5)
5. **Technical Research Report** with comparative analysis (Sprint 6)
6. **Open-Source Repository** with reproducible experiments (Sprint 6)

### Critical Path

```
Foundation (Sprints 1-2) → Primary Experiment Infrastructure (Sprint 3)
→ Code Quality Validation (Sprint 4) → Additional Experiments (Sprint 5)
→ Analysis & Reporting (Sprint 6)
```

### Success Criteria

**Phase I is successful if:**
- ✅ Context maintains steady state with zero linear growth
- ✅ Information preservation exceeds discrete baseline by ≥25%
- ✅ Code generation quality equals or exceeds discrete baseline
- ✅ All acceptance criteria met across four experiments

---

## Sprint Overview

### Sprint Timeline

| Sprint | Week | Duration | Focus Area | Key Deliverable | Priority |
|--------|------|----------|------------|-----------------|----------|
| **Sprint 1** | 1-2 | 2 weeks | Foundation - Adaptive Pruning | `calculate_adaptive_rate()` implementation | P0 |
| **Sprint 2** | 3-4 | 2 weeks | Foundation - Baseline & CORE Budget | `DiscreteCompactionBaseline` + `CoreBudgetEnforcer` | P0 |
| **Sprint 3** | 5-6 | 2 weeks | Experiment 4 Infrastructure | SWE-bench-Lite Extended task loader | P0 |
| **Sprint 4** | 7-8 | 2 weeks | Primary Validation | Code quality experiment execution | P0 |
| **Sprint 5** | 9-10 | 2 weeks | Additional Experiments | Experiments 2 & 3 + comprehensive metrics | P1 |
| **Sprint 6** | 11-12 | 2 weeks | Analysis & Reporting | Technical report + repository finalization | P1 |

### Resource Allocation by Sprint

```
Sprint 1-2: 100% Core Algorithm Development
Sprint 3-4: 80% Experiment Infrastructure, 20% Integration
Sprint 5:   60% Experiments, 40% Analysis
Sprint 6:   20% Final Validation, 80% Documentation/Reporting
```

### Velocity Planning

**Estimated Velocity:** 40 hours per sprint (single developer, research-focused)

- **Sprint 1-2:** 35-40 hours (implementation-heavy)
- **Sprint 3-4:** 40-45 hours (infrastructure + experiment setup)
- **Sprint 5:** 35-40 hours (experiment execution + analysis)
- **Sprint 6:** 30-35 hours (reporting + documentation)

---

## Detailed Sprint Breakdown

## Sprint 1: Foundation - Adaptive Pruning Rate

**Duration:** Week 1-2
**Goal:** Implement and validate the adaptive pruning rate mechanism that enables self-regulating context management

### Tasks

#### T1.1: Implement `calculate_adaptive_rate()` Function
**Priority:** P0
**Estimated Hours:** 8
**Dependencies:** None

**Description:**
Implement the adaptive pruning rate formula from Technical Specification §2.2.2 that dynamically adjusts pruning aggressiveness based on current context utilization and CORE tier pressure.

**Acceptance Criteria:**
- [ ] Function implements the complete formula with all adjustment factors
- [ ] Returns rate within bounds [0.90, 1.10]
- [ ] Correctly adjusts based on utilization thresholds (<20%, 20-30%, 30-50%, 50-70%, >70%)
- [ ] Applies CORE budget pressure adjustment when core_utilization > 0.25
- [ ] Unit tests cover all threshold boundaries and edge cases
- [ ] Documentation includes formula explanation and examples

**Implementation Notes:**
```python
# Location: pruner.py
# Reference: TECHNICAL_SPECIFICATION.md §2.2.2

def calculate_adaptive_rate(current_utilization: float, core_utilization: float) -> float:
    """
    Calculate adaptive pruning rate (0.90 - 1.10)

    Factors:
    - Current utilization: Higher usage → more aggressive pruning
    - CORE budget pressure: More CORE content → more aggressive HOT pruning
    """
    # Implementation per spec
```

#### T1.2: Integrate Adaptive Rate into Pruner
**Priority:** P0
**Estimated Hours:** 6
**Dependencies:** T1.1

**Description:**
Update existing `prune_after_interaction()` method to use the adaptive pruning rate instead of a fixed rate.

**Acceptance Criteria:**
- [ ] `prune_after_interaction()` calls `calculate_adaptive_rate()` before pruning
- [ ] Pruning target calculated as `tokens_added * adaptive_rate`
- [ ] Metrics track actual pruning rate used per interaction
- [ ] Behavior verified via unit tests with various utilization scenarios
- [ ] No regressions in existing test suite

#### T1.3: Unit Tests for Adaptive Rate
**Priority:** P0
**Estimated Hours:** 6
**Dependencies:** T1.1

**Description:**
Comprehensive unit test coverage for adaptive rate calculation under all scenarios.

**Acceptance Criteria:**
- [ ] Test all utilization threshold boundaries (20%, 30%, 50%, 70%)
- [ ] Test CORE budget pressure scenarios
- [ ] Test edge cases (0% utilization, 100% utilization)
- [ ] Test boundary enforcement (min 0.90, max 1.10)
- [ ] Test combined adjustments (utilization + CORE pressure)
- [ ] All tests pass with >95% code coverage for adaptive rate logic

#### T1.4: Update Experiment 1 for Adaptive Rate
**Priority:** P0
**Estimated Hours:** 8
**Dependencies:** T1.2

**Description:**
Update `experiments/experiment_1_linear_growth.py` to use adaptive pruning rate and add convergence time measurement.

**Acceptance Criteria:**
- [ ] Experiment uses adaptive rate (not fixed 1.10)
- [ ] Tracks and plots pruning rate adjustments over time
- [ ] Measures time to steady state (when σ stabilizes)
- [ ] Verifies acceptance criteria from spec:
  - Linear growth coefficient: |slope| < 0.01
  - Steady-state oscillation: σ < 15% of target
  - Max utilization: <60% of target
  - Convergence time: <20 interactions
- [ ] Generates updated visualization showing rate adaptation
- [ ] Documentation updated with new metrics

#### T1.5: Convergence Validation Testing
**Priority:** P0
**Estimated Hours:** 6
**Dependencies:** T1.4

**Description:**
Run Experiment 1 with various initial conditions to validate convergence behavior.

**Acceptance Criteria:**
- [ ] Run experiment with 500 interactions
- [ ] Test with different random seeds (reproducibility)
- [ ] Verify all acceptance criteria met
- [ ] Document convergence behavior
- [ ] Create baseline results for comparison

#### T1.6: Documentation & Code Review
**Priority:** P0
**Estimated Hours:** 4
**Dependencies:** T1.5

**Description:**
Document adaptive rate implementation and prepare for Sprint 1 review.

**Acceptance Criteria:**
- [ ] Update README.md with adaptive rate explanation
- [ ] Add docstrings to all new functions
- [ ] Create inline comments explaining formula adjustments
- [ ] Update SPEC_SUMMARY.md if needed
- [ ] Self-review code for quality and maintainability

### Sprint 1 Deliverables

1. **Code Artifacts:**
   - `pruner.py`: Updated with `calculate_adaptive_rate()` and integrated into pruner
   - `test_pruner.py`: New unit tests for adaptive rate
   - `experiments/experiment_1_linear_growth.py`: Updated experiment

2. **Test Results:**
   - All unit tests passing (target: 100% of new tests)
   - Experiment 1 results showing convergence behavior
   - Validation data for adaptive rate formula

3. **Documentation:**
   - Updated README.md
   - Inline code documentation
   - Sprint 1 completion report

### Sprint 1 Definition of Done

- [ ] All task acceptance criteria met
- [ ] All unit tests passing (>95% coverage for new code)
- [ ] Experiment 1 updated and validated
- [ ] Code reviewed (self-review with checklist)
- [ ] Documentation complete and accurate
- [ ] No critical bugs or blockers
- [ ] Sprint demo prepared (adaptive rate visualization)

### Sprint 1 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Adaptive rate formula doesn't converge as expected | Medium | High | Adjust thresholds empirically, add safety bounds |
| Integration breaks existing tests | Low | Medium | Maintain backward compatibility, run full test suite |
| Convergence time exceeds 20 interactions | Medium | Low | Adjust formula parameters, document actual behavior |

---

## Sprint 2: Foundation - Baseline & CORE Budget

**Duration:** Week 3-4
**Goal:** Implement CORE budget enforcement and rule-based discrete compaction baseline for comparative evaluation

### Tasks

#### T2.1: Implement `CoreBudgetEnforcer` Class
**Priority:** P0
**Estimated Hours:** 10
**Dependencies:** None

**Description:**
Implement the CORE budget enforcement system that ensures CORE tier never exceeds 25% of target capacity (Technical Specification §2.3.1).

**Acceptance Criteria:**
- [ ] `CoreBudgetEnforcer` class implemented with all methods:
  - `can_add_to_core(item)`: Check budget availability
  - `add_to_core(item)`: Add item if budget allows
  - `remove_from_core(item)`: Remove item from CORE
  - `get_core_utilization()`: Calculate current CORE usage percentage
- [ ] Hard constraint enforced: CORE never exceeds 25% of target
- [ ] Overflow behavior: Items go to HOT tier with importance=0.95
- [ ] Budget tracking accurate (token counting)
- [ ] Warning logged when budget exceeded
- [ ] Unit tests cover all budget scenarios

#### T2.2: Integrate CORE Budget into Pruner
**Priority:** P0
**Estimated Hours:** 6
**Dependencies:** T2.1

**Description:**
Integrate `CoreBudgetEnforcer` into the main pruning algorithm.

**Acceptance Criteria:**
- [ ] Pruner initializes `CoreBudgetEnforcer` with target size
- [ ] CORE tier additions checked against budget before adding
- [ ] Overflow items correctly assigned to HOT with high importance
- [ ] Adaptive pruning rate receives CORE utilization for adjustment
- [ ] Metrics track CORE budget usage over time
- [ ] Integration tests verify end-to-end behavior

#### T2.3: Unprunable State Detection & Fallback
**Priority:** P1
**Estimated Hours:** 8
**Dependencies:** T2.2

**Description:**
Implement unprunable state detection and fallback strategy (Technical Specification §2.4).

**Acceptance Criteria:**
- [ ] `check_unprunable_state()` detects when <10% of context is prunable
- [ ] Fallback strategy: Force-unpin lowest 20% of HOT items
- [ ] Warning logged when unprunable state detected
- [ ] System continues operating (doesn't crash)
- [ ] Metrics track unprunable state events
- [ ] Unit tests simulate unprunable scenarios

#### T2.4: Implement `DiscreteCompactionBaseline` Class
**Priority:** P0
**Estimated Hours:** 12
**Dependencies:** None

**Description:**
Implement rule-based discrete compaction simulator that mimics traditional context management (Technical Specification §3.2.1).

**Acceptance Criteria:**
- [ ] `DiscreteCompactionBaseline` class implements:
  - Compaction at 80% utilization threshold
  - Compression to 30% of target capacity
  - Keep recent 5 interactions (10 items) fully
  - Summarize older content (keep top 20% by importance)
- [ ] Compaction events logged with metrics:
  - Interaction number
  - Tokens before/after
  - Items removed
- [ ] Compatible interface with continuous pruning (same API)
- [ ] Deterministic and reproducible behavior
- [ ] Unit tests verify compaction logic

#### T2.5: Baseline Validation Tests
**Priority:** P0
**Estimated Hours:** 6
**Dependencies:** T2.4

**Description:**
Create comprehensive tests for discrete compaction baseline to ensure it accurately simulates traditional behavior.

**Acceptance Criteria:**
- [ ] Test compaction triggers at correct threshold (80%)
- [ ] Verify compression reaches target (30%)
- [ ] Confirm recent items preserved
- [ ] Verify older items pruned according to importance
- [ ] Test multiple compaction cycles
- [ ] Measure degradation over cycles (expected behavior)

#### T2.6: Token Estimation Accuracy Tracking
**Priority:** P1
**Estimated Hours:** 6
**Dependencies:** T2.2

**Description:**
Implement token estimation accuracy measurement system (Technical Specification §2.5.2).

**Acceptance Criteria:**
- [ ] `TokenEstimationMetrics` class implemented:
  - `record(estimated, actual)`: Record estimation
  - `get_accuracy()`: Calculate metrics (mean error, max error, within 20%)
- [ ] Integrated into pruner for continuous tracking
- [ ] Acceptance criteria validation:
  - Mean error ≤ 20%
  - Max error ≤ 40%
  - 80%+ of estimates within ±20%
- [ ] Metrics reported in experiment results
- [ ] Unit tests for metrics calculation

#### T2.7: Integration Testing & Documentation
**Priority:** P0
**Estimated Hours:** 6
**Dependencies:** T2.2, T2.4, T2.6

**Description:**
End-to-end integration testing and documentation for Sprint 2 deliverables.

**Acceptance Criteria:**
- [ ] Integration tests for CORE budget + pruning
- [ ] Integration tests for baseline compaction
- [ ] Comparative test: run same scenario with both strategies
- [ ] Documentation updated (README, docstrings)
- [ ] Code review completed
- [ ] Sprint 2 demo prepared

### Sprint 2 Deliverables

1. **Code Artifacts:**
   - `pruner.py`: Updated with `CoreBudgetEnforcer` integration
   - `baseline.py`: New file with `DiscreteCompactionBaseline` class
   - `metrics.py`: New file with `TokenEstimationMetrics` class
   - `test_pruner.py`: Updated tests
   - `test_baseline.py`: New baseline tests

2. **Test Results:**
   - CORE budget enforcement validated
   - Baseline compaction behavior verified
   - Token estimation accuracy measured
   - Integration tests passing

3. **Documentation:**
   - Updated implementation documentation
   - Baseline comparison methodology documented

### Sprint 2 Definition of Done

- [ ] All task acceptance criteria met
- [ ] All unit and integration tests passing
- [ ] CORE budget never exceeded in any test scenario
- [ ] Baseline compaction behavior matches specification
- [ ] Token estimation tracking functional
- [ ] Unprunable state fallback tested
- [ ] Code reviewed and documented
- [ ] Sprint demo successful

### Sprint 2 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CORE budget enforcement too restrictive | Medium | Medium | Make budget configurable, test with various sizes |
| Baseline doesn't accurately simulate discrete compaction | Medium | High | Validate against real compaction behavior patterns, adjust rules |
| Unprunable state occurs frequently | Low | Medium | Tune importance scoring to reduce pinning |
| Token estimation too inaccurate | Medium | Low | Document actual accuracy, consider upgrading to tiktoken if critical |

---

## Sprint 3: Experiment 4 Infrastructure - SWE-bench Extended

**Duration:** Week 5-6
**Goal:** Build infrastructure for the primary code quality benchmark experiment using extended SWE-bench-Lite tasks

### Tasks

#### T3.1: SWE-bench-Lite Task Selection
**Priority:** P0
**Estimated Hours:** 10
**Dependencies:** None

**Description:**
Select and document 50 representative tasks from SWE-bench-Lite (300 total) for Phase I validation.

**Acceptance Criteria:**
- [ ] 50 tasks selected using principled methodology:
  - Stratified by difficulty (easy/medium/hard)
  - Diverse repository representation (multiple Python projects)
  - Varied task types (bug fixes, feature additions, refactoring)
- [ ] Selection criteria documented
- [ ] Task metadata extracted:
  - Issue description
  - Test suite
  - Expected solution characteristics
- [ ] Tasks stored in structured format (JSON/YAML)
- [ ] Validation: All selected tasks loadable and parseable

#### T3.2: Conversation Script Generator
**Priority:** P0
**Estimated Hours:** 12
**Dependencies:** T3.1

**Description:**
Create system to extend SWE-bench tasks into multi-turn conversations (15-30 turns) to stress-test context management.

**Acceptance Criteria:**
- [ ] Script generator creates conversation patterns:
  - Initial issue presentation
  - Clarification questions (2-3 turns)
  - Implementation planning (2-4 turns)
  - Code generation (3-5 turns)
  - Test execution and debugging (5-10 turns)
  - Refinement iterations (3-5 turns)
- [ ] Scripts include "noise" context items (logs, traces) to stress pruning
- [ ] Target: 15-30 turns per task
- [ ] Templates customizable per task
- [ ] Generated scripts reproducible (seeded random generation)
- [ ] Validation: Scripts generate realistic multi-turn interactions

**Implementation Notes:**
```python
# Location: experiments/swe_bench_extended/script_generator.py

class ConversationScriptGenerator:
    def generate_script(self, task: SWEBenchTask, seed: int) -> List[Turn]:
        """Generate extended multi-turn conversation for task"""
        # Template-based generation with task-specific customization
```

#### T3.3: SWE-bench Extended Task Loader
**Priority:** P0
**Estimated Hours:** 8
**Dependencies:** T3.1, T3.2

**Description:**
Implement task loader that provides extended SWE-bench tasks to experiment harness.

**Acceptance Criteria:**
- [ ] `SWEBenchExtendedLoader` class implemented:
  - `load_task(task_id)`: Load single task with conversation script
  - `load_batch(task_ids)`: Load multiple tasks
  - `iterate_tasks()`: Iterator over all 50 tasks
- [ ] Lazy loading for memory efficiency
- [ ] Caching for repeated access
- [ ] Error handling for missing/corrupt tasks
- [ ] Unit tests for loader functionality

#### T3.4: Test Harness Scaffolding
**Priority:** P0
**Estimated Hours:** 10
**Dependencies:** T3.3

**Description:**
Create test harness that executes tasks with different context strategies and collects results.

**Acceptance Criteria:**
- [ ] `ExperimentHarness` class implemented:
  - `run_task(task, strategy)`: Execute single task with context strategy
  - `run_batch(tasks, strategies)`: Batch execution with multiple strategies
  - `collect_metrics()`: Gather all metrics during execution
- [ ] Supports both continuous pruning and discrete baseline
- [ ] Configurable execution parameters (timeout, retries)
- [ ] Progress tracking and logging
- [ ] Result serialization (JSON/CSV)
- [ ] Error recovery (failed tasks don't block entire experiment)

#### T3.5: Mock Agent Implementation
**Priority:** P0
**Estimated Hours:** 8
**Dependencies:** T3.4

**Description:**
Create mock coding agent for testing harness infrastructure (will be replaced with real agent in Sprint 4).

**Acceptance Criteria:**
- [ ] `MockCodingAgent` implements agent interface:
  - `receive_message(content)`: Process user message
  - `generate_response()`: Generate agent response
  - `get_context_stats()`: Return context state
- [ ] Simulates realistic token usage (adds ~500-2000 tokens per turn)
- [ ] Deterministic behavior for testing
- [ ] Compatible with both pruning strategies
- [ ] Allows harness testing without LLM dependency

#### T3.6: End-to-End Infrastructure Test
**Priority:** P0
**Estimated Hours:** 6
**Dependencies:** T3.4, T3.5

**Description:**
Run end-to-end test of complete infrastructure with mock agent.

**Acceptance Criteria:**
- [ ] Successfully load and execute 5 sample tasks
- [ ] Run with both continuous pruning and discrete baseline
- [ ] Verify metrics collected correctly
- [ ] Confirm results serialized properly
- [ ] Performance acceptable (5 tasks complete in <5 minutes with mock agent)
- [ ] No memory leaks or resource issues

#### T3.7: Documentation & Sprint Review
**Priority:** P0
**Estimated Hours:** 4
**Dependencies:** T3.6

**Description:**
Document infrastructure and prepare Sprint 3 demo.

**Acceptance Criteria:**
- [ ] Infrastructure architecture documented
- [ ] Task selection methodology documented
- [ ] Conversation script format documented
- [ ] Usage examples provided
- [ ] Sprint demo prepared showing end-to-end flow

### Sprint 3 Deliverables

1. **Code Artifacts:**
   - `experiments/swe_bench_extended/`: New directory with:
     - `task_loader.py`: Task loading infrastructure
     - `script_generator.py`: Conversation script generation
     - `harness.py`: Experiment execution harness
     - `mock_agent.py`: Mock agent for testing
   - `data/swe_bench_tasks.json`: Selected 50 tasks with metadata
   - `data/conversation_scripts/`: Generated scripts for tasks

2. **Data Assets:**
   - 50 selected SWE-bench-Lite tasks
   - Generated conversation scripts (15-30 turns each)
   - Task metadata and selection criteria

3. **Test Results:**
   - Infrastructure validation tests passing
   - End-to-end test successful with mock agent
   - Performance benchmarks documented

4. **Documentation:**
   - Infrastructure design document
   - Task selection methodology
   - Usage guide for experiment harness

### Sprint 3 Definition of Done

- [ ] All task acceptance criteria met
- [ ] 50 tasks selected and loaded successfully
- [ ] Conversation scripts generated for all tasks
- [ ] Test harness executes end-to-end with mock agent
- [ ] All infrastructure tests passing
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Sprint demo successful
- [ ] Ready for real agent integration in Sprint 4

### Sprint 3 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SWE-bench-Lite tasks too complex to extend | Medium | High | Start with simpler tasks, adjust conversation length if needed |
| Generated scripts not realistic enough | Medium | Medium | Manual review of sample scripts, iterate on templates |
| Infrastructure too slow for 50 tasks | Low | Medium | Optimize critical paths, consider parallel execution |
| 50 tasks insufficient for statistical significance | Low | Low | Document limitation, consider expanding to 100 in Sprint 5 if time permits |

---

## Sprint 4: Code Quality Experiment Execution

**Duration:** Week 7-8
**Goal:** Execute Experiment 4 (primary validation) comparing continuous pruning vs. discrete baseline on code generation quality

### Tasks

#### T4.1: Implement Code Quality Metrics
**Priority:** P0
**Estimated Hours:** 12
**Dependencies:** None

**Description:**
Implement all four code quality metrics for evaluating agent performance (Technical Specification §4.3).

**Acceptance Criteria:**
- [ ] **Metric 1: Task Completion Rate**
  - Test suite execution
  - Pass/fail determination
  - Percentage calculation
- [ ] **Metric 2: Specification Adherence Score**
  - Requirement extraction from issue description
  - Implementation validation (checklist-based)
  - Scoring: 0-100% requirements met
- [ ] **Metric 3: Code Quality Score**
  - Maintainability rubric (0-5)
  - Convention adherence (0-5)
  - Completeness (0-5)
  - Specification match (0-5)
  - Aggregate score (0-20)
- [ ] **Metric 4: Implementation Consistency**
  - Track approach consistency across turns
  - Measure decision coherence
  - Detect contradictions or reversals
  - Score: 0-5 (5 = perfectly consistent)
- [ ] All metrics implemented as classes with common interface
- [ ] Unit tests for each metric

#### T4.2: Real Agent Integration
**Priority:** P0
**Estimated Hours:** 10
**Dependencies:** Sprint 3 deliverables

**Description:**
Replace mock agent with actual LLM-based coding agent implementation.

**Acceptance Criteria:**
- [ ] Agent integrates with Claude API (or chosen LLM)
- [ ] Implements full coding agent interface:
  - Message processing
  - Code generation
  - Context management with strategy injection
  - Test execution
- [ ] Works with both continuous pruning and discrete baseline
- [ ] Error handling for API failures
- [ ] Rate limiting and retry logic
- [ ] API cost tracking
- [ ] Deterministic mode for reproducibility (temperature=0)

**Implementation Notes:**
```python
# Location: experiments/coding_agent.py

class CodingAgent:
    def __init__(self, context_strategy: ContextStrategy, llm_config: dict):
        self.context_strategy = context_strategy
        self.llm = initialize_llm(llm_config)

    def generate_response(self, prompt: str) -> str:
        # Use context_strategy to manage context
        # Call LLM with managed context
        # Return response
```

#### T4.3: Experiment 4 Implementation
**Priority:** P0
**Estimated Hours:** 8
**Dependencies:** T4.1, T4.2

**Description:**
Implement complete Experiment 4: Code Quality Benchmark (Technical Specification §5.4).

**Acceptance Criteria:**
- [ ] Experiment script (`experiments/experiment_4_code_quality.py`) implemented
- [ ] Runs all 50 tasks with both strategies:
  - Continuous pruning (adaptive rate)
  - Discrete compaction baseline
  - Control (no pruning, if capacity allows)
- [ ] Collects all four quality metrics per task
- [ ] Saves results in structured format
- [ ] Configurable parameters (task subset, strategies, iterations)
- [ ] Progress tracking and estimated time remaining
- [ ] Checkpointing (resume if interrupted)

#### T4.4: Experiment 4 Execution - Continuous Pruning
**Priority:** P0
**Estimated Hours:** 6 (execution time)
**Dependencies:** T4.3

**Description:**
Execute Experiment 4 with continuous pruning strategy on all 50 tasks.

**Acceptance Criteria:**
- [ ] All 50 tasks executed successfully
- [ ] No execution failures or crashes
- [ ] All metrics collected for each task
- [ ] Results saved and backed up
- [ ] Execution time logged
- [ ] API costs tracked

#### T4.5: Experiment 4 Execution - Discrete Baseline
**Priority:** P0
**Estimated Hours:** 6 (execution time)
**Dependencies:** T4.3

**Description:**
Execute Experiment 4 with discrete compaction baseline on all 50 tasks.

**Acceptance Criteria:**
- [ ] All 50 tasks executed successfully
- [ ] Same tasks as continuous pruning (fair comparison)
- [ ] All metrics collected for each task
- [ ] Results saved and backed up
- [ ] Execution time logged
- [ ] API costs tracked

#### T4.6: Preliminary Analysis
**Priority:** P0
**Estimated Hours:** 8
**Dependencies:** T4.4, T4.5

**Description:**
Perform initial comparative analysis of continuous pruning vs. discrete baseline results.

**Acceptance Criteria:**
- [ ] Statistical comparison of all four metrics:
  - Task completion rate comparison
  - Specification adherence comparison
  - Code quality score comparison
  - Consistency score comparison
- [ ] Visualizations created:
  - Bar charts for each metric
  - Box plots showing distributions
  - Scatter plots for correlations
- [ ] Statistical significance testing (t-test, if applicable)
- [ ] Acceptance criteria validation:
  - Continuous ≥90% of baseline completion rate
  - Continuous ≥95% of baseline spec adherence
  - Continuous ≥ baseline code quality
- [ ] Preliminary findings documented

#### T4.7: Sprint 4 Documentation & Review
**Priority:** P0
**Estimated Hours:** 4
**Dependencies:** T4.6

**Description:**
Document Experiment 4 results and prepare sprint review.

**Acceptance Criteria:**
- [ ] Experiment 4 methodology documented
- [ ] Results documented with visualizations
- [ ] Preliminary findings summarized
- [ ] Limitations and observations noted
- [ ] Sprint demo prepared
- [ ] Go/no-go decision for Phase I success prepared

### Sprint 4 Deliverables

1. **Code Artifacts:**
   - `experiments/coding_agent.py`: Real agent implementation
   - `experiments/experiment_4_code_quality.py`: Complete experiment
   - `experiments/metrics.py`: All four quality metrics
   - Updated test suite

2. **Experimental Results:**
   - 50 tasks × 2 strategies = 100 task executions
   - Complete metrics dataset
   - Raw results (JSON/CSV)
   - Processed results with analysis

3. **Analysis:**
   - Comparative analysis report
   - Visualizations (charts, plots)
   - Statistical significance tests
   - Preliminary conclusions

4. **Documentation:**
   - Experiment methodology
   - Results interpretation
   - Sprint 4 completion report

### Sprint 4 Definition of Done

- [ ] All task acceptance criteria met
- [ ] All 100 task executions completed successfully
- [ ] All four metrics calculated for each execution
- [ ] Preliminary analysis complete
- [ ] Results validate at least 2 of 3 acceptance criteria:
  - Task completion ≥90% of baseline
  - Spec adherence ≥95% of baseline
  - Code quality ≥ baseline
- [ ] Documentation complete
- [ ] Sprint demo successful
- [ ] Phase I success likelihood assessed

### Sprint 4 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM API failures during execution | Medium | High | Implement robust retry logic, checkpoint progress, budget extra time |
| Results don't meet acceptance criteria | Medium | Critical | Analyze failure modes, adjust algorithm if systematic issues found |
| Execution time exceeds 2-week sprint | Low | Medium | Run experiments in parallel if possible, prioritize critical tasks |
| API costs exceed budget | Low | Medium | Monitor costs closely, use smaller model for testing, budget contingency |
| Code quality metric unreliable/subjective | Medium | Medium | Add automated quality checks (linters), manual review of sample outputs |

**Critical Decision Point:** If results significantly fail acceptance criteria, may need to iterate on algorithm before proceeding to Sprint 5.

---

## Sprint 5: Additional Experiments & Comprehensive Metrics

**Duration:** Week 9-10
**Goal:** Execute Experiments 2 & 3, implement comprehensive metrics collection, and validate all secondary hypotheses

### Tasks

#### T5.1: Implement Experiment 2: Convergence
**Priority:** P1
**Estimated Hours:** 8
**Dependencies:** Sprint 1-2 deliverables

**Description:**
Implement Experiment 2 to validate that adaptive pruning rate causes convergence from various initial states (Technical Specification §5.2).

**Acceptance Criteria:**
- [ ] Experiment script (`experiments/experiment_2_convergence.py`) implemented
- [ ] Tests 4 initial conditions:
  - 0% full (empty context)
  - 20% full (low utilization)
  - 50% full (medium utilization)
  - 80% full (high utilization)
- [ ] Runs 100 interactions for each condition
- [ ] Measures for each condition:
  - Time to steady state (interactions until σ stabilizes)
  - Final steady-state utilization
  - Pruning rate trajectory over time
- [ ] Generates convergence trajectory plots
- [ ] Validates acceptance criteria:
  - All conditions converge to 20-40% utilization
  - Convergence time <30 interactions
  - Pruning rate adapts correctly per formula

#### T5.2: Execute Experiment 2 & Analyze Results
**Priority:** P1
**Estimated Hours:** 6
**Dependencies:** T5.1

**Description:**
Run Experiment 2 and perform analysis on convergence behavior.

**Acceptance Criteria:**
- [ ] All 4 initial conditions tested successfully
- [ ] Convergence trajectories plotted
- [ ] Statistical analysis of convergence time
- [ ] Verification that adaptive rate formula works as designed
- [ ] Acceptance criteria validation completed
- [ ] Results documented with visualizations

#### T5.3: Implement Experiment 3: Information Preservation
**Priority:** P1
**Estimated Hours:** 10
**Dependencies:** Sprint 2 deliverables

**Description:**
Implement Experiment 3 to compare CORE decision recall between continuous pruning and discrete baseline (Technical Specification §5.3).

**Acceptance Criteria:**
- [ ] Experiment script (`experiments/experiment_3_preservation.py`) implemented
- [ ] 10 critical decisions defined with ground truth:
  - Technical decisions (database choice, auth method, etc.)
  - Each decision has: topic, full rationale, key details
- [ ] Decisions added to CORE at interactions 1-5
- [ ] Runs 100 interactions with decision injection
- [ ] Recall tests at interactions 50 and 100:
  - Query about each decision
  - Score recall quality (0-5 scale)
  - Measure completeness and accuracy
- [ ] Runs with both strategies:
  - Continuous pruning (CORE protected)
  - Discrete baseline (rule-based compression)
- [ ] Implements recall assessment scoring function

**Implementation Notes:**
```python
# Location: experiments/experiment_3_preservation.py

CRITICAL_DECISIONS = [
    {
        'topic': 'database',
        'decision': 'Use PostgreSQL for primary database',
        'rationale': 'Chose PostgreSQL for ACID compliance, JSON support, and team expertise',
        'key_details': ['ACID compliance', 'JSON support', 'team expertise']
    },
    # ... 9 more decisions
]

def assess_recall_quality(decision: dict, agent_response: str) -> float:
    """Score recall quality 0-5 based on accuracy and completeness"""
    # Check if decision mentioned correctly
    # Check if rationale preserved
    # Check if key details present
    # Return score
```

#### T5.4: Execute Experiment 3 & Analyze Results
**Priority:** P1
**Estimated Hours:** 8
**Dependencies:** T5.3

**Description:**
Run Experiment 3 with both strategies and perform comparative analysis.

**Acceptance Criteria:**
- [ ] Both strategies tested (continuous + discrete)
- [ ] Recall tested at interactions 50 and 100
- [ ] All 10 decisions tested per checkpoint
- [ ] Recall scores calculated and aggregated
- [ ] Comparative analysis completed:
  - Continuous pruning recall vs. discrete baseline
  - Degradation over time measured
  - Statistical significance tested
- [ ] Acceptance criteria validated:
  - Continuous: >90% recall (score ≥4.5/5)
  - Discrete: <70% recall (demonstrates degradation)
  - Relative improvement: ≥25%
- [ ] Results visualized (bar charts, degradation curves)

#### T5.5: Implement Comprehensive Metrics Collection
**Priority:** P1
**Estimated Hours:** 8
**Dependencies:** Sprint 2-4 deliverables

**Description:**
Implement `EvaluationHarness` for collecting all metrics across four dimensions (Technical Specification §4.3.1).

**Acceptance Criteria:**
- [ ] `EvaluationHarness` class implemented with:
  - `StabilityMetrics`: Token oscillation, growth, utilization
  - `PreservationMetrics`: Recall accuracy, rationale completeness
  - `CodeQualityMetrics`: All four from Experiment 4
  - `PerformanceMetrics`: Execution time, API costs, throughput
- [ ] Automated collection during all experiments
- [ ] Unified reporting format across experiments
- [ ] Aggregation and statistical analysis functions
- [ ] Export to multiple formats (JSON, CSV, markdown)

#### T5.6: Cross-Experiment Analysis
**Priority:** P1
**Estimated Hours:** 8
**Dependencies:** T5.2, T5.4, T5.5

**Description:**
Perform comprehensive analysis across all four experiments.

**Acceptance Criteria:**
- [ ] Unified dataset with all experiment results
- [ ] Multi-dimensional scorecard populated (4 dimensions from spec)
- [ ] Comparative analysis: continuous vs. discrete across all metrics
- [ ] Correlation analysis: Are stability and code quality related?
- [ ] Comprehensive visualizations:
  - Dashboard showing all key metrics
  - Comparative charts for each dimension
  - Summary scorecards
- [ ] Statistical validation of all claims
- [ ] Findings documented with evidence

#### T5.7: Sprint 5 Documentation & Review
**Priority:** P1
**Estimated Hours:** 4
**Dependencies:** T5.6

**Description:**
Document Experiments 2-3 and comprehensive analysis.

**Acceptance Criteria:**
- [ ] Experiment 2 methodology and results documented
- [ ] Experiment 3 methodology and results documented
- [ ] Comprehensive metrics documentation
- [ ] Cross-experiment analysis documented
- [ ] Sprint demo prepared
- [ ] Phase I success assessment updated

### Sprint 5 Deliverables

1. **Code Artifacts:**
   - `experiments/experiment_2_convergence.py`: Convergence testing
   - `experiments/experiment_3_preservation.py`: Information preservation
   - `experiments/evaluation_harness.py`: Comprehensive metrics
   - Updated metrics classes

2. **Experimental Results:**
   - Experiment 2 results (4 initial conditions)
   - Experiment 3 results (continuous vs. discrete recall)
   - Comprehensive metrics across all experiments
   - Unified dataset

3. **Analysis:**
   - Convergence analysis report
   - Information preservation analysis
   - Multi-dimensional comparative analysis
   - Statistical validation

4. **Documentation:**
   - Experiment 2-3 documentation
   - Comprehensive metrics guide
   - Cross-experiment analysis report

### Sprint 5 Definition of Done

- [ ] All task acceptance criteria met
- [ ] Experiments 2 and 3 executed successfully
- [ ] All acceptance criteria for Experiments 2-3 validated
- [ ] Comprehensive metrics collection functional
- [ ] Cross-experiment analysis complete
- [ ] All documentation complete
- [ ] Sprint demo successful
- [ ] Phase I success criteria substantially met

### Sprint 5 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Recall assessment scoring too subjective | Medium | Medium | Define clear rubric, use automated checks where possible, manual review samples |
| Convergence doesn't meet acceptance criteria | Low | Medium | Tune adaptive rate parameters, document actual behavior if different |
| Time insufficient for comprehensive analysis | Medium | Low | Prioritize critical analyses, defer nice-to-have visualizations to Sprint 6 |

---

## Sprint 6: Analysis, Reporting & Phase I Completion

**Duration:** Week 11-12
**Goal:** Complete Phase I validation with comprehensive technical report, finalize repository, and make Phase II go/no-go decision

### Tasks

#### T6.1: Final Validation & Verification
**Priority:** P1
**Estimated Hours:** 8
**Dependencies:** Sprint 1-5 deliverables

**Description:**
Run final validation tests to ensure all claims are reproducible and acceptance criteria met.

**Acceptance Criteria:**
- [ ] Re-run critical experiments to verify reproducibility
- [ ] Validate all acceptance criteria from Technical Specification §7.2:
  - **Context Stability**: Linear growth, oscillation, utilization, convergence
  - **Information Preservation**: CORE recall, relative improvement
  - **Code Quality**: Task completion, spec adherence, code quality
  - **System Integrity**: CORE budget, adaptive rate, token estimation, unprunable fallback
- [ ] Create acceptance criteria checklist with evidence
- [ ] Document any criteria not met with explanations
- [ ] Verify all statistical claims are properly supported
- [ ] Identify and document limitations

#### T6.2: Technical Report - Draft
**Priority:** P1
**Estimated Hours:** 12
**Dependencies:** T6.1

**Description:**
Write comprehensive technical report documenting Phase I research findings.

**Acceptance Criteria:**
- [ ] Report structure includes:
  1. Executive Summary
  2. Introduction & Motivation
  3. Methodology (algorithm description, experimental design)
  4. Results (all four experiments with data)
  5. Analysis (comparative, statistical)
  6. Discussion (implications, limitations)
  7. Conclusion (success criteria assessment)
  8. Appendices (detailed data, additional plots)
- [ ] Length: 15-25 pages
- [ ] Professional academic/technical style
- [ ] All claims supported by data
- [ ] Visualizations clear and informative
- [ ] Limitations honestly discussed
- [ ] References complete

#### T6.3: Technical Report - Peer Review & Revision
**Priority:** P1
**Estimated Hours:** 6
**Dependencies:** T6.2

**Description:**
Internal peer review and revision of technical report.

**Acceptance Criteria:**
- [ ] Self-review using quality checklist:
  - Clarity and organization
  - Data accuracy
  - Claim validity
  - Completeness
  - Professional presentation
- [ ] Revisions completed based on review
- [ ] Final version proofread
- [ ] PDF and markdown versions generated

#### T6.4: Repository Finalization
**Priority:** P1
**Estimated Hours:** 8
**Dependencies:** T6.1

**Description:**
Finalize open-source repository for public release with reproducible experiments.

**Acceptance Criteria:**
- [ ] All code cleaned and documented:
  - Consistent style (PEP 8 for Python)
  - Comprehensive docstrings
  - Clear comments
  - Type hints
- [ ] Complete test coverage:
  - All unit tests passing
  - Integration tests passing
  - Test coverage >90%
- [ ] Documentation complete:
  - README.md with clear setup instructions
  - TECHNICAL_SPECIFICATION.md
  - IMPLEMENTATION_WORKFLOW.md (this document)
  - API documentation
  - Experiment reproduction guide
- [ ] Example notebooks for key experiments
- [ ] Requirements.txt with pinned versions
- [ ] LICENSE file (MIT)
- [ ] CONTRIBUTING.md guidelines
- [ ] .gitignore comprehensive

#### T6.5: Reproducibility Validation
**Priority:** P1
**Estimated Hours:** 6
**Dependencies:** T6.4

**Description:**
Validate that experiments are fully reproducible from clean repository.

**Acceptance Criteria:**
- [ ] Fresh virtual environment setup successful
- [ ] All dependencies install correctly
- [ ] All tests pass in fresh environment
- [ ] All experiments run successfully
- [ ] Results match documented findings (within random variation)
- [ ] Reproduction guide tested by running all steps
- [ ] Estimated reproduction time documented

#### T6.6: Phase II Decision Document
**Priority:** P1
**Estimated Hours:** 6
**Dependencies:** T6.1, T6.2

**Description:**
Create decision document for Phase II go/no-go based on Phase I results.

**Acceptance Criteria:**
- [ ] Document structure:
  1. Phase I Success Assessment
  2. Quantitative Results Summary
  3. Qualitative Assessment
  4. Lessons Learned
  5. Recommended Next Steps
  6. Phase II Scope (if go)
  7. Resource Requirements (if go)
  8. Alternative Approaches (if no-go)
- [ ] Clear recommendation: Go / Iterate / No-go
- [ ] Risk assessment for Phase II
- [ ] Resource and timeline estimates for Phase II
- [ ] Stakeholder presentation deck

#### T6.7: Final Presentation & Sprint Demo
**Priority:** P1
**Estimated Hours:** 6
**Dependencies:** T6.3, T6.6

**Description:**
Prepare and deliver final Phase I presentation.

**Acceptance Criteria:**
- [ ] Presentation deck created (20-30 slides):
  - Problem statement
  - Approach overview
  - Key results from all experiments
  - Comparative analysis
  - Success criteria assessment
  - Phase II recommendation
- [ ] Live demo of pruning algorithm
- [ ] Q&A preparation
- [ ] Presentation delivered to stakeholders
- [ ] Feedback collected

#### T6.8: Project Handoff & Closure
**Priority:** P1
**Estimated Hours:** 4
**Dependencies:** All Sprint 6 tasks

**Description:**
Complete project handoff and administrative closure.

**Acceptance Criteria:**
- [ ] All deliverables packaged and delivered:
  - Technical report (PDF + markdown)
  - Open-source repository (GitHub)
  - Phase II decision document
  - Final presentation
- [ ] Project retrospective completed:
  - What went well
  - What could be improved
  - Lessons learned for Phase II
- [ ] Documentation archived
- [ ] Project closure checklist completed
- [ ] Thank you notes to contributors (if applicable)

### Sprint 6 Deliverables

1. **Technical Report:**
   - Comprehensive Phase I research report (PDF + markdown)
   - 15-25 pages with full experimental results
   - Professional academic/technical quality

2. **Repository:**
   - Finalized open-source codebase
   - Complete documentation
   - Reproducible experiments
   - >90% test coverage

3. **Decision Document:**
   - Phase II go/no-go recommendation
   - Resource and timeline estimates
   - Risk assessment

4. **Presentation:**
   - Final presentation deck
   - Live demo materials
   - Stakeholder Q&A

5. **Project Artifacts:**
   - Complete documentation archive
   - Retrospective notes
   - Handoff materials

### Sprint 6 Definition of Done

- [ ] All task acceptance criteria met
- [ ] Technical report complete and reviewed
- [ ] Repository finalized and reproducible
- [ ] All experiments validated
- [ ] Phase II decision made
- [ ] Final presentation delivered
- [ ] All deliverables packaged and delivered
- [ ] Project closure complete
- [ ] Phase I officially concluded

### Sprint 6 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Technical report takes longer than estimated | Medium | Low | Start writing early, reuse analysis from sprints 4-5 |
| Reproducibility issues discovered late | Low | Medium | Test early and continuously, maintain clean environment |
| Stakeholders request major changes | Low | Low | Set clear expectations early, manage scope |
| Time insufficient for quality report | Medium | Medium | Prioritize content over polish, extend 2-3 days if critical |

---

## Dependency Map

### Task Dependencies Across Sprints

```
Sprint 1: Foundation - Adaptive Pruning
├─ T1.1: calculate_adaptive_rate()
├─ T1.2: Integrate into pruner ────────► (depends on T1.1)
├─ T1.3: Unit tests ───────────────────► (depends on T1.1)
├─ T1.4: Update Experiment 1 ──────────► (depends on T1.2)
├─ T1.5: Validation testing ───────────► (depends on T1.4)
└─ T1.6: Documentation ────────────────► (depends on T1.5)

Sprint 2: Baseline & CORE Budget
├─ T2.1: CoreBudgetEnforcer
├─ T2.2: Integrate CORE budget ────────► (depends on T2.1, T1.2)
├─ T2.3: Unprunable fallback ──────────► (depends on T2.2)
├─ T2.4: DiscreteCompactionBaseline
├─ T2.5: Baseline validation tests ────► (depends on T2.4)
├─ T2.6: Token estimation tracking ────► (depends on T2.2)
└─ T2.7: Integration testing ──────────► (depends on T2.2, T2.4, T2.6)

Sprint 3: Experiment 4 Infrastructure
├─ T3.1: Task selection
├─ T3.2: Script generator ─────────────► (depends on T3.1)
├─ T3.3: Task loader ──────────────────► (depends on T3.1, T3.2)
├─ T3.4: Test harness ─────────────────► (depends on T3.3)
├─ T3.5: Mock agent ───────────────────► (depends on T3.4)
├─ T3.6: E2E test ─────────────────────► (depends on T3.4, T3.5)
└─ T3.7: Documentation ────────────────► (depends on T3.6)

Sprint 4: Code Quality Experiment
├─ T4.1: Quality metrics
├─ T4.2: Real agent ───────────────────► (depends on Sprint 3)
├─ T4.3: Experiment 4 impl ────────────► (depends on T4.1, T4.2)
├─ T4.4: Execute - continuous ─────────► (depends on T4.3, Sprint 1-2)
├─ T4.5: Execute - baseline ───────────► (depends on T4.3, Sprint 2)
├─ T4.6: Preliminary analysis ─────────► (depends on T4.4, T4.5)
└─ T4.7: Documentation ────────────────► (depends on T4.6)

Sprint 5: Additional Experiments
├─ T5.1: Implement Experiment 2 ───────► (depends on Sprint 1-2)
├─ T5.2: Execute Experiment 2 ─────────► (depends on T5.1)
├─ T5.3: Implement Experiment 3 ───────► (depends on Sprint 2)
├─ T5.4: Execute Experiment 3 ─────────► (depends on T5.3, Sprint 2)
├─ T5.5: Metrics collection ───────────► (depends on Sprint 2-4)
├─ T5.6: Cross-experiment analysis ────► (depends on T5.2, T5.4, T5.5)
└─ T5.7: Documentation ────────────────► (depends on T5.6)

Sprint 6: Analysis & Reporting
├─ T6.1: Final validation ─────────────► (depends on Sprint 1-5)
├─ T6.2: Technical report draft ───────► (depends on T6.1)
├─ T6.3: Report revision ──────────────► (depends on T6.2)
├─ T6.4: Repository finalization ──────► (depends on T6.1)
├─ T6.5: Reproducibility validation ───► (depends on T6.4)
├─ T6.6: Phase II decision ────────────► (depends on T6.1, T6.2)
├─ T6.7: Final presentation ───────────► (depends on T6.3, T6.6)
└─ T6.8: Project closure ──────────────► (depends on all T6 tasks)
```

### Critical Path

**Critical Path Tasks** (delays block project completion):

```
T1.1 → T1.2 → T1.4 → T1.5 →
T2.2 → T2.4 → T2.7 →
T3.1 → T3.2 → T3.3 → T3.4 → T3.6 →
T4.2 → T4.3 → T4.4 → T4.5 → T4.6 →
T5.6 →
T6.1 → T6.2 → T6.3 → T6.7 → T6.8
```

**Critical Path Duration:** ~11 weeks (with 1 week buffer)

---

## Resource Requirements

### Development Tools

**Required:**
- Python 3.9+ environment
- Git version control
- Code editor / IDE (VS Code, PyCharm)
- Testing framework (pytest)
- Virtual environment management (venv, conda, or uv)

**Optional:**
- Jupyter notebooks (for analysis)
- Docker (for reproducibility)
- CI/CD pipeline (GitHub Actions)

### External Dependencies

**Phase I Requirements:**

1. **LLM API Access** (Sprint 4+)
   - Claude API (Anthropic) or equivalent
   - Estimated tokens: 50 tasks × 30 turns × 4000 tokens = ~6M tokens
   - Budget: $60-120 depending on model (assuming $0.01-0.02 per 1K tokens)
   - Rate limits: Handle API throttling

2. **SWE-bench Dataset**
   - SWE-bench-Lite (300 tasks, publicly available)
   - Storage: ~100MB for task data
   - No special access required

3. **Compute Resources**
   - Development machine: Modern laptop/desktop (8GB+ RAM)
   - Experiment execution: ~10-20 hours total runtime
   - Storage: 5-10GB for results, logs, checkpoints

### Data Requirements

**Storage Estimates:**

| Asset | Size | Description |
|-------|------|-------------|
| SWE-bench tasks | 100MB | 50 selected tasks with metadata |
| Conversation scripts | 50MB | Generated 15-30 turn scripts |
| Experiment results | 500MB | Raw data from all experiments |
| Checkpoints | 200MB | Intermediate results, recovery data |
| Logs | 100MB | Execution logs, debug traces |
| Visualizations | 50MB | Charts, plots, diagrams |
| **Total** | **~1GB** | Complete project data |

### API Budget

**LLM API Cost Estimates:**

| Experiment | Tokens | Cost (Claude Opus) | Cost (Claude Sonnet) |
|------------|--------|---------------------|----------------------|
| Exp 4 - Continuous | ~3M tokens | $45 | $15 |
| Exp 4 - Baseline | ~3M tokens | $45 | $15 |
| Exp 3 - Recall tests | ~0.5M tokens | $7.50 | $2.50 |
| Testing & debugging | ~0.5M tokens | $7.50 | $2.50 |
| **Total** | **~7M tokens** | **~$105** | **~$35** |

**Recommendation:** Use Claude Sonnet for cost efficiency (~$35 total budget)

**Buffer:** Add 50% contingency for retries, debugging = **~$50 total**

### Human Resources

**Single Developer (Research Engineer):**
- **Availability:** 20-25 hours/week (50% allocation)
- **Skills Required:**
  - Python development (intermediate-advanced)
  - Algorithm design and analysis
  - Statistical analysis
  - Technical writing
  - LLM API integration
  - Git/GitHub proficiency

**Time Allocation:**
- Implementation: 40%
- Experimentation: 30%
- Analysis: 15%
- Documentation: 15%

---

## Testing Strategy

### Testing Pyramid

```
                    /\
                   /  \
                  / E2E\         5% - End-to-end experiments
                 /______\
                /        \
               /Integration\     20% - Component integration
              /____________\
             /              \
            /  Unit Tests    \   75% - Unit tests
           /__________________\
```

### Testing Levels

#### 1. Unit Tests (75% of test effort)

**Scope:** Individual functions and classes

**Tools:** pytest, pytest-cov

**Coverage Target:** >95% for core algorithm code

**Key Test Suites:**

| Component | Test File | Tests | Coverage Target |
|-----------|-----------|-------|-----------------|
| Adaptive pruning rate | `test_pruner.py::TestAdaptiveRate` | 15+ | 100% |
| CORE budget enforcer | `test_pruner.py::TestCoreBudget` | 12+ | 100% |
| Importance scoring | `test_pruner.py::TestImportanceScore` | 10+ | 95% |
| Discrete baseline | `test_baseline.py::TestDiscrete` | 10+ | 95% |
| Token estimation | `test_metrics.py::TestTokenEstimation` | 8+ | 95% |
| Context item management | `test_pruner.py::TestContextItem` | 8+ | 95% |

**Execution:** Every commit (pre-commit hook)

#### 2. Integration Tests (20% of test effort)

**Scope:** Component interactions

**Key Integration Tests:**

1. **Pruner + CORE Budget Integration**
   - Test: CORE additions with budget constraints
   - Test: Overflow behavior (CORE full → HOT with high importance)
   - Test: Adaptive rate adjusts based on CORE utilization

2. **Pruner + Baseline Comparison**
   - Test: Same scenario with both strategies
   - Test: Verify different behaviors (continuous vs. discrete)
   - Test: Metrics collection for both

3. **Experiment Harness + Agent**
   - Test: Full task execution with mock agent
   - Test: Metrics collection during execution
   - Test: Result serialization and loading

**Execution:** Daily (CI/CD pipeline)

#### 3. End-to-End Tests (5% of test effort)

**Scope:** Complete experiment workflows

**E2E Test Scenarios:**

1. **Experiment 1 E2E**
   - Run 100 interactions (reduced from 500 for testing)
   - Verify stability metrics calculated correctly
   - Confirm results match expected patterns

2. **Experiment 4 E2E (Mini)**
   - Run 3 sample tasks with both strategies
   - Verify all metrics collected
   - Confirm comparative analysis generates

3. **Reproducibility E2E**
   - Fresh environment setup
   - Run key experiments
   - Verify results within expected variance

**Execution:** Weekly + before major milestones

### Sprint-Specific Testing

#### Sprint 1 Testing Focus
- Adaptive rate formula correctness
- Convergence behavior validation
- Experiment 1 updated tests

#### Sprint 2 Testing Focus
- CORE budget enforcement (no violations)
- Unprunable state fallback
- Baseline compaction behavior
- Token estimation accuracy

#### Sprint 3 Testing Focus
- Task loading correctness
- Script generation validity
- Harness execution flow
- Mock agent behavior

#### Sprint 4 Testing Focus
- Quality metrics accuracy
- Real agent integration
- Full experiment execution
- Result validation

#### Sprint 5 Testing Focus
- Experiment 2 convergence tests
- Experiment 3 recall tests
- Cross-experiment metrics
- Statistical analysis validation

#### Sprint 6 Testing Focus
- Reproducibility validation
- All experiments re-run
- Final acceptance criteria verification
- Clean environment testing

### Continuous Integration

**CI Pipeline (GitHub Actions):**

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run unit tests
        run: pytest test_*.py -v --cov=. --cov-report=term-missing
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Check code style
        run: |
          pip install black flake8
          black --check .
          flake8 . --max-line-length=100
```

**Quality Gates:**
- All tests must pass
- Coverage >90%
- No critical flake8 violations
- Code formatted with black

### Manual Testing Checklist

**Before Each Sprint Demo:**
- [ ] Run all automated tests
- [ ] Execute demo scenario end-to-end
- [ ] Verify visualizations render correctly
- [ ] Check documentation is up-to-date
- [ ] Test edge cases manually
- [ ] Verify error messages are clear

---

## Milestone Schedule

### Project Milestones

```
Week 0  ─┬─ PROJECT KICKOFF
         │
Week 2  ─┼─ MILESTONE 1: Adaptive Pruning Foundation Complete
         │  Deliverable: Working adaptive rate + updated Experiment 1
         │  Gate: Convergence demonstrated
         │
Week 4  ─┼─ MILESTONE 2: CORE Budget & Baseline Complete
         │  Deliverable: CORE enforcement + discrete baseline simulator
         │  Gate: No CORE violations, baseline compaction works
         │
Week 6  ─┼─ MILESTONE 3: Experiment 4 Infrastructure Ready
         │  Deliverable: SWE-bench Extended task loader + harness
         │  Gate: End-to-end test with mock agent successful
         │
Week 8  ─┼─ MILESTONE 4: Primary Experiment Complete (CRITICAL)
         │  Deliverable: Experiment 4 results with comparative analysis
         │  Gate: Results meet ≥2 of 3 acceptance criteria
         │  Decision: Go/No-go for continuing Phase I
         │
Week 10 ─┼─ MILESTONE 5: All Experiments Complete
         │  Deliverable: Experiments 1-4 all executed and analyzed
         │  Gate: All acceptance criteria assessed
         │
Week 12 ─┼─ MILESTONE 6: Phase I Complete
         │  Deliverable: Technical report + finalized repository
         │  Gate: Phase II decision made
         │
Week 12 ─┴─ PROJECT CLOSURE
```

### Go/No-Go Decision Gates

#### Gate 1: End of Sprint 2 (Week 4)
**Decision:** Proceed to Experiment 4 infrastructure?

**Criteria:**
- [ ] Adaptive rate functional and tested
- [ ] CORE budget never violated in any test
- [ ] Discrete baseline compaction working
- [ ] All Sprint 1-2 tests passing

**Risk:** If CORE budget enforcement unreliable, must fix before proceeding

**Contingency:** Extend Sprint 2 by 2-3 days if critical bugs found

---

#### Gate 2: End of Sprint 4 (Week 8) - **CRITICAL GATE**
**Decision:** Continue Phase I to completion?

**Criteria:**
- [ ] Experiment 4 executed successfully (all 100 task runs)
- [ ] Results meet ≥2 of 3 acceptance criteria:
  - Task completion ≥90% of baseline
  - Spec adherence ≥95% of baseline
  - Code quality ≥ baseline
- [ ] No systematic algorithm failures

**Outcomes:**

**GO:** Results promising → Continue to Sprints 5-6
- Complete remaining experiments
- Proceed to technical report
- Prepare Phase II recommendation

**ITERATE:** Results mixed → Pause and refine
- Analyze failure modes
- Adjust algorithm parameters
- Re-run Experiment 4 (2-3 week iteration)
- Reassess at new gate

**NO-GO:** Results clearly fail → Pivot or halt
- Document findings (negative results valid)
- Explore alternative approaches
- Consider fundamentally different strategy
- Prepare lessons-learned report

**Escalation:** Stakeholder review required if NO-GO

---

#### Gate 3: End of Sprint 6 (Week 12)
**Decision:** Proceed to Phase II?

**Criteria:**
- [ ] Phase I success criteria substantially met (§7.2 of spec)
- [ ] Technical report complete and reviewed
- [ ] Repository reproducible
- [ ] Clear Phase II scope defined

**Outcomes:**

**GO to Phase II:** Strong validation → Full production implementation
**ITERATE:** Moderate validation → Refine before Phase II
**RESEARCH ONLY:** Weak validation → Publish findings, defer production

---

### Key Deliverable Schedule

| Week | Deliverable | Type | Criticality |
|------|-------------|------|-------------|
| 2 | Adaptive pruning rate implementation | Code | P0 |
| 2 | Updated Experiment 1 results | Data | P0 |
| 4 | CORE budget enforcer | Code | P0 |
| 4 | Discrete compaction baseline | Code | P0 |
| 6 | SWE-bench Extended infrastructure | Code | P0 |
| 6 | 50 task conversation scripts | Data | P0 |
| 8 | **Experiment 4 complete results** | **Data** | **P0** |
| 8 | **Preliminary comparative analysis** | **Report** | **P0** |
| 10 | Experiments 2-3 results | Data | P1 |
| 10 | Comprehensive metrics analysis | Report | P1 |
| 12 | **Technical research report** | **Document** | **P1** |
| 12 | **Finalized open-source repository** | **Code** | **P1** |
| 12 | Phase II decision document | Document | P1 |

---

## Risk Management

### Risk Register

| ID | Risk | Category | Probability | Impact | Priority | Owner | Mitigation Strategy | Contingency Plan |
|----|------|----------|-------------|--------|----------|-------|---------------------|------------------|
| R1 | Adaptive rate formula doesn't converge as expected | Technical | Medium | High | Critical | Developer | Empirically validate thresholds early (Sprint 1), adjust parameters iteratively | Fall back to simpler fixed-rate model if necessary, document limitations |
| R2 | Experiment 4 results don't meet acceptance criteria | Validation | Medium | Critical | Critical | Developer | Thorough testing in Sprints 1-3, pilot with 5 tasks before full run | Iterate on algorithm (2-3 weeks), reassess, or pivot approach |
| R3 | LLM API failures during critical experiments | Infrastructure | Medium | High | High | Developer | Robust retry logic, checkpointing every 5 tasks, backup API provider | Resume from checkpoints, extend timeline 2-3 days if needed |
| R4 | SWE-bench tasks too complex to extend to multi-turn | Design | Medium | High | High | Developer | Validate approach with 3 pilot tasks (Sprint 3), iterate on script templates | Simplify conversation scripts, reduce turn count target to 10-15 |
| R5 | CORE budget violations occur | Technical | Low | Critical | Critical | Developer | Comprehensive testing (Sprint 2), buffer testing (Sprint 3-5) | Emergency fix required, may delay sprint by 1-2 days |
| R6 | Token estimation accuracy too low (<80% within ±20%) | Technical | Medium | Low | Medium | Developer | Track accuracy from Sprint 2, upgrade to tiktoken if needed | Document limitation, acceptable for Phase I validation |
| R7 | Code quality metrics too subjective/unreliable | Methodology | Medium | Medium | Medium | Developer | Add automated checks (linters), manual review of samples | Rely more on objective metrics (test pass rate), document limitation |
| R8 | Single developer illness/unavailability | Resource | Low | Medium | Medium | N/A | Cross-train stakeholder on critical paths, document thoroughly | Extend timeline 1 week per week unavailable, prioritize critical path |
| R9 | API costs exceed budget | Financial | Low | Low | Low | Developer | Use Sonnet instead of Opus, monitor costs continuously | Request additional $25 budget, reduce task count to 30 if necessary |
| R10 | Reproducibility issues discovered late (Sprint 6) | Quality | Low | Medium | Medium | Developer | Test reproducibility continuously, maintain clean environments | Allocate 3-5 extra days in Sprint 6 for debugging |
| R11 | Time insufficient for quality technical report | Schedule | Medium | Medium | Medium | Developer | Start writing early (Sprint 5), reuse analysis from prior sprints | Extend Sprint 6 by 2-3 days, deprioritize non-essential sections |
| R12 | Baseline doesn't accurately simulate discrete compaction | Methodology | Medium | High | High | Developer | Validate against known compaction behaviors, adjust rules empirically | Implement LLM-based baseline (3-5 days extra), increase budget |
| R13 | Experiments not statistically significant (n=50 too small) | Methodology | Low | Medium | Low | Developer | Use appropriate statistical tests, document power analysis | Expand to 100 tasks if time/budget allow (Sprint 5), or document limitation |
| R14 | Integration issues between components | Technical | Low | Medium | Medium | Developer | Integration tests at each sprint boundary, early integration | Debug and fix (1-3 days), may delay sprint |
| R15 | Scope creep from stakeholder requests | Management | Low | Low | Low | Developer | Clear Phase I scope defined, polite pushback to Phase II | Defer non-critical features, document for Phase II |

### Risk Mitigation by Sprint

**Sprint 1-2 (Foundation):**
- **Focus:** Technical correctness (R1, R5, R6)
- **Strategy:** Comprehensive unit testing, empirical validation early
- **Checkpoint:** Daily self-review of critical algorithm components

**Sprint 3 (Infrastructure):**
- **Focus:** Design validation (R4)
- **Strategy:** Pilot testing with sample tasks before full implementation
- **Checkpoint:** End-to-end test with 3 tasks

**Sprint 4 (Critical Experiment):**
- **Focus:** Validation success (R2, R3, R7)
- **Strategy:** Checkpointing, retry logic, pilot runs
- **Checkpoint:** Mid-sprint review after 25 tasks

**Sprint 5 (Additional Experiments):**
- **Focus:** Statistical validity (R13)
- **Strategy:** Appropriate statistical tests, consider expansion if time allows
- **Checkpoint:** Cross-experiment consistency check

**Sprint 6 (Reporting):**
- **Focus:** Quality and reproducibility (R10, R11)
- **Strategy:** Start writing early, continuous reproducibility testing
- **Checkpoint:** Draft review at day 3 of sprint

### Escalation Path

**Level 1 - Developer Decision:**
- Minor technical issues
- Schedule adjustments <2 days
- Tool/library selection

**Level 2 - Stakeholder Consultation:**
- Major technical pivots (e.g., R2 contingency)
- Budget increases >$25
- Timeline extensions >1 week
- Scope changes

**Level 3 - Project Re-evaluation:**
- Phase I cancellation consideration
- Fundamental approach change
- Resource allocation changes

---

## Success Metrics

### Phase I Success Criteria

Based on Technical Specification §7.2, Phase I is successful if the following criteria are met:

### 1. Context Stability (Experiments 1 & 2)

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| Linear growth coefficient | \|slope\| < 0.01 | Regression analysis over 500 interactions | P0 |
| Steady-state oscillation | σ < 15% of target | Standard deviation after convergence | P0 |
| Maximum utilization | <60% of target at all times | Max token count / target capacity | P0 |
| Convergence time | <30 interactions from any start | Iterations until σ stabilizes | P0 |

**Pass Criteria:** ALL four metrics must meet targets

---

### 2. Information Preservation (Experiment 3)

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| Continuous pruning CORE recall | >90% (score ≥4.5/5) | Average recall score for 10 decisions | P1 |
| Discrete baseline recall | <70% (demonstrates degradation) | Average recall score for 10 decisions | P1 |
| Relative improvement | ≥25% better for continuous | (Continuous - Discrete) / Discrete | P1 |

**Pass Criteria:** ALL three metrics must meet targets

---

### 3. Code Quality (Experiment 4) - PRIMARY VALIDATION

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| Task completion rate | ≥90% of discrete baseline | % tests passed (continuous / baseline) | P0 |
| Specification adherence | ≥95% of discrete baseline | % requirements met (continuous / baseline) | P0 |
| Code quality score | ≥ discrete baseline | Rubric score (continuous vs. baseline) | P0 |
| Implementation consistency | Score ≥4.0/5.0 | Consistency metric across turns | P1 |

**Pass Criteria:** At least **2 of 3 PRIMARY metrics** (completion, adherence, quality) must meet targets

---

### 4. System Integrity

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| CORE budget violations | 0 violations | Count of times CORE >25% budget | P0 |
| Adaptive rate correctness | 100% correct behavior | Validation against formula §2.2.2 | P0 |
| Token estimation accuracy | Mean error ≤20%, 80%+ within ±20% | TokenEstimationMetrics | P1 |
| Unprunable fallback | Triggers correctly, system continues | Test with forced unprunable states | P1 |

**Pass Criteria:** ALL P0 metrics must pass, ≥1 P1 metric should pass

---

### Composite Success Score

**Overall Phase I Success:**

```
Total Points Possible: 15
- Context Stability (4 metrics × 1 point each) = 4 points
- Information Preservation (3 metrics × 1 point each) = 3 points
- Code Quality (4 metrics × 1.5 points each) = 6 points [weighted higher]
- System Integrity (2 P0 metrics × 1 point each) = 2 points

Success Thresholds:
- COMPLETE SUCCESS: ≥13 points (≥87%)
- PARTIAL SUCCESS: 10-12 points (67-80%)
- NEEDS ITERATION: 7-9 points (47-60%)
- FAILED: <7 points (<47%)
```

**Decision Matrix:**

| Score | Outcome | Action |
|-------|---------|--------|
| ≥13 points | Complete Success | Proceed to Phase II with confidence |
| 10-12 points | Partial Success | Proceed to Phase II with noted limitations |
| 7-9 points | Needs Iteration | Refine algorithm, re-test (2-4 weeks) |
| <7 points | Failed | Pivot to alternative approach or halt |

---

### Tracking & Reporting

**Metrics Dashboard (Updated Weekly):**

```
┌─────────────────────────────────────────────────────┐
│ Phase I Success Metrics Dashboard                  │
├─────────────────────────────────────────────────────┤
│ Context Stability:              [█████████░] 3/4    │
│ Information Preservation:       [██████████] 3/3    │
│ Code Quality (PRIMARY):         [████████░░] 4/6    │
│ System Integrity:               [██████████] 2/2    │
├─────────────────────────────────────────────────────┤
│ TOTAL SCORE:                    12/15 (80%)         │
│ STATUS:                         PARTIAL SUCCESS     │
│ RECOMMENDATION:                 PROCEED TO PHASE II │
└─────────────────────────────────────────────────────┘
```

**Reporting Frequency:**
- Sprint demos: High-level progress on success metrics
- Weekly updates: Detailed metrics tracking
- Gate reviews: Full assessment against criteria
- Final report: Comprehensive scoring with evidence

---

## Appendix: Gantt Chart

### Text-Based Gantt Chart

```
CONTEXT PRUNING LAB - PHASE I IMPLEMENTATION GANTT CHART
═══════════════════════════════════════════════════════════════════════════════

Sprint 1: Foundation - Adaptive Pruning (Weeks 1-2)
────────────────────────────────────────────────────────────────────────────────
Week 1    │████████████████████████│
          │ T1.1 Adaptive Rate     │
          │ T1.2 Integration       │
          │ T1.3 Unit Tests        ├──────────────────────────────────────────┐
Week 2    │████████████████████████│                                          │
          │ T1.4 Update Exp 1      │                                          │
          │ T1.5 Validation        │                                          │
          │ T1.6 Documentation     │                                          │
          └────────────────────────┘                                          │
                    ▼                                                          │
             MILESTONE 1: Adaptive Pruning Complete                           │
                                                                               │
Sprint 2: Baseline & CORE Budget (Weeks 3-4)                                  │
────────────────────────────────────────────────────────────────────────────── │
Week 3    │████████████████████████│                                          │
          │ T2.1 CORE Enforcer     │◄─────────────────────────────────────────┘
          │ T2.2 Integration       │
          │ T2.4 Discrete Baseline │
Week 4    │████████████████████████│
          │ T2.3 Unprunable        │
          │ T2.5 Baseline Tests    │
          │ T2.6 Token Estimation  │
          │ T2.7 Integration Tests │
          └────────────────────────┘
                    ▼
             MILESTONE 2: CORE Budget & Baseline Complete
                    ▼
              ┌──────────┐
              │ GATE 1   │ Continue to Experiment 4 Infrastructure?
              └──────────┘
                    ▼

Sprint 3: Experiment 4 Infrastructure (Weeks 5-6)
────────────────────────────────────────────────────────────────────────────────
Week 5    │████████████████████████│
          │ T3.1 Task Selection    │
          │ T3.2 Script Generator  │
Week 6    │████████████████████████│
          │ T3.3 Task Loader       │
          │ T3.4 Test Harness      │
          │ T3.5 Mock Agent        │
          │ T3.6 E2E Test          │
          │ T3.7 Documentation     │
          └────────────────────────┘
                    ▼
             MILESTONE 3: Experiment 4 Infrastructure Ready

Sprint 4: Code Quality Experiment (Weeks 7-8) ★ CRITICAL ★
────────────────────────────────────────────────────────────────────────────────
Week 7    │████████████████████████│
          │ T4.1 Quality Metrics   │
          │ T4.2 Real Agent        │
          │ T4.3 Experiment 4 Impl │
Week 8    │████████████████████████│
          │ T4.4 Execute: Cont.    │ ← 50 tasks, continuous pruning
          │ T4.5 Execute: Baseline │ ← 50 tasks, discrete baseline
          │ T4.6 Preliminary Anal. │
          │ T4.7 Documentation     │
          └────────────────────────┘
                    ▼
             MILESTONE 4: Primary Experiment Complete
                    ▼
              ┌──────────┐
              │ GATE 2   │ ★ CRITICAL DECISION POINT ★
              │CRITICAL! │ Continue Phase I? Iterate? Pivot?
              └──────────┘
                    ▼

Sprint 5: Additional Experiments & Metrics (Weeks 9-10)
────────────────────────────────────────────────────────────────────────────────
Week 9    │████████████████████████│
          │ T5.1 Implement Exp 2   │
          │ T5.2 Execute Exp 2     │
          │ T5.3 Implement Exp 3   │
Week 10   │████████████████████████│
          │ T5.4 Execute Exp 3     │
          │ T5.5 Metrics Harness   │
          │ T5.6 Cross-Exp Analysis│
          │ T5.7 Documentation     │
          └────────────────────────┘
                    ▼
             MILESTONE 5: All Experiments Complete

Sprint 6: Analysis & Reporting (Weeks 11-12)
────────────────────────────────────────────────────────────────────────────────
Week 11   │████████████████████████│
          │ T6.1 Final Validation  │
          │ T6.2 Report Draft      │
          │ T6.3 Report Revision   │
Week 12   │████████████████████████│
          │ T6.4 Repo Finalization │
          │ T6.5 Reproducibility   │
          │ T6.6 Phase II Decision │
          │ T6.7 Presentation      │
          │ T6.8 Project Closure   │
          └────────────────────────┘
                    ▼
             MILESTONE 6: Phase I Complete
                    ▼
              ┌──────────┐
              │ GATE 3   │ Proceed to Phase II?
              └──────────┘
                    ▼
              PROJECT CLOSURE


CRITICAL PATH (⬛ = critical, □ = non-critical):
═══════════════════════════════════════════════════════════════════════════════

Weeks:     1    2    3    4    5    6    7    8    9   10   11   12
           ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
Adaptive   ⬛⬛⬛⬛
CORE             ⬛⬛⬛⬛
SWE Infra            ⬛⬛⬛⬛
Exp 4                    ⬛⬛⬛⬛⬛⬛⬛⬛
Exp 2-3                          □□□□
Analysis                              ⬛⬛⬛⬛
Report                                    ⬛⬛⬛⬛

LEGEND:
═══════════════════════════════════════════════════════════════════════════════
⬛ = Critical path task (delays impact project completion)
□ = Important but not on critical path
★ = Critical decision gate
▼ = Milestone
```

### Dependency Flow Diagram

```
                          PHASE I DEPENDENCY FLOW
                          ═══════════════════════

      SPRINT 1              SPRINT 2              SPRINT 3
   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
   │  Adaptive    │───▶│ CORE Budget  │    │ SWE Task     │
   │  Pruning     │    │  Enforcer    │    │  Selection   │
   │  Rate        │    └──────┬───────┘    └──────┬───────┘
   └──────┬───────┘           │                   │
          │                   │                   ▼
          │                   │            ┌──────────────┐
          │                   │            │ Script       │
          │                   │            │  Generator   │
          │                   │            └──────┬───────┘
          │                   │                   │
          │                   ▼                   ▼
          │            ┌──────────────┐    ┌──────────────┐
          │            │  Discrete    │    │ Task Loader  │
          │            │  Baseline    │    └──────┬───────┘
          │            └──────┬───────┘           │
          │                   │                   ▼
          │                   │            ┌──────────────┐
          │                   │            │ Test         │
          │                   │            │  Harness     │
          │                   │            └──────┬───────┘
          │                   │                   │
          └───────────────────┴───────────────────┘
                              │
                              ▼
      ┌───────────────────────────────────────────────┐
      │           SPRINT 4: EXPERIMENT 4               │
      │                                                │
      │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
      │  │ Quality  │  │   Real   │  │ Execute  │   │
      │  │ Metrics  │  │  Agent   │  │ Tasks    │   │
      │  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
      │       └─────────────┼─────────────┘         │
      │                     ▼                         │
      │           ┌──────────────────┐               │
      │           │ Comparative      │               │
      │           │ Analysis         │               │
      │           └────────┬─────────┘               │
      └────────────────────┼───────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
      ┌──────────────┐          ┌──────────────┐
      │ SPRINT 5     │          │ SPRINT 6     │
      │ Exp 2-3      │          │ Technical    │
      │ Metrics      │──────────▶ Report       │
      └──────────────┘          │ Repository   │
                                │ Phase II Dec │
                                └──────────────┘
```

---

## Appendix: Risk Heatmap

```
RISK IMPACT vs. PROBABILITY MATRIX
═══════════════════════════════════════════════════════════════════

           PROBABILITY
           │
    High   │                    R2 ★
           │         R3
           │                    R4
           │                    R12
  IMPACT   │
           │  R6    R7    R8    R13   R14
    Medium │         R9    R10   R11
           │
           │                    R1 ★
     Low   │  R15               R5 ★
           │
           └─────────────────────────────────────────
              Low      Medium      High
                   PROBABILITY

LEGEND:
═══════════════════════════════════════════════════════════════════
★ = Critical risk requiring proactive mitigation
R# = Risk ID (see Risk Register for details)

HIGH PRIORITY RISKS (Top Right Quadrant):
  R1  - Adaptive rate convergence issues
  R2  - Experiment 4 results don't meet criteria (CRITICAL)
  R3  - LLM API failures
  R4  - SWE-bench task extension complexity
  R5  - CORE budget violations (CRITICAL - must not occur)
  R12 - Baseline accuracy

MONITOR RISKS (Middle):
  R7  - Code quality metric reliability
  R8  - Developer unavailability
  R11 - Technical report time
  R13 - Statistical significance
  R14 - Integration issues

LOW PRIORITY RISKS (Bottom/Left):
  R6  - Token estimation accuracy
  R9  - API cost overrun
  R10 - Reproducibility issues
  R15 - Scope creep
```

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-29 | Initial implementation workflow document created | Research Team |

---

**END OF IMPLEMENTATION WORKFLOW DOCUMENT**

**Next Actions:**
1. Review this workflow with stakeholders
2. Confirm resource availability and timeline
3. Set up project tracking (GitHub Projects, Jira, or similar)
4. Begin Sprint 1 implementation
5. Schedule weekly sprint reviews
6. Establish communication channels for blockers/questions

**Contact:**
For questions about this implementation plan, contact the research team.

---

*This document is a living document and will be updated as the project progresses. All stakeholders will be notified of material changes.*
