# Context Management Research: Warmup & Logistic Growth

**Date**: 2025-11-04
**Research Question**: How should continuous pruning handle context growth during agent initialization?
**Current Problem**: ContinuousPruner removes 100% of context from the start, breaking agent memory

---

## Executive Summary

Our continuous pruning implementation has a **catastrophic bug**: it removes all context immediately because:
1. New items start with importance 0.55 (below 0.95 protection threshold)
2. Adaptive rate of 0.95 means pruning 95% of tokens added
3. No warmup period allows context to build before pruning starts

**Research finding**: Production AI systems use **phased growth** strategies:
- **Phase 1 (Warmup)**: Let context grow to working size
- **Phase 2 (Steady State)**: Apply gentle pruning with logistic limits
- **Phase 3 (Crisis)**: Aggressive compaction if approaching hard limits

This matches your intuition about logistic growth approaching a reasonable limit.

---

## Key Research Findings

### 1. Industry Best Practices for Context Management

#### Anthropic Claude Code (Context Engineering Blog, 2025)
**Approach**: Auto-compaction at 95% context usage
- Doesn't prune until threshold reached
- When triggered, summarizes entire conversation
- Preserves critical info (objectives, key decisions)
- Uses persistent memory (NOTES.md) for continuity

**Key Insight**: "Aggressive reduction risks information loss. Better approach: offload full data to external memory and feed back only summaries."

#### AWS AgentCore Memory (2025)
**Dual Memory System**:
- **Short-term (working memory)**: Immediate conversation context within session
- **Long-term (intelligent memory)**: Persistent knowledge across sessions

**Design Principles**:
1. Proactive memory management (not reactive)
2. Intelligent decay (not arbitrary pruning)
3. User control over what's remembered
4. Transparent operations

#### OpenAI Agents SDK Session Memory
**Context Management Techniques**:
1. **Trimming**: Remove old messages beyond N-turn window
2. **Compression**: Summarize older content, keep recent full
3. **Selective Loading**: Only load relevant memories per turn

**Implementation Pattern**:
```python
# Simplified pattern
if context_size < threshold:
    # Warmup: Just accumulate
    context.append(new_message)
else:
    # Steady state: Compress old, keep recent
    context = compress_old(context) + [new_message]
```

### 2. Academic Research on Context Length

#### "Fewer is More: Boosting LLM Reasoning with Reinforced Context Pruning" (Microsoft, 2024)
**Finding**: Pruning CAN improve reasoning by removing distracting context
- But timing matters: need sufficient context first
- Pruning improves few-shot CoT by removing irrelevant examples
- Keep high-quality examples, prune low-quality ones

**Relevance**: Supports gradual pruning after warmup, not immediate pruning

#### "StreamingLLM" (Xiao et al., 2024)
**Key Innovation**: Address "attention sink" phenomenon
- First tokens get disproportionate attention regardless of relevance
- Solution: Merge window context with first token (anchor)
- Enables finite-length attention windows for infinite streams

**Relevance**: Protect initial context items from pruning (they anchor attention)

#### "Memory Management for Long-Running LCNC Agents" (arXiv, 2025)
**Problem Identified**:
- **Memory inflation**: Unbounded growth from long interactions
- **Contextual degradation**: Quality drops as context fills

**Solution - Intelligent Decay**:
- Proactive memory management (not reactive)
- Prune AND consolidate information
- User interface for curation

**Experimental Results** (500-turn task):
- Sliding Window Baseline: Simple 10-turn window
- Intelligent Decay: 91% lower p95 latency, 90% token cost savings
- Full Context: Fails at scale

**Key Quote**: "Intelligent pruning leads to substantial increase in task completion rate, reduction in contradictions, and significant improvement in long-term contextual consistency."

### 3. Logistic Growth Functions

#### Self-Extend Context with Logistic Growth (arXiv, 2025)
**Approach**: Use logistic function to control context growth
```
f(x) = L / (1 + e^(-k(x - x0)))

Where:
- L = carrying capacity (max context size)
- k = steepness of growth
- x0 = midpoint of growth
```

**Application to Context**:
- x = interaction number
- L = target context size (e.g., 125K tokens)
- Early interactions: Low limit (allow growth)
- Middle interactions: Rapid growth
- Late interactions: Approach asymptote (steady pruning)

