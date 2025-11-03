"""
Experiment 4: Code Quality Benchmark - Main Script

Executes the primary validation experiment comparing continuous pruning
vs discrete baseline on 50 SWE-bench Extended coding tasks.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import infrastructure
from experiments.swe_bench_extended.task_loader import SWEBenchExtendedLoader
from experiments.swe_bench_extended.harness import ExperimentHarness
from experiments.swe_bench_extended.types import TaskDifficulty

# Import agent
from experiments.experiment_4.agent import create_agent

# Import metrics
from experiments.metrics import MetricsCalculator


class Experiment4Runner:
    """
    Main runner for Experiment 4.

    Coordinates:
    - Task loading
    - Agent execution with both strategies
    - Metrics collection
    - Result serialization
    """

    def __init__(
        self,
        num_tasks: int = 50,
        strategies: List[str] = None,
        results_dir: str = "results/experiment_4",
        verbose: bool = True
    ):
        """
        Initialize experiment runner.

        Args:
            num_tasks: Number of tasks to run (default: 50)
            strategies: List of strategies to test (default: both)
            results_dir: Directory for saving results
            verbose: Enable verbose logging
        """
        self.num_tasks = num_tasks
        self.strategies = strategies or ["continuous_pruning", "discrete_baseline"]
        self.results_dir = Path(results_dir)
        self.verbose = verbose

        # Create results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.task_loader = SWEBenchExtendedLoader(
            data_dir="data",
            auto_generate_scripts=True
        )

        self.harness = ExperimentHarness(
            results_dir=str(self.results_dir),
            timeout_seconds=600,  # 10 min per task
            max_retries=1,
            verbose=verbose
        )

        self.metrics_calculator = MetricsCalculator()

        if self.verbose:
            print("=" * 70)
            print("EXPERIMENT 4: CODE QUALITY BENCHMARK")
            print("=" * 70)
            print(f"\nConfiguration:")
            print(f"  Tasks: {self.num_tasks}")
            print(f"  Strategies: {', '.join(self.strategies)}")
            print(f"  Results: {self.results_dir}")

    def run(self) -> Dict[str, Any]:
        """
        Run the complete experiment.

        Returns:
            Dictionary with experiment results
        """
        if self.verbose:
            print(f"\n{'-' * 70}")
            print("PHASE 1: Loading Tasks")
            print("-" * 70)

        # Load tasks
        task_ids = self.task_loader.get_task_ids()[:self.num_tasks]
        tasks_and_scripts = []

        for task_id in task_ids:
            task, script = self.task_loader.load_task_with_script(task_id)
            tasks_and_scripts.append((task, script))

        if self.verbose:
            print(f"✅ Loaded {len(tasks_and_scripts)} tasks with scripts")

        # Run experiments
        if self.verbose:
            print(f"\n{'-' * 70}")
            print("PHASE 2: Executing Experiments")
            print("-" * 70)

        results = self.harness.run_batch(
            tasks_and_scripts=tasks_and_scripts,
            agent_factory=lambda strategy: create_agent(strategy=strategy),
            strategies=self.strategies
        )

        # Calculate metrics for all results
        if self.verbose:
            print(f"\n{'-' * 70}")
            print("PHASE 3: Calculating Metrics")
            print("-" * 70)

        enhanced_results = self._calculate_metrics(results)

        # Save results
        if self.verbose:
            print(f"\n{'-' * 70}")
            print("PHASE 4: Saving Results")
            print("-" * 70)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_name = f"exp4_{timestamp}"

        self.harness.save_results(enhanced_results, experiment_name, format='json')
        self.harness.save_results(enhanced_results, experiment_name, format='csv')

        # Print summary
        if self.verbose:
            self._print_summary(enhanced_results)

        return enhanced_results

    def _calculate_metrics(self, results: Dict[str, List]) -> Dict[str, List]:
        """
        Calculate code quality metrics for all results.

        Args:
            results: Raw results from harness

        Returns:
            Enhanced results with metrics
        """
        enhanced = {}

        for strategy, task_results in results.items():
            enhanced[strategy] = []

            for result in task_results:
                # Calculate metrics
                generated_code = result.generated_code

                task_data = {
                    'test_results': result.test_results,
                    'requirements': {},  # TODO: Extract from task
                    'context_stats': result.context_stats
                }

                metric_results = self.metrics_calculator.calculate_all(
                    generated_code,
                    task_data
                )

                # Add metrics to result
                result.metrics.update({
                    'code_quality_scores': self.metrics_calculator.get_summary(metric_results),
                    'aggregate_score': self.metrics_calculator.get_aggregate_score(metric_results)
                })

                enhanced[strategy].append(result)

            if self.verbose:
                print(f"✅ Calculated metrics for {len(task_results)} tasks ({strategy})")

        return enhanced

    def _print_summary(self, results: Dict[str, List]):
        """Print experiment summary."""
        print(f"\n{'=' * 70}")
        print("EXPERIMENT 4 SUMMARY")
        print("=" * 70)

        for strategy, task_results in results.items():
            print(f"\n--- Strategy: {strategy} ---")

            # Basic stats
            num_tasks = len(task_results)
            num_success = sum(1 for r in task_results if r.success)

            print(f"  Tasks completed: {num_success}/{num_tasks} ({num_success/num_tasks*100:.1f}%)")

            # Average metrics
            if num_tasks > 0:
                avg_aggregate = sum(
                    r.metrics.get('aggregate_score', 0)
                    for r in task_results
                ) / num_tasks

                avg_tokens = sum(
                    r.context_stats.get('total_tokens', 0)
                    for r in task_results
                ) / num_tasks

                avg_time = sum(r.execution_time for r in task_results) / num_tasks

                print(f"  Avg aggregate score: {avg_aggregate:.3f}")
                print(f"  Avg tokens: {avg_tokens:.0f}")
                print(f"  Avg time: {avg_time:.1f}s")

        print(f"\n{'=' * 70}")
        print("✅ Experiment 4 Complete!")
        print("=" * 70)


def main():
    """Run Experiment 4."""
    import argparse

    parser = argparse.ArgumentParser(description='Run Experiment 4: Code Quality Benchmark')
    parser.add_argument(
        '--num-tasks',
        type=int,
        default=5,  # Start small for testing
        help='Number of tasks to run (default: 5 for quick test)'
    )
    parser.add_argument(
        '--strategies',
        nargs='+',
        default=['continuous_pruning', 'discrete_baseline'],
        help='Strategies to test (default: both)'
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default='results/experiment_4',
        help='Results directory (default: results/experiment_4)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Disable verbose output'
    )

    args = parser.parse_args()

    # Check for API key
    import os
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n⚠️  ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("\nTo run Experiment 4, you need a Claude API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        print("\nGet your API key from: https://console.anthropic.com/")
        sys.exit(1)

    # Run experiment
    runner = Experiment4Runner(
        num_tasks=args.num_tasks,
        strategies=args.strategies,
        results_dir=args.results_dir,
        verbose=not args.quiet
    )

    try:
        results = runner.run()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
