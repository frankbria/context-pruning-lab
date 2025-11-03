# Sprint 4: Code Quality Benchmark - Implementation Checklist

**Sprint Duration**: Week 7-8 (2 weeks)
**Goal**: Execute Experiment 4 (primary validation) comparing continuous pruning vs. discrete baseline on code generation quality
**Status**: Not Started
**Critical**: This is the PRIMARY validation experiment - Phase I success depends on it

---

## 🎯 Sprint 4 Objectives

1. Implement all four code quality metrics
2. Integrate real LLM-based coding agent (replace mock)
3. Execute 50 SWE-bench Extended tasks with both strategies
4. Perform comparative analysis
5. Validate acceptance criteria (≥2 of 3 must pass)

**Success Criteria**:
- [ ] All 100 task executions completed (50 tasks × 2 strategies)
- [ ] ≥2 of 3 primary acceptance criteria met:
  - Task completion ≥90% of baseline
  - Spec adherence ≥95% of baseline
  - Code quality ≥ baseline
- [ ] Preliminary analysis complete with visualizations
- [ ] Go/no-go decision for Phase I completion

---

## Task Overview

| Task | Priority | Hours | Dependencies | Status |
|------|----------|-------|--------------|--------|
| T4.1: Code Quality Metrics | P0 | 12 | None | ⬜ Not Started |
| T4.2: Real Agent Integration | P0 | 10 | Sprint 3 | ⬜ Not Started |
| T4.3: Experiment 4 Implementation | P0 | 8 | T4.1, T4.2 | ⬜ Not Started |
| T4.4: Execute - Continuous Pruning | P0 | 6 | T4.3 | ⬜ Not Started |
| T4.5: Execute - Discrete Baseline | P0 | 6 | T4.3 | ⬜ Not Started |
| T4.6: Preliminary Analysis | P0 | 8 | T4.4, T4.5 | ⬜ Not Started |
| T4.7: Documentation & Review | P0 | 4 | T4.6 | ⬜ Not Started |

**Total Estimated Hours**: 54 hours (2.7 weeks at 20 hrs/week)

---

# T4.1: Implement Code Quality Metrics

**Priority**: P0
**Estimated Hours**: 12
**Dependencies**: None
**Location**: `experiments/metrics.py`

## Overview

Implement all four code quality metrics for evaluating agent performance on coding tasks.

## Sub-Tasks

### 1.1: Create Metrics Base Class (1 hour)

**File**: `experiments/metrics.py`

- [ ] Define `BaseMetric` abstract base class
  ```python
  from abc import ABC, abstractmethod
  from typing import Dict, Any

  class BaseMetric(ABC):
      """Base class for all evaluation metrics"""

      @abstractmethod
      def calculate(self, task_result: Dict[str, Any]) -> float:
          """Calculate metric score for a task result"""
          pass

      @abstractmethod
      def get_name(self) -> str:
          """Return metric name"""
          pass

      @abstractmethod
      def get_description(self) -> str:
          """Return metric description"""
          pass
  ```

- [ ] Add common utility methods (normalization, aggregation)
- [ ] Write docstrings for all methods

**Acceptance Criteria**:
- [ ] Base class defined with abstract methods
- [ ] Common utilities implemented
- [ ] Type hints on all methods
- [ ] Comprehensive docstrings

---

### 1.2: Implement TaskCompletionRateMetric (2 hours)

**File**: `experiments/metrics.py`

- [ ] Create `TaskCompletionRateMetric` class
  ```python
  class TaskCompletionRateMetric(BaseMetric):
      """Measures percentage of test cases that pass"""

      def calculate(self, task_result: Dict[str, Any]) -> float:
          """
          Calculate task completion rate

          Returns:
              float: Percentage of tests passed (0.0 - 1.0)
          """
          tests_passed = task_result['tests_passed']
          tests_total = task_result['tests_total']

          if tests_total == 0:
              return 0.0

          return tests_passed / tests_total
  ```

- [ ] Add test suite execution logic
- [ ] Handle edge cases (no tests, all tests pass, all tests fail)
- [ ] Add logging for test execution results

**Implementation Notes**:
- Use pytest or unittest to run test suites
- Capture test output for debugging
- Timeout tests after 30 seconds (configurable)

**Acceptance Criteria**:
- [ ] Metric returns percentage (0.0 - 1.0)
- [ ] Handles edge cases gracefully
- [ ] Logs test execution details
- [ ] Unit tests covering all scenarios

---

### 1.3: Implement SpecificationAdherenceMetric (3 hours)

**File**: `experiments/metrics.py`

- [ ] Create `SpecificationAdherenceMetric` class
  ```python
  class SpecificationAdherenceMetric(BaseMetric):
      """Measures how well implementation meets requirements"""

      def calculate(self, task_result: Dict[str, Any]) -> float:
          """
          Calculate specification adherence score

          Process:
          1. Extract requirements from issue description
          2. Validate implementation against each requirement
          3. Return percentage of requirements met

          Returns:
              float: Percentage of requirements met (0.0 - 1.0)
          """
          issue_description = task_result['issue_description']
          implementation = task_result['generated_code']

          # Extract requirements
          requirements = self._extract_requirements(issue_description)

          # Validate each requirement
          met_requirements = 0
          for req in requirements:
              if self._validate_requirement(req, implementation):
                  met_requirements += 1

          return met_requirements / len(requirements) if requirements else 0.0
  ```

- [ ] Implement `_extract_requirements()` method
  - Parse issue description for requirements
  - Use heuristics: "should", "must", "needs to", etc.
  - Create requirement checklist

- [ ] Implement `_validate_requirement()` method
  - Keyword matching (basic)
  - Pattern matching (regex)
  - Optional: LLM-based validation (if budget allows)

- [ ] Add caching for extracted requirements

**Implementation Notes**:
- Start with rule-based validation (simpler, faster)
- Consider LLM-based validation only if rule-based insufficient
- Document validation heuristics

**Acceptance Criteria**:
- [ ] Requirements extracted from issue descriptions
- [ ] Validation logic implemented
- [ ] Handles various requirement phrasings
- [ ] Returns score 0.0 - 1.0
- [ ] Unit tests with sample issue descriptions

---

### 1.4: Implement CodeQualityScoreMetric (4 hours)

**File**: `experiments/metrics.py`

- [ ] Create `CodeQualityScoreMetric` class with rubric
  ```python
  class CodeQualityScoreMetric(BaseMetric):
      """Evaluates code quality on 20-point rubric"""

      RUBRIC = {
          'maintainability': 5,    # Clear structure, readable
          'conventions': 5,        # PEP 8, naming, style
          'completeness': 5,       # All functions implemented
          'specification_match': 5 # Matches spec exactly
      }

      def calculate(self, task_result: Dict[str, Any]) -> float:
          """
          Calculate code quality score (0-20)

          Returns:
              float: Score 0-20 (normalized to 0.0-1.0 for consistency)
          """
          code = task_result['generated_code']
          spec = task_result['issue_description']

          scores = {
              'maintainability': self._score_maintainability(code),
              'conventions': self._score_conventions(code),
              'completeness': self._score_completeness(code, spec),
              'specification_match': self._score_spec_match(code, spec)
          }

          total_score = sum(scores.values())
          return total_score / 20.0  # Normalize to 0.0-1.0
  ```

- [ ] Implement `_score_maintainability()` (0-5)
  - Function length (prefer < 50 lines)
  - Cyclomatic complexity (prefer < 10)
  - Docstring presence
  - Comment presence

- [ ] Implement `_score_conventions()` (0-5)
  - Run flake8 or pylint
  - Count violations
  - Deduct points for violations
  - Check naming conventions

- [ ] Implement `_score_completeness()` (0-5)
  - Check all required functions present
  - Check imports complete
  - Check error handling present

- [ ] Implement `_score_spec_match()` (0-5)
  - API matches specification
  - Function signatures correct
  - Return types match

**Implementation Notes**:
- Use static analysis tools: flake8, pylint, radon (complexity)
- Cache linter results
- Document scoring rubric clearly

**Acceptance Criteria**:
- [ ] All 4 rubric dimensions implemented
- [ ] Scores in range 0-5 for each dimension
- [ ] Total score 0-20 (normalized to 0-1)
- [ ] Static analysis tools integrated
- [ ] Unit tests for each scoring dimension

---

### 1.5: Implement ImplementationConsistencyMetric (2 hours)

**File**: `experiments/metrics.py`

- [ ] Create `ImplementationConsistencyMetric` class
  ```python
  class ImplementationConsistencyMetric(BaseMetric):
      """Measures consistency of approach across conversation turns"""

      def calculate(self, task_result: Dict[str, Any]) -> float:
          """
          Calculate implementation consistency score (0-5)

          Tracks:
          - Architecture decisions maintained
          - No contradictions or reversals
          - Coherent progression

          Returns:
              float: Consistency score 0.0-1.0 (normalized from 0-5)
          """
          conversation = task_result['conversation_history']

          # Track decisions across turns
          decisions = self._extract_decisions(conversation)

          # Detect contradictions
          contradictions = self._detect_contradictions(decisions)

          # Score: Start at 5, deduct for contradictions
          score = 5.0 - (len(contradictions) * 0.5)
          score = max(0.0, score)  # Floor at 0

          return score / 5.0  # Normalize to 0-1
  ```

