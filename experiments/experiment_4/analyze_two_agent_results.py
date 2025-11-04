#!/usr/bin/env python3
"""
Statistical analysis script for two-agent experiment results.
Compares continuous_pruning vs discrete_baseline strategies.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class TaskResult:
    """Result for a single task execution."""
    task_id: str
    strategy: str
    success: bool
    tokens: int
    turns: int
    time: float
    difficulty: str = "unknown"


@dataclass
class StrategyStats:
    """Statistical summary for a strategy."""
    strategy: str
    num_tasks: int
    success_rate: float
    total_tokens: int
    avg_tokens: float
    median_tokens: float
    std_tokens: float
    avg_turns: float
    avg_time: float

    # By difficulty
    easy_avg_tokens: float = 0.0
    medium_avg_tokens: float = 0.0
    hard_avg_tokens: float = 0.0


def load_results(results_file: Path) -> Dict:
    """Load experiment results from JSON file."""
    with open(results_file) as f:
        return json.load(f)


def get_difficulty_map() -> Dict[str, str]:
    """Get task difficulty mapping."""
    difficulty_map = {}
    try:
        # Import from simple_tasks
        sys.path.insert(0, str(Path(__file__).parent))
        from simple_tasks import get_all_tasks
        tasks = get_all_tasks()
        difficulty_map = {task.task_id: task.difficulty for task in tasks}
    except Exception as e:
        print(f"Warning: Could not load task difficulties: {e}")
    return difficulty_map


def extract_task_results(data: Dict, difficulty_map: Dict[str, str]) -> Tuple[List[TaskResult], List[TaskResult]]:
    """Extract task results for both strategies."""
    pruning_results = []
    baseline_results = []

    for result in data["results"].get("continuous_pruning", []):
        pruning_results.append(TaskResult(
            task_id=result["task_id"],
            strategy="continuous_pruning",
            success=result["success"],
            tokens=result["coding_agent_tokens"],
            turns=result["total_turns"],
            time=result["execution_time"],
            difficulty=difficulty_map.get(result["task_id"], "unknown")
        ))

    for result in data["results"].get("discrete_baseline", []):
        baseline_results.append(TaskResult(
            task_id=result["task_id"],
            strategy="discrete_baseline",
            success=result["success"],
            tokens=result["coding_agent_tokens"],
            turns=result["total_turns"],
            time=result["execution_time"],
            difficulty=difficulty_map.get(result["task_id"], "unknown")
        ))

    return pruning_results, baseline_results


def compute_strategy_stats(results: List[TaskResult]) -> StrategyStats:
    """Compute statistical summary for a strategy."""
    if not results:
        return None

    tokens = [r.tokens for r in results]
    turns = [r.turns for r in results]
    times = [r.time for r in results]
    successes = [r.success for r in results]

    # By difficulty
    easy_tokens = [r.tokens for r in results if r.difficulty == "easy"]
    medium_tokens = [r.tokens for r in results if r.difficulty == "medium"]
    hard_tokens = [r.tokens for r in results if r.difficulty == "hard"]

    return StrategyStats(
        strategy=results[0].strategy,
        num_tasks=len(results),
        success_rate=sum(successes) / len(successes) * 100,
        total_tokens=sum(tokens),
        avg_tokens=statistics.mean(tokens),
        median_tokens=statistics.median(tokens),
        std_tokens=statistics.stdev(tokens) if len(tokens) > 1 else 0,
        avg_turns=statistics.mean(turns),
        avg_time=statistics.mean(times),
        easy_avg_tokens=statistics.mean(easy_tokens) if easy_tokens else 0.0,
        medium_avg_tokens=statistics.mean(medium_tokens) if medium_tokens else 0.0,
        hard_avg_tokens=statistics.mean(hard_tokens) if hard_tokens else 0.0,
    )


def paired_comparison(pruning: List[TaskResult], baseline: List[TaskResult]) -> Tuple:
    """Perform paired comparison and calculate effect size."""
    # Match tasks by task_id
    pruning_dict = {r.task_id: r.tokens for r in pruning}
    baseline_dict = {r.task_id: r.tokens for r in baseline}

    # Get paired samples
    paired_pruning = []
    paired_baseline = []
    for task_id in pruning_dict:
        if task_id in baseline_dict:
            paired_pruning.append(pruning_dict[task_id])
            paired_baseline.append(baseline_dict[task_id])

    if len(paired_pruning) < 2:
        return None, None, None

    # Try scipy for t-test if available
    try:
        from scipy import stats as scipy_stats
        t_stat, p_value = scipy_stats.ttest_rel(paired_pruning, paired_baseline)
        t_stat = float(t_stat)
        p_value = float(p_value)
    except ImportError:
        print("Warning: scipy not available, skipping t-test")
        t_stat, p_value = None, None

    # Calculate effect size (Cohen's d for paired samples)
    diff = [p - b for p, b in zip(paired_pruning, paired_baseline)]
    if statistics.stdev(diff) > 0:
        d = statistics.mean(diff) / statistics.stdev(diff)
    else:
        d = 0

    return t_stat, p_value, d


def analyze_task_characteristics(pruning: List[TaskResult], baseline: List[TaskResult]):
    """Analyze which strategy performs better for different task types."""
    # Match tasks
    comparisons = []
    for p_result in pruning:
        b_result = next((r for r in baseline if r.task_id == p_result.task_id), None)
        if b_result:
            winner = "continuous_pruning" if p_result.tokens < b_result.tokens else \
                    "discrete_baseline" if b_result.tokens < p_result.tokens else "tie"
            ratio = p_result.tokens / b_result.tokens if b_result.tokens > 0 else 1.0

            comparisons.append({
                "task_id": p_result.task_id,
                "difficulty": p_result.difficulty,
                "cp_tokens": p_result.tokens,
                "cp_turns": p_result.turns,
                "db_tokens": b_result.tokens,
                "db_turns": b_result.turns,
                "winner": winner,
                "ratio": ratio,
            })

    return comparisons


def print_report(pruning_stats: StrategyStats, baseline_stats: StrategyStats,
                t_stat: float, p_value: float, effect_size: float,
                comparisons: List[Dict]):
    """Print comprehensive analysis report."""

    print("=" * 80)
    print("Two-Agent Experiment Statistical Analysis")
    print("=" * 80)
    print()

    print("Overall Performance")
    print("-" * 80)
    print(f"{'Strategy':<25} {'Tasks':<8} {'Success':<10} {'Total Tokens':<15} {'Avg Tokens':<12}")
    print("-" * 80)
    print(f"{'continuous_pruning':<25} {pruning_stats.num_tasks:<8} "
          f"{pruning_stats.success_rate:>6.1f}%   {pruning_stats.total_tokens:<15,} "
          f"{pruning_stats.avg_tokens:<12,.0f}")
    print(f"{'discrete_baseline':<25} {baseline_stats.num_tasks:<8} "
          f"{baseline_stats.success_rate:>6.1f}%   {baseline_stats.total_tokens:<15,} "
          f"{baseline_stats.avg_tokens:<12,.0f}")
    print()

    # Efficiency comparison
    token_diff = baseline_stats.total_tokens - pruning_stats.total_tokens
    pct_diff = (token_diff / pruning_stats.total_tokens) * 100
    winner = "continuous_pruning" if token_diff > 0 else "discrete_baseline"

    print(f"Winner: {winner} used {abs(pct_diff):.1f}% {'fewer' if pct_diff < 0 else 'more'} tokens")
    print(f"Absolute difference: {abs(token_diff):,} tokens")
    print()

    # Statistical significance
    print("Statistical Significance (Paired t-test)")
    print("-" * 80)
    if t_stat is not None and p_value is not None:
        print(f"t-statistic: {t_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        print(f"Effect size (Cohen's d): {effect_size:.4f}")

        if p_value < 0.001:
            sig = "Highly significant (p < 0.001)"
        elif p_value < 0.01:
            sig = "Very significant (p < 0.01)"
        elif p_value < 0.05:
            sig = "Significant (p < 0.05)"
        else:
            sig = "Not significant (p >= 0.05)"
        print(f"Result: {sig}")

        # Effect size interpretation
        if abs(effect_size) < 0.2:
            effect_interp = "negligible"
        elif abs(effect_size) < 0.5:
            effect_interp = "small"
        elif abs(effect_size) < 0.8:
            effect_interp = "medium"
        else:
            effect_interp = "large"
        print(f"Effect size: {effect_interp}")
    else:
        print("Insufficient data for t-test or scipy not available")
    print()

    # Performance by difficulty
    print("Performance by Difficulty")
    print("-" * 80)
    print(f"{'Difficulty':<15} {'CP Avg Tokens':<20} {'DB Avg Tokens':<20} {'Winner':<15}")
    print("-" * 80)

    if pruning_stats.easy_avg_tokens > 0 or baseline_stats.easy_avg_tokens > 0:
        easy_winner = "CP" if pruning_stats.easy_avg_tokens < baseline_stats.easy_avg_tokens else "DB"
        print(f"{'Easy':<15} {pruning_stats.easy_avg_tokens:<20,.0f} "
              f"{baseline_stats.easy_avg_tokens:<20,.0f} {easy_winner:<15}")

    if pruning_stats.medium_avg_tokens > 0 or baseline_stats.medium_avg_tokens > 0:
        medium_winner = "CP" if pruning_stats.medium_avg_tokens < baseline_stats.medium_avg_tokens else "DB"
        print(f"{'Medium':<15} {pruning_stats.medium_avg_tokens:<20,.0f} "
              f"{baseline_stats.medium_avg_tokens:<20,.0f} {medium_winner:<15}")

    if pruning_stats.hard_avg_tokens > 0 or baseline_stats.hard_avg_tokens > 0:
        hard_winner = "CP" if pruning_stats.hard_avg_tokens < baseline_stats.hard_avg_tokens else "DB"
        print(f"{'Hard':<15} {pruning_stats.hard_avg_tokens:<20,.0f} "
              f"{baseline_stats.hard_avg_tokens:<20,.0f} {hard_winner:<15}")
    print()

    # Per-task comparison
    print("Per-Task Comparison")
    print("-" * 80)
    print(f"{'Task':<25} {'Difficulty':<12} {'CP Tokens':<12} {'DB Tokens':<12} {'Winner':<10}")
    print("-" * 80)

    for comp in sorted(comparisons, key=lambda x: x["ratio"]):
        print(f"{comp['task_id']:<25} {comp['difficulty']:<12} "
              f"{comp['cp_tokens']:<12,} {comp['db_tokens']:<12,} "
              f"{comp['winner']:<10}")
    print()

    # Summary statistics
    print("Detailed Statistics")
    print("-" * 80)
    print(f"{'Metric':<30} {'Continuous Pruning':<25} {'Discrete Baseline':<25}")
    print("-" * 80)
    print(f"{'Median tokens':<30} {pruning_stats.median_tokens:<25,.0f} {baseline_stats.median_tokens:<25,.0f}")
    print(f"{'Std dev tokens':<30} {pruning_stats.std_tokens:<25,.0f} {baseline_stats.std_tokens:<25,.0f}")
    print(f"{'Avg turns':<30} {pruning_stats.avg_turns:<25,.1f} {baseline_stats.avg_turns:<25,.1f}")
    print(f"{'Avg time (seconds)':<30} {pruning_stats.avg_time:<25,.1f} {baseline_stats.avg_time:<25,.1f}")
    print()

    print("=" * 80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_two_agent_results.py <results_file.json>")
        sys.exit(1)

    results_file = Path(sys.argv[1])
    if not results_file.exists():
        print(f"Error: {results_file} not found")
        sys.exit(1)

    # Load and analyze results
    data = load_results(results_file)
    difficulty_map = get_difficulty_map()
    pruning, baseline = extract_task_results(data, difficulty_map)

    if not pruning or not baseline:
        print("Error: Missing results for one or both strategies")
        sys.exit(1)

    # Compute statistics
    pruning_stats = compute_strategy_stats(pruning)
    baseline_stats = compute_strategy_stats(baseline)

    # Statistical tests
    t_stat, p_value, effect_size = paired_comparison(pruning, baseline)

    # Task characteristics
    comparisons = analyze_task_characteristics(pruning, baseline)

    # Print report
    print_report(pruning_stats, baseline_stats, t_stat, p_value, effect_size, comparisons)


if __name__ == "__main__":
    main()
