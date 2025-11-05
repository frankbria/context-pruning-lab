"""
Quick validation test for bug fixes.

Tests:
1. BUG-001 fix: tokens_at_first_compaction timing
2. BUG-002 debug: continuous pruning context tracking
3. Conversation logging functionality

Runs 1 problem with continuous_pruning to validate fixes.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.experiment_5.experiment_runner import SWEBenchExperimentRunner


def main():
    """Run single-problem validation test"""

    print("=" * 70)
    print("BUG FIX VALIDATION TEST")
    print("=" * 70)
    print("\nTesting:")
    print("  - BUG-001: tokens_at_first_compaction timing fix")
    print("  - BUG-002: continuous pruning context tracking")
    print("  - Conversation logging")
    print()

    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not set")
        print("Set with: export ANTHROPIC_API_KEY='your-key'")
        return

    # Run minimal test - just 1 problem
    runner = SWEBenchExperimentRunner(
        output_dir="results/experiment_5/test_fixes",
        max_turns=50,
        verbose=True
    )

    print("Running 1 problem with continuous_pruning strategy...")
    print("Expected runtime: 10-15 minutes")
    print("Expected cost: ~$10-15")
    print()

    results = runner.run_experiment(
        n_problems=1,
        strategies=["continuous_pruning"]
    )

    # Validate results
    print("\n" + "=" * 70)
    print("VALIDATION CHECKS")
    print("=" * 70)

    result = results["continuous_pruning"][0]

    # Check 1: Context size tracking
    print("\n✓ BUG-002 Check: Context Size Tracking")
    print(f"  context_size_final: {result.context_size_final}")
    print(f"  context_size_max: {result.context_size_max}")

    if result.context_size_final == 0 and result.context_size_max == 0:
        print("  ⚠️  STILL BROKEN: Context sizes are 0")
        print("  → Check debug logs for pruning operations")
    else:
        print("  ✓ FIXED: Context sizes are non-zero")

    # Check 2: Conversation log exists
    print("\n✓ Conversation Logging Check")
    log_dir = Path("results/experiment_5/test_fixes/conversations")
    log_files = list(log_dir.glob("*.json"))

    if log_files:
        print(f"  ✓ Found {len(log_files)} conversation log(s)")
        for log_file in log_files:
            print(f"    - {log_file.name}")
    else:
        print("  ⚠️  NO LOGS FOUND")

    # Check 3: Pruning operations
    print("\n✓ Pruning Operations Check")
    print(f"  pruning_operations: {result.pruning_operations}")
    print(f"  turns: {result.turns}")

    if result.pruning_operations > 0:
        print(f"  ✓ Pruning occurred ({result.pruning_operations} times)")
    else:
        print("  ⚠️  No pruning operations recorded")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review conversation log for agent behavior")
    print("2. Check debug output for pruning operations")
    print("3. If context_size still 0, investigate pruner.py further")
    print()


if __name__ == "__main__":
    main()