- [ ] Implement `_extract_decisions()` method
  - Parse conversation for key decisions
  - Track: architecture, algorithm, data structure choices

- [ ] Implement `_detect_contradictions()` method
  - Compare decisions across turns
  - Flag reversals without explanation

**Implementation Notes**:
- Use simple pattern matching for decisions
- Look for keywords: "decided", "will use", "changed to"
- Consider LLM-based consistency check if needed

**Acceptance Criteria**:
- [ ] Decisions extracted from conversation
- [ ] Contradictions detected
- [ ] Score in range 0-5 (normalized to 0-1)
- [ ] Unit tests with sample conversations

---

### 1.6: Create MetricsCollector (1 hour)

**File**: `experiments/metrics.py`

- [ ] Create `MetricsCollector` class
  ```python
  class MetricsCollector:
      """Collects and aggregates all metrics for a task"""

      def __init__(self):
          self.metrics = [
              TaskCompletionRateMetric(),
              SpecificationAdherenceMetric(),
              CodeQualityScoreMetric(),
              ImplementationConsistencyMetric()
          ]

      def collect_all(self, task_result: Dict[str, Any]) -> Dict[str, float]:
          """Collect all metrics for a task result"""
          return {
              metric.get_name(): metric.calculate(task_result)
              for metric in self.metrics
          }

      def aggregate_results(self, all_results: List[Dict[str, float]]) -> Dict[str, Any]:
          """Aggregate metrics across multiple tasks"""
          # Calculate mean, std, min, max for each metric
          pass
  ```

- [ ] Implement aggregation methods (mean, std, percentiles)
- [ ] Add serialization (save to JSON/CSV)

**Acceptance Criteria**:
- [ ] Collector runs all metrics
- [ ] Aggregation functions work
- [ ] Results serializable
- [ ] Unit tests for collection and aggregation

---

### 1.7: Unit Tests for Metrics (1 hour)

**File**: `tests/test_metrics.py`

- [ ] Create test suite for all metrics
  ```python
  import pytest
  from experiments.metrics import (
      TaskCompletionRateMetric,
      SpecificationAdherenceMetric,
      CodeQualityScoreMetric,
      ImplementationConsistencyMetric,
      MetricsCollector
  )

  class TestTaskCompletionRateMetric:
      def test_all_tests_pass(self):
          metric = TaskCompletionRateMetric()
          result = {'tests_passed': 10, 'tests_total': 10}
          assert metric.calculate(result) == 1.0

      def test_partial_pass(self):
          metric = TaskCompletionRateMetric()
          result = {'tests_passed': 7, 'tests_total': 10}
          assert metric.calculate(result) == 0.7

      def test_no_tests(self):
          metric = TaskCompletionRateMetric()
          result = {'tests_passed': 0, 'tests_total': 0}
          assert metric.calculate(result) == 0.0

  # Similar tests for other metrics...
  ```

- [ ] Test edge cases for each metric
- [ ] Test MetricsCollector integration
- [ ] Test aggregation functions
- [ ] Achieve >95% code coverage for metrics module

**Acceptance Criteria**:
- [ ] All metrics have unit tests
- [ ] Edge cases covered
- [ ] Tests pass
- [ ] >95% code coverage

---

## T4.1 Completion Checklist

- [ ] All 7 sub-tasks completed
- [ ] All 4 metrics implemented and tested
- [ ] MetricsCollector functional
- [ ] Unit tests passing (>95% coverage)
- [ ] Documentation complete (docstrings, README update)
- [ ] Code reviewed (self-review checklist)

**Deliverables**:
- `experiments/metrics.py` (~400 lines)
- `tests/test_metrics.py` (~200 lines)
- Updated documentation

---

# T4.2: Real Agent Integration

**Priority**: P0
**Estimated Hours**: 10
**Dependencies**: Sprint 3 (test harness infrastructure)
**Location**: `experiments/coding_agent.py`

## Overview

Replace mock agent with actual LLM-based coding agent that integrates with Claude API and uses context management strategies.

## Sub-Tasks

### 2.1: Design CodingAgent Interface (1 hour)

**File**: `experiments/coding_agent.py`

- [ ] Define `CodingAgent` interface
  ```python
  from typing import Protocol, Dict, Any, List
  from abc import ABC, abstractmethod

  class ContextStrategy(Protocol):
      """Protocol for context management strategies"""
      def add_interaction(self, user_msg: str, agent_msg: str) -> None:
          """Add interaction to context"""
          pass

      def get_context(self) -> List[Dict[str, str]]:
          """Get current context for LLM"""
          pass

      def get_stats(self) -> Dict[str, Any]:
          """Get context statistics"""
          pass

  class CodingAgent:
      """LLM-based coding agent with pluggable context strategy"""

      def __init__(self,
                   context_strategy: ContextStrategy,
                   llm_config: Dict[str, Any]):
          self.context_strategy = context_strategy
          self.llm_config = llm_config
          self.conversation_history = []

      def process_message(self, user_message: str) -> str:
          """Process user message and generate response"""
          pass

      def get_context_stats(self) -> Dict[str, Any]:
          """Get current context statistics"""
          return self.context_strategy.get_stats()
  ```

- [ ] Document interface contracts
- [ ] Add type hints throughout

**Acceptance Criteria**:
- [ ] Interface clearly defined
- [ ] Type hints complete
- [ ] Documentation complete

---

### 2.2: Implement Claude API Integration (3 hours)

**File**: `experiments/coding_agent.py`

- [ ] Add Anthropic SDK dependency
  ```bash
  # requirements.txt
  anthropic>=0.25.0
  ```

- [ ] Implement LLM client wrapper
  ```python
  from anthropic import Anthropic
  import os

  class ClaudeClient:
      """Wrapper for Claude API with error handling"""

      def __init__(self, config: Dict[str, Any]):
          self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
          self.model = config.get('model', 'claude-sonnet-3-5-20241022')
          self.temperature = config.get('temperature', 0.0)  # Deterministic
          self.max_tokens = config.get('max_tokens', 4096)

      def generate_response(self,
                          messages: List[Dict[str, str]],
                          system_prompt: str = None) -> str:
          """Generate response from Claude API"""
          try:
              response = self.client.messages.create(
                  model=self.model,
                  max_tokens=self.max_tokens,
                  temperature=self.temperature,
                  system=system_prompt,
                  messages=messages
              )
              return response.content[0].text
          except Exception as e:
              # Handle API errors
              raise
  ```

- [ ] Add error handling for:
  - API rate limits (429)
  - Network errors
  - Invalid responses
  - Timeout errors

- [ ] Add retry logic with exponential backoff
  ```python
  import time
  from functools import wraps

  def retry_with_backoff(max_retries=3, base_delay=1.0):
      def decorator(func):
          @wraps(func)
          def wrapper(*args, **kwargs):
              for attempt in range(max_retries):
                  try:
                      return func(*args, **kwargs)
                  except Exception as e:
                      if attempt == max_retries - 1:
                          raise
                      delay = base_delay * (2 ** attempt)
                      time.sleep(delay)
              return None
          return wrapper
      return decorator
  ```

- [ ] Add API call logging (requests, responses, tokens used)

**Implementation Notes**:
- Use environment variable for API key
- Start with Claude Sonnet (cost-effective)
- Set temperature=0 for reproducibility

**Acceptance Criteria**:
- [ ] Claude API integration working
- [ ] Error handling comprehensive
- [ ] Retry logic implemented
- [ ] API calls logged
- [ ] Unit tests with mocked API

---

### 2.3: Implement Context Strategy Integration (2 hours)

**File**: `experiments/coding_agent.py`

- [ ] Create strategy adapter for ContinuousPruner
  ```python
  class ContinuousPrunerStrategy:
      """Adapter for ContinuousPruner as ContextStrategy"""

      def __init__(self, target_tokens: int = 40000):
          from pruner import ContinuousPruner
          self.pruner = ContinuousPruner(target_tokens)

      def add_interaction(self, user_msg: str, agent_msg: str) -> None:
          self.pruner.add_item(user_msg, item_type='user_message')
          self.pruner.add_item(agent_msg, item_type='agent_response')
          self.pruner.prune_after_interaction(user_msg, agent_msg)

      def get_context(self) -> List[Dict[str, str]]:
          """Convert pruner context to LLM message format"""
          messages = []
          for item in self.pruner.get_current_context():
              role = 'user' if item.item_type == 'user_message' else 'assistant'
              messages.append({'role': role, 'content': item.content})
          return messages

      def get_stats(self) -> Dict[str, Any]:
          return self.pruner.get_metrics_summary()
  ```

