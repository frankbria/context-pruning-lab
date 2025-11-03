"""
Conversation Script Generator

Generates multi-turn conversation scripts from SWE-bench tasks to stress-test
context management strategies. Creates realistic back-and-forth interactions
with clarifications, planning, coding, debugging, and refinement phases.
"""

import random
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Handle both module and standalone execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from experiments.swe_bench_extended.types import (
        SWEBenchTask, ConversationTurn, ConversationScript
    )
else:
    from .types import SWEBenchTask, ConversationTurn, ConversationScript


class ConversationScriptGenerator:
    """
    Generate extended multi-turn conversation scripts for coding tasks.

    Converts single-shot coding tasks into realistic multi-turn dialogues
    that include:
    - Initial issue presentation
    - Clarification questions
    - Implementation planning
    - Code generation (iterative)
    - Test execution and debugging
    - Refinement iterations
    - Context "noise" (logs, traces) to stress pruning
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize script generator.

        Args:
            seed: Random seed for reproducibility (default: None)
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        # Conversation phase templates
        self.templates = self._load_templates()

    def generate_script(
        self,
        task: SWEBenchTask,
        target_turns: int = 20,
        include_noise: bool = True
    ) -> ConversationScript:
        """
        Generate a multi-turn conversation script for a task.

        Args:
            task: The coding task to generate conversation for
            target_turns: Target number of turns (will vary slightly)
            include_noise: Whether to include noise items (logs, etc.)

        Returns:
            ConversationScript with multi-turn conversation
        """
        turns = []
        turn_counter = 1

        # Phase 1: Issue Presentation (1 turn)
        turn = self._generate_issue_presentation(task, turn_counter)
        turns.append(turn)
        turn_counter += 1

        # Phase 2: Clarification (2-4 turns)
        clarification_turns = self._generate_clarification_phase(
            task, turn_counter, num_exchanges=random.randint(1, 2)
        )
        turns.extend(clarification_turns)
        turn_counter += len(clarification_turns)

        # Phase 3: Planning (2-4 turns)
        planning_turns = self._generate_planning_phase(
            task, turn_counter, num_exchanges=random.randint(1, 2)
        )
        turns.extend(planning_turns)
        turn_counter += len(planning_turns)

        # Phase 4: Code Generation (4-8 turns)
        coding_turns = self._generate_coding_phase(
            task, turn_counter, num_exchanges=random.randint(2, 4)
        )
        turns.extend(coding_turns)
        turn_counter += len(coding_turns)

        # Phase 5: Testing & Debugging (4-8 turns)
        debug_turns = self._generate_debugging_phase(
            task, turn_counter, num_exchanges=random.randint(2, 4)
        )
        turns.extend(debug_turns)
        turn_counter += len(debug_turns)

        # Phase 6: Refinement (2-4 turns)
        refinement_turns = self._generate_refinement_phase(
            task, turn_counter, num_exchanges=random.randint(1, 2)
        )
        turns.extend(refinement_turns)
        turn_counter += len(refinement_turns)

        # Add noise items if requested
        if include_noise:
            turns = self._inject_noise(turns, task)

        script = ConversationScript(
            task_id=task.task_id,
            turns=turns,
            seed=self.seed or 0,
            template_version="1.0",
            metadata={
                "task_difficulty": task.difficulty.value,
                "task_type": task.task_type.value,
                "num_phases": 6,
                "includes_noise": include_noise
            }
        )

        return script

    def _generate_issue_presentation(
        self, task: SWEBenchTask, turn_number: int
    ) -> ConversationTurn:
        """Generate initial issue presentation turn."""
        content = f"""I need help with an issue in the {task.repo} repository.

{task.issue_description}

