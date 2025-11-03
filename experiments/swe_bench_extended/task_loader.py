"""
SWE-bench Extended Task Loader

Provides efficient loading of tasks with conversation scripts.
Includes lazy loading, caching, and iterator support for batch processing.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from functools import lru_cache

# Handle both module and standalone execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from experiments.swe_bench_extended.types import (
        SWEBenchTask, ConversationScript, ConversationTurn,
        TaskDifficulty, TaskType
    )
    from experiments.swe_bench_extended.script_generator import ConversationScriptGenerator
else:
    from .types import (
        SWEBenchTask, ConversationScript, ConversationTurn,
        TaskDifficulty, TaskType
    )
    from .script_generator import ConversationScriptGenerator


class SWEBenchExtendedLoader:
    """
    Load and manage SWE-bench Extended tasks with conversation scripts.

    Features:
    - Lazy loading (tasks loaded on-demand)
    - LRU caching (frequently accessed tasks cached in memory)
    - Batch loading support
    - Iterator interface for streaming large datasets
    - Automatic script generation if not cached
    """

    def __init__(
        self,
        data_dir: str = "data",
        cache_size: int = 50,
        auto_generate_scripts: bool = True,
        script_seed: int = 42
    ):
        """
        Initialize task loader.

        Args:
            data_dir: Directory containing task and script data
            cache_size: Number of tasks to keep in LRU cache
            auto_generate_scripts: Generate scripts if not found
            script_seed: Random seed for script generation
        """
        self.data_dir = Path(data_dir)
        self.tasks_file = self.data_dir / "swe_bench_tasks.json"
        self.scripts_dir = self.data_dir / "conversation_scripts"
        self.cache_size = cache_size
        self.auto_generate_scripts = auto_generate_scripts
        self.script_seed = script_seed

        # Ensure directories exist
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

        # Load task index (lightweight metadata)
        self._task_index = self._load_task_index()

        # Script generator for on-demand generation
        if auto_generate_scripts:
            self._script_generator = ConversationScriptGenerator(seed=script_seed)

    def _load_task_index(self) -> Dict[str, Dict[str, Any]]:
        """
        Load lightweight task index (metadata only, not full tasks).

        Returns:
            Dictionary mapping task_id to task metadata
        """
        if not self.tasks_file.exists():
            raise FileNotFoundError(
                f"Tasks file not found: {self.tasks_file}\n"
                "Run task_selector.py to generate tasks."
            )

        with open(self.tasks_file) as f:
            tasks_data = json.load(f)

        # Create index with just metadata
        index = {}
        for task_data in tasks_data:
            task_id = task_data["task_id"]
            index[task_id] = {
                "instance_id": task_data["instance_id"],
                "repo": task_data["repo"],
                "difficulty": task_data["difficulty"],
                "task_type": task_data["task_type"],
                "has_patch": task_data.get("patch") is not None
            }

        return index

    @lru_cache(maxsize=50)
    def load_task(self, task_id: str) -> SWEBenchTask:
        """
        Load a single task by ID.

        Uses LRU cache to keep frequently accessed tasks in memory.

        Args:
            task_id: Task identifier

        Returns:
            SWEBenchTask object

        Raises:
            KeyError: If task_id not found
        """
        if task_id not in self._task_index:
            raise KeyError(f"Task not found: {task_id}")

        # Load full task data from file
        with open(self.tasks_file) as f:
            tasks_data = json.load(f)

        task_data = next((t for t in tasks_data if t["task_id"] == task_id), None)
        if not task_data:
            raise KeyError(f"Task data not found: {task_id}")

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

        return task

    def load_task_with_script(
        self,
        task_id: str,
        target_turns: int = 20,
        include_noise: bool = True
    ) -> tuple[SWEBenchTask, ConversationScript]:
        """
        Load task with its conversation script.

        If script doesn't exist and auto_generate_scripts is True,
        generates and caches it automatically.

        Args:
            task_id: Task identifier
            target_turns: Target number of conversation turns
            include_noise: Include noise items in conversation

        Returns:
            Tuple of (SWEBenchTask, ConversationScript)
        """
        task = self.load_task(task_id)

        # Try to load cached script
        script_file = self.scripts_dir / f"{task_id}_conversation.json"

        if script_file.exists():
            script = self._load_script_from_file(script_file)
        elif self.auto_generate_scripts:
            # Generate script on-demand
            script = self._script_generator.generate_script(
                task, target_turns=target_turns, include_noise=include_noise
            )
            # Cache it for future use
            self._save_script_to_file(script, script_file)
        else:
            raise FileNotFoundError(
                f"Script not found for task {task_id} and auto_generate_scripts is False"
            )

        return task, script

    def _load_script_from_file(self, script_file: Path) -> ConversationScript:
        """Load conversation script from JSON file."""
        with open(script_file) as f:
            script_data = json.load(f)

        turns = [
            ConversationTurn(
                turn_number=t["turn_number"],
                role=t["role"],
                content=t["content"],
                turn_type=t["turn_type"],
                metadata=t.get("metadata", {})
            )
            for t in script_data["turns"]
        ]

        script = ConversationScript(
            task_id=script_data["task_id"],
            turns=turns,
            seed=script_data["seed"],
            template_version=script_data.get("template_version", "1.0"),
            metadata=script_data.get("metadata", {})
        )

        return script

    def _save_script_to_file(self, script: ConversationScript, file_path: Path):
        """Save conversation script to JSON file."""
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

        with open(file_path, 'w') as f:
            json.dump(script_data, f, indent=2)

    def load_batch(
        self,
        task_ids: List[str],
        with_scripts: bool = False
    ) -> List[SWEBenchTask] | List[tuple[SWEBenchTask, ConversationScript]]:
        """
        Load multiple tasks at once.

        Args:
            task_ids: List of task identifiers
            with_scripts: Whether to include conversation scripts

        Returns:
            List of tasks (or tuples of task and script if with_scripts=True)
        """
        if with_scripts:
            return [self.load_task_with_script(tid) for tid in task_ids]
        else:
            return [self.load_task(tid) for tid in task_ids]

    def iterate_tasks(
        self,
        with_scripts: bool = False,
        filter_difficulty: Optional[TaskDifficulty] = None,
        filter_type: Optional[TaskType] = None
    ) -> Iterator[SWEBenchTask] | Iterator[tuple[SWEBenchTask, ConversationScript]]:
        """
        Iterate over all tasks (streaming, memory-efficient).

        Args:
            with_scripts: Whether to include conversation scripts
            filter_difficulty: Optional difficulty filter
            filter_type: Optional task type filter

        Yields:
            Task (or tuple of task and script if with_scripts=True)
        """
        task_ids = self.get_task_ids(
            filter_difficulty=filter_difficulty,
            filter_type=filter_type
        )

        for task_id in task_ids:
            if with_scripts:
                yield self.load_task_with_script(task_id)
            else:
                yield self.load_task(task_id)

    def get_task_ids(
        self,
        filter_difficulty: Optional[TaskDifficulty] = None,
        filter_type: Optional[TaskType] = None
    ) -> List[str]:
        """
        Get list of task IDs, optionally filtered.

        Args:
            filter_difficulty: Optional difficulty filter
            filter_type: Optional task type filter

        Returns:
            List of task IDs matching filters
        """
        task_ids = list(self._task_index.keys())

        if filter_difficulty:
            task_ids = [
                tid for tid in task_ids
                if self._task_index[tid]["difficulty"] == filter_difficulty.value
            ]

        if filter_type:
            task_ids = [
                tid for tid in task_ids
                if self._task_index[tid]["task_type"] == filter_type.value
            ]

        return task_ids

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded task set.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_tasks": len(self._task_index),
            "by_difficulty": {},
            "by_type": {},
            "repositories": set(),
            "cached_scripts": 0
        }

        # Count by difficulty and type
        for task_id, metadata in self._task_index.items():
            difficulty = metadata["difficulty"]
            task_type = metadata["task_type"]

            stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1
            stats["by_type"][task_type] = stats["by_type"].get(task_type, 0) + 1
            stats["repositories"].add(metadata["repo"])

            # Check if script exists
            script_file = self.scripts_dir / f"{task_id}_conversation.json"
            if script_file.exists():
                stats["cached_scripts"] += 1

        stats["repositories"] = len(stats["repositories"])

        return stats

    def pregenerate_all_scripts(
        self,
        target_turns: int = 20,
        include_noise: bool = True,
        show_progress: bool = True
    ):
        """
        Pre-generate conversation scripts for all tasks.

        Useful for preparing dataset before running experiments.

        Args:
            target_turns: Target number of conversation turns
            include_noise: Include noise items
            show_progress: Show progress bar
        """
        if not self.auto_generate_scripts:
            raise ValueError("auto_generate_scripts must be True to pre-generate scripts")

        task_ids = self.get_task_ids()

        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(task_ids, desc="Generating scripts")
            except ImportError:
                iterator = task_ids
                print(f"Generating scripts for {len(task_ids)} tasks...")
        else:
            iterator = task_ids

        generated = 0
        skipped = 0

        for task_id in iterator:
            script_file = self.scripts_dir / f"{task_id}_conversation.json"

            if script_file.exists():
                skipped += 1
                continue

            # Load task and generate script
            task = self.load_task(task_id)
            script = self._script_generator.generate_script(
                task, target_turns=target_turns, include_noise=include_noise
            )
            self._save_script_to_file(script, script_file)
            generated += 1

        if show_progress:
            print(f"\nGenerated: {generated}, Skipped (already exist): {skipped}")


def main():
    """Test the task loader."""
    print("Initializing SWE-bench Extended Loader...")

    loader = SWEBenchExtendedLoader(
        data_dir="data",
        cache_size=50,
        auto_generate_scripts=True
    )

    # Show statistics
    stats = loader.get_statistics()
    print(f"\nDataset statistics:")
    print(f"  Total tasks: {stats['total_tasks']}")
    print(f"  By difficulty: {stats['by_difficulty']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Repositories: {stats['repositories']}")
    print(f"  Cached scripts: {stats['cached_scripts']}")

    # Test loading a single task
    print("\n--- Testing single task load ---")
    task_ids = loader.get_task_ids()
    if task_ids:
        task_id = task_ids[0]
        print(f"Loading task: {task_id}")

        task, script = loader.load_task_with_script(task_id)

        print(f"  Repo: {task.repo}")
        print(f"  Difficulty: {task.difficulty.value}")
        print(f"  Type: {task.task_type.value}")
        print(f"  Script turns: {script.num_turns}")

    # Test batch loading
    print("\n--- Testing batch load ---")
    batch_ids = task_ids[:3]
    print(f"Loading {len(batch_ids)} tasks...")

    batch_tasks = loader.load_batch(batch_ids, with_scripts=False)
    print(f"Loaded {len(batch_tasks)} tasks")

    # Test filtering
    print("\n--- Testing filtering ---")
    easy_tasks = loader.get_task_ids(filter_difficulty=TaskDifficulty.EASY)
    print(f"Easy tasks: {len(easy_tasks)}")

    bug_fix_tasks = loader.get_task_ids(filter_type=TaskType.BUG_FIX)
    print(f"Bug fix tasks: {len(bug_fix_tasks)}")

    # Test pre-generation (just first 5 tasks for demo)
    print("\n--- Testing script pre-generation (first 5 tasks) ---")
    for task_id in task_ids[:5]:
        script_file = loader.scripts_dir / f"{task_id}_conversation.json"
        if not script_file.exists():
            task = loader.load_task(task_id)
            script = loader._script_generator.generate_script(task)
            loader._save_script_to_file(script, script_file)
            print(f"  Generated script for {task_id}")

    # Show updated stats
    stats = loader.get_statistics()
    print(f"\nUpdated cached scripts: {stats['cached_scripts']}")

    print("\n✅ Task loader working correctly!")


if __name__ == "__main__":
    main()