- [ ] Create strategy adapter for DiscreteCompactionBaseline
  ```python
  class DiscreteBaselineStrategy:
      """Adapter for DiscreteCompactionBaseline as ContextStrategy"""

      def __init__(self, target_tokens: int = 40000):
          from baseline import DiscreteCompactionBaseline
          self.baseline = DiscreteCompactionBaseline(target_tokens)

      def add_interaction(self, user_msg: str, agent_msg: str) -> None:
          self.baseline.add_item(user_msg, item_type='user_message')
          self.baseline.add_item(agent_msg, item_type='agent_response')

      def get_context(self) -> List[Dict[str, str]]:
          """Convert baseline context to LLM message format"""
          messages = []
          for item in self.baseline.get_current_context():
              role = 'user' if item.item_type == 'user_message' else 'assistant'
              messages.append({'role': role, 'content': item.content})
          return messages

      def get_stats(self) -> Dict[str, Any]:
          return self.baseline.get_metrics_summary()
  ```

- [ ] Integrate strategies into CodingAgent
  ```python
  class CodingAgent:
      def process_message(self, user_message: str) -> str:
          """Process message using context strategy"""
          # Get current context from strategy
          context_messages = self.context_strategy.get_context()

          # Add new user message
          context_messages.append({'role': 'user', 'content': user_message})

          # Generate response
          response = self.llm_client.generate_response(
              messages=context_messages,
              system_prompt=self.system_prompt
          )

          # Update context strategy
          self.context_strategy.add_interaction(user_message, response)

          return response
  ```

**Acceptance Criteria**:
- [ ] Both strategy adapters implemented
- [ ] Integration with CodingAgent complete
- [ ] Context flows correctly through strategies
- [ ] Unit tests for strategy adapters

---

### 2.4: Implement Rate Limiting & Cost Tracking (2 hours)

**File**: `experiments/coding_agent.py`

- [ ] Add rate limiter
  ```python
  import time
  from collections import deque

  class RateLimiter:
      """Rate limiter for API calls"""

      def __init__(self, calls_per_minute: int = 50):
          self.calls_per_minute = calls_per_minute
          self.call_times = deque()

      def acquire(self):
          """Wait if necessary to respect rate limit"""
          now = time.time()

          # Remove calls older than 1 minute
          while self.call_times and now - self.call_times[0] > 60:
              self.call_times.popleft()

          # If at limit, wait
          if len(self.call_times) >= self.calls_per_minute:
              sleep_time = 60 - (now - self.call_times[0])
              if sleep_time > 0:
                  time.sleep(sleep_time)

          self.call_times.append(now)
  ```

- [ ] Add cost tracker
  ```python
  class CostTracker:
      """Track API costs"""

      # Pricing per 1K tokens (as of 2024)
      PRICING = {
          'claude-opus-3-5-20250219': {'input': 0.015, 'output': 0.075},
          'claude-sonnet-3-5-20241022': {'input': 0.003, 'output': 0.015},
          'claude-haiku-3-5-20241022': {'input': 0.001, 'output': 0.005}
      }

      def __init__(self, model: str):
          self.model = model
          self.total_input_tokens = 0
          self.total_output_tokens = 0

      def record_usage(self, input_tokens: int, output_tokens: int):
          self.total_input_tokens += input_tokens
          self.total_output_tokens += output_tokens

      def get_total_cost(self) -> float:
          pricing = self.PRICING.get(self.model, self.PRICING['claude-sonnet-3-5-20241022'])
          input_cost = (self.total_input_tokens / 1000) * pricing['input']
          output_cost = (self.total_output_tokens / 1000) * pricing['output']
          return input_cost + output_cost

      def get_summary(self) -> Dict[str, Any]:
          return {
              'total_input_tokens': self.total_input_tokens,
              'total_output_tokens': self.total_output_tokens,
              'total_cost_usd': self.get_total_cost()
          }
  ```

- [ ] Integrate into ClaudeClient
- [ ] Log costs after each experiment run

**Acceptance Criteria**:
- [ ] Rate limiter prevents API throttling
- [ ] Cost tracker accurate
- [ ] Costs logged and displayed
- [ ] Unit tests for rate limiter and cost tracker

---

### 2.5: Create System Prompt for Coding Agent (1 hour)

**File**: `experiments/prompts.py`

- [ ] Design system prompt
  ```python
  CODING_AGENT_SYSTEM_PROMPT = """You are an expert Python coding assistant helping to solve GitHub issues.

Your task:
1. Understand the issue description and requirements
2. Ask clarifying questions if needed
3. Propose an implementation approach
4. Write clean, well-documented code
5. Include error handling and edge cases
6. Write or update tests as needed

Guidelines:
- Follow PEP 8 style conventions
- Write clear docstrings
- Keep functions focused and modular
- Handle errors gracefully
- Consider performance and maintainability

Output format:
- Explain your approach first
- Provide complete, runnable code
- Include any necessary imports
- Note any assumptions or limitations
"""
  ```

- [ ] Add task-specific prompt templates
- [ ] Document prompt engineering decisions

**Acceptance Criteria**:
- [ ] System prompt written and tested
- [ ] Prompt produces quality code
- [ ] Prompt templates documented

---

### 2.6: Integration Testing (1 hour)

**File**: `tests/test_coding_agent.py`

- [ ] Create integration test suite
  ```python
  import pytest
  from experiments.coding_agent import CodingAgent, ContinuousPrunerStrategy

  @pytest.mark.integration
  class TestCodingAgentIntegration:
      def test_agent_with_continuous_pruning(self):
          """Test agent with continuous pruning strategy"""
          strategy = ContinuousPrunerStrategy(target_tokens=10000)
          agent = CodingAgent(
              context_strategy=strategy,
              llm_config={'model': 'claude-sonnet-3-5-20241022'}
          )

          # Simple coding task
          response = agent.process_message(
              "Write a Python function to check if a number is prime."
          )

          assert response  # Got a response
          assert 'def' in response  # Contains function definition
          assert agent.get_context_stats()['total_tokens'] > 0

      def test_agent_with_baseline_strategy(self):
          """Test agent with discrete baseline strategy"""
          # Similar test with DiscreteBaselineStrategy
          pass

      @pytest.mark.skipif(
          not os.environ.get('ANTHROPIC_API_KEY'),
          reason="API key not available"
      )
      def test_real_api_call(self):
          """Test with real API (only if key available)"""
          pass
  ```

- [ ] Test with mocked API (fast tests)
- [ ] Test with real API (optional, gated by env var)
- [ ] Test error handling paths
- [ ] Test context strategy switching

**Acceptance Criteria**:
- [ ] Integration tests pass
- [ ] Both strategies tested
- [ ] Error handling validated
- [ ] Can run with or without API key

---

## T4.2 Completion Checklist

- [ ] All 6 sub-tasks completed
- [ ] CodingAgent fully functional
- [ ] Claude API integrated with error handling
- [ ] Both context strategies working
- [ ] Rate limiting and cost tracking implemented
- [ ] Integration tests passing
- [ ] Documentation complete

**Deliverables**:
- `experiments/coding_agent.py` (~400 lines)
- `experiments/prompts.py` (~100 lines)
- `tests/test_coding_agent.py` (~150 lines)

---

# T4.3: Experiment 4 Implementation

**Priority**: P0
**Estimated Hours**: 8
**Dependencies**: T4.1 (metrics), T4.2 (agent), Sprint 3 (infrastructure)
**Location**: `experiments/experiment_4_code_quality.py`

## Overview

Implement complete Experiment 4 script that executes SWE-bench Extended tasks with both strategies and collects all metrics.

## Sub-Tasks

### 3.1: Design Experiment Configuration (1 hour)

**File**: `experiments/experiment_4_config.py`

- [ ] Create configuration dataclass
  ```python
  from dataclasses import dataclass
  from typing import List, Optional

  @dataclass
  class Experiment4Config:
      """Configuration for Experiment 4"""

      # Task selection
      task_ids: List[str]  # List of SWE-bench task IDs to run
      num_tasks: int = 50  # Default: 50 tasks

      # Execution
      strategies: List[str] = ('continuous', 'baseline')
      target_tokens: int = 40000
      timeout_per_task: int = 600  # 10 minutes per task

      # LLM configuration
      llm_model: str = 'claude-sonnet-3-5-20241022'
      llm_temperature: float = 0.0
      llm_max_tokens: int = 4096

      # Output
      results_dir: str = 'results/experiment_4'
      checkpoint_interval: int = 5  # Checkpoint every 5 tasks

      # Debugging
      debug_mode: bool = False
      verbose: bool = True
  ```

- [ ] Add configuration validation
- [ ] Add config loading from YAML/JSON
- [ ] Document all configuration options

**Acceptance Criteria**:
- [ ] Configuration class complete
- [ ] Validation implemented
- [ ] Can load from file
- [ ] All options documented

---

### 3.2: Implement Task Execution Loop (2 hours)

