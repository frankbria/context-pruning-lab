"""
SWE-bench Extended Experiment Harness

Executes coding tasks with different context management strategies,
collects metrics, and saves results.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import sys

# Handle both module and standalone execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from experiments.swe_bench_extended.types import (
        SWEBenchTask, ConversationScript, ConversationTurn, TaskResult
    )
else:
    from .types import (
        SWEBenchTask, ConversationScript, ConversationTurn, TaskResult
    )


class ExperimentHarness:
    """
    Test harness for running SWE-bench Extended tasks with context strategies.

    Features:
    - Execute tasks with different context management strategies
    - Collect metrics during execution
    - Handle errors gracefully (failed tasks don't block experiments)
    - Progress tracking and logging
    - Result serialization to JSON/CSV
    """

    def __init__(
        self,
        results_dir: str = "results",
        timeout_seconds: int = 600,
        max_retries: int = 1,
        verbose: bool = True
    ):
        """
        Initialize experiment harness.

        Args:
            results_dir: Directory to save results
            timeout_seconds: Timeout for single task execution
            max_retries: Number of retries on failure
            verbose: Enable progress logging
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.verbose = verbose

        # Statistics tracking
        self.stats = {
            'tasks_attempted': 0,
            'tasks_succeeded': 0,
            'tasks_failed': 0,
            'total_execution_time': 0.0
        }

    def run_task(
        self,
        task: SWEBenchTask,
        script: ConversationScript,
        agent,  # Type: CodingAgent (will be defined in mock_agent.py)
        strategy: str
    ) -> TaskResult:
        """
        Execute a single task with the given agent and strategy.

        Args:
            task: SWE-bench task to execute
            script: Conversation script for the task
            agent: Coding agent to execute the task
            strategy: Context management strategy name

        Returns:
            TaskResult with execution details and metrics
        """
        if self.verbose:
            print(f"Running task {task.task_id} with {strategy}...")

        start_time = time.time()
        conversation_history = []
        error_message = ""
        success = False
        generated_code = ""

        try:
            # Reset agent for new task
            agent.reset()

            # Execute conversation script turn by turn
            for turn in script.turns:
                if turn.role == 'user':
                    # Send user message to agent
                    agent.receive_message(turn.content)
                    conversation_history.append(turn)

                    if self.verbose:
                        print(f"  Turn {turn.turn_number} ({turn.turn_type}): user message sent")

                else:  # assistant turn
                    # Generate agent response
                    response = agent.generate_response()

                    # Record assistant turn with generated response
                    assistant_turn = ConversationTurn(
                        turn_number=turn.turn_number,
                        role='assistant',
                        content=response,
                        turn_type=turn.turn_type,
                        metadata=turn.metadata
                    )
                    conversation_history.append(assistant_turn)

                    if self.verbose:
                        print(f"  Turn {turn.turn_number} ({turn.turn_type}): agent responded ({len(response)} chars)")

            # Get final generated code (agent should accumulate during conversation)
            generated_code = agent.get_generated_code()

            # Run tests (mocked for now - will be implemented in Sprint 4)
            test_results = self._run_tests(task, generated_code)
            success = test_results.get('all_passed', False)

            if self.verbose:
                print(f"  Task {'✅ PASSED' if success else '❌ FAILED'}")

        except Exception as e:
            error_message = str(e)
            success = False
            if self.verbose:
                print(f"  Task ❌ ERROR: {error_message}")

        execution_time = time.time() - start_time

        # Get context stats from agent
        context_stats = agent.get_context_stats()

        # Collect metrics
        metrics = {
            'execution_time': execution_time,
            'num_turns': len(conversation_history),
            'total_tokens': context_stats.get('total_tokens', 0),
            'context_size': context_stats.get('context_size', 0),
            'pruning_operations': context_stats.get('pruning_operations', 0),
            'tokens_pruned': context_stats.get('tokens_pruned', 0)
        }

        # Update statistics
        self.stats['tasks_attempted'] += 1
        if success:
            self.stats['tasks_succeeded'] += 1
        else:
            self.stats['tasks_failed'] += 1
        self.stats['total_execution_time'] += execution_time

        # Create result
        result = TaskResult(
            task_id=task.task_id,
            strategy=strategy,
            success=success,
            generated_code=generated_code,
            test_results=test_results if 'test_results' in locals() else {},
            metrics=metrics,
            conversation_history=conversation_history,
            context_stats=context_stats,
            execution_time=execution_time,
            error_message=error_message
        )

        return result

    def run_batch(
        self,
        tasks_and_scripts: List[tuple[SWEBenchTask, ConversationScript]],
        agent_factory,  # Callable that creates new agent instances
        strategies: List[str]
    ) -> Dict[str, List[TaskResult]]:
        """
        Execute multiple tasks with multiple strategies.

        Args:
            tasks_and_scripts: List of (task, script) tuples
            agent_factory: Factory function to create agent instances
            strategies: List of strategy names to test

        Returns:
            Dictionary mapping strategy name to list of results
        """
        results = {strategy: [] for strategy in strategies}

        total_runs = len(tasks_and_scripts) * len(strategies)
        completed_runs = 0

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Starting batch execution:")
            print(f"  Tasks: {len(tasks_and_scripts)}")
            print(f"  Strategies: {len(strategies)}")
            print(f"  Total runs: {total_runs}")
            print(f"{'='*60}\n")

        for strategy in strategies:
            if self.verbose:
                print(f"\n--- Strategy: {strategy} ---")

            for task, script in tasks_and_scripts:
                # Create fresh agent instance for each run
                agent = agent_factory(strategy=strategy)

                # Run task with retry logic
                result = None
                for attempt in range(self.max_retries + 1):
                    try:
                        result = self.run_task(task, script, agent, strategy)
                        break  # Success, no retry needed
                    except Exception as e:
                        if attempt < self.max_retries:
                            if self.verbose:
                                print(f"  Retry {attempt + 1}/{self.max_retries} after error: {e}")
                        else:
                            # Final attempt failed, create error result
                            result = TaskResult(
                                task_id=task.task_id,
                                strategy=strategy,
                                success=False,
                                error_message=f"Failed after {self.max_retries} retries: {str(e)}"
                            )

                results[strategy].append(result)
                completed_runs += 1

                if self.verbose:
                    progress = (completed_runs / total_runs) * 100
                    print(f"  Progress: {completed_runs}/{total_runs} ({progress:.1f}%)")

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Batch execution complete!")
            print(f"{'='*60}\n")

        return results

    def _run_tests(self, task: SWEBenchTask, generated_code: str) -> Dict[str, Any]:
        """
        Run test suite for the task (mocked for now).

        In Sprint 4, this will execute actual tests in a sandbox environment.
        For now, returns simulated test results.

        Args:
            task: Task being tested
            generated_code: Code generated by agent

        Returns:
            Dictionary with test results
        """
        # TODO: Implement real test execution in Sprint 4
        # For now, return simulated results
        return {
            'all_passed': False,  # Will be determined by actual tests
            'num_tests': len(task.test_suite),
            'passed': 0,
            'failed': len(task.test_suite),
            'execution_method': 'mocked'
        }

    def save_results(
        self,
        results: Dict[str, List[TaskResult]],
        experiment_name: str,
        format: str = 'json'
    ):
        """
        Save experiment results to disk.

        Args:
            results: Results dictionary from run_batch
            experiment_name: Name for this experiment run
            format: Output format ('json' or 'csv')
        """
        if format == 'json':
            self._save_json(results, experiment_name)
        elif format == 'csv':
            self._save_csv(results, experiment_name)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_json(self, results: Dict[str, List[TaskResult]], experiment_name: str):
        """Save results as JSON."""
        output_file = self.results_dir / f"{experiment_name}_results.json"

        # Convert results to serializable format
        serializable_results = {}
        for strategy, task_results in results.items():
            serializable_results[strategy] = [
                asdict(result) for result in task_results
            ]

        with open(output_file, 'w') as f:
            json.dump({
                'experiment_name': experiment_name,
                'statistics': self.stats,
                'results': serializable_results
            }, f, indent=2)

        if self.verbose:
            print(f"\n✅ Results saved to {output_file}")

    def _save_csv(self, results: Dict[str, List[TaskResult]], experiment_name: str):
        """Save results as CSV (summary format)."""
        import csv

        output_file = self.results_dir / f"{experiment_name}_summary.csv"

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'task_id', 'strategy', 'success', 'execution_time',
                'num_turns', 'total_tokens', 'pruning_operations',
                'tokens_pruned', 'error_message'
            ])

            # Data rows
            for strategy, task_results in results.items():
                for result in task_results:
                    writer.writerow([
                        result.task_id,
                        result.strategy,
                        result.success,
                        result.execution_time,
                        result.metrics.get('num_turns', 0),
                        result.metrics.get('total_tokens', 0),
                        result.metrics.get('pruning_operations', 0),
                        result.metrics.get('tokens_pruned', 0),
                        result.error_message
                    ])

        if self.verbose:
            print(f"✅ Summary saved to {output_file}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current execution statistics.

        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()

    def print_summary(self, results: Dict[str, List[TaskResult]]):
        """
        Print a summary of experiment results.

        Args:
            results: Results dictionary from run_batch
        """
        print(f"\n{'='*60}")
        print("EXPERIMENT SUMMARY")
        print(f"{'='*60}")

        for strategy, task_results in results.items():
            print(f"\n--- Strategy: {strategy} ---")

            num_tasks = len(task_results)
            num_success = sum(1 for r in task_results if r.success)
            num_failed = num_tasks - num_success

            avg_time = sum(r.execution_time for r in task_results) / num_tasks if num_tasks > 0 else 0
            avg_tokens = sum(r.metrics.get('total_tokens', 0) for r in task_results) / num_tasks if num_tasks > 0 else 0
            total_pruned = sum(r.metrics.get('tokens_pruned', 0) for r in task_results)

            print(f"  Tasks: {num_tasks}")
            print(f"  Success: {num_success} ({num_success/num_tasks*100:.1f}%)")
            print(f"  Failed: {num_failed} ({num_failed/num_tasks*100:.1f}%)")
            print(f"  Avg execution time: {avg_time:.2f}s")
            print(f"  Avg tokens: {avg_tokens:.0f}")
            print(f"  Total tokens pruned: {total_pruned}")

        print(f"\n{'='*60}")


def main():
    """Test the experiment harness (requires mock agent)."""
    print("Experiment Harness Test")
    print("=" * 60)
    print("\nHarness initialized successfully!")
    print("\nTo fully test the harness, run this after implementing mock_agent.py:")
    print("  python experiments/swe_bench_extended/harness.py")
    print("\n✅ Harness scaffolding complete!")


if __name__ == "__main__":
    main()
