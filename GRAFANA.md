# Grafana Dashboard Configuration

This guide explains how to set up Grafana dashboards to visualize the benchmark metrics from the Aurea Orchestrator.

## Prerequisites

- Running Aurea Orchestrator instance (default: `http://localhost:5000`)
- Prometheus server
- Grafana instance

## Step 1: Configure Prometheus

Add the following configuration to your `prometheus.yml`:

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'aurea-orchestrator'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

Restart Prometheus after updating the configuration.

## Step 2: Add Prometheus Data Source in Grafana

1. Open Grafana (default: `http://localhost:3000`)
2. Navigate to **Configuration** > **Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Configure:
   - Name: `Prometheus`
   - URL: `http://localhost:9090` (or your Prometheus URL)
6. Click **Save & Test**

## Step 3: Import Dashboard

Create a new dashboard with the following panels:

### Panel 1: Throughput (Jobs/Second)

**Query:**
```promql
benchmark_throughput_jobs_per_second
```

**Visualization:** Gauge or Time Series

### Panel 2: Mean Latency (Seconds)

**Query:**
```promql
benchmark_mean_latency_seconds
```

**Visualization:** Gauge or Time Series

### Panel 3: Total Cost

**Query:**
```promql
benchmark_cost_total
```

**Visualization:** Stat or Time Series

### Panel 4: Total Benchmark Runs

**Query:**
```promql
benchmark_runs_total
```

**Visualization:** Stat

### Panel 5: Total Jobs Executed

**Query:**
```promql
benchmark_jobs_total
```

**Visualization:** Stat

### Panel 6: Job Duration Distribution (95th Percentile)

**Query:**
```promql
histogram_quantile(0.95, rate(benchmark_job_duration_seconds_bucket[5m]))
```

**Visualization:** Time Series

### Panel 7: Job Duration Distribution (50th Percentile)

**Query:**
```promql
histogram_quantile(0.50, rate(benchmark_job_duration_seconds_bucket[5m]))
```

**Visualization:** Time Series

### Panel 8: Jobs Execution Rate

**Query:**
```promql
rate(benchmark_jobs_total[1m])
```

**Visualization:** Time Series

## Example Dashboard JSON

Save this as `grafana-dashboard.json` and import it in Grafana:

```json
{
  "dashboard": {
    "title": "Aurea Orchestrator Benchmark Metrics",
    "panels": [
      {
        "title": "Throughput (Jobs/Second)",
        "targets": [
          {
            "expr": "benchmark_throughput_jobs_per_second"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Mean Latency (Seconds)",
        "targets": [
          {
            "expr": "benchmark_mean_latency_seconds"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Total Cost",
        "targets": [
          {
            "expr": "benchmark_cost_total"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

## Metrics Reference

| Metric Name | Type | Description |
|------------|------|-------------|
| `benchmark_runs_total` | Counter | Total number of benchmark runs executed |
| `benchmark_jobs_total` | Counter | Total number of jobs executed across all benchmarks |
| `benchmark_throughput_jobs_per_second` | Gauge | Current throughput in jobs per second |
| `benchmark_mean_latency_seconds` | Gauge | Mean job execution latency in seconds |
| `benchmark_cost_total` | Gauge | Total cost of the last benchmark run |
| `benchmark_job_duration_seconds` | Histogram | Distribution of job execution durations |

## Alerting

You can set up alerts in Grafana based on these metrics. Example alerts:

### High Latency Alert

```promql
benchmark_mean_latency_seconds > 1.0
```

Alert when mean latency exceeds 1 second.

### Low Throughput Alert

```promql
benchmark_throughput_jobs_per_second < 10
```

Alert when throughput drops below 10 jobs/second.

## Tips

1. Use appropriate time ranges for your queries (e.g., `[5m]`, `[1h]`)
2. Consider using `rate()` function for counters to see changes over time
3. Set up refresh intervals appropriate for your use case
4. Use dashboard variables for dynamic filtering if needed
