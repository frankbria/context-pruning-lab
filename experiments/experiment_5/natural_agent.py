"""
Natural Completion Agent

Agent that can declare completion naturally (not fixed turns)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.experiment_4.agent import RealCodingAgent, AgentConfig


class AgentStatus(Enum):
    """Agent status indicators"""
    WORKING = "working"               # Still analyzing/coding
    SOLUTION_READY = "solution_ready"  # Complete solution available
    NEED_INFO = "need_more_info"       # Request additional context
    STUCK = "stuck"                    # Can't proceed without help


@dataclass
class AgentResponse:
    """Structured agent response with status"""
    status: AgentStatus
    content: str                      # Full response text
    confidence: float                  # 0.0 - 1.0
    solution: Optional[str] = None     # Code if status == SOLUTION_READY
    info_request: Optional[str] = None # Details if status == NEED_INFO


class NaturalCompletionAgent(RealCodingAgent):
    """
    Agent that declares completion naturally

    Key features:
    - Declares "SOLUTION READY" when done (no fixed turns)
    - Can request additional context
    - Rates confidence level
    - Natural conversation flow
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize natural completion agent

        Args:
            config: Agent configuration (includes strategy)
        """
        super().__init__(config)
        self._update_system_prompt()

    def _update_system_prompt(self):
        """Update system prompt for natural completion"""
        natural_prompt = """You are an expert coding assistant solving real GitHub issues.

COMPLETION PROTOCOL:
When you have a complete, tested solution ready:
1. Write exactly: "SOLUTION READY"
2. Provide your complete code changes
3. Explain what you fixed/implemented
4. Include any new test cases

CONTEXT REQUESTS:
If you need additional files or information:
1. Write exactly: "I NEED: <file path or description>"
2. Explain why you need it
3. I will provide the requested context

CONFIDENCE:
At the end of each response, rate your confidence:
"CONFIDENCE: <0.0-1.0>"

Examples:
- "CONFIDENCE: 0.95" (very confident)
- "CONFIDENCE: 0.5" (moderate uncertainty)
- "CONFIDENCE: 0.3" (low confidence, may need more info)

