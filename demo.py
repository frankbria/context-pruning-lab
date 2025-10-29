"""
Interactive demo of continuous context pruning

Run with: python demo.py
"""

from pruner import ContinuousPruner
import time


def print_separator():
    print("\n" + "="*60 + "\n")


def demo_basic_pruning():
    """Demonstrate basic pruning behavior"""
    print("=== DEMO 1: Basic Continuous Pruning ===\n")

    pruner = ContinuousPruner(target_size=10000)

    print(f"Target context size: {pruner.target_size} tokens")
    print(f"Pruning overhead: {pruner.pruning_overhead}x (removes 110% of added)\n")

    # Add some core decisions
    print("Adding CORE tier items (never pruned):")
    pruner.add_core_item("Project uses OAuth2 for authentication", "core_decision")
    pruner.add_core_item("Target: Python 3.11+", "requirement")
    pruner.add_core_item("Database: PostgreSQL", "architecture")
    print(f"  ✓ Added 3 core items\n")

    # Simulate interactions
    print("Simulating 10 interactions:\n")

    for i in range(10):
        user_msg = f"User message {i+1}: Implement feature X with approach Y. " * 15
        agent_msg = f"Agent response {i+1}: I'll implement that using pattern Z. " * 20

        metrics = pruner.add_interaction(user_msg, agent_msg)

        print(f"Interaction {i+1}:")
        print(f"  Added: {metrics.tokens_added} tokens")
        print(f"  Removed: {metrics.tokens_removed} tokens")
        print(f"  Current: {metrics.current_token_count}/{metrics.target_token_count} tokens")
        print(f"  Utilization: {metrics.current_token_count/metrics.target_token_count:.1%}")
        print(f"  Items: {len(pruner.context)}")

    print_separator()

    # Final summary
    summary = pruner.get_metrics_summary()
    print("=== FINAL SUMMARY ===\n")
    print(f"Total interactions: {summary['total_interactions']}")
    print(f"Total items: {summary['total_items']}")
    print(f"Total tokens: {summary['total_tokens']}/{summary['target_tokens']}")
    print(f"Utilization: {summary['utilization']:.1%}\n")

    print("Items by tier:")
    for tier, count in summary['items_by_tier'].items():
        tokens = summary['tokens_by_tier'][tier]
        if count > 0:
            print(f"  {tier}: {count} items, {tokens} tokens")

    print_separator()


def demo_steady_state():
    """Demonstrate steady-state oscillation"""
    print("=== DEMO 2: Steady-State Oscillation ===\n")
    print("Showing that context oscillates around target, never explodes\n")

    pruner = ContinuousPruner(target_size=5000)

    token_history = []

    print("Running 30 interactions...\n")
    for i in range(30):
        user_msg = "User message " * 50
        agent_msg = "Agent response " * 60

        pruner.add_interaction(user_msg, agent_msg)
        tokens = pruner.get_total_tokens()
        token_history.append(tokens)

        # Print every 5 interactions
        if (i + 1) % 5 == 0:
            print(f"Interaction {i+1:2d}: {tokens:5d} tokens")

    print(f"\nTarget: {pruner.target_size} tokens")
    print(f"Min:    {min(token_history)} tokens")
    print(f"Max:    {max(token_history)} tokens")
    print(f"Avg:    {sum(token_history)/len(token_history):.0f} tokens")

    # Check if oscillating (not growing linearly)
    first_10 = sum(token_history[:10]) / 10
    last_10 = sum(token_history[-10:]) / 10

    print(f"\nFirst 10 avg:  {first_10:.0f} tokens")
    print(f"Last 10 avg:   {last_10:.0f} tokens")
    print(f"Difference:    {abs(last_10 - first_10):.0f} tokens")

    if abs(last_10 - first_10) < pruner.target_size * 0.2:
        print("✓ Stable oscillation achieved!")
    else:
        print("⚠ Still stabilizing...")

    print_separator()


