# Sprint 5 Redux: Real Context Management Validation

**Status**: Planning
**Goal**: Test continuous pruning vs discrete compaction under **realistic** conditions where compaction actually triggers
**Critical Fix**: Sprint 5 tested 0 compaction cycles. This tests 2-4+ cycles per task.

---

## Core Problem to Solve

**Research Question**: Does continuous pruning prevent degradation after 2-3 discrete compaction cycles?

**Sprint 5 Failed Because**:
- Threshold: 32K tokens (never reached)
- Tasks: Simple single-file problems (800-6K tokens)
- Result: Zero compaction events = invalid test

**Sprint 5 Redux Must**:
- Threshold: 125K tokens (realistic for 200K context window)
- Tasks: Multi-file coding with codebase reading (100K-150K tokens)
- Result: 2-4 compaction cycles per task = valid test

---

## Configuration Changes

### Context Parameters
```python
# OLD (Sprint 5 - INVALID)
target_context_size = 40_000      # 40K tokens
compaction_threshold = 0.80       # Triggers at 32K
# Result: Never triggered

# NEW (Sprint 5 Redux - REALISTIC)
target_context_size = 156_250     # ~156K tokens (leaves room in 200K window)
compaction_threshold = 0.80       # Triggers at 125K
# Result: Will trigger 2-4x per realistic task
```

### Expected Task Characteristics
```
Per-task requirements:
- 30-50 conversation turns
- Read 10-30 source files from codebase (30-60K tokens)
- Multiple test/debug cycles
- Context naturally grows to 120K-150K tokens
- Baseline: 2-4 compaction events per task
- Continuous: 30-50 pruning operations per task
```

---

## Two Implementation Paths

### Path A: Real SWE-bench (Recommended)

**Pros**:
- Authentic real-world problems
- Validates with actual codebases
- Publication-ready results

**Cons**:
- Setup complexity (git clones, test execution)
- Longer runtime (12-24 hours for 20 tasks)
- Higher cost ($50-150)

**Tasks**:
1. Install SWE-bench dataset
2. Select 20 problems (balanced difficulty/repos)
3. Implement file reading system
4. Run real pytest tests
5. Execute experiment

**Estimated Time**: 3-4 sessions (12-16 hours)

---

### Path B: Realistic Multi-File Scenarios (Faster)

**Pros**:
- Faster iteration (4-6 hours for 20 tasks)
- Controlled complexity
- Still tests compaction properly
- Lower cost ($20-40)

**Cons**:
- Not "real" problems
- Less publishable
- Need to design scenarios carefully

**Task Design**:
```python
@dataclass
class RealisticScenario:
    """Multi-file coding scenario that triggers compaction"""

    # Codebase (30-50 files, 30K-50K tokens)
    codebase_files: Dict[str, str]  # {path: content}

    # Problem requiring cross-file changes
    problem: str
    test_cases: List[TestCase]

    # Force codebase reading
    requires_reading: List[str]  # Files agent must read

    # Target metrics
    expected_turns: int = 40
    expected_context_tokens: int = 130_000
    expected_compactions: int = 3

# Example scenarios:
1. "Add authentication middleware to Flask app" (20 files, needs 8 reads)
2. "Fix race condition in async worker pool" (15 files, needs 12 reads)
3. "Refactor database layer to use connection pooling" (25 files, needs 15 reads)
4. "Add caching layer with Redis integration" (18 files, needs 10 reads)
5. "Implement rate limiting with distributed state" (22 files, needs 14 reads)
```

**Estimated Time**: 2 sessions (8-10 hours)

---

## Recommended Approach: Hybrid Path

### Phase 1: Quick Validation (1-2 sessions)
1. Create 5 realistic multi-file scenarios
2. Run with 125K threshold
3. Verify compaction triggers 2-3x per task
4. Confirm continuous pruning prevents degradation

### Phase 2: Full SWE-bench (2-3 sessions)
1. If Phase 1 shows clear results → proceed to SWE-bench
2. Select 20 real problems
3. Run full validation
4. Prepare results for publication

---

## Implementation Tasks

### T5R.1: Update Configuration (1 hour)
```python
# experiments/experiment_4/agent.py
@dataclass
class AgentConfig:
    strategy: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    target_context_size: int = 156_250  # ← CHANGED
    api_key: Optional[str] = None
```

