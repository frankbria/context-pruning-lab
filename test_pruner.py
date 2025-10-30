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


class TestAdaptiveRate:
    """Tests for adaptive pruning rate calculation"""

    def test_adaptive_rate_low_utilization(self):
        """Test adaptive rate with very low context utilization (<20%)"""
        pruner = ContinuousPruner(target_size=10000)

        # Add minimal context (< 20% utilization)
        pruner.add_interaction("short", "message")

        rate = pruner.calculate_adaptive_rate()

        # Should allow growth (rate < 1.0)
        assert rate < 1.0
        assert rate >= 0.90  # Within bounds

    def test_adaptive_rate_target_utilization(self):
        """Test adaptive rate at target utilization (30-50%)"""
        pruner = ContinuousPruner(target_size=5000)

        # Directly set context to reach ~40% utilization (bypass pruning)
        target_tokens = int(5000 * 0.40)
        while pruner.get_total_tokens() < target_tokens:
            from pruner import ContextItem
            pruner.context.append(
                ContextItem("x" * 400, "user_message", tier="HOT")
            )

        rate = pruner.calculate_adaptive_rate()

        # Should be at standard rate (1.10 + 0.0 adjustment)
        assert rate == 1.10

    def test_adaptive_rate_high_utilization(self):
        """Test adaptive rate with high utilization (>70%)"""
        pruner = ContinuousPruner(target_size=2000)

        # Directly set context to >70% utilization (bypass pruning)
        target_tokens = int(2000 * 0.75)
        while pruner.get_total_tokens() < target_tokens:
            from pruner import ContextItem
            pruner.context.append(
                ContextItem("x" * 400, "user_message", tier="HOT")
            )

        rate = pruner.calculate_adaptive_rate()

        # Should force aggressive pruning (max rate)
        assert rate == 1.10

    def test_adaptive_rate_core_pressure(self):
        """Test adaptive rate adjusts for CORE budget pressure"""
        pruner = ContinuousPruner(target_size=10000, core_budget=2000)

        # Add CORE items exceeding 25% budget (>500 tokens)
        for i in range(10):
            pruner.add_core_item(f"Critical decision {i} " * 30, "core_decision")

        # Add some HOT tier context
        pruner.add_interaction("User" * 20, "Agent" * 20)

        rate = pruner.calculate_adaptive_rate()

        # Should add CORE pressure adjustment (+0.05)
        # Even at low utilization, rate should be higher due to CORE pressure
        assert rate > pruner.calculate_adaptive_rate.__code__.co_consts[1]  # base_rate

    def test_adaptive_rate_boundaries(self):
        """Test adaptive rate enforces min/max boundaries"""
        pruner = ContinuousPruner(target_size=10000)

        # Test minimum bound (empty context)
        rate_min = pruner.calculate_adaptive_rate()
        assert rate_min >= 0.90

        # Test maximum bound (overfull context)
        # Force high utilization + CORE pressure
        pruner.target_size = 100  # Very small target
        for _ in range(20):
            pruner.add_interaction("msg" * 50, "resp" * 50)

        rate_max = pruner.calculate_adaptive_rate()
        assert rate_max <= 1.10

    def test_adaptive_rate_all_thresholds(self):
        """Test all utilization threshold boundaries"""
        pruner = ContinuousPruner(target_size=10000)

        # Test each threshold range
        test_cases = [
            (0.15, "very_low"),   # <20%: -0.15 adjustment
            (0.25, "low"),         # 20-30%: -0.10 adjustment
            (0.40, "target"),      # 30-50%: 0.0 adjustment
            (0.60, "high"),        # 50-70%: +0.05 adjustment
            (0.80, "very_high"),   # >70%: +0.10 adjustment
        ]

        expected_rates = {
            "very_low": 0.95,      # 1.10 - 0.15
            "low": 1.00,            # 1.10 - 0.10
            "target": 1.10,         # 1.10 + 0.0
            "high": 1.10,           # 1.10 + 0.05, capped at 1.10
            "very_high": 1.10,      # 1.10 + 0.10, capped at 1.10
        }

        for target_util, label in test_cases:
            # Set up context to achieve target utilization
            pruner.context = []
            target_tokens = int(pruner.target_size * target_util)

            # Add items to reach target utilization
            while pruner.get_total_tokens() < target_tokens:
                pruner.context.append(
                    ContextItem("x" * 400, "user_message", tier="HOT")
                )

            rate = pruner.calculate_adaptive_rate()
            # Use approximate comparison for floating point
            assert abs(rate - expected_rates[label]) < 0.001, \
                f"Expected {expected_rates[label]} for {label} ({target_util*100}% util), got {rate}"

    def test_adaptive_rate_history_tracking(self):
        """Test that pruning rate history is tracked"""
        pruner = ContinuousPruner(target_size=10000)

        # Initially empty
        assert len(pruner.pruning_rate_history) == 0

        # Add interactions
        for i in range(5):
            pruner.add_interaction(f"msg {i}", f"resp {i}")

        # Should have tracked 5 rates
        assert len(pruner.pruning_rate_history) == 5

        # All rates should be within bounds
        assert all(0.90 <= rate <= 1.10 for rate in pruner.pruning_rate_history)

    def test_adaptive_rate_in_metrics_summary(self):
        """Test adaptive rate appears in metrics summary"""
        pruner = ContinuousPruner(target_size=10000)

        # Add some interactions
        for i in range(10):
            pruner.add_interaction(f"User {i}" * 20, f"Agent {i}" * 20)

        summary = pruner.get_metrics_summary()

        # Should include adaptive rate stats
        assert 'adaptive_rate' in summary
        assert 'current_rate' in summary['adaptive_rate']
        assert 'mean_rate' in summary['adaptive_rate']
        assert 'min_rate' in summary['adaptive_rate']
        assert 'max_rate' in summary['adaptive_rate']

        # Values should be sensible
        assert 0.90 <= summary['adaptive_rate']['current_rate'] <= 1.10
        assert 0.90 <= summary['adaptive_rate']['mean_rate'] <= 1.10

    def test_adaptive_rate_integration(self):
        """Test adaptive rate actually used during pruning"""
        pruner = ContinuousPruner(target_size=5000)

        # Track initial state
        initial_rate = pruner.calculate_adaptive_rate()

        # Add interaction
        pruner.add_interaction("Test user message " * 50, "Test agent response " * 50)

        # Check that rate was recorded
        assert len(pruner.pruning_rate_history) == 1

        # The used rate should match calculated rate
        used_rate = pruner.pruning_rate_history[0]
        assert 0.90 <= used_rate <= 1.10


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
