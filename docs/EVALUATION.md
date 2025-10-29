# Evaluation Framework

This document defines how to measure CareConnect's success against its target metrics.

## Target Metrics

| Metric | Target | Current Implementation |
|--------|--------|------------------------|
| Task Completion Rate | ≥90% | Tracked via booking events |
| Response Latency (p50) | <2s | Prometheus histograms |
| Response Latency (p90) | <5s | Prometheus histograms |
| Ambiguity Resolution | ≥80% | Clarification → success tracking |
| User Satisfaction | ≥4/5 | Feedback endpoint |

## Metric Definitions

### 1. Task Completion Rate

**Definition**: Percentage of user intents successfully fulfilled.

**Formula**:
```
Task Completion Rate = (Successful Tasks / Total Tasks) × 100
```

**What Counts as Success**:
- **Booking**: Appointment created with confirmation code
- **Modification**: Appointment time changed
- **Cancellation**: Appointment status set to cancelled
- **Information**: User receives relevant answer (implicit success if conversation continues positively)

**What Counts as Failure**:
- User abandons conversation mid-task
- Agent unable to fulfill after 10 tool calls
- User expresses dissatisfaction ("this isn't working", "never mind")

**Implementation**:

Track via `booking_event` table:
```sql
SELECT 
  COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
  COUNT(*) as total,
  COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as completion_rate
FROM booking_event
WHERE action IN ('book', 'modify', 'cancel')
  AND created_at >= '2025-01-01'
```

**API Endpoint**: `GET /api/v1/eval/kpis`

**Code Location**: `backend/app/api/v1/metrics.py`

### 2. Response Latency

**Definition**: Time from user message submission to assistant response received.

**Measured By**: Prometheus histogram buckets

**Histogram Configuration**:
```python
response_duration = Histogram(
    'agent_response_duration_seconds',
    'Time to generate agent response',
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0]
)
```

**PromQL Queries**:

P50 (median):
```promql
histogram_quantile(0.5, 
  rate(agent_response_duration_seconds_bucket[5m])
)
```

P90 (90th percentile):
```promql
histogram_quantile(0.9, 
  rate(agent_response_duration_seconds_bucket[5m])
)
```

P99 (99th percentile):
```promql
histogram_quantile(0.99, 
  rate(agent_response_duration_seconds_bucket[5m])
)
```

**Breakdown by Component**:

```python
# Instrument each component
with openai_duration.time():
    response = await openai.chat.completions.create(...)

with rag_duration.time():
    chunks = await rag_service.retrieve(query)

with db_duration.time():
    appointment = await db.execute(query)
```

**Alerting**:
- Warning: P50 > 2s for 5 minutes
- Critical: P90 > 5s for 5 minutes

### 3. Ambiguity Resolution Rate

**Definition**: Percentage of ambiguous queries successfully resolved through clarification.

**Formula**:
```
Ambiguity Resolution = (Resolved Clarifications / Total Clarifications) × 100
```

**Detection**:

An ambiguity occurs when:
- Agent asks a clarifying question (identified by `?` in response)
- Multiple options presented (e.g., "Which doctor: Dr. A or Dr. B?")
- Missing required parameter (date, provider, etc.)

**Tracking**:

Add to conversation metadata:
```json
{
  "conversation_id": "conv_123",
  "turn": 3,
  "clarification_needed": true,
  "clarification_type": "provider_selection",
  "resolved": true,
  "resolution_turns": 1
}
```

**SQL Query**:
```sql
SELECT 
  COUNT(CASE WHEN resolved = true THEN 1 END) as resolved,
  COUNT(*) as total_clarifications,
  COUNT(CASE WHEN resolved = true THEN 1 END) * 100.0 / COUNT(*) as resolution_rate
FROM conversation_metadata
WHERE clarification_needed = true
  AND created_at >= NOW() - INTERVAL '7 days'
```

**Implementation Status**: ⚠️ Requires additional metadata tracking (TODO)

### 4. User Satisfaction

**Definition**: Average user rating and positive feedback percentage.

**Measurement Methods**:

1. **Explicit Rating** (thumbs up/down):
   ```json
   POST /api/v1/agent/feedback
   {
     "conversation_id": "conv_123",
     "rating": 5,  // 1-5 scale
     "feedback_text": "Very helpful!"
   }
   ```

2. **Implicit Signals**:
   - Task completion (positive signal)
   - Conversation abandonment (negative signal)
   - Return user (positive signal)