**File**: `experiments/experiment_4_code_quality.py`

- [ ] Create main experiment class
  ```python
  import logging
  from pathlib import Path
  from typing import Dict, Any, List

  class Experiment4Runner:
      """Execute Experiment 4: Code Quality Benchmark"""

      def __init__(self, config: Experiment4Config):
          self.config = config
          self.logger = self._setup_logging()
          self.results_dir = Path(config.results_dir)
          self.results_dir.mkdir(parents=True, exist_ok=True)

      def run(self):
          """Run complete experiment"""
          self.logger.info("Starting Experiment 4: Code Quality Benchmark")

          # Load tasks
          tasks = self._load_tasks()
          self.logger.info(f"Loaded {len(tasks)} tasks")

          # Run with each strategy
          all_results = {}
          for strategy_name in self.config.strategies:
              self.logger.info(f"Running with strategy: {strategy_name}")
              results = self._run_strategy(strategy_name, tasks)
              all_results[strategy_name] = results

              # Checkpoint
              self._save_checkpoint(strategy_name, results)

          # Analyze results
          self.logger.info("Analyzing results...")
          analysis = self._analyze_results(all_results)

          # Save final results
          self._save_final_results(all_results, analysis)

          self.logger.info("Experiment 4 complete!")
          return analysis
  ```

- [ ] Implement `_load_tasks()` method
  - Load from SWE-bench data
  - Filter to selected task IDs
  - Validate task data

- [ ] Implement `_run_strategy()` method
  ```python
  def _run_strategy(self, strategy_name: str, tasks: List[Dict]) -> List[Dict]:
      """Run all tasks with a specific strategy"""
      results = []

      for i, task in enumerate(tasks):
          self.logger.info(f"Task {i+1}/{len(tasks)}: {task['id']}")

          try:
              result = self._execute_task(task, strategy_name)
              results.append(result)

              # Checkpoint periodically
              if (i + 1) % self.config.checkpoint_interval == 0:
                  self._save_checkpoint(strategy_name, results)

          except Exception as e:
              self.logger.error(f"Task {task['id']} failed: {e}")
              results.append({
                  'task_id': task['id'],
                  'status': 'error',
                  'error': str(e)
              })

      return results
  ```

- [ ] Implement `_execute_task()` method
  - Initialize agent with strategy
  - Run conversation script
  - Collect generated code
  - Run tests
  - Collect metrics

**Acceptance Criteria**:
- [ ] Experiment runner class implemented
- [ ] Task execution loop working
- [ ] Error handling robust
- [ ] Progress logging clear
- [ ] Checkpointing implemented

---

### 3.3: Implement Checkpointing & Recovery (1 hour)

**File**: `experiments/experiment_4_code_quality.py`

- [ ] Add checkpoint saving
  ```python
  def _save_checkpoint(self, strategy: str, results: List[Dict]):
      """Save checkpoint for recovery"""
      checkpoint_file = self.results_dir / f'checkpoint_{strategy}.json'

      checkpoint_data = {
          'strategy': strategy,
          'completed_tasks': len(results),
          'results': results,
          'timestamp': time.time()
      }

      with open(checkpoint_file, 'w') as f:
          json.dump(checkpoint_data, f, indent=2)

      self.logger.info(f"Checkpoint saved: {len(results)} tasks complete")
  ```

- [ ] Add checkpoint loading
  ```python
  def _load_checkpoint(self, strategy: str) -> Optional[List[Dict]]:
      """Load checkpoint if exists"""
      checkpoint_file = self.results_dir / f'checkpoint_{strategy}.json'

      if not checkpoint_file.exists():
          return None

      with open(checkpoint_file, 'r') as f:
          data = json.load(f)

      self.logger.info(f"Loaded checkpoint: {data['completed_tasks']} tasks")
      return data['results']
  ```

- [ ] Add resume functionality
  ```python
  def _run_strategy(self, strategy_name: str, tasks: List[Dict]) -> List[Dict]:
      # Check for existing checkpoint
      checkpoint_results = self._load_checkpoint(strategy_name)

      if checkpoint_results:
          completed_ids = {r['task_id'] for r in checkpoint_results}
          remaining_tasks = [t for t in tasks if t['id'] not in completed_ids]

          self.logger.info(
              f"Resuming from checkpoint: {len(checkpoint_results)} complete, "
              f"{len(remaining_tasks)} remaining"
          )

          results = checkpoint_results
          tasks = remaining_tasks
      else:
          results = []

      # Continue with remaining tasks...
  ```

**Acceptance Criteria**:
- [ ] Checkpoints saved periodically
- [ ] Can resume from checkpoint
- [ ] No duplicate task execution
- [ ] Checkpoint data validated

---

### 3.4: Implement Metrics Collection (1 hour)

**File**: `experiments/experiment_4_code_quality.py`

- [ ] Integrate MetricsCollector
  ```python
  from experiments.metrics import MetricsCollector

  def _execute_task(self, task: Dict, strategy: str) -> Dict[str, Any]:
      """Execute single task and collect metrics"""
      # Initialize agent
      agent = self._create_agent(strategy)

      # Run task
      generated_code = self._run_conversation(agent, task)

      # Run tests
      test_results = self._run_tests(generated_code, task)

      # Collect all metrics
      metrics_collector = MetricsCollector()

      task_result = {
          'task_id': task['id'],
          'issue_description': task['issue_description'],
          'generated_code': generated_code,
          'tests_passed': test_results['passed'],
          'tests_total': test_results['total'],
          'conversation_history': agent.conversation_history,
          'context_stats': agent.get_context_stats()
      }

      metrics = metrics_collector.collect_all(task_result)

      return {
          'task_id': task['id'],
          'strategy': strategy,
          'metrics': metrics,
          'context_stats': task_result['context_stats'],
          'status': 'success'
      }
  ```

- [ ] Handle metric collection errors gracefully
- [ ] Log metrics after each task

**Acceptance Criteria**:
- [ ] All 4 metrics collected per task
- [ ] Metrics saved with results
- [ ] Error handling for metric failures
- [ ] Metrics logged clearly

---

### 3.5: Implement Progress Tracking (1 hour)

**File**: `experiments/experiment_4_code_quality.py`

- [ ] Add progress bar
  ```python
  from tqdm import tqdm

  def _run_strategy(self, strategy_name: str, tasks: List[Dict]) -> List[Dict]:
      results = []

      # Progress bar
      with tqdm(total=len(tasks), desc=f"{strategy_name} strategy") as pbar:
          for i, task in enumerate(tasks):
              result = self._execute_task(task, strategy_name)
              results.append(result)

              # Update progress bar with metrics
              if result['status'] == 'success':
                  completion_rate = result['metrics']['task_completion_rate']
                  pbar.set_postfix(completion=f"{completion_rate:.1%}")

              pbar.update(1)

      return results
  ```

- [ ] Add time estimation
  ```python
  import time

  class TimeEstimator:
      """Estimate time remaining for experiment"""

      def __init__(self, total_tasks: int):
          self.total_tasks = total_tasks
          self.completed = 0
          self.start_time = time.time()
          self.task_times = []

      def record_task(self, duration: float):
          self.task_times.append(duration)
          self.completed += 1

      def get_eta(self) -> float:
          """Estimate time remaining in seconds"""
          if not self.task_times:
              return 0

          avg_time = sum(self.task_times) / len(self.task_times)
          remaining_tasks = self.total_tasks - self.completed
          return avg_time * remaining_tasks

      def format_eta(self) -> str:
          """Format ETA as human-readable string"""
          eta_seconds = self.get_eta()
          hours = int(eta_seconds // 3600)
          minutes = int((eta_seconds % 3600) // 60)
          return f"{hours}h {minutes}m remaining"
  ```

- [ ] Log progress regularly
- [ ] Display summary statistics

**Acceptance Criteria**:
- [ ] Progress bar shows task completion
- [ ] Time estimation accurate
- [ ] Summary stats displayed
- [ ] Logging clear and informative

---

### 3.6: Implement Command-Line Interface (1 hour)

**File**: `experiments/experiment_4_code_quality.py`

- [ ] Add CLI with argparse
  ```python
  import argparse

  def main():
      parser = argparse.ArgumentParser(
          description="Run Experiment 4: Code Quality Benchmark"
      )

      parser.add_argument(
          '--config',
          type=str,
          default='experiments/experiment_4_config.yaml',
          help='Path to configuration file'
      )

      parser.add_argument(
          '--tasks',
          type=int,
          default=50,
          help='Number of tasks to run (default: 50)'
      )

      parser.add_argument(
          '--strategies',
          nargs='+',
          default=['continuous', 'baseline'],
          choices=['continuous', 'baseline', 'control'],
          help='Strategies to test'
      )

      parser.add_argument(
          '--resume',
          action='store_true',
          help='Resume from last checkpoint'
      )

      parser.add_argument(
          '--debug',
          action='store_true',
          help='Enable debug mode'
      )

      args = parser.parse_args()

      # Load config
      if Path(args.config).exists():
          config = Experiment4Config.from_yaml(args.config)
      else:
          config = Experiment4Config()

      # Override with CLI args
      config.num_tasks = args.tasks
      config.strategies = args.strategies
      config.debug_mode = args.debug

      # Run experiment
      runner = Experiment4Runner(config)
      results = runner.run()

      # Print summary
      print("\n" + "="*70)
      print("EXPERIMENT 4 COMPLETE")
      print("="*70)
      print(runner.format_summary(results))

  if __name__ == '__main__':
      main()
  ```

