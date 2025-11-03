"""
SWE-bench Task Selection Module

Handles selection and management of coding tasks for experiments.
For Phase I, uses simplified synthetic tasks that mimic SWE-bench characteristics.
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Handle both module and standalone execution
if __name__ == "__main__":
    # Running as script
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from experiments.swe_bench_extended.types import SWEBenchTask, TaskDifficulty, TaskType
else:
    # Running as module
    from .types import SWEBenchTask, TaskDifficulty, TaskType


class TaskSelector:
    """
    Select and manage coding tasks for experiments.

    Supports both synthetic tasks (for development/testing) and
    real SWE-bench tasks (when dataset is available).
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize task selector.

        Args:
            data_dir: Directory for storing task data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.data_dir / "swe_bench_tasks.json"

    def generate_synthetic_tasks(self, num_tasks: int = 50, seed: int = 42) -> List[SWEBenchTask]:
        """
        Generate synthetic coding tasks for development and testing.

        These tasks mimic SWE-bench characteristics:
        - Realistic issue descriptions
        - Varied difficulty levels
        - Different task types
        - Diverse "repositories"

        Args:
            num_tasks: Number of tasks to generate
            seed: Random seed for reproducibility

        Returns:
            List of synthetic SWEBenchTask objects
        """
        random.seed(seed)
        tasks = []

        # Task templates for different types and difficulties
        templates = self._get_task_templates()

        # Distribute tasks across difficulty levels
        difficulty_distribution = {
            TaskDifficulty.EASY: int(num_tasks * 0.3),    # 30% easy
            TaskDifficulty.MEDIUM: int(num_tasks * 0.5),  # 50% medium
            TaskDifficulty.HARD: int(num_tasks * 0.2)     # 20% hard
        }

        task_id_counter = 1

        for difficulty, count in difficulty_distribution.items():
            for _ in range(count):
                # Select random template
                template = random.choice(templates[difficulty.value])

                task = SWEBenchTask(
                    task_id=f"synthetic_{task_id_counter:03d}",
                    instance_id=f"synthetic-{task_id_counter}",
                    repo=template["repo"],
                    issue_description=template["issue_description"],
                    test_suite=template["test_suite"],
                    base_commit=f"commit_{task_id_counter:06x}",
                    patch=template.get("patch"),
                    difficulty=difficulty,
                    task_type=TaskType(template["task_type"]),
                    metadata={
                        "estimated_lines": template.get("estimated_lines", 50),
                        "files_to_modify": template.get("files_to_modify", ["main.py"]),
                        "template_id": template["id"]
                    }
                )

                tasks.append(task)
                task_id_counter += 1

        # Shuffle for variety
        random.shuffle(tasks)

        return tasks

    def _get_task_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get task templates organized by difficulty.

        Returns:
            Dictionary mapping difficulty level to list of templates
        """
        return {
            "easy": [
                {
                    "id": "easy_string_utils",
                    "repo": "python-utils",
                    "task_type": "bug_fix",
                    "issue_description": (
                        "# Bug: String reversal function fails on empty strings\n\n"
                        "## Description\n"
                        "The `reverse_string()` function in `string_utils.py` raises an "
                        "IndexError when given an empty string as input.\n\n"
                        "## Expected Behavior\n"
                        "Should return an empty string without errors.\n\n"
                        "## Current Behavior\n"
                        "```python\n"
                        "reverse_string('')  # IndexError: string index out of range\n"
                        "```\n\n"
                        "## Steps to Reproduce\n"
                        "1. Call `reverse_string('')`\n"
                        "2. Observe IndexError\n\n"
                        "## Proposed Solution\n"
                        "Add empty string check before processing."
                    ),
                    "test_suite": ["pytest tests/test_string_utils.py::test_reverse_empty"],
                    "estimated_lines": 3,
                    "files_to_modify": ["string_utils.py"],
                    "patch": (
                        "def reverse_string(s: str) -> str:\n"
                        "    if not s:\n"
                        "        return s\n"
                        "    return s[::-1]\n"
                    )
                },
                {
                    "id": "easy_math_divide",
                    "repo": "math-lib",
                    "task_type": "bug_fix",
                    "issue_description": (
                        "# Bug: Division function doesn't handle divide by zero\n\n"
                        "## Description\n"
                        "The `safe_divide()` function should handle division by zero gracefully, "
                        "but currently crashes with ZeroDivisionError.\n\n"
                        "## Expected Behavior\n"
                        "Should return None or raise a custom exception with a helpful message.\n\n"
                        "## Current Behavior\n"
                        "```python\n"
                        "safe_divide(10, 0)  # ZeroDivisionError\n"
                        "```\n"
                    ),
                    "test_suite": ["pytest tests/test_math.py::test_divide_by_zero"],
                    "estimated_lines": 5,
                    "files_to_modify": ["math_ops.py"]
                },
                {
                    "id": "easy_list_sort",
                    "repo": "data-structures",
                    "task_type": "feature_addition",
                    "issue_description": (
                        "# Feature: Add custom sort key parameter\n\n"
                        "## Description\n"
                        "The `sort_list()` function should accept an optional `key` parameter "
                        "for custom sorting, similar to Python's built-in `sorted()`.\n\n"
                        "## Requested Behavior\n"
                        "```python\n"
                        "sort_list([{'name': 'Bob', 'age': 25}, {'name': 'Alice', 'age': 30}], "
                        "key=lambda x: x['age'])\n"
                        "```\n"
                    ),
                    "test_suite": ["pytest tests/test_list_ops.py::test_sort_with_key"],
                    "estimated_lines": 10,
                    "files_to_modify": ["list_ops.py"]
                }
            ],
            "medium": [
                {
                    "id": "medium_api_pagination",
                    "repo": "rest-api",
                    "task_type": "feature_addition",
                    "issue_description": (
                        "# Feature: Implement pagination for GET /users endpoint\n\n"
                        "## Description\n"
                        "The `/users` endpoint returns all users at once, causing performance issues "
                        "with large datasets. Need to add pagination support.\n\n"
                        "## Requirements\n"
                        "1. Accept `page` and `per_page` query parameters\n"
                        "2. Default: page=1, per_page=20\n"
                        "3. Return pagination metadata in response:\n"
                        "   - total_items\n"
                        "   - total_pages\n"
                        "   - current_page\n"
                        "   - next_page (URL)\n"
                        "   - prev_page (URL)\n\n"
                        "## Example Response\n"
                        "```json\n"
                        "{\n"
                        "  \"data\": [...],\n"
                        "  \"pagination\": {\n"
                        "    \"total_items\": 100,\n"
                        "    \"total_pages\": 5,\n"
                        "    \"current_page\": 2,\n"
                        "    \"next_page\": \"/users?page=3\",\n"
                        "    \"prev_page\": \"/users?page=1\"\n"
                        "  }\n"
                        "}\n"
                        "```\n"
                    ),
                    "test_suite": [
                        "pytest tests/test_api.py::test_users_pagination",
                        "pytest tests/test_api.py::test_pagination_metadata"
                    ],
                    "estimated_lines": 40,
                    "files_to_modify": ["api/routes.py", "api/pagination.py"]
                },
                {
                    "id": "medium_cache_invalidation",
                    "repo": "cache-system",
                    "task_type": "bug_fix",
                    "issue_description": (
                        "# Bug: Cache not invalidated after data update\n\n"
                        "## Description\n"
                        "When data is updated via `update_record()`, the cache still returns "
                        "stale data. Cache invalidation logic is not being triggered.\n\n"
                        "## Expected Behavior\n"
                        "Cache should be invalidated or updated when underlying data changes.\n\n"
                        "## Current Behavior\n"
                        "```python\n"
                        "get_record(123)  # Returns {name: 'Old Name'}\n"
                        "update_record(123, name='New Name')\n"
                        "get_record(123)  # Still returns {name: 'Old Name'} (WRONG!)\n"
                        "```\n\n"
                        "## Root Cause\n"
                        "`update_record()` modifies database but doesn't call `cache.invalidate()`.\n"
                    ),
                    "test_suite": [
                        "pytest tests/test_cache.py::test_cache_invalidation_on_update",
                        "pytest tests/test_cache.py::test_cache_coherence"
                    ],
                    "estimated_lines": 20,
                    "files_to_modify": ["cache/manager.py", "db/operations.py"]
                },
                {
                    "id": "medium_async_timeout",
                    "repo": "async-lib",
                    "task_type": "feature_addition",
                    "issue_description": (
                        "# Feature: Add timeout support for async operations\n\n"
                        "## Description\n"
                        "The `fetch_data_async()` function can hang indefinitely if the remote "
                        "service doesn't respond. Need to add configurable timeout.\n\n"
                        "## Requirements\n"
                        "1. Add optional `timeout` parameter (default: 30 seconds)\n"
                        "2. Raise `TimeoutError` if operation exceeds timeout\n"
                        "3. Ensure proper cleanup of resources on timeout\n"
                        "4. Support both per-call and global timeout configuration\n"
                    ),
                    "test_suite": [
                        "pytest tests/test_async.py::test_timeout_enforced",
                        "pytest tests/test_async.py::test_timeout_cleanup"
                    ],
                    "estimated_lines": 30,
                    "files_to_modify": ["async_ops.py", "config.py"]
                }
            ],
            "hard": [
                {
                    "id": "hard_race_condition",
                    "repo": "concurrent-system",
                    "task_type": "bug_fix",
                    "issue_description": (
                        "# Bug: Race condition in multi-threaded counter\n\n"
                        "## Description\n"
                        "The shared counter implementation has a race condition when multiple "
                        "threads increment concurrently. Final count is often incorrect.\n\n"
                        "## Expected Behavior\n"
                        "With 10 threads each incrementing 1000 times, final count should be 10,000.\n\n"
                        "## Current Behavior\n"
                        "Final count varies between 8,000-10,000 (non-deterministic).\n\n"
                        "## Root Cause\n"
                        "The increment operation (read-modify-write) is not atomic. Multiple threads "
                        "can read the same value, increment it, and write back, causing lost updates.\n\n"
                        "## Proposed Solution\n"
                        "Use thread-safe primitives (Lock, atomic operations, or thread-safe data structures)."
                    ),
                    "test_suite": [
                        "pytest tests/test_concurrency.py::test_counter_thread_safety",
                        "pytest tests/test_concurrency.py::test_counter_stress"
                    ],
                    "estimated_lines": 25,
                    "files_to_modify": ["counter.py", "thread_manager.py"]
                },
                {
                    "id": "hard_query_optimizer",
                    "repo": "database-engine",
                    "task_type": "feature_addition",
                    "issue_description": (
                        "# Feature: Implement query optimization for JOIN operations\n\n"
                        "## Description\n"
                        "The query engine performs nested loop joins for all JOIN operations, "
                        "resulting in O(n*m) complexity. Need to implement hash join optimization.\n\n"
                        "## Requirements\n"
                        "1. Detect when hash join is more efficient than nested loop\n"
                        "2. Build hash table for smaller relation\n"
                        "3. Probe with larger relation\n"
                        "4. Handle hash collisions correctly\n"
                        "5. Maintain correctness for all join types (INNER, LEFT, RIGHT)\n"
                        "6. Add query plan explanation showing chosen join algorithm\n\n"
                        "## Performance Target\n"
                        "Queries with large JOINs should be 10x+ faster."
                    ),
                    "test_suite": [
                        "pytest tests/test_query_optimizer.py::test_hash_join_correctness",
                        "pytest tests/test_query_optimizer.py::test_hash_join_performance",
                        "pytest tests/test_query_optimizer.py::test_join_algorithm_selection"
                    ],
                    "estimated_lines": 100,
                    "files_to_modify": ["query/optimizer.py", "query/join_executor.py", "query/plan.py"]
                },
                {
                    "id": "hard_memory_leak",
                    "repo": "graphics-engine",
                    "task_type": "bug_fix",
                    "issue_description": (
                        "# Bug: Memory leak in texture cache\n\n"
                        "## Description\n"
                        "The graphics engine has a memory leak that causes steady memory growth "
                        "during texture loading/unloading cycles. After running for several hours, "
                        "the application exhausts memory and crashes.\n\n"
                        "## Investigation\n"
                        "Profiling shows texture objects are not being garbage collected even after "
                        "`release_texture()` is called. Strong references are being held somewhere.\n\n"
                        "## Suspected Issues\n"
                        "1. Circular references between Texture and TextureCache\n"
                        "2. Event listeners not being unregistered\n"
                        "3. Texture data in GPU memory not being freed\n\n"
                        "## Expected Behavior\n"
                        "Memory usage should remain stable during load/unload cycles."
                    ),
                    "test_suite": [
                        "pytest tests/test_memory.py::test_texture_cleanup",
                        "pytest tests/test_memory.py::test_no_memory_leak"
                    ],
                    "estimated_lines": 40,
                    "files_to_modify": ["graphics/texture.py", "graphics/cache.py", "graphics/gpu.py"]
                }
            ]
        }

    def save_tasks(self, tasks: List[SWEBenchTask]) -> None:
        """
        Save tasks to JSON file.

        Args:
            tasks: List of tasks to save
        """
        tasks_data = [
            {
                "task_id": task.task_id,
                "instance_id": task.instance_id,
                "repo": task.repo,
                "issue_description": task.issue_description,
                "test_suite": task.test_suite,
                "base_commit": task.base_commit,
                "patch": task.patch,
                "difficulty": task.difficulty.value,
                "task_type": task.task_type.value,
                "metadata": task.metadata
            }
            for task in tasks
        ]

        with open(self.tasks_file, 'w') as f:
            json.dump(tasks_data, f, indent=2)

    def load_tasks(self) -> List[SWEBenchTask]:
        """
        Load tasks from JSON file.

        Returns:
            List of SWEBenchTask objects
        """
        if not self.tasks_file.exists():
            raise FileNotFoundError(f"Tasks file not found: {self.tasks_file}")

        with open(self.tasks_file, 'r') as f:
            tasks_data = json.load(f)

        tasks = [
            SWEBenchTask(
                task_id=data["task_id"],
                instance_id=data["instance_id"],
                repo=data["repo"],
                issue_description=data["issue_description"],
                test_suite=data["test_suite"],
                base_commit=data["base_commit"],
                patch=data.get("patch"),
                difficulty=TaskDifficulty(data["difficulty"]),
                task_type=TaskType(data["task_type"]),
                metadata=data.get("metadata", {})
            )
            for data in tasks_data
        ]

        return tasks

    def get_task_statistics(self, tasks: List[SWEBenchTask]) -> Dict[str, Any]:
        """
        Generate statistics about task collection.

        Args:
            tasks: List of tasks to analyze

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_tasks": len(tasks),
            "by_difficulty": {
                "easy": len([t for t in tasks if t.difficulty == TaskDifficulty.EASY]),
                "medium": len([t for t in tasks if t.difficulty == TaskDifficulty.MEDIUM]),
                "hard": len([t for t in tasks if t.difficulty == TaskDifficulty.HARD])
            },
            "by_type": {
                "bug_fix": len([t for t in tasks if t.task_type == TaskType.BUG_FIX]),
                "feature_addition": len([t for t in tasks if t.task_type == TaskType.FEATURE_ADDITION]),
                "refactoring": len([t for t in tasks if t.task_type == TaskType.REFACTORING]),
                "documentation": len([t for t in tasks if t.task_type == TaskType.DOCUMENTATION])
            },
            "repositories": len(set(t.repo for t in tasks))
        }

        return stats


def main():
    """Generate and save default task set for experiments."""
    print("Generating 50 synthetic SWE-bench tasks...")

    selector = TaskSelector()
    tasks = selector.generate_synthetic_tasks(num_tasks=50, seed=42)

    print(f"Generated {len(tasks)} tasks")
    print("\nTask statistics:")
    stats = selector.get_task_statistics(tasks)
    print(f"  Total: {stats['total_tasks']}")
    print(f"  By difficulty: {stats['by_difficulty']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Repositories: {stats['repositories']}")

    print(f"\nSaving tasks to {selector.tasks_file}...")
    selector.save_tasks(tasks)
    print("Done!")


if __name__ == "__main__":
    main()
