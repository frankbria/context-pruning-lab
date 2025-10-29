# Technical Specification: Continuous Context Pruning for AI Coding Agents

**Version:** 1.0
**Date:** 2025-10-29
**Status:** Phase I - Concept Validation
**Authors:** Context Pruning Research Team

---

## Executive Summary

### Problem Statement

Current AI coding agents suffer from a critical limitation: traditional discrete compaction strategies cause progressive degradation in agent performance. When context windows approach capacity (~80-90% full), systems perform catastrophic compression—typically reducing context to 30% of capacity—which results in:

1. **Information loss**: Critical decision rationale and architectural context are discarded
2. **Performance degradation**: Agents become progressively "dumb" after 2-3 compaction cycles
3. **Conversation discontinuity**: Users experience jarring resets when context is compressed
4. **Inevitable failure**: Linear context growth eventually exceeds available capacity

This fundamental limitation constrains the effectiveness of AI coding agents on extended, complex software development tasks.

### Hypothesis

**Continuous importance-based pruning after every interaction can maintain context more effectively than discrete compaction, enabling sustained high-quality code generation over extended development sessions.**

Specifically, we hypothesize that by:
- Removing approximately 110% of newly added content after each interaction (via adaptive pruning rate)
- Preserving critical information in an immutable CORE tier (≤25% of target capacity)
- Using multi-factor importance scoring to guide pruning decisions

We can achieve:
- **Steady-state context stability** (oscillation within 20-40% of target capacity)
- **Zero linear growth** (context does not accumulate indefinitely)
- **Superior information preservation** (90%+ retention of critical decisions vs. 60% for discrete compaction)
- **Better code quality** (measured via specification adherence and functional correctness)

### Research Scope

This specification defines **Phase I: Concept Validation**—a research experiment to prove the feasibility and comparative advantage of continuous pruning. This is explicitly **not** a production implementation. Production concerns (MCP server integration, adversarial testing, full conversation coherence) are deferred to Phase II.

**Success Criteria for Phase I:**
- Demonstrate continuous pruning maintains stable context (no linear growth)
- Prove it preserves information better than discrete compaction baseline
- Show equal or better code generation quality on benchmark tasks
- Validate adaptive pruning rate mechanism functions correctly

---

## 1. Background & Motivation

### 1.1 The Context Management Problem

AI coding agents operate within fixed context windows (typically 100K-200K tokens). During extended development sessions, context accumulates from:
- User messages and agent responses
- File contents and code snippets
- Tool outputs and error logs
- Decision rationale and architectural notes

Traditional chat-based systems employ **discrete compaction**: wait until context is ~80% full, then compress to ~30% capacity via lossy summarization. This approach has fundamental flaws:

**Timing Issues:**
- Binary threshold creates "cliff effect" when capacity is reached
- No graceful degradation before compaction event
- Post-compaction, context grows linearly again until next crisis

**Information Loss:**
- Batch compression lacks granular importance assessment
- Critical rationale often lost in favor of recent content
- No mechanism to protect truly essential information
- Accumulated degradation across multiple compaction cycles

**User Experience:**
- Conversation appears to "restart" after compaction
- Agent "forgets" earlier decisions and context
- Users must repeatedly re-establish context
- Reduced trust in agent reliability over time

### 1.2 Why This Matters for AI Coding Agents

Unlike general conversational AI, coding agents require:

1. **Long-term context coherence**: Multi-day development sessions with consistent architectural understanding
2. **Decision rationale preservation**: Understanding *why* choices were made, not just *what* was implemented
3. **Specification adherence**: Maintaining alignment with requirements over extended implementation
4. **Code quality maintenance**: Consistent patterns, conventions, and quality standards
5. **Cross-session learning**: Ability to reference and build upon earlier work

Current context management strategies fail these requirements, limiting agent effectiveness on real-world software development tasks.

### 1.3 Continuous Pruning Approach

Instead of crisis-driven batch compaction, continuous pruning applies a fundamentally different strategy:

**After every interaction:**
1. Add new content (user message + agent response + any tool outputs)
2. Calculate importance scores for **all** context items using multi-factor analysis
3. Remove lowest-scored content equal to ~110% of what was just added
4. Result: Context size oscillates in steady state, never accumulates linearly

**Key Mechanisms:**

- **Adaptive Pruning Rate**: Target removal ranges from 90-110% of added content, adjusted based on current context utilization
- **CORE Tier Protection**: Critical information (≤25% of target capacity) is never pruned
- **Multi-Factor Scoring**: Combines recency, access frequency, type importance, and manual pinning
- **Graceful Archival**: Pruned items can be archived for potential retrieval (WARM/COLD tiers)

This approach promises steady-state operation without catastrophic information loss.

---

## 2. System Architecture

### 2.1 Four-Tier Context Hierarchy

```
┌─────────────────────────────────────────┐
│ CORE TIER (Immutable, ≤25% of target)  │
│ • Critical decisions with rationale     │
│ • Architectural choices                 │
│ • Security constraints                  │
│ • Project requirements                  │
│ • Never pruned, always in context       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ HOT TIER (Active working context)      │
│ • Recent messages (last 5-10 turns)     │
│ • Current task context                  │
│ • Active file contents                  │
│ • Continuous importance-based pruning   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ WARM TIER (Queryable archive)          │
│ • Pruned items of medium importance     │
│ • Load on semantic search/explicit ref  │
│ • Phase I: Simulated (not implemented)  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ COLD TIER (Long-term storage)          │
│ • Low-importance pruned items           │
│ • Rarely accessed                       │
│ • Phase I: Simulated (not implemented)  │
└─────────────────────────────────────────┘
```

