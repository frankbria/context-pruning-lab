# Solution Verification Strategy: Handling Overconfident AI

**Your Question**: "How are we sure the 'solution done' is really correct? AI coders think they're done when they're not."

**Answer**: We don't trust the AI's self-assessment. We verify objectively with real tests.

---

## The Problem: Overconfident AI

### **What AI Agents Do**:
```python
# Agent response
"SOLUTION READY! I've fixed the bug. Here's my code: ..."
# Confidence: 0.95

# Reality
Tests passed: 2/10 ❌
Actual confidence: ~0.20
```

**Why This Happens**:
- ✅ AI is trained to be helpful and certain
- ✅ Can't actually run code (hallucinates results)
- ✅ Doesn't know what it doesn't know
- ✅ Pattern matches "solution-like" code

**Examples**:
```python
# AI thinks this works
def divide(a, b):
    return a / b  # "SOLUTION READY!"

# Reality
divide(5, 0)  # ZeroDivisionError! ❌
```

---

## Our Multi-Layer Verification System

### **Layer 1: Agent Claims Completion**

**Agent Output**:
```python
{
    "status": "solution_ready",
    "confidence": 0.95,  # Self-reported (don't trust!)
    "solution": "<code>"
}
```

**Our Response**: "Interesting. Let's verify..."

---

### **Layer 2: Real Test Execution** ✅ PRIMARY VERIFICATION

**Objective Test Harness**:
```python
def verify_solution(solution_code: str, problem: Problem) -> VerificationResult:
    """
    Run REAL tests - no mocking, no trust, just facts.

    Args:
        solution_code: What AI generated
        problem: Problem definition with tests

    Returns:
        VerificationResult with pass/fail data
    """
    # 1. Create isolated environment
    with tempfile.TemporaryDirectory() as tmpdir:
        # 2. Write solution to file
        solution_file = Path(tmpdir) / "solution.py"
        solution_file.write_text(solution_code)

        # 3. Write test file
        test_file = Path(tmpdir) / "test_solution.py"
        test_file.write_text(problem.test_suite)

        # 4. Run tests with timeout
        result = subprocess.run(
            ['pytest', str(test_file), '-v', '--tb=short'],
            capture_output=True,
            timeout=30,  # 30 second timeout
            cwd=tmpdir
        )

        # 5. Parse results
        return VerificationResult(
            all_passed=result.returncode == 0,
            num_passed=parse_passed_count(result.stdout),
            num_failed=parse_failed_count(result.stdout),
            num_total=problem.num_tests,
            stderr=result.stderr.decode(),
            execution_time=parse_execution_time(result.stdout)
        )
```

**Key Point**: We ACTUALLY RUN THE CODE, not just ask the AI if it works.

---

### **Layer 3: Iterative Refinement** (if tests fail)

**When Tests Fail**:
```python
verification = verify_solution(solution, problem)

if not verification.all_passed:
    # AI was wrong! Send it back
    feedback = f"""
    Your solution has issues:

    Tests Passed: {verification.num_passed}/{verification.num_total}

    Failed Tests:
    {verification.stderr}

    Please fix these issues and try again.
    """

    agent.receive_message(feedback)
    # Loop continues - agent tries again
```

**Conversation Flow**:
```
Turn 1: Agent: "SOLUTION READY!"
        Test: 2/10 passed ❌

Turn 2: Us: "Failed 8 tests. Error: ZeroDivisionError. Try again."
        Agent: "Oops! Here's v2..."
        Test: 7/10 passed ❌

Turn 3: Us: "Failed 3 tests. Error: IndexError on empty list. Try again."
        Agent: "Got it! Here's v3..."
        Test: 10/10 passed ✅

ACTUALLY DONE!
```

---

## Detailed Verification Implementation

### **Phase 5 Test Runner**

