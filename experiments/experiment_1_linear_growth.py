"""
Experiment 1: Linear Growth Prevention with Adaptive Rate

Hypothesis: Context will NOT grow linearly like traditional chat systems,
and adaptive pruning rate will converge to steady-state behavior.

Method:
- Run 500 interactions with continuous adaptive pruning
- Measure token count after each interaction
- Track adaptive pruning rate adjustments over time
- Measure convergence time (when variance stabilizes)
- Compare with linear growth baseline

Expected:
- Token count oscillates around target, never exceeds 1.5x target
- Adaptive rate converges within 20 interactions
- Rate variance stabilizes (σ < 0.05)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pruner import ContinuousPruner
import matplotlib.pyplot as plt
import statistics


def calculate_convergence_time(rates, window_size=20, variance_threshold=0.05):
    """
    Calculate when adaptive rate converges to steady state.

    Convergence criteria: variance of last N rates < threshold

    Args:
        rates: List of adaptive pruning rates
        window_size: Size of rolling window for variance calculation
        variance_threshold: Maximum variance to consider converged

    Returns:
        int: Interaction number where convergence occurred, or -1 if not converged
    """
    if len(rates) < window_size:
        return -1

    for i in range(window_size, len(rates) + 1):
        window = rates[i - window_size:i]
        variance = statistics.variance(window)

        if variance < variance_threshold:
            return i  # First interaction where convergence achieved

    return -1  # Not converged


def run_experiment(num_interactions=500, target_size=20000):
    """
    Run linear growth prevention experiment with adaptive rate tracking.

    Args:
        num_interactions: Number of interactions to simulate (default: 500)
        target_size: Target context size in tokens (default: 20000)
    """

    print("="*60)
    print("EXPERIMENT 1: Linear Growth Prevention + Adaptive Rate")
    print("="*60)
    print()

    # Setup
    pruner = ContinuousPruner(target_size=target_size)

    # Add some core items to prevent cold-start issues
    pruner.add_core_item("Project requirement: High performance", "requirement")
    pruner.add_core_item("Architecture: Microservices", "architecture")

    print(f"Target size: {target_size} tokens")
    print(f"Running {num_interactions} interactions...")
    print(f"Adaptive rate range: [0.90, 1.10]")
    print()

    # Track metrics
    token_counts = []
    utilizations = []
    adaptive_rates = []

    # Run interactions
    for i in range(num_interactions):
        user_msg = f"User message {i}: " + "Implement feature " * 50
        agent_msg = f"Agent response {i}: " + "I will implement " * 60

        pruner.add_interaction(user_msg, agent_msg)

        tokens = pruner.get_total_tokens()
        token_counts.append(tokens)
        utilizations.append(tokens / target_size)

        # Get the adaptive rate that was just used
        current_rate = pruner.pruning_rate_history[-1]
        adaptive_rates.append(current_rate)

        if (i + 1) % 100 == 0:
            print(f"Interaction {i+1:3d}: {tokens:6d} tokens ({tokens/target_size:.1%}), rate={current_rate:.3f}")

    # Analysis - Token Count Behavior
    print("\n" + "="*60)
    print("RESULTS: TOKEN COUNT BEHAVIOR")
    print("="*60)
    print()

    min_tokens = min(token_counts)
    max_tokens = max(token_counts)
    avg_tokens = sum(token_counts) / len(token_counts)
    final_tokens = token_counts[-1]

    print(f"Min tokens:   {min_tokens:6d} ({min_tokens/target_size:.1%} of target)")
    print(f"Max tokens:   {max_tokens:6d} ({max_tokens/target_size:.1%} of target)")
    print(f"Avg tokens:   {avg_tokens:6.0f} ({avg_tokens/target_size:.1%} of target)")
    print(f"Final tokens: {final_tokens:6d} ({final_tokens/target_size:.1%} of target)")
    print()

    # Check for linear growth
    first_20 = sum(token_counts[:20]) / 20
    last_20 = sum(token_counts[-20:]) / 20
    growth = (last_20 - first_20) / first_20 * 100 if first_20 > 0 else 0

    print(f"First 20 avg: {first_20:6.0f} tokens")
    print(f"Last 20 avg:  {last_20:6.0f} tokens")
    print(f"Growth:       {growth:+6.1f}%")
    print()

    # Analysis - Adaptive Rate Behavior
    print("="*60)
    print("RESULTS: ADAPTIVE RATE BEHAVIOR")
    print("="*60)
    print()

    min_rate = min(adaptive_rates)
    max_rate = max(adaptive_rates)
    avg_rate = sum(adaptive_rates) / len(adaptive_rates)
    final_rate = adaptive_rates[-1]
    rate_stddev = statistics.stdev(adaptive_rates) if len(adaptive_rates) > 1 else 0

    print(f"Min rate:        {min_rate:.3f}")
    print(f"Max rate:        {max_rate:.3f}")
    print(f"Average rate:    {avg_rate:.3f}")
    print(f"Final rate:      {final_rate:.3f}")
    print(f"Std deviation:   {rate_stddev:.4f}")
    print()

    # Calculate convergence time
    convergence_time = calculate_convergence_time(adaptive_rates)

    if convergence_time > 0:
        print(f"✓ Convergence achieved at interaction: {convergence_time}")
        print(f"  (variance stabilized below 0.05 threshold)")
    else:
        print(f"⚠ Convergence not achieved within {num_interactions} interactions")
        # Calculate current variance for debugging
        if len(adaptive_rates) >= 20:
            recent_variance = statistics.variance(adaptive_rates[-20:])
            print(f"  (last 20 variance: {recent_variance:.4f}, threshold: 0.05)")
    print()

    # Acceptance Criteria Checks
    print("="*60)
    print("ACCEPTANCE CRITERIA")
    print("="*60)
    print()

    # AC1: Token count never exceeds 1.5x target
    if max_tokens < target_size * 1.5:
        print("✓ PASS: Token count stayed within 150% of target")
    else:
        print("✗ FAIL: Token count exceeded 150% of target")

    # AC2: No significant linear growth
    if abs(growth) < 20:
        print("✓ PASS: No significant linear growth detected (|growth| < 20%)")
    else:
        print("✗ FAIL: Linear growth detected (|growth| >= 20%)")

    # AC3: Adaptive rate converges within 20 interactions
    if convergence_time > 0 and convergence_time <= 20:
        print(f"✓ PASS: Adaptive rate converged within 20 interactions (at {convergence_time})")
    elif convergence_time > 20:
        print(f"⚠ WARNING: Adaptive rate converged but took {convergence_time} interactions (>20)")
    else:
        print("✗ FAIL: Adaptive rate did not converge")

    # AC4: Rate variance stabilizes (σ < 0.05)
    if len(adaptive_rates) >= 20:
        final_variance = statistics.variance(adaptive_rates[-20:])
        if final_variance < 0.05:
            print(f"✓ PASS: Final variance stabilized (σ={final_variance:.4f} < 0.05)")
        else:
            print(f"✗ FAIL: Final variance too high (σ={final_variance:.4f} >= 0.05)")
    else:
        print("⚠ N/A: Not enough data to calculate final variance")

    # AC5: Adaptive rate stays within bounds [0.90, 1.10]
    if min_rate >= 0.90 and max_rate <= 1.10:
        print(f"✓ PASS: Adaptive rate stayed within bounds [0.90, 1.10]")
    else:
        print(f"✗ FAIL: Adaptive rate violated bounds [0.90, 1.10]")

    print()

    # Plotting
    print("="*60)
    print("GENERATING PLOTS")
    print("="*60)
    print()

    try:
        fig = plt.figure(figsize=(15, 10))

        # Plot 1: Token Count Over Time
        plt.subplot(2, 2, 1)
        plt.plot(token_counts, label='Actual tokens', linewidth=2)
        plt.axhline(y=target_size, color='r', linestyle='--', label='Target', linewidth=1.5)
        plt.axhline(y=target_size*1.5, color='orange', linestyle='--', label='1.5x Target', linewidth=1.5)
        plt.xlabel('Interaction', fontsize=10)
        plt.ylabel('Tokens', fontsize=10)
        plt.title('Token Count Over Time', fontsize=12, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plot 2: Context Utilization Over Time
        plt.subplot(2, 2, 2)
        plt.plot(utilizations, label='Utilization', color='green', linewidth=2)
        plt.axhline(y=1.0, color='r', linestyle='--', label='100%', linewidth=1.5)
        plt.axhline(y=1.5, color='orange', linestyle='--', label='150%', linewidth=1.5)
        plt.xlabel('Interaction', fontsize=10)
        plt.ylabel('Utilization', fontsize=10)
        plt.title('Context Utilization Over Time', fontsize=12, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plot 3: Adaptive Rate Over Time
        plt.subplot(2, 2, 3)
        plt.plot(adaptive_rates, label='Adaptive rate', color='purple', linewidth=2)
        plt.axhline(y=1.0, color='gray', linestyle=':', label='Neutral (1.0)', linewidth=1)
        plt.axhline(y=0.90, color='red', linestyle='--', label='Min bound', linewidth=1.5)
        plt.axhline(y=1.10, color='red', linestyle='--', label='Max bound', linewidth=1.5)

        # Mark convergence point if achieved
        if convergence_time > 0:
            plt.axvline(x=convergence_time-1, color='green', linestyle='--',
                       label=f'Convergence (t={convergence_time})', linewidth=1.5)

        plt.xlabel('Interaction', fontsize=10)
        plt.ylabel('Pruning Rate', fontsize=10)
        plt.title('Adaptive Pruning Rate Over Time', fontsize=12, fontweight='bold')
        plt.ylim(0.85, 1.15)
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plot 4: Rate Variance (Rolling Window)
        plt.subplot(2, 2, 4)
        window_size = 20
        variances = []
        for i in range(window_size, len(adaptive_rates) + 1):
            window = adaptive_rates[i - window_size:i]
            var = statistics.variance(window)
            variances.append(var)

        plt.plot(range(window_size, len(adaptive_rates) + 1), variances,
                label=f'Variance (window={window_size})', color='orange', linewidth=2)
        plt.axhline(y=0.05, color='r', linestyle='--',
                   label='Convergence threshold', linewidth=1.5)

        # Mark convergence point if achieved
        if convergence_time > 0:
            plt.axvline(x=convergence_time, color='green', linestyle='--',
                       label=f'Convergence (t={convergence_time})', linewidth=1.5)

        plt.xlabel('Interaction', fontsize=10)
        plt.ylabel('Variance (σ²)', fontsize=10)
        plt.title('Rate Variance Over Time', fontsize=12, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('experiments/experiment_1_results.png', dpi=150)
        print("✓ Plot saved to: experiments/experiment_1_results.png")

    except ImportError:
        print("ℹ matplotlib not available, skipping plots")
    except Exception as e:
        print(f"⚠ Error generating plots: {e}")

    print()

    # Return summary for programmatic access
    return {
        'token_counts': token_counts,
        'adaptive_rates': adaptive_rates,
        'convergence_time': convergence_time,
        'max_tokens': max_tokens,
        'avg_rate': avg_rate,
        'final_variance': statistics.variance(adaptive_rates[-20:]) if len(adaptive_rates) >= 20 else None
    }


if __name__ == '__main__':
    run_experiment()
