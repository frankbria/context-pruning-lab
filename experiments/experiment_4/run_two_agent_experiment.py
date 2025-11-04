"""
Two-Agent Experiment Runner

Runs experiments using the two-agent system (UserSimulator + CodingAgent)
with simple, executable test cases. This proves the architecture works
before integrating with complex SWE-bench infrastructure.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.experiment_4.simple_tasks import get_all_tasks, get_task
from experiments.experiment_4.user_simulator import UserSimulatorAgent
from experiments.experiment_4.agent import RealCodingAgent, AgentConfig
from experiments.experiment_4.orchestrator import ConversationOrchestrator, ConversationResult


class TwoAgentExperimentRunner:
    """
    Experiment runner for two-agent system.

    Executes multiple tasks with both strategies and compares:
    - Task completion rates
    - Token efficiency (coding agent only)
    - Execution time
    - Code quality
    """

    def __init__(
        self,
        api_key: str,
        num_tasks: int = 5,
        strategies: List[str] = None,
        results_dir: str = "results/experiment_4",
        verbose: bool = True
    ):
        """
        Initialize experiment runner.

        Args:
            api_key: Anthropic API key
            num_tasks: Number of tasks to run per strategy
            strategies: List of strategies to test
            results_dir: Directory for results
            verbose: Enable verbose output
        """
        self.api_key = api_key
        self.num_tasks = num_tasks
        self.strategies = strategies or ["continuous_pruning", "discrete_baseline"]
        self.results_dir = Path(results_dir)
        self.verbose = verbose

        # Create results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Load tasks
        all_tasks = get_all_tasks()
        self.tasks = all_tasks[:num_tasks]

        if self.verbose:
            print("=" * 70)
            print("TWO-AGENT EXPERIMENT")
            print("=" * 70)
            print(f"\nConfiguration:")
            print(f"  Tasks: {len(self.tasks)}")
            print(f"  Strategies: {', '.join(self.strategies)}")
            print(f"  Results: {self.results_dir}")

    def run(self) -> Dict[str, Any]:
        """
        Run the complete experiment.

        Returns:
            Dictionary with experiment results
        """
        all_results = {}

        for strategy in self.strategies:
            if self.verbose:
                print(f"\n{'-' * 70}")
                print(f"Running strategy: {strategy}")
                print("-" * 70)

            strategy_results = []

            for i, task in enumerate(self.tasks, 1):
                if self.verbose:
                    print(f"\n[{i}/{len(self.tasks)}] Task: {task.task_id}")

                result = self._run_task(task, strategy)
                strategy_results.append(result)

                if self.verbose:
                    status = "✅ PASS" if result['success'] else "❌ FAIL"
                    print(f"  {status} - {result['total_turns']} turns, "
                          f"{result['coding_agent_tokens']:,} tokens, "
                          f"{result['execution_time']:.1f}s")

            all_results[strategy] = strategy_results

        # Save and summarize
        self._save_results(all_results)
        self._print_summary(all_results)

        return all_results

    def _run_task(self, task, strategy: str) -> Dict[str, Any]:
        """
        Execute a single task with given strategy.

        Args:
            task: SimpleTask to execute
            strategy: Strategy name

        Returns:
            Task result dictionary
        """
        try:
            # Create user simulator
            user_sim = UserSimulatorAgent(
                task_description=task.description,
                test_cases=task.test_cases,
                gold_solution=task.gold_solution,
                api_key=self.api_key
            )

            # Create coding agent with strategy
            agent_config = AgentConfig(
                strategy=strategy,
                api_key=self.api_key
            )
            coding_agent = RealCodingAgent(agent_config)

            # Create orchestrator
            orchestrator = ConversationOrchestrator(
                user_simulator=user_sim,
                coding_agent=coding_agent,
                max_turns=30,
                verbose=False  # Suppress turn-by-turn output
            )

            # Run conversation
            result = orchestrator.run_conversation()

            # Convert to dict format
            return {
                'task_id': task.task_id,
                'strategy': strategy,
                'success': result.success,
                'total_turns': result.total_turns,
                'coding_agent_tokens': result.coding_agent_tokens,
                'user_sim_tokens': result.user_sim_tokens,
                'execution_time': result.execution_time,
                'test_results': result.test_results,
                'solution_code': result.solution_code,
                'error_message': result.error_message,
                'conversation_length': len(result.conversation_history)
            }

        except Exception as e:
            # Handle errors gracefully
            return {
                'task_id': task.task_id,
                'strategy': strategy,
                'success': False,
                'total_turns': 0,
                'coding_agent_tokens': 0,
                'user_sim_tokens': 0,
                'execution_time': 0.0,
                'test_results': None,
                'solution_code': None,
                'error_message': str(e),
                'conversation_length': 0
            }

    def _save_results(self, results: Dict[str, List[Dict]]):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"two_agent_exp_{timestamp}.json"
        filepath = self.results_dir / filename

        # Add metadata
        output = {
            'metadata': {
                'timestamp': timestamp,
                'num_tasks': self.num_tasks,
                'strategies': self.strategies,
            },
            'results': results
        }

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)

        if self.verbose:
            print(f"\n✅ Results saved to: {filepath}")

    def _print_summary(self, results: Dict[str, List[Dict]]):
        """Print experiment summary."""
        print(f"\n{'=' * 70}")
        print("EXPERIMENT SUMMARY")
        print("=" * 70)

        for strategy, task_results in results.items():
            print(f"\n--- Strategy: {strategy} ---")

            num_tasks = len(task_results)
            num_success = sum(1 for r in task_results if r['success'])

            avg_tokens = sum(r['coding_agent_tokens'] for r in task_results) / num_tasks
            avg_turns = sum(r['total_turns'] for r in task_results) / num_tasks
            avg_time = sum(r['execution_time'] for r in task_results) / num_tasks

            print(f"  Success rate: {num_success}/{num_tasks} ({num_success/num_tasks*100:.1f}%)")
            print(f"  Avg tokens (coding agent): {avg_tokens:,.0f}")
            print(f"  Avg turns: {avg_turns:.1f}")
            print(f"  Avg time: {avg_time:.1f}s")

            # Show failed tasks
            failed = [r for r in task_results if not r['success']]
            if failed:
                print(f"\n  Failed tasks:")
                for r in failed:
                    error_preview = (r['error_message'] or 'No tests passed')[:50]
                    print(f"    - {r['task_id']}: {error_preview}")

        # Comparison
        if len(results) == 2:
            print(f"\n{'=' * 70}")
            print("STRATEGY COMPARISON")
            print("=" * 70)

            s1, s2 = list(results.keys())
            r1, r2 = results[s1], results[s2]

            success_1 = sum(1 for r in r1 if r['success'])
            success_2 = sum(1 for r in r2 if r['success'])

            tokens_1 = sum(r['coding_agent_tokens'] for r in r1)
            tokens_2 = sum(r['coding_agent_tokens'] for r in r2)

            print(f"\nSuccess Rate:")
            print(f"  {s1}: {success_1}/{len(r1)} ({success_1/len(r1)*100:.1f}%)")
            print(f"  {s2}: {success_2}/{len(r2)} ({success_2/len(r2)*100:.1f}%)")

            print(f"\nTotal Tokens (Coding Agent):")
            print(f"  {s1}: {tokens_1:,}")
            print(f"  {s2}: {tokens_2:,}")

            if tokens_2 > 0:
                efficiency = (tokens_2 - tokens_1) / tokens_2 * 100
                print(f"\n{s1} uses {efficiency:+.1f}% tokens vs {s2}")

        print(f"\n{'=' * 70}")


def main():
    """Run two-agent experiment."""
    import argparse
    from dotenv import load_dotenv

    # Load .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Run two-agent experiment with simple tasks'
    )
    parser.add_argument(
        '--num-tasks',
        type=int,
        default=5,
        help='Number of tasks to run (default: 5)'
    )
    parser.add_argument(
        '--strategies',
        nargs='+',
        default=['continuous_pruning', 'discrete_baseline'],
        help='Strategies to test'
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default='results/experiment_4',
        help='Results directory'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Disable verbose output'
    )

    args = parser.parse_args()

    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n⚠️  ERROR: ANTHROPIC_API_KEY not found")
        print("\nSet it in .env file or export:")
        print("  export ANTHROPIC_API_KEY='your-key'")
        sys.exit(1)

    # Run experiment
    runner = TwoAgentExperimentRunner(
        api_key=api_key,
        num_tasks=args.num_tasks,
        strategies=args.strategies,
        results_dir=args.results_dir,
        verbose=not args.quiet
    )

    try:
        results = runner.run()

        # Exit with success if any strategy achieved >0% completion
        any_success = any(
            any(r['success'] for r in strategy_results)
            for strategy_results in results.values()
        )

        sys.exit(0 if any_success else 1)

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