```python
# experiments/swe_bench_real/test_runner.py

class RealTestRunner:
    """
    Executes actual tests - no mocking, no shortcuts.
    """

    def __init__(self, timeout_seconds: int = 30):
        self.timeout = timeout_seconds

    def run_tests(
        self,
        solution_code: str,
        problem: SWEBenchProblem
    ) -> TestResult:
        """
        Run problem's test suite against solution.

        Returns:
            TestResult with objective pass/fail data
        """
        # Create isolated environment
        env = self._create_test_environment(problem)

        try:
            # Apply solution (patch files)
            self._apply_solution(env, solution_code, problem)

            # Run test suite
            test_output = self._execute_tests(env, problem.test_patch)

            # Parse results
            return self._parse_test_results(test_output)

        except TimeoutError:
            return TestResult(
                status='timeout',
                all_passed=False,
                error='Tests exceeded 30 second timeout'
            )
        except Exception as e:
            return TestResult(
                status='error',
                all_passed=False,
                error=str(e)
            )
        finally:
            # Cleanup
            env.cleanup()

    def _create_test_environment(self, problem: SWEBenchProblem):
        """
        Clone repo at specific commit, install deps.
        """
        tmpdir = tempfile.mkdtemp()

        # Clone repository
        subprocess.run([
            'git', 'clone', problem.repo_url, tmpdir
        ], check=True)

        # Checkout base commit
        subprocess.run([
            'git', 'checkout', problem.base_commit
        ], cwd=tmpdir, check=True)

        # Install dependencies
        if Path(tmpdir, 'requirements.txt').exists():
            subprocess.run([
                'pip', 'install', '-r', 'requirements.txt'
            ], cwd=tmpdir, check=True)

        return TestEnvironment(tmpdir)

    def _apply_solution(self, env, solution_code, problem):
        """
        Apply AI's solution to the codebase.
        """
        # Parse patch from solution_code
        patch = parse_patch(solution_code)

        # Apply to files
        for file_change in patch.changes:
            file_path = env.path / file_change.filename
            file_path.write_text(file_change.new_content)

    def _execute_tests(self, env, test_patch) -> subprocess.CompletedProcess:
        """
        Run the actual test suite.
        """
        # Apply test patch
        test_file = env.path / 'test_solution.py'
        test_file.write_text(test_patch)

        # Run with pytest
        return subprocess.run(
            ['pytest', 'test_solution.py', '-v', '--tb=short', '--no-header'],
            cwd=env.path,
            capture_output=True,
            timeout=self.timeout,
            text=True
        )

    def _parse_test_results(self, output: subprocess.CompletedProcess) -> TestResult:
        """
        Parse pytest output into structured results.
        """
        stdout = output.stdout
        stderr = output.stderr

        # Regex patterns for pytest output
        passed_pattern = r'(\d+) passed'
        failed_pattern = r'(\d+) failed'

        passed_match = re.search(passed_pattern, stdout)
        failed_match = re.search(failed_pattern, stdout)

        num_passed = int(passed_match.group(1)) if passed_match else 0
        num_failed = int(failed_match.group(1)) if failed_match else 0

        return TestResult(
            status='passed' if output.returncode == 0 else 'failed',
            all_passed=output.returncode == 0,
            num_passed=num_passed,
            num_failed=num_failed,
            num_total=num_passed + num_failed,
            stdout=stdout,
            stderr=stderr,
            returncode=output.returncode
        )
```

---

### **Agent-In-The-Loop Workflow**

```python
# experiments/swe_bench_real/solving_loop.py

def solve_problem_with_verification(
    agent: NaturalCompletionAgent,
    problem: SWEBenchProblem,
    test_runner: RealTestRunner,
    max_attempts: int = 5,
    max_turns: int = 50
) -> SolutionResult:
    """
    Solve problem with iterative verification.

    Agent proposes solutions, we verify with real tests,
    provide feedback until correct or max attempts.
    """

    attempt = 0
    turn = 0

    # Initial problem statement
    agent.receive_message(problem.description)

    while attempt < max_attempts and turn < max_turns:
        # Agent works on solution
        response = agent.generate_response_with_status()
        turn += 1

        if response['status'] == 'solution_ready':
            # Agent CLAIMS it's done - don't trust, verify!
            attempt += 1

            print(f"  Attempt {attempt}: Agent claims solution ready")

            # VERIFY with real tests
            verification = test_runner.run_tests(
                solution_code=response['solution'],
                problem=problem
            )

            if verification.all_passed:
                # Actually correct! ✅
                print(f"  ✅ All tests passed! Solution verified.")
                return SolutionResult(
                    success=True,
                    solution=response['solution'],
                    attempts=attempt,
                    turns=turn,
                    verification=verification
                )
            else:
                # Agent was WRONG ❌
                print(f"  ❌ Tests failed: {verification.num_passed}/{verification.num_total} passed")

                # Provide detailed feedback
                feedback = generate_test_feedback(verification)
                agent.receive_message(feedback)

                # Agent will try again...

        elif response['status'] == 'need_info':
            # Agent requests context
            context = fetch_requested_context(response['request'], problem)
            agent.receive_message(context)
            turn += 1

    # Max attempts/turns exceeded
    return SolutionResult(
        success=False,
        solution=None,
        attempts=attempt,
        turns=turn,
        error='Max attempts exceeded without passing tests'
    )


def generate_test_feedback(verification: TestResult) -> str:
    """
    Generate helpful feedback from test failures.
    """
    feedback = f"""
Your solution has issues:

Tests Status: {verification.num_passed}/{verification.num_total} passed

Failed Tests:
{verification.stderr}

Please analyze the failures and provide an updated solution.
"""
    return feedback
```