Can you help me fix this?"""

        return ConversationTurn(
            turn_number=turn_number,
            role='user',
            content=content,
            turn_type='clarification',
            metadata={'phase': 'issue_presentation'}
        )

    def _generate_clarification_phase(
        self, task: SWEBenchTask, start_turn: int, num_exchanges: int
    ) -> List[ConversationTurn]:
        """Generate clarification question exchanges."""
        turns = []
        turn_num = start_turn

        templates = self.templates['clarification']

        for i in range(num_exchanges):
            # Assistant asks clarifying question
            question_template = random.choice(templates['questions'])
            assistant_content = question_template.format(
                repo=task.repo,
                task_type=task.task_type.value
            )

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='assistant',
                content=assistant_content,
                turn_type='clarification',
                metadata={'phase': 'clarification', 'exchange': i + 1}
            ))
            turn_num += 1

            # User provides answer
            answer_template = random.choice(templates['answers'])
            user_content = answer_template.format(
                repo=task.repo
            )

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='user',
                content=user_content,
                turn_type='clarification',
                metadata={'phase': 'clarification', 'exchange': i + 1}
            ))
            turn_num += 1

        return turns

    def _generate_planning_phase(
        self, task: SWEBenchTask, start_turn: int, num_exchanges: int
    ) -> List[ConversationTurn]:
        """Generate implementation planning exchanges."""
        turns = []
        turn_num = start_turn

        templates = self.templates['planning']

        # Assistant proposes approach
        approach_template = random.choice(templates['approaches'])
        approach_content = approach_template.format(
            repo=task.repo,
            task_type=task.task_type.value
        )

        turns.append(ConversationTurn(
            turn_number=turn_num,
            role='assistant',
            content=approach_content,
            turn_type='planning',
            metadata={'phase': 'planning'}
        ))
        turn_num += 1

        # User feedback on approach
        for i in range(num_exchanges - 1):
            feedback_template = random.choice(templates['feedback'])
            user_content = feedback_template

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='user',
                content=user_content,
                turn_type='planning',
                metadata={'phase': 'planning', 'iteration': i + 1}
            ))
            turn_num += 1

            # Assistant adjusts plan
            adjustment_template = random.choice(templates['adjustments'])
            assistant_content = adjustment_template

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='assistant',
                content=assistant_content,
                turn_type='planning',
                metadata={'phase': 'planning', 'iteration': i + 1}
            ))
            turn_num += 1

        return turns

    def _generate_coding_phase(
        self, task: SWEBenchTask, start_turn: int, num_exchanges: int
    ) -> List[ConversationTurn]:
        """Generate code implementation exchanges."""
        turns = []
        turn_num = start_turn

        templates = self.templates['coding']

        for i in range(num_exchanges):
            # User requests code or next step
            request_template = random.choice(templates['requests'])
            user_content = request_template

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='user',
                content=user_content,
                turn_type='coding',
                metadata={'phase': 'coding', 'iteration': i + 1}
            ))
            turn_num += 1

            # Assistant provides code
            code_template = random.choice(templates['responses'])
            # Add realistic code snippet
            code_snippet = self._generate_code_snippet(task, i + 1)
            assistant_content = code_template.format(code=code_snippet)

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='assistant',
                content=assistant_content,
                turn_type='coding',
                metadata={
                    'phase': 'coding',
                    'iteration': i + 1,
                    'code_length': len(code_snippet)
                }
            ))
            turn_num += 1

        return turns

    def _generate_debugging_phase(
        self, task: SWEBenchTask, start_turn: int, num_exchanges: int
    ) -> List[ConversationTurn]:
        """Generate test execution and debugging exchanges."""
        turns = []
        turn_num = start_turn

        templates = self.templates['debugging']

        for i in range(num_exchanges):
            # User reports test results / error
            error_template = random.choice(templates['errors'])
            # Generate realistic error message
            error_msg = self._generate_error_message(task, i + 1)
            user_content = error_template.format(error=error_msg)

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='user',
                content=user_content,
                turn_type='debugging',
                metadata={'phase': 'debugging', 'iteration': i + 1}
            ))
            turn_num += 1

            # Assistant analyzes and provides fix
            fix_template = random.choice(templates['fixes'])
            fix_code = self._generate_fix_snippet(task, i + 1)
            assistant_content = fix_template.format(fix=fix_code)

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='assistant',
                content=assistant_content,
                turn_type='debugging',
                metadata={'phase': 'debugging', 'iteration': i + 1}
            ))
            turn_num += 1

        return turns

    def _generate_refinement_phase(
        self, task: SWEBenchTask, start_turn: int, num_exchanges: int
    ) -> List[ConversationTurn]:
        """Generate final refinement exchanges."""
        turns = []
        turn_num = start_turn

        templates = self.templates['refinement']

        for i in range(num_exchanges):
            # User requests improvement
            request_template = random.choice(templates['requests'])
            user_content = request_template

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='user',
                content=user_content,
                turn_type='refinement',
                metadata={'phase': 'refinement', 'iteration': i + 1}
            ))
            turn_num += 1

            # Assistant provides refinement
            refinement_template = random.choice(templates['responses'])
            assistant_content = refinement_template

            turns.append(ConversationTurn(
                turn_number=turn_num,
                role='assistant',
                content=assistant_content,
                turn_type='refinement',
                metadata={'phase': 'refinement', 'iteration': i + 1}
            ))
            turn_num += 1

        return turns

    def _inject_noise(
        self, turns: List[ConversationTurn], task: SWEBenchTask
    ) -> List[ConversationTurn]:
        """
        Inject noise items (logs, traces) to stress context management.

        Adds realistic but low-importance content that should be pruned.
        """
        noise_templates = self.templates['noise']

        # Inject noise at 20% of turns (approximately)
        num_noise_items = max(1, len(turns) // 5)

        # Select random positions to inject noise (avoid first/last turns)
        injection_positions = random.sample(
            range(2, len(turns) - 2), min(num_noise_items, len(turns) - 4)
        )

        for pos in sorted(injection_positions, reverse=True):
            # Insert after this position
            noise_type = random.choice(list(noise_templates.keys()))
            noise_content = random.choice(noise_templates[noise_type])

            noise_turn = ConversationTurn(
                turn_number=turns[pos].turn_number + 0.5,  # Between turns
                role='assistant',
                content=noise_content,
                turn_type='noise',
                metadata={'noise_type': noise_type, 'importance': 0.1}
            )

            turns.insert(pos + 1, noise_turn)

        # Renumber turns
        for i, turn in enumerate(turns, start=1):
            turn.turn_number = i

        return turns

    def _generate_code_snippet(self, task: SWEBenchTask, iteration: int) -> str:
        """Generate realistic code snippet for the task."""
        # Simplified code generation - in real implementation,
        # this would use templates based on task type
        code_templates = {
            'bug_fix': '''def fixed_function(input_data):
    """Fixed version with proper error handling"""
    if not input_data:
        return None  # Handle empty input

    # Process data
    result = process(input_data)
    return result''',

            'feature_addition': '''def new_feature(data, **kwargs):
    """New feature implementation"""
    # Parse parameters
    options = {**DEFAULT_OPTIONS, **kwargs}

    # Implement feature logic
    if options.get('enable_validation'):
        validate(data)

    result = execute_feature(data, options)
    return result''',

            'refactoring': '''class RefactoredClass:
    """Improved implementation with better structure"""

    def __init__(self, config):
        self.config = config
        self._cache = {}

    def optimized_method(self, key):
        """Optimized with caching"""
        if key in self._cache:
            return self._cache[key]

        result = self._compute(key)
        self._cache[key] = result
        return result'''
        }

        task_type = task.task_type.value
        return code_templates.get(task_type, code_templates['bug_fix'])

    def _generate_error_message(self, task: SWEBenchTask, iteration: int) -> str:
        """Generate realistic error message."""
        error_templates = [
            "AssertionError: Expected 10, got 8\n  File test_module.py, line 42",
            "TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'\n  File main.py, line 15",
            "AttributeError: 'dict' object has no attribute 'get_value'\n  File utils.py, line 88",
            "ValueError: invalid literal for int() with base 10: 'abc'\n  File parser.py, line 23"
        ]
        return random.choice(error_templates)

    def _generate_fix_snippet(self, task: SWEBenchTask, iteration: int) -> str:
        """Generate realistic fix snippet."""
        fix_templates = [
            "# Add null check\nif value is not None:\n    return value + 1\nreturn 0",
            "# Fix type conversion\ntry:\n    result = int(value)\nexcept ValueError:\n    result = 0",
            "# Use correct method\nreturn data.get('key', default_value)",
            "# Add boundary check\nif index < len(array):\n    return array[index]\nreturn None"
        ]
        return random.choice(fix_templates)

    def _load_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load conversation templates for different phases."""
        return {
            'clarification': {
                'questions': [
                    "To better understand the issue: Are there any specific edge cases or inputs that trigger this behavior?",
                    "Could you provide more context about how this function is typically called? What are the expected inputs?",
                    "Is this issue consistent or intermittent? Have you noticed any patterns?",
                    "What version of the codebase are you using? Has this worked correctly in previous versions?"
                ],
                'answers': [
                    "It happens with empty strings and null values. The function should handle these gracefully.",
                    "This is called from multiple places in the codebase, usually with user input that hasn't been validated.",
                    "It's consistent - happens every time with the specific input pattern I mentioned.",
                    "We're on the latest version. This is a new issue that appeared recently."
                ]
            },
            'planning': {
                'approaches': [
                    "I'll approach this by:\n1. Adding input validation\n2. Implementing proper error handling\n3. Adding comprehensive tests\n\nDoes this sound reasonable?",
                    "My plan:\n1. Refactor the problematic function\n2. Extract reusable logic\n3. Add edge case handling\n\nShould I proceed with this approach?",
                    "I propose:\n1. Fix the immediate bug\n2. Add defensive programming checks\n3. Update documentation\n\nLet me know if you'd like me to focus on any particular aspect."
                ],
                'feedback': [
                    "That sounds good, but could you also add logging for debugging purposes?",
                    "Yes, proceed. Also make sure to maintain backward compatibility.",
                    "Good approach. Please also add docstrings explaining the expected behavior.",
                    "Perfect. One more thing - can you ensure the fix doesn't impact performance?"
                ],
                'adjustments': [
                    "Absolutely, I'll add comprehensive logging at key points.",
                    "Will do. I'll make sure all existing tests pass and behavior is preserved.",
                    "Yes, I'll add detailed docstrings with examples.",
                    "Good point. I'll benchmark the changes to ensure no performance regression."
                ]
            },
            'coding': {
                'requests': [
                    "Let's start with the core implementation.",
                    "Please show me the code for the main function.",
                    "Can you implement the validation logic now?",
                    "What would the updated code look like?"
                ],
                'responses': [
                    "Here's the implementation:\n\n```python\n{code}\n```\n\nThis handles the main logic with proper error checking.",
                    "Here's the updated code:\n\n```python\n{code}\n```\n\nI've added comprehensive validation.",
                    "Here's the refactored version:\n\n```python\n{code}\n```\n\nThis is more maintainable and handles edge cases.",
                    "Implementation:\n\n```python\n{code}\n```\n\nThis follows best practices and includes proper error handling."
                ]
            },
            'debugging': {
                'errors': [
                    "I'm getting this error when running the tests:\n\n```\n{error}\n```",
                    "The tests are failing with:\n\n```\n{error}\n```\n\nWhat's causing this?",
                    "After implementing your changes, I see:\n\n```\n{error}\n```",
                    "Test output:\n\n```\n{error}\n```\n\nHow should we fix this?"
                ],
                'fixes': [
                    "The issue is a type mismatch. Here's the fix:\n\n```python\n{fix}\n```",
                    "We need to handle the None case:\n\n```python\n{fix}\n```",
                    "The problem is missing validation. Add this:\n\n```python\n{fix}\n```",
                    "Fix the boundary condition:\n\n```python\n{fix}\n```"
                ]
            },
            'refinement': {
                'requests': [
                    "Can you add more comments explaining the logic?",
                    "Could we make this more efficient?",
                    "Please add type hints for better code quality.",
                    "Can you refactor this to be more readable?"
                ],
                'responses': [
                    "Sure, I've added detailed comments explaining each step.",
                    "Good idea. I've optimized the algorithm to use O(n) instead of O(n²).",
                    "Added comprehensive type hints throughout the code.",
                    "Refactored into smaller, more focused functions for better readability."
                ]
            },
            'noise': {
                'logs': [
                    "[DEBUG] Processing batch 1/10...\n[DEBUG] Cache hit rate: 85%\n[DEBUG] Memory usage: 234MB",
                    "[INFO] Connection established to database\n[INFO] Query executed in 45ms\n[INFO] Returned 127 rows",
                    "[TRACE] Entering function validate_input\n[TRACE] Input size: 1024 bytes\n[TRACE] Validation passed"
                ],
                'system_info': [
                    "System: Python 3.9.7, Linux x86_64\nCPU: 8 cores @ 2.4GHz\nMemory: 16GB",
                    "Environment: Development\nDatabase: PostgreSQL 13.4\nCache: Redis 6.2",
                    "Build: #1234\nCommit: abc123def456\nBranch: feature/improvements"
                ],
                'metrics': [
                    "Performance metrics:\n- Response time: 120ms\n- Throughput: 850 req/s\n- Error rate: 0.02%",
                    "Resource usage:\n- CPU: 45%\n- Memory: 62%\n- Disk I/O: 12MB/s",
                    "Test coverage:\n- Lines: 87%\n- Branches: 92%\n- Functions: 95%"
                ]
            }
        }


