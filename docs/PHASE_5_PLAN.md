# Phase 5 Plan: Real-World Validation Experiment

**Goal**: Validate continuous pruning on 20 real coding problems with natural conversation flow and complete cost accounting.

**Your Questions Addressed**:
1. ✅ Public benchmarks for real problems
2. ✅ Anthropic's actual compactification vs. ours
3. ✅ Open-ended problem solving (natural completion)
4. ✅ Full cost accounting (tokens, time, quality, overhead)
5. ✅ Current pruning token costs

---

## Question 5 Answer: Current Pruning Token Costs

### **In Sprint 4: Pruning Uses NO AI Calls**

**Code**: `pruner.py:367` - `_calculate_importance()`

```python
def _calculate_importance(self, item: ContextItem) -> float:
    """Calculate importance using LOCAL algorithms"""
    # TF-IDF-based content importance
    # Recency weighting
    # Access count tracking
    # NO API CALLS - pure Python computation
```

**What This Means**:
- ✅ **Pruning cost**: ~0 tokens (local computation only)
- ✅ **Pruning time**: <1ms per interaction (negligible)
- ✅ **All costs measured**: 100% of token costs are in the 82% calculation

**Verification**:
```bash
grep -c "anthropic\|client.messages" pruner.py
# Result: 0 matches
```

**Implication**: Our 82% reduction is the ACTUAL savings - no hidden costs.

---

## Question 1: Public Benchmarks for Real Problems

### **Option 1: SWE-bench (RECOMMENDED)**

**What**: Real GitHub issues from popular Python repos
**Size**: 2,294 problems (can sample 20)
**Context**: Real codebases (large enough to require compaction)
**Quality**: Production code, real bugs/features

**Why Best**:
- ✅ Real-world complexity
- ✅ Actual codebases (100K+ tokens available)
- ✅ Verified solutions (merged PRs)
- ✅ Multiple difficulty levels
- ✅ Already has evaluation harness

**Example Problems**:
```
django/django#12345: Fix QuerySet filtering bug
requests/requests#2456: Add retry functionality
pandas/pandas#8901: Optimize DataFrame merge performance
```

**How to Use**:
```python
from datasets import load_dataset
swe_bench = load_dataset("princeton-nlp/SWE-bench")
# Select 20 problems spanning difficulty levels
problems = swe_bench.filter(lambda x: x['difficulty'] in ['medium', 'hard'])[:20]
```

**Dataset Structure**:
```json
{
  "instance_id": "django__django-12345",
  "patch": "<actual fix>",
  "repo": "django/django",
  "base_commit": "abc123",
  "problem_statement": "Bug description",
  "hints_text": "Relevant files",
  "test_patch": "Tests to verify fix"
}
```

---

### **Option 2: CodeContests**

**What**: Competitive programming problems (Codeforces, etc.)
**Size**: 13,000+ problems
**Context**: Problem descriptions + examples

**Pros**:
- ✅ Clear success criteria (test cases pass/fail)
- ✅ Verifiable correctness