---

## Confidence Calibration

### **Track Agent Accuracy Over Time**

```python
@dataclass
class ConfidenceCalibration:
    """Track how often agent's confidence matches reality"""

    predictions: List[Tuple[float, bool]] = field(default_factory=list)
    # (claimed_confidence, actual_success)

    def record(self, claimed_confidence: float, tests_passed: bool):
        """Record a prediction"""
        self.predictions.append((claimed_confidence, tests_passed))

    def get_calibration_curve(self) -> Dict[str, float]:
        """
        Compare claimed vs actual success rates.

        Well-calibrated: 0.9 confidence → 90% success
        Overconfident:  0.9 confidence → 60% success ❌
        """
        buckets = {
            '0.0-0.2': [],
            '0.2-0.4': [],
            '0.4-0.6': [],
            '0.6-0.8': [],
            '0.8-1.0': []
        }

        for confidence, success in self.predictions:
            bucket = self._get_bucket(confidence)
            buckets[bucket].append(1.0 if success else 0.0)

        return {
            bucket: sum(successes) / len(successes) if successes else 0.0
            for bucket, successes in buckets.items()
        }
```

**Example Output**:
```
Agent Confidence Calibration:
  0.8-1.0 confidence → 65% actually passed (overconfident!)
  0.6-0.8 confidence → 58% actually passed
  0.4-0.6 confidence → 40% actually passed (well-calibrated)
```

---

## Multi-Stage Verification Checklist

### **Before Accepting Solution**:

```python
def verify_solution_complete(solution: str, problem: Problem) -> VerificationResult:
    """
    Multi-stage verification - all must pass.
    """

    # Stage 1: Syntax Check
    syntax_check = verify_syntax(solution)
    if not syntax_check.valid:
        return VerificationResult(
            passed=False,
            stage='syntax',
            error=syntax_check.error
        )

    # Stage 2: Required Changes Present
    required_check = verify_required_changes(solution, problem.requirements)
    if not required_check.valid:
        return VerificationResult(
            passed=False,
            stage='requirements',
            error=f"Missing required changes: {required_check.missing}"
        )

    # Stage 3: Test Suite Passes
    test_result = run_tests(solution, problem)
    if not test_result.all_passed:
        return VerificationResult(
            passed=False,
            stage='tests',
            error=f"Tests failed: {test_result.num_failed}/{test_result.num_total}"
        )

    # Stage 4: No Regressions (run full test suite)
    regression_result = run_full_test_suite(solution, problem)
    if regression_result.has_regressions:
        return VerificationResult(
            passed=False,
            stage='regression',
            error=f"Introduced regressions: {regression_result.failed_tests}"
        )

    # All stages passed ✅
    return VerificationResult(
        passed=True,
        stage='complete',
        stages_passed=['syntax', 'requirements', 'tests', 'regression']
    )
```

---

## Example: Full Verification Flow

### **Problem**: Fix `divide()` function to handle zero

**Turn 1**:
```
Agent: "SOLUTION READY! Here's my fix:
def divide(a, b):
    if b == 0:
        return 0
    return a / b
"
Confidence: 0.95
```

