# Two-Agent Architecture for Context Management Experiments

**Date**: 2025-11-03
**Status**: Design Proposal

## Problem Statement

Current single-agent design with scripted prompts fails because:
1. Real LLMs respond to context literally ("refactor THIS" → "what code?")
2. No test execution feedback loop
3. Generic prompts derail conversation
4. Can't measure pure context management efficiency

## Solution: User Simulator + Coding Agent

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  EXPERIMENT HARNESS                                         │
│                                                             │
│  ┌───────────────────────────┐  ┌──────────────────────┐   │
│  │  User Simulator Agent     │  │  Coding Agent [SUT]  │   │
│  │  ─────────────────────    │  │  ───────────────────  │   │
│  │  Role: Product Owner/QA   │  │  Role: Developer     │   │
│  │                           │  │                      │   │
│  │  Responsibilities:        │  │  Responsibilities:   │   │
│  │  • Provide task spec      │  │  • Understand task   │   │
│  │  • Answer questions       │◄─┤  • Ask questions     │   │
│  │  • Run tests              ├─►│  • Generate code     │   │
│  │  • Give feedback          │  │  • Iterate on feedback│  │
│  │  • Guide conversation     │  │  • Manage context    │   │
│  │                           │  │                      │   │
│  │  Tokens: NOT counted      │  │  Tokens: COUNTED     │   │
│  └───────────────────────────┘  └──────────────────────┘   │
│              ↓                           ↓                  │
│     [Python test executor]    [Context Manager Strategy]   │
│     [Gold solution access]    [Continuous vs Baseline]     │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. UserSimulatorAgent

**Purpose**: Intelligent user that guides coding agent to correct solution

**System Prompt**:
```
You are a product owner/QA engineer working with a developer (AI coding agent).

Your goal: Guide the developer to solve this coding task by:
1. Providing clear requirements when asked
2. Running tests on their code and reporting results
3. Answering clarification questions
4. Giving helpful feedback on failures
5. Confirming when solution is correct

Task: {task_description}
Tests: {test_cases}
Gold Solution (for reference only): {gold_solution}

Be helpful but realistic. Don't give away the solution, but guide through:
- Clarifying requirements
- Pointing out test failures
- Suggesting areas to investigate
- Confirming correct solutions
```

**Key Methods**:
```python
class UserSimulatorAgent:
    def __init__(self, task, api_key):
        self.task = task
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history = []

    def respond_to_agent(self, agent_message: str) -> str:
        """
        Generate user response to agent's message.

        - If agent asks question: Answer based on task spec
        - If agent provides code: Run tests and report results
        - If agent seems stuck: Provide hint
        - If tests pass: Confirm success
        """
        pass

    def run_tests(self, code: str) -> TestResult:
        """Execute tests against agent's code."""
        pass

    def extract_code_from_message(self, message: str) -> Optional[str]:
        """Extract code blocks from agent's message."""
        pass
```

### 2. ConversationOrchestrator

**Purpose**: Manage dialogue between two agents

**Flow**:
```python
class ConversationOrchestrator:
    def __init__(self, user_sim: UserSimulatorAgent,
                 coding_agent: RealCodingAgent):
        self.user_sim = user_sim
        self.coding_agent = coding_agent

    def run_conversation(self, max_turns: int = 50) -> ConversationResult:
        """
        Orchestrate conversation until solution found or max turns.

        Flow:
        1. User sim provides initial task description
        2. Loop until done:
           a. Coding agent responds
           b. Extract any code from response
           c. User sim responds (runs tests if code present)
           d. Check if tests passed
        3. Return results with metrics
        """

        # Initial task
        task_description = self.user_sim.get_initial_task_message()
        self.coding_agent.receive_message(task_description)

        for turn in range(max_turns):
            # Coding agent's turn
            agent_response = self.coding_agent.generate_response()

            # User simulator's turn (runs tests if needed)
            user_response = self.user_sim.respond_to_agent(agent_response)

            # Check completion
            if self.user_sim.is_task_complete():
                return ConversationResult(success=True, turns=turn+1)

            # Continue conversation
            self.coding_agent.receive_message(user_response)

        return ConversationResult(success=False, turns=max_turns)
```

### 3. Token Accounting

**Critical**: Only count coding agent's tokens

```python
class TokenMetrics:
    """Separate token tracking for each agent."""

    def __init__(self):
        self.user_sim_tokens = 0      # NOT counted in comparison
        self.coding_agent_tokens = 0  # COUNTED - this is what we measure

    def record_user_sim_turn(self, input_tokens, output_tokens):
        """Track but don't include in efficiency metrics."""
        self.user_sim_tokens += input_tokens + output_tokens

    def record_coding_agent_turn(self, input_tokens, output_tokens):
        """This is what we compare between strategies!"""
        self.coding_agent_tokens += input_tokens + output_tokens
```

### 4. Test Execution

**In UserSimulatorAgent**:

```python
def run_tests(self, code: str) -> TestResult:
    """
    Execute test cases against agent's code.

    Returns detailed results:
    - All tests passed?
    - Which tests failed?
    - Error messages
    - Expected vs actual outputs
    """

    # Create safe execution environment
    namespace = {'__name__': '__main__'}

    try:
        # Execute code
        exec(code, namespace)

        # Run each test
        results = []
        for test_case in self.task.test_cases:
            try:
                actual = eval(test_case.call, namespace)
                passed = actual == test_case.expected
                results.append(TestCaseResult(
                    passed=passed,
                    expected=test_case.expected,
                    actual=actual,
                    test_input=test_case.input
                ))
            except Exception as e:
                results.append(TestCaseResult(
                    passed=False,
                    error=str(e),
                    test_input=test_case.input
                ))

        return TestResult(
            all_passed=all(r.passed for r in results),
            test_cases=results
        )

    except Exception as e:
        return TestResult(
            all_passed=False,
            compile_error=str(e)
        )
```