### T5R.2: Create Realistic Scenarios (3-4 hours)
```python
# experiments/experiment_5/realistic_scenarios.py

def create_flask_auth_scenario() -> RealisticScenario:
    """
    Scenario: Add JWT authentication to Flask app

    Codebase: 20-file Flask application
    - app/routes/*.py (8 files)
    - app/models/*.py (4 files)
    - app/utils/*.py (3 files)
    - tests/*.py (5 files)

    Problem: Add JWT auth middleware, protect routes, add login endpoint
    Expected: Agent must read 6-8 files, make changes to 4 files
    Context: Will grow to ~120K tokens, trigger 2-3 compactions
    """
    return RealisticScenario(
        codebase_files=generate_flask_codebase(),
        problem="""Add JWT authentication to this Flask app:
        1. Install PyJWT and implement token generation/validation
        2. Add /login endpoint that issues tokens
        3. Create @require_auth decorator for protected routes
        4. Protect /api/users and /api/admin routes
        5. Add tests for auth flow
        """,
        test_cases=[...],
        requires_reading=["app/routes/users.py", "app/models/user.py", ...],
        expected_turns=35,
        expected_context_tokens=125_000
    )
```

### T5R.3: Implement File Reading Agent Enhancement (2 hours)
```python
# experiments/experiment_5/codebase_agent.py

class CodebaseAwareAgent(RealCodingAgent):
    """Agent that can read files from a codebase"""

    def __init__(self, config: AgentConfig, codebase: Dict[str, str]):
        super().__init__(config)
        self.codebase = codebase
        self.files_read = []

    def read_file(self, path: str) -> str:
        """Simulate reading a file from the codebase"""
        if path not in self.codebase:
            return f"Error: File {path} not found"

        content = self.codebase[path]
        self.files_read.append(path)

        # Add to context as a tool result
        self.add_tool_result(f"read_file({path})", content)
        return content
```

### T5R.4: Run Experiment with Compaction Tracking (2 hours)
```python
# Track compaction events
for task in scenarios:
    result = run_task_with_strategy(task, "discrete_baseline")

    # Verify compaction triggered
    assert result.compaction_count >= 2, \
        f"Task {task.id} only had {result.compaction_count} compactions!"

    # Measure degradation
    quality_by_compaction = [
        result.quality_before_compaction_1,
        result.quality_after_compaction_1,
        result.quality_before_compaction_2,
        result.quality_after_compaction_2,
    ]

    degradation = calculate_degradation(quality_by_compaction)
```

---

## Success Metrics

### Minimum Viable
- ✅ Average 2+ compactions per task (baseline)
- ✅ Context reaches 120K+ tokens per task
- ✅ Continuous pruning prevents degradation across compactions
- ✅ Statistical significance (p < 0.05)

### Target
- ✅ Average 3-4 compactions per task
- ✅ Context reaches 140K+ tokens
- ✅ Degradation quantified (baseline drops 20%+ quality after compaction 2)
- ✅ Continuous pruning maintains >95% quality throughout

---

## Resource Estimates

### Path B (Realistic Scenarios)
- **Development**: 8-10 hours
- **Execution**: 4-6 hours (5 scenarios × 2 strategies × 40 min)
- **Cost**: $20-40 (estimated 400K-600K tokens)
- **Timeline**: 2-3 sessions

### Path A (SWE-bench)
- **Development**: 12-16 hours (includes git/test integration)
- **Execution**: 12-24 hours (20 tasks × 2 strategies × 30-60 min)
- **Cost**: $50-150 (estimated 2M-4M tokens)
- **Timeline**: 4-5 sessions

---

## Next Steps

1. **Decide on path**: Realistic scenarios (B) or SWE-bench (A)?
2. **Update configuration**: Change target_context_size to 156_250
3. **Implement chosen path**: Scenarios OR SWE-bench integration
4. **Run pilot**: 2 tasks to verify compaction triggers
5. **Full experiment**: 20 tasks with both strategies
6. **Analyze**: Focus on degradation across compaction cycles

---

## Key Changes from Sprint 5

| Aspect | Sprint 5 (Invalid) | Sprint 5 Redux (Valid) |
|--------|-------------------|----------------------|
| **Context Threshold** | 32K tokens | 125K tokens |
| **Task Type** | Single-file puzzles | Multi-file codebase work |
| **Avg Tokens/Task** | 2K-6K | 120K-150K |
| **Compaction Events** | 0 per task | 2-4 per task |
| **What's Tested** | Nothing (no compaction) | Degradation across cycles |
| **Turns per Task** | 3-8 | 30-50 |
| **Files Read** | 0 | 10-30 |
| **Cost** | $2-5 | $20-150 |
| **Research Validity** | ❌ Invalid | ✅ Valid |

---

**Status**: Ready to implement
**Recommendation**: Start with Path B (realistic scenarios) for quick validation, then optionally proceed to Path A (SWE-bench) for publication
**First Task**: Update AgentConfig.target_context_size = 156_250
