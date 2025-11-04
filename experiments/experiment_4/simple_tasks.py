"""
Simple coding tasks for two-agent system testing.

These tasks have explicit test cases that can be executed directly,
making them compatible with the UserSimulatorAgent test execution.
"""

from dataclasses import dataclass
from typing import List
from experiments.experiment_4.user_simulator import TestCase


@dataclass
class SimpleTask:
    """A simple coding task with executable test cases."""
    task_id: str
    description: str
    test_cases: List[TestCase]
    gold_solution: str
    difficulty: str = "easy"


# Task definitions
SIMPLE_TASKS = [
    SimpleTask(
        task_id="reverse_string",
        description="""I need a function called `reverse_string` that reverses a string.

Requirements:
- Function name must be `reverse_string`
- Takes one parameter: a string
- Returns the reversed string
- Must handle empty strings correctly

Examples:
- reverse_string('hello') → 'olleh'
- reverse_string('') → ''
- reverse_string('a') → 'a'""",
        test_cases=[
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
        ],
        gold_solution="def reverse_string(s):\n    return s[::-1]",
        difficulty="easy"
    ),

    SimpleTask(
        task_id="is_palindrome",
        description="""I need a function called `is_palindrome` that checks if a string is a palindrome.

Requirements:
- Function name must be `is_palindrome`
- Takes one parameter: a string
- Returns True if the string reads the same forwards and backwards, False otherwise
- Should be case-insensitive
- Ignore spaces and punctuation

Examples:
- is_palindrome('racecar') → True
- is_palindrome('hello') → False
- is_palindrome('A man a plan a canal Panama') → True""",
        test_cases=[
            TestCase(
                name="simple palindrome",
                call="is_palindrome('racecar')",
                expected=True,
                description="Simple palindrome should return True"
            ),
            TestCase(
                name="not palindrome",
                call="is_palindrome('hello')",
                expected=False,
                description="Non-palindrome should return False"
            ),
            TestCase(
                name="case insensitive",
                call="is_palindrome('RaceCar')",
                expected=True,
                description="Should ignore case"
            ),
            TestCase(
                name="with spaces",
                call="is_palindrome('race car')",
                expected=True,
                description="Should ignore spaces"
            ),
        ],
        gold_solution="""def is_palindrome(s):
    # Remove spaces and convert to lowercase
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]""",
        difficulty="easy"
    ),

    SimpleTask(
        task_id="count_vowels",
        description="""I need a function called `count_vowels` that counts vowels in a string.

Requirements:
- Function name must be `count_vowels`
- Takes one parameter: a string
- Returns the count of vowels (a, e, i, o, u)
- Should be case-insensitive

Examples:
- count_vowels('hello') → 2
- count_vowels('AEIOU') → 5
- count_vowels('xyz') → 0""",
        test_cases=[
            TestCase(
                name="mixed string",
                call="count_vowels('hello')",
                expected=2,
                description="Should count e and o"
            ),
            TestCase(
                name="all vowels",
                call="count_vowels('AEIOU')",
                expected=5,
                description="Should count all vowels case-insensitively"
            ),
            TestCase(
                name="no vowels",
                call="count_vowels('xyz')",
                expected=0,
                description="Should return 0 for no vowels"
            ),
            TestCase(
                name="empty string",
                call="count_vowels('')",
                expected=0,
                description="Empty string should return 0"
            ),
        ],
        gold_solution="""def count_vowels(s):
    vowels = 'aeiouAEIOU'
    return sum(1 for c in s if c in vowels)""",
        difficulty="easy"
    ),

    SimpleTask(
        task_id="fibonacci",
        description="""I need a function called `fibonacci` that returns the nth Fibonacci number.

Requirements:
- Function name must be `fibonacci`
- Takes one parameter: n (non-negative integer)
- Returns the nth Fibonacci number (0-indexed)
- fibonacci(0) = 0, fibonacci(1) = 1
- For n >= 2: fibonacci(n) = fibonacci(n-1) + fibonacci(n-2)

Examples:
- fibonacci(0) → 0
- fibonacci(1) → 1
- fibonacci(5) → 5
- fibonacci(10) → 55""",
        test_cases=[
            TestCase(
                name="base case 0",
                call="fibonacci(0)",
                expected=0,
                description="fibonacci(0) should be 0"
            ),
            TestCase(
                name="base case 1",
                call="fibonacci(1)",
                expected=1,
                description="fibonacci(1) should be 1"
            ),
            TestCase(
                name="fibonacci 5",
                call="fibonacci(5)",
                expected=5,
                description="fibonacci(5) should be 5"
            ),
            TestCase(
                name="fibonacci 10",
                call="fibonacci(10)",
                expected=55,
                description="fibonacci(10) should be 55"
            ),
        ],
        gold_solution="""def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b""",
        difficulty="medium"
    ),

    SimpleTask(
        task_id="merge_sorted_lists",
        description="""I need a function called `merge_sorted_lists` that merges two sorted lists into one sorted list.

Requirements:
- Function name must be `merge_sorted_lists`
- Takes two parameters: two sorted lists of integers
- Returns a new sorted list containing all elements from both input lists
- Should maintain O(n+m) time complexity

Examples:
- merge_sorted_lists([1, 3, 5], [2, 4, 6]) → [1, 2, 3, 4, 5, 6]
- merge_sorted_lists([], [1, 2]) → [1, 2]
- merge_sorted_lists([1], []) → [1]""",
        test_cases=[
            TestCase(
                name="normal merge",
                call="merge_sorted_lists([1, 3, 5], [2, 4, 6])",
                expected=[1, 2, 3, 4, 5, 6],
                description="Should merge two sorted lists"
            ),
            TestCase(
                name="empty first list",
                call="merge_sorted_lists([], [1, 2, 3])",
                expected=[1, 2, 3],
                description="Should handle empty first list"
            ),
            TestCase(
                name="empty second list",
                call="merge_sorted_lists([1, 2, 3], [])",
                expected=[1, 2, 3],
                description="Should handle empty second list"
            ),
            TestCase(
                name="both empty",
                call="merge_sorted_lists([], [])",
                expected=[],
                description="Should handle both empty lists"
            ),
        ],
        gold_solution="""def merge_sorted_lists(list1, list2):
    result = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    result.extend(list1[i:])
    result.extend(list2[j:])
    return result""",
        difficulty="medium"
    ),
]


def get_task(task_id: str) -> SimpleTask:
    """Get a task by ID."""
    for task in SIMPLE_TASKS:
        if task.task_id == task_id:
            return task
    raise ValueError(f"Task not found: {task_id}")


def get_all_tasks() -> List[SimpleTask]:
    """Get all available tasks."""
    return SIMPLE_TASKS


def get_tasks_by_difficulty(difficulty: str) -> List[SimpleTask]:
    """Get tasks filtered by difficulty."""
    return [t for t in SIMPLE_TASKS if t.difficulty == difficulty]