- [ ] Add usage examples in docstring
- [ ] Add help text for all options

**Acceptance Criteria**:
- [ ] CLI arguments work correctly
- [ ] Config file loading works
- [ ] Help text clear and complete
- [ ] Can run from command line

---

### 3.7: Integration Testing (1 hour)

**File**: `tests/test_experiment_4.py`

- [ ] Create test suite
  ```python
  import pytest
  from experiments.experiment_4_code_quality import Experiment4Runner
  from experiments.experiment_4_config import Experiment4Config

  class TestExperiment4:
      def test_config_creation(self):
          """Test configuration creation"""
          config = Experiment4Config(num_tasks=5)
          assert config.num_tasks == 5

      @pytest.mark.integration
      def test_small_experiment(self):
          """Test running experiment with 2 tasks"""
          config = Experiment4Config(
              num_tasks=2,
              task_ids=['test_task_1', 'test_task_2'],
              strategies=['continuous']
          )

          runner = Experiment4Runner(config)
          # Mock task loader to return test tasks
          # Run experiment
          # Validate results structure

      def test_checkpoint_save_load(self):
          """Test checkpoint saving and loading"""
          # Create checkpoint
          # Load checkpoint
          # Verify data matches
  ```

- [ ] Test checkpoint functionality
- [ ] Test resume functionality
- [ ] Test error handling

**Acceptance Criteria**:
- [ ] Unit tests pass
- [ ] Integration tests pass (with small task set)
- [ ] Can run mini-experiment end-to-end
- [ ] Error scenarios handled

---

## T4.3 Completion Checklist

- [ ] All 7 sub-tasks completed
- [ ] Experiment script fully functional
- [ ] Can execute tasks with both strategies
- [ ] Checkpointing and resume working
- [ ] Metrics collection integrated
- [ ] Progress tracking clear
- [ ] CLI working
- [ ] Tests passing

**Deliverables**:
- `experiments/experiment_4_code_quality.py` (~500 lines)
- `experiments/experiment_4_config.py` (~100 lines)
- `tests/test_experiment_4.py` (~200 lines)

---

# T4.4: Execute Experiment - Continuous Pruning

**Priority**: P0
**Estimated Hours**: 6 (execution time)
**Dependencies**: T4.3
**Location**: N/A (execution task)

## Overview

Execute Experiment 4 with continuous pruning strategy on all 50 tasks.

## Sub-Tasks

### 4.1: Pre-Execution Validation (0.5 hours)

- [ ] Verify API key is set
  ```bash
  echo $ANTHROPIC_API_KEY  # Should be non-empty
  ```

- [ ] Run mini experiment (2 tasks) to validate setup
  ```bash
  python experiments/experiment_4_code_quality.py \
    --tasks 2 \
    --strategies continuous \
    --debug
  ```

- [ ] Check results directory structure
- [ ] Verify metrics are being collected
- [ ] Verify checkpoints are being saved

**Acceptance Criteria**:
- [ ] Mini experiment completes successfully
- [ ] All metrics collected
- [ ] Checkpoints saved
- [ ] No errors or warnings

---

### 4.2: Execute Full Experiment - Continuous (5 hours)

- [ ] Start execution
  ```bash
  # Set up logging
  export EXPERIMENT_LOG="logs/experiment_4_continuous_$(date +%Y%m%d_%H%M%S).log"

  # Run experiment
  python experiments/experiment_4_code_quality.py \
    --tasks 50 \
    --strategies continuous \
    --verbose 2>&1 | tee $EXPERIMENT_LOG
  ```

- [ ] Monitor progress
  - Check log file regularly
  - Verify checkpoints being created
  - Monitor API costs
  - Watch for errors

- [ ] Handle interruptions
  - If interrupted, resume with `--resume` flag
  - Verify no duplicate task execution

**Execution Checklist**:
- [ ] Execution started (log timestamp)
- [ ] 10 tasks complete (checkpoint)
- [ ] 20 tasks complete (checkpoint)
- [ ] 30 tasks complete (checkpoint)
- [ ] 40 tasks complete (checkpoint)
- [ ] 50 tasks complete (final)
- [ ] No errors encountered
- [ ] All results saved

**Acceptance Criteria**:
- [ ] All 50 tasks executed successfully
- [ ] No execution failures
- [ ] All metrics collected for each task
- [ ] Results saved in structured format
- [ ] Execution time logged
- [ ] API costs tracked and logged

---

### 4.3: Validate Results (0.5 hours)

- [ ] Check results completeness
  ```python
  import json

  # Load results
  with open('results/experiment_4/continuous_final.json') as f:
      results = json.load(f)

  # Validate
  assert len(results) == 50, "Not all tasks completed"

  for result in results:
      assert 'metrics' in result
      assert 'task_completion_rate' in result['metrics']
      assert 'specification_adherence' in result['metrics']
      assert 'code_quality_score' in result['metrics']
      assert 'implementation_consistency' in result['metrics']
  ```

- [ ] Verify no missing data
- [ ] Check for any error statuses
- [ ] Quick sanity check on metrics (reasonable ranges)

**Acceptance Criteria**:
- [ ] All 50 results present
- [ ] No missing metrics
- [ ] No error statuses (or documented if any)
- [ ] Data structure valid

---

## T4.4 Completion Checklist

- [ ] Pre-execution validation passed
- [ ] Full experiment executed (50 tasks)
- [ ] Results validated
- [ ] Execution time logged
- [ ] API costs documented
- [ ] Results backed up

**Deliverables**:
- `results/experiment_4/continuous_final.json`
- `logs/experiment_4_continuous_*.log`
- Execution summary (time, cost, completion rate)

---

# T4.5: Execute Experiment - Discrete Baseline

**Priority**: P0
**Estimated Hours**: 6 (execution time)
**Dependencies**: T4.3
**Location**: N/A (execution task)

## Overview

Execute Experiment 4 with discrete compaction baseline on all 50 tasks (same tasks as continuous).

## Sub-Tasks

### 5.1: Pre-Execution Validation (0.5 hours)

- [ ] Use SAME 50 tasks as continuous pruning (fair comparison)
  ```bash
  # Extract task IDs from continuous results
  python -c "
  import json
  with open('results/experiment_4/continuous_final.json') as f:
      results = json.load(f)
  task_ids = [r['task_id'] for r in results]
  with open('results/experiment_4/task_ids.json', 'w') as f:
      json.dump(task_ids, f)
  "
  ```

- [ ] Run mini experiment (2 tasks) with baseline
  ```bash
  python experiments/experiment_4_code_quality.py \
    --tasks 2 \
    --strategies baseline \
    --debug
  ```

- [ ] Verify baseline strategy working correctly
- [ ] Check compaction events are being triggered

**Acceptance Criteria**:
- [ ] Using same task IDs as continuous
- [ ] Mini experiment passes
- [ ] Baseline compaction working
- [ ] Metrics collected correctly

---

### 5.2: Execute Full Experiment - Baseline (5 hours)

- [ ] Start execution
  ```bash
  # Set up logging
  export EXPERIMENT_LOG="logs/experiment_4_baseline_$(date +%Y%m%d_%H%M%S).log"

  # Run experiment with same task IDs
  python experiments/experiment_4_code_quality.py \
    --task-ids results/experiment_4/task_ids.json \
    --strategies baseline \
    --verbose 2>&1 | tee $EXPERIMENT_LOG
  ```

- [ ] Monitor progress (same as T4.4)
- [ ] Handle interruptions (resume with --resume)

**Execution Checklist**:
- [ ] Execution started (log timestamp)
- [ ] 10 tasks complete (checkpoint)
- [ ] 20 tasks complete (checkpoint)
- [ ] 30 tasks complete (checkpoint)
- [ ] 40 tasks complete (checkpoint)
- [ ] 50 tasks complete (final)
- [ ] No errors encountered
- [ ] All results saved

**Acceptance Criteria**:
- [ ] All 50 tasks executed successfully (SAME tasks as continuous)
- [ ] No execution failures
- [ ] All metrics collected
- [ ] Results saved
- [ ] Execution time logged
- [ ] API costs tracked

---

### 5.3: Validate Results (0.5 hours)

- [ ] Check results completeness (same validation as T4.4)
- [ ] Verify same tasks executed as continuous
- [ ] Compare execution times (should be similar)

**Acceptance Criteria**:
- [ ] All 50 results present
- [ ] Same task IDs as continuous experiment
- [ ] No missing metrics
- [ ] Data structure valid