**Verification**:
```python
# Test 1: divide(10, 2) == 5 ✅
# Test 2: divide(10, 0) == None ❌ (returned 0, expected None)
# Result: 1/2 tests passed
```

**Feedback**:
```
Your solution failed 1/2 tests.

Failed: test_divide_by_zero
  Expected: None
  Got: 0

The problem statement says to return None for division by zero,
not 0. Please fix.
```

---

**Turn 2**:
```
Agent: "SOLUTION READY! Fixed:
def divide(a, b):
    if b == 0:
        return None
    return a / b
"
Confidence: 0.98
```

**Verification**:
```python
# Test 1: divide(10, 2) == 5 ✅
# Test 2: divide(10, 0) == None ✅
# Result: 2/2 tests passed ✅
```

**Outcome**: **ACTUALLY CORRECT** - solution accepted!

---

## Handling Edge Cases

### **Case 1: Tests Pass But Solution Is Wrong**

**Scenario**: Weak test suite, AI exploits it

```python
# Problem: Sort a list
# Test: assert sort([3,1,2]) == [1,2,3]

# AI's "solution"
def sort(lst):
    if lst == [3,1,2]:
        return [1,2,3]
    return lst  # Doesn't actually sort!

# Test passes ✅ but solution is wrong!
```

**Our Defense**: SWE-bench has comprehensive test suites (not toy examples)

---

### **Case 2: Tests Timeout**

```python
# AI's solution has infinite loop
def process(data):
    while True:  # ❌
        pass

# Verification
try:
    result = run_tests(solution, timeout=30)
except TimeoutError:
    return VerificationResult(
        passed=False,
        error='Tests exceeded 30s timeout - possible infinite loop'
    )
```

---

### **Case 3: Tests Crash Python**

```python
# AI's solution causes segfault
import ctypes
ctypes.string_at(0)  # ❌ Segfault!

# Verification runs in subprocess
result = subprocess.run(...)
if result.returncode < 0:  # Negative = signal
    return VerificationResult(
        passed=False,
        error=f'Tests crashed with signal {-result.returncode}'
    )
```

---

## Metrics: AI Accuracy vs Reality

### **Track Over 20 Problems**:

```python
results = {
    'agent_claimed_ready': 0,     # How many times AI said "done"
    'actually_correct': 0,         # How many were actually right
    'false_positives': 0,          # AI said done, but tests failed
    'attempts_until_correct': [],  # How many tries it took
}

# Example outcome:
# Agent claimed ready: 45 times
# Actually correct: 20 times (first try)
# False positives: 25 times (had to retry)
# Average attempts: 2.3
```

**Interpretation**:
- 44% first-attempt accuracy (AI overconfident!)
- But: With feedback, reaches 100% within 2.3 attempts
- Verification system catches 100% of false claims

---

## Summary: Trust But Verify

### **The Answer to Your Question**:

**Q**: "How are we sure the solution is really correct?"

**A**: We don't trust the AI - we run REAL TESTS.

```python
# Don't do this ❌
if agent.claims_done():
    solution = agent.solution
    # Assume it works - BAD!

# Do this ✅
if agent.claims_done():
    solution = agent.solution
    test_result = run_actual_tests(solution)  # Objective verification

    if test_result.all_passed:
        # NOW we trust it
        return solution
    else:
        # AI was wrong - send back for revision
        agent.receive_feedback(test_result.errors)
```

---

### **Key Principles**:

1. **Never trust AI self-assessment** - Agents are overconfident
2. **Always run real tests** - Objective, reproducible verification
3. **Iterate with feedback** - Give AI chance to fix mistakes
4. **Track calibration** - Measure claimed vs actual accuracy
5. **Multi-stage verification** - Syntax → Requirements → Tests → Regressions

---

### **Phase 5 Will Measure**:

- **Claimed accuracy**: How often AI says "done"
- **Actual accuracy**: How often tests pass
- **False positive rate**: AI said done, but wrong
- **Attempts until correct**: Average iterations needed
- **Calibration**: Confidence vs reality correlation

This gives us **complete transparency** on AI reliability!

---

**Last Updated**: 2025-11-03
**Status**: Documented - will implement in Phase 5
