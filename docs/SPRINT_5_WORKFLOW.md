# Sprint 5: Real-World Validation - Implementation Workflow

**Sprint Goal**: Validate continuous pruning on 20 real SWE-bench problems with natural completion, full cost accounting, and multi-strategy comparison.

**Timeline**: 2 weeks (14 days)
**Prerequisites**: Sprint 4 complete with statistical analysis
**Success Criteria**: Demonstrate continuous pruning superiority on real-world problems

---

## Executive Summary

### What We're Building

A production-grade validation experiment comparing three context management strategies:
1. **Continuous Pruning** (our approach)
2. **Discrete Baseline** (traditional compaction)
3. **Prompt Caching** (Anthropic's approach)

### Key Innovations

- **Natural Completion**: Agent-driven task finishing (no fixed turns)
- **Real Problems**: 20 SWE-bench GitHub issues with actual codebases
- **Complete Cost Accounting**: Tokens + computational overhead + quality metrics
- **Real Test Validation**: Objective correctness measurement (no mocked tests)

### Expected Outcomes

- Continuous pruning wins on total cost (tokens) and efficiency (quality/token)
- Prompt caching wins on raw speed (cache hits)
- Discrete baseline uses most tokens but achieves similar quality
- Statistical validation (p < 0.05) with real-world evidence

---

## Architecture Overview

```
experiments/
└── experiment_5/           # Sprint 5: Real-world validation
    ├── __init__.py
    ├── run_experiment_5.py        # Main experiment orchestrator
    ├── natural_agent.py           # Agent with natural completion
    ├── caching_agent.py           # Prompt caching strategy
    ├── cost_tracker.py            # Complete cost accounting
    ├── test_runner.py             # Real test execution
    ├── loader.py                  # SWE-bench data loader
    └── analyze_results.py         # Statistical analysis

data/
└── swe_bench/              # Real problem dataset
    ├── problems/           # 20 selected problems
    ├── codebases/          # Cloned repositories
    └── metadata.json       # Problem metadata

results/
└── experiment_5/           # Sprint 5 results
    ├── exp5_*.json         # Detailed results
    ├── exp5_*_summary.csv  # Summary statistics
    ├── exp5_*_analysis.md  # Statistical report
    └── visualizations/     # Charts and plots
```

---

## Week 1: Infrastructure (Days 1-7)

### Day 1-2: T5.1 - SWE-bench Dataset Preparation

**Objective**: Load and prepare 20 real GitHub issues for validation

**Deliverables**:
- `experiments/experiment_5/loader.py` (300 lines)
- `data/swe_bench/problems/` (20 problem files)
- `data/swe_bench/metadata.json` (problem catalog)

**Implementation Steps**:

#### Step 1.1: Install Dependencies (1 hour)
```bash
# Add to requirements
uv pip install datasets gitpython subprocess32
```

#### Step 1.2: Create SWE-bench Loader (4 hours)
```python
# experiments/experiment_5/loader.py
from datasets import load_dataset
from dataclasses import dataclass
import git
from pathlib import Path
from typing import List, Dict

@dataclass
class SWEBenchProblem:
    """Real GitHub issue from SWE-bench"""
    instance_id: str           # e.g., "django__django-12345"
    repo: str                  # e.g., "django/django"
    base_commit: str           # SHA to checkout
    problem_statement: str     # Bug description
    hints_text: str            # Relevant files mentioned
    test_patch: str            # Tests to validate fix
    patch: str                 # Actual solution (for validation)
    difficulty: str            # easy, medium, hard

    # Derived fields
    codebase_path: Path        # Local clone path
    relevant_files: List[str]  # Files to include in context
    estimated_tokens: int      # Context size estimate

class SWEBenchLoader:
    """Load and prepare SWE-bench problems"""

    def __init__(self, cache_dir: str = "data/swe_bench"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.dataset = load_dataset("princeton-nlp/SWE-bench")

    def select_balanced_problems(self, n: int = 20) -> List[SWEBenchProblem]:
        """
        Select balanced problem set:
        - 5 easy (baseline)
        - 10 medium (primary validation)
        - 5 hard (stress test)

        From diverse repos:
        - 5 Django (large framework)
        - 5 Requests (mid-size library)
        - 5 Pandas (data science)
        - 5 Scikit-learn (ML)
        """
        problems = []

        # Distribution strategy
        selection = [
            ('easy', 'django/django', 2),
            ('easy', 'psf/requests', 1),
            ('easy', 'pandas-dev/pandas', 1),
            ('easy', 'scikit-learn/scikit-learn', 1),

            ('medium', 'django/django', 2),
            ('medium', 'psf/requests', 3),
            ('medium', 'pandas-dev/pandas', 3),
            ('medium', 'scikit-learn/scikit-learn', 2),

            ('hard', 'django/django', 1),
            ('hard', 'psf/requests', 1),
            ('hard', 'pandas-dev/pandas', 2),
            ('hard', 'scikit-learn/scikit-learn', 1),
        ]

        for difficulty, repo, count in selection:
            subset = self._filter_problems(difficulty=difficulty, repo=repo)
            problems.extend(subset[:count])

        return problems

    def _filter_problems(self, difficulty: str, repo: str) -> List[SWEBenchProblem]:
        """Filter dataset by criteria"""
        filtered = self.dataset['test'].filter(
            lambda x: x['repo'] == repo and self._estimate_difficulty(x) == difficulty
        )
        return [self._convert_to_problem(x) for x in filtered]

    def _estimate_difficulty(self, instance: Dict) -> str:
        """Estimate difficulty based on context size and complexity"""
        # Heuristic: look at patch size, files changed, etc.
        patch_lines = len(instance['patch'].split('\n'))
        files_changed = instance['patch'].count('diff --git')

        if patch_lines < 50 and files_changed <= 2:
            return 'easy'
        elif patch_lines < 200 and files_changed <= 5:
            return 'medium'
        else:
            return 'hard'

    def prepare_problem(self, problem: SWEBenchProblem) -> SWEBenchProblem:
        """
        Clone repository, checkout commit, extract relevant files
        """
        # Clone repo if not cached
        repo_path = self.cache_dir / 'codebases' / problem.instance_id
        if not repo_path.exists():
            print(f"Cloning {problem.repo}...")
            git.Repo.clone_from(
                f"https://github.com/{problem.repo}.git",
                repo_path
            )

        # Checkout base commit
        repo = git.Repo(repo_path)
        repo.git.checkout(problem.base_commit)

        # Extract relevant files from hints
        problem.relevant_files = self._extract_relevant_files(
            problem.hints_text,
            repo_path
        )

        # Estimate context tokens
        problem.estimated_tokens = self._estimate_context_tokens(
            problem.relevant_files,
            repo_path
        )

        problem.codebase_path = repo_path
        return problem

    def _extract_relevant_files(self, hints: str, repo_path: Path) -> List[str]:
        """Parse hints for file paths"""
        # Look for file paths in hints text
        # Example: "Look at django/db/models/query.py"
        import re
        file_pattern = r'[\w/]+\.py'
        files = re.findall(file_pattern, hints)

        # Verify files exist
        verified = []
        for file in files:
            if (repo_path / file).exists():
                verified.append(file)

        return verified if verified else ['README.md']  # Fallback

    def _estimate_context_tokens(self, files: List[str], repo_path: Path) -> int:
        """Estimate total context size"""
        total_chars = 0
        for file in files:
            try:
                content = (repo_path / file).read_text()
                total_chars += len(content)
            except:
                pass

        # Rough estimate: 4 chars per token
        return total_chars // 4
```

#### Step 1.3: Generate Problem Set (3 hours)
```python
# scripts/prepare_swe_bench.py
from experiments.experiment_5.loader import SWEBenchLoader

loader = SWEBenchLoader()
problems = loader.select_balanced_problems(n=20)

# Prepare each problem (clone repos, etc.)
for i, problem in enumerate(problems):
    print(f"[{i+1}/20] Preparing {problem.instance_id}...")
    prepared = loader.prepare_problem(problem)

    # Save metadata
    problem_meta = {
        'instance_id': prepared.instance_id,
        'repo': prepared.repo,
        'difficulty': prepared.difficulty,
        'estimated_tokens': prepared.estimated_tokens,
        'relevant_files': prepared.relevant_files
    }

    # Write to data/swe_bench/problems/{instance_id}.json
    with open(f"data/swe_bench/problems/{prepared.instance_id}.json", 'w') as f:
        json.dump(problem_meta, f, indent=2)

print("✅ 20 problems prepared!")
```

**Validation**:
- [ ] 20 problems selected across difficulty levels
- [ ] Repos cloned and commits checked out
- [ ] Relevant files identified
- [ ] Context size estimates within 10K-200K tokens
- [ ] Metadata saved to JSON

---

### Day 3-4: T5.2 - Natural Completion Logic

**Objective**: Enable agent-driven task finishing (no fixed turns)

**Deliverables**:
- `experiments/experiment_5/natural_agent.py` (400 lines)
- System prompt for natural completion
- Status extraction logic

**Implementation Steps**:

#### Step 2.1: Design Status Protocol (2 hours)
```python
# Status indicators agent can use
from enum import Enum

class AgentStatus(Enum):
    WORKING = "working"              # Still analyzing/coding
    SOLUTION_READY = "solution_ready" # Complete solution available
    NEED_INFO = "need_more_info"      # Request additional context
    STUCK = "stuck"                   # Can't proceed without help

@dataclass
class AgentResponse:
    status: AgentStatus
    content: str                     # Full response text
    confidence: float                # 0.0 - 1.0
    solution: Optional[str] = None   # Code if status == SOLUTION_READY
    info_request: Optional[str] = None  # Details if status == NEED_INFO
```

#### Step 2.2: Implement Natural Completion Agent (6 hours)
```python
# experiments/experiment_5/natural_agent.py
from experiments.experiment_4.agent import RealCodingAgent
import re
import json

class NaturalCompletionAgent(RealCodingAgent):
    """Agent that declares completion naturally"""

    def __init__(self, config, strategy: str):
        super().__init__(config, strategy)
        self.system_prompt = self._build_natural_prompt()

    def _build_natural_prompt(self) -> str:
        """System prompt for natural completion"""
        return """You are an expert coding assistant solving real GitHub issues.

COMPLETION PROTOCOL:
When you have a complete, tested solution ready:
1. Write exactly: "SOLUTION READY"
2. Provide your complete code changes
3. Explain what you fixed/implemented
4. Include any new test cases

CONTEXT REQUESTS:
If you need additional files or information:
1. Write exactly: "I NEED: <file path or description>"
2. Explain why you need it
3. I will provide the requested context

CONFIDENCE:
At the end of each response, rate your confidence:
"CONFIDENCE: <0.0-1.0>"

IMPORTANT:
- Take as many turns as needed (no rush)
- Don't declare SOLUTION READY until you're confident
- It's okay to request context multiple times
- Test your solution mentally before declaring ready
"""

    def generate_response_with_status(self) -> AgentResponse:
        """Generate response and extract status"""
        # Get response from Claude
        raw_response = self.generate_response()

        # Extract status indicators
        status = self._extract_status(raw_response)
        confidence = self._extract_confidence(raw_response)
        solution = self._extract_solution(raw_response) if status == AgentStatus.SOLUTION_READY else None
        info_request = self._extract_info_request(raw_response) if status == AgentStatus.NEED_INFO else None

        return AgentResponse(
            status=status,
            content=raw_response,
            confidence=confidence,
            solution=solution,
            info_request=info_request
        )

    def _extract_status(self, response: str) -> AgentStatus:
        """Parse status from response"""
        response_upper = response.upper()

        # Check for explicit status declarations
        if "SOLUTION READY" in response_upper:
            return AgentStatus.SOLUTION_READY
        elif "I NEED:" in response_upper or "PLEASE PROVIDE" in response_upper:
            return AgentStatus.NEED_INFO
        elif "I'M STUCK" in response_upper or "CANNOT PROCEED" in response_upper:
            return AgentStatus.STUCK
        else:
            return AgentStatus.WORKING

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence rating"""
        # Look for "CONFIDENCE: 0.85" pattern
        match = re.search(r'CONFIDENCE:\s*(0?\.\d+|1\.0)', response, re.IGNORECASE)
        if match:
            return float(match.group(1))

        # Default confidence based on status keywords
        if "definitely" in response.lower() or "certainly" in response.lower():
            return 0.9
        elif "probably" in response.lower() or "likely" in response.lower():
            return 0.7
        elif "maybe" in response.lower() or "possibly" in response.lower():
            return 0.5
        else:
            return 0.6  # Default moderate confidence

    def _extract_solution(self, response: str) -> Optional[str]:
        """Extract code solution from response"""
        # Look for code blocks after "SOLUTION READY"
        if "SOLUTION READY" not in response.upper():
            return None

        # Extract all code blocks
        code_blocks = re.findall(r'```(?:python)?\n(.*?)```', response, re.DOTALL)

        if code_blocks:
            # Return concatenated code blocks
            return '\n\n'.join(code_blocks)

        return None

    def _extract_info_request(self, response: str) -> Optional[str]:
        """Extract information request"""
        # Look for "I NEED: <request>" pattern
        match = re.search(r'I NEED:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Alternative patterns
        match = re.search(r'PLEASE PROVIDE:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None
```

#### Step 2.3: Implement Conversation Loop (4 hours)
```python
# experiments/experiment_5/conversation_manager.py
class NaturalConversationManager:
    """Manage open-ended conversations"""

    def __init__(self, agent: NaturalCompletionAgent, problem: SWEBenchProblem, max_turns: int = 50):
        self.agent = agent
        self.problem = problem
        self.max_turns = max_turns
        self.turns = 0
        self.completed = False

    def run_until_complete(self) -> Dict:
        """Run conversation until agent declares completion or timeout"""
        # Initialize with problem statement
        self.agent.receive_message(self._format_initial_prompt())

        while not self.completed and self.turns < self.max_turns:
            self.turns += 1

            # Get agent response with status
            response = self.agent.generate_response_with_status()

            # Handle based on status
            if response.status == AgentStatus.SOLUTION_READY:
                # Validate solution with real tests
                if self._validate_solution(response.solution):
                    self.completed = True
                    return self._build_result(response, success=True)
                else:
                    # Solution failed - give feedback
                    feedback = self._get_test_feedback()
                    self.agent.receive_message(f"Tests failed:\n{feedback}\n\nPlease fix and try again.")

            elif response.status == AgentStatus.NEED_INFO:
                # Fetch requested context
                context = self._fetch_requested_context(response.info_request)
                self.agent.receive_message(context)

            elif response.status == AgentStatus.STUCK:
                # Provide hint or guidance
                hint = self._generate_hint()
                self.agent.receive_message(hint)

            # else: WORKING - continue

        # Timeout reached
        return self._build_result(None, success=False, reason="timeout")

    def _format_initial_prompt(self) -> str:
        """Format problem as initial message"""
        return f"""Please solve this GitHub issue:

ISSUE: {self.problem.instance_id}
REPOSITORY: {self.problem.repo}

PROBLEM STATEMENT:
{self.problem.problem_statement}

HINTS:
{self.problem.hints_text}

CODEBASE CONTEXT:
{self._load_relevant_files()}

Take your time and work through this systematically. When you have a complete solution, declare "SOLUTION READY".
"""

    def _load_relevant_files(self) -> str:
        """Load relevant files from codebase"""
        content = []
        for file_path in self.problem.relevant_files:
            full_path = self.problem.codebase_path / file_path
            try:
                file_content = full_path.read_text()
                content.append(f"=== {file_path} ===\n{file_content}\n")
            except:
                pass
        return '\n'.join(content)
```

**Validation**:
- [ ] Agent can declare SOLUTION READY
- [ ] Agent can request additional context
- [ ] Confidence extraction working
- [ ] Code solution extraction working
- [ ] Conversation loop handles all statuses
- [ ] Max turn limit prevents infinite loops

---

### Day 5: T5.3 - Prompt Caching Strategy

**Objective**: Implement Anthropic's prompt caching for comparison

**Deliverables**:
- `experiments/experiment_5/caching_agent.py` (300 lines)
- Cache configuration management
- Cache hit/miss tracking

**Implementation Steps**:

#### Step 3.1: Implement Caching Agent (4 hours)
```python
# experiments/experiment_5/caching_agent.py
class PromptCachingAgent(NaturalCompletionAgent):
    """Agent using Anthropic's prompt caching"""

    def __init__(self, config):
        super().__init__(config, strategy="prompt_caching")
        self.cache_config = {'type': 'ephemeral'}
        self.cache_stats = {
            'writes': 0,
            'reads': 0,
            'write_tokens': 0,
            'read_tokens': 0
        }

    def _build_context_messages(self):
        """Build messages with cache control"""
        messages = []

        # Cache codebase context (static, large, reused)
        if hasattr(self, 'codebase_context'):
            messages.append({
                'role': 'user',
                'content': self.codebase_context,
                'cache_control': self.cache_config  # ← Anthropic caching
            })
            self.cache_stats['writes'] += 1
            self.cache_stats['write_tokens'] += len(self.codebase_context) // 4

        # Don't cache conversation (changes every turn)
        for item in self.context_manager.context:
            messages.append({
                'role': item.role,
                'content': item.content
                # No cache_control - changes frequently
            })

        return messages

    def generate_response(self):
        """Generate with cache tracking"""
        response = super().generate_response()

        # Track cache usage from response
        if hasattr(response, 'usage') and hasattr(response.usage, 'cache_read_input_tokens'):
            self.cache_stats['reads'] += 1
            self.cache_stats['read_tokens'] += response.usage.cache_read_input_tokens

        return response
```

#### Step 3.2: Cache Configuration (2 hours)
```python
# Cache timing and invalidation
class CacheManager:
    """Manage cache lifecycle"""

    def __init__(self, ttl_minutes: int = 5):
        self.ttl = ttl_minutes * 60  # Convert to seconds
        self.cache_start = None

    def should_refresh_cache(self) -> bool:
        """Check if cache expired (5-min TTL)"""
        if self.cache_start is None:
            return True

        elapsed = time.time() - self.cache_start
        return elapsed > self.ttl

    def mark_cache_write(self):
        """Record cache write"""
        self.cache_start = time.time()
```

**Validation**:
- [ ] Caching agent initializes correctly
- [ ] Cache control applied to static content
- [ ] Cache stats tracked accurately
- [ ] TTL enforced (5 minutes)
- [ ] Fallback to non-cached if expired

---

### Day 6-7: T5.4 - Complete Cost Accounting

**Objective**: Track all costs for fair comparison

**Deliverables**:
- `experiments/experiment_5/cost_tracker.py` (400 lines)
- `experiments/experiment_5/test_runner.py` (500 lines)
- Complete cost model implementation

**Implementation Steps**:

#### Step 4.1: Cost Tracking Data Structure (3 hours)
```python
# experiments/experiment_5/cost_tracker.py
from dataclasses import dataclass, field
from typing import Dict, List
import time

@dataclass
class CompleteCost:
    """Complete cost accounting for fair comparison"""

    # API Token Costs
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0

    # Computational Overhead
    pruning_time_ms: float = 0.0
    pruning_operations: int = 0
    context_fetch_count: int = 0

    # Solution Metrics
    turns_to_solution: int = 0
    wall_clock_seconds: float = 0.0
    tests_passed: int = 0
    tests_total: int = 0
    first_attempt_success: bool = False

    # Quality Metrics
    code_quality_score: float = 0.0
    solution_length_lines: int = 0

    # Timeline
    timestamps: List[float] = field(default_factory=list)

    @property
    def api_cost_usd(self) -> float:
        """Calculate total API cost"""
        # Pricing (as of Sprint 5)
        input_cost = self.input_tokens * 3.00 / 1_000_000
        output_cost = self.output_tokens * 15.00 / 1_000_000
        cache_write_cost = self.cache_write_tokens * 3.75 / 1_000_000
        cache_read_cost = self.cache_read_tokens * 0.30 / 1_000_000

        return input_cost + output_cost + cache_write_cost + cache_read_cost

    @property
    def total_tokens(self) -> int:
        """Total tokens (for comparison with Sprint 4)"""
        return self.input_tokens + self.output_tokens

    @property
    def correctness_rate(self) -> float:
        """Test pass rate"""
        if self.tests_total == 0:
            return 0.0
        return self.tests_passed / self.tests_total

    @property
    def efficiency_score(self) -> float:
        """Quality per dollar (higher is better)"""
        if self.api_cost_usd == 0:
            return 0.0
        return self.correctness_rate / self.api_cost_usd

    @property
    def quality_per_token(self) -> float:
        """Quality per 1K tokens (higher is better)"""
        if self.total_tokens == 0:
            return 0.0
        return (self.correctness_rate * 1000) / self.total_tokens

    @property
    def overhead_ratio(self) -> float:
        """Pruning overhead as % of total time"""
        if self.wall_clock_seconds == 0:
            return 0.0
        total_time_ms = self.wall_clock_seconds * 1000
        return (self.pruning_time_ms / total_time_ms) * 100

    def to_dict(self) -> Dict:
        """Export for JSON serialization"""
        return {
            # Tokens
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'cache_write_tokens': self.cache_write_tokens,
            'cache_read_tokens': self.cache_read_tokens,
            'total_tokens': self.total_tokens,

            # Costs
            'api_cost_usd': self.api_cost_usd,

            # Overhead
            'pruning_time_ms': self.pruning_time_ms,
            'pruning_operations': self.pruning_operations,
            'overhead_ratio_pct': self.overhead_ratio,

            # Performance
            'turns_to_solution': self.turns_to_solution,
            'wall_clock_seconds': self.wall_clock_seconds,

            # Quality
            'tests_passed': self.tests_passed,
            'tests_total': self.tests_total,
            'correctness_rate': self.correctness_rate,
            'first_attempt_success': self.first_attempt_success,
            'code_quality_score': self.code_quality_score,

            # Efficiency
            'efficiency_score': self.efficiency_score,
            'quality_per_token': self.quality_per_token,
        }

class CostTracker:
    """Track costs during experiment execution"""

    def __init__(self):
        self.cost = CompleteCost()
        self.start_time = None

    def start(self):
        """Begin tracking"""
        self.start_time = time.time()
        self.cost.timestamps.append(self.start_time)

    def record_api_call(self, response):
        """Record API token usage"""
        self.cost.input_tokens += response.usage.input_tokens
        self.cost.output_tokens += response.usage.output_tokens

        # Cache tokens (if present)
        if hasattr(response.usage, 'cache_write_input_tokens'):
            self.cost.cache_write_tokens += response.usage.cache_write_input_tokens
        if hasattr(response.usage, 'cache_read_input_tokens'):
            self.cost.cache_read_tokens += response.usage.cache_read_input_tokens

        self.cost.timestamps.append(time.time())

    def record_pruning(self, duration_ms: float):
        """Record pruning operation"""
        self.cost.pruning_time_ms += duration_ms
        self.cost.pruning_operations += 1

    def record_solution(self, tests_passed: int, tests_total: int, is_first_attempt: bool):
        """Record solution validation"""
        self.cost.tests_passed = tests_passed
        self.cost.tests_total = tests_total
        self.cost.first_attempt_success = is_first_attempt

    def finish(self, turns: int):
        """Complete tracking"""
        self.cost.wall_clock_seconds = time.time() - self.start_time
        self.cost.turns_to_solution = turns
```

#### Step 4.2: Real Test Runner (8 hours)
```python
# experiments/experiment_5/test_runner.py
import subprocess
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TestResult:
    """Real test execution result"""
    all_passed: bool
    num_tests: int
    num_passed: int
    num_failed: int
    execution_time_seconds: float
    stdout: str
    stderr: str
    execution_method: str = "pytest"

class RealTestRunner:
    """Execute actual tests - no mocking"""

    def __init__(self, timeout_seconds: int = 30):
        self.timeout = timeout_seconds

    def run_tests(self, solution_code: str, problem: SWEBenchProblem) -> TestResult:
        """
        Execute real tests against solution

        Steps:
        1. Create isolated test environment
        2. Apply solution to codebase
        3. Run test suite with pytest
        4. Parse results
        5. Clean up
        """
        start_time = time.time()

        # Create temporary test environment
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy codebase to temp
            test_env = self._create_test_environment(problem, temp_path)

            # Apply solution
            self._apply_solution(solution_code, problem, test_env)

            # Run tests
            result = self._execute_tests(problem, test_env)

            # Add execution time
            result.execution_time_seconds = time.time() - start_time

            return result

    def _create_test_environment(self, problem: SWEBenchProblem, temp_path: Path) -> Path:
        """Clone repo to temp directory"""
        test_env = temp_path / problem.instance_id
        shutil.copytree(problem.codebase_path, test_env)
        return test_env

    def _apply_solution(self, solution_code: str, problem: SWEBenchProblem, test_env: Path):
        """Apply solution code to test environment"""
        # Parse solution to identify which files to modify
        # This is simplified - real implementation would be more sophisticated

        # For now, assume solution is a patch format
        patch_file = test_env / 'solution.patch'
        patch_file.write_text(solution_code)

        # Apply patch
        try:
            subprocess.run(
                ['git', 'apply', 'solution.patch'],
                cwd=test_env,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            # Patch failed - try alternative application method
            self._apply_solution_alternative(solution_code, problem, test_env)

    def _apply_solution_alternative(self, solution_code: str, problem: SWEBenchProblem, test_env: Path):
        """Alternative: directly write solution files"""
        # Extract file paths and contents from solution
        # This would parse the solution format
        pass

    def _execute_tests(self, problem: SWEBenchProblem, test_env: Path) -> TestResult:
        """Run pytest on test suite"""
        try:
            # Run pytest with test patch
            result = subprocess.run(
                [
                    'pytest',
                    '-v',                 # Verbose
                    '--tb=short',         # Short traceback
                    '--no-header',        # No header
                    '--color=no',         # No color codes
                ],
                cwd=test_env,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Parse pytest output
            return self._parse_pytest_output(result)

        except subprocess.TimeoutExpired:
            return TestResult(
                all_passed=False,
                num_tests=0,
                num_passed=0,
                num_failed=0,
                execution_time_seconds=self.timeout,
                stdout="",
                stderr="TIMEOUT: Tests exceeded 30 seconds",
                execution_method="pytest"
            )
        except Exception as e:
            return TestResult(
                all_passed=False,
                num_tests=0,
                num_passed=0,
                num_failed=0,
                execution_time_seconds=0,
                stdout="",
                stderr=f"ERROR: {str(e)}",
                execution_method="pytest"
            )

    def _parse_pytest_output(self, result: subprocess.CompletedProcess) -> TestResult:
        """Parse pytest results"""
        stdout = result.stdout
        stderr = result.stderr

        # Parse summary line: "5 passed, 2 failed in 1.23s"
        import re
        summary_match = re.search(
            r'(\d+) passed(?:, (\d+) failed)?',
            stdout
        )

        if summary_match:
            num_passed = int(summary_match.group(1))
            num_failed = int(summary_match.group(2)) if summary_match.group(2) else 0
            num_tests = num_passed + num_failed
            all_passed = (num_failed == 0) and (num_passed > 0)
        else:
            # Could not parse - assume failure
            num_tests = 0
            num_passed = 0
            num_failed = 0
            all_passed = False

        return TestResult(
            all_passed=all_passed,
            num_tests=num_tests,
            num_passed=num_passed,
            num_failed=num_failed,
            execution_time_seconds=0,  # Will be set by caller
            stdout=stdout,
            stderr=stderr,
            execution_method="pytest"
        )
```

**Validation**:
- [ ] Cost tracker captures all metrics
- [ ] Test runner executes real pytest
- [ ] Solution application works
- [ ] Test results parsed correctly
- [ ] Timeout handling prevents hangs
- [ ] Isolated environments prevent cross-contamination

---

## Week 2: Execution & Analysis (Days 8-14)

### Day 8-10: T5.5 - Run 20-Problem Experiment

**Objective**: Execute experiment on all 20 problems with 3 strategies

**Deliverables**:
- `experiments/experiment_5/run_experiment_5.py` (600 lines)
- Experiment orchestration logic
- Results persistence

**Implementation Steps**:

#### Step 5.1: Main Experiment Script (6 hours)
```python
# experiments/experiment_5/run_experiment_5.py
class Experiment5Runner:
    """Sprint 5: Real-world validation"""

    def __init__(self, num_problems: int = 20):
        self.num_problems = num_problems
        self.strategies = [
            'continuous_pruning',
            'discrete_baseline',
            'prompt_caching'
        ]
        self.loader = SWEBenchLoader()
        self.test_runner = RealTestRunner()

    def run(self):
        """Execute full experiment"""
        print("=" * 70)
        print("EXPERIMENT 5: REAL-WORLD VALIDATION")
        print("=" * 70)

        # Phase 1: Load problems
        print("\n--- Phase 1: Loading Problems ---")
        problems = self.loader.select_balanced_problems(self.num_problems)
        print(f"✅ Loaded {len(problems)} problems")

        # Phase 2: Run experiments
        print("\n--- Phase 2: Running Experiments ---")
        results = self._run_all_experiments(problems)

        # Phase 3: Save results
        print("\n--- Phase 3: Saving Results ---")
        self._save_results(results)

        # Phase 4: Summary
        print("\n--- Phase 4: Summary ---")
        self._print_summary(results)

        print("\n✅ Experiment 5 complete!")

    def _run_all_experiments(self, problems: List[SWEBenchProblem]) -> Dict:
        """Run all strategy × problem combinations"""
        results = {}
        total_runs = len(problems) * len(self.strategies)
        current = 0

        for problem in problems:
            for strategy in self.strategies:
                current += 1
                print(f"\n[{current}/{total_runs}] Running {problem.instance_id} with {strategy}...")

                result = self._run_single_problem(problem, strategy)
                results[(problem.instance_id, strategy)] = result

                # Print immediate result
                status = "✅ SOLVED" if result['solved'] else "❌ FAILED"
                print(f"  {status} in {result['turns']} turns ({result['cost_usd']:.3f} USD)")

        return results

    def _run_single_problem(self, problem: SWEBenchProblem, strategy: str) -> Dict:
        """Run single problem with specific strategy"""
        # Create agent
        agent = self._create_agent(strategy)

        # Create cost tracker
        cost_tracker = CostTracker()
        cost_tracker.start()

        # Create conversation manager
        conversation = NaturalConversationManager(
            agent=agent,
            problem=problem,
            max_turns=50
        )

        # Run until complete or timeout
        result = conversation.run_until_complete()

        # Finish cost tracking
        cost_tracker.finish(turns=conversation.turns)

        # Combine results
        return {
            'problem_id': problem.instance_id,
            'strategy': strategy,
            'solved': result['success'],
            'turns': conversation.turns,
            'cost': cost_tracker.cost.to_dict(),
            'cost_usd': cost_tracker.cost.api_cost_usd,
            'solution': result.get('solution'),
            'test_results': result.get('test_results'),
            'conversation_history': result.get('conversation_history'),
        }

    def _create_agent(self, strategy: str):
        """Factory for creating agents"""
        config = AgentConfig(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.0
        )

        if strategy == "continuous_pruning":
            return NaturalCompletionAgent(config, strategy="continuous_pruning")
        elif strategy == "discrete_baseline":
            return NaturalCompletionAgent(config, strategy="discrete_baseline")
        elif strategy == "prompt_caching":
            return PromptCachingAgent(config)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--num-problems", type=int, default=20)
    args = parser.parse_args()

    runner = Experiment5Runner(num_problems=args.num_problems)
    runner.run()
```

#### Step 5.2: Execute Experiment (12 hours computing time)
```bash
# Full 20-problem experiment
source .venv/bin/activate
python experiments/experiment_5/run_experiment_5.py --num-problems 20

# Expected runtime: ~10-12 hours
# - 20 problems × 3 strategies = 60 runs
# - Average ~10-12 minutes per run
```

**Validation**:
- [ ] All 60 runs complete successfully
- [ ] No crashes or hangs
- [ ] Results saved incrementally
- [ ] API errors handled gracefully
- [ ] Cost tracking accurate

---

### Day 11-12: T5.6 - Statistical Analysis

**Objective**: Analyze results and generate statistical report

**Deliverables**:
- `experiments/experiment_5/analyze_results.py` (700 lines)
- Statistical analysis report
- Visualizations

**Implementation** (Similar to Sprint 4, but enhanced):
```python
# Enhanced statistical tests
# - Paired comparisons (same 20 problems)
# - Multiple hypothesis correction (Bonferroni)
# - Effect size calculations
# - Cost-quality tradeoff analysis
# - Efficiency frontier plotting
```

---

### Day 13: T5.7 - Write Phase 5 Report

**Objective**: Document findings and conclusions

**Deliverables**:
- `results/experiment_5/PHASE_5_REPORT.md`
- Executive summary
- Detailed findings

---

### Day 14: T5.8 - Update Documentation

**Objective**: Update project documentation with Phase 5 results

**Deliverables**:
- Updated `README.md`
- Updated `docs/SPRINT_5_STATUS.md`
- Phase 5 summary in main docs

---

## Success Criteria

### Sprint 5 Success Metrics

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Infrastructure** | 100% complete | All 8 tasks done |
| **Execution** | ≥18/20 problems complete | 90%+ completion rate |
| **Token Efficiency** | Continuous < Baseline | Paired t-test p < 0.05 |
| **Cost Efficiency** | Continuous best $/quality | Efficiency score highest |
| **Solution Quality** | No degradation | Same pass rate as baseline |
| **Statistical Significance** | p < 0.05 | All 3 metrics validated |

### Quality Gates

**Before Execution**:
- [ ] All 20 problems prepared
- [ ] All 3 agents tested
- [ ] Test runner validated
- [ ] Cost tracking verified

**During Execution**:
- [ ] Monitor for crashes
- [ ] Verify results saved
- [ ] Check API rate limits
- [ ] Track cost budget

**After Execution**:
- [ ] All data persisted
- [ ] No corrupted results
- [ ] Statistical tests pass
- [ ] Report complete

---

## Risk Management

### High Risks

**Risk**: SWE-bench problems too complex (low solve rate)
**Mitigation**: Select problems with verified solutions; allow 50 turns
**Contingency**: If <50% solve rate, analyze partial solutions

**Risk**: API costs exceed budget ($50 estimated)
**Mitigation**: Run 5-problem pilot first; monitor costs
**Contingency**: Reduce sample size to 10 problems if needed

### Medium Risks

**Risk**: Test execution unreliable (environment issues)
**Mitigation**: Isolated temp directories; timeout handling
**Contingency**: Manual test validation for critical cases

**Risk**: Cache TTL causes inconsistent results
**Mitigation**: Track cache hits/misses; document in results
**Contingency**: Re-run with cache prewarming if needed

---

## Budget

### Time Budget
- Week 1: 40 hours (infrastructure)
- Week 2: 40 hours (execution + analysis)
- **Total**: 80 hours (2 full weeks)

### API Cost Budget
- 20 problems × 3 strategies × 30 turns avg × 2000 tokens = ~3.6M tokens
- Input: 1.8M × $3/M = $5.40
- Output: 1.8M × $15/M = $27.00
- **Estimated Total**: ~$35-50 (depending on actual turns)

### Compute Budget
- 60 runs × 12 min avg = 720 minutes = 12 hours wall time
- Test execution: ~1 hour total
- Analysis: ~30 min
- **Total**: ~13-14 hours execution time

---

## Dependencies

### External
- SWE-bench dataset (HuggingFace)
- Git repositories (GitHub)
- Anthropic Claude API
- pytest framework

### Internal
- Sprint 4 infrastructure (agent, cost tracking)
- Context management (pruner, baseline)
- Metrics calculation (from T4.1)
- Statistical analysis (scipy)

---

## Deliverables Summary

### Code (2000+ lines)
- `experiments/experiment_5/loader.py` (300 lines)
- `experiments/experiment_5/natural_agent.py` (400 lines)
- `experiments/experiment_5/caching_agent.py` (300 lines)
- `experiments/experiment_5/cost_tracker.py` (400 lines)
- `experiments/experiment_5/test_runner.py` (500 lines)
- `experiments/experiment_5/run_experiment_5.py` (600 lines)
- `experiments/experiment_5/analyze_results.py` (700 lines)

### Documentation (10,000+ words)
- This workflow document
- Phase 5 report
- Statistical analysis report
- Updated README and status docs

### Data
- 20 prepared problems
- 60 experiment results
- Statistical analysis
- Visualizations (6-8 charts)

---

## Next Steps After Sprint 5

### Sprint 6: Publication & Productionization
1. Write research paper
2. Submit to MLOps conference
3. Open-source release
4. Production deployment guide

### Future Enhancements
1. AI-assisted pruning (Phase 6)
2. Multi-agent collaboration
3. Adaptive threshold tuning
4. Real-time compaction

---

**Last Updated**: 2025-11-03
**Status**: Ready for implementation after Sprint 4 completes
**Owner**: Context Pruning Lab Team