---

## T4.5 Completion Checklist

- [ ] Pre-execution validation passed
- [ ] Full experiment executed (50 tasks, SAME as continuous)
- [ ] Results validated
- [ ] Execution time logged
- [ ] API costs documented
- [ ] Results backed up

**Deliverables**:
- `results/experiment_4/baseline_final.json`
- `logs/experiment_4_baseline_*.log`
- Execution summary

---

# T4.6: Preliminary Analysis

**Priority**: P0
**Estimated Hours**: 8
**Dependencies**: T4.4, T4.5
**Location**: `experiments/experiment_4_analysis.py`

## Overview

Perform comparative analysis of continuous pruning vs. discrete baseline results.

## Sub-Tasks

### 6.1: Load and Prepare Data (1 hour)

**File**: `experiments/experiment_4_analysis.py`

- [ ] Create analysis script
  ```python
  import json
  import pandas as pd
  import numpy as np
  from pathlib import Path

  class Experiment4Analyzer:
      """Analyze Experiment 4 results"""

      def __init__(self, results_dir: str = 'results/experiment_4'):
          self.results_dir = Path(results_dir)
          self.continuous_data = None
          self.baseline_data = None

      def load_results(self):
          """Load results from both strategies"""
          with open(self.results_dir / 'continuous_final.json') as f:
              continuous_results = json.load(f)

          with open(self.results_dir / 'baseline_final.json') as f:
              baseline_results = json.load(f)

          # Convert to DataFrames
          self.continuous_data = self._to_dataframe(continuous_results, 'continuous')
          self.baseline_data = self._to_dataframe(baseline_results, 'baseline')

          # Merge for comparison
          self.merged_data = pd.merge(
              self.continuous_data,
              self.baseline_data,
              on='task_id',
              suffixes=('_continuous', '_baseline')
          )

      def _to_dataframe(self, results: List[Dict], strategy: str) -> pd.DataFrame:
          """Convert results to DataFrame"""
          rows = []
          for result in results:
              row = {
                  'task_id': result['task_id'],
                  'strategy': strategy,
                  **result['metrics']
              }
              rows.append(row)
          return pd.DataFrame(rows)
  ```

- [ ] Validate data consistency
  - Same task IDs in both datasets
  - All metrics present
  - No missing values

**Acceptance Criteria**:
- [ ] Data loaded successfully
- [ ] DataFrames created
- [ ] Data validated (same tasks, complete metrics)

---

### 6.2: Statistical Comparison (2 hours)

**File**: `experiments/experiment_4_analysis.py`

- [ ] Implement comparison methods
  ```python
  from scipy import stats

  class Experiment4Analyzer:
      def compare_metrics(self) -> Dict[str, Any]:
          """Compare metrics between strategies"""
          metrics = [
              'task_completion_rate',
              'specification_adherence',
              'code_quality_score',
              'implementation_consistency'
          ]

          comparisons = {}

          for metric in metrics:
              continuous_vals = self.merged_data[f'{metric}_continuous']
              baseline_vals = self.merged_data[f'{metric}_baseline']

              # Descriptive statistics
              comparison = {
                  'continuous': {
                      'mean': continuous_vals.mean(),
                      'std': continuous_vals.std(),
                      'median': continuous_vals.median(),
                      'min': continuous_vals.min(),
                      'max': continuous_vals.max()
                  },
                  'baseline': {
                      'mean': baseline_vals.mean(),
                      'std': baseline_vals.std(),
                      'median': baseline_vals.median(),
                      'min': baseline_vals.min(),
                      'max': baseline_vals.max()
                  },
                  'difference': {
                      'absolute': continuous_vals.mean() - baseline_vals.mean(),
                      'relative': ((continuous_vals.mean() - baseline_vals.mean())
                                   / baseline_vals.mean() * 100)
                  }
              }

              # Statistical significance (paired t-test)
              t_stat, p_value = stats.ttest_rel(continuous_vals, baseline_vals)
              comparison['statistical_test'] = {
                  't_statistic': t_stat,
                  'p_value': p_value,
                  'significant': p_value < 0.05
              }

              comparisons[metric] = comparison

          return comparisons
  ```