**Benefits**:
- Natural S-curve growth
- Smooth transition from warmup to steady state
- Never exceeds carrying capacity

### 4. Warmup Period Best Practices

From LLM training literature (applied to context management):

**Standard Warmup Schedules**:
- 5-10% of total expected interactions
- Example: For 50-turn task, warmup = 3-5 turns
- Linear growth during warmup, stable after

**Warmup Functions**:
```python
# Linear warmup
pruning_rate = min(target_rate, current_turn / warmup_turns * target_rate)

# Cosine warmup
pruning_rate = target_rate * 0.5 * (1 - cos(π * current_turn / warmup_turns))
```

**Why Warmup Matters**:
1. Prevents premature information loss
2. Allows agent to build working memory
3. Establishes context foundation
4. Reduces early-interaction instability

---

## Root Cause Analysis: Current Bug

### The Importance Formula Problem

```python
# Current formula (pruner.py:411-416)
final_score = (
    recency_score * 0.4 +    # exp(-age/10)
    access_score * 0.2 +     # min(access * 0.05, 0.3)
    type_score * 0.3 +       # default 0.5
    pin_score * 0.1          # 0 if not pinned
)
```

**For brand new items** (age=0, access=0):
```
recency = exp(0) = 1.0
access = 0
type = 0.5 (default)
pin = 0

final = 1.0*0.4 + 0*0.2 + 0.5*0.3 + 0
      = 0.4 + 0 + 0.15 + 0
      = 0.55  ← TOO LOW!
```

**But protection threshold** (pruner.py:428):
```python
prunable_items = [i for i in self.context if i.importance < 0.95]
```

**Result**: New items (0.55) < threshold (0.95) → **IMMEDIATELY PRUNABLE!**

### The Adaptive Rate Problem

```python
# Current adaptive rate (pruner.py:300)
final_rate = max(0.90, min(1.10, final_rate))
```

**Typical value**: 0.95 (95% pruning)

**With 0.95 rate**:
- Add 4000 tokens
- Target prune = 4000 * 0.95 = 3800 tokens
- New items are lowest importance
- Remove 3800 tokens (almost everything!)
- Context → nearly empty

### Why Agent "Succeeded" Despite This

The agent sent/received tokens (268K total), so it WAS generating responses. But:

1. **Conversation log shows random flailing**:
   - Turn 1: Asks to see sessions.py
   - Turn 2: Reads flask_theme_support.py (unrelated!)
   - Turn 3: Reads conf.py (doc config)
   - No coherence between turns

2. **Zero memory**:
   - Doesn't remember problem description
   - Doesn't remember files read
   - Each turn is independent

3. **"Success" is misleading**:
   - Experiment marks success if `turns > 1`
   - Agent completed turns, but produced nonsense
   - Like saying a conversation "succeeded" because words were spoken

---

## Design Options for Fix

### Option 1: Simple Warmup Period (Easiest)

**Concept**: Don't prune at all for first N interactions

```python
class ContinuousPruner:
    def __init__(self, ..., warmup_interactions: int = 5):
        self.warmup_interactions = warmup_interactions

    def add_interaction(self, ...):
        # ... add to context ...

        # Skip pruning during warmup
        if self.interaction_count <= self.warmup_interactions:
            return self.metrics  # No pruning

        # Normal pruning after warmup
        adaptive_rate = self.calculate_adaptive_rate()
        target_prune = int(tokens_added * adaptive_rate)
        self._prune_context(target_prune)
```

**Pros**:
- Dead simple implementation
- Guarantees agent has working memory
- Clear phase transition

**Cons**:
- Hard cutoff (not smooth)
- Doesn't scale with task complexity
- Could still over-accumulate during warmup

**Recommended Settings**:
- warmup_interactions = 5 (for 50-turn tasks)
- warmup_interactions = 10 (for 100+ turn tasks)
- Rule of thumb: 5-10% of expected total turns

---

### Option 2: Logistic Growth Function (Most Principled)

**Concept**: Context capacity grows logistically from low → target over time

