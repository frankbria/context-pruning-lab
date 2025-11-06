# Continuous Context Pruning: A 63% Reduction in LLM API Costs
## Preliminary Results from Real-World Software Engineering Tasks

**TL;DR:** We tested a continuous context pruning strategy against a traditional discrete baseline on 15 real software engineering problems from SWE-bench. Continuous pruning achieved a **62.7% reduction in API token usage** and **72.8% smaller peak context sizes** while maintaining **100% success rate**. These preliminary results suggest significant potential for cost savings in long-running LLM applications.

---

## The Problem: Context Window Exhaustion

Large Language Models (LLMs) like Claude, GPT-4, and others have revolutionized software development, but they face a critical constraint: **limited context windows**. As conversations grow longer—especially in complex software engineering tasks—context accumulates rapidly, leading to:

1. **Exponential cost increases** (you pay for every token sent on every API call)
2. **Degraded performance** when approaching context limits
3. **Hard failures** when limits are exceeded
4. **Quality degradation** as context becomes bloated with less relevant information

Current solutions typically use **discrete compaction**: wait until context reaches 80% of the limit, then compress everything to 30%. While this works, it's reactive rather than proactive, and the quality impact of aggressive compaction is not well understood.

## Our Hypothesis: Continuous Is Better Than Discrete

We hypothesized that **continuous, gradual pruning** would outperform discrete compaction by:
- Maintaining consistently low context sizes (avoiding expensive near-limit API calls)
- Preserving context quality (gentle 60% pruning vs aggressive 70% compaction)
- Preventing quality degradation from sudden, drastic context changes

## The Experiment: 15 Real Software Engineering Problems