def main():
    """Test script generation with a sample task."""
    # Need to load a task first
    import json

    tasks_file = Path("data/swe_bench_tasks.json")
    if not tasks_file.exists():
        print("Error: Tasks file not found. Run task_selector.py first.")
        return

    with open(tasks_file) as f:
        tasks_data = json.load(f)

    if not tasks_data:
        print("No tasks found!")
        return

    # Load first task
    from experiments.swe_bench_extended.types import TaskDifficulty, TaskType
    task_data = tasks_data[0]
    task = SWEBenchTask(
        task_id=task_data["task_id"],
        instance_id=task_data["instance_id"],
        repo=task_data["repo"],
        issue_description=task_data["issue_description"],
        test_suite=task_data["test_suite"],
        base_commit=task_data["base_commit"],
        patch=task_data.get("patch"),
        difficulty=TaskDifficulty(task_data["difficulty"]),
        task_type=TaskType(task_data["task_type"]),
        metadata=task_data.get("metadata", {})
    )

    print(f"Generating conversation script for task: {task.task_id}")
    print(f"Task type: {task.task_type.value}, Difficulty: {task.difficulty.value}")

    generator = ConversationScriptGenerator(seed=42)
    script = generator.generate_script(task, target_turns=20, include_noise=True)

    print(f"\nGenerated conversation with {script.num_turns} turns")
    print(f"User turns: {len(script.user_turns)}")
    print(f"Assistant turns: {len(script.assistant_turns)}")

    print("\nFirst 5 turns:")
    for turn in script.turns[:5]:
        print(f"\n--- Turn {turn.turn_number} ({turn.role}, {turn.turn_type}) ---")
        print(turn.content[:200] + ("..." if len(turn.content) > 200 else ""))

    # Save script
    output_dir = Path("data/conversation_scripts")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"{task.task_id}_conversation.json"

    script_data = {
        "task_id": script.task_id,
        "seed": script.seed,
        "template_version": script.template_version,
        "metadata": script.metadata,
        "num_turns": script.num_turns,
        "turns": [
            {
                "turn_number": t.turn_number,
                "role": t.role,
                "content": t.content,
                "turn_type": t.turn_type,
                "metadata": t.metadata
            }
            for t in script.turns
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(script_data, f, indent=2)

    print(f"\nSaved conversation script to {output_file}")


if __name__ == "__main__":
    main()