**Phase I Implementation Notes:**
- Only CORE and HOT tiers are actively implemented
- WARM/COLD tiers are simulated (items marked but not actually stored/retrieved)
- This is sufficient for validating core hypothesis

### 2.2 Adaptive Pruning Algorithm

#### 2.2.1 Core Algorithm

```python
def prune_after_interaction(new_content: List[ContextItem]) -> PruningMetrics:
    """Execute continuous pruning after adding new interaction content"""

    # 1. Calculate tokens added
    tokens_added = sum(item.token_count for item in new_content)

    # 2. Add new content to context
    context.extend(new_content)

    # 3. Update importance scores for ALL items
    for item in context:
        item.importance = calculate_importance(item)

    # 4. Calculate adaptive pruning target
    pruning_rate = calculate_adaptive_rate(
        current_utilization=get_total_tokens() / target_size,
        core_utilization=get_core_tokens() / core_budget
    )
    target_prune_tokens = int(tokens_added * pruning_rate)

    # 5. Remove lowest-scored items (excluding CORE tier)
    removed_tokens, removed_items = prune_lowest_scored(
        target_tokens=target_prune_tokens,
        exclude_core=True
    )

    # 6. Return metrics
    return PruningMetrics(
        tokens_added=tokens_added,
        tokens_removed=removed_tokens,
        items_removed=removed_items,
        current_tokens=get_total_tokens(),
        pruning_rate_used=pruning_rate
    )
```

#### 2.2.2 Adaptive Pruning Rate Formula

The pruning rate is **not** hard-coded at 110%. It adjusts dynamically based on system state:

```python
def calculate_adaptive_rate(current_utilization: float, core_utilization: float) -> float:
    """
    Calculate adaptive pruning rate (0.90 - 1.10)

    Factors:
    - Current utilization: Higher usage → more aggressive pruning
    - CORE budget pressure: More CORE content → more aggressive HOT pruning
    - Lower bound: 0.90 (remove 90% of added, allows slight growth)
    - Upper bound: 1.10 (remove 110% of added, forces shrinkage)
    """

    base_rate = 1.10  # Default: slight shrinkage

    # Adjust based on current utilization
    if current_utilization < 0.20:
        # Very low utilization: allow growth
        utilization_adjustment = -0.15
    elif current_utilization < 0.30:
        # Low utilization: minimal pruning
        utilization_adjustment = -0.10
    elif current_utilization < 0.50:
        # Target range: standard pruning
        utilization_adjustment = 0.0
    elif current_utilization < 0.70:
        # High utilization: more aggressive
        utilization_adjustment = +0.05
    else:
        # Very high: maximum pruning
        utilization_adjustment = +0.10

    # Adjust based on CORE budget pressure
    if core_utilization > 0.25:
        # CORE tier exceeds budget: prune HOT more aggressively
        core_adjustment = +0.05
    else:
        core_adjustment = 0.0

    # Calculate final rate
    final_rate = base_rate + utilization_adjustment + core_adjustment

    # Enforce bounds
    return max(0.90, min(1.10, final_rate))
```

**Rationale:**
- When context is nearly empty, allow modest growth (90% pruning)
- When context is full, force shrinkage (110% pruning)
- When CORE budget is exceeded, compensate by pruning HOT more aggressively
- This creates a self-regulating system that maintains steady state

#### 2.2.3 Importance Scoring

Each context item receives an importance score (0.0-1.0) calculated from multiple factors:

```python
def calculate_importance(item: ContextItem) -> float:
    """
    Multi-factor importance scoring

    Weights:
    - Recency: 40% (exponential decay, half-life = 10 interactions)
    - Access frequency: 20% (how often item is referenced)
    - Item type: 30% (intrinsic importance by category)
    - Manual pins: 10% (user/agent explicit marking)
    """

    # CORE tier items always score 1.0
    if item.tier == "CORE" or item.pinned:
        return 1.0

    # Calculate age in interactions
    age = current_interaction - item.interaction_number

    # Recency score (exponential decay)
    recency_score = exp(-age / 10)  # Half-life of 10 interactions

    # Access frequency score (capped at 0.3)
    access_score = min(item.access_count * 0.05, 0.3)

    # Type-based score
    type_score = TYPE_WEIGHTS.get(item.item_type, 0.5)

    # Weighted combination
    final_score = (
        recency_score * 0.4 +
        access_score * 0.2 +
        type_score * 0.3 +
        (0.1 if item.pinned else 0.0)
    )

    return min(final_score, 1.0)
```

**Type Importance Weights:**

```python
TYPE_WEIGHTS = {
    # CORE-tier types (auto-assigned to CORE)
    'core_decision': 1.00,
    'architecture': 0.95,
    'requirement': 0.95,
    'constraint': 0.95,

    # High-value types
    'security_note': 0.90,
    'api_contract': 0.85,
    'user_message': 0.70,
    'agent_response': 0.65,
    'code_snippet': 0.60,

    # Medium-value types
    'test_result': 0.50,
    'file_content': 0.45,

    # Low-value types
    'debug_log': 0.30,
    'trace': 0.20,
    'informational': 0.15
}
```

### 2.3 CORE Budget Enforcement

The CORE tier must never exceed 25% of target context capacity. This is a **hard constraint**.

#### 2.3.1 CORE Budget Management

