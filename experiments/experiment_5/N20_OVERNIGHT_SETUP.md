# N=20 Overnight Experiment Setup Guide
## Sprint 5: Statistical Validation

## Overview

This guide prepares for running the N=20 experiment overnight to validate the N=2 results with statistical significance.

**Goal:** Run 20 SWE-bench Lite problems with both strategies to confirm:
- Continuous pruning achieves ~45% token reduction (statistically significant)
- Continuous pruning maintains ~68% lower peak context
- 100% success rate is maintained
- Compaction behavior is consistent

## Estimated Costs & Runtime

**Runtime:**
- 8-10 hours total
- ~25 minutes per problem per strategy
- Both strategies run in sequence

**Cost Estimate:**
- N=2 experiment: $26.51 ($17.66 discrete + $10.85 continuous)
- N=20 projection: **~$265** ($176 discrete + $108 continuous)
- Expected savings with continuous: **~$68 (38%)**

## Prerequisites

1. ✓ API key configured: `ANTHROPIC_API_KEY` in `.env`
2. ✓ Current codebase validated (N=2 experiment complete)
3. ✓ Sufficient API credits (~$300 recommended for safety)
4. ✓ Stable machine (no sleep/hibernation for 10 hours)

## Files Prepared

1. **experiment_runner.py** (modified)
   - Now accepts command line argument for n_problems
   - Usage: `uv run python experiment_runner.py 20`

2. **run_n20_overnight.sh**
   - Launch script with logging
   - Handles errors and reports status
   - Auto-creates timestamped log files

3. **monitor_n20.sh**
   - Progress monitoring every 10 minutes
   - Shows completion status, errors, summaries
   - Usage: `./monitor_n20.sh /tmp/n20_experiment_*.log`

## Launch Instructions

### Option A: Direct Launch (Recommended)

```bash
# Navigate to project root
cd ~/projects/context-pruning-lab

# Make scripts executable
chmod +x experiments/experiment_5/run_n20_overnight.sh
chmod +x experiments/experiment_5/monitor_n20.sh

# Launch experiment (runs in foreground)
./experiments/experiment_5/run_n20_overnight.sh
```

**Note:** This will run for 8-10 hours. Keep terminal open or use screen/tmux.

### Option B: Background with nohup

```bash
# Launch in background
nohup ./experiments/experiment_5/run_n20_overnight.sh > /tmp/n20_nohup.log 2>&1 &

# Save PID
echo $! > /tmp/n20_experiment.pid

# Monitor progress
tail -f /tmp/n20_experiment_*.log
```

### Option C: With screen/tmux (Best for SSH)

```bash
# Start screen session
screen -S n20_experiment

# Launch experiment
./experiments/experiment_5/run_n20_overnight.sh

# Detach: Ctrl+A then D
# Reattach: screen -r n20_experiment
```

## Monitoring During Run

### Active Monitoring

```bash
# In separate terminal, run monitor script
./experiments/experiment_5/monitor_n20.sh /tmp/n20_experiment_20251104_*.log
```

### Manual Checks

```bash
# Check last 50 lines
tail -50 /tmp/n20_experiment_*.log

# Check for errors
grep -i "error\|fail\|exception" /tmp/n20_experiment_*.log | tail -20

# Check progress
grep -E "Problem |SUCCESS|Compaction" /tmp/n20_experiment_*.log | tail -30

# Watch live
tail -f /tmp/n20_experiment_*.log
```

## Expected Progress

### Timeline

```
Hour 0-2:   Discrete baseline problems 1-5
Hour 2-4:   Discrete baseline problems 6-10
Hour 4-5:   Discrete baseline problems 11-15
Hour 5-6:   Discrete baseline problems 16-20
Hour 6-8:   Continuous pruning problems 1-10
Hour 8-10:  Continuous pruning problems 11-20
```

### Milestones

- [ ] 2 hours: 5 problems complete (discrete)
- [ ] 4 hours: 10 problems complete (discrete)
- [ ] 6 hours: All discrete complete, continuous starting
- [ ] 8 hours: 10 problems complete (continuous)
- [ ] 10 hours: All complete, summary available

## Results Location

After completion:
```
results/experiment_5/
├── swe_bench_exp_YYYYMMDD_HHMMSS.json  (raw results)
└── conversations/  (40 conversation logs: 20 problems × 2 strategies)
```

Log file:
```
/tmp/n20_experiment_YYYYMMDD_HHMMSS.log  (full execution log)
```

## Validation Checklist

After experiment completes, validate:

- [ ] Both strategies completed 20/20 problems
- [ ] Token efficiency: Continuous ~45% fewer tokens
- [ ] Context management: Continuous ~68% lower peak
- [ ] Success rate: 100% for both strategies
- [ ] Compaction events: Discrete triggers appropriately
- [ ] No catastrophic failures or API errors
- [ ] Results saved correctly to JSON
- [ ] Conversation logs captured

## Troubleshooting

### Experiment Stops Early

```bash
# Check last errors
tail -100 /tmp/n20_experiment_*.log | grep -i "error\|fail"

# Check API key
echo $ANTHROPIC_API_KEY | cut -c1-10

# Resume if needed (will skip completed problems)
./experiments/experiment_5/run_n20_overnight.sh
```

### Out of API Credits

- Monitor spending at: https://console.anthropic.com/settings/billing
- Add credits before resuming
- Results up to failure point are saved

### Machine Sleep/Network Issues

- Ensure "never sleep" in power settings
- Use tmux/screen to survive SSH disconnects
- Consider cloud VM for stability

## Post-Experiment Actions

After successful completion:

1. **Document results**
   ```bash
   # Create analysis document
   # Compare N=20 vs N=2 results
   # Calculate confidence intervals
   ```

2. **Commit results**
   ```bash
   git add results/experiment_5/swe_bench_exp_*.json
   git add results/experiment_5/conversations/
   git commit -m "Sprint 5: N=20 statistical validation results"
   git push
   ```

3. **Create summary report**
   - Update SPRINT_5_REDUX_RESULTS.md
   - Document statistical significance
   - Prepare production recommendation

## Safety Notes

- ⚠️  **Cost:** Experiment costs ~$265. Monitor API usage.
- ⚠️  **Time:** Requires 8-10 hours uninterrupted.
- ⚠️  **Machine:** Don't let machine sleep/hibernate.
- ⚠️  **Credits:** Ensure sufficient API credits before starting.

## Quick Reference

```bash
# Launch
./experiments/experiment_5/run_n20_overnight.sh

# Monitor
./experiments/experiment_5/monitor_n20.sh /tmp/n20_experiment_*.log

# Check progress
tail -50 /tmp/n20_experiment_*.log

# Check for errors
grep -i error /tmp/n20_experiment_*.log

# Stop (if needed)
pkill -f "experiment_runner.py"
```

## Status

- [x] Code modified for N argument
- [x] Launch script created
- [x] Monitor script created
- [x] Documentation complete
- [ ] **READY TO LAUNCH** ✓

Launch when ready with:
```bash
cd ~/projects/context-pruning-lab
chmod +x experiments/experiment_5/run_n20_overnight.sh
./experiments/experiment_5/run_n20_overnight.sh
```
