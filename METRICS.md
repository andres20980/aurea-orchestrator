# Metrics and Monitoring Details

This document provides detailed information about the telemetry and monitoring implementation in Aurea Orchestrator.

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│                                                  │
│            Aurea Orchestrator (FastAPI)          │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  OpenTelemetry Instrumentation            │  │
│  │  - Auto-instrumentation for FastAPI       │  │
│  │  - Metrics collection                      │  │
│  └────────────────────────────────────────────┘  │
│                      │                           │
│  ┌────────────────────────────────────────────┐  │
│  │  Prometheus Client                        │  │
│  │  - Counters for tasks, tokens, cost       │  │
│  │  - Histograms for latency                 │  │
│  │  - Gauges for active tasks                │  │
│  └────────────────────────────────────────────┘  │
│                      │                           │
└──────────────────────┼───────────────────────────┘
                       │
                       │ HTTP /metrics endpoint
                       │ (Prometheus exposition format)
                       ▼
        ┌──────────────────────────────┐
        │        Prometheus            │
        │  - Scrapes metrics every 5s  │
        │  - Stores time-series data   │
        │  - Provides query interface  │
        └──────────────┬───────────────┘
                       │
                       │ PromQL queries
                       ▼
              ┌─────────────────┐
              │    Grafana      │
              │  - Visualizes   │
              │  - Dashboards   │
              │  - Alerting     │
              └─────────────────┘