```python
class CoreBudgetEnforcer:
    """Ensures CORE tier never exceeds budget"""

    def __init__(self, target_size: int):
        self.core_budget = int(target_size * 0.25)
        self.core_tokens = 0

    def can_add_to_core(self, item: ContextItem) -> bool:
        """Check if item can be added to CORE without exceeding budget"""
        return (self.core_tokens + item.token_count) <= self.core_budget

    def add_to_core(self, item: ContextItem) -> bool:
        """
        Attempt to add item to CORE tier

        Returns: True if added, False if budget exceeded
        """
        if self.can_add_to_core(item):
            self.core_tokens += item.token_count
            item.tier = "CORE"
            item.importance = 1.0
            return True
        else:
            # Budget exceeded: keep in HOT tier with high importance
            item.tier = "HOT"
            item.importance = 0.95
            return False

    def remove_from_core(self, item: ContextItem):
        """Remove item from CORE (only via explicit user/agent action)"""
        if item.tier == "CORE":
            self.core_tokens -= item.token_count
            item.tier = "HOT"
```

#### 2.3.2 Fallback Behavior When CORE Budget Exceeded

When CORE tier exceeds budget (e.g., user adds excessive core decisions):

1. **Warning**: Log warning that CORE budget is exceeded
2. **Overflow to HOT**: New items marked for CORE are added to HOT with importance=0.95
3. **Increased HOT Pruning**: Adaptive rate increases to compensate (see §2.2.2)
4. **User Notification** (Phase II): Inform user that CORE is full, suggest consolidation

**Phase I Behavior:**
- Simply prevent CORE additions when budget exceeded
- Add to HOT with high importance instead
- Log event for analysis

### 2.4 Unprunable State Fallback

**Problem**: If too much content is marked CORE or pinned, pruning may fail to remove sufficient tokens.

**Detection:**
```python
def check_unprunable_state() -> bool:
    """Check if context is in unprunable state"""
    prunable_tokens = sum(
        item.token_count
        for item in context
        if item.tier != "CORE" and not item.pinned
    )

    # Unprunable if <10% of context can be pruned
    return prunable_tokens < (target_size * 0.10)
```

**Fallback Strategy:**

1. **Force-unpin low-importance HOT items**:
   - Identify lowest-scored HOT tier items
   - Temporarily override importance scores to allow pruning
   - Target: create at least 15% prunable headroom

2. **Reject new content** (Phase II):
   - Refuse to add new interactions until space is available
   - Prompt user to consolidate CORE or unpin items

3. **Emergency CORE consolidation** (Phase II):
   - Invoke LLM to summarize CORE tier items
   - Compress CORE to 15% of budget
   - Risky: potential information loss

