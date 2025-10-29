# Quick Start Guide: Implementation Workflow

## For the Busy Developer

This guide provides a quick overview of the [IMPLEMENTATION_WORKFLOW.md](../IMPLEMENTATION_WORKFLOW.md) to get you started immediately.

---

## TL;DR

**Project:** Phase I concept validation of continuous context pruning
**Duration:** 12 weeks (6 sprints × 2 weeks)
**Team:** 1 developer (you!)
**Goal:** Prove continuous pruning beats discrete compaction

---

## Week-by-Week Overview

### Weeks 1-2: Sprint 1 - Get Adaptive Pruning Working
**Goal:** Make pruning rate adapt to context utilization

**What to Build:**
- `calculate_adaptive_rate()` function (spec §2.2.2)
- Integration into existing pruner
- Update Experiment 1 to use it

**Success:** Context converges to steady state from any starting point

---

### Weeks 3-4: Sprint 2 - CORE Budget & Baseline
**Goal:** Protect critical content, build comparison baseline

**What to Build:**
- `CoreBudgetEnforcer` class (prevents CORE >25% budget)
- `DiscreteCompactionBaseline` class (rule-based compaction simulator)
- Token estimation accuracy tracking

**Success:** CORE never violated, baseline behaves like real compaction

---

### Weeks 5-6: Sprint 3 - SWE-bench Infrastructure
**Goal:** Build testing infrastructure for code quality experiment

**What to Build:**
- Task selection (50 tasks from SWE-bench-Lite)
- Conversation script generator (extend to 15-30 turns)
- Test harness for running experiments
- Mock agent for testing

**Success:** End-to-end test runs with mock agent

---

### Weeks 7-8: Sprint 4 - PRIMARY EXPERIMENT ⚠️ CRITICAL
**Goal:** Prove continuous pruning works for real coding tasks

**What to Build:**
- 4 quality metrics (completion, spec adherence, code quality, consistency)
- Real LLM agent integration
- Execute 100 task runs (50 tasks × 2 strategies)

**Success:** Meet ≥2 of 3 acceptance criteria (see workflow doc)

**⚠️ Decision Gate:** If this fails significantly, may need to iterate before continuing

---

### Weeks 9-10: Sprint 5 - Additional Validation
**Goal:** Complete remaining experiments and metrics

**What to Build:**
- Experiment 2: Convergence testing
- Experiment 3: Information preservation testing
- Comprehensive metrics collection
- Cross-experiment analysis

**Success:** All experiments validate hypothesis

---

### Weeks 11-12: Sprint 6 - Wrap Up
**Goal:** Write it up, make it reproducible, decide Phase II

**What to Build:**
- Technical research report (15-25 pages)
- Finalized repository (tests, docs, examples)
- Phase II decision document
- Final presentation

**Success:** Phase I complete, clear recommendation on Phase II

---

## Critical Path (What Blocks Everything)

```
Adaptive Rate → CORE Budget → SWE Infrastructure → Experiment 4 → Report
```

**Do these first.** Everything else can flex.

---

## Quick Reference: Sprint Priorities

### Sprint 1 (P0 - Must Have)
- T1.1: `calculate_adaptive_rate()` - 8 hours
- T1.2: Integrate into pruner - 6 hours
- T1.4: Update Experiment 1 - 8 hours

### Sprint 2 (P0 - Must Have)
- T2.1: `CoreBudgetEnforcer` - 10 hours
- T2.2: CORE integration - 6 hours
- T2.4: Discrete baseline - 12 hours

### Sprint 3 (P0 - Must Have)
- T3.1: Task selection - 10 hours
- T3.2: Script generator - 12 hours
- T3.4: Test harness - 10 hours

### Sprint 4 (P0 - Must Have) ⭐
- T4.1: Quality metrics - 12 hours
- T4.2: Real agent - 10 hours
- T4.4-T4.5: Execute experiments - 12 hours

### Sprint 5 (P1 - Should Have)
- T5.1-T5.2: Experiment 2 - 14 hours
- T5.3-T5.4: Experiment 3 - 18 hours
- T5.6: Cross-analysis - 8 hours

### Sprint 6 (P1 - Should Have)
- T6.2-T6.3: Technical report - 18 hours
- T6.4-T6.5: Repository finalization - 14 hours

---

## Resource Budgets

**Time:** 240 hours total (20 hours/week × 12 weeks)
**Money:** ~$50 for LLM API calls
**Storage:** ~1GB for data and results

---

## When Things Go Wrong

### Problem: Adaptive rate doesn't converge (Sprint 1)
**Solution:** Tune thresholds empirically, document actual behavior, adjust bounds

### Problem: Experiment 4 results fail acceptance criteria (Sprint 4) ⚠️
**Solution:**
- Analyze failure modes
- Adjust algorithm parameters
- Re-run experiment (2-3 week iteration)
- Reassess at new decision gate

### Problem: Running out of time
**Solution:**
- Sprint 1-4 are P0 (critical path) - protect these
- Sprint 5 experiments can be simplified
- Sprint 6 can extend 2-3 days if needed

