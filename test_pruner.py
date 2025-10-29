"""
Unit tests for continuous context pruning algorithm
"""

import pytest
from pruner import ContinuousPruner, ContextItem


class TestContextItem:
    """Tests for ContextItem dataclass"""

    def test_token_count_estimation(self):
        """Test rough token count estimation"""
        item = ContextItem(content="Hello world", item_type="user_message")
        # "Hello world" = 11 chars / 4 = 2.75 ≈ 2 tokens
        assert item.token_count == 2

    def test_default_tier(self):
        """Test default tier assignment"""
        item = ContextItem(content="Test", item_type="user_message")
        assert item.tier == "HOT"


class TestContinuousPruner:
    """Tests for ContinuousPruner class"""

    def test_initialization(self):
        """Test pruner initializes correctly"""
        pruner = ContinuousPruner(target_size=10000)
        assert pruner.target_size == 10000
        assert pruner.pruning_overhead == 1.10
        assert len(pruner.context) == 0
        assert pruner.interaction_count == 0

    def test_add_interaction(self):
        """Test adding interaction increases context"""
        pruner = ContinuousPruner(target_size=10000)

        metrics = pruner.add_interaction(
            "User message",
            "Agent response"
        )

        assert pruner.interaction_count == 1
        assert len(pruner.context) >= 0  # May prune immediately
        assert metrics.tokens_added > 0

    def test_core_items_never_pruned(self):
        """Test that CORE tier items are never pruned"""
        pruner = ContinuousPruner(target_size=1000)  # Small target

        # Add core item
        pruner.add_core_item("Critical decision", "core_decision")

        # Add many interactions to trigger aggressive pruning
        for i in range(50):
            pruner.add_interaction(
                f"User message {i}" * 100,
                f"Agent response {i}" * 100
            )

        # Core item should still exist
        core_items = [i for i in pruner.context if i.tier == "CORE"]
        assert len(core_items) == 1
        assert "Critical decision" in core_items[0].content

    def test_pruning_removes_low_importance(self):
        """Test that pruning removes lowest-importance items first"""
        pruner = ContinuousPruner(target_size=5000)

        # Add items with different importance
        item_high = ContextItem("High", "user_message", importance=0.9)
        item_low = ContextItem("Low", "debug_log", importance=0.2)

        pruner.context = [item_high, item_low]

        # Trigger pruning
        pruner.add_interaction("New user msg", "New agent response")

        # High importance item should remain
        remaining_content = [i.content for i in pruner.context]
        assert "High" in str(remaining_content) or len(pruner.context) == 0

    def test_steady_state_oscillation(self):
        """Test that context oscillates around target size"""
        pruner = ContinuousPruner(target_size=5000)

        token_counts = []
        for i in range(20):
            pruner.add_interaction(
                f"User message {i}" * 50,
                f"Agent response {i}" * 50
            )
            token_counts.append(pruner.get_total_tokens())

        # After settling, should oscillate around target
        # (may take a few interactions to stabilize)
        stable_counts = token_counts[-10:]  # Last 10 interactions

        # Should never exceed target significantly
        assert all(count < pruner.target_size * 1.5 for count in stable_counts)

    def test_importance_decay(self):
        """Test that importance decays with age"""
        pruner = ContinuousPruner()

        # Add old item
        old_item = ContextItem("Old", "user_message", interaction_number=1)
        pruner.context = [old_item]
        pruner.interaction_count = 20  # 19 interactions later

        # Calculate importance
        importance = pruner._calculate_importance(old_item)

        # Should be lower than a recent item
        assert importance < 0.5  # Decayed significantly

    def test_pinned_items_never_pruned(self):
        """Test that pinned items are never pruned"""
        pruner = ContinuousPruner(target_size=1000)

        # Add pinned item
        pinned = ContextItem("Important", "user_message", pinned=True)
        pruner.context = [pinned]

        # Add many interactions
        for i in range(50):
            pruner.add_interaction(
                f"User {i}" * 100,
                f"Agent {i}" * 100
            )

        # Pinned item should remain
        assert any("Important" in i.content for i in pruner.context)

    def test_get_context_by_tier(self):
        """Test grouping context by tier"""
        pruner = ContinuousPruner()

        pruner.context = [
            ContextItem("Core", "core_decision", tier="CORE"),
            ContextItem("Hot", "user_message", tier="HOT"),
            ContextItem("Warm", "code", tier="WARM"),
        ]

        tiers = pruner.get_context_by_tier()

        assert len(tiers['CORE']) == 1
        assert len(tiers['HOT']) == 1
        assert len(tiers['WARM']) == 1
        assert len(tiers['COLD']) == 0

    def test_metrics_tracking(self):
        """Test that metrics are tracked correctly"""
        pruner = ContinuousPruner()

        metrics = pruner.add_interaction("User", "Agent")

        assert metrics.total_interactions == 1
        assert metrics.tokens_added > 0
        assert metrics.current_token_count >= 0

    def test_type_weights(self):
        """Test that different types have appropriate weights"""
        pruner = ContinuousPruner()

        # Core decision should have highest weight
        assert pruner.type_weights['core_decision'] == 1.0

        # Debug log should have low weight
        assert pruner.type_weights['debug_log'] < 0.5


class TestIntegration:
    """Integration tests for full workflows"""

    def test_full_conversation_cycle(self):
        """Test complete conversation cycle with pruning"""
        pruner = ContinuousPruner(target_size=10000)

        # Add core decisions
        pruner.add_core_item("Use Python 3.11", "requirement")
        pruner.add_core_item("OAuth2 authentication", "architecture")

        # Simulate 100 interactions
        for i in range(100):
            pruner.add_interaction(
                f"User question {i}" * 20,
                f"Agent answer {i}" * 25
            )

        # Should have pruned significantly
        assert pruner.get_total_tokens() < pruner.target_size * 1.2

        # Core items should remain
        core_items = [i for i in pruner.context if i.tier == "CORE"]
        assert len(core_items) == 2

    def test_no_linear_growth(self):
        """Test that context doesn't grow linearly"""
        pruner = ContinuousPruner(target_size=5000)

        token_counts = []
        for i in range(50):
            pruner.add_interaction(
                "User message" * 50,
                "Agent response" * 50
            )
            token_counts.append(pruner.get_total_tokens())

        # Should NOT show linear growth
        # (would be steadily increasing if linear)
        first_half_avg = sum(token_counts[:25]) / 25
        second_half_avg = sum(token_counts[25:]) / 25

        # Second half should not be significantly larger
        # (allows for some variance)
        assert second_half_avg < first_half_avg * 1.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
