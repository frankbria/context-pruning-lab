#!/bin/bash
#
# N=20 Overnight Experiment Runner
# Runs 20 problems with both strategies (discrete baseline, continuous pruning)
# Estimated runtime: 8-10 hours
# Estimated cost: ~$260 ($130 per strategy)
#

set -e

# Configuration
N_PROBLEMS=20
LOG_FILE="/tmp/n20_experiment_$(date +%Y%m%d_%H%M%S).log"
RESULT_DIR="results/experiment_5"
CHECKPOINT_INTERVAL=600  # 10 minutes

echo "======================================================================="
echo "N=20 OVERNIGHT EXPERIMENT"
echo "======================================================================="
echo "Start time: $(date)"
echo "Problems: $N_PROBLEMS"
echo "Log file: $LOG_FILE"
echo "Result dir: $RESULT_DIR"
echo ""
echo "Estimated runtime: 8-10 hours"
echo "Estimated cost: ~\$260 (both strategies)"
echo ""
echo "======================================================================="
echo ""

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY not set"
    echo "Set with: export ANTHROPIC_API_KEY='your-key'"
    exit 1
fi

# Source .env if it exists
if [ -f ".env" ]; then
    echo "Loading .env file..."
    source .env
fi

# Create results directory
mkdir -p "$RESULT_DIR"

# Start experiment
echo "Starting experiment at $(date)"
echo "Running: uv run python experiments/experiment_5/experiment_runner.py $N_PROBLEMS"
echo ""

# Run with full logging
uv run python experiments/experiment_5/experiment_runner.py $N_PROBLEMS 2>&1 | tee "$LOG_FILE"

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================="
    echo "✓ EXPERIMENT COMPLETE"
    echo "======================================================================="
    echo "End time: $(date)"
    echo "Log file: $LOG_FILE"
    echo ""

    # Show final summary
    echo "FINAL SUMMARY:"
    tail -50 "$LOG_FILE" | grep -A 20 "EXPERIMENT SUMMARY" || echo "Summary not found in log"

else
    echo ""
    echo "======================================================================="
    echo "❌ EXPERIMENT FAILED"
    echo "======================================================================="
    echo "End time: $(date)"
    echo "Log file: $LOG_FILE"
    echo ""
    echo "Check log for errors:"
    echo "  tail -100 $LOG_FILE"
    exit 1
fi
