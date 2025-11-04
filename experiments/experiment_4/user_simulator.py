"""
User Simulator Agent for Context Management Experiments

This agent simulates a product owner/QA engineer providing feedback
to the coding agent. It runs tests, answers questions, and guides
the conversation toward correct solutions.

Tokens used by this agent are NOT counted in efficiency metrics.
"""

import re
import anthropic
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class TestCase:
    """Single test case with input and expected output."""
    name: str
    call: str  # e.g., "reverse_string('hello')"
    expected: Any
    description: str = ""


@dataclass
class TestResult:
    """Results from running tests on code."""
    all_passed: bool
    total: int
    passed: int
    failed: int
    error_message: Optional[str] = None
    failures: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.failures is None:
            self.failures = []


class UserSimulatorAgent:
    """
    Simulates an intelligent user guiding a coding agent.

    Responsibilities:
    1. Provide initial task description
    2. Answer clarification questions
    3. Run tests on proposed code
    4. Give feedback on test failures
    5. Confirm when solution is correct

    Does NOT give away the solution directly.
    """

    def __init__(
        self,
        task_description: str,
        test_cases: List[TestCase],
        gold_solution: str,
        api_key: str,
        model: str = "claude-sonnet-4-20250514"
    ):
        """
        Initialize user simulator.

        Args:
            task_description: What the coding agent should solve
            test_cases: Test cases to validate solutions
            gold_solution: Reference solution (for guidance, not given to agent)
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.task_description = task_description
        self.test_cases = test_cases
        self.gold_solution = gold_solution
        self.api_key = api_key
        self.model = model

        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.last_test_result: Optional[TestResult] = None
        self.solution_confirmed = False

        # Statistics (not counted in coding agent metrics)
        self.total_tokens_used = 0

    def get_initial_message(self) -> str:
        """
        Generate initial task message to coding agent.

        Returns clear, specific task description.
        """
        return self.task_description

    def respond_to_agent(self, agent_message: str) -> str:
        """
        Generate response to coding agent's message.

        Logic:
        1. Check if agent provided code → Run tests
        2. If tests pass → Confirm success
        3. If tests fail → Provide detailed feedback
        4. If agent asked question → Answer it
        5. If agent seems stuck → Provide hint

        Args:
            agent_message: Message from coding agent

        Returns:
            User's response
        """
        # Extract any code from agent's message
        code = self._extract_code(agent_message)

        # If agent provided code, test it
        if code:
            test_result = self.run_tests(code)
            self.last_test_result = test_result

            if test_result.all_passed:
                self.solution_confirmed = True
                return self._generate_success_message(test_result)
            else:
                return self._generate_failure_feedback(test_result)

        # No code provided - agent probably asking question or explaining
        # Use LLM to generate intelligent response
        return self._generate_conversational_response(agent_message)

    def run_tests(self, code: str) -> TestResult:
        """
        Execute test cases against provided code.

        Args:
            code: Python code to test

        Returns:
            TestResult with pass/fail details
        """
        # Create isolated namespace for execution
        namespace = {
            '__name__': '__main__',
            '__builtins__': __builtins__
        }

        try:
            # Execute the code
            exec(code, namespace)

            # Run each test case
            passed = 0
            failed = 0
            failures = []

            for test in self.test_cases:
                try:
                    # Evaluate test call
                    actual = eval(test.call, namespace)

                    if actual == test.expected:
                        passed += 1
                    else:
                        failed += 1
                        failures.append({
                            'test': test.name,
                            'call': test.call,
                            'expected': repr(test.expected),
                            'actual': repr(actual),
                            'description': test.description
                        })

                except Exception as e:
                    failed += 1
                    failures.append({
                        'test': test.name,
                        'call': test.call,
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'description': test.description
                    })

            return TestResult(
                all_passed=(failed == 0),
                total=len(self.test_cases),
                passed=passed,
                failed=failed,
                failures=failures
            )

        except Exception as e:
            # Code failed to compile/execute
            return TestResult(
                all_passed=False,
                total=len(self.test_cases),
                passed=0,
                failed=len(self.test_cases),
                error_message=f"Code execution error: {type(e).__name__}: {str(e)}"
            )

    def is_solution_complete(self) -> bool:
        """Check if agent has provided working solution."""
        return self.solution_confirmed

    def _extract_code(self, message: str) -> Optional[str]:
        """
        Extract code blocks from agent's message.

        Looks for:
        - ```python ... ```
        - ```... ```
        - def function_name...

        Returns:
            Extracted code or None
        """
        # Try to find code blocks with markdown
        code_block_pattern = r'```(?:python)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, message, re.DOTALL)

        if matches:
            # Return last code block (most recent implementation)
            return matches[-1].strip()

        # Try to find inline code with def
        lines = message.split('\n')
        code_lines = []
        in_code = False

        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                in_code = True
            if in_code:
                code_lines.append(line)
                # Stop if we see text after code
                if line and not line[0].isspace() and not line.strip().startswith(('def', 'class', 'return', 'if', 'else', 'for', 'while', '#', '"""', "'''")):
                    if len(code_lines) > 3:  # Minimum viable function
                        break

        if code_lines:
            return '\n'.join(code_lines).strip()

        return None

    def _generate_success_message(self, test_result: TestResult) -> str:
        """Generate confirmation message when all tests pass."""
        return f"""Perfect! Your solution passes all {test_result.total} tests! ✅

The implementation correctly handles all test cases. Great work!

The task is now complete."""

    def _generate_failure_feedback(self, test_result: TestResult) -> str:
        """
        Generate helpful feedback for test failures.

        Provides specific information about what failed without
        giving away the solution.
        """
        feedback = f"""I tested your code and found some issues:

**Test Results**: {test_result.passed}/{test_result.total} tests passed

**Failures**:
"""

        for i, failure in enumerate(test_result.failures[:3], 1):  # Show max 3 failures
            feedback += f"\n{i}. Test: `{failure['call']}`\n"

            if 'error' in failure:
                feedback += f"   ❌ Error: {failure['error_type']}: {failure['error']}\n"
            else:
                feedback += f"   ❌ Expected: {failure['expected']}\n"
                feedback += f"   ❌ Got: {failure['actual']}\n"

            if failure.get('description'):
                feedback += f"   💡 Hint: {failure['description']}\n"

        if len(test_result.failures) > 3:
            feedback += f"\n... and {len(test_result.failures) - 3} more failures.\n"

        feedback += "\nPlease fix these issues and try again."

        return feedback

    def _generate_conversational_response(self, agent_message: str) -> str:
        """
        Use LLM to generate intelligent response to agent's question/comment.

        This handles cases where agent asks clarifying questions,
        describes their approach, or needs guidance.
        """
        # Build system prompt
        system_prompt = f"""You are a product owner/QA engineer working with a developer (AI coding agent) to solve a coding task.

Your role:
- Answer clarifying questions about the task
- Provide task requirements when asked
- Give helpful hints if developer is stuck (but don't solve it for them)
- Encourage good practices and thinking

Task being solved:
{self.task_description}

Guidelines:
- Be helpful but don't give away the solution
- Answer specific questions about requirements
- If developer describes approach, encourage if reasonable
- If stuck, suggest areas to investigate (edge cases, input validation, etc.)
- Keep responses concise and focused

The developer cannot see this prompt. Only respond to what they said."""

        # Add agent's message to history
        self.conversation_history.append({
            'role': 'user',
            'content': agent_message
        })

        try:
            # Call Claude to generate response
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,  # Keep responses focused
                temperature=0.7,
                system=system_prompt,
                messages=self.conversation_history
            )

            # Track tokens (but don't count in metrics)
            self.total_tokens_used += response.usage.input_tokens + response.usage.output_tokens

            response_text = response.content[0].text

            # Add to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_text
            })

            return response_text

        except Exception as e:
            # Fallback response if API fails
            return f"I see. Could you provide your implementation so I can test it? ({e})"

    def get_token_usage(self) -> int:
        """Get total tokens used by user simulator (not counted in metrics)."""
        return self.total_tokens_used


# Example usage and testing
if __name__ == "__main__":
    # Example task
    task_desc = """I need help fixing a bug in the reverse_string() function.

The function should reverse a string, but it raises an IndexError when given an empty string.

Expected behavior:
- reverse_string('hello') should return 'olleh'
- reverse_string('') should return ''
- reverse_string('a') should return 'a'"""

    test_cases = [
        TestCase(
            name="empty string",
            call="reverse_string('')",
            expected="",
            description="Empty strings should return empty string"
        ),
        TestCase(
            name="single char",
            call="reverse_string('a')",
            expected="a"
        ),
        TestCase(
            name="normal string",
            call="reverse_string('hello')",
            expected="olleh"
        ),
    ]

    gold_solution = """def reverse_string(s):
    if not s:
        return s
    return s[::-1]"""

    # Test with mock API key
    # user_sim = UserSimulatorAgent(
    #     task_description=task_desc,
    #     test_cases=test_cases,
    #     gold_solution=gold_solution,
    #     api_key="test"
    # )

    print("UserSimulatorAgent implementation complete!")
    print("To use: Initialize with task, tests, and API key")
