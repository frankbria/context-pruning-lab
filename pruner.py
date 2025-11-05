"""
Continuous Context Pruning Algorithm

Core algorithm for maintaining steady-state context size through
continuous importance-based pruning after every interaction.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class CoreBudgetEnforcer:
    """
    Enforces CORE tier budget constraint (≤25% of target capacity).

    The CORE tier contains critical information that should never be pruned
    (decisions, requirements, architecture). However, it must not exceed
    25% of the total target capacity to leave room for HOT tier operations.

    When budget is exceeded:
    - New CORE items are redirected to HOT tier with high importance (0.95)
    - Warning is logged for visibility
    - System continues operating (soft constraint)
    """

    def __init__(self, target_size: int, core_budget_ratio: float = 0.25):
        """
        Initialize CORE budget enforcer.

        Args:
            target_size: Total target context size in tokens
            core_budget_ratio: Maximum fraction of target for CORE tier (default: 0.25)
        """
        self.target_size = target_size
        self.core_budget_ratio = core_budget_ratio
        self.core_budget = int(target_size * core_budget_ratio)
        self.core_items: List[ContextItem] = []
        self.overflow_count = 0  # Track how many items overflowed

    def can_add_to_core(self, item: ContextItem) -> bool:
        """
        Check if item can be added to CORE without exceeding budget.

        Args:
            item: Context item to check

        Returns:
            bool: True if adding item would stay within budget
        """
        current_tokens = sum(i.token_count for i in self.core_items)
        return (current_tokens + item.token_count) <= self.core_budget

    def add_to_core(self, item: ContextItem) -> Tuple[bool, Optional[str]]:
        """
        Add item to CORE tier if budget allows, otherwise return overflow info.

        Args:
            item: Context item to add to CORE

        Returns:
            Tuple of (success: bool, reason: Optional[str])
            - (True, None) if item added to CORE
            - (False, reason) if item overflowed with explanation
        """
        if self.can_add_to_core(item):
            # Budget allows, add to CORE
            item.tier = "CORE"
            item.importance = 1.0
            item.pinned = True
            self.core_items.append(item)
            return (True, None)
        else:
            # Budget exceeded, item overflows to HOT
            self.overflow_count += 1
            current_tokens = sum(i.token_count for i in self.core_items)
            utilization = current_tokens / self.core_budget if self.core_budget > 0 else 0

            reason = (
                f"CORE budget exceeded: {current_tokens}/{self.core_budget} tokens "
                f"({utilization:.1%}). Item redirected to HOT tier with importance=0.95"
            )

            logger.warning(reason)

            # Item will be added to HOT tier by caller with high importance
            return (False, reason)

    def remove_from_core(self, item: ContextItem) -> bool:
        """
        Remove item from CORE tier.

        Args:
            item: Context item to remove

        Returns:
            bool: True if item was in CORE and removed, False otherwise
        """
        if item in self.core_items:
            self.core_items.remove(item)
            return True
        return False

    def get_core_utilization(self) -> float:
        """
        Calculate current CORE tier utilization as fraction of budget.

        Returns:
            float: Utilization ratio (0.0-1.0+, can exceed 1.0 if over budget)
        """
        current_tokens = sum(i.token_count for i in self.core_items)
        return current_tokens / self.core_budget if self.core_budget > 0 else 0.0

    def get_core_tokens(self) -> int:
        """Get current token count in CORE tier"""
        return sum(i.token_count for i in self.core_items)

    def get_available_budget(self) -> int:
        """Get remaining CORE budget in tokens"""
        current = self.get_core_tokens()
        return max(0, self.core_budget - current)

    def get_stats(self) -> Dict[str, Any]:
        """Get CORE budget statistics for reporting"""
        return {
            'core_budget': self.core_budget,
            'core_tokens': self.get_core_tokens(),
            'core_utilization': self.get_core_utilization(),
            'core_items_count': len(self.core_items),
            'available_budget': self.get_available_budget(),
            'overflow_count': self.overflow_count
        }


class ContinuousPruner:
    """
    Continuous context pruning implementation.

    Maintains steady-state context by pruning after every interaction.
    Uses adaptive pruning rate (0.90-1.10) that adjusts based on context utilization.
    """

    def __init__(
        self,
        target_size: int = 40000,  # Target context size in tokens
        pruning_overhead: float = 1.10,  # DEPRECATED: Use adaptive rate instead
        core_budget: int = 10000,  # Reserved for CORE tier (never pruned)
        # NEW: Warmup and gradual ramp parameters
        warmup_interactions: int = 5,  # No pruning for first N interactions
        ramp_interactions: int = 10,  # Gradual rate increase over N interactions
        recent_protection: int = 3,  # Always protect last N interactions
        min_pruning_rate: float = 0.10,  # Minimum rate during warmup (10%)
        target_pruning_rate: float = 0.60  # Maximum rate at steady state (60%)
    ):
        self.target_size = target_size
        self.pruning_overhead = pruning_overhead  # Kept for backward compatibility
        self.core_budget = core_budget

        # NEW: Warmup and ramp parameters
        self.warmup_interactions = warmup_interactions
        self.ramp_interactions = ramp_interactions
        self.recent_protection = recent_protection
        self.min_pruning_rate = min_pruning_rate
        self.target_pruning_rate = target_pruning_rate

        self.context: List[ContextItem] = []
        self.interaction_count = 0
        self.metrics = PruningMetrics(target_token_count=target_size)

        # Initialize CORE budget enforcer
        self.core_enforcer = CoreBudgetEnforcer(
            target_size=target_size,
            core_budget_ratio=0.25
        )

        # Track pruning rate history for analysis
        self.pruning_rate_history: List[float] = []

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

    def calculate_adaptive_rate(self) -> float:
        """
        Calculate adaptive pruning rate (0.90 - 1.10) based on system state.

        The pruning rate self-regulates to maintain steady-state context:
        - When context is low: prune less (allow growth)
        - When context is high: prune more (force shrinkage)
        - When CORE budget exceeded: prune HOT more aggressively

        Formula from Technical Specification §2.2.2:
        - Base rate: 1.10 (slight shrinkage by default)
        - Utilization adjustment: -0.15 to +0.10 based on current_utilization
        - CORE pressure adjustment: +0.05 if CORE exceeds 25% budget
        - Final rate: clamped to [0.90, 1.10]

        Returns:
            float: Pruning rate in range [0.90, 1.10]

        Examples:
            >>> pruner.calculate_adaptive_rate()  # 20% utilization
            0.95  # Allow modest growth
            >>> pruner.calculate_adaptive_rate()  # 80% utilization
            1.10  # Force aggressive shrinkage
        """
        # Calculate current context utilization
        current_tokens = self.get_total_tokens()
        current_utilization = current_tokens / self.target_size if self.target_size > 0 else 0.0

        # Calculate CORE tier utilization using budget enforcer
        core_utilization = self.core_enforcer.get_core_utilization()

        # Base pruning rate (default: slight shrinkage)
        base_rate = 1.10

        # Adjust based on current utilization
        if current_utilization < 0.20:
            # Very low utilization: allow significant growth
            utilization_adjustment = -0.15
        elif current_utilization < 0.30:
            # Low utilization: allow modest growth
            utilization_adjustment = -0.10
        elif current_utilization < 0.50:
            # Target range: standard pruning
            utilization_adjustment = 0.0
        elif current_utilization < 0.70:
            # High utilization: more aggressive pruning
            utilization_adjustment = +0.05
        else:
            # Very high utilization: maximum pruning
            utilization_adjustment = +0.10

        # Adjust based on CORE budget pressure
        if core_utilization > 0.25:
            # CORE tier exceeds budget: prune HOT more aggressively
            core_adjustment = +0.05
        else:
            core_adjustment = 0.0

        # Calculate final rate
        final_rate = base_rate + utilization_adjustment + core_adjustment

        # Enforce bounds [0.90, 1.10]
        final_rate = max(0.90, min(1.10, final_rate))

        return final_rate

    def get_current_pruning_rate(self) -> float:
        """
        Calculate current pruning rate based on warmup/ramp phases.

        Phase 1 (Warmup): interactions 1-warmup_interactions
            - Use min_pruning_rate (default 10%)
            - Allows agent to build working memory

        Phase 2 (Ramp): interactions (warmup+1) to (warmup+ramp)
            - Linear increase from min to target rate
            - Smooth transition to steady state

        Phase 3 (Steady State): interactions > (warmup+ramp)
            - Use target_pruning_rate (default 60%)
            - Maintain stable context size

        Returns:
            float: Current pruning rate (0.0-1.0)
        """
        if self.interaction_count <= self.warmup_interactions:
            # Warmup phase: minimal pruning to build context
            return self.min_pruning_rate

        if self.interaction_count <= self.warmup_interactions + self.ramp_interactions:
            # Ramp phase: linear increase
            progress = (self.interaction_count - self.warmup_interactions) / self.ramp_interactions
            rate_range = self.target_pruning_rate - self.min_pruning_rate
            return self.min_pruning_rate + (progress * rate_range)

        # Steady state: full pruning rate
        return self.target_pruning_rate

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

        # NEW: Use gradual pruning rate instead of adaptive
        pruning_rate = self.get_current_pruning_rate()
        self.pruning_rate_history.append(pruning_rate)

        # Calculate how much to prune using gradual rate
        target_prune = int(tokens_added * pruning_rate)

        # Prune lowest-scored items
        tokens_before_prune = self.get_total_tokens()
        tokens_removed, items_removed = self._prune_context(target_prune)
        tokens_after_prune = self.get_total_tokens()

        # Enhanced DEBUG logging with phase information
        if self.interaction_count % 5 == 0 or self.interaction_count <= self.warmup_interactions:
            import logging

            # Determine current phase
            if self.interaction_count <= self.warmup_interactions:
                phase = "WARMUP"
            elif self.interaction_count <= self.warmup_interactions + self.ramp_interactions:
                phase = "RAMP"
            else:
                phase = "STEADY"

            logging.info(f"ContinuousPruner[{self.interaction_count}] {phase}: "
                        f"tokens_before={tokens_before_prune}, "
                        f"tokens_after={tokens_after_prune}, "
                        f"removed={tokens_removed}, "
                        f"items_in_context={len(self.context)}, "
                        f"pruning_rate={pruning_rate:.3f}")

        # Update metrics
        self.metrics.tokens_removed = tokens_removed
        self.metrics.items_removed = items_removed
        self.metrics.current_token_count = tokens_after_prune
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

        NEW: Adds explicit recent protection - last N interactions are never pruned.

        Returns: (tokens_removed, items_removed)
        """

        # NEW: Calculate recent protection threshold
        recent_threshold = self.interaction_count - self.recent_protection

        # Separate protected items (CORE + high importance + recent) from prunable
        protected_items = [
            i for i in self.context
            if i.tier == "CORE"
            or i.importance >= 0.95
            or i.interaction_number > recent_threshold  # NEW: Recent protection
        ]

        prunable_items = [
            i for i in self.context
            if i.tier != "CORE"
            and i.importance < 0.95
            and i.interaction_number <= recent_threshold  # NEW: Must be old enough
        ]

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

        # Rebuild context (protected + kept items)
        self.context = protected_items + items_to_keep

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
        Add item to CORE tier (never pruned) if budget allows.

        Used for critical decisions, architecture, requirements, etc.

        If CORE budget is exceeded, item is added to HOT tier with
        high importance (0.95) instead.

        Args:
            content: Content of the item
            item_type: Type of item (default: 'core_decision')

        Returns:
            bool: True if added to CORE, False if overflowed to HOT
        """
        item = ContextItem(
            content=content,
            item_type=item_type,
            interaction_number=self.interaction_count
        )

        # Try to add to CORE tier via budget enforcer
        success, reason = self.core_enforcer.add_to_core(item)

        if success:
            # Added to CORE tier
            self.context.append(item)
            return True
        else:
            # Budget exceeded, add to HOT tier with high importance
            item.tier = "HOT"
            item.importance = 0.95  # Very high, but not CORE-level
            item.pinned = False  # Can be pruned if necessary
            self.context.append(item)
            logger.info(f"CORE budget overflow: Item added to HOT tier (reason: {reason})")
            return False

    def pin_item(self, item: ContextItem):
        """Manually mark item as important (prevents pruning)"""
        item.pinned = True
        item.importance = 1.0

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current pruning metrics and statistics"""
        tiers = self.get_context_by_tier()

        # Calculate adaptive rate stats
        adaptive_rate_stats = {}
        if self.pruning_rate_history:
            adaptive_rate_stats = {
                'current_rate': self.pruning_rate_history[-1],
                'mean_rate': sum(self.pruning_rate_history) / len(self.pruning_rate_history),
                'min_rate': min(self.pruning_rate_history),
                'max_rate': max(self.pruning_rate_history),
            }

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
            'adaptive_rate': adaptive_rate_stats,
            'core_budget': self.core_enforcer.get_stats(),
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
