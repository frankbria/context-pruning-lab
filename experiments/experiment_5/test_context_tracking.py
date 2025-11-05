#!/usr/bin/env python3
"""
Quick test to verify context tracking is working.
This bypasses SWE-bench loading and just tests the agent + pruner directly.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from experiments.experiment_4.agent import RealCodingAgent, AgentConfig

# Load API key
from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== Testing Context Tracking ===\n")

    # Create agent with continuous pruning
    config = AgentConfig(
        strategy="continuous_pruning",
        target_context_size=156_250
    )

    agent = RealCodingAgent(config)
    print(f"✅ Created agent with strategy: {agent.strategy}")

    # Test 1: Initial state
    stats = agent.get_context_stats()
    print(f"\nInitial stats:")
    print(f"  context_size: {stats['context_size']}")
    print(f"  num_messages: {stats['num_messages']}")

    # Test 2: Add first interaction
    print("\n--- Turn 1 ---")
    agent.receive_message("Hello, what's 2+2?")
    response = agent.generate_response()
    print(f"Agent response: {response[:100]}...")

    stats = agent.get_context_stats()
    print(f"After turn 1:")
    print(f"  context_size: {stats['context_size']}")
    print(f"  num_messages: {stats['num_messages']}")
    print(f"  pruning_operations: {stats['pruning_operations']}")

    # Test 3: Add second interaction
    print("\n--- Turn 2 ---")
    agent.receive_message("And what's 3+3?")
    response = agent.generate_response()
    print(f"Agent response: {response[:100]}...")

    stats = agent.get_context_stats()
    print(f"After turn 2:")
    print(f"  context_size: {stats['context_size']}")
    print(f"  num_messages: {stats['num_messages']}")
    print(f"  pruning_operations: {stats['pruning_operations']}")

    # Test 4: Inspect context manager directly
    print("\n--- Direct Context Inspection ---")
    print(f"context_manager.context has {len(agent.context_manager.context)} items")
    print(f"context_manager.get_total_tokens() returns: {agent.context_manager.get_total_tokens()}")

    if agent.context_manager.context:
        first_item = agent.context_manager.context[0]
        print(f"\nFirst item:")
        print(f"  type: {first_item.item_type}")
        print(f"  content length: {len(first_item.content)} chars")
        print(f"  token_count: {first_item.token_count}")
        print(f"  importance: {first_item.importance}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