Rather than synthetic benchmarks, we tested on **real-world GitHub issues** from the [SWE-bench Lite](https://www.swebench.com/) dataset, which contains 300 authentic software engineering problems from popular open-source repositories.

### Experimental Design

**Problems Selected:** 15 problems balanced across 3 repositories
- **psf/requests** (6 problems): HTTP library issues
- **sympy** (4 problems): Symbolic mathematics bugs
- **django** (5 problems): Web framework issues

**Two Strategies Compared:**

1. **Discrete Baseline** (traditional approach)
   - Wait until context reaches 125K tokens (80% of 156K limit)
   - Compact to 30% (aggressive pruning)
   - React only when necessary

2. **Continuous Pruning** (our approach)
   - Prune every 5 turns after a 5-turn warmup
   - Three-phase strategy:
     - **Warmup (turns 1-5):** 10% pruning rate (build initial context)
     - **Ramp (turns 5-15):** 35-60% gradual increase (smooth transition)
     - **Steady (turn 15+):** 60% pruning rate (maintain low context)
   - Proactively maintain small context throughout

**Problem Characteristics:**
- Average 38.4 turns per problem
- Average 37.4 files read per problem
- Real codebases (not simplified test cases)
- Each problem took 7-28 minutes to complete

### Execution Details

- **Model:** Claude Sonnet 4.5 (claude-sonnet-4-20250514)
- **Runtime:** 8 hours 45 minutes total
- **Cost:** $197.33 total ($140.80 discrete + $56.53 continuous)
- **Environment:** Sequential execution (15 discrete, then 15 continuous)

## Results: Dramatic Token Reduction

### Overall Performance

| Metric | Discrete Baseline | Continuous Pruning | Improvement |
|--------|------------------|-------------------|-------------|
| **Total Tokens** | 39,927,662 | 14,910,991 | **-62.7%** 💰 |
| **Avg Tokens/Problem** | 2,661,844 | 994,066 | **-62.7%** |
| **Avg Peak Context** | 96,667 tokens | 26,327 tokens | **-72.8%** 📉 |
| **Success Rate** | 15/15 (100%) | 15/15 (100%) | **Equal** ✅ |
| **Cost Savings** | $140.80 | $56.53 | **-59.9%** |

### Context Management

The most striking difference is in **peak context sizes**:

**Discrete Baseline:**
- Average peak: 96,667 tokens
- Maximum peak: 124,502 tokens
- 7 out of 15 problems triggered compaction
- Context grows until threshold, then drops sharply

**Continuous Pruning:**
- Average peak: 26,327 tokens
- Maximum peak: 44,344 tokens
- 599 pruning operations (avg 39.9 per problem)
- Context stays consistently low throughout

**The difference:** Continuous pruning maintains context at **27% of discrete baseline's peak** on average.

### Cost Analysis

Using Claude Sonnet 4.5 pricing ($3/1M input tokens, $15/1M output):

| Strategy | Input Cost | Output Cost | **Total Cost** |
|----------|-----------|------------|----------------|
| Discrete Baseline | $114.53 | $26.27 | **$140.80** |
| Continuous Pruning | $41.78 | $14.75 | **$56.53** |
| **Savings** | **-$72.75** | **-$11.52** | **-$84.27** |

**Cost Reduction: 59.9%**

**Projected annual savings** (assuming 1,000 problems/year): **$5,618**

For production applications with thousands of users and millions of interactions, this scales to substantial savings.

### Repository-Specific Results

**psf/requests (6 problems):**
- Token reduction: 47.1% average
- Context reduction: 71.9% average
- All 6 problems triggered compaction in discrete mode
- Most consistent behavior across problems

**sympy (4 problems):**
- Token reduction: 52.6% average (excluding trivial 2-turn problem)
- Best individual reduction: 76.1% (sympy-12236)
- Higher variance: 2-41 turns per problem

**django (5 problems):**
- Token reduction: 84.5% average
- Lowest peak contexts: 69K (discrete) vs 18K (continuous)
- Most efficient repository for continuous pruning

## Validation: Comparing N=15 with Previous N=2 Results

Our previous pilot study with N=2 showed promising results. The N=15 experiment **confirms and exceeds** those findings:

| Metric | N=2 Result | N=15 Result | Validation |
|--------|-----------|-------------|--------------|
| Token Reduction | 45.3% | **62.7%** | ✅ **Better** |
| Context Reduction | 68.3% | **72.8%** | ✅ **Better** |
| Success Rate | 100% | 100% | ✅ **Maintained** |
| Compaction Triggers | 50% (1/2) | 46.7% (7/15) | ✅ **Consistent** |

The 7.5x increase in sample size provides much higher confidence in the results.

## The Data Is Open

All experiment data, code, and analysis are available in our GitHub repository:

**Repository:** [github.com/frankbria/context-pruning-lab](https://github.com/frankbria/context-pruning-lab) *(will be made public)*

The repository includes:
- **Full implementation** of both strategies (Python)
- **Raw experiment data** (30 conversation logs, full metrics)
- **Analysis notebooks** and detailed results
- **Reproducible experiment runner**
- **SWE-bench integration** for running your own tests

You can review the methodology, examine individual problem conversations, and even run the experiments yourself with different parameters.

## Important Caveats and Limitations

### These Results Are Preliminary

While promising, these results should be interpreted with appropriate caution:

**1. Limited Sample Size**
- 15 problems is statistically stronger than N=2, but still modest
- We need N=50+ for robust statistical significance
- Current 95% confidence intervals are wide

**2. Single Domain**
- All problems are software engineering tasks
- Results may differ for other domains (creative writing, analysis, etc.)
- Different task types may benefit differently from pruning

**3. Sequential Execution Artifacts**
- Discrete baseline ran first, continuous pruning second
- API rate limiting affected the second batch
- Execution time differences (50% slower for continuous) are likely experimental artifacts, not inherent overhead
- See [EXECUTION_TIME_ANALYSIS.md](https://github.com/frankbria/context-pruning-lab/blob/main/results/experiment_5/EXECUTION_TIME_ANALYSIS.md) for detailed investigation

**4. Simulated Agent Behavior**
- Experiment runner feeds files to the agent sequentially
- Real agents would have more autonomy in file selection
- May affect context growth patterns

**5. No Quality Metrics**
- We measured token usage and success rate only
- Did not measure code quality, solution correctness, or reasoning quality
- Future work should include human evaluation of outputs

**6. Single Model**
- Tested only on Claude Sonnet 4.5
- Different models may respond differently to pruning
- Context management strategies may need tuning per model

### Known Issues

**Execution Time Variance:**
Our experiment showed continuous pruning taking 50% longer to execute, but investigation revealed this is due to API rate limiting affecting the second batch (continuous), not inherent algorithmic overhead. In production with distributed workloads, execution time should be similar or faster due to smaller context sizes. See our [detailed execution time analysis](https://github.com/frankbria/context-pruning-lab/blob/main/results/experiment_5/EXECUTION_TIME_ANALYSIS.md).

**Incomplete Logging:**
Conversation logs capture every 5th turn after turn 5 (to manage log size). This limits detailed turn-by-turn analysis but doesn't affect final metrics.

## Why These Results Matter

Despite the caveats, these preliminary findings are significant:

**1. Dramatic Cost Reduction**
A 60% reduction in API costs is substantial for production applications. For companies spending $100K/month on LLM APIs, this could translate to $60K/month in savings.

**2. Scalable Context Management**
Maintaining context at 27% of baseline peak size means applications can run much longer before hitting limits, enabling more complex multi-turn interactions.

**3. No Quality Degradation**
100% success rate maintained across all 15 problems suggests continuous pruning doesn't harm task completion, though more sophisticated quality metrics are needed.

**4. Production-Ready Implementation**
The continuous pruning strategy is algorithmically simple (local operations, no API calls), adding negligible computational overhead.

## Next Steps: Where We Go From Here

These preliminary results warrant further investigation. Here's what we'd like to explore:

### Immediate Priorities

**1. Larger Sample (N=50-100)**
Run experiments on 50+ problems to achieve statistical significance and tighter confidence intervals.

**2. Quality Evaluation**
- Human evaluation of solution quality
- Automated code quality metrics (correctness, style, completeness)
- Compare reasoning quality in conversation logs

**3. Interleaved Execution**
Re-run experiments with interleaved strategies (alternating discrete/continuous per problem) to eliminate rate limiting bias and validate execution time findings.

### Research Questions

**4. Domain Generalization**
Test on different task types:
- Creative writing (novels, poetry, screenplays)
- Data analysis and visualization
- Mathematical reasoning
- Code review and refactoring

**5. Pruning Strategy Optimization**
- Experiment with different pruning rates (40%, 60%, 80%)
- Test different warmup/ramp configurations
- Adaptive pruning based on task complexity

**6. Multi-Model Validation**
Test on different LLMs:
- GPT-4 Turbo
- Claude Opus
- Gemini Pro
- Open-source models (Llama 3, Mixtral)

**7. Long-Term Context Stability**
- 100+ turn conversations
- Multi-hour coding sessions
- Track context quality degradation over time

**8. Production Deployment**
- A/B testing in real applications
- User satisfaction metrics
- Real-world cost savings validation

## How You Can Contribute

We're releasing this research openly to encourage community involvement:

**For Researchers:**
- Review our methodology and suggest improvements
- Propose alternative pruning strategies
- Help design quality evaluation frameworks
- Contribute to statistical analysis

**For Practitioners:**
- Try the implementation in your applications
- Share production deployment experiences
- Report edge cases and failure modes
- Contribute domain-specific evaluations

**For Open Source Contributors:**
- Improve the codebase (PRs welcome!)
- Add support for more LLM providers
- Implement additional pruning strategies
- Enhance experiment tooling

**Get Involved:**
- ⭐ Star the repository: [github.com/frankbria/context-pruning-lab](https://github.com/frankbria/context-pruning-lab)
- 🐛 Report issues or suggest features
- 💬 Join discussions in GitHub Discussions
- 📧 Contact: [your contact info]

## Conclusion: Promising, But More Work Needed

Our preliminary results show that continuous context pruning can achieve **62.7% reduction in API token usage** while maintaining task success rates. For production LLM applications, this represents potentially transformative cost savings.

However, these are **preliminary findings from a limited sample**. We need:
- ✅ Larger sample sizes (N=50+)
- ✅ Quality evaluation metrics
- ✅ Multi-domain testing
- ✅ Production validation
- ✅ Multi-model testing

The results are **worthy of further study**, and we're committed to continuing this research openly. If you're interested in LLM cost optimization, context management, or production AI applications, we invite you to explore the data, replicate the experiments, and join the conversation.

**The future of LLM applications depends on solving the context window problem. Continuous pruning shows promise as one piece of that puzzle.**

---

## Appendix: Key Technical Details

### Pruning Algorithm Overview

The continuous pruning strategy uses a three-phase approach:

```python
# Phase 1: WARMUP (turns 1-5)
# Goal: Build initial context, minimal pruning
pruning_rate = 0.10  # Keep 90% of context

# Phase 2: RAMP (turns 5-15)
# Goal: Gradual transition to steady-state
pruning_rate = 0.35 + (turn - 5) * 0.025  # 35% → 60%

# Phase 3: STEADY (turn 15+)
# Goal: Maintain low, stable context
pruning_rate = 0.60  # Keep 40% of context
```

Each pruning operation:
1. Calculates importance scores for all context items
2. Sorts by importance (considering recency, type, and relevance)
3. Removes the bottom N% based on pruning rate
4. Never removes CORE-tier items (critical decisions, requirements)

### Discrete Compaction Baseline

```python
# Wait until threshold
if context_size > 125_000:  # 80% of 156K limit
    # Aggressive compaction
    compact_to_target(47_000)  # 30% of limit
```

### Experimental Configuration

```yaml
model: claude-sonnet-4-20250514
max_tokens_per_response: 4096
temperature: 0.7
target_context_size: 156_250  # ~156K tokens
compaction_threshold: 125_000  # 80% of target
max_turns: 50
files_per_problem: 40
content_limit: none  # Full files
```

---

**Published:** November 5, 2025
**Last Updated:** November 5, 2025
**Experiment ID:** swe_bench_exp_20251105_091500
**Repository:** [github.com/frankbria/context-pruning-lab](https://github.com/frankbria/context-pruning-lab)

---

## Further Reading

- [Full N=15 Results Analysis](https://github.com/frankbria/context-pruning-lab/blob/main/results/experiment_5/N15_RESULTS_ANALYSIS.md)
- [Conversation Log Review](https://github.com/frankbria/context-pruning-lab/blob/main/results/experiment_5/CONVERSATION_LOG_REVIEW.md)
- [Execution Time Analysis](https://github.com/frankbria/context-pruning-lab/blob/main/results/experiment_5/EXECUTION_TIME_ANALYSIS.md)
- [Sprint 5 Redux Plan](https://github.com/frankbria/context-pruning-lab/blob/main/SPRINT_5_REDUX_PLAN.md)
- [SWE-bench Official Site](https://www.swebench.com/)

---

*This research is shared openly to advance the field of LLM context management. We welcome feedback, replication attempts, and collaborative improvements.*
