"""
Conversation Orchestrator for Two-Agent Experiments

Manages dialogue between UserSimulatorAgent and RealCodingAgent,
tracking tokens separately to measure only the coding agent's efficiency.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from experiments.experiment_4.user_simulator import UserSimulatorAgent
from experiments.experiment_4.agent import RealCodingAgent


@dataclass
class ConversationTurn:
    """Record of a single turn in the conversation."""
    turn_number: int
    role: str  # 'user_sim' or 'coding_agent'
    content: str
    tokens_input: int = 0
    tokens_output: int = 0
    phase: str = ""  # 'clarification', 'coding', 'testing', 'refinement'


@dataclass
class ConversationResult:
    """Complete results from a two-agent conversation."""
    success: bool
    total_turns: int
    solution_code: Optional[str]
    test_results: Optional[Dict[str, Any]]

    # Token metrics (ONLY coding agent counted in efficiency)
    coding_agent_tokens: int
    user_sim_tokens: int  # Tracked but not compared

    # Detailed history
    conversation_history: List[ConversationTurn] = field(default_factory=list)

    # Timing
    execution_time: float = 0.0

    # Error tracking
    error_message: Optional[str] = None


class ConversationOrchestrator:
    """
    Orchestrates conversation between user simulator and coding agent.

    Key responsibilities:
    1. Initialize both agents with appropriate context
    2. Manage turn-by-turn dialogue
    3. Extract and test code from agent responses
    4. Track tokens separately for each agent
    5. Determine when task is complete
    6. Return results with proper metrics
    """

    def __init__(
        self,
        user_simulator: UserSimulatorAgent,
        coding_agent: RealCodingAgent,
        max_turns: int = 50,
        verbose: bool = True
    ):
        """
        Initialize orchestrator.

        Args:
            user_simulator: User simulator agent (not counted in metrics)
            coding_agent: Coding agent (counted in metrics)
            max_turns: Maximum conversation turns
            verbose: Print progress updates
        """
        self.user_sim = user_simulator
        self.coding_agent = coding_agent
        self.max_turns = max_turns
        self.verbose = verbose

        self.conversation_history: List[ConversationTurn] = []
        self.start_time: Optional[datetime] = None

    def run_conversation(self) -> ConversationResult:
        """
        Execute full conversation until solution found or max turns.

        Flow:
        1. User sim provides initial task
        2. Loop:
           a. Coding agent responds
           b. Check for code in response
           c. User sim responds (tests code if present)
           d. Check if complete
           e. Continue to next turn
        3. Return results

        Returns:
            ConversationResult with metrics and history
        """
        self.start_time = datetime.now()

        try:
            # Initial task message from user simulator
            initial_message = self.user_sim.get_initial_message()

            self._log_turn(
                turn_number=1,
                role='user_sim',
                content=initial_message,
                phase='initial'
            )

            # Send to coding agent
            self.coding_agent.receive_message(initial_message)

            # Main conversation loop
            for turn in range(2, self.max_turns + 1):
                if self.verbose and turn % 5 == 0:
                    print(f"  Turn {turn}/{self.max_turns}...")

                # Coding agent's turn
                agent_response = self.coding_agent.generate_response()

                self._log_turn(
                    turn_number=turn,
                    role='coding_agent',
                    content=agent_response,
                    tokens_input=self.coding_agent.total_tokens_sent,
                    tokens_output=self.coding_agent.total_tokens_received,
                    phase=self._determine_phase(agent_response)
                )

                # User simulator responds (may run tests)
                user_response = self.user_sim.respond_to_agent(agent_response)

                self._log_turn(
                    turn_number=turn + 1,
                    role='user_sim',
                    content=user_response,
                    tokens_input=0,  # Not tracked for user sim
                    tokens_output=0,
                    phase='feedback'
                )

                # Check if task complete
                if self.user_sim.is_solution_complete():
                    if self.verbose:
                        print(f"  ✅ Solution confirmed at turn {turn}")
                    break

                # Continue conversation
                self.coding_agent.receive_message(user_response)

                # Safety: Check if stuck in loop
                if turn > 10 and self._is_stuck():
                    if self.verbose:
                        print(f"  ⚠️ Conversation appears stuck, terminating")
                    break

            # Get final code (last code agent produced)
            final_code = self._extract_final_code()

            # Build result
            result = ConversationResult(
                success=self.user_sim.is_solution_complete(),
                total_turns=len(self.conversation_history),
                solution_code=final_code,
                test_results=self._get_test_results(),
                coding_agent_tokens=self.coding_agent.total_tokens_sent +
                                   self.coding_agent.total_tokens_received,
                user_sim_tokens=self.user_sim.get_token_usage(),
                conversation_history=self.conversation_history,
                execution_time=(datetime.now() - self.start_time).total_seconds()
            )

            return result

        except Exception as e:
            # Handle errors gracefully
            if self.verbose:
                print(f"  ❌ Error in conversation: {e}")

            return ConversationResult(
                success=False,
                total_turns=len(self.conversation_history),
                solution_code=None,
                test_results=None,
                coding_agent_tokens=self.coding_agent.total_tokens_sent +
                                   self.coding_agent.total_tokens_received,
                user_sim_tokens=self.user_sim.get_token_usage(),
                conversation_history=self.conversation_history,
                execution_time=(datetime.now() - self.start_time).total_seconds()
                              if self.start_time else 0.0,
                error_message=str(e)
            )

    def _log_turn(
        self,
        turn_number: int,
        role: str,
        content: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        phase: str = ""
    ):
        """Record a conversation turn."""
        turn = ConversationTurn(
            turn_number=turn_number,
            role=role,
            content=content,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            phase=phase
        )
        self.conversation_history.append(turn)

    def _determine_phase(self, message: str) -> str:
        """
        Determine conversation phase from message content.

        Phases:
        - 'clarification': Asking questions
        - 'coding': Providing code solution
        - 'explanation': Explaining approach
        - 'testing': Discussing test results
        """
        message_lower = message.lower()

        if '```' in message or 'def ' in message:
            return 'coding'
        elif '?' in message[-100:]:  # Question at end
            return 'clarification'
        elif 'test' in message_lower or 'result' in message_lower:
            return 'testing'
        else:
            return 'explanation'

    def _extract_final_code(self) -> Optional[str]:
        """
        Extract the last code snippet produced by coding agent.

        Returns:
            Last code from agent or None
        """
        # Look through history in reverse for coding agent's code
        for turn in reversed(self.conversation_history):
            if turn.role == 'coding_agent':
                code = self.user_sim._extract_code(turn.content)
                if code:
                    return code
        return None

    def _get_test_results(self) -> Optional[Dict[str, Any]]:
        """
        Get final test results from user simulator.

        Returns:
            Test result dict or None
        """
        if self.user_sim.last_test_result:
            result = self.user_sim.last_test_result
            return {
                'all_passed': result.all_passed,
                'total': result.total,
                'passed': result.passed,
                'failed': result.failed,
                'failures': result.failures
            }
        return None

    def _is_stuck(self) -> bool:
        """
        Detect if conversation is stuck in a loop.

        Heuristics:
        - Same question repeated 3+ times
        - No progress in last 5 turns
        - User sim keeps saying same thing

        Returns:
            True if stuck, False otherwise
        """
        if len(self.conversation_history) < 10:
            return False

        # Check last 6 user_sim messages for repetition
        user_sim_messages = [
            turn.content[:200]  # First 200 chars
            for turn in self.conversation_history[-12:]
            if turn.role == 'user_sim'
        ]

        if len(user_sim_messages) >= 3:
            # If last 3 messages are very similar, likely stuck
            if len(set(user_sim_messages[-3:])) == 1:
                return True

        return False


# Example usage
if __name__ == "__main__":
    print("ConversationOrchestrator implementation complete!")
    print("To use:")
    print("  1. Create UserSimulatorAgent with task")
    print("  2. Create RealCodingAgent with strategy")
    print("  3. Create ConversationOrchestrator")
    print("  4. Call orchestrator.run_conversation()")
    print("  5. Analyze results (coding_agent_tokens is what we measure!)")
