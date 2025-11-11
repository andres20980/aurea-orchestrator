#!/bin/bash
# Example script to run benchmarks and demonstrate the API

echo "=== Aurea Orchestrator Benchmark Examples ==="
echo ""

# Check if server is running
echo "1. Checking server health..."
curl -s http://localhost:5000/health | python -m json.tool
echo ""
echo ""

# Run a small benchmark
echo "2. Running benchmark with 10 jobs (50ms duration each)..."
curl -s -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 10, "job_duration_ms": 50}' | python -m json.tool
echo ""
echo ""

# Run a medium benchmark
echo "3. Running benchmark with 50 jobs (100ms duration each)..."
curl -s -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 50, "job_duration_ms": 100}' | python -m json.tool
echo ""
echo ""

# Run a larger benchmark
echo "4. Running benchmark with 100 jobs (100ms duration each)..."
curl -s -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 100, "job_duration_ms": 100}' | python -m json.tool
echo ""
echo ""

# Check Prometheus metrics
echo "5. Checking Prometheus metrics..."
curl -s http://localhost:5000/metrics | grep "^benchmark"
echo ""
echo ""

echo "=== Benchmarks Complete ==="
