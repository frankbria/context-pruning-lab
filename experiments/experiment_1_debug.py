"""
Debug run to understand cold-start behavior in Experiment 1
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pruner import ContinuousPruner


def debug_run():
    """Run with detailed output to understand what's happening"""

    print("Debug Run - First 10 Interactions")
    print("="*60)
    print()

    pruner = ContinuousPruner(target_size=20000)

    # Add CORE items
    pruner.add_core_item("Project requirement: High performance", "requirement")
    pruner.add_core_item("Architecture: Microservices", "architecture")

    print(f"After adding CORE items:")
    print(f"  Total tokens: {pruner.get_total_tokens()}")
    print(f"  Context items: {len(pruner.context)}")
    print()

    # Run 10 interactions with detailed output
    for i in range(10):
        user_msg = f"User message {i}: " + "Implement feature " * 50
        agent_msg = f"Agent response {i}: " + "I will implement " * 60

        print(f"Interaction {i+1}:")

        # Calculate what will be added
        from pruner import ContextItem
        user_item = ContextItem(user_msg, "user_message")
        agent_item = ContextItem(agent_msg, "agent_response")
        tokens_to_add = user_item.token_count + agent_item.token_count

        print(f"  Tokens to add: {tokens_to_add}")

        # Check adaptive rate before interaction
        rate_before = pruner.calculate_adaptive_rate()
        util_before = pruner.get_total_tokens() / pruner.target_size
        print(f"  Utilization before: {util_before:.2%}")
        print(f"  Adaptive rate: {rate_before:.3f}")
        print(f"  Target prune: {int(tokens_to_add * rate_before)}")

        # Add interaction
        metrics = pruner.add_interaction(user_msg, agent_msg)

        print(f"  Tokens added: {metrics.tokens_added}")
        print(f"  Tokens removed: {metrics.tokens_removed}")
        print(f"  Items removed: {metrics.items_removed}")
        print(f"  Total tokens after: {pruner.get_total_tokens()}")
        print(f"  Total items after: {len(pruner.context)}")

        # Show what's left in context
        hot_items = [item for item in pruner.context if item.tier == "HOT"]
        core_items = [item for item in pruner.context if item.tier == "CORE"]
        print(f"  CORE items: {len(core_items)}, HOT items: {len(hot_items)}")

        print()


if __name__ == '__main__':
    debug_run()
