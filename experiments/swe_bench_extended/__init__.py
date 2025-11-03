"""
SWE-bench Extended Infrastructure

This package provides infrastructure for running extended SWE-bench coding tasks
with multi-turn conversations to stress-test context management strategies.

Modules:
    types: Shared type definitions
    task_loader: SWE-bench task loading and management
    script_generator: Multi-turn conversation script generation
    harness: Experiment execution framework
    mock_agent: Mock coding agent for testing
"""

from .types import (
    TaskDifficulty,
    TaskType,
    SWEBenchTask,
    ConversationTurn,
    ConversationScript,
    TaskResult
)

__version__ = "1.0.0"
__all__ = [
    'TaskDifficulty',
    'TaskType',
    'SWEBenchTask',
    'ConversationTurn',
    'ConversationScript',
    'TaskResult',
]