### Problem: API costs too high
**Solution:**
- Use Claude Sonnet instead of Opus (~3x cheaper)
- Reduce task count from 50 to 30 if necessary
- Run experiments in batches to monitor costs

---

## Success Checklist

**Phase I is successful if you can check these boxes:**

### Context Stability ✅
- [ ] Linear growth coefficient < 0.01
- [ ] Steady-state oscillation < 15% of target
- [ ] Max utilization < 60%
- [ ] Convergence time < 30 interactions

### Information Preservation ✅
- [ ] Continuous pruning recall > 90%
- [ ] Discrete baseline recall < 70%
- [ ] Relative improvement ≥ 25%

### Code Quality (PRIMARY) ✅
- [ ] Task completion ≥ 90% of baseline
- [ ] Spec adherence ≥ 95% of baseline
- [ ] Code quality ≥ baseline

### System Integrity ✅
- [ ] Zero CORE budget violations
- [ ] Adaptive rate works correctly
- [ ] Token estimation accurate enough

**Need:** ALL stability metrics + ALL preservation metrics + ≥2 of 3 primary code quality metrics

---

## Daily Workflow

1. **Morning:** Review sprint backlog, pick highest priority task
2. **Work:** Implement task following acceptance criteria
3. **Test:** Run unit tests, verify acceptance criteria met
4. **Document:** Update docs, add docstrings
5. **Commit:** Commit working changes to git
6. **Evening:** Update sprint progress, identify blockers

---

## Weekly Workflow

1. **Monday:** Sprint planning (if new sprint), review week's tasks
2. **Wednesday:** Mid-week check-in, adjust if behind
3. **Friday:** Sprint demo (every 2 weeks), week review, commit all changes

---

## Tools You'll Need

**Development:**
- Python 3.9+
- pytest (testing)
- git (version control)
- Your favorite IDE

**Experiments:**
- Claude API access (or equivalent LLM)
- Jupyter notebooks (optional, for analysis)
- Matplotlib/seaborn (visualizations)

**Documentation:**
- Markdown editor
- PDF generator (for final report)

---

## First Steps (Start Here!)

### Day 1 Tasks:
1. ✅ Read this Quick Start Guide
2. ✅ Skim [IMPLEMENTATION_WORKFLOW.md](../IMPLEMENTATION_WORKFLOW.md)
3. ✅ Review [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §2.2.2 (adaptive rate formula)
4. ⬜ Set up development environment
5. ⬜ Run existing tests: `pytest test_pruner.py -v`
6. ⬜ Read existing code: `pruner.py`, `experiment_1_linear_growth.py`

### Day 2 Tasks:
1. ⬜ Start T1.1: Implement `calculate_adaptive_rate()`
2. ⬜ Write unit tests as you go
3. ⬜ Verify formula matches spec

### Day 3 Tasks:
1. ⬜ Complete T1.1
2. ⬜ Start T1.2: Integration into pruner
3. ⬜ Run integration tests

---

## Questions to Ask Yourself

**End of Sprint 1:**
- Does adaptive rate converge from empty context?
- Does it converge from 80% full context?
- Do all unit tests pass?

**End of Sprint 2:**
- Has CORE budget ever been violated (should be NO)?
- Does baseline compaction feel realistic?
- Are we ready for SWE-bench work?

**End of Sprint 4 (CRITICAL):**
- Do results meet ≥2 of 3 acceptance criteria?
- If not, what failed and why?
- Should we continue, iterate, or pivot?

**End of Sprint 6:**
- Can someone reproduce our experiments from the repo?
- Does the technical report tell a compelling story?
- Do we recommend Phase II: yes, maybe, or no?

---

## Get Help

**Stuck on implementation?**
- Review relevant section in TECHNICAL_SPECIFICATION.md
- Check existing code for patterns
- Write a test first (test-driven development)

**Falling behind schedule?**
- Review critical path (don't let it slip!)
- Defer non-P0 tasks if necessary
- Ask for schedule review if >3 days behind

**Results not meeting acceptance criteria?**
- Analyze failure systematically (don't guess)
- Check unit tests are all passing first
- Review algorithm parameters
- Consider iteration cycle before giving up

---

## Remember

**Phase I is research, not production.**

The goal is to **prove the concept works**, not to build production-ready code.

- It's okay to use simple token estimation (chars/4)
- It's okay to use rule-based baseline (not LLM summarization)
- It's okay if code isn't optimized for performance

**It's NOT okay to:**
- Skip critical tests (especially CORE budget enforcement)
- Ignore failing acceptance criteria
- Rush through experiments without proper analysis

---

## You've Got This! 🚀

This is a well-scoped research project with clear milestones and success criteria. Follow the sprint plan, ask questions when stuck, and iterate when needed.

**Good luck with Sprint 1!**

---

**Next:** Start with [IMPLEMENTATION_WORKFLOW.md](../IMPLEMENTATION_WORKFLOW.md) Sprint 1 detailed task list.
