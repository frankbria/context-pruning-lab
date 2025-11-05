"""
Weighted Scorecard for Strategy Comparison

Compares discrete_baseline vs continuous_pruning using weighted metrics.
Normalizes all scores to 1000 as maximum.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import json
from pathlib import Path


@dataclass
class WeightedScoreConfig:
    """Configuration for weighted scoring"""

    # Weights (must sum to 1.0)
    correctness_weight: float = 0.50      # 50% - highest priority
    tokens_efficiency_weight: float = 0.25  # 25% - second priority
    turns_efficiency_weight: float = 0.15   # 15% - third priority
    compaction_weight: float = 0.05         # 5% - context management efficiency
    files_weight: float = 0.05              # 5% - code exploration efficiency

    # Normalization targets (lower is better for efficiency metrics)
    target_tokens: int = 2_000_000      # Baseline: 2M tokens is "typical"
    target_turns: int = 40               # Baseline: 40 turns is "typical"
    target_compactions: int = 2          # Baseline: 2 compactions is "typical"
    target_files: int = 40               # Baseline: 40 files is "typical"

    def validate(self):
        """Ensure weights sum to 1.0"""
        total = (
            self.correctness_weight +
            self.tokens_efficiency_weight +
            self.turns_efficiency_weight +
            self.compaction_weight +
            self.files_weight
        )
        assert abs(total - 1.0) < 0.001, f"Weights must sum to 1.0, got {total}"


@dataclass
class StrategyScore:
    """Scores for a single strategy across all problems"""

    strategy: str
    n_problems: int

    # Raw metrics (averaged across problems)
    avg_success_rate: float          # 0-1 (1 = perfect)
    avg_tokens: float                # Lower is better
    avg_turns: float                 # Lower is better
    avg_compactions: float           # Strategy-dependent (discrete wants 2-4, continuous wants 0)
    avg_files: float                 # Lower is better (more efficient)

    # Normalized scores (0-1, higher is better)
    correctness_score: float = 0.0
    tokens_score: float = 0.0
    turns_score: float = 0.0
    compaction_score: float = 0.0
    files_score: float = 0.0

    # Weighted score (0-1000)
    total_score: float = 0.0

    # Breakdown for transparency
    score_breakdown: Dict[str, float] = None

    def __post_init__(self):
        if self.score_breakdown is None:
            self.score_breakdown = {}


class WeightedScorer:
    """
    Calculates weighted scores for strategy comparison.

    Scoring Philosophy:
    - Correctness: Most important (50%) - did it work?
    - Efficiency: Second (40% total) - how many resources used?
    - Context Management: Third (10% total) - how well managed context?

    All scores normalized to 0-1000 scale for easy comparison.
    """

    def __init__(self, config: WeightedScoreConfig = None):
        self.config = config or WeightedScoreConfig()
        self.config.validate()

    def score_strategy(
        self,
        strategy: str,
        results: List[Dict[str, Any]]
    ) -> StrategyScore:
        """
        Score a strategy based on its results.

        Args:
            strategy: Strategy name
            results: List of ExperimentResult dicts

        Returns:
            StrategyScore with normalized and weighted scores
        """
        if not results:
            raise ValueError("No results provided for scoring")

        # Calculate average raw metrics
        n = len(results)
        avg_success = sum(r['success'] for r in results) / n
        avg_tokens = sum(r['total_tokens'] for r in results) / n
        avg_turns = sum(r['turns'] for r in results) / n
        avg_compactions = sum(r['compaction_events'] for r in results) / n
        avg_files = sum(r['files_read'] for r in results) / n

        # Normalize each metric to 0-1 scale (higher = better)
        correctness_score = self._normalize_correctness(avg_success)
        tokens_score = self._normalize_efficiency(avg_tokens, self.config.target_tokens)
        turns_score = self._normalize_efficiency(avg_turns, self.config.target_turns)
        compaction_score = self._normalize_compaction(avg_compactions, strategy)
        files_score = self._normalize_efficiency(avg_files, self.config.target_files)

        # Calculate weighted contributions
        breakdown = {
            'correctness': correctness_score * self.config.correctness_weight,
            'tokens': tokens_score * self.config.tokens_efficiency_weight,
            'turns': turns_score * self.config.turns_efficiency_weight,
            'compaction': compaction_score * self.config.compaction_weight,
            'files': files_score * self.config.files_weight
        }

        # Total weighted score (0-1)
        weighted_sum = sum(breakdown.values())

        # Scale to 1000
        total_score = weighted_sum * 1000

        return StrategyScore(
            strategy=strategy,
            n_problems=n,
            avg_success_rate=avg_success,
            avg_tokens=avg_tokens,
            avg_turns=avg_turns,
            avg_compactions=avg_compactions,
            avg_files=avg_files,
            correctness_score=correctness_score,
            tokens_score=tokens_score,
            turns_score=turns_score,
            compaction_score=compaction_score,
            files_score=files_score,
            total_score=total_score,
            score_breakdown=breakdown
        )

    def _normalize_correctness(self, success_rate: float) -> float:
        """
        Normalize correctness: 1.0 = perfect, 0.0 = total failure.
        This is already 0-1, just pass through.
        """
        return success_rate

    def _normalize_efficiency(self, actual: float, target: float) -> float:
        """
        Normalize efficiency metric (lower actual is better).

        Logic:
        - actual == target → score = 0.5 (baseline)
        - actual < target → score > 0.5 (better than baseline)
        - actual > target → score < 0.5 (worse than baseline)

        Formula: score = target / (actual + target)
        This gives:
        - actual = 0 → score = 1.0 (perfect)
        - actual = target → score = 0.5 (baseline)
        - actual = 2*target → score = 0.33 (worse)
        - actual = infinity → score = 0.0 (terrible)
        """
        if actual <= 0:
            return 1.0
        return target / (actual + target)

    def _normalize_compaction(self, avg_compactions: float, strategy: str) -> float:
        """
        Normalize compaction metric (strategy-dependent).

        For discrete_baseline:
        - Target is 2-4 compactions (sweet spot)
        - Too few → didn't test enough
        - Too many → inefficient compaction

        For continuous_pruning:
        - Target is 0 compactions (shouldn't trigger discrete)
        - Any compactions → strategy failing to prevent them
        """
        if strategy == "discrete_baseline":
            # Target: 2-4 compactions
            # Score highest at 3, falls off outside 2-4 range
            if 2 <= avg_compactions <= 4:
                # Within ideal range
                return 1.0 - abs(avg_compactions - 3) / 4  # Peak at 3
            elif avg_compactions < 2:
                # Too few (didn't trigger enough)
                return avg_compactions / 2  # Linear from 0 → 0.5
            else:
                # Too many (inefficient)
                return max(0, 1.0 - (avg_compactions - 4) / 4)  # Linear decline

        elif strategy == "continuous_pruning":
            # Target: 0 compactions (perfect pruning)
            # Score decreases with any compactions
            if avg_compactions == 0:
                return 1.0
            else:
                # Penalty for each compaction
                return max(0, 1.0 - avg_compactions / 4)  # 4 compactions → score 0

        else:
            # Unknown strategy, use neutral score
            return 0.5

    def compare_strategies(
        self,
        results_by_strategy: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, StrategyScore]:
        """
        Compare multiple strategies and return scores.

        Args:
            results_by_strategy: Dict mapping strategy name → list of results

        Returns:
            Dict mapping strategy name → StrategyScore
        """
        scores = {}
        for strategy, results in results_by_strategy.items():
            scores[strategy] = self.score_strategy(strategy, results)
        return scores

    def print_comparison(
        self,
        scores: Dict[str, StrategyScore],
        show_breakdown: bool = True
    ):
        """
        Print formatted comparison of strategies.

        Args:
            scores: Dict mapping strategy → StrategyScore
            show_breakdown: Whether to show detailed breakdown
        """
        print("\n" + "=" * 80)
        print("WEIGHTED SCORECARD COMPARISON")
        print("=" * 80)

        # Sort by total score
        sorted_strategies = sorted(
            scores.items(),
            key=lambda x: x[1].total_score,
            reverse=True
        )

        for strategy, score in sorted_strategies:
            print(f"\n{strategy.upper()}")
            print(f"{'─' * 80}")
            print(f"  Total Score: {score.total_score:.1f} / 1000")
            print()
            print(f"  Raw Metrics (averaged across {score.n_problems} problems):")
            print(f"    Success Rate: {score.avg_success_rate:.1%}")
            print(f"    Avg Tokens:   {score.avg_tokens:,.0f}")
            print(f"    Avg Turns:    {score.avg_turns:.1f}")
            print(f"    Avg Compactions: {score.avg_compactions:.1f}")
            print(f"    Avg Files Read:  {score.avg_files:.1f}")

            if show_breakdown:
                print()
                print(f"  Normalized Scores (0-1, higher = better):")
                print(f"    Correctness:  {score.correctness_score:.3f}")
                print(f"    Tokens Efficiency: {score.tokens_score:.3f}")
                print(f"    Turns Efficiency:  {score.turns_score:.3f}")
                print(f"    Compaction:   {score.compaction_score:.3f}")
                print(f"    Files:        {score.files_score:.3f}")
                print()
                print(f"  Weighted Contributions (weights × scores):")
                for metric, contribution in score.score_breakdown.items():
                    print(f"    {metric.capitalize():15s}: {contribution:.4f}")

        # Winner
        winner_strategy, winner_score = sorted_strategies[0]
        if len(sorted_strategies) > 1:
            runner_up = sorted_strategies[1][1]
            margin = winner_score.total_score - runner_up.total_score
            print()
            print("=" * 80)
            print(f"WINNER: {winner_strategy.upper()}")
            print(f"Score: {winner_score.total_score:.1f} / 1000")
            print(f"Margin: +{margin:.1f} points over runner-up")
            print("=" * 80)


def score_experiment_results(results_file: Path, output_file: Path = None):
    """
    Score experiment results from a JSON file.

    Args:
        results_file: Path to experiment results JSON
        output_file: Optional path to save scores JSON
    """
    # Load results
    with open(results_file) as f:
        data = json.load(f)

    results_by_strategy = data['results']

    # Score strategies
    scorer = WeightedScorer()
    scores = scorer.compare_strategies(results_by_strategy)

    # Print comparison
    scorer.print_comparison(scores, show_breakdown=True)

    # Save scores if requested
    if output_file:
        scores_data = {
            strategy: {
                'total_score': score.total_score,
                'raw_metrics': {
                    'success_rate': score.avg_success_rate,
                    'avg_tokens': score.avg_tokens,
                    'avg_turns': score.avg_turns,
                    'avg_compactions': score.avg_compactions,
                    'avg_files': score.avg_files
                },
                'normalized_scores': {
                    'correctness': score.correctness_score,
                    'tokens': score.tokens_score,
                    'turns': score.turns_score,
                    'compaction': score.compaction_score,
                    'files': score.files_score
                },
                'breakdown': score.score_breakdown
            }
            for strategy, score in scores.items()
        }

        with open(output_file, 'w') as f:
            json.dump(scores_data, f, indent=2)

        print(f"\n✓ Scores saved to: {output_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scorer.py <results_file.json> [output_file.json]")
        sys.exit(1)

    results_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    score_experiment_results(results_file, output_file)
