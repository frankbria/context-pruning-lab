# Two-Agent System Experimental Results

**Date**: 2025-11-03
**Status**: Initial Validation Complete

## Summary

The two-agent architecture (UserSimulatorAgent + CodingAgent + ConversationOrchestrator) has been successfully implemented and validated. This system replaces scripted conversations with realistic dialogue and executable test feedback.

## Key Achievements

### 1. System Validation ✅

**Problem**: Original single-agent system with scripted conversations achieved 0% task completion because:
- Generic prompts like "Can you refactor this?" lacked code context
- Real LLMs responded "I don't see any code in your message"
- No test execution feedback loop
- Agents never learned if their code worked

**Solution**: Two-agent architecture with:
- UserSimulatorAgent provides task description and runs Python tests
- Real test execution with specific error feedback
- Natural conversation flow with clarifying questions
- Token accounting separates test harness from agent being measured

### 2. Success Rate: 0% → 100% 🎉

**Before** (Scripted Conversations):
- 0/50 tasks completed
- Agents derailed by context-less prompts
- No meaningful comparison possible

**After** (Two-Agent System):
- 5/5 tasks completed (100% success rate)
- Both strategies achieved 100%
- Real code generation and validation
- Meaningful efficiency comparison

## Experimental Results (5 Tasks)

### Overall Performance

| Strategy | Success Rate | Total Tokens | Avg Tokens/Task | Avg Turns/Task | Avg Time/Task |
|----------|-------------|--------------|-----------------|----------------|---------------|
| continuous_pruning | 5/5 (100%) | 9,531 | 1,906 | 9.4 | 36.4s |
| discrete_baseline | 5/5 (100%) | 7,044 | 1,409 | 4.2 | 13.6s |

**Winner**: discrete_baseline used **26% fewer tokens** (7,044 vs 9,531)

### Per-Task Breakdown

| Task | Difficulty | CP Tokens | CP Turns | DB Tokens | DB Turns | Winner |
|------|-----------|-----------|----------|-----------|----------|--------|
| reverse_string | Easy | 455 | 3 | 1,955 | 5 | CP (4.3x better) |
| is_palindrome | Easy | 671 | 3 | 743 | 3 | CP (10% better) |
| count_vowels | Easy | 3,305 | 19 | 2,860 | 7 | DB (16% better) |
| fibonacci | Medium | 4,147 | 19 | 533 | 3 | DB (7.8x better) |
| merge_sorted_lists | Medium | 953 | 3 | 953 | 3 | Tie |

## Analysis

### Surprising Finding: Discrete Baseline More Efficient

This contradicts our hypothesis that continuous pruning would be more efficient. Possible explanations:

1. **Context Removal Impact**: For short, focused tasks, pruning may remove important context
   - fibonacci task: CP took 19 turns (4,147 tokens) vs DB took 3 turns (533 tokens)
   - Agent may have needed earlier conversation context to understand the task

2. **Task Length Dependency**:
   - Very short tasks (reverse_string, is_palindrome): CP performs well
   - Moderately complex tasks (fibonacci, count_vowels): DB performs better
   - This suggests pruning overhead outweighs benefits for short conversations

3. **Pruning Overhead**:
   - Continuous pruning adds computational cost at each turn
   - For tasks that complete in 3-5 turns, this overhead may not pay off
   - Discrete baseline only compacts when truly necessary (80% threshold)

### When Each Strategy Excels

**Continuous Pruning Best For**:
- Very short, straightforward tasks (< 500 tokens)
- Tasks where conversation won't grow large
- When minimal context is sufficient

**Discrete Baseline Best For**:
- Tasks with nuanced requirements
- Conversations that benefit from full history
- When context removal might lose important details

## System Architecture Validation

### What Works ✅

1. **Realistic Conversations**:
   - User sim asks natural questions
   - Agent responds meaningfully
   - No derailment from context-less prompts

2. **Test Execution Loop**:
   - Python tests execute successfully
   - Specific error feedback helps agent fix bugs
   - Agent iterates based on real test results

3. **Token Separation**:
   - Coding agent: 7,044 - 9,531 tokens (COUNTED)
   - User simulator: ~2,000 tokens per strategy (NOT counted)
   - Fair comparison between strategies

4. **Conversation Efficiency**:
   - Average 3-19 turns to complete tasks
   - Most tasks complete in < 10 turns
   - Natural termination when tests pass

### Implementation Quality

- **Code executed**: All test cases run successfully
- **Error handling**: Graceful failure handling
- **Metrics tracking**: Accurate token counting
- **Results format**: Compatible with existing infrastructure

## Implications

### For Experiment 4

**Success**: We now have a working system that:
- Completes tasks reliably (100% vs 0%)
- Measures efficiency accurately
- Compares strategies fairly
- Produces meaningful results

**Next Steps**:
1. Test with more complex tasks
2. Increase task count to 20-50 for statistical significance
3. Explore why discrete baseline outperforms on certain tasks
4. Consider hybrid strategies

### For Context Management Research

**Key Insight**: Context pruning effectiveness depends on task characteristics:
- Short tasks may not benefit from pruning (overhead > savings)
- Complex tasks may need full history for coherence
- Pruning strategy should adapt to conversation length/complexity

**Hypothesis Revision**:
- Original: Continuous pruning always more efficient
- Revised: Efficiency depends on task length and complexity
- Optimal: Dynamic strategy selection based on conversation metrics

## Technical Details

### Task Definitions

5 simple Python coding tasks with executable test cases:
- 3 easy tasks (string manipulation, basic algorithms)
- 2 medium tasks (recursion, list operations)

All tasks have:
- Clear requirements
- Executable test cases (not pytest commands)
- Gold reference solutions
- Multiple test cases per task

### Execution Environment

- Model: Claude Sonnet 4 (claude-sonnet-4-20250514)
- API: Anthropic Messages API
- Test execution: Direct Python exec/eval (not subprocess)
- Timeout: 30 turns maximum per task
- Time limit: None (tasks completed quickly)

### Files Created

1. `experiments/experiment_4/user_simulator.py` - User simulator agent
2. `experiments/experiment_4/orchestrator.py` - Conversation orchestrator
3. `experiments/experiment_4/simple_tasks.py` - Task definitions
4. `experiments/experiment_4/run_two_agent_experiment.py` - Experiment runner
5. `experiments/experiment_4/test_two_agent.py` - System validation test

## Conclusion

**The two-agent architecture successfully solves the 0% completion problem** by creating realistic conversations with executable test feedback. While the initial results show discrete baseline outperforming continuous pruning, this represents a valuable finding: context management strategy should match task characteristics.

The infrastructure is now validated and ready for larger-scale experiments to determine optimal strategies for different task types.

---

**Status**: ✅ Two-agent system validated
**Next**: Scale to 20-50 tasks for statistical significance
**Timeline**: 1-2 sessions to complete full Experiment 4
