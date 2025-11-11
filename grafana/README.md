# Grafana Dashboard Setup

This directory contains the Grafana dashboard configuration for visualizing agent evaluation metrics.

## Dashboard Features

The dashboard provides the following visualizations:

1. **Average Accuracy Trend** - Line graph showing accuracy over time
2. **Average Latency Trend** - Line graph showing latency over time
3. **Total Cost Trend** - Line graph showing costs over time
4. **Pass Rate by Feature Type** - Bar gauge showing pass rates for each feature
5. **Recent Evaluation Runs** - Table of recent evaluation runs
6. **Accuracy Distribution** - Histogram of accuracy scores
7. **Test Results by Type** - Pie chart showing golden vs regression tests

## Setup Instructions

### 1. Configure Postgres Data Source

In Grafana, add a PostgreSQL data source:

- **Host**: Your Postgres host (e.g., `localhost:5432`)
- **Database**: `aurea_evals`
- **User**: Your database user
- **Password**: Your database password
- **SSL Mode**: Prefer or require (based on your setup)

### 2. Import Dashboard

1. Log into Grafana
2. Go to Dashboards > Import
3. Upload the `dashboard.json` file
4. Select your Postgres data source
5. Click Import

### 3. Configure Refresh Rate

The dashboard is set to auto-refresh every 30 seconds. You can adjust this in the dashboard settings.

## Metrics Tracked

- **Accuracy**: How well agent outputs match expected results (0-1)
- **Latency**: Time taken to execute each test (milliseconds)
- **Cost**: Estimated cost based on token usage (USD)
- **Pass Rate**: Percentage of tests that pass accuracy threshold

## Querying Data

You can also query the data directly from Postgres:

```sql
-- Get latest evaluation runs
SELECT * FROM eval_runs ORDER BY started_at DESC LIMIT 10;

-- Get results for a specific run
SELECT * FROM eval_results WHERE run_id = <run_id>;

-- Average metrics by feature type
SELECT 
  feature_type,
  AVG(average_accuracy) as avg_accuracy,
  AVG(average_latency) as avg_latency,
  AVG(total_cost) as avg_cost
FROM eval_runs
WHERE status = 'completed'
GROUP BY feature_type;
```
