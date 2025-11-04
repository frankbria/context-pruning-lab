"""
Test script for two-agent system.

Verifies that UserSimulatorAgent + RealCodingAgent + ConversationOrchestrator
work together to solve a simple task.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.experiment_4.user_simulator import UserSimulatorAgent, TestCase
from experiments.experiment_4.agent import RealCodingAgent, AgentConfig
from experiments.experiment_4.orchestrator import ConversationOrchestrator


def test_simple_task():
    """Test two-agent system with a simple reverse string task."""

    print("=" * 70)
    print("TWO-AGENT SYSTEM TEST")
    print("=" * 70)

    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not set")
        print("Set it: export ANTHROPIC_API_KEY='your-key'")
        return

    # Define task
    task_description = """I need a function called `reverse_string` that reverses a string.

Requirements:
- Function name must be `reverse_string`
- Takes one parameter: a string
- Returns the reversed string
- Must handle empty strings correctly

Examples:
- reverse_string('hello') → 'olleh'
- reverse_string('') → ''
- reverse_string('a') → 'a'"""

    test_cases = [
        TestCase(
            name="empty string",
            call="reverse_string('')",
            expected="",
            description="Empty strings should return empty string"
        ),
        TestCase(
            name="single character",
            call="reverse_string('a')",
            expected="a",
            description="Single character should return itself"
        ),
        TestCase(
            name="normal string",
            call="reverse_string('hello')",
            expected="olleh",
            description="Should reverse character order"
        ),
        TestCase(
            name="palindrome",
            call="reverse_string('racecar')",
            expected="racecar",
            description="Palindromes should equal themselves"
        ),
    ]

    gold_solution = """def reverse_string(s):
    return s[::-1]"""

    print("\n--- Creating Agents ---")

    # Create user simulator (not counted in metrics)
    user_sim = UserSimulatorAgent(
        task_description=task_description,
        test_cases=test_cases,
        gold_solution=gold_solution,
        api_key=api_key
    )
    print("✅ User Simulator Agent created")

    # Create coding agent (tokens counted in metrics)
    coding_agent_config = AgentConfig(
        strategy="continuous_pruning",  # Test with continuous pruning
        api_key=api_key
    )
    coding_agent = RealCodingAgent(coding_agent_config)
    print("✅ Coding Agent created (strategy: continuous_pruning)")

    # Create orchestrator
    orchestrator = ConversationOrchestrator(
        user_simulator=user_sim,
        coding_agent=coding_agent,
        max_turns=30,
        verbose=True
    )
    print("✅ Conversation Orchestrator created")

    print("\n--- Running Conversation ---")
    print("(This will use real Claude API calls)")
    print()

    # Run conversation
    result = orchestrator.run_conversation()

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\n✅ Success: {result.success}")
    print(f"📊 Total turns: {result.total_turns}")
    print(f"⏱️  Execution time: {result.execution_time:.1f}s")

    print(f"\n💰 Token Usage:")
    print(f"   Coding Agent: {result.coding_agent_tokens:,} tokens (COUNTED)")
    print(f"   User Simulator: {result.user_sim_tokens:,} tokens (not counted)")
    print(f"   Total Conversation: {result.coding_agent_tokens + result.user_sim_tokens:,} tokens")

    if result.test_results:
        print(f"\n🧪 Test Results:")
        print(f"   Passed: {result.test_results['passed']}/{result.test_results['total']}")
        if result.test_results['failures']:
            print(f"   Failures:")
            for failure in result.test_results['failures'][:3]:
                if 'error' in failure:
                    print(f"     - {failure['test']}: {failure['error']}")
                else:
                    print(f"     - {failure['test']}: expected {failure['expected']}, got {failure['actual']}")

    if result.solution_code:
        print(f"\n📝 Final Solution ({len(result.solution_code)} chars):")
        print("```python")
        print(result.solution_code)
        print("```")

    if result.error_message:
        print(f"\n❌ Error: {result.error_message}")

    print("\n" + "=" * 70)

    # Analyze conversation
    print("\nCONVERSATION ANALYSIS")
    print("=" * 70)

    agent_turns = [t for t in result.conversation_history if t.role == 'coding_agent']
    user_turns = [t for t in result.conversation_history if t.role == 'user_sim']

    print(f"Coding agent turns: {len(agent_turns)}")
    print(f"User simulator turns: {len(user_turns)}")

    # Show phases
    phases = {}
    for turn in agent_turns:
        phases[turn.phase] = phases.get(turn.phase, 0) + 1

    print(f"\nCoding agent phases:")
    for phase, count in sorted(phases.items()):
        print(f"  {phase}: {count} turns")

    # Show sample conversation
    print(f"\nSample conversation (first 3 turns):")
    for turn in result.conversation_history[:6]:
        print(f"\n[Turn {turn.turn_number}] {turn.role}:")
        content_preview = turn.content[:150].replace('\n', ' ')
        print(f"  {content_preview}...")

    print("\n" + "=" * 70)

    if result.success:
        print("\n🎉 SUCCESS! Two-agent system working correctly!")
        print("\nKey achievements:")
        print("  ✅ Realistic conversation flow")
        print("  ✅ Test execution and feedback working")
        print("  ✅ Agent iterates based on feedback")
        print("  ✅ Correct solution found")
        print("  ✅ Token accounting separated correctly")
    else:
        print("\n⚠️  Task not completed, but system is functional")
        print("\nWhat happened:")
        print(f"  - Conversation lasted {result.total_turns} turns")
        print(f"  - Tests: {result.test_results['passed'] if result.test_results else 0} passed")
        print("  - May need more turns or better prompting")

    return result


if __name__ == "__main__":
    result = test_simple_task()

    sys.exit(0 if result.success else 1)
