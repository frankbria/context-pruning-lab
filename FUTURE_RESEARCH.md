# Future Research Directions

## Beyond Phase I & II: Optimization and Machine Learning

This document captures strategic research directions for after the core concept is validated.

---

## 1. Learned Importance Functions

### Current State (Phase I)
**Hard-coded heuristics:**
```python
type_weights = {
    'core_decision': 1.0,
    'architecture': 0.95,
    'requirement': 0.90,
    'user_message': 0.70,
    # ... etc
}

importance = (
    recency * 0.4 +
    access_frequency * 0.2 +
    type_weight * 0.3 +
    pin_bonus * 0.1
)
```

**Problems:**
- Weights are arbitrary (why 0.7 for user_message?)
- Categories themselves are arbitrary (why these 10 types?)
- Component weights (40%, 20%, 30%, 10%) are guesses
- No adaptation to actual coding task performance

### Future Vision: Optimization-Based Approach

**High-Level Strategy:**
Once we have a validated balanced scorecard (metrics we trust), optimize the importance function based on actual outcomes.

#### Phase A: Optimize Within Current Framework
```python
"""
Given:
- Current categorical framework (10 types)
- Current component structure (recency, access, type, pins)
- Validated outcome metrics (code quality, spec adherence, etc.)

Optimize:
- type_weights dictionary values
- Component weight ratios (40/20/30/10 → ?)
- Recency decay rate (currently half-life = 10)

Method:
- Collect data: pruning decisions → outcome quality
- Regression/optimization: find weights maximizing outcomes
- Validate: does optimized function beat hand-crafted?
"""

# Example optimization target:
def objective_function(weights, data):
    """
    Given candidate weights, evaluate on historical data.

    Returns: weighted scorecard performance
    """
    predictions = apply_pruning_with_weights(weights, data)
    outcomes = evaluate_code_quality(predictions)
    return composite_score(outcomes)

# Use black-box optimization (e.g., Bayesian optimization)
optimal_weights = optimize(objective_function, initial_weights)
```

**Estimated Effort:** 2-3 weeks
**Prerequisites:** Phase I complete + outcome data collected
**Risk:** Medium (might overfit to training data)

---

#### Phase B: Learn Natural Categories (Advanced)
```python
"""
Challenge: Current categories (user_message, agent_response, etc.)
are human-defined and potentially suboptimal.

Better approach: Let data reveal natural groupings.
"""

# Step 1: Text Analysis & Representation
def analyze_context_items(all_items):
    """
    Extract semantic representations of all context items.

    Methods:
    - Embeddings: sentence-transformers, code-bert, etc.
    - Features: length, code ratio, question markers, etc.
    - Metadata: position in conversation, references, etc.
    """
    embeddings = []
    for item in all_items:
        # Get semantic embedding
        vec = embed_text(item.content)

        # Add structural features
        features = {
            'has_code': detect_code(item.content),
            'is_question': is_question(item.content),
            'length': len(item.content),
            'references_count': count_references(item),
            'position': item.interaction_number / total_interactions,
            # ... more features
        }

        embeddings.append(concatenate(vec, features))

    return embeddings

# Step 2: Dimensionality Reduction & Clustering
def find_natural_categories(embeddings, n_components=50):
    """
    Use PCA/UMAP to reduce dimensionality,
    then cluster to find natural groupings.
    """
    # Reduce dimensions (e.g., 768-dim embeddings → 50-dim)
    reduced = PCA(n_components=n_components).fit_transform(embeddings)

    # Find natural clusters
    clusters = HDBSCAN().fit_predict(reduced)

    # Identify cluster representatives
    representatives = []
    for cluster_id in unique(clusters):
        cluster_items = reduced[clusters == cluster_id]
        # Centroid or medoid
        rep = compute_representative(cluster_items)
        representatives.append(rep)

    return representatives

# Step 3: Model Representatives → Outcomes
def learn_importance_model(representatives, historical_data):
    """
    Learn: How does similarity to representatives predict importance?

    For each context item:
    - Compute similarity to each representative
    - Use those similarities as features
    - Predict: should this item be retained?
    - Validate: did retaining it improve outcomes?
    """
    X = []  # Similarity vectors
    y = []  # Outcome quality when retained

    for session in historical_data:
        for item in session.context:
            # Feature vector: similarity to each representative
            similarities = [
                cosine_similarity(item.embedding, rep)
                for rep in representatives
            ]

            X.append(similarities)

            # Outcome: did keeping this improve final code quality?
            y.append(session.outcome_quality)

    # Learn model: similarities → importance
    model = GradientBoostingRegressor()
    model.fit(X, y)

    return model

# Step 4: Deploy Learned Importance Function
def calculate_importance_learned(item, representatives, model):
    """
    Replace hand-crafted importance scoring with learned model.
    """
    # Get item's similarity to representatives
    similarities = [
        cosine_similarity(item.embedding, rep)
        for rep in representatives
    ]

    # Model predicts importance based on similarities
    importance = model.predict([similarities])[0]

    # Still apply hard constraints
    if item.tier == "CORE":
        importance = 1.0
    if item.pinned:
        importance = max(importance, 0.95)

    return importance
```

