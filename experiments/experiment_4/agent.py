"""
Real Coding Agent with Claude API

Integrates Claude API with continuous pruning and discrete baseline strategies.
Replaces the mock agent from Sprint 3 with real LLM-based agent.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required, can use system env vars

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import pruning components
from pruner import ContinuousPruner

# Import discrete baseline
from baseline import DiscreteCompactionBaseline

# Import Anthropic SDK
try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed")
    print("Install with: pip install anthropic")
    sys.exit(1)


@dataclass
class AgentConfig:
    """Configuration for coding agent."""
    strategy: str  # 'continuous_pruning' or 'discrete_baseline'
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    target_context_size: int = 40_000  # Target context size in tokens
    api_key: Optional[str] = None

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")


class RealCodingAgent:
    """
    Real coding agent using Claude API with context management.

    Implements the same interface as MockCodingAgent for drop-in replacement.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize real coding agent.

        Args:
            config: Agent configuration including strategy and API key
        """
        self.config = config
        self.strategy = config.strategy

        # Initialize Claude client
        self.client = anthropic.Anthropic(api_key=config.api_key)

        # Initialize context management strategy
        if self.strategy == "continuous_pruning":
            self.context_manager = ContinuousPruner(
                target_size=config.target_context_size
            )
        elif self.strategy == "discrete_baseline":
            self.context_manager = DiscreteCompactionBaseline(
                target_size=config.target_context_size
            )
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # Track conversation for API
        self.pending_user_message: Optional[str] = None
        self.generated_code_parts: List[str] = []

        # Statistics
        self.total_tokens_sent = 0
        self.total_tokens_received = 0

    def reset(self):
        """Reset agent for a new task."""
        # Reset context manager
        if self.strategy == "continuous_pruning":
            self.context_manager = ContinuousPruner(
                target_size=self.config.target_context_size
            )
        else:
            self.context_manager = DiscreteCompactionBaseline(
                target_size=self.config.target_context_size
            )

        self.pending_user_message = None
        self.generated_code_parts = []
        self.total_tokens_sent = 0
        self.total_tokens_received = 0

    def receive_message(self, content: str):
        """
        Process a user message.

        Args:
            content: User message content
        """
        # Store message until generate_response is called
        self.pending_user_message = content

    def generate_response(self) -> str:
        """
        Generate agent response to the last user message.

        Returns:
            Generated response content
        """
        if not self.pending_user_message:
            return "Error: No user message to respond to"

        # Build context from context manager
        context_messages = self._build_context_messages()

        # Add current user message
        context_messages.append({
            'role': 'user',
            'content': self.pending_user_message
        })

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=context_messages
            )

            # Extract response text
            response_text = response.content[0].text

            # Track token usage
            self.total_tokens_sent += response.usage.input_tokens
            self.total_tokens_received += response.usage.output_tokens

        except Exception as e:
            # Handle API errors gracefully
            response_text = f"Error generating response: {str(e)}"
            print(f"Claude API error: {e}")

        # Add interaction to context manager
        if self.strategy == "continuous_pruning":
            self.context_manager.add_interaction(
                user_message=self.pending_user_message,
                agent_response=response_text
            )
        else:  # discrete_baseline
            self.context_manager.add_interaction(
                user_msg=self.pending_user_message,
                agent_msg=response_text
            )

        # Clear pending message
        self.pending_user_message = None

        # Extract code if present
        code = self._extract_code_from_response(response_text)
        if code:
            self.generated_code_parts.append(code)

        return response_text

    def _build_context_messages(self) -> List[Dict[str, str]]:
        """
        Build context messages from context manager.

        Returns:
            List of messages in Claude API format
        """
        messages = []

        # Get context items from manager
        for item in self.context_manager.context:
            if item.item_type in ['user_message']:
                messages.append({
                    'role': 'user',
                    'content': item.content
                })
            elif item.item_type in ['agent_response']:
                messages.append({
                    'role': 'assistant',
                    'content': item.content
                })

        # Ensure alternating roles
        messages = self._ensure_alternating_roles(messages)

        return messages

    def _ensure_alternating_roles(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Ensure messages alternate between user and assistant.

        Claude API requires strict alternation. If we have consecutive messages
        from the same role (due to pruning), merge them.

        Args:
            messages: List of messages

        Returns:
            List of messages with alternating roles
        """
        if not messages:
            return messages

        result = []
        current_role = None
        current_content = []

        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role == current_role:
                # Same role, accumulate content
                current_content.append(content)
            else:
                # Different role, flush accumulated content
                if current_content:
                    result.append({
                        'role': current_role,
                        'content': '\n\n'.join(current_content)
                    })
                current_role = role
                current_content = [content]

        # Flush remaining
        if current_content:
            result.append({
                'role': current_role,
                'content': '\n\n'.join(current_content)
            })

        # Ensure we start with user
        if result and result[0]['role'] != 'user':
            result = result[1:]

        # If we end with user (shouldn't happen but handle it)
        if result and result[-1]['role'] == 'user':
            # This is problematic for generating a response
            # But we'll let the API call handle adding the new user message
            pass

        return result

    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """
        Extract code from agent response.

        Looks for code blocks marked with ```python or similar.

        Args:
            response: Agent response text

        Returns:
            Extracted code or None
        """
        import re

        # Match code blocks
        pattern = r'```(?:python|py)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return '\n\n'.join(matches)

        return None

    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get current context statistics.

        Returns:
            Dictionary with context metrics
        """
        if self.strategy == "continuous_pruning":
            return {
                'total_tokens': self.total_tokens_sent + self.total_tokens_received,
                'tokens_sent': self.total_tokens_sent,
                'tokens_received': self.total_tokens_received,
                'context_size': self.context_manager.get_total_tokens(),
                'pruning_operations': self.context_manager.interaction_count,
                'tokens_pruned': self.context_manager.metrics.tokens_removed,
                'num_messages': len(self.context_manager.context),
                'strategy': self.strategy
            }
        else:
            # Discrete baseline stats
            return {
                'total_tokens': self.total_tokens_sent + self.total_tokens_received,
                'tokens_sent': self.total_tokens_sent,
                'tokens_received': self.total_tokens_received,
                'context_size': self.context_manager.current_tokens,
                'pruning_operations': len(self.context_manager.compaction_events),
                'tokens_pruned': sum(e.get('tokens_removed', 0) for e in self.context_manager.compaction_events),
                'num_messages': len(self.context_manager.context),
                'strategy': self.strategy
            }

    def get_generated_code(self) -> str:
        """
        Get all code generated during the conversation.

        Returns:
            Combined generated code
        """
        return '\n\n'.join(self.generated_code_parts)


def create_agent(strategy: str = "continuous_pruning", **kwargs) -> RealCodingAgent:
    """
    Factory function to create real coding agents.

    Args:
        strategy: Context management strategy
        **kwargs: Additional configuration parameters

    Returns:
        Configured RealCodingAgent instance
    """
    config = AgentConfig(strategy=strategy, **kwargs)
    return RealCodingAgent(config)


def main():
    """Test the real coding agent (requires API key)."""
    print("Real Coding Agent Test")
    print("=" * 60)

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n⚠️  ANTHROPIC_API_KEY not set")
        print("To test with real API:")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        print("\nSkipping real API test...")
        return

    print("\n--- Testing Continuous Pruning Agent ---")

    try:
        agent = create_agent(strategy="continuous_pruning")

        # Simple test conversation
        agent.receive_message("Write a Python function to reverse a string.")
        response = agent.generate_response()

        print(f"Agent responded ({len(response)} chars)")
        print(f"First 200 chars: {response[:200]}...")

        # Get stats
        stats = agent.get_context_stats()
        print(f"\nAgent Stats:")
        print(f"  Total tokens: {stats['total_tokens']}")
        print(f"  Context size: {stats['context_size']}")
        print(f"  Messages: {stats['num_messages']}")

        # Get generated code
        code = agent.get_generated_code()
        if code:
            print(f"\nGenerated code ({len(code)} chars):")
            print(code[:200] + "..." if len(code) > 200 else code)

        print("\n✅ Real agent test passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
