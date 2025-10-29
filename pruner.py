"""
Continuous Context Pruning Algorithm

Core algorithm for maintaining steady-state context size through
continuous importance-based pruning after every interaction.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import math


@dataclass
class ContextItem:
    """Single item in context (message, file, decision, etc.)"""

    content: str
    item_type: str  # 'user_message', 'agent_response', 'decision', 'code', etc.
    timestamp: datetime = field(default_factory=datetime.now)
    interaction_number: int = 0

    # Importance tracking
    importance: float = 0.5
    access_count: int = 0
    pinned: bool = False  # Manually marked as important

    # Tier assignment
    tier: str = "HOT"  # HOT, WARM, COLD, CORE

    @property
    def token_count(self) -> int:
        """Rough token count estimate (4 chars per token)"""
        return len(self.content) // 4

    @property
    def age_in_interactions(self) -> int:
        """How many interactions ago was this created"""
        # Will be set by pruner
        return 0


@dataclass
class PruningMetrics:
    """Metrics tracked during pruning"""

    total_interactions: int = 0
    tokens_added: int = 0
    tokens_removed: int = 0
    items_removed: int = 0
    current_token_count: int = 0
    target_token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_interactions': self.total_interactions,
            'tokens_added': self.tokens_added,
            'tokens_removed': self.tokens_removed,
            'items_removed': self.items_removed,
            'current_token_count': self.current_token_count,
            'target_token_count': self.target_token_count,
            'efficiency': self.tokens_removed / max(self.tokens_added, 1)
        }


class ContinuousPruner:
    """
    Continuous context pruning implementation.

    Maintains steady-state context by pruning after every interaction.
    Goal: Remove ~110% of what's added to gradually reduce context over time.
    """

    def __init__(
        self,
        target_size: int = 40000,  # Target context size in tokens
        pruning_overhead: float = 1.10,  # Remove 110% of what's added
        core_budget: int = 10000  # Reserved for CORE tier (never pruned)
    ):
        self.target_size = target_size
        self.pruning_overhead = pruning_overhead
        self.core_budget = core_budget

        self.context: List[ContextItem] = []
        self.interaction_count = 0
        self.metrics = PruningMetrics(target_token_count=target_size)

        # Type importance weights
        self.type_weights = {
            'core_decision': 1.0,      # Never pruned
            'architecture': 0.95,
            'requirement': 0.90,
            'constraint': 0.90,
            'user_message': 0.70,
            'agent_response': 0.65,
            'code': 0.60,
            'test_result': 0.50,
            'debug_log': 0.30,
            'trace': 0.20
        }

    def add_interaction(
        self,
        user_message: str,
        agent_response: str,
        user_type: str = 'user_message',
        agent_type: str = 'agent_response'
    ) -> PruningMetrics:
        """
        Add new interaction and prune to maintain target size.

        Returns metrics about the pruning operation.
        """
        self.interaction_count += 1

        # Create new context items
        new_items = [
            ContextItem(
                content=user_message,
                item_type=user_type,
                interaction_number=self.interaction_count,
                importance=0.9  # Recent messages start high
            ),
            ContextItem(
                content=agent_response,
                item_type=agent_type,
                interaction_number=self.interaction_count,
                importance=0.85
            )
        ]

        # Calculate tokens added
        tokens_added = sum(item.token_count for item in new_items)
        self.metrics.tokens_added = tokens_added

        # Add to context
        self.context.extend(new_items)

        # Update all importance scores
        self._update_importance_scores()

        # Calculate how much to prune (110% of what was added)
        target_prune = int(tokens_added * self.pruning_overhead)

        # Prune lowest-scored items
        tokens_removed, items_removed = self._prune_context(target_prune)

        # Update metrics
        self.metrics.tokens_removed = tokens_removed
        self.metrics.items_removed = items_removed
        self.metrics.current_token_count = self.get_total_tokens()
        self.metrics.total_interactions = self.interaction_count

        return self.metrics

    def _update_importance_scores(self):
        """Update importance scores for all context items"""
        for item in self.context:
            item.importance = self._calculate_importance(item)

    def _calculate_importance(self, item: ContextItem) -> float:
        """
        Calculate importance score (0.0-1.0) for a context item.

        Factors:
        - Recency (40%): Exponential decay
        - Access frequency (20%): How often referenced
        - Item type (30%): Some types more important
        - Manual pins (10%): User/agent marked as critical
        """

        # If manually pinned, always maximum importance
        if item.pinned:
            return 1.0

        # If CORE tier, always maximum importance
        if item.tier == "CORE":
            return 1.0

        # Calculate age in interactions
        age = self.interaction_count - item.interaction_number

        # Recency score (exponential decay, half-life = 10 interactions)
        recency_score = math.exp(-age / 10)

        # Access frequency score (capped at 0.3)
        access_score = min(item.access_count * 0.05, 0.3)

        # Type weight score
        type_score = self.type_weights.get(item.item_type, 0.5)

        # Weighted combination
        final_score = (
            recency_score * 0.4 +
            access_score * 0.2 +
            type_score * 0.3 +
            (0.1 if item.pinned else 0.0)
        )

        return min(final_score, 1.0)

    def _prune_context(self, target_tokens: int) -> tuple[int, int]:
        """
        Prune lowest-importance items until target tokens removed.

        Returns: (tokens_removed, items_removed)
        """

        # Separate CORE tier (never prune) from prunable
        core_items = [i for i in self.context if i.tier == "CORE" or i.importance >= 0.95]
        prunable_items = [i for i in self.context if i.tier != "CORE" and i.importance < 0.95]

        # Sort prunable by importance (lowest first)
        prunable_items.sort(key=lambda x: x.importance)

        # Remove items until target met
        tokens_removed = 0
        items_removed = 0
        items_to_keep = []

        for item in prunable_items:
            if tokens_removed < target_tokens:
                # Remove this item
                tokens_removed += item.token_count
                items_removed += 1
                # Optionally: archive to WARM/COLD tier
                self._archive_item(item)
            else:
                # Keep this item
                items_to_keep.append(item)

        # Rebuild context (CORE + kept items)
        self.context = core_items + items_to_keep

        return tokens_removed, items_removed

    def _archive_item(self, item: ContextItem):
        """
        Archive item to WARM or COLD tier based on importance.

        In real implementation, this would:
        - Move to database (WARM tier)
        - Move to filesystem (COLD tier)

        For lab purposes, we just track that it was archived.
        """
        if item.importance >= 0.4:
            item.tier = "WARM"
        else:
            item.tier = "COLD"

    def get_total_tokens(self) -> int:
        """Get current total token count in context"""
        return sum(item.token_count for item in self.context)

    def get_context_by_tier(self) -> Dict[str, List[ContextItem]]:
        """Group context items by tier"""
        tiers = {'CORE': [], 'HOT': [], 'WARM': [], 'COLD': []}
        for item in self.context:
            tiers[item.tier].append(item)
        return tiers

    def add_core_item(self, content: str, item_type: str = 'core_decision'):
        """
        Add item to CORE tier (never pruned).

        Used for critical decisions, architecture, requirements, etc.
        """
        item = ContextItem(
            content=content,
            item_type=item_type,
            interaction_number=self.interaction_count,
            importance=1.0,
            tier="CORE",
            pinned=True
        )
        self.context.append(item)

    def pin_item(self, item: ContextItem):
        """Manually mark item as important (prevents pruning)"""
        item.pinned = True
        item.importance = 1.0

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current pruning metrics and statistics"""
        tiers = self.get_context_by_tier()

        return {
            'total_interactions': self.interaction_count,
            'total_items': len(self.context),
            'total_tokens': self.get_total_tokens(),
            'target_tokens': self.target_size,
            'utilization': self.get_total_tokens() / self.target_size,
            'items_by_tier': {
                tier: len(items) for tier, items in tiers.items()
            },
            'tokens_by_tier': {
                tier: sum(i.token_count for i in items)
                for tier, items in tiers.items()
            },
            'last_prune': self.metrics.to_dict()
        }


def demo():
    """Quick demonstration of continuous pruning"""
    pruner = ContinuousPruner(target_size=10000)

    # Add some core decisions
    pruner.add_core_item("Project uses OAuth2 for authentication", "core_decision")
    pruner.add_core_item("Target: Python 3.11+", "requirement")

    # Simulate 20 interactions
    for i in range(20):
        user_msg = f"User message {i}: Let's implement feature X with approach Y " * 20
        agent_msg = f"Agent response {i}: I'll implement that using pattern Z " * 25

        metrics = pruner.add_interaction(user_msg, agent_msg)

        print(f"\nInteraction {i+1}:")
        print(f"  Tokens: {metrics.current_token_count}/{metrics.target_token_count}")
        print(f"  Added: {metrics.tokens_added}, Removed: {metrics.tokens_removed}")
        print(f"  Items: {len(pruner.context)}")

    # Final summary
    summary = pruner.get_metrics_summary()
    print("\n=== Final Summary ===")
    print(f"Total tokens: {summary['total_tokens']}")
    print(f"Utilization: {summary['utilization']:.1%}")
    print(f"Items by tier: {summary['items_by_tier']}")
    print(f"Tokens by tier: {summary['tokens_by_tier']}")


if __name__ == '__main__':
    demo()