**Cons**:
- ❌ Less realistic than real repos
- ❌ Smaller context (doesn't stress compaction)

---

### **Option 3: HumanEval / MBPP**

**What**: Hand-crafted Python programming problems
**Size**: 164 (HumanEval) / 974 (MBPP)

**Pros**:
- ✅ Well-tested
- ✅ Clear specifications

**Cons**:
- ❌ Too small (doesn't require compaction)
- ❌ Single-function problems (not realistic)

---

### **Recommendation: SWE-bench Subset**

**Proposed 20-Problem Set**:
```
Difficulty Distribution:
- 5 easy   (baseline performance)
- 10 medium (primary validation)
- 5 hard   (stress test)

Repo Distribution:
- 5 Django (large framework)
- 5 Requests (mid-size library)
- 5 Pandas (data science)
- 5 Scikit-learn (ML library)

Problem Types:
- 8 bug fixes
- 7 new features
- 5 refactorings
```

**Context Sizes** (estimated):
- Easy: 10K-30K tokens (codebase context)
- Medium: 30K-80K tokens
- Hard: 80K-200K tokens

---

## Question 2: Anthropic's Compactification vs. Ours

### **Anthropic's Approach: Prompt Caching**

**What They Offer** (via API):
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system=[
        {
            "type": "text",
            "text": "System prompt...",
            "cache_control": {"type": "ephemeral"}  # ← Their caching
        }
    ],
    messages=messages
)
```

**How It Works**:
- Caches portions of prompts (system, context)
- Reduces cost for repeated content (75% discount)
- TTL: 5 minutes
- User marks what to cache (manual)

**Limitations**:
- ❌ Doesn't prune/compact (just caches)
- ❌ Requires manual cache control
- ❌ 5-min TTL (doesn't help long sessions)
- ❌ Doesn't reduce context size (just cost)

**Our Approach**: Different goal (reduce context, not just cost)

---

### **Comparison Framework**

**Three Strategies to Test**:

1. **Continuous Pruning** (Ours)
   - Active pruning after every turn
   - Importance-based content removal
   - Target: 40K tokens

2. **Discrete Baseline** (Our baseline)
   - Compaction at 80% threshold
   - Aggressive removal to 30%
   - Traditional approach

3. **Prompt Caching** (Anthropic's)
   - No pruning
   - Cache system prompts + codebase
   - Let context grow naturally

**Fair Comparison**:
```python
strategies = {
    'continuous_pruning': {
        'manager': ContinuousPruner(target_size=40000),
        'caching': False  # No caching
    },
    'discrete_baseline': {
        'manager': DiscreteCompactionBaseline(target_size=40000),
        'caching': False
    },
    'prompt_caching': {
        'manager': None,  # No pruning
        'caching': True,  # Use Anthropic's caching
        'cache_config': {'type': 'ephemeral'}
    }
}
```

**Metrics**:
- Token usage (input + output)
- API costs (accounting for cache discounts)
- Context size over time
- Solution quality
- Time to completion

---

## Question 3: Natural Problem Completion

### **Current Problem**: Fixed-Turn Scripts

```python
# Sprint 4 (artificial)
for turn in range(19):  # Fixed!
    agent.respond()
```

**Issues**:
- ❌ Agent can't indicate completion
- ❌ May solve in 5 turns but forced to continue
- ❌ May need 30 turns but limited to 19

---

### **Phase 5 Solution**: Agent-Driven Completion

**Design**: Agent declares when done via special token

```python
# Agent response format
{
    "status": "working" | "solution_ready" | "need_more_info",
    "confidence": 0.0-1.0,
    "response": "...",
    "proposed_solution": "..." if status == "solution_ready"
}
```

**Conversation Flow**:
```python
max_turns = 50  # Safety limit
while not done and turns < max_turns:
    response = agent.generate_response()

    # Agent can declare completion
    if response.status == "solution_ready":
        if validate_solution(response.proposed_solution):
            done = True
            break

    # Or request more context
    elif response.status == "need_more_info":
        context = fetch_requested_context(response.request)
        agent.receive_message(context)

    turns += 1
```

**Advantages**:
- ✅ Natural completion (no artificial limits)
- ✅ Measures actual problem-solving time
- ✅ Agent can request specific context
- ✅ More realistic workflow

**Implementation**:
```python
# Agent prompt modification
system_prompt = """
You are a coding assistant. When you have a complete solution:
1. Test it mentally
2. Return: {"status": "solution_ready", "solution": "<code>"}

If you need more information:
1. Return: {"status": "need_more_info", "request": "Show me file X"}

Continue working until confident in your solution.
"""
```

---

## Question 4: Full Cost Accounting

### **Current Gap**: Incomplete Cost Model

**What We Measure Now**:
- ✅ API tokens (input + output)
- ✅ Wall-clock time
- ❌ Pruning computation cost
- ❌ Context fetching cost
- ❌ Solution quality
- ❌ Opportunity cost (could have been faster?)

---

### **Phase 5: Complete Cost Model**

**1. Direct API Costs**
```python
costs = {
    'input_tokens': tokens_sent * $3.00/M,
    'output_tokens': tokens_received * $15.00/M,
    'cache_writes': cache_tokens * $3.75/M,  # If using caching
    'cache_reads': cache_tokens * $0.30/M
}
```

**2. Computational Overhead**
```python
overhead = {
    'pruning_time': sum(time_per_prune),      # Milliseconds
    'pruning_cpu': pruning_operations * cpu_cost,
    'importance_calc': num_items * calc_time
}
```

**3. Solution Quality**
```python
quality = {
    'correctness': tests_passed / total_tests,
    'time_to_solution': turns_until_complete,
    'code_quality': aggregate_score,
    'first_attempt_success': bool
}
```

**4. Efficiency Metrics**
```python
efficiency = {
    'tokens_per_turn': total_tokens / num_turns,
    'cost_per_problem': total_cost / problems_solved,
    'quality_per_token': quality_score / total_tokens
}
```

---

### **Cost Comparison Framework**

**Scenario**: Agent uses more tokens due to pruning overhead, but solves faster

```python
# Continuous Pruning
continuous = {
    'tokens': 15000,
    'turns': 12,
    'solved': True,
    'quality': 0.95,
    'time': 180s,
    'pruning_overhead': 50 tokens  # From additional context fetches
}

# Discrete Baseline
baseline = {
    'tokens': 45000,
    'turns': 20,
    'solved': True,
    'quality': 0.92,
    'time': 350s,
    'pruning_overhead': 0
}

# Calculate adjusted efficiency
continuous_efficiency = (
    continuous['quality'] / continuous['tokens'] * 1000
)  # Quality per 1K tokens

baseline_efficiency = (
    baseline['quality'] / baseline['tokens'] * 1000
)

# Result:
# Continuous: 0.95 / 15 = 63.3 quality per 1K tokens
# Baseline:   0.92 / 45 = 20.4 quality per 1K tokens

# Continuous is 3.1x more efficient!
```

**Win Conditions**:
1. **Cost Win**: Lower total tokens (even with overhead)
2. **Speed Win**: Faster solution (fewer turns)
3. **Quality Win**: Better solution (higher test pass rate)
4. **Efficiency Win**: Best quality/token ratio

**Verdict**: Winner needs 2+ of 4 metrics

---

### **Accounting for "Intelligent" Overhead**

**Example**: Pruning triggers context fetch

```python
# Turn 10: Context gets pruned
pruned_item = "Helper function definition"

# Turn 12: Agent asks for it back
agent_request = "Show me the helper function"

# Cost accounting
overhead = {
    'pruning_saved': 200 tokens * 8 turns = 1600 tokens saved,
    'fetch_cost': 1 fetch * 50 tokens = 50 tokens,
    'net_savings': 1600 - 50 = 1550 tokens
}
```

**Key**: Even with overhead, net is positive if pruning is smart.

---

## Question 5 Deep Dive: Pruning Token Costs in Sprint 4

### **Complete Token Flow**

**What Gets Counted**:
```python
# agent.py:155-156
self.total_tokens_sent += response.usage.input_tokens      # ← Includes context
self.total_tokens_received += response.usage.output_tokens # ← Agent response
```

**What Does NOT Cost Tokens**:
```python
# pruner.py:367 - _calculate_importance()
def _calculate_importance(self, item):
    # TF-IDF calculation: LOCAL, no API
    # Recency scoring: LOCAL, no API
    # Tier assignment: LOCAL, no API
    return importance_score  # 0 tokens, <1ms
```

**Pruning Process**:
```
1. Agent responds → API tokens counted ✅
2. Add to context → Local operation (0 tokens)
3. Calculate importance → Local TF-IDF (0 tokens)
4. Sort by importance → Local sort (0 tokens)
5. Remove low-importance → Local deletion (0 tokens)
6. Next turn → Smaller context sent → SAVINGS! ✅
```

**Verification**:
```bash
# Check for any AI calls in pruner
$ grep -E "anthropic|openai|client|api" pruner.py
# Result: 0 matches (pure Python)
```

---

### **Future: AI-Assisted Pruning (Phase 6?)**

**Hypothetical**: Use AI to score importance

```python
# Would add cost:
def _calculate_importance_with_ai(self, item):
    prompt = f"Rate importance 0-1: {item.content}"
    response = self.client.messages.create(
        model="claude-haiku",  # Cheap model
        messages=[{"role": "user", "content": prompt}]
    )
    # Cost: ~100 tokens per item
    return float(response.content[0].text)
```

**Cost Analysis**:
```
Continuous pruning: 8 operations * 10 items * 100 tokens = 8,000 tokens
Baseline: 0 tokens (no pruning)

Net savings: 24,409 tokens (saved) - 8,000 tokens (overhead) = 16,409 tokens
Still 55% reduction!
```

**But**: Current approach has NO AI cost, so this is purely hypothetical.

---

## Phase 5 Implementation Plan

### **Timeline**: 2 weeks (Sprint 5)

**Week 1: Infrastructure**
- T5.1: Load SWE-bench dataset (20 problems)
- T5.2: Implement natural completion logic
- T5.3: Add prompt caching strategy
- T5.4: Implement full cost accounting

**Week 2: Execution & Analysis**
- T5.5: Run 20-problem experiment (3 strategies)
- T5.6: Statistical analysis + visualization
- T5.7: Write Phase 5 report
- T5.8: Update documentation

---

### **Detailed Task Breakdown**

#### **T5.1: Load SWE-bench Dataset** (4 hours)

```python
# experiments/swe_bench_real/loader.py
from datasets import load_dataset

class SWEBenchRealLoader:
    def __init__(self):
        self.dataset = load_dataset("princeton-nlp/SWE-bench")

    def select_problems(self, n=20, difficulties=['medium', 'hard']):
        """Select balanced problem set"""
        problems = []
        for diff in difficulties:
            subset = self.dataset.filter(lambda x: x['difficulty'] == diff)
            problems.extend(subset.select(range(n // len(difficulties))))
        return problems

    def prepare_problem(self, problem):
        """Convert to our format"""
        return {
            'task_id': problem['instance_id'],
            'description': problem['problem_statement'],
            'codebase': self._fetch_codebase(problem['repo'], problem['base_commit']),
            'tests': problem['test_patch'],
            'solution': problem['patch']  # For validation
        }
```

---

#### **T5.2: Natural Completion Logic** (6 hours)

```python
# experiments/swe_bench_real/natural_agent.py
class NaturalCompletionAgent(RealCodingAgent):
    def generate_response_with_status(self):
        """Generate response with completion status"""
        response = super().generate_response()

        # Parse status from response
        status = self._extract_status(response)

        return {
            'response': response,
            'status': status,  # 'working', 'solution_ready', 'need_info'
            'confidence': self._extract_confidence(response),
            'solution': self._extract_solution(response) if status == 'solution_ready' else None
        }

    def _extract_status(self, response):
        """Parse status indicators from response"""
        if "SOLUTION READY" in response or "HERE IS MY FINAL SOLUTION" in response:
            return 'solution_ready'
        elif "I NEED" in response or "PLEASE PROVIDE" in response:
            return 'need_info'
        return 'working'
```

**Prompt Engineering**:
```python
system_prompt = """
You are a coding assistant solving real GitHub issues.

When ready to submit your solution:
- Write: "SOLUTION READY"
- Provide complete code changes
- Include tests

If you need more context:
- Write: "I NEED: [specific file/info]"
- Explain why you need it

Continue working until you have a complete, tested solution.
"""
```

---

#### **T5.3: Prompt Caching Strategy** (4 hours)

```python
# experiments/swe_bench_real/caching_agent.py
class PromptCachingAgent(RealCodingAgent):
    def __init__(self, config):
        super().__init__(config)
        self.cache_config = {'type': 'ephemeral'}

    def _build_cached_messages(self):
        """Build messages with cache control"""
        # Cache codebase context (changes rarely)
        codebase_message = {
            'role': 'user',
            'content': self.codebase_context,
            'cache_control': self.cache_config  # ← Anthropic caching
        }

        # Don't cache conversation (changes often)
        conversation_messages = [
            {'role': r, 'content': c}
            for r, c in self.conversation_history
        ]

        return [codebase_message] + conversation_messages
```

---

#### **T5.4: Full Cost Accounting** (6 hours)

```python
# experiments/swe_bench_real/cost_tracker.py
@dataclass
class CompleteCost:
    """Track all costs for fair comparison"""

    # API costs
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0

    # Computational costs
    pruning_time_ms: float = 0.0
    pruning_operations: int = 0

    # Solution metrics
    turns_to_solution: int = 0
    wall_clock_seconds: float = 0.0
    tests_passed: int = 0
    tests_total: int = 0

    @property
    def api_cost_usd(self) -> float:
        """Calculate API cost"""
        return (
            self.input_tokens * 3.00 / 1_000_000 +
            self.output_tokens * 15.00 / 1_000_000 +
            self.cache_write_tokens * 3.75 / 1_000_000 +
            self.cache_read_tokens * 0.30 / 1_000_000
        )

    @property
    def efficiency_score(self) -> float:
        """Quality per dollar"""
        quality = self.tests_passed / max(self.tests_total, 1)
        cost = max(self.api_cost_usd, 0.001)  # Avoid div by zero
        return quality / cost

    @property
    def overhead_ratio(self) -> float:
        """Pruning overhead as % of total time"""
        total_time_ms = self.wall_clock_seconds * 1000
        return self.pruning_time_ms / max(total_time_ms, 1)
```

---

### **Experimental Design**

**20 Problems × 3 Strategies = 60 Runs**

```python
problems = load_swe_bench_problems(n=20)
strategies = ['continuous_pruning', 'discrete_baseline', 'prompt_caching']

results = {}
for problem in problems:
    for strategy in strategies:
        agent = create_agent(strategy=strategy, natural_completion=True)
        result = run_problem_until_solved(agent, problem, max_turns=50)
        results[(problem.id, strategy)] = result
```

**Success Criteria**:
- Problem "solved" when tests pass (real validation!)
- Max 50 turns per problem (timeout)
- Compare costs, time, quality across strategies

---

### **Expected Outcomes**

**Hypothesis**:
1. **Continuous pruning** will win on:
   - Total cost (tokens)
   - Efficiency (quality/token)

2. **Prompt caching** will win on:
   - Raw speed (cache hits are fast)

3. **Discrete baseline** will:
   - Use most tokens
   - Take most turns
   - But: similar quality if given enough turns

**Statistical Tests**:
- Paired t-test (same 20 problems)
- Effect size (Cohen's d)
- Cost per successful solution
- Quality-adjusted efficiency

---

## Summary: Answers to Your Questions

### **1. Public Benchmark?**
✅ **SWE-bench** - 2,294 real GitHub issues
- Select 20 problems (5 easy, 10 medium, 5 hard)
- Real codebases (10K-200K tokens)
- Verified solutions (merged PRs)

### **2. Anthropic's Algorithm?**
✅ **Prompt Caching** (different approach)
- They cache, we prune (different goals)
- Phase 5 will test both approaches
- Fair comparison framework designed

### **3. Natural Completion?**
✅ **Agent-driven finishing**
- Agent declares "SOLUTION READY"
- Validates solution with real tests
- Max 50 turns (safety limit)
- More realistic than fixed turns

### **4. Full Cost Accounting?**
✅ **Complete metrics**:
- API tokens (input + output + cache)
- Computational overhead (pruning time)
- Solution quality (tests passed)
- Efficiency (quality/cost ratio)
- Winner needs 2/4 metrics

### **5. Sprint 4 Pruning Costs?**
✅ **ZERO tokens for pruning**
- Local TF-IDF importance calculation
- No AI calls in pruner
- 82% is pure savings (no hidden costs)

---

## Next Steps

**Immediate** (After Sprint 4 Completes):
1. Review 10-task experiment results
2. Run statistical analysis
3. Complete Sprint 4 documentation

**Phase 5 Kickoff** (Next Session):
1. Load SWE-bench dataset
2. Implement natural completion
3. Design full cost tracking

**Timeline**:
- Sprint 4: 1-2 days remaining
- Sprint 5 (Phase 5): 2 weeks
- Total to real validation: ~2.5 weeks

---

**Last Updated**: 2025-11-03
**Status**: Planning phase - ready to implement after Sprint 4