def demo_importance_preservation():
    """Demonstrate that important items are preserved"""
    print("=== DEMO 3: Importance Preservation ===\n")
    print("Showing that high-importance items survive aggressive pruning\n")

    pruner = ContinuousPruner(target_size=2000)  # Very small target

    # Add critical decision
    pruner.add_core_item("CRITICAL: Security audit required before release", "core_decision")
    print("Added CORE item: 'Security audit required'\n")

    # Add important message and pin it
    important = f"Important architectural decision: Use microservices pattern"
    pruner.add_interaction(important, "Acknowledged. I'll use microservices.")
    pruner.pin_item(pruner.context[-2])  # Pin the user message
    print("Added PINNED item: 'Use microservices pattern'\n")

    # Add many low-importance interactions
    print("Adding 50 low-importance interactions (debug logs)...\n")
    for i in range(50):
        pruner.add_interaction(
            f"Debug log {i}" * 100,
            f"Processing {i}" * 100
        )

    # Check what survived
    print("=== SURVIVAL CHECK ===\n")

    core_items = [i for i in pruner.context if i.tier == "CORE"]
    pinned_items = [i for i in pruner.context if i.pinned]

    print(f"Total items remaining: {len(pruner.context)}")
    print(f"CORE items: {len(core_items)}")
    print(f"Pinned items: {len(pinned_items)}")

    if core_items:
        print(f"\n✓ CORE item preserved: '{core_items[0].content[:50]}...'")

    if pinned_items:
        print(f"✓ Pinned item preserved: '{pinned_items[0].content[:50]}...'")

    print_separator()


def demo_comparison_with_linear():
    """Compare with linear growth (no pruning)"""
    print("=== DEMO 4: Comparison with Linear Growth ===\n")
    print("Showing difference between continuous pruning vs. no pruning\n")

    # Pruner with continuous pruning
    pruner_smart = ContinuousPruner(target_size=5000)

    # Simulate "dumb" pruner that never prunes
    class NoPruner:
        def __init__(self):
            self.context = []

        def add_interaction(self, user, agent):
            self.context.append({'content': user, 'tokens': len(user)//4})
            self.context.append({'content': agent, 'tokens': len(agent)//4})

        def get_total_tokens(self):
            return sum(i['tokens'] for i in self.context)

    pruner_dumb = NoPruner()

    smart_tokens = []
    dumb_tokens = []

    print("Running 25 interactions...\n")
    print("Interaction | Smart Pruner | Dumb Pruner | Difference")
    print("-" * 60)

    for i in range(25):
        msg = "User message " * 50
        resp = "Agent response " * 60

        pruner_smart.add_interaction(msg, resp)
        pruner_dumb.add_interaction(msg, resp)

        smart = pruner_smart.get_total_tokens()
        dumb = pruner_dumb.get_total_tokens()

        smart_tokens.append(smart)
        dumb_tokens.append(dumb)

        if (i + 1) % 5 == 0:
            diff = dumb - smart
            print(f"{i+1:11d} | {smart:12d} | {dumb:11d} | +{diff:10d}")

    print("\n=== RESULTS ===\n")
    print(f"Smart Pruner (final): {smart_tokens[-1]} tokens")
    print(f"Dumb Pruner (final):  {dumb_tokens[-1]} tokens")
    print(f"Savings: {dumb_tokens[-1] - smart_tokens[-1]} tokens ({(1 - smart_tokens[-1]/dumb_tokens[-1])*100:.1f}%)")

    print_separator()


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "CONTINUOUS CONTEXT PRUNING DEMO" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")

    demos = [
        ("Basic Pruning", demo_basic_pruning),
        ("Steady-State Oscillation", demo_steady_state),
        ("Importance Preservation", demo_importance_preservation),
        ("Comparison with Linear Growth", demo_comparison_with_linear)
    ]

    for i, (name, func) in enumerate(demos, 1):
        print(f"\nRunning Demo {i}/{len(demos)}: {name}")
        time.sleep(0.5)
        func()

        if i < len(demos):
            input("\nPress Enter to continue to next demo...")

    print("\n" + "="*60)
    print("  All demos completed!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