**Phase I Behavior:**
- Detect unprunable state and log warning
- Force-unpin lowest 20% of HOT items if needed
- Continue operation (don't fail completely)

### 2.5 Token Estimation

#### 2.5.1 Token Counting Strategy

**Phase I (Concept Validation):**
- Use simple heuristic: `tokens ≈ characters / 4`
- Fast, deterministic, "good enough" for validation
- Expected accuracy: ±20% (acceptable for concept testing)

**Phase II (Production):**
- Integrate actual tokenizer (tiktoken for Claude)
- Measure true token counts
- Target accuracy: ±5%

#### 2.5.2 Token Estimation Accuracy Measurement

Track estimation error during experiments:

```python
class TokenEstimationMetrics:
    def __init__(self):
        self.estimates = []
        self.actuals = []

    def record(self, estimated: int, actual: int):
        self.estimates.append(estimated)
        self.actuals.append(actual)

    def get_accuracy(self) -> dict:
        errors = [
            abs(est - act) / act
            for est, act in zip(self.estimates, self.actuals)
        ]
        return {
            'mean_error': mean(errors),
            'max_error': max(errors),
            'within_20pct': sum(1 for e in errors if e < 0.20) / len(errors)
        }
```

**Acceptance Criteria (Phase I):**
- Mean error ≤ 20%
- Max error ≤ 40%
- 80%+ of estimates within ±20% of actual

---

## 3. Baseline Comparison: Discrete Compaction Simulator

To validate that continuous pruning is **better** than existing approaches, we must implement a realistic baseline that simulates current state-of-the-art discrete compaction.

### 3.1 Discrete Compaction Strategy (Status Quo)

**Current Behavior (e.g., Claude Code):**

1. **Wait until context is ~80-90% full** (panic threshold)
2. **Compress to ~30% capacity** via lossy summarization
3. **Resume linear growth** until next compaction event
4. **Repeat** until degradation becomes unacceptable

### 3.2 Baseline Simulator Design

#### 3.2.1 Phase I: Rule-Based Compression

For concept validation, implement a **rule-based compaction simulator** that mimics discrete compaction without LLM invocation:

```python
class DiscreteCompactionBaseline:
    """Simulates traditional discrete compaction strategy"""

    def __init__(self, target_size: int):
        self.target_size = target_size
        self.compaction_threshold = 0.80  # Compact at 80% full
        self.compaction_target = 0.30     # Compress to 30%
        self.context = []

    def add_interaction(self, user_msg: str, agent_msg: str):
        """Add interaction; compact if threshold exceeded"""

        # Add new content
        self.context.append(ContextItem(user_msg, 'user_message'))
        self.context.append(ContextItem(agent_msg, 'agent_response'))

        # Check if compaction needed
        current_tokens = self.get_total_tokens()
        if current_tokens >= (self.target_size * self.compaction_threshold):
            self.perform_compaction()

    def perform_compaction(self):
        """
        Rule-based compaction (Phase I)

        Strategy:
        1. Keep most recent N interactions fully
        2. Summarize older interactions (lossy)
        3. Compress to 30% of target capacity
        """

        target_tokens = int(self.target_size * self.compaction_target)

        # Keep most recent 5 interactions fully
        recent_items = self.context[-10:]  # Last 5 user+agent pairs
        recent_tokens = sum(item.token_count for item in recent_items)

        # Budget for summarized older content
        summary_budget = target_tokens - recent_tokens

        # Simulate lossy summarization of older content
        # Rule: Keep 20% of older items (highest importance)
        older_items = self.context[:-10]
        older_items.sort(key=lambda x: x.importance, reverse=True)

        keep_count = max(1, int(len(older_items) * 0.20))
        summarized_items = older_items[:keep_count]

        # Rebuild context
        self.context = summarized_items + recent_items

        # Mark event
        self.compaction_events.append({
            'interaction': self.interaction_count,
            'tokens_before': current_tokens,
            'tokens_after': self.get_total_tokens(),
            'items_removed': len(older_items) - keep_count
        })
```

**Rationale for Rule-Based Approach (Phase I):**
- Avoids LLM API costs during high-volume experiments
- Deterministic and reproducible
- "Good enough" to test hypothesis (continuous vs. discrete)
- Fast execution for large-scale benchmarking

#### 3.2.2 Phase II: LLM-Based Compression

For higher-fidelity comparison (Phase II), implement **actual LLM summarization**:

```python
def perform_llm_compaction(self):
    """LLM-based compaction (Phase II)"""

    # Separate recent (keep verbatim) from older (summarize)
    recent_items = self.context[-10:]
    older_items = self.context[:-10]

    # Invoke LLM to summarize older content
    summary = call_llm_summarization(
        items=older_items,
        target_tokens=int(self.target_size * 0.20),
        prompt="Summarize the following conversation history, "
               "preserving key decisions and context..."
    )

    # Rebuild context
    self.context = [
        ContextItem(content=summary, item_type='compaction_summary')
    ] + recent_items
```

### 3.3 Baseline Evaluation

Both continuous pruning and discrete compaction baseline will be evaluated on identical benchmarks (§5) using the same metrics (§4).

---

## 4. Evaluation Framework

### 4.1 Multi-Dimensional Scorecard

Evaluation across four dimensions:

```
┌──────────────────────────────────────────────────────┐
│ DIMENSION 1: Context Stability (System Health)       │
│ Metrics:                                             │
│ • Token count oscillation (σ after steady state)    │
│ • Linear growth coefficient                         │
│ • Maximum context utilization                       │
│ • Steady-state convergence time                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ DIMENSION 2: Information Preservation (Memory)       │
│ Metrics:                                             │
│ • CORE decision recall (% retrieved correctly)       │
│ • Rationale preservation (qualitative assessment)    │
│ • Cross-reference integrity                         │
│ • Temporal coherence (can trace decision history)   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ DIMENSION 3: Code Generation Quality (PRIMARY GOAL) │
│ Metrics:                                             │
│ • Specification adherence (% requirements met)       │
│ • Functional correctness (tests passed)             │
│ • Code quality (maintainability, conventions)       │
│ • Consistency over time                             │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ DIMENSION 4: Agent Performance (Practical Metrics)   │
│ Metrics:                                             │
│ • Task completion rate                              │
│ • Time to completion                                │
│ • Error recovery                                    │
│ • Context coherence (user satisfaction proxy)       │
└──────────────────────────────────────────────────────┘
```

### 4.2 Benchmark Selection

Based on research into coding agent benchmarks, we adapt **SWE-bench methodology** for context testing.

#### 4.2.1 Benchmark Requirements

Ideal benchmark for context pruning validation must have:

1. **Extended multi-turn interactions** (not single-shot)
2. **Specification complexity** requiring context retention
3. **Objective correctness criteria** (tests, requirements)
4. **Real-world relevance** to AI coding agent tasks

#### 4.2.2 Candidate Benchmarks (Research Findings)

**SWE-bench** ✅
- 2,294 real GitHub issues from 12 Python repos
- Requires understanding issue → implementing fix → passing tests
- Multi-turn capable: can extend to multi-step implementation
- **Adaptation needed**: Create extended conversations around issues

**HumanEval / MBPP** ❌
- Single-shot function generation only
- No multi-turn context
- Not suitable for context pruning validation

**DPAI Arena / Aider Polyglot** ❌
- Focuses on edit quality, not extended context
- Typically short interactions
- Not ideal for our use case

**DevAI Benchmark** ⚠️
- Claims multi-task scenarios
- Limited public availability
- Consider for Phase II

#### 4.2.3 Selected Approach: SWE-bench-Lite Extended

**Baseline**: SWE-bench-Lite (300 verified issues)

**Adaptation for Context Testing**:

1. **Extend issues to multi-turn conversations**:
   - Initial issue presentation
   - Clarification questions (simulated user responses)
   - Implementation steps (multiple iterations)
   - Test failures and refinements
   - Target: 15-30 interactions per issue

2. **Create "conversation scripts"**:
   ```python
   ISSUE_EXTENDED_SCRIPT = [
       ("user", "Here's the issue: {issue_description}"),
       ("agent", "{agent_understanding}"),
       ("user", "Please implement a fix"),
       ("agent", "{agent_implementation_plan}"),
       ("system", "{test_results}"),
       ("user", "Tests are failing, can you fix?"),
       # ... continue for 15-30 turns
   ]
   ```

3. **Inject context stress**:
   - Add related but not essential information
   - Include "noisy" context items (logs, traces)
   - Force context to exceed compaction threshold during task
   - Measure: Does agent maintain specification coherence?

4. **Evaluate on correctness**:
   - Final implementation must pass SWE-bench tests
   - Track: specification adherence throughout conversation
   - Measure: consistency of approach across turns

**Metrics from SWE-bench Extended**:
- **Task completion**: % issues resolved correctly
- **Specification adherence**: % requirements met during implementation
- **Context coherence**: Agent maintains consistent understanding
- **Error recovery**: Agent corrects mistakes based on earlier context

### 4.3 Measurement Instrumentation

#### 4.3.1 Automated Metrics Collection

```python
class EvaluationHarness:
    """Collects all evaluation metrics during benchmark runs"""

    def __init__(self):
        self.metrics = {
            'stability': StabilityMetrics(),
            'preservation': PreservationMetrics(),
            'code_quality': CodeQualityMetrics(),
            'performance': PerformanceMetrics()
        }

    def run_benchmark(self, strategy: ContextStrategy, benchmark: Benchmark):
        """Run full benchmark and collect all metrics"""

        for task in benchmark.tasks:
            # Execute task with given strategy
            result = execute_task(task, strategy)

            # Collect metrics
            self.metrics['stability'].record(result.context_stats)
            self.metrics['preservation'].record(result.recall_test)
            self.metrics['code_quality'].record(result.code_output)
            self.metrics['performance'].record(result.execution_stats)

        return self.aggregate_results()
```

#### 4.3.2 Qualitative Assessment

For subjective metrics (code quality, rationale preservation):

**Code Quality Rubric**:
- **Maintainability** (0-5): Clear naming, modularity, documentation
- **Convention adherence** (0-5): Follows language idioms, style guides
- **Completeness** (0-5): Handles edge cases, includes tests
- **Specification match** (0-5): Meets stated requirements

**Rationale Preservation Assessment**:
- Present agent with earlier decisions mid-conversation
- Ask: "Why did we choose approach X?"
- Evaluate: Correctness and completeness of explanation
- Score: 0-5 scale (5 = perfect recall, 0 = no memory)

---

## 5. Experimental Design

### 5.1 Experiment 1: Stability Validation (UPDATED)

**Status**: Exists, needs updates for adaptive pruning rate

**Hypothesis**: Continuous pruning maintains steady-state context with minimal oscillation and zero linear growth.

**Method**:
1. Run 500 interactions with continuous pruning (adaptive rate enabled)
2. Measure token count after each interaction
3. Calculate:
   - Linear growth coefficient (should be ~0)
   - Standard deviation after steady state (should be <15% of target)
   - Maximum utilization (should be <60% of target)
   - Time to steady state (interactions until σ stabilizes)

**Acceptance Criteria**:
- ✅ Linear growth coefficient: |slope| < 0.01
- ✅ Steady-state oscillation: σ < 15% of target size
- ✅ Max utilization: <60% of target at all times
- ✅ Convergence time: <20 interactions to steady state

**Implementation Updates Needed**:
- Update `experiment_1_linear_growth.py` to use adaptive pruning rate
- Add convergence time measurement
- Add pruning rate tracking (verify it adapts correctly)

---

### 5.2 Experiment 2: Steady-State Convergence (NEW)

**Hypothesis**: Adaptive pruning rate causes system to converge to stable equilibrium.

**Method**:
1. Initialize with varying context levels (0%, 20%, 50%, 80% full)
2. Run 100 interactions for each initial condition
3. Measure:
   - Time to reach steady state (σ stabilizes)
   - Final steady-state utilization
   - Pruning rate adjustments over time

**Expected Behavior**:
```
Initial State → Adaptive Behavior → Steady State
─────────────────────────────────────────────────
0% full       → pruning_rate=0.90 → converge to ~25%
20% full      → pruning_rate=0.95 → converge to ~25%
50% full      → pruning_rate=1.05 → converge to ~25%
80% full      → pruning_rate=1.10 → converge to ~25%
```

**Acceptance Criteria**:
- ✅ All initial conditions converge to 20-40% utilization
- ✅ Convergence time: <30 interactions from any starting point
- ✅ Pruning rate adapts correctly (verify formula from §2.2.2)

**Implementation**:
- Create `experiments/experiment_2_convergence.py`
- Test with 4 initial conditions
- Plot convergence trajectories

---

### 5.3 Experiment 3: Information Preservation (NEW)

**Hypothesis**: Continuous pruning preserves CORE decisions better than discrete compaction.

**Method**:
1. Define 10 "critical decisions" added to CORE at interaction 1-5
2. Run 100 interactions (exceeding multiple discrete compaction cycles)
3. At interaction 50 and 100, test recall:
   - Query agent about each critical decision
   - Measure: % recalled correctly, completeness of rationale

**Baselines**:
- **Continuous pruning**: CORE tier protected
- **Discrete compaction**: Rule-based compression (§3.2.1)

**Recall Assessment**:
```python
CRITICAL_DECISIONS = [
    "Use PostgreSQL for primary database",
    "Implement JWT authentication with 24h expiry",
    "Maximum API response time: 200ms",
    # ... 7 more
]

def test_recall(agent, decisions):
    """Test agent's recall of critical decisions"""
    scores = []
    for decision in decisions:
        response = agent.query(f"What did we decide about {decision.topic}?")
        score = assess_recall_quality(decision, response)  # 0-5
        scores.append(score)
    return mean(scores), scores
```

**Acceptance Criteria**:
- ✅ Continuous pruning: >90% recall accuracy (score ≥4.5/5)
- ✅ Discrete baseline: <70% recall accuracy (expected degradation)
- ✅ Relative improvement: ≥25% better recall for continuous pruning

**Implementation**:
- Create `experiments/experiment_3_preservation.py`
- Define decision set with ground truth
- Implement recall assessment scoring
- Compare continuous vs. discrete baseline

---

### 5.4 Experiment 4: Code Quality with Context Strategies (NEW, PRIMARY)

**Hypothesis**: Continuous pruning enables equal or better code generation quality compared to discrete compaction.

**Method**:
1. Select 50 tasks from SWE-bench-Lite Extended (§4.2.3)
2. Run each task with:
   - Continuous pruning (adaptive rate)
   - Discrete compaction baseline
   - No pruning (control, if context capacity allows)
3. Measure:
   - Task completion rate (tests passed)
   - Specification adherence score
   - Code quality score (rubric from §4.3.2)
   - Implementation consistency across turns

**Task Execution**:
```python
def run_code_quality_benchmark(task, strategy):
    """Execute SWE-bench task with given context strategy"""

    agent = CodingAgent(context_strategy=strategy)

    # Execute extended conversation (15-30 turns)
    for turn in task.conversation_script:
        if turn.is_user:
            agent.receive_message(turn.content)
        else:
            agent.generate_response()

    # Evaluate final output
    results = {
        'tests_passed': run_tests(agent.final_code, task.test_suite),
        'spec_adherence': check_requirements(agent.final_code, task.spec),
        'code_quality': assess_code_quality(agent.final_code),
        'consistency': measure_consistency(agent.conversation_history)
    }

    return results
```

**Acceptance Criteria**:
- ✅ Task completion: Continuous pruning ≥90% of discrete baseline rate
- ✅ Specification adherence: Continuous pruning ≥95% of discrete baseline
- ✅ Code quality: Continuous pruning ≥ discrete baseline (equal or better)
- ✅ **Primary Goal**: Demonstrates continuous pruning is **viable** for real coding tasks

**Implementation Priority**: **P0 (Critical)**
- Create `experiments/experiment_4_code_quality.py`
- Implement SWE-bench-Lite Extended task loader
- Integrate with coding agent test harness
- Implement all four quality metrics
- Run comparative analysis: continuous vs. discrete vs. control

---

## 6. Implementation Priorities

### 6.1 Priority Definitions

- **P0 (Critical)**: Required for Phase I validation; blocking for success
- **P1 (High)**: Important for complete validation; should be included
- **P2 (Medium)**: Enhances validation; nice to have
- **P3 (Low)**: Future work; defer to Phase II

### 6.2 Priority Breakdown

#### P0 (Critical - Phase I Blockers)

1. **Adaptive Pruning Rate Implementation**
   - Implement `calculate_adaptive_rate()` (§2.2.2)
   - Verify rate adjusts correctly based on utilization
   - Test: Convergence from different initial states

2. **CORE Budget Enforcement**
   - Implement `CoreBudgetEnforcer` (§2.3.1)
   - Verify CORE never exceeds 25% budget
   - Implement overflow fallback (items go to HOT with high importance)

3. **Discrete Compaction Baseline (Rule-Based)**
   - Implement `DiscreteCompactionBaseline` (§3.2.1)
   - Rule-based compression (no LLM required)
   - Verify behavior matches expected discrete compaction

4. **Experiment 4: Code Quality Benchmark**
   - SWE-bench-Lite Extended task loader
   - Coding agent test harness
   - All four quality metrics (completion, adherence, quality, consistency)
   - Comparative analysis: continuous vs. discrete

5. **Experiment 1: Stability (Updates)**
   - Update to use adaptive pruning rate
   - Add convergence time measurement
   - Verify acceptance criteria

#### P1 (High - Important for Validation)

6. **Experiment 2: Convergence**
   - Test convergence from multiple initial states
   - Verify adaptive rate formula
   - Measure convergence time

7. **Experiment 3: Information Preservation**
   - CORE decision recall testing
   - Comparative recall: continuous vs. discrete
   - Quantitative recall metrics

8. **Unprunable State Fallback**
   - Detect unprunable conditions (§2.4)
   - Implement force-unpin fallback
   - Log warnings for analysis

9. **Token Estimation Accuracy Measurement**
   - Track estimation errors (§2.5.2)
   - Report mean/max error, ±20% compliance
   - Verify acceptance criteria

10. **Comprehensive Metrics Collection**
    - Implement `EvaluationHarness` (§4.3.1)
    - Collect all four dimension metrics
    - Generate comparison reports

#### P2 (Medium - Enhancements)

11. **Qualitative Assessment Tooling**
    - Code quality rubric scorer (§4.3.2)
    - Rationale preservation assessor
    - Human evaluation interface

12. **Extended SWE-bench Task Set**
    - Expand from 50 to 100+ tasks
    - Vary task complexity
    - Include edge cases (very long conversations)

13. **Visualization & Reporting**
    - Enhanced plotting for all experiments
    - Interactive dashboards
    - Comparative analysis reports

14. **Performance Profiling**
    - Measure O(n²) impact at scale
    - Identify optimization opportunities
    - Document acceptable performance range

#### P3 (Low - Future Work / Phase II)

15. **LLM-Based Compaction Baseline**
    - Implement actual LLM summarization (§3.2.2)
    - Higher-fidelity comparison
    - Defer to Phase II (cost/complexity)

16. **WARM/COLD Tier Implementation**
    - Actual archival storage
    - Semantic retrieval
    - Defer to Phase II

17. **MCP Server Integration**
    - Production MCP server
    - Integration with Claude Code
    - Defer to Phase II

18. **Adversarial Testing**
    - Pathological inputs
    - Attack scenarios
    - Defer to Phase II

---

## 7. Success Criteria for Phase I

Phase I is successful if we can affirmatively answer:

### 7.1 Primary Research Question

**"Can continuous importance-based pruning maintain context more effectively than discrete compaction for AI coding agents?"**

**Evidence Required**:
- ✅ Stability: Context maintains steady state (Exp 1, Exp 2)
- ✅ Preservation: Better information retention (Exp 3)
- ✅ Code Quality: Equal or better task performance (Exp 4)

### 7.2 Quantitative Success Criteria

**Context Stability** (Experiments 1 & 2):
- [ ] Linear growth coefficient: |slope| < 0.01
- [ ] Steady-state oscillation: σ < 15% of target
- [ ] Max utilization: <60% of target
- [ ] Convergence: <30 interactions from any initial state

**Information Preservation** (Experiment 3):
- [ ] Continuous pruning CORE recall: >90% (score ≥4.5/5)
- [ ] Discrete baseline recall: <70% (demonstrates degradation)
- [ ] Relative improvement: ≥25% better for continuous

**Code Quality** (Experiment 4):
- [ ] Task completion: ≥90% of discrete baseline rate
- [ ] Specification adherence: ≥95% of discrete baseline
- [ ] Code quality score: ≥ discrete baseline (equal or better)

**System Integrity**:
- [ ] CORE budget never exceeded (0 violations across all experiments)
- [ ] Adaptive pruning rate functions correctly (verify formula)
- [ ] Token estimation: mean error ≤20%, 80%+ within ±20%
- [ ] Unprunable fallback: triggers correctly, system continues

### 7.3 Qualitative Success Criteria

- [ ] Approach is conceptually sound (peer review, academic validation)
- [ ] Results are reproducible (documented methodology, open-source code)
- [ ] Findings are actionable (clear path to Phase II if successful)
- [ ] Limitations are well-understood (known edge cases, acceptable trade-offs)

### 7.4 Deliverables for Phase I

**Research Artifacts**:
1. ✅ Functional continuous pruning implementation
2. ✅ All four experiments with results
3. ✅ Comparative analysis: continuous vs. discrete
4. ✅ Technical report documenting findings
5. ✅ Open-source repository with reproducible experiments

**Decision Points**:
- **If successful**: Proceed to Phase II (production implementation)
- **If mixed results**: Iterate on algorithm, refine hypothesis
- **If unsuccessful**: Pivot to alternative approaches or abandon

---

## 8. Open Questions & Items Needing Clarification

### 8.1 Technical Questions

**Q1: Optimal target context utilization?**
- Current hypothesis: 20-40% of capacity
- Needs empirical validation
- May vary by use case (short vs. long sessions)

**Q2: Recency decay half-life?**
- Currently: 10 interactions
- Optimal value may depend on task type
- Consider making adaptive based on interaction frequency

**Q3: CORE budget percentage?**
- Currently: 25% of target
- Is this sufficient for real development sessions?
- May need adjustment based on Experiment 3 results

**Q4: Pruning rate bounds?**
- Currently: 0.90-1.10 (±10% of neutral)
- Are bounds too conservative? Too aggressive?
- Empirical tuning needed

### 8.2 Experimental Design Questions

**Q5: SWE-bench task selection?**
- How to choose representative 50 tasks from 300?
- Stratify by difficulty? Domain? Repository?
- Needs principled selection methodology

**Q6: Conversation script design?**
- How to extend SWE-bench to 15-30 turns naturally?
- Use templates? LLM generation? Manual curation?
- Balance realism vs. reproducibility

**Q7: Code quality rubric validation?**
- Is our 4-dimension rubric (§4.3.2) sufficient?
- Should we include external validators (linters, static analysis)?
- How to ensure inter-rater reliability for qualitative assessment?

### 8.3 Scope & Boundary Questions

**Q8: Multi-agent scenarios?**
- Phase I focuses on single agent
- When to test agent teams with continuous pruning?
- Defer to Phase II or include in Phase I?

**Q9: Conversation coherence guarantees?**
- Not explicitly tested in Phase I
- Should we add coherence-specific experiments?
- Or is this implicitly covered by code quality metrics?

**Q10: Real-world validation?**
- Phase I uses synthetic extended conversations
- When to test with real user sessions?
- Defer to Phase II or pilot in Phase I?

### 8.4 Decisions Needed Before Implementation

**D1: Experiment 4 task count**
- Specification says 50 tasks
- Is this sufficient for statistical significance?
- Trade-off: more tasks vs. faster iteration

**D2: Baseline fidelity**
- Phase I uses rule-based discrete compaction
- Is this "good enough" to prove hypothesis?
- Or should we bite bullet and implement LLM baseline?

**D3: Token estimation strategy**
- Phase I uses chars/4 heuristic
- Acceptable for concept validation?
- Or should we integrate tiktoken from start?

**D4: Metrics reporting**
- How to present results? (Academic paper? Technical blog? Both?)
- Target audience: Researchers? Practitioners? Both?
- Influences depth and format of results

---

## 9. Appendices

### Appendix A: Research on Coding Benchmarks

**Summary of Benchmark Analysis**:

**SWE-bench Family**:
- **SWE-bench**: 2,294 GitHub issues, 12 Python repos
- **SWE-bench-Lite**: 300 verified issues, human-validated
- **SWE-bench-Verified**: Higher quality subset
- **Best for**: Real-world task complexity, objective evaluation
- **Limitation**: Originally single-shot, requires extension for multi-turn

**HumanEval / MBPP**:
- **HumanEval**: 164 handwritten function-level tasks
- **MBPP**: 974 crowd-sourced Python problems
- **Best for**: Quick correctness checks
- **Limitation**: Single-shot only, too simple for context testing

**Aider Polyglot Benchmark**:
- **Focus**: Multi-language edit quality
- **Best for**: Testing edit operations
- **Limitation**: Short interactions, not context-intensive

**DPAI Arena**:
- **Focus**: Developer-centric leaderboard
- **Best for**: Comparative agent performance
- **Limitation**: Not designed for context management research

**Conclusion**: SWE-bench-Lite Extended (our adaptation) is best fit for Phase I validation.

### Appendix B: Adaptive Pruning Rate Design Rationale

**Why adaptive rate instead of fixed 110%?**

Fixed rate problems:
1. **Cold start**: Empty context would shrink to nothing
2. **CORE overflow**: Can't compensate when CORE exceeds budget
3. **No equilibrium**: System doesn't naturally seek target utilization

Adaptive rate benefits:
1. **Self-regulating**: System naturally converges to target range
2. **Robust**: Handles varying CORE budgets and initial conditions
3. **Tunable**: Can adjust target utilization by changing rate formula

**Why 90-110% range?**
- 100% = neutral (steady state)
- ±10% provides sufficient control authority
- Bounds prevent extreme behavior (aggressive collapse or runaway growth)

### Appendix C: CORE Budget Trade-offs

**Why 25% of target capacity?**

Too small (<15%):
- Insufficient for real development sessions
- Constant CORE overflow, defeating purpose

Too large (>40%):
- Reduces HOT tier headroom
- More likely to hit unprunable states
- Negates pruning benefits

**25% rationale**:
- Typical coding session: 5-10 critical architectural decisions
- Average decision: 200-500 tokens (with rationale)
- 25% of 100K target = 25K tokens = ~50 rich decisions
- Empirically sufficient based on pilot testing

**Phase I validation**:
- Experiment 3 will test if 25% is sufficient
- May need adjustment based on results

### Appendix D: Algorithm Complexity Analysis

**Time Complexity**:

Per-interaction pruning:
```
1. Add new items: O(1)
2. Update all importance scores: O(n) where n = context size
3. Sort for pruning: O(n log n)
4. Remove items: O(n)

Total: O(n log n) per interaction
```

Over k interactions:
```
O(k * n log n)
```

**Problem**: This is O(n²) in the worst case if context grows linearly.

**Mitigation**:
- Continuous pruning keeps n bounded (steady state)
- n oscillates around ~30% of target, not unbounded
- Acceptable for Phase I concept validation
- Optimization for Phase II (incremental scoring, lazy evaluation)

**Performance Expectations (Phase I)**:
- Target: 100K tokens, ~25K steady state
- 500 interactions: ~125M operations
- Estimated runtime: <5 seconds on modern hardware
- **Acceptable for validation experiments**

### Appendix E: Known Limitations & Acceptable Trade-offs

**Phase I Limitations** (Acceptable for Concept Validation):

1. **Token estimation accuracy**: ±20% vs. ±5% ideal
   - Trade-off: Speed and simplicity vs. precision
   - Acceptable: Doesn't materially impact hypothesis testing

2. **Rule-based discrete baseline**: Approximation of LLM summarization
   - Trade-off: Determinism and cost vs. fidelity
   - Acceptable: "Good enough" to demonstrate relative advantage

3. **No WARM/COLD tier retrieval**: Simulated only
   - Trade-off: Implementation complexity vs. concept validation
   - Acceptable: Phase I tests HOT tier management primarily

4. **O(n²) complexity**: Not optimized
   - Trade-off: Development time vs. performance
   - Acceptable: Fast enough for validation-scale experiments

5. **No production integration**: Lab environment only
   - Trade-off: Realism vs. rapid iteration
   - Acceptable: Phase II concern, not Phase I

**Unacceptable Limitations** (Must Fix):
- ❌ CORE budget violations
- ❌ Pruning failures causing system crash
- ❌ Incorrect adaptive rate behavior
- ❌ Comparison using incomparable baselines

### Appendix F: Glossary

**Adaptive Pruning Rate**: Dynamic multiplier (0.90-1.10) applied to tokens added, determining how aggressively to prune

**CORE Tier**: Immutable context containing critical decisions, never pruned, ≤25% of target capacity

**Discrete Compaction**: Traditional approach: wait until context ~80% full, compress to ~30%

**HOT Tier**: Active working context, subject to continuous pruning based on importance scores

**Importance Score**: 0.0-1.0 value indicating retention priority, calculated from recency, access, type, and pins

**Linear Growth**: Undesirable behavior where context size increases unbounded, eventually exceeding capacity

**Prunable Tokens**: Context content not in CORE tier and not pinned, eligible for removal

**Steady State**: Equilibrium where context oscillates around target utilization without net growth

**Token Estimation**: Approximate counting of tokens (chars/4 heuristic in Phase I)

**Unprunable State**: Condition where insufficient prunable content exists to maintain target size

---

## 10. References & Further Reading

**Benchmark Research**:
- SWE-bench: "SWE-bench: Can Language Models Resolve Real-world GitHub Issues?" (2023)
- HumanEval: "Evaluating Large Language Models Trained on Code" (2021)
- MBPP: "Program Synthesis with Large Language Models" (2021)

**Context Management**:
- "Lost in the Middle: How Language Models Use Long Contexts" (2023)
- "Improving Context Usage in Language Models" (2024)
- Claude 3 Technical Report: Context window management strategies

**Code Generation**:
- "Competition-Level Code Generation with AlphaCode" (2022)
- "Teaching Large Language Models to Self-Debug" (2023)

**Internal References**:
- `/home/frankbria/projects/context-pruning-lab/README.md` - Project overview
- `/home/frankbria/projects/context-pruning-lab/pruner.py` - Core implementation
- `/home/frankbria/projects/context-pruning-lab/experiments/` - Experimental code

---

## Document Revision History

| Version | Date       | Changes                                      | Author |
|---------|------------|----------------------------------------------|--------|
| 1.0     | 2025-10-29 | Initial specification based on stakeholder discussion and brainstorming | Research Team |

---

**End of Technical Specification**

**Next Steps**: Review with stakeholders → Approve for implementation → Execute Phase I experiments → Evaluate results → Decide Phase II go/no-go
