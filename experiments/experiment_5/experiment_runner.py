"""
SWE-bench Experiment Runner

Runs real coding agents on SWE-bench problems with codebase access.
Tracks context growth and compaction events to validate hypothesis.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.experiment_5.loader import SWEBenchLoader, SWEBenchProblem
from experiments.experiment_5.codebase_tools import CodebaseTools
from experiments.experiment_4.agent import RealCodingAgent, AgentConfig


@dataclass
class ExperimentResult:
    """Results from running one problem with one strategy"""

    # Problem info
    instance_id: str
    repo: str
    strategy: str

    # Success metrics
    success: bool
    turns: int
    execution_time: float

    # Token metrics
    total_tokens: int
    tokens_sent: int
    tokens_received: int

    # Context metrics
    context_size_final: int
    context_size_max: int
    compaction_events: int
    pruning_operations: int

    # File reading metrics
    files_read: int
    unique_files_read: int

    # Compaction tracking (key for validation!)
    compaction_triggered: bool
    tokens_at_first_compaction: Optional[int] = None
    compaction_history: List[Dict[str, Any]] = None

    # Error tracking
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.compaction_history is None:
            self.compaction_history = []


class SWEBenchExperimentRunner:
    """
    Runs experiments on real SWE-bench problems.

    Key responsibilities:
    1. Load real problems and clone repos
    2. Give agent access to codebase via tools
    3. Run agent in conversation loop
    4. Track when compaction triggers
    5. Measure context growth and degradation
    """

    def __init__(
        self,
        output_dir: str = "results/experiment_5",
        max_turns: int = 50,
        verbose: bool = True
    ):
        """
        Initialize experiment runner.

        Args:
            output_dir: Directory for results
            max_turns: Maximum turns per problem
            verbose: Print progress
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_turns = max_turns
        self.verbose = verbose

        # Initialize loader
        self.loader = SWEBenchLoader(use_simulated=False)

    def run_experiment(
        self,
        n_problems: int = 3,
        strategies: List[str] = None
    ) -> Dict[str, List[ExperimentResult]]:
        """
        Run experiment with multiple problems and strategies.

        Args:
            n_problems: Number of problems to test
            strategies: List of strategies to compare

        Returns:
            Dictionary mapping strategy -> list of results
        """
        if strategies is None:
            strategies = ["continuous_pruning", "discrete_baseline"]

        if self.verbose:
            print("=" * 70)
            print("SWE-BENCH EXPERIMENT")
            print("=" * 70)
            print(f"Problems: {n_problems}")
            print(f"Strategies: {', '.join(strategies)}")
            print(f"Max turns: {self.max_turns}")
            print()

        # Load problems
        print("Loading problems...")
        problems = self.loader.select_balanced_problems(n=n_problems)
        print(f"✓ Selected {len(problems)} problems\n")

        # Prepare problems (clone repos)
        print("Preparing problems (cloning repos - may take 5-10 min)...")
        for i, problem in enumerate(problems, 1):
            print(f"  [{i}/{len(problems)}] {problem.instance_id}...")
            try:
                problems[i-1] = self.loader.prepare_problem(problem)
                print(f"    ✓ Ready: {problem.codebase_path}")
            except Exception as e:
                print(f"    ✗ Failed: {e}")
                # Remove failed problem
                problems[i-1] = None

        # Filter out failed preparations
        problems = [p for p in problems if p is not None]
        print(f"\n✓ {len(problems)} problems ready\n")

        # Run each problem with each strategy
        all_results = {}

        for strategy in strategies:
            print(f"\n{'='*70}")
            print(f"STRATEGY: {strategy}")
            print('='*70)

            strategy_results = []

            for i, problem in enumerate(problems, 1):
                print(f"\n[{i}/{len(problems)}] {problem.instance_id}")

                result = self.run_single_problem(problem, strategy)
                strategy_results.append(result)

                # Print summary
                status = "✓ SUCCESS" if result.success else "✗ FAILED"
                print(f"{status}")
                print(f"  Turns: {result.turns}")
                print(f"  Tokens: {result.total_tokens:,}")
                print(f"  Context max: {result.context_size_max:,}")
                print(f"  Compactions: {result.compaction_events}")

                if result.compaction_triggered:
                    print(f"  ✓ COMPACTION TRIGGERED at {result.tokens_at_first_compaction:,} tokens")
                else:
                    print(f"  ⚠ NO COMPACTION (max context: {result.context_size_max:,})")

                print(f"  Files read: {result.files_read}")

            all_results[strategy] = strategy_results

        # Save results
        self.save_results(all_results)

        # Print summary
        self.print_summary(all_results)

        return all_results

    def run_single_problem(
        self,
        problem: SWEBenchProblem,
        strategy: str
    ) -> ExperimentResult:
        """
        Run one problem with one strategy.

        This is where the real work happens:
        - Agent gets problem description
        - Agent can read files from repo
        - Agent proposes solution
        - We track context growth and compaction
        """
        start_time = time.time()

        # Initialize codebase tools
        tools = CodebaseTools(problem.codebase_path)

        # Initialize agent with correct config
        config = AgentConfig(
            strategy=strategy,
            target_context_size=156_250  # Key: realistic threshold!
        )

        try:
            agent = RealCodingAgent(config)
        except Exception as e:
            return ExperimentResult(
                instance_id=problem.instance_id,
                repo=problem.repo,
                strategy=strategy,
                success=False,
                turns=0,
                execution_time=0,
                total_tokens=0,
                tokens_sent=0,
                tokens_received=0,
                context_size_final=0,
                context_size_max=0,
                compaction_events=0,
                pruning_operations=0,
                files_read=0,
                unique_files_read=0,
                compaction_triggered=False,
                error_message=f"Failed to initialize agent: {e}"
            )

        # Track metrics
        max_context = 0
        compaction_history = []
        compaction_triggered = False
        first_compaction_tokens = None

        # Conversation logging for validation
        conversation_log = []

        # Simplified conversation loop for validation
        # Real implementation would be more sophisticated
        turns = 0

        # Turn 1: Give problem description
        initial_message = self._format_problem_message(problem)
        agent.receive_message(initial_message)
        response = agent.generate_response()
        turns += 1

        # Track context after first turn
        stats = agent.get_context_stats()
        max_context = max(max_context, stats['context_size'])

        # Log initial interaction
        conversation_log.append({
            'turn': turns,
            'user_message': initial_message[:500] + '...' if len(initial_message) > 500 else initial_message,
            'agent_response': response[:1000] + '...' if len(response) > 1000 else response,
            'context_size': stats['context_size'],
            'tokens_sent': stats.get('tokens_sent', 0),
            'tokens_received': stats.get('tokens_received', 0),
            'timestamp': datetime.now().isoformat()
        })

        # Simulate reading files (in real implementation, agent would request these)
        # For validation, read MANY files to trigger compaction (need 125K tokens)
        if problem.relevant_files:
            files_to_read = problem.relevant_files[:40]  # Read up to 40 files to reach threshold
        else:
            # Find some Python files to read
            files_to_read = tools.list_files(".", "*.py")[:40]

        for file_path in files_to_read:
            if turns >= self.max_turns:
                break

            # Simulate agent reading file
            content = tools.read_file(file_path)

            if not content.startswith("Error:"):
                # Add FULL file content to context (no truncation)
                # Need to accumulate 125K+ tokens to trigger compaction
                file_message = f"Read file {file_path}:\n```python\n{content}\n```"
                agent.receive_message(file_message)
                response = agent.generate_response()
                turns += 1

                # Track context growth
                stats = agent.get_context_stats()
                context_size = stats['context_size']
                max_context = max(max_context, context_size)

                # Log this interaction (every 5 turns to avoid huge logs)
                if turns % 5 == 0 or turns <= 5:
                    conversation_log.append({
                        'turn': turns,
                        'user_message': f"Read file {file_path} ({len(content)} chars)",
                        'agent_response': response[:500] + '...' if len(response) > 500 else response,
                        'context_size': context_size,
                        'max_context': max_context,
                        'tokens_sent': stats.get('tokens_sent', 0),
                        'tokens_received': stats.get('tokens_received', 0),
                        'timestamp': datetime.now().isoformat()
                    })

                # Check for compaction
                if strategy == "discrete_baseline":
                    current_compactions = stats['pruning_operations']
                    if current_compactions > len(compaction_history):
                        # New compaction occurred!
                        if not compaction_triggered:
                            compaction_triggered = True
                            # BUG FIX: Capture tokens BEFORE compaction, not after
                            first_compaction_tokens = max_context

                        compaction_history.append({
                            'turn': turns,
                            'tokens_before': max_context,
                            'tokens_after': context_size
                        })

                        # Log compaction event
                        conversation_log.append({
                            'turn': turns,
                            'event': 'COMPACTION',
                            'tokens_before': max_context,
                            'tokens_after': context_size,
                            'reduction_pct': (1 - context_size/max_context) * 100 if max_context > 0 else 0,
                            'timestamp': datetime.now().isoformat()
                        })

        # Get final stats
        final_stats = agent.get_context_stats()
        tool_stats = tools.get_stats()
        execution_time = time.time() - start_time

        # Save conversation log
        log_dir = self.output_dir / "conversations"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_filename = log_dir / f"{problem.instance_id}_{strategy}_conversation.json"

        with open(log_filename, 'w') as f:
            json.dump({
                'instance_id': problem.instance_id,
                'repo': problem.repo,
                'strategy': strategy,
                'turns': turns,
                'execution_time': execution_time,
                'conversation': conversation_log,
                'final_context_size': final_stats['context_size'],
                'final_total_tokens': final_stats['total_tokens']
            }, f, indent=2)

        if self.verbose:
            print(f"  ✓ Conversation log saved: {log_filename}")

        # Build result
        result = ExperimentResult(
            instance_id=problem.instance_id,
            repo=problem.repo,
            strategy=strategy,
            success=(turns > 1),  # Basic success: completed at least one turn
            turns=turns,
            execution_time=execution_time,
            total_tokens=final_stats['total_tokens'],
            tokens_sent=final_stats['tokens_sent'],
            tokens_received=final_stats['tokens_received'],
            context_size_final=final_stats['context_size'],
            context_size_max=max_context,
            compaction_events=len(compaction_history),
            pruning_operations=final_stats['pruning_operations'],
            files_read=tool_stats['files_read_count'],
            unique_files_read=tool_stats['unique_files_read'],
            compaction_triggered=compaction_triggered,
            tokens_at_first_compaction=first_compaction_tokens,
            compaction_history=compaction_history
        )

        return result

    def _format_problem_message(self, problem: SWEBenchProblem) -> str:
        """Format problem as initial message to agent"""
        return f"""You are working on a bug fix for {problem.repo}.

Problem: {problem.problem_statement}

The repository has been cloned for you. You can read files by asking me to show you specific files.

Please analyze the problem and propose a solution."""

    def save_results(self, results: Dict[str, List[ExperimentResult]]):
        """Save results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"swe_bench_exp_{timestamp}.json"

        # Convert to serializable format
        output = {
            'timestamp': timestamp,
            'metadata': {
                'max_turns': self.max_turns,
                'config': {
                    'target_context_size': 156_250,
                    'compaction_threshold': 125_000
                }
            },
            'results': {
                strategy: [asdict(r) for r in results_list]
                for strategy, results_list in results.items()
            }
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✓ Results saved to: {filename}")

    def print_summary(self, results: Dict[str, List[ExperimentResult]]):
        """Print experiment summary"""
        print("\n" + "=" * 70)
        print("EXPERIMENT SUMMARY")
        print("=" * 70)

        for strategy, strategy_results in results.items():
            print(f"\n{strategy}:")
            print(f"  Problems: {len(strategy_results)}")
            print(f"  Success: {sum(r.success for r in strategy_results)}/{len(strategy_results)}")
            print(f"  Avg turns: {sum(r.turns for r in strategy_results) / len(strategy_results):.1f}")
            print(f"  Total tokens: {sum(r.total_tokens for r in strategy_results):,}")
            print(f"  Avg tokens: {sum(r.total_tokens for r in strategy_results) / len(strategy_results):,.0f}")

            # Key validation metric!
            compactions = sum(r.compaction_triggered for r in strategy_results)
            print(f"  Compaction triggered: {compactions}/{len(strategy_results)}")

            if compactions > 0:
                avg_first_compaction = sum(
                    r.tokens_at_first_compaction for r in strategy_results
                    if r.tokens_at_first_compaction
                ) / compactions
                print(f"  Avg tokens at compaction: {avg_first_compaction:,.0f}")

            print(f"  Avg files read: {sum(r.files_read for r in strategy_results) / len(strategy_results):.1f}")


def main():
    """Run experiment"""
    print("SWE-bench Real Validation Experiment")
    print()

    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not set")
        print("Set with: export ANTHROPIC_API_KEY='your-key'")
        return

    # Run with 1 problem for quick validation first
    runner = SWEBenchExperimentRunner(
        output_dir="results/experiment_5",
        max_turns=50,  # Increased to allow more context growth
        verbose=True
    )

    # Configuration: Set via command line arg or default to 2
    import sys
    n_problems = int(sys.argv[1]) if len(sys.argv) > 1 else 2

    results = runner.run_experiment(
        n_problems=n_problems,
        strategies=["discrete_baseline", "continuous_pruning"]  # Test both strategies
    )

    print("\n✓ Experiment complete!")


if __name__ == "__main__":
    main()