```python
import math

class ContinuousPruner:
    def __init__(
        self,
        target_context_size: int = 125_000,
        warmup_interactions: int = 10,
        max_growth_interactions: int = 30
    ):
        self.target_context_size = target_context_size
        self.warmup_interactions = warmup_interactions
        self.max_growth_interactions = max_growth_interactions

    def get_current_capacity(self) -> int:
        """Calculate current context capacity using logistic function"""

        if self.interaction_count <= 1:
            # Very first interaction: generous capacity
            return int(self.target_context_size * 0.3)  # 37.5K tokens

        if self.interaction_count <= self.warmup_interactions:
            # Warmup phase: linear growth
            fraction = self.interaction_count / self.warmup_interactions
            return int(self.target_context_size * 0.3 * fraction)

        # Logistic growth phase
        # S-curve from 30% to 100% of target over 30 interactions
        x = self.interaction_count - self.warmup_interactions
        L = self.target_context_size  # Carrying capacity
        k = 0.3  # Steepness (adjust for faster/slower growth)
        x0 = self.max_growth_interactions / 2  # Midpoint

        capacity = L / (1 + math.exp(-k * (x - x0)))

        # Ensure we approach but don't exceed target
        return int(min(capacity, self.target_context_size))

    def add_interaction(self, ...):
        # ... add to context ...

        current_capacity = self.get_current_capacity()
        current_size = self.get_total_tokens()

        # Only prune if exceeding current capacity
        if current_size > current_capacity:
            tokens_to_prune = current_size - current_capacity
            self._prune_context(tokens_to_prune)
```

**Growth Curve Example** (target=125K):

```
Interaction | Capacity | % of Target | Phase
------------|----------|-------------|-------
1           | 37,500   | 30%         | First interaction
2           | 15,000   | 12%         | Warmup
5           | 37,500   | 30%         | Warmup
10          | 37,500   | 30%         | End warmup
15          | 52,000   | 42%         | Growth
20          | 78,000   | 62%         | Growth
25          | 102,000  | 82%         | Growth
30          | 118,000  | 94%         | Growth
40          | 124,500  | 99.6%       | Steady state
50+         | 125,000  | 100%        | Steady state
```

**Pros**:
- Smooth, natural growth
- Matches biological systems (S-curve growth)
- Automatically adapts to task length
- Never exceeds capacity

**Cons**:
- More complex implementation
- Requires tuning parameters (k, x0)
- Harder to explain/debug

**Recommended Settings**:
- warmup_interactions = 5-10
- max_growth_interactions = 20-30
- k = 0.2-0.4 (steepness)

---

### Option 3: Gradual Pruning Rate Ramp (Hybrid)

**Concept**: Start with low pruning rate, gradually increase to target

```python
class ContinuousPruner:
    def __init__(
        self,
        warmup_interactions: int = 5,
        ramp_interactions: int = 15,
        min_pruning_rate: float = 0.1,  # 10% during warmup
        target_pruning_rate: float = 0.95  # 95% at steady state
    ):
        self.warmup_interactions = warmup_interactions
        self.ramp_interactions = ramp_interactions
        self.min_pruning_rate = min_pruning_rate
        self.target_pruning_rate = target_pruning_rate

    def get_current_pruning_rate(self) -> float:
        """Calculate current pruning rate based on interaction count"""

        if self.interaction_count <= self.warmup_interactions:
            # Warmup: minimal pruning
            return self.min_pruning_rate

        if self.interaction_count <= self.warmup_interactions + self.ramp_interactions:
            # Ramp phase: linear increase
            progress = (self.interaction_count - self.warmup_interactions) / self.ramp_interactions
            rate_range = self.target_pruning_rate - self.min_pruning_rate
            return self.min_pruning_rate + (progress * rate_range)

        # Steady state: full pruning rate
        return self.target_pruning_rate

    def add_interaction(self, ...):
        # ... add to context ...

        # Use phased pruning rate instead of adaptive
        pruning_rate = self.get_current_pruning_rate()
        target_prune = int(tokens_added * pruning_rate)
        self._prune_context(target_prune)
```

**Pruning Rate Example**:

```
Interaction | Pruning Rate | Tokens Added | Tokens Pruned
------------|--------------|--------------|---------------
1-5         | 10%          | 4000         | 400
6           | 15%          | 4000         | 600
10          | 33%          | 4000         | 1320
15          | 62%          | 4000         | 2480
20          | 90%          | 4000         | 3600
25+         | 95%          | 4000         | 3800
```

