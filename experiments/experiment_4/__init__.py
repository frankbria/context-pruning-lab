"""
Experiment 4: Code Quality Benchmark (Primary Validation)

Tests continuous pruning vs discrete baseline on real coding tasks.
"""

from .agent import RealCodingAgent, create_agent, AgentConfig

__all__ = ['RealCodingAgent', 'create_agent', 'AgentConfig']
