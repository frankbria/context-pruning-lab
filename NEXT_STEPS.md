# Next Steps: Real SWE-bench Validation

**Status**: Configuration fixed ✅ (156K threshold)
**Current**: Need minimal SWE-bench integration
**Goal**: 2-3 real tasks to verify compaction triggers

---

## What We Fixed

```python
# experiments/experiment_4/agent.py (line 46)
target_context_size: int = 156_250  # Was 40_000
```

**Result**: Compaction now triggers at 125K tokens (80% of 156K)

---

## Next: SWE-bench Integration

### Option 1: Use Existing Infrastructure (experiments/experiment_5/)

There's already a `loader.py` stub:

```bash
# Check what exists
ls experiments/experiment_5/

# Files present:
- loader.py          # SWE-bench loader (stubbed)
- __init__.py
```

**Pros**: Foundation exists
**Cons**: Needs real implementation

### Option 2: Minimal Direct Integration

Create simple integration that:
1. Loads SWE-bench from HuggingFace
2. Clones repo at specific commit
3. Agent reads files via tool
4. Runs pytest to validate

**Estimated**: 4-6 hours

---

## Minimal Implementation Plan

### Step 1: Install SWE-bench Dataset (30 min)
```bash
uv pip install datasets gitpython pytest

# Test loading
python -c "
from datasets import load_dataset
ds = load_dataset('princeton-nlp/SWE-bench_Lite')
print(f'Problems available: {len(ds[\"test\"])}')
problem = ds['test'][0]
print(f'First problem: {problem[\"instance_id\"]}')
"
```

### Step 2: Create File Reading Tool (2 hours)
```python
# experiments/experiment_5/swe_tools.py

class CodebaseTools:
    """Tools for agent to interact with real codebases"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def read_file(self, path: str) -> str:
        """Read a file from the repository"""
        full_path = self.repo_path / path
        if not full_path.exists():
            return f"Error: File not found: {path}"
        try:
            return full_path.read_text()
        except Exception as e:
            return f"Error reading file: {e}"

    def list_files(self, directory: str = ".") -> List[str]:
        """List files in a directory"""
        dir_path = self.repo_path / directory
        if not dir_path.exists():
            return []
        return [str(p.relative_to(self.repo_path))
                for p in dir_path.rglob("*.py")]

    def search_code(self, pattern: str) -> Dict[str, List[int]]:
        """Search for pattern in codebase, return file:line_numbers"""
        matches = {}
        for py_file in self.repo_path.rglob("*.py"):
            content = py_file.read_text()
            line_nums = [i+1 for i, line in enumerate(content.split('\n'))
                        if pattern in line]
            if line_nums:
                matches[str(py_file.relative_to(self.repo_path))] = line_nums
        return matches
```

### Step 3: Agent Integration (2 hours)
Extend RealCodingAgent to use CodebaseTools when available:

```python
# experiments/experiment_5/swe_agent.py

class SWEBenchAgent(RealCodingAgent):
    def __init__(self, config: AgentConfig, codebase_tools: CodebaseTools):
        super().__init__(config)
        self.tools = codebase_tools

    def generate_response_with_tools(self) -> str:
        """Enhanced response that can use codebase tools"""
        # Agent can request: read_file, list_files, search_code
        # Results get added to context
        # Standard context management applies
        pass
```

### Step 4: Test Runner (1 hour)
```python
# experiments/experiment_5/test_runner.py

def run_swe_bench_tests(problem: SWEBenchProblem,
                        agent_changes: Dict[str, str]) -> TestResults:
    """
    Apply agent's changes and run tests

    Args:
        problem: SWE-bench problem with test patch
        agent_changes: {file_path: new_content}

    Returns:
        TestResults with pass/fail counts
    """
    # 1. Apply agent's changes to files
    # 2. Apply test patch from SWE-bench
    # 3. Run pytest
    # 4. Parse results
    pass
```

---

## Validation Experiment

### Select 3 Test Problems

```python
# Pick 3 diverse, medium-difficulty problems
test_problems = [
    "django__django-12345",     # Django: Template rendering bug
    "requests__requests-6789",  # Requests: HTTP header handling
    "pandas-dev__pandas-1011",  # Pandas: DataFrame merge issue
]
```

### Expected Results Per Task
- Agent reads: 10-20 files (~30-50K tokens)
- Conversation: 30-50 turns
- Context growth: 120K-150K tokens
- **Baseline compactions: 2-3 events** ← This is what Sprint 5 missed!
- Continuous pruning ops: 30-50

### Verification Checklist
- [ ] Compaction triggers (check logs)
- [ ] Context size reaches 125K+ before compaction
- [ ] System records metrics correctly
- [ ] Can measure quality before/after compaction
- [ ] Agent successfully reads files from repo
- [ ] Tests run and provide results

---

## Timeline

**Session 1 (Today - 4 hours)**:
- Install SWE-bench dataset ✓
- Implement CodebaseTools
- Test file reading with 1 problem

**Session 2 (Tomorrow - 3 hours)**:
- Integrate tools with agent
- Run 1 complete task
- Verify compaction triggers

**Session 3 (Day 3 - 2 hours)**:
- Run 2 more tasks
- Confirm system works correctly
- Fix any issues

**Session 4+ (Day 4-5)**:
- Scale to 20-30 tasks
- Collect real data
- Analyze results

---

## Success = Real Data

If we get 20-30 real SWE-bench tasks completed with:
- Compaction triggering 2-3x per task (baseline)
- Measurable quality metrics
- Can compare degradation between strategies

Then we have **real, publishable results** about whether continuous pruning prevents degradation.

No more testing nothing. Test the actual hypothesis.