- [ ] Calculate effect sizes (Cohen's d)
  ```python
  def cohens_d(self, x1, x2):
      """Calculate Cohen's d effect size"""
      n1, n2 = len(x1), len(x2)
      var1, var2 = np.var(x1, ddof=1), np.var(x2, ddof=1)
      pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
      return (np.mean(x1) - np.mean(x2)) / pooled_std
  ```

- [ ] Validate acceptance criteria
  ```python
  def check_acceptance_criteria(self, comparisons: Dict) -> Dict[str, bool]:
      """Check if acceptance criteria are met"""
      criteria = {}

      # Criterion 1: Task completion ≥90% of baseline
      completion_ratio = (comparisons['task_completion_rate']['continuous']['mean'] /
                         comparisons['task_completion_rate']['baseline']['mean'])
      criteria['task_completion'] = completion_ratio >= 0.90

      # Criterion 2: Spec adherence ≥95% of baseline
      adherence_ratio = (comparisons['specification_adherence']['continuous']['mean'] /
                        comparisons['specification_adherence']['baseline']['mean'])
      criteria['spec_adherence'] = adherence_ratio >= 0.95

      # Criterion 3: Code quality ≥ baseline
      quality_diff = (comparisons['code_quality_score']['continuous']['mean'] -
                     comparisons['code_quality_score']['baseline']['mean'])
      criteria['code_quality'] = quality_diff >= 0

      # Overall: ≥2 of 3 must pass
      criteria['overall_pass'] = sum(criteria.values()) >= 2

      return criteria
  ```

**Acceptance Criteria**:
- [ ] Descriptive stats calculated for all metrics
- [ ] Statistical tests performed
- [ ] Effect sizes calculated
- [ ] Acceptance criteria validated
- [ ] Results structured for reporting

---

### 6.3: Create Visualizations (3 hours)

**File**: `experiments/experiment_4_analysis.py`

- [ ] Implement visualization methods
  ```python
  import matplotlib.pyplot as plt
  import seaborn as sns

  class Experiment4Analyzer:
      def create_visualizations(self, output_dir: Path):
          """Generate all visualizations"""
          output_dir.mkdir(parents=True, exist_ok=True)

          # 1. Bar chart comparison
          self._plot_metric_comparison(output_dir)

          # 2. Box plots for distributions
          self._plot_distributions(output_dir)

          # 3. Scatter plots for correlation
          self._plot_correlations(output_dir)

          # 4. Summary dashboard
          self._plot_summary_dashboard(output_dir)
  ```

- [ ] Create bar chart comparison
  ```python
  def _plot_metric_comparison(self, output_dir: Path):
      """Bar chart comparing metrics"""
      metrics = ['task_completion_rate', 'specification_adherence',
                'code_quality_score', 'implementation_consistency']

      fig, axes = plt.subplots(2, 2, figsize=(12, 10))
      axes = axes.flatten()

      for i, metric in enumerate(metrics):
          ax = axes[i]

          continuous_mean = self.merged_data[f'{metric}_continuous'].mean()
          baseline_mean = self.merged_data[f'{metric}_baseline'].mean()

          x = ['Continuous\nPruning', 'Discrete\nBaseline']
          y = [continuous_mean, baseline_mean]

          bars = ax.bar(x, y, color=['#2ecc71', '#e74c3c'])
          ax.set_ylabel('Score')
          ax.set_title(metric.replace('_', ' ').title())
          ax.set_ylim(0, 1.1)

          # Add value labels
          for bar in bars:
              height = bar.get_height()
              ax.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.3f}',
                     ha='center', va='bottom')

      plt.tight_layout()
      plt.savefig(output_dir / 'metric_comparison.png', dpi=300, bbox_inches='tight')
      plt.close()
  ```

- [ ] Create box plots
  ```python
  def _plot_distributions(self, output_dir: Path):
      """Box plots showing distributions"""
      metrics = ['task_completion_rate', 'specification_adherence',
                'code_quality_score', 'implementation_consistency']

      fig, axes = plt.subplots(2, 2, figsize=(12, 10))
      axes = axes.flatten()

      for i, metric in enumerate(metrics):
          ax = axes[i]

          data_to_plot = [
              self.merged_data[f'{metric}_continuous'],
              self.merged_data[f'{metric}_baseline']
          ]

          bp = ax.boxplot(data_to_plot, labels=['Continuous', 'Baseline'],
                         patch_artist=True)

          # Color boxes
          bp['boxes'][0].set_facecolor('#2ecc71')
          bp['boxes'][1].set_facecolor('#e74c3c')

          ax.set_ylabel('Score')
          ax.set_title(metric.replace('_', ' ').title())
          ax.grid(axis='y', alpha=0.3)

      plt.tight_layout()
      plt.savefig(output_dir / 'distributions.png', dpi=300, bbox_inches='tight')
      plt.close()
  ```

- [ ] Create scatter plot for correlation
  ```python
  def _plot_correlations(self, output_dir: Path):
      """Scatter plots showing correlations"""
      fig, axes = plt.subplots(2, 2, figsize=(12, 10))
      axes = axes.flatten()

      metrics = ['task_completion_rate', 'specification_adherence',
                'code_quality_score', 'implementation_consistency']

      for i, metric in enumerate(metrics):
          ax = axes[i]

          x = self.merged_data[f'{metric}_baseline']
          y = self.merged_data[f'{metric}_continuous']

          ax.scatter(x, y, alpha=0.6)

          # Add diagonal line (y=x)
          lims = [0, 1]
          ax.plot(lims, lims, 'k--', alpha=0.3, label='y=x')

          ax.set_xlabel('Baseline Score')
          ax.set_ylabel('Continuous Pruning Score')
          ax.set_title(metric.replace('_', ' ').title())
          ax.legend()
          ax.grid(alpha=0.3)

      plt.tight_layout()
      plt.savefig(output_dir / 'correlations.png', dpi=300, bbox_inches='tight')
      plt.close()
  ```

- [ ] Create summary dashboard
  ```python
  def _plot_summary_dashboard(self, output_dir: Path):
      """Single-page summary dashboard"""
      fig = plt.figure(figsize=(16, 10))
      gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

      # Top: Acceptance criteria status
      ax_criteria = fig.add_subplot(gs[0, :])
      self._plot_acceptance_criteria(ax_criteria)

      # Middle: Metric comparison bars
      ax_bars = fig.add_subplot(gs[1, :])
      self._plot_all_metrics_bar(ax_bars)

      # Bottom left: Task completion distribution
      ax_completion = fig.add_subplot(gs[2, 0])
      # ... plot completion distribution

      # Bottom middle: Context stats
      ax_context = fig.add_subplot(gs[2, 1])
      # ... plot context usage

      # Bottom right: Cost comparison
      ax_cost = fig.add_subplot(gs[2, 2])
      # ... plot API costs

      plt.savefig(output_dir / 'summary_dashboard.png', dpi=300, bbox_inches='tight')
      plt.close()
  ```

**Acceptance Criteria**:
- [ ] All 4 visualization types created
- [ ] Charts clear and readable
- [ ] Figures saved at high resolution
- [ ] Summary dashboard comprehensive

---

### 6.4: Generate Analysis Report (1 hour)

**File**: `results/experiment_4/preliminary_analysis.md`

- [ ] Create markdown report
  ```python
  def generate_report(self, comparisons: Dict, criteria: Dict, output_file: Path):
      """Generate markdown analysis report"""
      report = f"""# Experiment 4: Preliminary Analysis

## Executive Summary

**Experiment**: Code Quality Benchmark (SWE-bench Extended)
**Tasks**: 50 coding tasks
**Strategies**: Continuous Pruning vs. Discrete Baseline
**Date**: {datetime.now().strftime('%Y-%m-%d')}

## Acceptance Criteria Status

"""

      # Add criteria status
      for criterion, passed in criteria.items():
          status = "✅ PASS" if passed else "❌ FAIL"
          report += f"- {criterion}: {status}\n"

      report += f"\n**Overall**: {'✅ SUCCESS' if criteria['overall_pass'] else '❌ NEEDS ITERATION'}\n\n"

      # Add detailed metrics
      report += "## Detailed Metrics Comparison\n\n"

      for metric, data in comparisons.items():
          report += f"### {metric.replace('_', ' ').title()}\n\n"
          report += f"| Strategy | Mean | Std | Median | Min | Max |\n"
          report += f"|----------|------|-----|--------|-----|-----|\n"
          report += f"| Continuous | {data['continuous']['mean']:.3f} | {data['continuous']['std']:.3f} | {data['continuous']['median']:.3f} | {data['continuous']['min']:.3f} | {data['continuous']['max']:.3f} |\n"
          report += f"| Baseline | {data['baseline']['mean']:.3f} | {data['baseline']['std']:.3f} | {data['baseline']['median']:.3f} | {data['baseline']['min']:.3f} | {data['baseline']['max']:.3f} |\n"
          report += f"\n**Difference**: {data['difference']['absolute']:+.3f} ({data['difference']['relative']:+.1f}%)\n"
          report += f"**Statistical Significance**: p={data['statistical_test']['p_value']:.4f} ({'significant' if data['statistical_test']['significant'] else 'not significant'})\n\n"

      # Add visualizations section
      report += "## Visualizations\n\n"
      report += "![Metric Comparison](metric_comparison.png)\n\n"
      report += "![Distributions](distributions.png)\n\n"
      report += "![Summary Dashboard](summary_dashboard.png)\n\n"

      # Add next steps
      report += "## Next Steps\n\n"
      if criteria['overall_pass']:
          report += "- ✅ Proceed to Sprint 5 (Additional Experiments)\n"
          report += "- Continue to comprehensive analysis\n"
      else:
          report += "- ⚠️ Review failure modes\n"
          report += "- Consider algorithm adjustments\n"
          report += "- Re-run experiment or pivot approach\n"

      # Write report
      with open(output_file, 'w') as f:
          f.write(report)
  ```

**Acceptance Criteria**:
- [ ] Report generated in markdown
- [ ] All metrics documented
- [ ] Acceptance criteria status clear
- [ ] Visualizations embedded
- [ ] Next steps outlined

---

### 6.5: Run Complete Analysis (1 hour)

**File**: `experiments/run_analysis.py`

- [ ] Create analysis runner script
  ```python
  #!/usr/bin/env python3
  """Run complete Experiment 4 analysis"""

  from pathlib import Path
  from experiment_4_analysis import Experiment4Analyzer

  def main():
      print("="*70)
      print("EXPERIMENT 4: PRELIMINARY ANALYSIS")
      print("="*70)

      # Initialize analyzer
      analyzer = Experiment4Analyzer(results_dir='results/experiment_4')

      # Load data
      print("\n1. Loading results...")
      analyzer.load_results()
      print(f"   Loaded {len(analyzer.merged_data)} tasks")

      # Statistical comparison
      print("\n2. Computing statistical comparisons...")
      comparisons = analyzer.compare_metrics()

      # Check acceptance criteria
      print("\n3. Validating acceptance criteria...")
      criteria = analyzer.check_acceptance_criteria(comparisons)

      # Print criteria status
      print("\n   Acceptance Criteria:")
      for criterion, passed in criteria.items():
          status = "✅ PASS" if passed else "❌ FAIL"
          print(f"   - {criterion}: {status}")

      # Create visualizations
      print("\n4. Generating visualizations...")
      output_dir = Path('results/experiment_4/analysis')
      analyzer.create_visualizations(output_dir)
      print(f"   Saved to {output_dir}")

      # Generate report
      print("\n5. Creating analysis report...")
      analyzer.generate_report(
          comparisons,
          criteria,
          output_dir / 'preliminary_analysis.md'
      )

      # Final summary
      print("\n" + "="*70)
      if criteria['overall_pass']:
          print("✅ EXPERIMENT 4: SUCCESS")
          print("   Proceed to Sprint 5")
      else:
          print("⚠️ EXPERIMENT 4: NEEDS ITERATION")
          print("   Review findings and decide on next steps")
      print("="*70)

  if __name__ == '__main__':
      main()
  ```

- [ ] Run analysis
  ```bash
  python experiments/run_analysis.py
  ```

- [ ] Review outputs
- [ ] Verify all artifacts created

**Acceptance Criteria**:
- [ ] Analysis runs without errors
- [ ] All outputs generated
- [ ] Results clearly presented
- [ ] Decision recommendation clear

---

## T4.6 Completion Checklist

- [ ] All 5 sub-tasks completed
- [ ] Statistical analysis complete
- [ ] Visualizations generated (4 types)
- [ ] Preliminary report written
- [ ] Acceptance criteria validated
- [ ] Go/no-go recommendation clear

**Deliverables**:
- `experiments/experiment_4_analysis.py` (~500 lines)
- `experiments/run_analysis.py` (~100 lines)
- `results/experiment_4/analysis/preliminary_analysis.md`
- `results/experiment_4/analysis/*.png` (4+ visualizations)
- Statistical comparison data (JSON/CSV)

---

# T4.7: Documentation & Sprint Review

**Priority**: P0
**Estimated Hours**: 4
**Dependencies**: T4.6
**Location**: Various documentation files

## Overview

Document Experiment 4 implementation, results, and findings. Prepare sprint demo and update project documentation.

## Sub-Tasks

### 7.1: Update README (0.5 hours)

**File**: `README.md`

- [ ] Update Sprint 4 status to COMPLETE
- [ ] Add Experiment 4 results summary
- [ ] Update progress indicators
- [ ] Add link to detailed analysis

**Acceptance Criteria**:
- [ ] README updated with Sprint 4 completion
- [ ] Results summary added
- [ ] Links to detailed docs working

---

### 7.2: Create Sprint 4 Summary (1.5 hours)

**File**: `SPRINT_4_SUMMARY.md`

- [ ] Create comprehensive sprint summary
  ```markdown
  # Sprint 4 Summary: Code Quality Benchmark

  **Sprint Duration**: Week 7-8
  **Status**: ✅ COMPLETE
  **Date**: YYYY-MM-DD

  ## Executive Summary

  Sprint 4 successfully executed the primary validation experiment...

  ## Completed Tasks

  ### T4.1: Code Quality Metrics (12 hours)
  - Implemented 4 metrics...

  ### T4.2: Real Agent Integration (10 hours)
  - Integrated Claude API...

  ...

  ## Results

  ### Acceptance Criteria Status

  | Criterion | Target | Result | Status |
  |-----------|--------|--------|--------|
  | Task Completion | ≥90% of baseline | X% | ✅/❌ |
  ...

  ## Key Findings

  1. ...
  2. ...

  ## Lessons Learned

  ### What Worked Well
  - ...

  ### Challenges
  - ...

  ## Next Steps

  - Sprint 5: Additional experiments
  - ...
  ```

- [ ] Include all task summaries
- [ ] Document results and findings
- [ ] Add lessons learned
- [ ] Outline next steps

**Acceptance Criteria**:
- [ ] Sprint summary complete
- [ ] All tasks documented
- [ ] Results clearly presented
- [ ] Lessons learned captured

---

### 7.3: Update Technical Documentation (1 hour)

**Files**: Various

- [ ] Update `experiments/README.md`
  - Add Experiment 4 documentation
  - Explain how to run experiment
  - Document analysis process

- [ ] Update `docs/QUICK_START_GUIDE.md` if needed

- [ ] Add inline documentation to code
  - Docstrings complete
  - Complex logic explained
  - Usage examples added

- [ ] Document known limitations
  - API rate limits
  - Timeout issues
  - Edge cases

**Acceptance Criteria**:
- [ ] All documentation updated
- [ ] Usage instructions clear
- [ ] Known issues documented
- [ ] Examples provided

---

### 7.4: Prepare Sprint Demo (0.5 hours)

**File**: `SPRINT_4_DEMO.md`

- [ ] Create demo script
  ```markdown
  # Sprint 4 Demo: Code Quality Benchmark

  ## Demo Outline

  1. **Quick Recap** (2 min)
     - Sprint 4 goal: Validate continuous pruning on real coding tasks
     - Primary validation experiment

  2. **Implementation Overview** (3 min)
     - 4 code quality metrics
     - Real LLM agent integration
     - 50 task execution

  3. **Results Walkthrough** (10 min)
     - Show summary dashboard
     - Explain key metrics
     - Present acceptance criteria status
     - Discuss statistical significance

  4. **Key Findings** (3 min)
     - What worked well
     - Unexpected results
     - Implications for hypothesis

  5. **Go/No-Go Decision** (2 min)
     - Recommendation for Phase I continuation
     - Next steps (Sprint 5)

  ## Demo Artifacts

  - Summary dashboard (visualization)
  - Preliminary analysis report
  - Sample task execution (walkthrough)
  - Cost and time summary
  ```

- [ ] Prepare visualizations for presentation
- [ ] Rehearse demo flow
- [ ] Prepare Q&A responses

**Acceptance Criteria**:
- [ ] Demo script prepared
- [ ] Visualizations ready
- [ ] Demo rehearsed
- [ ] Q&A anticipated

---

### 7.5: Code Review & Cleanup (0.5 hours)

- [ ] Self-review all Sprint 4 code
  - Check style consistency (PEP 8)
  - Verify all docstrings present
  - Remove debugging code
  - Clean up commented code

- [ ] Run code quality checks
  ```bash
  # Format code
  black experiments/*.py

  # Lint
  flake8 experiments/*.py --max-line-length=100

  # Type check
  mypy experiments/*.py
  ```

- [ ] Run all tests
  ```bash
  pytest tests/test_metrics.py tests/test_coding_agent.py tests/test_experiment_4.py -v
  ```

- [ ] Update requirements.txt if needed

**Acceptance Criteria**:
- [ ] Code reviewed and cleaned
- [ ] Style consistent
- [ ] All tests passing
- [ ] Quality checks passing

---

## T4.7 Completion Checklist

- [ ] All 5 sub-tasks completed
- [ ] README updated
- [ ] Sprint 4 summary written
- [ ] Technical docs updated
- [ ] Sprint demo prepared
- [ ] Code reviewed and cleaned
- [ ] All tests passing
- [ ] Sprint 4 officially complete

**Deliverables**:
- Updated `README.md`
- `SPRINT_4_SUMMARY.md`
- Updated technical documentation
- `SPRINT_4_DEMO.md`
- Clean, tested code

---

# Sprint 4 Final Checklist

## All Tasks Complete

- [ ] T4.1: Code Quality Metrics (12 hours) ✅
- [ ] T4.2: Real Agent Integration (10 hours) ✅
- [ ] T4.3: Experiment 4 Implementation (8 hours) ✅
- [ ] T4.4: Execute - Continuous Pruning (6 hours) ✅
- [ ] T4.5: Execute - Discrete Baseline (6 hours) ✅
- [ ] T4.6: Preliminary Analysis (8 hours) ✅
- [ ] T4.7: Documentation & Review (4 hours) ✅

## Critical Deliverables

- [ ] All 4 metrics implemented and tested
- [ ] Real LLM agent functional with both strategies
- [ ] 100 task executions completed (50 × 2 strategies)
- [ ] Comparative analysis complete
- [ ] Acceptance criteria validated (≥2 of 3 passed)
- [ ] Visualizations generated
- [ ] Preliminary report written
- [ ] Sprint 4 summary documented

## Quality Gates

- [ ] All unit tests passing (>95% coverage)
- [ ] Integration tests passing
- [ ] Code reviewed and clean
- [ ] Documentation complete and accurate
- [ ] API costs within budget (<$50)
- [ ] Results reproducible

## Go/No-Go Decision

Based on acceptance criteria results:

- [ ] **GO**: ≥2 of 3 criteria met → Proceed to Sprint 5
- [ ] **ITERATE**: Mixed results → Analyze and adjust (2-3 weeks)
- [ ] **NO-GO**: Clear failure → Pivot or halt

**Decision**: ____________

**Rationale**: ____________

---

# Sprint 4 Success Metrics

## Primary Metrics (Acceptance Criteria)

| Metric | Target | Result | Status |
|--------|--------|--------|--------|
| Task Completion Rate | ≥90% of baseline | ___% | ☐ |
| Specification Adherence | ≥95% of baseline | ___% | ☐ |
| Code Quality Score | ≥ baseline | ___pts | ☐ |
| **Overall** | **≥2 of 3 pass** | **___ of 3** | **☐** |

## Secondary Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Execution Time | <3 days | ___ hours |
| API Cost | <$50 | $___ |
| Test Coverage | >95% | ___% |
| Task Completion % | 100% | ___% |

## Phase I Progress

- Sprint 1: ✅ COMPLETE (Adaptive Pruning)
- Sprint 2: ✅ COMPLETE (CORE Budget & Baseline)
- Sprint 3: ⚠️ PRELIMINARY (Needs Sprint 4 validation)
- Sprint 4: ☐ COMPLETE (Primary Validation)
- Sprint 5: ☐ PENDING (Additional Experiments)
- Sprint 6: ☐ PENDING (Analysis & Reporting)

**Phase I Completion**: ___%

---

# Appendix: Troubleshooting Guide

## Common Issues

### Issue: API Rate Limiting

**Symptoms**: 429 errors, slow execution

**Solutions**:
- Verify rate limiter configured correctly
- Increase backoff delay
- Use multiple API keys (if available)
- Reduce parallelism

### Issue: Test Execution Timeouts

**Symptoms**: Tasks failing due to test timeouts

**Solutions**:
- Increase timeout limit in config
- Optimize test execution
- Skip very slow tests (document)

### Issue: Memory Issues

**Symptoms**: Out of memory errors during execution

**Solutions**:
- Reduce batch size
- Clear context more aggressively
- Run on machine with more RAM
- Process tasks sequentially

### Issue: Checkpoint Corruption

**Symptoms**: Cannot resume from checkpoint

**Solutions**:
- Validate checkpoint before loading
- Keep backup checkpoints
- Re-run from last valid checkpoint

### Issue: Metrics Collection Failures

**Symptoms**: Missing metrics in results

**Solutions**:
- Check metric implementation
- Add fallback values
- Log metric errors separately
- Validate data structure

---

**End of Sprint 4 Implementation Checklist**

**Next Sprint**: Sprint 5 (Additional Experiments & Comprehensive Metrics)
**Timeline**: Week 9-10
**Status**: Blocked until Sprint 4 Go/No-Go decision

---

**Document Version**: 1.0
**Created**: 2025-01-03
**Last Updated**: 2025-01-03
