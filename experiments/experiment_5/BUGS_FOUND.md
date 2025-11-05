# Bugs Found in Sprint 5 Redux Experiments

**Date**: 2025-11-04
**Context**: Investigating anomalies in continuous pruning vs discrete baseline comparison
**Status**: Under investigation

---

## Summary of Issues

1. **BUG-001**: `tokens_at_first_compaction` captures wrong value (AFTER compaction instead of BEFORE)
2. **BUG-002**: `context_size_final` = 0 for continuous pruning (context appears empty at end)
3. **BUG-003**: API error "208454 tokens > 200000" for discrete baseline but success=true
4. **MISSING**: No conversation logs - can't review actual agent behavior

---

## BUG-001: tokens_at_first_compaction Captures Wrong Value

### Location
`experiments/experiment_5/experiment_runner.py:293`

### Issue
```python
if not compaction_triggered:
    compaction_triggered = True
    first_compaction_tokens = context_size  # BUG: This is AFTER compaction
```

When compaction is detected (line 289), the event has already occurred. So `context_size` is the size AFTER compaction reduction, not BEFORE.

### Evidence
```json
{
  "tokens_at_first_compaction": 45775,    // This is tokens_after!
  "compaction_history": [
    {
      "turn": 31,
      "tokens_before": 123844,           // This is the correct value
      "tokens_after": 45775
    }
  ]
}
```

### Impact
- Misleading metrics in results
- Makes it look like compaction triggered earlier than it actually did
- Not affecting actual experiment (just reporting bug)

### Fix
```python
if not compaction_triggered:
    compaction_triggered = True
    first_compaction_tokens = max_context  # Use max_context instead
```

### Priority
**LOW** - Doesn't affect experiment validity, just reporting accuracy

---

## BUG-002: context_size = 0 for Continuous Pruning

### Location
- `experiments/experiment_4/agent.py:303` (get_context_stats)
- `pruner.py:460` (get_total_tokens)

### Issue
Results show `context_size_final: 0` and `context_size_max: 0` for continuous pruning:

```json
{
  "strategy": "continuous_pruning",
  "context_size_final": 0,        // Should not be 0!
  "context_size_max": 0,          // Problem 1: even max is 0
  "pruning_operations": 41,       // But it did 41 pruning operations?
  "total_tokens": 268500          // And sent 268K tokens?
}
```

### Investigation Path

**Step 1**: Check how context_size is calculated

```python
# agent.py:303
'context_size': self.context_manager.get_total_tokens()

# pruner.py:460
def get_total_tokens(self) -> int:
    return sum(item.token_count for item in self.context)
```

**Step 2**: If returning 0, means `self.context` is empty

**Hypothesis**: One of these scenarios:
1. **Too aggressive pruning** - ContinuousPruner removes ALL items including recent ones
2. **Context cleared somewhere** - Context gets wiped after experiment or each interaction
3. **Wrong context reference** - Getting context from wrong object instance
4. **Token counting bug** - Context has items but all have token_count=0

### Evidence Supporting Hypothesis #1 (Aggressive Pruning)
- Continuous pruning did 41 pruning operations (one per turn)
- Sent only 268K tokens vs 3.9M for discrete baseline (15x less)
- Could be pruning TOO much, keeping context nearly empty

### Evidence Against Hypothesis #1
- Agent successfully completed both problems
- Can't solve problems with no context
- Must have SOME context to work with

### Debugging Needed
1. Add logging to `_prune_context` to see what's being removed
2. Check context size BEFORE and AFTER each prune operation
3. Verify that context items are actually being created with add_interaction
4. Check if context is cleared anywhere (search for `self.context = []` or `.clear()`)

### Impact
**MEDIUM** - Metrics are wrong but experiment appears valid
- Real token usage (total_tokens) is accurate
- Agent completed tasks successfully
- Context tracking is broken but context management may be working

### Priority
**HIGH** - Need to understand if continuous pruning is actually working correctly

---

## BUG-003: API Error but Success=True

### Location
Seen in experiment log for discrete_baseline

### Issue
```
Claude API error: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'prompt is too long: 208454 tokens > 200000 maximum'}, 'request_id': 'req_011CUohczFduMrvCFyY61U62'}
✓ SUCCESS
```

The log shows an API error about exceeding the 200K token limit, but the result shows `success: true`.

### Evidence
```json
{
  "instance_id": "psf__requests-1963",
  "strategy": "discrete_baseline",
  "success": true,              // Marked successful
  "turns": 41,
  "total_tokens": 3938019,
  "context_size_max": 123844,   // Never reached 200K in context
  "compaction_events": 1
}
```

### Analysis

