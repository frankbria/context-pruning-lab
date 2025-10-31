"""
Discrete Compaction Baseline

Rule-based simulator for traditional discrete compaction strategy used in
conventional LLM context management. Implements "wait-until-crisis" approach
as a baseline for comparison against continuous pruning.

Phase I uses rule-based compression (no LLM) for:
- Deterministic, reproducible behavior
- Fast execution for large-scale experiments
- Cost-effective validation

Reference: Technical Specification §3.2.1
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
import logging

# Reuse ContextItem from pruner module
from pruner import ContextItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscreteCompactionBaseline:
    """
    Simulates traditional discrete compaction strategy.

    Key Characteristics:
    - Waits until context is ~80% full before compacting
    - Compresses to 30% of target capacity (aggressive reset)
    - Keeps recent 5 interactions fully (10 items: 5 user + 5 agent)
    - Applies lossy compression to older content (keeps top 20% by importance)
    - Tracks compaction events and degradation metrics

    This represents the "batch compaction" approach that continuous
    pruning aims to improve upon.
    """

    def __init__(
        self,
        target_size: int = 40000,
        compaction_threshold: float = 0.80,
        compaction_target: float = 0.30,
        recent_interactions_to_keep: int = 5,
    ):
        """
        Initialize discrete compaction baseline.

        Args:
            target_size: Target context size in tokens (default 40K)
            compaction_threshold: Utilization % that triggers compaction (default 0.80)
            compaction_target: Target % after compaction (default 0.30)
            recent_interactions_to_keep: Number of recent interactions to preserve fully
        """
        self.target_size = target_size
        self.compaction_threshold = compaction_threshold
        self.compaction_target = compaction_target
        self.recent_interactions_to_keep = recent_interactions_to_keep

        # Context storage
        self.context: List[ContextItem] = []

        # Tracking
        self.interaction_count = 0
        self.compaction_events: List[Dict[str, Any]] = []
        self.current_tokens = 0

        logger.info(
            f"DiscreteCompactionBaseline initialized: "
            f"target={target_size}, threshold={compaction_threshold:.0%}, "
            f"compaction_target={compaction_target:.0%}"
        )

    def add_interaction(self, user_msg: str, agent_msg: str) -> bool:
        """
        Add a user-agent interaction pair.

        Args:
            user_msg: User message content
            agent_msg: Agent response content

        Returns:
            True if compaction was triggered, False otherwise
        """
        self.interaction_count += 1

        # Create context items
        user_item = ContextItem(
            content=user_msg,
            item_type="user_message",
            interaction_number=self.interaction_count,
            importance=0.5,
        )
        agent_item = ContextItem(
            content=agent_msg,
            item_type="agent_response",
            interaction_number=self.interaction_count,
            importance=0.5,
        )

        # Add to context
        self.context.append(user_item)
        self.context.append(agent_item)

        # Update token count
        self.current_tokens = self.get_total_tokens()

        # Check if compaction needed
        threshold_tokens = int(self.target_size * self.compaction_threshold)
        if self.current_tokens >= threshold_tokens:
            logger.info(
                f"Compaction triggered at interaction {self.interaction_count}: "
                f"{self.current_tokens} >= {threshold_tokens} tokens "
                f"({self.get_utilization():.1%})"
            )
            self.perform_compaction()
            return True

        return False

    def perform_compaction(self) -> None:
        """
        Perform discrete compaction.

        Strategy (Phase I - Rule-Based):
        1. Keep most recent N interactions fully (default: 5 interactions = 10 items)
        2. From older content, keep top 20% by importance (simulate lossy summarization)
        3. Compress to 30% of target capacity
        4. Track metrics for degradation analysis

        This simulates the "lossy batch compression" that occurs in traditional
        context management systems.
        """
        tokens_before = self.current_tokens

        # Calculate target tokens after compaction
        target_tokens = int(self.target_size * self.compaction_target)

        # Separate recent vs. older content
        # Recent: Last N interactions (2*N items: user + agent pairs)
        items_to_keep_recent = self.recent_interactions_to_keep * 2
        recent_items = self.context[-items_to_keep_recent:] if len(self.context) > items_to_keep_recent else self.context
        older_items = self.context[:-items_to_keep_recent] if len(self.context) > items_to_keep_recent else []

        # Calculate budget
        recent_tokens = sum(item.token_count for item in recent_items)
        summary_budget = max(0, target_tokens - recent_tokens)

        # Rule-based "summarization" of older content
        # Keep top 20% of older items by importance (simulate lossy compression)
        if older_items:
            older_items_sorted = sorted(older_items, key=lambda x: x.importance, reverse=True)
            keep_count = max(1, int(len(older_items) * 0.20))  # Keep top 20%

            # Only keep items that fit within summary budget
            summarized_items = []
            budget_remaining = summary_budget
            for item in older_items_sorted[:keep_count]:
                if item.token_count <= budget_remaining:
                    summarized_items.append(item)
                    budget_remaining -= item.token_count
                else:
                    break

            # Rebuild context: summarized older + recent
            self.context = summarized_items + recent_items
        else:
            # No older items, just keep recent
            self.context = recent_items

        # Update metrics
        self.current_tokens = self.get_total_tokens()
        tokens_after = self.current_tokens
        items_removed = len(older_items) - len([i for i in self.context if i not in recent_items]) if older_items else 0

        # Record compaction event
        event = {
            "interaction": self.interaction_count,
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "tokens_removed": tokens_before - tokens_after,
            "items_before": len(older_items) + len(recent_items),
            "items_after": len(self.context),
            "items_removed": items_removed,
            "utilization_before": tokens_before / self.target_size,
            "utilization_after": tokens_after / self.target_size,
        }
        self.compaction_events.append(event)

        logger.info(
            f"Compaction complete: "
            f"{tokens_before} → {tokens_after} tokens "
            f"({event['utilization_before']:.1%} → {event['utilization_after']:.1%}), "
            f"removed {items_removed} items"
        )

    def get_total_tokens(self) -> int:
        """Calculate total tokens in current context."""
        return sum(item.token_count for item in self.context)

    def get_utilization(self) -> float:
        """Get current context utilization as fraction (0.0 - 1.0)."""
        return self.current_tokens / self.target_size

    def get_compaction_count(self) -> int:
        """Get number of compaction events that have occurred."""
        return len(self.compaction_events)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary.

        Returns:
            Dictionary containing:
            - Interaction count
            - Current token count and utilization
            - Compaction event count
            - Average tokens before/after compaction
            - Degradation metrics (avg items/tokens lost per compaction)
        """
        if not self.compaction_events:
            avg_tokens_before = 0
            avg_tokens_after = 0
            avg_tokens_removed = 0
            avg_items_removed = 0
        else:
            avg_tokens_before = sum(e["tokens_before"] for e in self.compaction_events) / len(self.compaction_events)
            avg_tokens_after = sum(e["tokens_after"] for e in self.compaction_events) / len(self.compaction_events)
            avg_tokens_removed = sum(e["tokens_removed"] for e in self.compaction_events) / len(self.compaction_events)
            avg_items_removed = sum(e["items_removed"] for e in self.compaction_events) / len(self.compaction_events)

        return {
            "interactions": self.interaction_count,
            "current_tokens": self.current_tokens,
            "current_utilization": self.get_utilization(),
            "context_items": len(self.context),
            "compaction_events": len(self.compaction_events),
            "avg_tokens_before_compaction": avg_tokens_before,
            "avg_tokens_after_compaction": avg_tokens_after,
            "avg_tokens_removed_per_compaction": avg_tokens_removed,
            "avg_items_removed_per_compaction": avg_items_removed,
            "compaction_events_details": self.compaction_events,
        }

    def get_context_by_tier(self, tier: str) -> List[ContextItem]:
        """
        Get context items by tier (for compatibility with ContinuousPruner API).

        Note: Baseline doesn't use tier system, but provides this for API compatibility.
        All items are treated as "HOT" tier.

        Args:
            tier: Tier name (ignored in baseline)

        Returns:
            List of all context items (baseline has no tier separation)
        """
        return self.context.copy()

    def __repr__(self) -> str:
        return (
            f"DiscreteCompactionBaseline("
            f"interactions={self.interaction_count}, "
            f"tokens={self.current_tokens}/{self.target_size}, "
            f"utilization={self.get_utilization():.1%}, "
            f"compactions={self.get_compaction_count()})"
        )
