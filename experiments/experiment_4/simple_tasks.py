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
    # EASY TASKS (10 total)
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

    # ADDITIONAL EASY TASKS (6-10)
    SimpleTask(
        task_id="find_max",
        description="""I need a function called `find_max` that finds the maximum element in a list.

Requirements:
- Function name must be `find_max`
- Takes one parameter: a list of numbers
- Returns the maximum value
- Must handle single-element lists

Examples:
- find_max([1, 5, 3, 9, 2]) → 9
- find_max([42]) → 42
- find_max([-5, -2, -10]) → -2""",
        test_cases=[
            TestCase(
                name="normal list",
                call="find_max([1, 5, 3, 9, 2])",
                expected=9,
                description="Should find maximum in list"
            ),
            TestCase(
                name="single element",
                call="find_max([42])",
                expected=42,
                description="Should return single element"
            ),
            TestCase(
                name="negative numbers",
                call="find_max([-5, -2, -10])",
                expected=-2,
                description="Should handle negative numbers"
            ),
            TestCase(
                name="duplicates",
                call="find_max([5, 5, 5])",
                expected=5,
                description="Should handle duplicates"
            ),
        ],
        gold_solution="def find_max(lst):\n    return max(lst)",
        difficulty="easy"
    ),

    SimpleTask(
        task_id="sum_list",
        description="""I need a function called `sum_list` that sums all elements in a list.

Requirements:
- Function name must be `sum_list`
- Takes one parameter: a list of numbers
- Returns the sum of all elements
- Must handle empty lists (return 0)

Examples:
- sum_list([1, 2, 3, 4]) → 10
- sum_list([]) → 0
- sum_list([-1, 1]) → 0""",
        test_cases=[
            TestCase(
                name="normal list",
                call="sum_list([1, 2, 3, 4])",
                expected=10,
                description="Should sum all elements"
            ),
            TestCase(
                name="empty list",
                call="sum_list([])",
                expected=0,
                description="Should return 0 for empty list"
            ),
            TestCase(
                name="negative and positive",
                call="sum_list([-1, 1])",
                expected=0,
                description="Should handle negative numbers"
            ),
            TestCase(
                name="single element",
                call="sum_list([42])",
                expected=42,
                description="Should handle single element"
            ),
        ],
        gold_solution="def sum_list(lst):\n    return sum(lst)",
        difficulty="easy"
    ),

    SimpleTask(
        task_id="remove_duplicates",
        description="""I need a function called `remove_duplicates` that removes duplicate elements from a list while preserving order.

Requirements:
- Function name must be `remove_duplicates`
- Takes one parameter: a list
- Returns a new list with duplicates removed
- Must preserve original order of first occurrences

Examples:
- remove_duplicates([1, 2, 2, 3, 1]) → [1, 2, 3]
- remove_duplicates([]) → []
- remove_duplicates([1, 1, 1]) → [1]""",
        test_cases=[
            TestCase(
                name="normal list with duplicates",
                call="remove_duplicates([1, 2, 2, 3, 1])",
                expected=[1, 2, 3],
                description="Should remove duplicates while preserving order"
            ),
            TestCase(
                name="empty list",
                call="remove_duplicates([])",
                expected=[],
                description="Should handle empty list"
            ),
            TestCase(
                name="all duplicates",
                call="remove_duplicates([1, 1, 1])",
                expected=[1],
                description="Should handle all same elements"
            ),
            TestCase(
                name="no duplicates",
                call="remove_duplicates([1, 2, 3])",
                expected=[1, 2, 3],
                description="Should handle list without duplicates"
            ),
        ],
        gold_solution="""def remove_duplicates(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result""",
        difficulty="easy"
    ),

    SimpleTask(
        task_id="capitalize_words",
        description="""I need a function called `capitalize_words` that capitalizes the first letter of each word.

Requirements:
- Function name must be `capitalize_words`
- Takes one parameter: a string
- Returns string with each word capitalized
- Words separated by spaces

Examples:
- capitalize_words('hello world') → 'Hello World'
- capitalize_words('python is great') → 'Python Is Great'
- capitalize_words('') → ''""",
        test_cases=[
            TestCase(
                name="normal string",
                call="capitalize_words('hello world')",
                expected="Hello World",
                description="Should capitalize each word"
            ),
            TestCase(
                name="multiple words",
                call="capitalize_words('python is great')",
                expected="Python Is Great",
                description="Should capitalize all words"
            ),
            TestCase(
                name="empty string",
                call="capitalize_words('')",
                expected="",
                description="Should handle empty string"
            ),
            TestCase(
                name="single word",
                call="capitalize_words('hello')",
                expected="Hello",
                description="Should capitalize single word"
            ),
        ],
        gold_solution="def capitalize_words(s):\n    return ' '.join(word.capitalize() for word in s.split())",
        difficulty="easy"
    ),

    SimpleTask(
        task_id="list_intersection",
        description="""I need a function called `list_intersection` that finds common elements between two lists.

Requirements:
- Function name must be `list_intersection`
- Takes two parameters: two lists
- Returns a list of elements present in both lists
- No duplicate elements in result

Examples:
- list_intersection([1, 2, 3], [2, 3, 4]) → [2, 3]
- list_intersection([1, 1, 2], [1, 3]) → [1]
- list_intersection([], [1, 2]) → []""",
        test_cases=[
            TestCase(
                name="normal intersection",
                call="list_intersection([1, 2, 3], [2, 3, 4])",
                expected=[2, 3],
                description="Should find common elements"
            ),
            TestCase(
                name="with duplicates",
                call="list_intersection([1, 1, 2], [1, 3])",
                expected=[1],
                description="Should handle duplicates"
            ),
            TestCase(
                name="empty first list",
                call="list_intersection([], [1, 2])",
                expected=[],
                description="Should handle empty first list"
            ),
            TestCase(
                name="no intersection",
                call="list_intersection([1, 2], [3, 4])",
                expected=[],
                description="Should return empty for no common elements"
            ),
        ],
        gold_solution="""def list_intersection(list1, list2):
    return list(set(list1) & set(list2))""",
        difficulty="easy"
    ),

    # MEDIUM TASKS (11-15)
    SimpleTask(
        task_id="binary_search",
        description="""I need a function called `binary_search` that searches for a target in a sorted list.

Requirements:
- Function name must be `binary_search`
- Takes two parameters: sorted list and target value
- Returns index of target if found, -1 if not found
- Must use binary search algorithm (O(log n))

Examples:
- binary_search([1, 2, 3, 4, 5], 3) → 2
- binary_search([1, 2, 3, 4, 5], 6) → -1
- binary_search([], 1) → -1""",
        test_cases=[
            TestCase(
                name="target exists",
                call="binary_search([1, 2, 3, 4, 5], 3)",
                expected=2,
                description="Should find target and return index"
            ),
            TestCase(
                name="target not found",
                call="binary_search([1, 2, 3, 4, 5], 6)",
                expected=-1,
                description="Should return -1 when target not found"
            ),
            TestCase(
                name="empty list",
                call="binary_search([], 1)",
                expected=-1,
                description="Should handle empty list"
            ),
            TestCase(
                name="single element found",
                call="binary_search([5], 5)",
                expected=0,
                description="Should handle single element list"
            ),
        ],
        gold_solution="""def binary_search(lst, target):
    left, right = 0, len(lst) - 1
    while left <= right:
        mid = (left + right) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""",
        difficulty="medium"
    ),

    SimpleTask(
        task_id="factorial",
        description="""I need a function called `factorial` that computes the factorial of a number.

Requirements:
- Function name must be `factorial`
- Takes one parameter: non-negative integer n
- Returns n! (n factorial)
- factorial(0) = 1

Examples:
- factorial(0) → 1
- factorial(1) → 1
- factorial(5) → 120
- factorial(10) → 3628800""",
        test_cases=[
            TestCase(
                name="base case 0",
                call="factorial(0)",
                expected=1,
                description="factorial(0) should be 1"
            ),
            TestCase(
                name="base case 1",
                call="factorial(1)",
                expected=1,
                description="factorial(1) should be 1"
            ),
            TestCase(
                name="factorial 5",
                call="factorial(5)",
                expected=120,
                description="factorial(5) should be 120"
            ),
            TestCase(
                name="factorial 10",
                call="factorial(10)",
                expected=3628800,
                description="factorial(10) should be 3628800"
            ),
        ],
        gold_solution="""def factorial(n):
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result""",
        difficulty="medium"
    ),

    SimpleTask(
        task_id="flatten_list",
        description="""I need a function called `flatten_list` that flattens a nested list.

Requirements:
- Function name must be `flatten_list`
- Takes one parameter: a nested list
- Returns a flat list with all elements
- Should handle arbitrary nesting depth

Examples:
- flatten_list([1, [2, 3], [4, [5]]]) → [1, 2, 3, 4, 5]
- flatten_list([]) → []
- flatten_list([1, 2, 3]) → [1, 2, 3]""",
        test_cases=[
            TestCase(
                name="nested list",
                call="flatten_list([1, [2, 3], [4, [5]]])",
                expected=[1, 2, 3, 4, 5],
                description="Should flatten nested list"
            ),
            TestCase(
                name="empty list",
                call="flatten_list([])",
                expected=[],
                description="Should handle empty list"
            ),
            TestCase(
                name="already flat",
                call="flatten_list([1, 2, 3])",
                expected=[1, 2, 3],
                description="Should handle already flat list"
            ),
            TestCase(
                name="deeply nested",
                call="flatten_list([[[[1]]]])",
                expected=[1],
                description="Should handle deeply nested list"
            ),
        ],
        gold_solution="""def flatten_list(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result""",
        difficulty="medium"
    ),

    SimpleTask(
        task_id="group_anagrams",
        description="""I need a function called `group_anagrams` that groups anagram strings together.

Requirements:
- Function name must be `group_anagrams`
- Takes one parameter: list of strings
- Returns list of lists, where each inner list contains anagrams
- Order doesn't matter

Examples:
- group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat']) → [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
- group_anagrams([]) → []
- group_anagrams(['a']) → [['a']]""",
        test_cases=[
            TestCase(
                name="multiple anagram groups",
                call="sorted([sorted(group) for group in group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])])",
                expected=[['bat'], ['ate', 'eat', 'tea'], ['nat', 'tan']],
                description="Should group anagrams together"
            ),
            TestCase(
                name="empty list",
                call="group_anagrams([])",
                expected=[],
                description="Should handle empty list"
            ),
            TestCase(
                name="single word",
                call="group_anagrams(['a'])",
                expected=[['a']],
                description="Should handle single word"
            ),
            TestCase(
                name="no anagrams",
                call="sorted([sorted(group) for group in group_anagrams(['a', 'b', 'c'])])",
                expected=[['a'], ['b'], ['c']],
                description="Should handle list with no anagrams"
            ),
        ],
        gold_solution="""def group_anagrams(strs):
    from collections import defaultdict
    groups = defaultdict(list)
    for s in strs:
        key = ''.join(sorted(s))
        groups[key].append(s)
    return list(groups.values())""",
        difficulty="medium"
    ),

    SimpleTask(
        task_id="longest_common_prefix",
        description="""I need a function called `longest_common_prefix` that finds the longest common prefix among strings.

Requirements:
- Function name must be `longest_common_prefix`
- Takes one parameter: list of strings
- Returns the longest common prefix string
- Return empty string if no common prefix

Examples:
- longest_common_prefix(['flower', 'flow', 'flight']) → 'fl'
- longest_common_prefix(['dog', 'racecar', 'car']) → ''
- longest_common_prefix(['']) → ''""",
        test_cases=[
            TestCase(
                name="common prefix exists",
                call="longest_common_prefix(['flower', 'flow', 'flight'])",
                expected="fl",
                description="Should find common prefix 'fl'"
            ),
            TestCase(
                name="no common prefix",
                call="longest_common_prefix(['dog', 'racecar', 'car'])",
                expected="",
                description="Should return empty string for no common prefix"
            ),
            TestCase(
                name="empty string in list",
                call="longest_common_prefix([''])",
                expected="",
                description="Should handle empty string"
            ),
            TestCase(
                name="all same",
                call="longest_common_prefix(['test', 'test', 'test'])",
                expected="test",
                description="Should return full string when all same"
            ),
        ],
        gold_solution="""def longest_common_prefix(strs):
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix""",
        difficulty="medium"
    ),

    # HARD TASKS (16-20)
    SimpleTask(
        task_id="is_valid_parentheses",
        description="""I need a function called `is_valid_parentheses` that checks if parentheses are balanced.

Requirements:
- Function name must be `is_valid_parentheses`
- Takes one parameter: string with parentheses (), {}, []
- Returns True if balanced, False otherwise
- Must handle nested and mixed parentheses

Examples:
- is_valid_parentheses('()') → True
- is_valid_parentheses('()[]{}') → True
- is_valid_parentheses('(]') → False
- is_valid_parentheses('([)]') → False""",
        test_cases=[
            TestCase(
                name="simple valid",
                call="is_valid_parentheses('()')",
                expected=True,
                description="Should validate simple parentheses"
            ),
            TestCase(
                name="multiple types valid",
                call="is_valid_parentheses('()[]{}')",
                expected=True,
                description="Should validate multiple types"
            ),
            TestCase(
                name="mismatched",
                call="is_valid_parentheses('(]')",
                expected=False,
                description="Should detect mismatched parentheses"
            ),
            TestCase(
                name="incorrect nesting",
                call="is_valid_parentheses('([)]')",
                expected=False,
                description="Should detect incorrect nesting"
            ),
        ],
        gold_solution="""def is_valid_parentheses(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack""",
        difficulty="hard"
    ),

    SimpleTask(
        task_id="rotate_matrix",
        description="""I need a function called `rotate_matrix` that rotates a 2D matrix 90 degrees clockwise.

Requirements:
- Function name must be `rotate_matrix`
- Takes one parameter: 2D list (matrix)
- Returns rotated matrix
- Must rotate in-place or return new matrix

Examples:
- rotate_matrix([[1,2],[3,4]]) → [[3,1],[4,2]]
- rotate_matrix([[1]]) → [[1]]""",
        test_cases=[
            TestCase(
                name="2x2 matrix",
                call="rotate_matrix([[1,2],[3,4]])",
                expected=[[3,1],[4,2]],
                description="Should rotate 2x2 matrix"
            ),
            TestCase(
                name="1x1 matrix",
                call="rotate_matrix([[1]])",
                expected=[[1]],
                description="Should handle 1x1 matrix"
            ),
            TestCase(
                name="3x3 matrix",
                call="rotate_matrix([[1,2,3],[4,5,6],[7,8,9]])",
                expected=[[7,4,1],[8,5,2],[9,6,3]],
                description="Should rotate 3x3 matrix"
            ),
        ],
        gold_solution="""def rotate_matrix(matrix):
    n = len(matrix)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            result[j][n-1-i] = matrix[i][j]
    return result""",
        difficulty="hard"
    ),

    SimpleTask(
        task_id="lru_cache",
        description="""I need a class called `LRUCache` that implements a Least Recently Used cache.

Requirements:
- Class name must be `LRUCache`
- __init__(self, capacity): Initialize with max capacity
- get(self, key): Return value if exists, -1 if not
- put(self, key, value): Set key-value, evict LRU if at capacity

Examples:
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
cache.get(1) → 1
cache.put(3, 3)
cache.get(2) → -1 (evicted)""",
        test_cases=[
            TestCase(
                name="basic operations",
                call="(lambda: (c := LRUCache(2), c.put(1, 1), c.put(2, 2), c.get(1))[3])()",
                expected=1,
                description="Should store and retrieve values"
            ),
            TestCase(
                name="eviction",
                call="(lambda: (c := LRUCache(2), c.put(1, 1), c.put(2, 2), c.put(3, 3), c.get(1))[4])()",
                expected=-1,
                description="Should evict least recently used"
            ),
        ],
        gold_solution="""class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key):
        if key not in self.cache:
            return -1
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            lru = self.order.pop(0)
            del self.cache[lru]
        self.cache[key] = value
        self.order.append(key)""",
        difficulty="hard"
    ),

    SimpleTask(
        task_id="word_ladder",
        description="""I need a function called `word_ladder_length` that finds shortest transformation sequence length.

Requirements:
- Function name must be `word_ladder_length`
- Takes: beginWord, endWord, wordList
- Returns length of shortest transformation sequence
- Each step changes one letter, all intermediate words must be in wordList
- Return 0 if no sequence exists

Examples:
- word_ladder_length('hit', 'cog', ['hot','dot','dog','lot','log','cog']) → 5
- word_ladder_length('hit', 'cog', ['hot','dot','dog','lot','log']) → 0""",
        test_cases=[
            TestCase(
                name="valid sequence exists",
                call="word_ladder_length('hit', 'cog', ['hot','dot','dog','lot','log','cog'])",
                expected=5,
                description="Should find shortest path"
            ),
            TestCase(
                name="no sequence",
                call="word_ladder_length('hit', 'cog', ['hot','dot','dog','lot','log'])",
                expected=0,
                description="Should return 0 when no path exists"
            ),
        ],
        gold_solution="""def word_ladder_length(beginWord, endWord, wordList):
    if endWord not in wordList:
        return 0
    from collections import deque
    wordSet = set(wordList)
    queue = deque([(beginWord, 1)])
    while queue:
        word, length = queue.popleft()
        if word == endWord:
            return length
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word in wordSet:
                    wordSet.remove(next_word)
                    queue.append((next_word, length + 1))
    return 0""",
        difficulty="hard"
    ),

    SimpleTask(
        task_id="median_of_two_sorted_arrays",
        description="""I need a function called `find_median_sorted_arrays` that finds median of two sorted arrays.

Requirements:
- Function name must be `find_median_sorted_arrays`
- Takes two parameters: two sorted arrays nums1, nums2
- Returns the median of the combined sorted arrays
- Must be O(log(m+n)) time complexity

Examples:
- find_median_sorted_arrays([1,3], [2]) → 2.0
- find_median_sorted_arrays([1,2], [3,4]) → 2.5""",
        test_cases=[
            TestCase(
                name="odd total length",
                call="find_median_sorted_arrays([1,3], [2])",
                expected=2.0,
                description="Should find median with odd total length"
            ),
            TestCase(
                name="even total length",
                call="find_median_sorted_arrays([1,2], [3,4])",
                expected=2.5,
                description="Should find median with even total length"
            ),
        ],
        gold_solution="""def find_median_sorted_arrays(nums1, nums2):
    merged = sorted(nums1 + nums2)
    n = len(merged)
    if n % 2 == 1:
        return float(merged[n // 2])
    else:
        return (merged[n // 2 - 1] + merged[n // 2]) / 2.0""",
        difficulty="hard"
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
