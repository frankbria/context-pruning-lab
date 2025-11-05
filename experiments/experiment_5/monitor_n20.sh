#!/bin/bash
#
# Monitor N=20 Experiment Progress
# Checks log file every 10 minutes for progress updates
#

if [ $# -lt 1 ]; then
    echo "Usage: $0 <log_file>"
    echo ""
    echo "Example: $0 /tmp/n20_experiment_20251104_230000.log"
    exit 1
fi

LOG_FILE="$1"
CHECK_INTERVAL=600  # 10 minutes

echo "======================================================================="
echo "N=20 EXPERIMENT MONITOR"
echo "======================================================================="
echo "Log file: $LOG_FILE"
echo "Check interval: ${CHECK_INTERVAL}s (10 min)"
echo "Started: $(date)"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo "======================================================================="
echo ""

check_count=1

while true; do
    if [ ! -f "$LOG_FILE" ]; then
        echo "[$(date +%H:%M:%S)] ⏳ Waiting for log file to appear..."
        sleep 60
        continue
    fi

    echo ""
    echo "======================================================================="
    echo "CHECK #$check_count - $(date +%H:%M:%S)"
    echo "======================================================================="

    # Show current progress
    echo ""
    echo "RECENT ACTIVITY:"
    tail -30 "$LOG_FILE" | grep -E "(STRATEGY|Problem |\[|SUCCESS|FAIL|Compaction|Context max:|Tokens:|ERROR)" | tail -15

    # Count completions
    discrete_count=$(grep -c "discrete_baseline" "$LOG_FILE" | tail -1)
    continuous_count=$(grep -c "continuous_pruning" "$LOG_FILE" | tail -1)

    echo ""
    echo "PROGRESS:"
    echo "  Discrete baseline: $discrete_count/20 problems"
    echo "  Continuous pruning: $continuous_count/20 problems"

    # Check for completion
    if grep -q "EXPERIMENT SUMMARY" "$LOG_FILE"; then
        echo ""
        echo "======================================================================="
        echo "✓ EXPERIMENT COMPLETE!"
        echo "======================================================================="
        echo ""
        tail -50 "$LOG_FILE" | grep -A 20 "EXPERIMENT SUMMARY"
        break
    fi

    # Check for errors
    error_count=$(grep -c "ERROR\|FAILED\|Exception" "$LOG_FILE" || echo "0")
    if [ "$error_count" -gt 0 ]; then
        echo ""
        echo "⚠️  ERRORS DETECTED: $error_count"
        echo "Recent errors:"
        grep "ERROR\|FAILED\|Exception" "$LOG_FILE" | tail -5
    fi

    echo ""
    echo "Next check in 10 minutes..."

    check_count=$((check_count + 1))
    sleep $CHECK_INTERVAL
done

echo ""
echo "Monitoring stopped at $(date)"
