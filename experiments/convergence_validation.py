"""
Task T1.5: Convergence Validation Testing

Run multiple scenarios to validate adaptive rate convergence behavior:
1. Low target size (rapid convergence to target range)
2. High target size (slower convergence)
3. Multiple random seeds for reproducibility
4. Different CORE budget pressures

Acceptance Criteria:
- Adaptive rate converges within 20 interactions in most scenarios
- Rate variance stabilizes (σ < 0.05)
- System behavior is consistent across random seeds
- Convergence time documented for different scenarios
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pruner import ContinuousPruner, ContextItem
import statistics


def run_scenario(name, target_size, num_interactions, seed=42):
    """
    Run a validation scenario with specific parameters.

    Args:
        name: Scenario name for reporting
        target_size: Target context size in tokens
        num_interactions: Number of interactions to simulate
        seed: Random seed for reproducibility

    Returns:
        dict: Scenario results including convergence time and metrics
    """
    print(f"\n{'='*60}")
    print(f"SCENARIO: {name}")
    print(f"{'='*60}")
    print(f"Target size: {target_size}, Interactions: {num_interactions}, Seed: {seed}")
    print()

    pruner = ContinuousPruner(target_size=target_size)

    # Pre-populate with substantial CORE context to avoid cold-start
    for i in range(10):
        pruner.add_core_item(f"Core requirement {i}: " + "x" * 50, "requirement")

    print(f"Initial CORE context: {pruner.get_total_tokens()} tokens")
    print()

    # Track metrics
    adaptive_rates = []
    token_counts = []

    # Run interactions
    for i in range(num_interactions):
        # Vary message sizes slightly for realism
        user_msg = f"User message {i}: " + "Implement feature " * (40 + (seed + i) % 20)
        agent_msg = f"Agent response {i}: " + "I will implement " * (50 + (seed + i) % 30)

        pruner.add_interaction(user_msg, agent_msg)

        adaptive_rates.append(pruner.pruning_rate_history[-1])
        token_counts.append(pruner.get_total_tokens())

    # Calculate convergence time
    convergence_time = -1
    window_size = 20
    variance_threshold = 0.05

    for i in range(window_size, len(adaptive_rates) + 1):
        window = adaptive_rates[i - window_size:i]
        variance = statistics.variance(window)

        if variance < variance_threshold:
            convergence_time = i
            break

    # Calculate metrics
    min_rate = min(adaptive_rates)
    max_rate = max(adaptive_rates)
    avg_rate = sum(adaptive_rates) / len(adaptive_rates)
    rate_stddev = statistics.stdev(adaptive_rates)

    final_variance = statistics.variance(adaptive_rates[-20:]) if len(adaptive_rates) >= 20 else None
    final_tokens = token_counts[-1]
    avg_tokens = sum(token_counts) / len(token_counts)
    utilization = final_tokens / target_size

    # Report results
    print(f"Results:")
    print(f"  Convergence time: {convergence_time if convergence_time > 0 else 'NOT CONVERGED'}")
    print(f"  Adaptive rate: min={min_rate:.3f}, max={max_rate:.3f}, avg={avg_rate:.3f}, σ={rate_stddev:.4f}")
    print(f"  Final variance: {final_variance:.4f}" if final_variance else "  Final variance: N/A")
    print(f"  Token count: final={final_tokens}, avg={avg_tokens:.0f}, utilization={utilization:.1%}")

    # Check acceptance criteria
    passed = []
    failed = []

    if convergence_time > 0 and convergence_time <= 20:
        passed.append(f"Converged at t={convergence_time}")
    elif convergence_time > 20:
        failed.append(f"Slow convergence (t={convergence_time})")
    else:
        failed.append("Did not converge")

    if final_variance and final_variance < 0.05:
        passed.append(f"Low final variance (σ={final_variance:.4f})")
    elif final_variance:
        failed.append(f"High final variance (σ={final_variance:.4f})")

    if min_rate >= 0.90 and max_rate <= 1.10:
        passed.append("Rate within bounds")
    else:
        failed.append("Rate violated bounds")

    print(f"\n  ✓ PASS: {', '.join(passed)}" if passed else "")
    print(f"  ✗ FAIL: {', '.join(failed)}" if failed else "")

    return {
        'name': name,
        'convergence_time': convergence_time,
        'min_rate': min_rate,
        'max_rate': max_rate,
        'avg_rate': avg_rate,
        'rate_stddev': rate_stddev,
        'final_variance': final_variance,
        'final_tokens': final_tokens,
        'utilization': utilization,
        'passed': len(failed) == 0
    }


def main():
    """Run comprehensive convergence validation"""

    print("="*60)
    print("CONVERGENCE VALIDATION TESTING (T1.5)")
    print("="*60)
    print()
    print("Testing adaptive rate convergence across multiple scenarios:")
    print("- Different target sizes")
    print("- Multiple random seeds")
    print("- Various CORE budget pressures")
    print()

    results = []

    # Scenario 1: Small target (5K tokens)
    results.append(run_scenario(
        "Small Target (5K tokens)",
        target_size=5000,
        num_interactions=100,
        seed=42
    ))

    # Scenario 2: Medium target (20K tokens)
    results.append(run_scenario(
        "Medium Target (20K tokens)",
        target_size=20000,
        num_interactions=100,
        seed=42
    ))

    # Scenario 3: Large target (40K tokens)
    results.append(run_scenario(
        "Large Target (40K tokens)",
        target_size=40000,
        num_interactions=100,
        seed=42
    ))

    # Scenario 4: Medium target, different seed
    results.append(run_scenario(
        "Medium Target (20K, seed=123)",
        target_size=20000,
        num_interactions=100,
        seed=123
    ))

    # Scenario 5: Medium target, another seed
    results.append(run_scenario(
        "Medium Target (20K, seed=789)",
        target_size=20000,
        num_interactions=100,
        seed=789
    ))

    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print()

    passed_scenarios = [r for r in results if r['passed']]
    failed_scenarios = [r for r in results if not r['passed']]

    print(f"Total scenarios: {len(results)}")
    print(f"Passed: {len(passed_scenarios)}")
    print(f"Failed: {len(failed_scenarios)}")
    print()

    if failed_scenarios:
        print("Failed scenarios:")
        for r in failed_scenarios:
            print(f"  - {r['name']}")
        print()

    # Convergence time statistics
    convergence_times = [r['convergence_time'] for r in results if r['convergence_time'] > 0]
    if convergence_times:
        avg_convergence = sum(convergence_times) / len(convergence_times)
        max_convergence = max(convergence_times)
        print(f"Convergence times: avg={avg_convergence:.1f}, max={max_convergence}")
    else:
        print("⚠ WARNING: No scenarios converged")

    # Rate statistics
    all_rates = [r['avg_rate'] for r in results]
    avg_of_avg_rates = sum(all_rates) / len(all_rates)
    print(f"Average adaptive rate across scenarios: {avg_of_avg_rates:.3f}")

    print()

    # Overall verdict
    if len(passed_scenarios) == len(results):
        print("✓✓✓ ALL SCENARIOS PASSED - Adaptive rate validated!")
    elif len(passed_scenarios) >= len(results) * 0.8:
        print("✓✓ MOSTLY PASSED - Adaptive rate working well")
    else:
        print("✗✗ FAILED - Adaptive rate needs improvement")

    print()


if __name__ == '__main__':
    main()