**Timing**: The error likely occurred at turn 40 (after turn 31 compaction reduced context to 45K, it grew back up approaching threshold again)

**Recovery**: The agent caught the exception (agent.py:158-161):
```python
except Exception as e:
    # Handle API errors gracefully
    response_text = f"Error generating response: {str(e)}"
    print(f"Claude API error: {e}")
```

**Why success=true**: The experiment_runner marks success based on `turns > 1` (line 311), not on whether all API calls succeeded.

### Impact
- One turn failed silently
- Agent continued and completed anyway
- Success metric may be misleading

### Questions
1. How did context reach 208K if max recorded was 123K?
2. Was this during context building (_build_context_messages)?
3. Did the error happen DURING compaction check?

### Priority
**MEDIUM** - Need to understand but doesn't invalidate results

---

## MISSING: No Conversation Logs

### Issue
The experiment doesn't save conversation transcripts. We can't review:
- What the agent actually said
- Whether responses make sense
- If it's doing real coding work or generating nonsense
- Quality of solutions proposed

### Impact
**HIGH** - Can't validate agent behavior

### What We Need
1. Save full conversation history for each problem
2. Include:
   - User messages (problem descriptions, file contents)
   - Agent responses
   - Timestamps
   - Token counts per message
   - Which files were read when

### Implementation Needed
```python
# In experiment_runner.py
conversation_log = []

# After each agent response
conversation_log.append({
    'turn': turns,
    'user_message': initial_message or file_message,
    'agent_response': response,
    'tokens_before': stats['context_size'],
    'timestamp': datetime.now().isoformat()
})

# Save to file
with open(f'results/experiment_5/conversation_{instance_id}_{strategy}.json', 'w') as f:
    json.dump(conversation_log, f, indent=2)
```

### Priority
**CRITICAL** - Need this to validate experiment properly

---

## Validation Checklist

To properly validate the experiment, we need to:

### Code Review ✅
- [x] Verify agent calls real Claude API (confirmed: agent.py:144)
- [x] Verify agent sends/receives actual messages (confirmed: token counts non-zero)
- [x] Check for any mock/fake data generation (none found)

### Conversation Review ❌
- [ ] Review actual conversations - BLOCKED (no logs)
- [ ] Verify agent does real coding work
- [ ] Check response quality
- [ ] Confirm files were actually read

### Metrics Validation ⚠️
- [x] Total tokens matches API calls (yes - 3.9M and 268K)
- [x] Turn counts make sense (41 and 2 turns)
- [ ] Context sizes accurate (BUG-002: continuous shows 0)
- [ ] Compaction triggers correctly (BUG-001: wrong timing captured)

### Behavior Verification ❌
- [ ] Agent explored codebase appropriately
- [ ] Agent proposed sensible solutions
- [ ] Agent responded to file contents
- [ ] Conversations look like real coding sessions

---

## Next Steps

### Immediate (This Session)
1. **Fix BUG-001** - Easy one-line fix
2. **Debug BUG-002** - Add logging to pruning to see what's happening
3. **Add conversation logging** - Critical for validation

### Testing
1. Run single problem with logging enabled
2. Review conversation transcript
3. Verify metrics match reality
4. Check that pruning isn't too aggressive

### Before Scaling to 20 Problems
1. Confirm bugs are fixed
2. Validate on 3-5 problems
3. Review at least one full conversation
4. Ensure metrics are accurate

---

## Questions for User

1. **Do you want us to re-run the experiment with fixes and logging?**
   - Pro: Get accurate metrics and conversation logs
   - Con: Another $60-90 cost, 60-90 minutes runtime

2. **Should we review the existing results despite bugs?**
   - Pro: Results may still be valid (bugs are in reporting, not logic)
   - Con: Can't be certain without conversation logs

3. **Priority: Fix bugs vs validate existing results?**
   - Option A: Fix bugs first, then re-run small validation
   - Option B: Accept results with caveats, document limitations

---

## Impact on Results

### What's Still Valid ✅
- Both strategies completed problems (success=true)
- Token usage is accurate (comes from API, not our calculations)
- Turn counts are accurate (we counted them)
- Relative comparison (continuous used 15x fewer tokens)

### What's Questionable ⚠️
- Context size metrics for continuous pruning (reports 0)
- Exact timing of compaction trigger (off by one turn)
- Whether one API call failed during discrete baseline

### What's Unknown ❌
- Actual agent behavior and response quality
- Whether solutions make sense
- If the agent is really "coding" or just generating text
- Quality comparison between strategies

---

**Status**: Investigation in progress
**Recommendation**: Fix bugs, add logging, run 2-3 problem validation before scaling to 20
