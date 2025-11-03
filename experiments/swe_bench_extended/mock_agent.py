"""
Mock Coding Agent for Testing

Simulates a coding agent without requiring LLM API calls.
Used for testing infrastructure before integrating real agent in Sprint 4.
"""

import random
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ContextState:
    """Tracks the agent's context state."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    total_tokens: int = 0
    context_size: int = 0  # Current size after pruning
    pruning_operations: int = 0
    tokens_pruned: int = 0


class MockCodingAgent:
    """
    Mock coding agent that simulates realistic behavior for testing.

    Features:
    - Deterministic token usage (based on seed)
    - Simulates context growth (~500-2000 tokens per turn)
    - Compatible with both continuous pruning and discrete baseline
    - Tracks context statistics for metrics collection
    - Generates fake code for testing purposes
    """

    def __init__(
        self,
        strategy: str = "continuous_pruning",
        seed: int = 42,
        tokens_per_turn_range: tuple[int, int] = (500, 2000),
        max_context_size: int = 100_000
    ):
        """
        Initialize mock agent.

        Args:
            strategy: Context management strategy ('continuous_pruning' or 'discrete_baseline')
            seed: Random seed for deterministic behavior
            tokens_per_turn_range: Range of tokens to add per turn (min, max)
            max_context_size: Maximum context size before requiring pruning
        """
        self.strategy = strategy
        self.seed = seed
        self.tokens_per_turn_range = tokens_per_turn_range
        self.max_context_size = max_context_size

        # Initialize random generator with seed for determinism
        self.rng = random.Random(seed)

        # Context state
        self.context = ContextState()

        # Generated code accumulator
        self.generated_code_parts = []

        # Strategy-specific parameters
        if strategy == "discrete_baseline":
            self.pruning_threshold = 0.8  # Prune at 80% capacity
        else:  # continuous_pruning
            self.pruning_threshold = 1.0  # No threshold, prune after every turn

    def reset(self):
        """Reset agent for a new task."""
        self.context = ContextState()
        self.generated_code_parts = []
        self.rng = random.Random(self.seed)  # Reset RNG for determinism

    def receive_message(self, content: str):
        """
        Process a user message.

        Args:
            content: User message content
        """
        # Simulate token count for user message (~1 token per 4 characters)
        tokens = len(content) // 4

        # Add to context
        self.context.messages.append({
            'role': 'user',
            'content': content
        })
        self.context.total_tokens += tokens
        self.context.context_size += tokens

    def generate_response(self) -> str:
        """
        Generate agent response to the last user message.

        Returns:
            Generated response content
        """
        # Simulate response generation with random token count in range
        response_tokens = self.rng.randint(*self.tokens_per_turn_range)

        # Generate fake response content
        response = self._generate_fake_response(response_tokens)

        # Add to context
        self.context.messages.append({
            'role': 'assistant',
            'content': response
        })
        self.context.total_tokens += response_tokens
        self.context.context_size += response_tokens

        # Generate some fake code during coding/debugging phases
        if self.rng.random() < 0.5:  # 50% chance to generate code
            code = self._generate_fake_code()
            self.generated_code_parts.append(code)

        # Apply pruning strategy
        self._apply_pruning_strategy()

        return response

    def _generate_fake_response(self, tokens: int) -> str:
        """
        Generate fake response content.

        Args:
            tokens: Approximate number of tokens to generate

        Returns:
            Fake response string
        """
        # Generate approximately the right number of characters (4 chars ≈ 1 token)
        num_chars = tokens * 4

        templates = [
            "I'll help you implement this feature. Let me analyze the requirements...",
            "Based on the issue description, here's my proposed approach...",
            "I've identified the bug in the code. The problem is...",
            "Let me refactor this section to improve code quality...",
            "Running the tests shows the following results...",
            "I've reviewed the code and have some suggestions for improvement...",
            "Let me break down this complex task into smaller steps...",
            "I've implemented the requested changes. Here's what I did...",
            "The error occurs because of this edge case. Let me fix it...",
            "I've optimized the implementation for better performance..."
        ]

        # Pick a random template
        response = self.rng.choice(templates)

        # Pad to approximate token count with filler text
        while len(response) < num_chars:
            response += " " + self.rng.choice([
                "Additional context information.",
                "Detailed analysis of the code structure.",
                "Explanation of the implementation approach.",
                "Discussion of potential edge cases.",
                "Performance considerations for this solution.",
                "Testing strategy and validation approach.",
                "Integration with existing codebase patterns.",
                "Documentation of key design decisions."
            ])

        return response[:num_chars]  # Trim to exact size

    def _generate_fake_code(self) -> str:
        """
        Generate fake code snippet.

        Returns:
            Fake code string
        """
        code_templates = [
            """def process_data(input_data):
    result = []
    for item in input_data:
        processed = transform(item)
        result.append(processed)
    return result
""",
            """class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = {}

    def process(self, data):
        if data in self.cache:
            return self.cache[data]
        result = self._process_internal(data)
        self.cache[data] = result
        return result
