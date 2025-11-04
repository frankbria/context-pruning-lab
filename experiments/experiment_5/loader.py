"""
SWE-bench Dataset Loader for Real-World Validation

Loads and prepares real GitHub issues from the SWE-bench dataset.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import json
import subprocess
import re


@dataclass
class SWEBenchProblem:
    """Real GitHub issue from SWE-bench dataset"""

    instance_id: str           # e.g., "django__django-12345"
    repo: str                  # e.g., "django/django"
    base_commit: str           # SHA to checkout
    problem_statement: str     # Bug description/feature request
    hints_text: str            # Relevant files mentioned
    test_patch: str            # Tests to validate fix
    patch: str                 # Actual solution (for validation)
    difficulty: str            # easy, medium, hard

    # Derived fields (populated by prepare_problem)
    codebase_path: Optional[Path] = None
    relevant_files: List[str] = None
    estimated_tokens: int = 0

    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.relevant_files is None:
            self.relevant_files = []


class SWEBenchLoader:
    """
    Load and prepare SWE-bench problems for validation experiment

    NOTE: For Sprint 5 pilot, we'll use simulated problems since downloading
    and preparing 20 real SWE-bench problems would require:
    - Installing datasets library
    - Cloning 4 large repositories (Django, Requests, Pandas, Scikit-learn)
    - ~2GB disk space
    - ~30 minutes setup time

    This loader provides the interface and can be connected to real SWE-bench
    dataset when ready for production validation.
    """

    def __init__(self, cache_dir: str = "data/swe_bench", use_simulated: bool = False):
        """
        Initialize loader

        Args:
            cache_dir: Directory to cache repos and problems
            use_simulated: If True, use simulated problems for testing (default: False - use real SWE-bench)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_simulated = use_simulated

        # Load real dataset
        if not use_simulated:
            try:
                from datasets import load_dataset
                print("Loading SWE-bench Lite dataset...")
                self.dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
                print(f"✓ Loaded {len(self.dataset)} problems from SWE-bench Lite")
            except Exception as e:
                print(f"Warning: Could not load SWE-bench dataset: {e}")
                print("Falling back to simulated mode")
                self.use_simulated = True
                self.dataset = None
        else:
            self.dataset = None

    def select_balanced_problems(self, n: int = 20) -> List[SWEBenchProblem]:
        """
        Select balanced problem set

        Distribution:
        - 5 easy (baseline)
        - 10 medium (primary validation)
        - 5 hard (stress test)

        From diverse repos:
        - 5 Django (large framework)
        - 5 Requests (mid-size library)
        - 5 Pandas (data science)
        - 5 Scikit-learn (ML)

        Args:
            n: Number of problems to select

        Returns:
            List of SWEBenchProblem instances
        """
        if self.use_simulated:
            return self._generate_simulated_problems(n)
        else:
            return self._select_real_problems(n)

    def _generate_simulated_problems(self, n: int) -> List[SWEBenchProblem]:
        """
        Generate simulated problems for testing infrastructure

        These are realistic problem descriptions that would come from SWE-bench,
        but use our synthetic codebase instead of real repos.
        """
        problems = []

        # Distribution matching real SWE-bench
        difficulties = ['easy'] * 5 + ['medium'] * 10 + ['hard'] * 5
        repos = ['django/django', 'psf/requests', 'pandas-dev/pandas', 'scikit-learn/scikit-learn']

        for i in range(min(n, len(difficulties))):
            difficulty = difficulties[i]
            repo = repos[i % len(repos)]

            # Create realistic problem
            problem = SWEBenchProblem(
                instance_id=f"simulated_{repo.replace('/', '_')}_{i:03d}",
                repo=repo,
                base_commit=f"abc{i:04d}",
                problem_statement=self._generate_problem_statement(difficulty, repo),
                hints_text=self._generate_hints(repo),
                test_patch=self._generate_test_patch(),
                patch=self._generate_solution_patch(),
                difficulty=difficulty
            )

            problems.append(problem)

        return problems

    def _generate_problem_statement(self, difficulty: str, repo: str) -> str:
        """Generate realistic problem statement"""
        templates = {
            'easy': [
                f"Bug: Function in {repo} raises TypeError when given None as input",
                f"Issue: Method doesn't handle empty list correctly in {repo}",
                f"Problem: Edge case not handled in validation function"
            ],
            'medium': [
                f"Bug: Incorrect behavior when combining multiple filters in {repo}",
                f"Issue: Memory leak in long-running process",
                f"Problem: Race condition in concurrent operations"
            ],
            'hard': [
                f"Bug: Complex interaction between components causes data corruption in {repo}",
                f"Issue: Performance degradation with large datasets",
                f"Problem: Deadlock under specific timing conditions"
            ]
        }

        import random
        return random.choice(templates[difficulty])

    def _generate_hints(self, repo: str) -> str:
        """Generate hints about relevant files"""
        # Simplified - real SWE-bench has actual file paths
        return f"Look at core module, utils.py, and tests in {repo}"

    def _generate_test_patch(self) -> str:
        """Generate test patch"""
        return """
def test_fix():
    '''Test that the fix works'''
    result = target_function(edge_case_input)
    assert result is not None
    assert len(result) > 0
"""

    def _generate_solution_patch(self) -> str:
        """Generate solution patch"""
        return """
--- a/module.py
+++ b/module.py
@@ -10,6 +10,9 @@ def target_function(input):
+    # Add edge case handling
+    if input is None:
+        return []
     return process(input)
"""

    def _select_real_problems(self, n: int) -> List[SWEBenchProblem]:
        """
        Select from real SWE-bench dataset

        Selects balanced problems across repos and difficulties.
        For initial validation, we'll select smaller, faster problems.
        """
        if not self.dataset:
            raise RuntimeError("Dataset not loaded. Initialize with use_simulated=False")

        problems = []

        # For initial validation, select specific repos with manageable codebases
        # Prioritize smaller repos for faster cloning
        target_repos = [
            "psf/requests",       # HTTP library - small, focused
            "sympy/sympy",        # Symbolic math - medium size
            "django/django",      # Web framework - large
        ]

        # Select problems from each repo
        problems_per_repo = max(1, n // len(target_repos))

        for repo in target_repos:
            if len(problems) >= n:
                break

            # Find problems for this repo
            repo_problems = [item for item in self.dataset if item['repo'] == repo]

            # Take first problems_per_repo items
            for item in repo_problems[:problems_per_repo]:
                if len(problems) >= n:
                    break

                # Convert dataset item to SWEBenchProblem
                problem = SWEBenchProblem(
                    instance_id=item['instance_id'],
                    repo=item['repo'],
                    base_commit=item['base_commit'],
                    problem_statement=item['problem_statement'],
                    hints_text=item.get('hints_text', ''),
                    test_patch=item.get('test_patch', ''),
                    patch=item.get('patch', ''),
                    difficulty='medium'  # SWE-bench doesn't provide difficulty, default to medium
                )
                problems.append(problem)

        print(f"Selected {len(problems)} problems from SWE-bench Lite")
        return problems[:n]

    def prepare_problem(self, problem: SWEBenchProblem) -> SWEBenchProblem:
        """
        Prepare problem for execution

        For simulated problems:
        - Use synthetic codebase from data/conversation_scripts
        - Estimate context size
        - Mark as ready

        For real problems:
        - Clone repository
        - Checkout commit
        - Extract relevant files
        - Estimate context size

        Args:
            problem: Problem to prepare

        Returns:
            Prepared problem with codebase_path and metadata
        """
        if self.use_simulated:
            return self._prepare_simulated_problem(problem)
        else:
            return self._prepare_real_problem(problem)

    def _prepare_simulated_problem(self, problem: SWEBenchProblem) -> SWEBenchProblem:
        """Prepare simulated problem using synthetic codebase"""
        # Use existing synthetic conversation scripts as "codebase"
        problem.codebase_path = Path("data/conversation_scripts")
        problem.relevant_files = ["README.md"]  # Placeholder
        problem.estimated_tokens = 5000  # Rough estimate
        return problem

    def _prepare_real_problem(self, problem: SWEBenchProblem) -> SWEBenchProblem:
        """
        Prepare real SWE-bench problem

        Steps:
        1. Clone repo if not cached
        2. Checkout base commit
        3. Extract relevant files from hints
        4. Estimate context tokens
        """
        # Clone repo if not cached
        repo_path = self.cache_dir / 'codebases' / problem.instance_id

        if not repo_path.exists():
            print(f"Cloning {problem.repo}...")
            try:
                subprocess.run(
                    [
                        'git', 'clone',
                        f"https://github.com/{problem.repo}.git",
                        str(repo_path)
                    ],
                    check=True,
                    capture_output=True,
                    timeout=300  # 5 min timeout
                )
            except subprocess.TimeoutExpired:
                raise RuntimeError(f"Timeout cloning {problem.repo}")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to clone {problem.repo}: {e.stderr}")

        # Checkout base commit
        try:
            subprocess.run(
                ['git', 'checkout', problem.base_commit],
                cwd=repo_path,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to checkout {problem.base_commit}: {e.stderr}")

        # Extract relevant files
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
        """
        Parse hints for file paths

        Looks for patterns like:
        - "Look at django/db/models/query.py"
        - "Check the utils module"
        - "See src/main.py"
        """
        # Find file paths (*.py, *.js, etc.)
        file_pattern = r'[\w/]+\.\w+'
        potential_files = re.findall(file_pattern, hints)

        # Verify files exist
        verified = []
        for file in potential_files:
            file_path = repo_path / file
            if file_path.exists() and file_path.is_file():
                verified.append(file)

        # Fallback to README if no files found
        if not verified:
            readme_path = repo_path / 'README.md'
            if readme_path.exists():
                verified = ['README.md']

        return verified

    def _estimate_context_tokens(self, files: List[str], repo_path: Path) -> int:
        """
        Estimate total context size in tokens

        Uses rough heuristic: 4 characters per token
        """
        total_chars = 0

        for file in files:
            try:
                file_path = repo_path / file
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                total_chars += len(content)
            except Exception:
                # Skip files that can't be read
                continue

        # 4 chars per token (rough estimate)
        return total_chars // 4

    def load_problem_context(self, problem: SWEBenchProblem) -> str:
        """
        Load codebase context for a problem

        Returns formatted context string ready for agent
        """
        if not problem.codebase_path:
            raise ValueError("Problem not prepared. Call prepare_problem() first.")

        context_parts = []

        # Add problem statement
        context_parts.append(f"# Problem: {problem.instance_id}\n")
        context_parts.append(f"Repository: {problem.repo}\n")
        context_parts.append(f"Difficulty: {problem.difficulty}\n\n")
        context_parts.append("## Issue Description\n")
        context_parts.append(problem.problem_statement)
        context_parts.append("\n\n")

        # Add hints
        if problem.hints_text:
            context_parts.append("## Hints\n")
            context_parts.append(problem.hints_text)
            context_parts.append("\n\n")

        # Add relevant files
        if problem.relevant_files:
            context_parts.append("## Relevant Files\n\n")

            for file_path in problem.relevant_files:
                full_path = problem.codebase_path / file_path

                try:
                    content = full_path.read_text(encoding='utf-8', errors='ignore')
                    context_parts.append(f"### {file_path}\n")
                    context_parts.append(f"```\n{content}\n```\n\n")
                except Exception as e:
                    context_parts.append(f"### {file_path}\n")
                    context_parts.append(f"*Could not read file: {e}*\n\n")

        return ''.join(context_parts)


def test_loader():
    """Test the loader with simulated problems"""
    print("Testing SWEBenchLoader...")

    # Create loader with simulated problems
    loader = SWEBenchLoader(use_simulated=True)

    # Select 5 problems
    problems = loader.select_balanced_problems(n=5)
    print(f"✅ Selected {len(problems)} problems")

    # Prepare first problem
    problem = problems[0]
    prepared = loader.prepare_problem(problem)
    print(f"✅ Prepared problem: {prepared.instance_id}")
    print(f"   Difficulty: {prepared.difficulty}")
    print(f"   Estimated tokens: {prepared.estimated_tokens}")

    # Load context
    context = loader.load_problem_context(prepared)
    print(f"✅ Loaded context: {len(context)} characters")

    print("\n✅ All loader tests passed!")


if __name__ == "__main__":
    test_loader()