```

## Metrics Collected

### HTTP Request Metrics

**`aurea_http_requests_total`** (Counter)
- Description: Total number of HTTP requests
- Labels:
  - `method`: HTTP method (GET, POST, etc.)
  - `endpoint`: API endpoint path
  - `status`: HTTP status code

**`aurea_request_latency_seconds`** (Histogram)
- Description: Request processing latency
- Labels:
  - `endpoint`: API endpoint path
- Buckets: 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, +Inf seconds

### Task Processing Metrics

**`aurea_tasks_total`** (Counter)
- Description: Total tasks processed
- Labels:
  - `model`: LLM model used (gpt-4, gpt-3.5-turbo, claude-2, llama-2)
  - `status`: Task status (completed, failed)

**`aurea_active_tasks`** (Gauge)
- Description: Number of currently active/processing tasks
- No labels

### LLM Usage Metrics

**`aurea_llm_tokens_total`** (Counter)
- Description: Total number of tokens consumed
- Labels:
  - `model`: LLM model used

**`aurea_llm_cost_usd_total`** (Counter)
- Description: Total cost in USD
- Labels:
  - `model`: LLM model used

## Cost Calculation

Token costs are based on current pricing (as of implementation):

| Model | Cost per 1K tokens |
|-------|-------------------|
| gpt-4 | $0.03 |
| gpt-3.5-turbo | $0.002 |
| claude-2 | $0.025 |
| llama-2 | $0.001 |

Formula:
```
cost_usd = (tokens_used / 1000) * rate_per_1k_tokens
```

## Prometheus Configuration

### Scrape Configuration
```yaml
scrape_configs:
  - job_name: 'aurea-orchestrator'
    static_configs:
      - targets: ['orchestrator:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Useful PromQL Queries

**Request rate:**
```promql
rate(aurea_http_requests_total[5m])
```

**Average latency:**
```promql
rate(aurea_request_latency_seconds_sum[5m]) / rate(aurea_request_latency_seconds_count[5m])
```

**P95 latency:**
```promql
histogram_quantile(0.95, rate(aurea_request_latency_seconds_bucket[5m]))
```

**Token usage rate by model:**
```promql
rate(aurea_llm_tokens_total[5m])
```

**Cost per minute:**
```promql
rate(aurea_llm_cost_usd_total[5m]) * 60
```

**Success rate:**
```promql
sum(rate(aurea_tasks_total{status="completed"}[5m])) / sum(rate(aurea_tasks_total[5m]))
```

## Grafana Dashboard

### Dashboard Panels

1. **Request Latency (p50 & p95)** - Time series
   - Shows median and 95th percentile latency
   - Helps identify performance degradation

2. **Total LLM Tokens Used** - Gauge
   - Cumulative token consumption
   - Color-coded thresholds

3. **Total LLM Cost** - Gauge
   - Running total cost
   - Helps monitor budget

4. **LLM Token Usage Rate by Model** - Time series
   - Real-time token consumption per model
   - Identifies most-used models

5. **Cost per Minute by Model** - Time series
   - Cost breakdown by model
   - Helps optimize model selection

6. **Task Processing Rate** - Time series (stacked)
   - Tasks processed per second
   - Split by model and status

7. **Active Tasks** - Gauge
   - Current concurrent tasks
   - Helps identify bottlenecks

8. **HTTP Request Rate** - Time series
   - Requests per second
   - Split by endpoint and status

### Dashboard Configuration

- **Refresh Rate**: 5 seconds (real-time)
- **Time Range**: Last 15 minutes (default)
- **Auto-refresh**: Enabled
- **Tags**: aurea, orchestrator, llm, telemetry

## OpenTelemetry Integration

The application uses:
- `opentelemetry-api`: Core OpenTelemetry API
- `opentelemetry-sdk`: SDK implementation
- `opentelemetry-instrumentation-fastapi`: Automatic FastAPI instrumentation
- `opentelemetry-exporter-prometheus`: Prometheus exporter

### Instrumentation

FastAPI is automatically instrumented to track:
- Request/response times
- Status codes
- Routes
- Exceptions

Additional custom metrics are added via Prometheus client:
- Task-specific metrics
- LLM usage metrics
- Cost tracking

## Monitoring Best Practices

### Alerting Suggestions

1. **High Latency Alert**
   ```promql
   histogram_quantile(0.95, rate(aurea_request_latency_seconds_bucket[5m])) > 5
   ```
   Alert if p95 latency exceeds 5 seconds

2. **High Cost Rate Alert**
   ```promql
   rate(aurea_llm_cost_usd_total[1h]) * 3600 > 100
   ```
   Alert if cost exceeds $100/hour

3. **Error Rate Alert**
   ```promql
   rate(aurea_http_requests_total{status=~"5.."}[5m]) > 0.1
   ```
   Alert if error rate exceeds 0.1/second

4. **High Token Usage Alert**
   ```promql
   rate(aurea_llm_tokens_total[1h]) * 3600 > 1000000
   ```
   Alert if token usage exceeds 1M/hour

### Dashboard Best Practices

1. **Monitor multiple time ranges**: Use multiple dashboard instances with different time ranges (15m, 1h, 24h)
2. **Set up annotations**: Mark deployments and changes
3. **Create custom variables**: Filter by model, endpoint, etc.
4. **Export dashboards**: Back up dashboard JSON regularly

## Data Retention

### Prometheus
- Default retention: 15 days
- Can be modified in docker-compose.yml:
  ```yaml
  command:
    - '--storage.tsdb.retention.time=30d'
  ```

### Grafana
- Dashboard configurations: Persisted in Grafana database
- Data source: Queries Prometheus in real-time

## Scaling Considerations

### High Load
- Prometheus can handle millions of time series
- Consider federation for multiple instances
- Use recording rules for expensive queries

### Multiple Instances
- Use service discovery instead of static targets
- Add instance labels to differentiate
- Consider Prometheus federation or Thanos for aggregation

## Extending Metrics

To add new metrics, update `main.py`:

```python
from prometheus_client import Counter, Histogram, Gauge

# Add new metric
my_metric = Counter('my_metric_total', 'Description', ['label1', 'label2'])

# Use in code
my_metric.labels(label1='value1', label2='value2').inc()
```

Then update Grafana dashboard to visualize the new metric.

## Security Considerations

1. **Authentication**: Add authentication to Grafana (default admin/admin should be changed)
2. **Network**: Use internal networks for Prometheus scraping
3. **Secrets**: Don't expose sensitive metrics publicly
4. **Access Control**: Limit access to /metrics endpoint in production

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/monitoring/)