""",
            """try:
    result = perform_operation(data)
    if result is None:
        raise ValueError("Operation returned None")
    return result
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return default_value
""",
            """if condition_a and condition_b:
    handle_case_a()
elif condition_c:
    handle_case_c()
else:
    handle_default_case()
""",
        ]

        return self.rng.choice(code_templates)

    def _apply_pruning_strategy(self):
        """Apply the configured pruning strategy."""
        if self.strategy == "continuous_pruning":
            # Prune after every turn
            self._prune_context()
        elif self.strategy == "discrete_baseline":
            # Only prune when hitting threshold
            utilization = self.context.context_size / self.max_context_size
            if utilization >= self.pruning_threshold:
                self._prune_context()

    def _prune_context(self):
        """
        Simulate context pruning operation.

        In real implementation, this would use importance scoring.
        Here we just simulate removing tokens.
        """
        if self.context.context_size == 0:
            return

        # Simulate pruning parameters
        if self.strategy == "continuous_pruning":
            # Continuous: prune aggressively, aim for 70% retention
            retention_rate = 0.7
        else:  # discrete_baseline
            # Discrete: prune to 50% when threshold hit
            retention_rate = 0.5

        # Calculate tokens to remove
        target_size = int(self.context.context_size * retention_rate)
        tokens_removed = self.context.context_size - target_size

        # Update context state
        self.context.context_size = target_size
        self.context.tokens_pruned += tokens_removed
        self.context.pruning_operations += 1

        # In real implementation, would remove actual message content
        # Here we just track the statistics

    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get current context statistics.

        Returns:
            Dictionary with context metrics
        """
        return {
            'total_tokens': self.context.total_tokens,
            'context_size': self.context.context_size,
            'pruning_operations': self.context.pruning_operations,
            'tokens_pruned': self.context.tokens_pruned,
            'num_messages': len(self.context.messages),
            'strategy': self.strategy
        }

    def get_generated_code(self) -> str:
        """
        Get all code generated during the conversation.

        Returns:
            Combined generated code
        """
        return "\n\n".join(self.generated_code_parts)


def create_agent(strategy: str = "continuous_pruning", seed: int = 42) -> MockCodingAgent:
    """
    Factory function to create mock agents.

    Args:
        strategy: Context management strategy
        seed: Random seed for determinism

    Returns:
        Configured MockCodingAgent instance
    """
    return MockCodingAgent(strategy=strategy, seed=seed)


def main():
    """Test the mock agent."""
    print("Mock Coding Agent Test")
    print("=" * 60)

    # Test continuous pruning strategy
    print("\n--- Testing Continuous Pruning Strategy ---")
    agent_continuous = MockCodingAgent(strategy="continuous_pruning", seed=42)

    agent_continuous.receive_message("Fix the bug in the authentication module.")
    response1 = agent_continuous.generate_response()
    print(f"Turn 1: Generated {len(response1)} chars")

    agent_continuous.receive_message("Can you add input validation?")
    response2 = agent_continuous.generate_response()
    print(f"Turn 2: Generated {len(response2)} chars")

    stats_continuous = agent_continuous.get_context_stats()
    print(f"\nContinuous Pruning Stats:")
    print(f"  Total tokens: {stats_continuous['total_tokens']}")
    print(f"  Context size: {stats_continuous['context_size']}")
    print(f"  Pruning operations: {stats_continuous['pruning_operations']}")
    print(f"  Tokens pruned: {stats_continuous['tokens_pruned']}")

    # Test discrete baseline strategy
    print("\n--- Testing Discrete Baseline Strategy ---")
    agent_discrete = MockCodingAgent(strategy="discrete_baseline", seed=42)

    agent_discrete.receive_message("Fix the bug in the authentication module.")
    response1 = agent_discrete.generate_response()
    print(f"Turn 1: Generated {len(response1)} chars")

    agent_discrete.receive_message("Can you add input validation?")
    response2 = agent_discrete.generate_response()
    print(f"Turn 2: Generated {len(response2)} chars")

    stats_discrete = agent_discrete.get_context_stats()
    print(f"\nDiscrete Baseline Stats:")
    print(f"  Total tokens: {stats_discrete['total_tokens']}")
    print(f"  Context size: {stats_discrete['context_size']}")
    print(f"  Pruning operations: {stats_discrete['pruning_operations']}")
    print(f"  Tokens pruned: {stats_discrete['tokens_pruned']}")

    # Test code generation
    print("\n--- Testing Code Generation ---")
    agent_code = MockCodingAgent(seed=123)
    agent_code.receive_message("Implement a data processor class.")

    for i in range(5):
        agent_code.generate_response()

    generated_code = agent_code.get_generated_code()
    print(f"Generated {len(generated_code)} characters of code")
    if generated_code:
        print("Sample code snippet:")
        print(generated_code[:200] + "..." if len(generated_code) > 200 else generated_code)

    print("\n✅ Mock agent working correctly!")


if __name__ == "__main__":
    main()
