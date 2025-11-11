#!/usr/bin/env python3
"""
Example Python script demonstrating how to use the Aurea Orchestrator benchmark API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"


def check_health():
    """Check if the server is running"""
    print("Checking server health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def run_benchmark(num_jobs, job_duration_ms=100):
    """Run a benchmark with specified parameters"""
    print(f"Running benchmark: {num_jobs} jobs @ {job_duration_ms}ms each...")
    
    payload = {
        "num_jobs": num_jobs,
        "job_duration_ms": job_duration_ms
    }
    
    response = requests.post(
        f"{BASE_URL}/benchmark/run",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Benchmark ID: {result['benchmark_id']}")
        print(f"Throughput: {result['throughput']} jobs/second")
        print(f"Mean Latency: {result['mean_latency']} seconds")
        print(f"Total Cost: ${result['total_cost']}")
        print(f"Duration: {result['duration']} seconds")
        print(f"Completed: {result['completed_jobs']}/{result['num_jobs']} jobs")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def get_metrics():
    """Fetch Prometheus metrics"""
    print("Fetching metrics...")
    response = requests.get(f"{BASE_URL}/metrics")
    
    # Filter and display only benchmark metrics
    lines = response.text.split('\n')
    benchmark_lines = [line for line in lines if line.startswith('benchmark')]
    
    print("Benchmark Metrics:")
    for line in benchmark_lines:
        print(f"  {line}")
    print()


def main():
    print("=" * 60)
    print("Aurea Orchestrator Benchmark API - Python Example")
    print("=" * 60)
    print()
    
    # Check health
    check_health()
    
    # Run different benchmark scenarios
    scenarios = [
        (10, 50),    # 10 jobs, 50ms each
        (50, 100),   # 50 jobs, 100ms each
        (100, 100),  # 100 jobs, 100ms each
    ]
    
    results = []
    for num_jobs, duration in scenarios:
        result = run_benchmark(num_jobs, duration)
        if result:
            results.append(result)
        print("-" * 60)
        print()
        time.sleep(1)  # Brief pause between benchmarks
    
    # Get metrics
    get_metrics()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total benchmarks run: {len(results)}")
    if results:
        avg_throughput = sum(r['throughput'] for r in results) / len(results)
        avg_latency = sum(r['mean_latency'] for r in results) / len(results)
        total_cost = sum(r['total_cost'] for r in results)
        print(f"Average throughput: {avg_throughput:.2f} jobs/second")
        print(f"Average latency: {avg_latency:.4f} seconds")
        print(f"Total cost: ${total_cost:.6f}")


if __name__ == "__main__":
    main()
