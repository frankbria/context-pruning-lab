"""
Experiment 1: Linear Growth Prevention

Hypothesis: Context will NOT grow linearly like traditional chat systems.

Method:
- Run 1000 interactions with continuous pruning
- Measure token count after each interaction
- Compare with linear growth baseline

Expected: Token count oscillates around target, never exceeds 1.5x target
"""

import sys
sys.path.append('..')

from pruner import ContinuousPruner
import matplotlib.pyplot as plt


def run_experiment():
    """Run linear growth prevention experiment"""

    print("="*60)
    print("EXPERIMENT 1: Linear Growth Prevention")
    print("="*60)
    print()

    # Setup
    target_size = 20000
    num_interactions = 100
    pruner = ContinuousPruner(target_size=target_size)

    # Add some core items
    pruner.add_core_item("Project requirement: High performance", "requirement")
    pruner.add_core_item("Architecture: Microservices", "architecture")

    print(f"Target size: {target_size} tokens")
    print(f"Running {num_interactions} interactions...\n")

    # Track metrics
    token_counts = []
    utilizations = []

    # Run interactions
    for i in range(num_interactions):
        user_msg = f"User message {i}: " + "Implement feature " * 50
        agent_msg = f"Agent response {i}: " + "I will implement " * 60

        pruner.add_interaction(user_msg, agent_msg)

        tokens = pruner.get_total_tokens()
        token_counts.append(tokens)
        utilizations.append(tokens / target_size)

        if (i + 1) % 20 == 0:
            print(f"Interaction {i+1:3d}: {tokens:6d} tokens ({tokens/target_size:.1%})")

    # Analysis
    print("\n" + "="*60)
    print("RESULTS")
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
    growth = (last_20 - first_20) / first_20 * 100

    print(f"First 20 avg: {first_20:6.0f} tokens")
    print(f"Last 20 avg:  {last_20:6.0f} tokens")
    print(f"Growth:       {growth:+6.1f}%")
    print()

    # Verdict
    if max_tokens < target_size * 1.5:
        print("✓ PASS: Token count stayed within 150% of target")
    else:
        print("✗ FAIL: Token count exceeded 150% of target")

    if abs(growth) < 20:
        print("✓ PASS: No significant linear growth detected")
    else:
        print("✗ FAIL: Linear growth detected")

    # Plot if matplotlib available
    try:
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.plot(token_counts, label='Actual tokens')
        plt.axhline(y=target_size, color='r', linestyle='--', label='Target')
        plt.axhline(y=target_size*1.5, color='orange', linestyle='--', label='1.5x Target')
        plt.xlabel('Interaction')
        plt.ylabel('Tokens')
        plt.title('Token Count Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.subplot(1, 2, 2)
        plt.plot(utilizations, label='Utilization')
        plt.axhline(y=1.0, color='r', linestyle='--', label='100%')
        plt.axhline(y=1.5, color='orange', linestyle='--', label='150%')
        plt.xlabel('Interaction')
        plt.ylabel('Utilization')
        plt.title('Context Utilization Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('experiments/experiment_1_results.png', dpi=150)
        print("\n✓ Plot saved to: experiments/experiment_1_results.png")

    except ImportError:
        print("\nℹ matplotlib not available, skipping plots")

    print()


if __name__ == '__main__':
    run_experiment()