**Calculation**:
```sql
SELECT 
  AVG(rating) as avg_satisfaction,
  COUNT(CASE WHEN rating >= 4 THEN 1 END) * 100.0 / COUNT(*) as satisfaction_rate,
  COUNT(CASE WHEN rating = 5 THEN 1 END) as promoters,
  COUNT(CASE WHEN rating <= 2 THEN 1 END) as detractors
FROM feedback
WHERE created_at >= NOW() - INTERVAL '30 days'
```

**Net Promoter Score (NPS)**:
```
NPS = (% Promoters) - (% Detractors)
```

Where:
- Promoters: rating = 5
- Passives: rating = 3 or 4
- Detractors: rating = 1 or 2

## Evaluation Reports

### Daily Report

Run every morning to summarize previous day:

```python
# backend/scripts/daily_eval_report.py
import asyncio
from app.api.v1.metrics import calculate_kpis

async def main():
    kpis = await calculate_kpis(
        start_date="2025-01-14",
        end_date="2025-01-15"
    )
    
    print(f"""
    CareConnect Daily Report - 2025-01-14
    =====================================
    
    Task Completion:     {kpis.task_completion_rate:.1f}% (target: ≥90%)
    Response Time (P50): {kpis.p50_latency:.2f}s (target: <2s)
    Response Time (P90): {kpis.p90_latency:.2f}s (target: <5s)
    User Satisfaction:   {kpis.avg_satisfaction:.1f}/5 (target: ≥4/5)
    
    Total Conversations: {kpis.total_conversations}
    Successful Bookings: {kpis.successful_bookings}
    Failed Bookings:     {kpis.failed_bookings}
    """)

if __name__ == "__main__":
    asyncio.run(main())
```

### Weekly Trend Analysis

Compare week-over-week metrics:

```python
# Identify regression or improvement
def trend_analysis(current_week, previous_week):
    metrics = [
        "task_completion_rate",
        "p50_latency",
        "avg_satisfaction"
    ]
    
    for metric in metrics:
        current = getattr(current_week, metric)
        previous = getattr(previous_week, metric)
        change = ((current - previous) / previous) * 100
        
        if metric == "p50_latency":
            # Lower is better
            status = "✅ Improved" if change < 0 else "⚠️ Regressed"
        else:
            # Higher is better
            status = "✅ Improved" if change > 0 else "⚠️ Regressed"
        
        print(f"{metric}: {change:+.1f}% - {status}")
```

## A/B Testing Framework

### Experiment Design

**Hypothesis**: Changing system prompt to be more concise will reduce response latency.

**Groups**:
- Control (A): Current system prompt (50% traffic)
- Treatment (B): Concise prompt (50% traffic)

**Assignment**:
```python
def assign_variant(user_id: int) -> str:
    # Stable assignment based on user_id
    return "B" if user_id % 2 == 0 else "A"
```

**Instrumentation**:
```python
variant = assign_variant(current_user.id)

if variant == "B":
    system_prompt = CONCISE_SYSTEM_PROMPT
else:
    system_prompt = DEFAULT_SYSTEM_PROMPT

# Log variant with metrics
response_duration.labels(variant=variant).observe(duration)
```

### Statistical Significance

**Minimum Sample Size**: 1000 conversations per variant

**Significance Test**: Two-sample t-test

```python
from scipy import stats

# Compare P50 latency between variants
control_latencies = get_latencies(variant="A")
treatment_latencies = get_latencies(variant="B")

t_stat, p_value = stats.ttest_ind(control_latencies, treatment_latencies)

if p_value < 0.05:
    print(f"Statistically significant difference (p={p_value:.4f})")
else:
    print(f"No significant difference (p={p_value:.4f})")
```

### Rollout Decision

Launch treatment if:
1. P-value < 0.05 (statistically significant)
2. Treatment shows ≥5% improvement in target metric
3. No regression in other metrics (task completion, satisfaction)

## Synthetic Evaluation

Test agent performance with synthetic conversations:

### Test Cases