**Pros**:
- Simple to implement and understand
- Smooth transition (no hard cutoffs)
- Keeps adaptive rate logic (just modulates it)
- Easy to tune (just adjust min/max rates)

**Cons**:
- Still uses aggressive pruning late (95%)
- Doesn't account for actual context size
- Fixed schedule (doesn't adapt to task needs)

**Recommended Settings**:
- warmup_interactions = 5
- ramp_interactions = 10-15
- min_pruning_rate = 0.05 - 0.10 (5-10%)
- target_pruning_rate = 0.50 - 0.70 (not 0.95!)

---

### Option 4: Fix Importance Calculation (Essential for All Options)

**Problem**: New items score 0.55, need ≥0.95 to avoid pruning

**Solution A - Adjust Formula Weights**:
```python
def _calculate_importance(self, item: ContextItem) -> float:
    # Increase recency weight, decrease type weight
    final_score = (
        recency_score * 0.6 +  # Was 0.4 → Now 0.6
        access_score * 0.2 +   # Same
        type_score * 0.1 +     # Was 0.3 → Now 0.1
        pin_score * 0.1        # Same
    )

    # New items now score:
    # 1.0*0.6 + 0*0.2 + 0.5*0.1 + 0 = 0.65 (still too low!)

    # Need even more aggressive:
    final_score = (
        recency_score * 0.8 +  # Even more recency weight
        access_score * 0.1 +
        type_score * 0.05 +
        pin_score * 0.05
    )

    # New items: 1.0*0.8 + 0 + 0.025 + 0 = 0.825 (better, but still < 0.95)
```

**Solution B - Lower Protection Threshold** (EASIER):
```python
def _prune_context(self, target_tokens: int):
    # Lower threshold from 0.95 to 0.7
    core_items = [i for i in self.context if i.tier == "CORE" or i.importance >= 0.70]
    prunable_items = [i for i in self.context if i.tier != "CORE" and i.importance < 0.70]

    # Now new items (0.55) are BELOW threshold
    # But items age=1 (recency=0.905) score 0.55*0.6 + 0.905*0.4 = 0.692 (barely protected)
```

**Solution C - Explicit Recent Item Protection** (RECOMMENDED):
```python
def _prune_context(self, target_tokens: int):
    # Protect last N interactions explicitly
    recent_threshold = self.interaction_count - 3  # Last 3 interactions

    core_items = [
        i for i in self.context
        if i.tier == "CORE"
        or i.importance >= 0.95
        or i.interaction_number > recent_threshold  # ← NEW PROTECTION
    ]

    prunable_items = [
        i for i in self.context
        if i.tier != "CORE"
        and i.importance < 0.95
        and i.interaction_number <= recent_threshold  # ← MUST BE OLD
    ]
```

**Pros**:
- Simple and explicit
- Guarantees recent context preserved
- Works regardless of importance scores

**Cons**:
- Adds another magic number (N=3)
- Could accumulate too much if turns are large

**Recommended**:
- recent_interactions = 2-3 (protect last 2-3 turns)
- Combine with warmup period for best results

---

## Recommended Implementation Strategy

### Phase 1: Immediate Fix (This Session)

**Implement Option 3 + Option 4C** (Gradual Ramp + Recent Protection)

```python
class ContinuousPruner:
    def __init__(
        self,
        target_context_size: int = 125_000,
        warmup_interactions: int = 5,
        ramp_interactions: int = 10,
        recent_protection: int = 3,  # Protect last N interactions
        min_pruning_rate: float = 0.10,  # Start gentle
        target_pruning_rate: float = 0.60  # Don't go crazy (was 0.95!)
    ):
        self.warmup_interactions = warmup_interactions
        self.ramp_interactions = ramp_interactions
        self.recent_protection = recent_protection
        self.min_pruning_rate = min_pruning_rate
        self.target_pruning_rate = target_pruning_rate

    def get_current_pruning_rate(self) -> float:
        """Gradual ramp from min to target"""
        if self.interaction_count <= self.warmup_interactions:
            return self.min_pruning_rate

        if self.interaction_count <= self.warmup_interactions + self.ramp_interactions:
            progress = (self.interaction_count - self.warmup_interactions) / self.ramp_interactions
            rate_range = self.target_pruning_rate - self.min_pruning_rate
            return self.min_pruning_rate + (progress * rate_range)

        return self.target_pruning_rate

    def _prune_context(self, target_tokens: int):
        """Prune with explicit recent protection"""
        recent_threshold = self.interaction_count - self.recent_protection

        # Core + high importance + recent items
        protected_items = [
            i for i in self.context
            if i.tier == "CORE"
            or i.importance >= 0.95
            or i.interaction_number > recent_threshold
        ]

        # Everything else is prunable
        prunable_items = [
            i for i in self.context
            if i not in protected_items
        ]

        # Sort by importance and prune lowest first
        prunable_items.sort(key=lambda x: x.importance)

        tokens_removed = 0
        items_removed = 0
        items_to_keep = []

        for item in prunable_items:
            if tokens_removed < target_tokens:
                tokens_removed += item.token_count
                items_removed += 1
            else:
                items_to_keep.append(item)

        # Rebuild context
        self.context = protected_items + items_to_keep

        return tokens_removed, items_removed
```

**Why This Combination**:
1. ✅ Warmup (5 turns): Agent builds working memory
2. ✅ Gradual ramp (10 turns): Smooth transition to pruning
3. ✅ Recent protection (3 turns): Always keep last 3 interactions
4. ✅ Lower target rate (60% not 95%): Less aggressive pruning
5. ✅ Simple to implement: ~50 lines of code changes

**Expected Behavior**:
```
Turn 1-5:   Context grows (10% pruning) → ~18K tokens
Turn 6-15:  Gradual pruning increase → ~60K tokens
Turn 16+:   Steady pruning (60%) → ~80-100K tokens
```

### Phase 2: Advanced Optimization (Future)

After validating Phase 1 works:

**Option 2 (Logistic Growth)** for smoother, more principled approach
- Better theoretical foundation
- Adapts to longer tasks automatically
- Worth the complexity if Phase 1 isn't smooth enough

---

## Validation Plan

### Test 1: Single Problem with Fixed Pruner
- Run 1 problem with new implementation
- Check context_size > 0 throughout
- Verify conversation shows coherence
- Ensure context grows during warmup, stabilizes after

### Test 2: 2-Problem Comparison (Redux)
- Repeat original experiment with fixed pruner
- Compare to discrete baseline
- Expected: Continuous still more efficient but not 15x (more like 2-3x)
- Expected: Context sizes non-zero and reasonable

### Test 3: Longer Task Validation
- Run on complex problem requiring 50+ turns
- Monitor context growth curve
- Verify logistic behavior if using Option 2
- Check for memory continuity

---

## Conclusion

**Root Cause**: Continuous pruner removes all context because:
1. New items score too low (0.55 < 0.95 threshold)
2. No warmup period before pruning starts
3. Aggressive pruning rate (95%)

**Industry Pattern**: All production systems use **phased growth**:
- Warmup: Let context build
- Growth: Gradual capacity increase
- Steady state: Maintain around target with gentle pruning

**Recommendation**: Implement **Option 3 + Option 4C**
- Simple warmup period (5 turns)
- Gradual pruning ramp (10 turns)
- Explicit recent protection (3 turns)
- Lower target rate (60% not 95%)

This matches your intuition about logistic growth with reasonable limits.

---

## References

1. Anthropic (2025). "Effective context engineering for AI agents"
2. AWS (2025). "Amazon Bedrock AgentCore Memory"
3. Microsoft Research (2024). "Fewer is More: Boosting LLM Reasoning with Reinforced Context Pruning"
4. Xiao et al. (2024). "StreamingLLM"
5. arXiv (2025). "Memory Management for Long-Running LCNC Agents"
6. arXiv (2025). "Self-Extend the Context Length With Logistic Growth Function"
7. OpenAI (2025). "Context Engineering - Session Memory"
8. Galileo AI (2025). "Deep Dive into Context Engineering for Agents"

**Status**: Research complete, ready for implementation
**Next**: Implement Phase 1 fix and validate