IMPORTANT:
- Take as many turns as needed (no rush)
- Don't declare SOLUTION READY until you're confident
- It's okay to request context multiple times
- Test your solution mentally before declaring ready
- Be honest about uncertainty"""

        # Note: In production, we'd modify the agent's system prompt
        # For now, this is a reference implementation
        self.natural_system_prompt = natural_prompt

    def generate_response_with_status(self) -> AgentResponse:
        """
        Generate response and extract status

        Returns:
            AgentResponse with parsed status, confidence, solution
        """
        # Get raw response from Claude
        raw_response = self.generate_response()

        # Extract status indicators
        status = self._extract_status(raw_response)
        confidence = self._extract_confidence(raw_response)

        # Extract solution if ready
        solution = None
        if status == AgentStatus.SOLUTION_READY:
            solution = self._extract_solution(raw_response)

        # Extract info request if needed
        info_request = None
        if status == AgentStatus.NEED_INFO:
            info_request = self._extract_info_request(raw_response)

        return AgentResponse(
            status=status,
            content=raw_response,
            confidence=confidence,
            solution=solution,
            info_request=info_request
        )

    def _extract_status(self, response: str) -> AgentStatus:
        """
        Parse status from response

        Looks for explicit status declarations:
        - "SOLUTION READY"
        - "I NEED:"
        - "I'M STUCK"
        """
        response_upper = response.upper()

        # Check for explicit status declarations
        if "SOLUTION READY" in response_upper:
            return AgentStatus.SOLUTION_READY
        elif "I NEED:" in response_upper or "PLEASE PROVIDE" in response_upper:
            return AgentStatus.NEED_INFO
        elif "I'M STUCK" in response_upper or "CANNOT PROCEED" in response_upper:
            return AgentStatus.STUCK
        else:
            return AgentStatus.WORKING

    def _extract_confidence(self, response: str) -> float:
        """
        Extract confidence rating from response

        Looks for:
        - "CONFIDENCE: 0.85"
        - "CONFIDENCE: 1.0"

        Falls back to keyword-based estimation if not found
        """
        # Look for explicit confidence rating
        match = re.search(r'CONFIDENCE:\s*(0?\.\d+|1\.0|1)', response, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                return max(0.0, min(1.0, value))  # Clamp to [0, 1]
            except ValueError:
                pass

        # Fallback: estimate from keywords
        response_lower = response.lower()

        if any(word in response_lower for word in ["definitely", "certainly", "sure", "confident"]):
            return 0.9
        elif any(word in response_lower for word in ["probably", "likely", "think"]):
            return 0.7
        elif any(word in response_lower for word in ["maybe", "possibly", "might"]):
            return 0.5
        elif any(word in response_lower for word in ["unsure", "uncertain", "don't know"]):
            return 0.3
        else:
            return 0.6  # Default moderate confidence

    def _extract_solution(self, response: str) -> Optional[str]:
        """
        Extract code solution from response

        Looks for code blocks after "SOLUTION READY"
        """
        if "SOLUTION READY" not in response.upper():
            return None

        # Extract all code blocks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)

        if code_blocks:
            # Return concatenated code blocks
            return '\n\n'.join(code_blocks)

        # Fallback: try to find code without markers
        # Look for indented blocks after SOLUTION READY
        solution_idx = response.upper().find("SOLUTION READY")
        after_solution = response[solution_idx:]

        # Look for indented code (4 spaces or tab)
        indented_lines = []
        for line in after_solution.split('\n'):
            if line.startswith('    ') or line.startswith('\t'):
                indented_lines.append(line)
            elif indented_lines and not line.strip():
                # Allow blank lines in code
                indented_lines.append(line)
            elif indented_lines:
                # End of indented block
                break

        if indented_lines:
            return '\n'.join(indented_lines)

        return None

    def _extract_info_request(self, response: str) -> Optional[str]:
        """
        Extract information request from response

        Looks for patterns:
        - "I NEED: <request>"
        - "PLEASE PROVIDE: <request>"
        """
        # Try explicit "I NEED:" pattern
        match = re.search(r'I NEED:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try "PLEASE PROVIDE:" pattern
        match = re.search(r'PLEASE PROVIDE:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try "Could you show me" pattern
        match = re.search(r'COULD YOU (?:SHOW ME|PROVIDE)\s+(.+?)[\.\?]', response, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None


def test_natural_agent():
    """Test natural completion agent"""
    print("Testing NaturalCompletionAgent...")

    # Create config
    config = AgentConfig(
        strategy="continuous_pruning",
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        temperature=0.0
    )

    # Create agent
    agent = NaturalCompletionAgent(config)
    print("✅ Agent created")

    # Test status extraction
    test_responses = [
        ("I'm working on it...", AgentStatus.WORKING),
        ("SOLUTION READY\n```python\ndef fix(): pass```", AgentStatus.SOLUTION_READY),
        ("I NEED: the utils.py file", AgentStatus.NEED_INFO),
        ("I'm stuck on this", AgentStatus.STUCK),
    ]

    for response, expected_status in test_responses:
        status = agent._extract_status(response)
        assert status == expected_status, f"Expected {expected_status}, got {status}"
    print("✅ Status extraction working")

    # Test confidence extraction
    test_confidences = [
        ("CONFIDENCE: 0.95", 0.95),
        ("I'm definitely sure", 0.9),
        ("Maybe this will work", 0.5),
    ]

    for response, expected in test_confidences:
        confidence = agent._extract_confidence(response)
        assert abs(confidence - expected) < 0.15, f"Expected ~{expected}, got {confidence}"
    print("✅ Confidence extraction working")

    # Test solution extraction
    solution_response = """SOLUTION READY

Here's the fix:

```python
def fixed_function(x):
    if x is None:
        return []
    return process(x)
```

This handles the None case."""

    solution = agent._extract_solution(solution_response)
    assert solution is not None, "Should extract solution"
    assert "def fixed_function" in solution, "Solution should contain function"
    print("✅ Solution extraction working")

    # Test info request extraction
    info_response = "I NEED: the database schema file to understand the models"
    info_request = agent._extract_info_request(info_response)
    assert info_request is not None, "Should extract request"
    assert "database schema" in info_request, "Request should match"
    print("✅ Info request extraction working")

    print("\n✅ All natural agent tests passed!")


if __name__ == "__main__":
    test_natural_agent()
