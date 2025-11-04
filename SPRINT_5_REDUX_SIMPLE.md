# Sprint 5 Redux: Simple Validation Plan

**Goal**: Test if our continuous pruning code works correctly with REAL coding problems

**Validation Strategy**:
1. Fix the configuration (125K threshold)
2. Run 2-3 real SWE-bench tasks to verify system works
3. Scale to 20-30 real tasks for statistics

**No fake scenarios. No synthetic codebases. Just real problems.**

---

## Step 1: Fix Configuration (15 minutes)

```python
# experiments/experiment_4/agent.py
@dataclass
class AgentConfig:
    target_context_size: int = 156_250  # Was 40_000 - NOW REALISTIC
```

This ensures compaction triggers at 125K tokens (80% of 156K).

---

## Step 2: Minimal SWE-bench Integration (4-6 hours)

**What we need**:
1. Load a SWE-bench problem (description + codebase)
2. Agent can read files from the codebase
3. Agent makes code changes
4. Run the tests to check if fix works

**Implementation**:
```python
# experiments/experiment_5/swe_agent.py

class SWEBenchAgent:
    """Agent that works with real SWE-bench problems"""

    def __init__(self, problem: SWEBenchProblem, strategy: str):
        self.problem = problem
        self.repo_path = problem.codebase_path
        self.strategy = strategy

    def read_file(self, path: str) -> str:
        """Read file from cloned repository"""
        full_path = self.repo_path / path
        if not full_path.exists():
            return f"File not found: {path}"
        return full_path.read_text()

    def write_file(self, path: str, content: str):
        """Write changes to file"""
        full_path = self.repo_path / path
        full_path.write_text(content)

    def run_tests(self) -> TestResults:
        """Run pytest on the problem's test file"""
        # Apply test patch, run pytest, return results
        pass
```

---

## Step 3: Validation Run (2-3 tasks)

**Select 3 real SWE-bench problems**:
- 1 from `django/django` (web framework)
- 1 from `requests/requests` (HTTP library)
- 1 from `pandas` (data science)

**Expected per task**:
- Agent reads 10-20 files from real codebase (~30-50K tokens)
- Conversation: 30-50 turns
- Context grows to 120-150K tokens
- **Baseline: 2-3 compaction events**
- **Continuous pruning: 30-50 pruning operations**

**Success criteria**:
- ✅ Compaction triggers (not 0 like Sprint 5!)
- ✅ System doesn't crash
- ✅ Metrics recorded correctly
- ✅ Can measure if quality degrades across compactions

---

## Step 4: Scale to Statistics (20-30 tasks)

Once validation confirms the system works:
- Select 20-30 balanced SWE-bench problems
- Run full experiment (12-24 hours)
- Analyze degradation across compaction cycles

**This produces real, publishable results.**

---

## Minimal SWE-bench Setup

```bash
# Install dependencies
uv pip install datasets gitpython

# Load dataset
python -c "
from datasets import load_dataset
ds = load_dataset('princeton-nlp/SWE-bench_Lite')
print(f'Loaded {len(ds[\"test\"])} problems')
"

# Clone a repo for testing
git clone https://github.com/django/django.git data/repos/django
cd data/repos/django
git checkout <commit_sha>  # From SWE-bench problem
```

---

## Timeline

- **Today**: Fix config, basic SWE-bench integration
- **Tomorrow**: Run 2-3 validation tasks
- **Day 3**: Verify results, fix any issues
- **Day 4-5**: Scale to 20-30 tasks, analyze

**Total**: ~4-5 sessions

---

## Key Point

We're testing **if our pruning code works correctly** on real problems, not creating artificial scenarios to game the metrics.

If continuous pruning prevents degradation → real contribution.
If it doesn't → we learned something real.
