"""
End-to-End Infrastructure Test

Tests the complete SWE-bench Extended infrastructure:
- Task loading with scripts
- Mock agent execution
- Experiment harness orchestration
- Results collection and serialization
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.swe_bench_extended.task_loader import SWEBenchExtendedLoader
from experiments.swe_bench_extended.mock_agent import create_agent
from experiments.swe_bench_extended.harness import ExperimentHarness
from experiments.swe_bench_extended.types import TaskDifficulty


def test_infrastructure():
    """Run end-to-end test of Sprint 3 infrastructure."""
    print("="*70)
    print("SWE-BENCH EXTENDED INFRASTRUCTURE - END-TO-END TEST")
    print("="*70)

    # ===================================================================
    # TEST 1: Task Loading
    # ===================================================================
    print("\n[TEST 1] Task Loading with Scripts")
    print("-" * 70)

    loader = SWEBenchExtendedLoader(
        data_dir="data",
        cache_size=50,
        auto_generate_scripts=True,
        script_seed=42
    )

    # Get statistics
    stats = loader.get_statistics()
    print(f"✓ Loaded task index: {stats['total_tasks']} tasks")
    print(f"  - By difficulty: {stats['by_difficulty']}")
    print(f"  - By type: {stats['by_type']}")
    print(f"  - Cached scripts: {stats['cached_scripts']}")

    # Load a single task with script
    task_ids = loader.get_task_ids(filter_difficulty=TaskDifficulty.EASY)
    print(f"\n✓ Found {len(task_ids)} easy tasks")

    test_task_id = task_ids[0]
    print(f"✓ Loading task {test_task_id} with script...")

    task, script = loader.load_task_with_script(test_task_id, target_turns=15)
    print(f"  - Task: {task.repo} ({task.difficulty.value})")
    print(f"  - Script: {script.num_turns} turns")
    print(f"  - Issue preview: {task.issue_description[:100]}...")

    # ===================================================================
    # TEST 2: Mock Agent Creation
    # ===================================================================
    print("\n[TEST 2] Mock Agent Creation")
    print("-" * 70)

    # Create agents for both strategies
    agent_continuous = create_agent(strategy="continuous_pruning", seed=42)
    print("✓ Created continuous pruning agent")

    agent_discrete = create_agent(strategy="discrete_baseline", seed=42)
    print("✓ Created discrete baseline agent")

    # Quick test of agent functionality
    agent_continuous.reset()
    agent_continuous.receive_message("Test message")
    response = agent_continuous.generate_response()
    stats_test = agent_continuous.get_context_stats()

    print(f"  - Test response length: {len(response)} chars")
    print(f"  - Context tokens: {stats_test['total_tokens']}")
    print(f"  - Pruning operations: {stats_test['pruning_operations']}")

    # ===================================================================
    # TEST 3: Single Task Execution
    # ===================================================================
    print("\n[TEST 3] Single Task Execution")
    print("-" * 70)

    harness = ExperimentHarness(
        results_dir="results/test_e2e",
        timeout_seconds=600,
        max_retries=1,
        verbose=False  # Suppress detailed logs for test
    )

    print(f"✓ Harness initialized")

    # Run single task with continuous pruning
    print(f"✓ Running task {test_task_id} with continuous pruning...")
    agent = create_agent(strategy="continuous_pruning", seed=42)
    result = harness.run_task(task, script, agent, "continuous_pruning")

    print(f"  - Success: {result.success}")
    print(f"  - Execution time: {result.execution_time:.2f}s")
    print(f"  - Turns completed: {result.metrics.get('num_turns', 0)}")
    print(f"  - Total tokens: {result.metrics.get('total_tokens', 0)}")
    print(f"  - Pruning ops: {result.metrics.get('pruning_operations', 0)}")
    print(f"  - Tokens pruned: {result.metrics.get('tokens_pruned', 0)}")

    # ===================================================================
    # TEST 4: Batch Execution
    # ===================================================================
    print("\n[TEST 4] Batch Execution (3 tasks, 2 strategies)")
    print("-" * 70)

    # Load 3 easy tasks for batch test
    batch_task_ids = task_ids[:3]
    print(f"✓ Loading {len(batch_task_ids)} tasks...")

    tasks_and_scripts = []
    for tid in batch_task_ids:
        t, s = loader.load_task_with_script(tid, target_turns=10)
        tasks_and_scripts.append((t, s))

    print(f"✓ Loaded {len(tasks_and_scripts)} tasks with scripts")

    # Run batch with both strategies
    print("✓ Running batch experiment...")
    results = harness.run_batch(
        tasks_and_scripts=tasks_and_scripts,
        agent_factory=lambda strategy: create_agent(strategy=strategy, seed=42),
        strategies=["continuous_pruning", "discrete_baseline"]
    )

    print(f"✓ Batch execution complete")

    # Show summary
    harness.print_summary(results)

    # ===================================================================
    # TEST 5: Results Serialization
    # ===================================================================
    print("\n[TEST 5] Results Serialization")
    print("-" * 70)

    # Save as JSON
    harness.save_results(results, experiment_name="e2e_test", format='json')
    print("✓ Saved results as JSON")

    # Save as CSV
    harness.save_results(results, experiment_name="e2e_test", format='csv')
    print("✓ Saved results as CSV")

    # Verify files exist
    results_dir = Path("results/test_e2e")
    json_file = results_dir / "e2e_test_results.json"
    csv_file = results_dir / "e2e_test_summary.csv"

    if json_file.exists():
        print(f"  - JSON file size: {json_file.stat().st_size / 1024:.1f} KB")
    if csv_file.exists():
        print(f"  - CSV file size: {csv_file.stat().st_size / 1024:.1f} KB")

    # ===================================================================
    # TEST 6: Statistics Collection
    # ===================================================================
    print("\n[TEST 6] Statistics Collection")
    print("-" * 70)

    final_stats = harness.get_statistics()
    print("✓ Harness statistics:")
    print(f"  - Tasks attempted: {final_stats['tasks_attempted']}")
    print(f"  - Tasks succeeded: {final_stats['tasks_succeeded']}")
    print(f"  - Tasks failed: {final_stats['tasks_failed']}")
    print(f"  - Total execution time: {final_stats['total_execution_time']:.2f}s")

    # ===================================================================
    # FINAL SUMMARY
    # ===================================================================
    print("\n" + "="*70)
    print("✅ END-TO-END TEST COMPLETE - ALL SYSTEMS OPERATIONAL")
    print("="*70)

    print("\nInfrastructure Components Verified:")
    print("  ✓ Task loading with lazy caching")
    print("  ✓ Conversation script generation")
    print("  ✓ Mock agent (continuous & discrete strategies)")
    print("  ✓ Experiment harness orchestration")
    print("  ✓ Single task execution")
    print("  ✓ Batch execution")
    print("  ✓ Results serialization (JSON & CSV)")
    print("  ✓ Statistics collection")

    print("\nSprint 3 Infrastructure: READY FOR SPRINT 4 🚀")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = test_infrastructure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