**Estimated Effort:** 3-6 months
**Prerequisites:** Phase A complete + significant data corpus
**Risk:** High (complex ML pipeline, interpretability concerns)

---

### Phased Approach

```
Phase I (Current):    Hand-crafted heuristics
                      ↓
                      Validate concept works
                      ↓
Phase II:             Optimize within heuristic framework
                      ↓
                      Collect data, tune weights
                      ↓
Phase III:            Learn from data
                      ↓
                      Natural categories, learned importance
                      ↓
Phase IV:             Adaptive/online learning
                      ↓
                      Continuously improve from usage
```

---

## 2. Related Future Research

### A. Conversation Coherence Modeling
**Challenge:** Current approach treats items independently
**Future:** Model dependencies (this message requires that context)

**Approach:**
- Build conversation graph (messages → references)
- Prune subgraphs, not individual nodes
- Ensure retained context forms coherent narrative

### B. Multi-Agent Context Sharing
**Challenge:** How do multiple agents share context efficiently?
**Future:** Distributed context with selective synchronization

**Approach:**
- Each agent maintains own pruned context
- Share only CORE/HOT items
- Lazy-load from shared WARM tier

### C. Semantic Compaction
**Challenge:** Current pruning = deletion (lossy)
**Alternative:** Semantic compaction = summarization (less lossy)

**Hybrid Approach:**
- Prune low-importance items (current approach)
- Summarize medium-importance items (future enhancement)
- Retain high-importance items verbatim (current approach)

### D. Context-Aware Token Budgeting
**Challenge:** Fixed target size for all conversation types
**Future:** Adaptive target based on task complexity

**Approach:**
- Simple tasks: 10K token budget
- Complex tasks: 50K token budget
- Learn: task complexity → optimal budget

---

## 3. Prerequisites for Advanced Research

Before pursuing optimization/ML approaches, need:

1. **Validated Metrics** ✅ (Phase I goal)
   - Reliable balanced scorecard
   - Correlation between metrics and real-world quality

2. **Data Corpus** ⏳ (Phase II outcome)
   - 100+ coding sessions with outcomes
   - Diverse task types and complexities
   - Ground truth for "good" vs "bad" pruning decisions

3. **Baseline Performance** ⏳ (Phase I/II goal)
   - Know what hand-crafted heuristics achieve
   - Establish ceiling (unlimited context)
   - Establish floor (aggressive random pruning)

4. **Infrastructure** 🚫 (Not started)
   - Logging/telemetry for pruning decisions
   - Outcome tracking pipeline
   - Experiment framework for A/B testing

---

## 4. Risk Mitigation

### Interpretability Risk
**Problem:** Learned models may be black boxes
**Mitigation:**
- Start with interpretable models (linear, decision trees)
- SHAP values for feature importance
- Always keep hand-crafted baseline for comparison

### Overfitting Risk
**Problem:** Optimize to training data, fail on new scenarios
**Mitigation:**
- Cross-validation with diverse task types
- Regular revalidation on fresh data
- Regularization in optimization

### Complexity Risk
**Problem:** ML pipeline adds maintenance burden
**Mitigation:**
- Only pursue if gains > 15% over hand-crafted
- Keep hand-crafted as fallback
- Phased rollout (A/B test in production)

---

## 5. Timeline Estimate

```
Now:              Phase I (Concept validation)     │ 2-3 months
                                                    │
After Phase I:    Phase II (Comparative)           │ 2-3 months
                                                    │
After Phase II:   Optimization (tune weights)      │ 1-2 months
                                                    │
6-12 months:      ML approach (learned categories) │ 3-6 months
                                                    │
12-18 months:     Online learning / Adaptation     │ Ongoing
```

**Note:** Timeline assumes concept validates in Phase I. If not, pivot or abandon.

---

## 6. Open Research Questions

1. **Generalization:** Do importance functions learned on Python code work for JavaScript? Rust?

2. **Transfer Learning:** Can we bootstrap from existing code understanding models (CodeBERT, etc.)?

3. **Personalization:** Should importance functions adapt per-user? Per-team?

4. **Feedback Loop:** How to collect ground truth for "good pruning decision"? Developer satisfaction? Task success?

5. **Adversarial:** Can agents "game" the importance function to keep unnecessary context?

---

## References for Future Work

### Relevant Papers
- "Learning to Summarize Conversations" (dialog systems)
- "Attention is All You Need" (attention mechanisms = learned importance)
- "Memory Networks" (external memory management)
- "Neural Turing Machines" (learned read/write policies)

### Relevant Techniques
- **Multi-armed Bandits:** Online learning for pruning decisions
- **Reinforcement Learning:** Reward = downstream task success
- **Meta-Learning:** Learn to learn importance across tasks
- **Active Learning:** Query human when uncertain about importance

---

*Document created: 2025-10-29*
*Author: Strategic planning session*
*Status: Aspirational - for post-Phase I consideration*