```python
# backend/tests/eval/test_booking_flows.py
import pytest

@pytest.mark.asyncio
async def test_simple_booking():
    """User books appointment in one conversation"""
    conversation = [
        ("Book appointment with cardiologist on Monday at 2pm", 
         "book_appointment"),
        ("John Doe, annual checkup",
         "send_email_confirmation")
    ]
    
    result = await run_synthetic_conversation(conversation)
    
    assert result.success == True
    assert result.turns <= 3
    assert result.confirmation_code is not None

@pytest.mark.asyncio
async def test_ambiguous_booking():
    """User provides incomplete info, requires clarification"""
    conversation = [
        ("Book appointment with cardiologist",
         "search_timeslots"),  # Agent searches available providers
        ("Dr. Johnson",
         "search_timeslots"),  # Agent asks for date
        ("Next Monday",
         "What time works for you?"),  # Agent shows slots
        ("2pm",
         "book_appointment")  # Agent books
    ]
    
    result = await run_synthetic_conversation(conversation)
    
    assert result.success == True
    assert result.clarifications >= 2
    assert result.turns <= 5

@pytest.mark.asyncio
async def test_rag_query():
    """User asks informational question"""
    conversation = [
        ("What are your parking options?",
         "We have 3 parking garages")  # Should cite RAG docs
    ]
    
    result = await run_synthetic_conversation(conversation)
    
    assert result.success == True
    assert result.used_rag == True
    assert "parking" in result.response.lower()
```

### Benchmark Dataset

Create 100 synthetic conversations covering:
- 40 simple bookings
- 30 ambiguous bookings (need clarification)
- 15 modifications/cancellations
- 15 informational queries

**Target Performance**:
- Simple bookings: 100% success, avg 2 turns
- Ambiguous bookings: ≥90% success, avg 4 turns
- Modifications: 100% success, avg 2 turns
- Information: ≥90% relevance, avg 1 turn

## Human Evaluation

### Labeling Protocol

For 100 random conversations per week, label:

1. **Intent Classification**:
   - [ ] Booking new appointment
   - [ ] Modifying existing
   - [ ] Cancelling
   - [ ] Information seeking
   - [ ] Other/unclear

2. **Outcome**:
   - [ ] Success (task completed)
   - [ ] Partial success (some info provided)
   - [ ] Failure (unable to help)
   - [ ] Abandonment (user left mid-task)

3. **Quality Assessment** (1-5 scale):
   - Helpfulness: ___
   - Accuracy: ___
   - Tone: ___

4. **Issues** (check all that apply):
   - [ ] Wrong information provided
   - [ ] Ignored user request
   - [ ] Hallucinated capabilities
   - [ ] Rude or inappropriate
   - [ ] Too verbose
   - [ ] Too terse

### Inter-Rater Reliability

Have 2 annotators label the same 20 conversations:

```python
from sklearn.metrics import cohen_kappa_score

rater1_labels = [...]  # Outcome labels
rater2_labels = [...]

kappa = cohen_kappa_score(rater1_labels, rater2_labels)

if kappa < 0.6:
    print("⚠️ Low agreement - refine labeling guidelines")
else:
    print(f"✅ Good agreement (κ={kappa:.2f})")
```

## Monitoring Dashboards

### Grafana Dashboard

**Panels**:

1. **Task Completion** (single stat)
   - Query: `booking_success_rate`
   - Threshold: Green ≥90%, Yellow 80-90%, Red <80%

2. **Response Latency** (graph)
   - P50 line (target: 2s)
   - P90 line (target: 5s)
   - P99 line

3. **Tool Usage** (pie chart)
   - Breakdown by tool name
   - Shows most common actions

4. **Satisfaction Trend** (graph)
   - Average rating over time
   - Volume of feedback submissions

5. **Error Rate** (single stat)
   - 5xx errors / total requests
   - Alert if >1%

### Alert Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: careconnect
    interval: 1m
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.9, rate(agent_response_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P90 latency above 5s"
      
      - alert: LowCompletionRate
        expr: booking_success_rate < 0.85
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Task completion below 85%"
      
      - alert: RateLimitHit
        expr: rate(rate_limit_exceeded_total[1m]) > 10
        for: 2m
        labels:
          severity: info
        annotations:
          summary: "Multiple users hitting rate limit"
```

## Continuous Improvement

### Monthly Review

1. **Analyze low-rated conversations**:
   - Pull all conversations with rating ≤2
   - Identify common failure patterns
   - Prioritize fixes

2. **Review tool success rates**:
   ```sql
   SELECT 
     tool_name,
     COUNT(*) as calls,
     COUNT(CASE WHEN success = true THEN 1 END) * 100.0 / COUNT(*) as success_rate
   FROM tool_calls
   WHERE created_at >= NOW() - INTERVAL '30 days'
   GROUP BY tool_name
   ORDER BY calls DESC
   ```
   - If any tool <90% success, investigate why

3. **Update benchmarks**:
   - Re-run synthetic eval suite
   - Compare to previous month
   - Ensure no regressions

4. **Document learnings**:
   - What worked well
   - What failed
   - Hypotheses for next month

---

**Last Updated:** 2025
**Version:** 1.0