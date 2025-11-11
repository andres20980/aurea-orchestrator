# Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Aurea Orchestrator Stack                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │         │              │         │              │
│   Client     │────────▶│  Flask API   │────────▶│  Grafana     │
│              │  HTTP   │  (port 5000) │  Query  │  (port 3000) │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
                                │                         ▲
                                │                         │
                                │ Metrics                 │
                                ▼                         │
                         ┌──────────────┐                 │
                         │              │                 │
                         │  Prometheus  │─────────────────┘
                         │  (port 9090) │   Scrape /metrics
                         │              │
                         └──────────────┘
```

## Request Flow

### 1. Benchmark Execution

```
Client                          Server                      Workers
  │                               │                            │
  ├─ POST /benchmark/run ────────▶│                            │
  │  {"num_jobs": 100}            │                            │
  │                               ├─ Create ThreadPool ───────▶│
  │                               │                            │
  │                               │◀─ Job 1 executes ─────────┤
  │                               │◀─ Job 2 executes ─────────┤
  │                               │◀─ Job 3 executes ─────────┤
  │                               │◀─ ... (N parallel jobs)    │
  │                               │                            │
  │                               ├─ Calculate metrics        │
  │                               │   - Throughput             │
  │                               │   - Mean latency           │
  │                               │   - Total cost             │
  │                               │                            │
  │◀─ Response with metrics ──────┤                            │
  │  {                            │                            │
  │    "throughput": 250.5,       │                            │
  │    "mean_latency": 0.399,     │                            │
  │    "total_cost": 0.0399       │                            │
  │  }                            │                            │
```

### 2. Metrics Export

```
Prometheus                    Server
    │                           │
    ├─ GET /metrics ───────────▶│
    │  (every 5s)               │
    │                           ├─ Generate Prometheus text
    │                           │   format with all metrics
    │◀─ Metrics response ───────┤
    │  benchmark_runs_total 5   │
    │  benchmark_throughput 250 │
    │  ...                      │
```

### 3. Visualization

```
Grafana                Prometheus              Server
   │                       │                      │
   ├─ Query: ─────────────▶│                      │
   │  benchmark_           │                      │
   │  throughput           │                      │
   │                       ├─ Fetch from TSDB    │
   │                       │   (time series)      │
   │                       │                      │
   │◀─ Time series ────────┤                      │
   │  data                 │                      │
   │                       │                      │
   ├─ Render dashboard    │                      │
   │  with graphs          │                      │
```

## Component Details

### Flask API (app.py)
- **Port**: 5000
- **Endpoints**:
  - `POST /benchmark/run` - Execute synthetic workload
  - `GET /metrics` - Prometheus metrics endpoint
  - `GET /health` - Health check
- **Features**:
  - Parallel job execution using ThreadPoolExecutor
  - Prometheus metrics instrumentation
  - Request validation and error handling

### Prometheus
- **Port**: 9090
- **Configuration**: prometheus.yml
- **Scrape Interval**: 5 seconds
- **Purpose**: Time-series database for metrics

### Grafana
- **Port**: 3000
- **Default Credentials**: admin/admin
- **Purpose**: Visualization and dashboards

## Data Flow

```
Synthetic Job ──▶ Latency Measurement ──▶ Prometheus Metrics ──▶ Time Series DB ──▶ Grafana Dashboard
```

## Metrics Collected

| Metric | Type | Description |
|--------|------|-------------|
| `benchmark_runs_total` | Counter | Total benchmark executions |
| `benchmark_jobs_total` | Counter | Total jobs executed |
| `benchmark_throughput_jobs_per_second` | Gauge | Current throughput |
| `benchmark_mean_latency_seconds` | Gauge | Average job latency |
| `benchmark_cost_total` | Gauge | Total cost |
| `benchmark_job_duration_seconds` | Histogram | Job duration distribution |

## Cost Calculation

```
Cost per job = Job latency (seconds) × $0.001
Total cost = Σ(Cost per job) for all jobs
```

## Deployment Options

### Option 1: Standalone
```
┌──────────────┐
│  Flask API   │
└──────────────┘
```

### Option 2: With Monitoring (Recommended)
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Flask API   │───▶│  Prometheus  │───▶│   Grafana    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Option 3: Docker Compose (Production)
```
docker-compose.yml orchestrates all components:
  - aurea-orchestrator
  - prometheus
  - grafana
  
All connected via Docker network 'monitoring'
```