## Expected Benefits

### 1. Realistic Conversations ✅
```
User Sim: "Fix the reverse_string function - it fails on empty strings"
Coding Agent: "What's the current implementation?"
User Sim: "Here's the buggy code: def reverse_string(s): return s[0::-1]"
Coding Agent: "I see the issue - accessing s[0] on empty string. Here's the fix..."
User Sim: *runs tests* "Perfect! All tests pass now."
```

### 2. Test-Driven Development ✅
```
Coding Agent: "Here's my solution: [code]"
User Sim: *runs tests* "Failed 2/10 tests. Empty string returns None instead of ''.
          Input 'hello' raised AttributeError: 'NoneType' has no attribute 'reverse'"
Coding Agent: "I see - let me fix the None handling..."
```

### 3. Natural Guidance ✅
```
Coding Agent: "Should I use recursion or iteration?"
User Sim: "Either works, but consider performance for long strings."
Coding Agent: "I'll use iteration for O(n) time complexity..."
```

### 4. Accurate Metrics ✅
- **Coding Agent**: 8,000 tokens (continuous pruning) vs 15,000 tokens (baseline)
  - This is the REAL efficiency comparison
- **User Sim**: 5,000 tokens (not counted - just test harness overhead)
  - Similar for both strategies, so doesn't affect comparison

## Implementation Plan

### Phase 1: Core Components (Immediate)
1. ✅ Design document (this file)
2. Implement UserSimulatorAgent class
3. Implement ConversationOrchestrator
4. Add test execution capability
5. Update token metrics tracking

### Phase 2: Integration (Next)
6. Modify experiment harness to use orchestrator
7. Update metrics calculator to separate token types
8. Remove scripted message generation
9. Test with 1 task end-to-end

### Phase 3: Validation (Final)
10. Run 10-task benchmark
11. Verify >0% completion rate
12. Verify token metrics accurate
13. Run full 50-task experiment

## Example Conversation Flow

```
Turn 1 (User Sim → Coding Agent):
"I need help fixing a bug in the reverse_string() function.
It raises IndexError when given an empty string."

Turn 2 (Coding Agent → User Sim):
"I'd be happy to help! Could you share the current implementation
so I can see what's causing the IndexError?"

Turn 3 (User Sim → Coding Agent):
"Here's the buggy code:
```python
def reverse_string(s):
    result = ""
    for i in range(len(s)-1, -1, -1):
        result += s[i]
    return result
```
When called with empty string '', it returns '' but the loop
should handle this case properly."

Turn 4 (Coding Agent → User Sim):
"I see the issue! Here's the fix:
```python
def reverse_string(s):
    if not s:  # Handle empty string
        return s
    result = ""
    for i in range(len(s)-1, -1, -1):
        result += s[i]
    return result
```"

Turn 5 (User Sim → Coding Agent):
*runs tests*
"Great! All tests pass:
✓ reverse_string('') == ''
✓ reverse_string('a') == 'a'
✓ reverse_string('hello') == 'olleh'
✓ reverse_string('python') == 'nohtyp'

Solution confirmed correct!"

RESULT: Success in 5 turns
Coding agent tokens: ~800
User sim tokens: ~600 (not counted)
```

## Success Criteria

### Minimum Viable
- [ ] Conversations stay on track (no "what code?" derailments)
- [ ] Test feedback works (agent learns from failures)
- [ ] >20% task completion rate
- [ ] Token metrics only count coding agent

### Target
- [ ] >50% task completion rate
- [ ] Natural conversation flow
- [ ] Accurate token efficiency comparison
- [ ] Clear winner between strategies

### Stretch
- [ ] >80% task completion rate
- [ ] Average <20 turns per solution
- [ ] Continuous pruning demonstrates efficiency gains
- [ ] Results publishable

## API Cost Implications

### Current (Single Agent)
- 1 task = 1 agent × 20 turns × ~200 tokens = ~4K tokens = $0.02
- 50 tasks = $1.00 per strategy

### Proposed (Two Agents)
- 1 task = 2 agents × 20 turns × ~200 tokens = ~8K tokens = $0.04
- 50 tasks = $2.00 per strategy

**BUT**: We expect:
- Higher success rate (fewer wasted runs)
- Fewer total tokens due to focused conversations
- More valuable results (actual task completion)

**Net**: Slightly higher cost but MUCH better quality

## Risks and Mitigations

### Risk 1: User Sim Gives Away Solution
**Mitigation**: Prompt engineering to guide, not solve
- Provide hints, not answers
- Point to failing tests, not fixes
- Ask leading questions

### Risk 2: Infinite Loops
**Mitigation**:
- Max turns limit (50)
- Detect repeated failures (3x same error = hint)
- Escalating hints after stuck

### Risk 3: Token Explosion
**Mitigation**:
- Track both agents separately
- Alert if user sim tokens > 2x coding agent
- Optimize user sim prompt if needed

## References

- Solution verification: `docs/SOLUTION_VERIFICATION_STRATEGY.md`
- Current agent: `experiments/experiment_4/agent.py`
- Experiment harness: `experiments/swe_bench_extended/harness.py`

---

**Status**: Design complete, ready for implementation
**Next**: Implement UserSimulatorAgent class
**Timeline**: 1-2 sessions to implement and validate
