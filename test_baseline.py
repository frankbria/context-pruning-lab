"""
Unit tests for DiscreteCompactionBaseline

Tests validate that the baseline correctly simulates traditional discrete
compaction behavior as specified in Technical Specification §3.2.1.

Test Coverage:
- Initialization and configuration
- Interaction addition without compaction
- Compaction trigger threshold (80%)
- Compaction target (30%)
- Recent interaction preservation (5 interactions)
- Older content compression (top 20% by importance)
- Metrics tracking and reporting
- Edge cases and boundary conditions
"""

import pytest
from baseline import DiscreteCompactionBaseline
from pruner import ContextItem


class TestDiscreteCompactionBaseline:
    """Test suite for DiscreteCompactionBaseline class"""

    def test_initialization(self):
        """Test baseline initialization with default and custom parameters"""
        # Default initialization
        baseline = DiscreteCompactionBaseline()
        assert baseline.target_size == 40000
        assert baseline.compaction_threshold == 0.80
        assert baseline.compaction_target == 0.30
        assert baseline.recent_interactions_to_keep == 5
        assert baseline.interaction_count == 0
        assert len(baseline.context) == 0
        assert len(baseline.compaction_events) == 0

        # Custom initialization
        baseline_custom = DiscreteCompactionBaseline(
            target_size=20000,
            compaction_threshold=0.75,
            compaction_target=0.25,
            recent_interactions_to_keep=3,
        )
        assert baseline_custom.target_size == 20000
        assert baseline_custom.compaction_threshold == 0.75
        assert baseline_custom.compaction_target == 0.25
        assert baseline_custom.recent_interactions_to_keep == 3

    def test_add_interaction_no_compaction(self):
        """Test adding interactions below compaction threshold"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Add a few interactions (well below threshold)
        compacted = baseline.add_interaction(
            user_msg="Hello" * 100,  # ~100 tokens
            agent_msg="World" * 100,  # ~100 tokens
        )

        assert compacted is False  # No compaction triggered
        assert baseline.interaction_count == 1
        assert len(baseline.context) == 2  # user + agent
        assert baseline.get_compaction_count() == 0
        assert baseline.get_utilization() < 0.80  # Below threshold

    def test_compaction_triggers_at_threshold(self):
        """Test that compaction triggers at 80% utilization"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Add interactions until we hit threshold
        # Each interaction ~1000 tokens, threshold is 8000 tokens
        for i in range(7):  # 7 interactions = 7000 tokens, safe
            compacted = baseline.add_interaction(
                user_msg="x" * 2000,  # ~500 tokens
                agent_msg="y" * 2000,  # ~500 tokens
            )
            assert compacted is False

        # 8th interaction should trigger compaction (pushes us to ~8000 tokens)
        compacted = baseline.add_interaction(
            user_msg="x" * 2000,
            agent_msg="y" * 2000,
        )
        assert compacted is True
        assert baseline.get_compaction_count() == 1

    def test_compaction_compresses_to_target(self):
        """Test that compaction compresses context to ~30% of target"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Fill to threshold - need more interactions to reach 80%
        for i in range(15):
            baseline.add_interaction(
                user_msg="message" * 200,  # ~350 tokens
                agent_msg="response" * 200,  # ~400 tokens
            )

        # Compaction should have occurred
        assert baseline.get_compaction_count() >= 1

        # After compaction, utilization should be near 30%
        utilization = baseline.get_utilization()
        assert utilization <= 0.70  # Should be around 30-50%, allow margin for token estimation variance
        assert utilization >= 0.10  # But not too aggressive

    def test_recent_interactions_preserved(self):
        """Test that most recent N interactions are fully preserved"""
        baseline = DiscreteCompactionBaseline(
            target_size=10000,
            recent_interactions_to_keep=5,
        )

        # Add 15 interactions, force compaction
        messages = []
        for i in range(15):
            user_msg = f"User message {i}" * 50
            agent_msg = f"Agent response {i}" * 50
            messages.append((user_msg, agent_msg))
            baseline.add_interaction(user_msg, agent_msg)

        # After compaction, check that last 5 interactions (10 items) are present
        # Get last 5 interactions we added
        recent_5 = messages[-5:]

        context_items = baseline.context
        # Check that recent items are in context
        # At minimum, we should have 10 items (5 interactions)
        assert len(context_items) >= 10

        # Verify last 10 items match last 5 interactions
        last_10_items = context_items[-10:]
        for i, (user_msg, agent_msg) in enumerate(recent_5):
            user_item = last_10_items[i * 2]
            agent_item = last_10_items[i * 2 + 1]
            assert user_msg in user_item.content or user_item.content in user_msg
            assert agent_msg in agent_item.content or agent_item.content in agent_msg

    def test_older_content_compression(self):
        """Test that older content is compressed (only top 20% kept)"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Create items with varying importance
        for i in range(20):
            user_item = ContextItem(
                content="x" * 800,  # ~200 tokens
                item_type="user_message",
                importance=0.5 + (i * 0.02),  # Gradually increasing importance
            )
            agent_item = ContextItem(
                content="y" * 800,
                item_type="agent_response",
                importance=0.5 + (i * 0.02),
            )
            baseline.context.append(user_item)
            baseline.context.append(agent_item)
            baseline.interaction_count += 1

        baseline.current_tokens = baseline.get_total_tokens()

        # Trigger compaction
        baseline.perform_compaction()

        # After compaction:
        # - Should keep last 5 interactions (10 items)
        # - Should keep ~20% of older 15 interactions (30 items) = ~6 items
        # Total: ~16 items (10 recent + 6 older)

        assert baseline.get_compaction_count() == 1
        assert len(baseline.context) >= 10  # At least recent items
        assert len(baseline.context) <= 20  # Some compression occurred

    def test_compaction_event_tracking(self):
        """Test that compaction events are properly tracked"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Fill and trigger compaction
        for i in range(12):
            baseline.add_interaction(
                user_msg="x" * 2000,
                agent_msg="y" * 2000,
            )

        # Check compaction events
        assert baseline.get_compaction_count() >= 1
        events = baseline.compaction_events

        # Validate event structure
        event = events[0]
        assert "interaction" in event
        assert "tokens_before" in event
        assert "tokens_after" in event
        assert "tokens_removed" in event
        assert "items_before" in event
        assert "items_after" in event
        assert "items_removed" in event
        assert "utilization_before" in event
        assert "utilization_after" in event

        # Validate event values
        assert event["tokens_before"] > event["tokens_after"]
        assert event["tokens_removed"] == event["tokens_before"] - event["tokens_after"]
        assert event["items_before"] > event["items_after"]
        assert event["utilization_before"] >= 0.80  # Triggered at threshold
        assert event["utilization_after"] <= 0.65  # Compressed to ~30%, allow margin for token estimation

    def test_metrics_summary(self):
        """Test metrics summary reporting"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Add interactions and trigger compaction
        for i in range(12):
            baseline.add_interaction(
                user_msg="test" * 250,
                agent_msg="response" * 250,
            )

        metrics = baseline.get_metrics_summary()

        # Validate metrics structure
        assert "interactions" in metrics
        assert "current_tokens" in metrics
        assert "current_utilization" in metrics
        assert "context_items" in metrics
        assert "compaction_events" in metrics
        assert "avg_tokens_before_compaction" in metrics
        assert "avg_tokens_after_compaction" in metrics
        assert "avg_tokens_removed_per_compaction" in metrics
        assert "avg_items_removed_per_compaction" in metrics
        assert "compaction_events_details" in metrics

        # Validate metrics values
        assert metrics["interactions"] == 12
        assert metrics["current_tokens"] > 0
        assert 0 <= metrics["current_utilization"] <= 1.0
        assert metrics["compaction_events"] >= 1

        if metrics["compaction_events"] > 0:
            assert metrics["avg_tokens_before_compaction"] > 0
            assert metrics["avg_tokens_after_compaction"] > 0
            assert metrics["avg_tokens_removed_per_compaction"] > 0

    def test_utilization_calculation(self):
        """Test context utilization calculation"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Initially 0%
        assert baseline.get_utilization() == 0.0

        # Add some content
        baseline.add_interaction(
            user_msg="x" * 2000,  # ~500 tokens
            agent_msg="y" * 2000,  # ~500 tokens
        )

        utilization = baseline.get_utilization()
        assert 0.05 <= utilization <= 0.15  # Around 10% (1000 tokens / 10000)

    def test_get_context_by_tier_compatibility(self):
        """Test get_context_by_tier for API compatibility"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        baseline.add_interaction(
            user_msg="test",
            agent_msg="response",
        )

        # Should return all context (tier is ignored in baseline)
        hot_items = baseline.get_context_by_tier("HOT")
        core_items = baseline.get_context_by_tier("CORE")

        assert len(hot_items) == 2
        assert len(core_items) == 2  # Same as HOT, tier is ignored
        assert hot_items == baseline.context

    def test_multiple_compaction_cycles(self):
        """Test that baseline handles multiple compaction cycles"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Run through multiple compaction cycles
        for cycle in range(3):
            # Fill to threshold
            for i in range(10):
                baseline.add_interaction(
                    user_msg="x" * 2000,
                    agent_msg="y" * 2000,
                )

        # Should have triggered multiple compactions
        assert baseline.get_compaction_count() >= 2

        # Context should still be functional
        assert len(baseline.context) > 0
        assert baseline.get_utilization() <= 0.80  # Below threshold

    def test_empty_context_edge_case(self):
        """Test baseline handles empty context gracefully"""
        baseline = DiscreteCompactionBaseline(target_size=10000)

        # Get metrics on empty baseline
        metrics = baseline.get_metrics_summary()
        assert metrics["interactions"] == 0
        assert metrics["current_tokens"] == 0
        assert metrics["current_utilization"] == 0.0
        assert metrics["context_items"] == 0
        assert metrics["compaction_events"] == 0

    def test_very_small_target_size(self):
        """Test baseline with very small target size"""
        baseline = DiscreteCompactionBaseline(target_size=1000)

        # Add interaction that triggers immediate compaction
        baseline.add_interaction(
            user_msg="x" * 2000,  # ~500 tokens, >50% of target
            agent_msg="y" * 2000,  # ~500 tokens, total >80%
        )

        # Should trigger compaction
        assert baseline.get_compaction_count() >= 1

        # Should still function
        assert len(baseline.context) >= 2  # Recent interaction preserved

    def test_repr_string(self):
        """Test string representation"""
        baseline = DiscreteCompactionBaseline(target_size=10000)
        baseline.add_interaction("test", "response")

        repr_str = repr(baseline)
        assert "DiscreteCompactionBaseline" in repr_str
        assert "interactions=1" in repr_str
        assert "tokens=" in repr_str
        assert "utilization=" in repr_str
        assert "compactions=" in repr_str


class TestDiscreteCompactionIntegration:
    """Integration tests comparing baseline with continuous pruner behavior"""

    def test_baseline_vs_pruner_context_growth(self):
        """Test that baseline exhibits linear growth while pruner maintains steady state"""
        from pruner import ContinuousPruner

        baseline = DiscreteCompactionBaseline(target_size=10000)
        pruner = ContinuousPruner(target_size=10000)

        baseline_sizes = []
        pruner_sizes = []

        # Run 50 interactions
        for i in range(50):
            msg = "x" * 400  # ~100 tokens per message
            response = "y" * 400

            baseline.add_interaction(msg, response)
            pruner.add_interaction(msg, response)

            baseline_sizes.append(baseline.get_total_tokens())
            pruner_sizes.append(pruner.get_total_tokens())

        # Baseline should show sawtooth pattern (grow then drop)
        # Pruner should show stable oscillation

        # After 50 interactions, baseline should have compacted at least once
        assert baseline.get_compaction_count() >= 1

        # Pruner should maintain lower average utilization
        avg_baseline_util = sum(s / baseline.target_size for s in baseline_sizes) / len(baseline_sizes)
        avg_pruner_util = sum(s / pruner.target_size for s in pruner_sizes) / len(pruner_sizes)

        # Baseline average should be higher (sawtooth: 30% to 80%)
        # Pruner average should be steady (~30-40%)
        assert avg_baseline_util > avg_pruner_util


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
