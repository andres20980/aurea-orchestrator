#!/usr/bin/env python
"""
Example usage of the Aurea Orchestrator Model Router.

This script demonstrates:
1. Recording metrics for different models
2. Selecting the best model
3. Viewing metrics summary
4. Optimizing weights
"""
import requests
import time
import random

BASE_URL = "http://localhost:8000"


def simulate_model_requests():
    """Simulate model requests with varying performance characteristics."""
    print("=" * 60)
    print("Simulating model requests...")
    print("=" * 60)
    
    # Simulate GPT-4: High quality, high cost, slower
    print("\n📝 Recording GPT-4 requests...")
    for i in range(20):
        latency = random.uniform(0.6, 1.0)
        cost = random.uniform(0.025, 0.035)
        success = random.random() > 0.02  # 98% success rate
        
        response = requests.post(f"{BASE_URL}/router/record", json={
            "model": "gpt-4",
            "latency": latency,
            "cost": cost,
            "success": success
        })
        print(f"  Request {i+1}/20: {response.status_code}")
    
    # Simulate GPT-3.5-turbo: Good quality, low cost, fast
    print("\n📝 Recording GPT-3.5-turbo requests...")
    for i in range(25):
        latency = random.uniform(0.2, 0.4)
        cost = random.uniform(0.001, 0.003)
        success = random.random() > 0.05  # 95% success rate
        
        response = requests.post(f"{BASE_URL}/router/record", json={
            "model": "gpt-3.5-turbo",
            "latency": latency,
            "cost": cost,
            "success": success
        })
        print(f"  Request {i+1}/25: {response.status_code}")
    
    # Simulate Claude-3-opus: High quality, high cost, medium speed
    print("\n📝 Recording Claude-3-opus requests...")
    for i in range(15):
        latency = random.uniform(0.5, 0.8)
        cost = random.uniform(0.02, 0.03)
        success = random.random() > 0.03  # 97% success rate
        
        response = requests.post(f"{BASE_URL}/router/record", json={
            "model": "claude-3-opus",
            "latency": latency,
            "cost": cost,
            "success": success
        })
        print(f"  Request {i+1}/15: {response.status_code}")
    
    # Simulate Claude-3-sonnet: Good quality, medium cost, medium speed
    print("\n📝 Recording Claude-3-sonnet requests...")
    for i in range(18):
        latency = random.uniform(0.4, 0.6)
        cost = random.uniform(0.01, 0.02)
        success = random.random() > 0.04  # 96% success rate
        
        response = requests.post(f"{BASE_URL}/router/record", json={
            "model": "claude-3-sonnet",
            "latency": latency,
            "cost": cost,
            "success": success
        })
        print(f"  Request {i+1}/18: {response.status_code}")
    
    # Simulate Llama-2-70b: Lower quality, very low cost, fast
    print("\n📝 Recording Llama-2-70b requests...")
    for i in range(22):
        latency = random.uniform(0.3, 0.5)
        cost = random.uniform(0.0005, 0.0015)
        success = random.random() > 0.08  # 92% success rate
        
        response = requests.post(f"{BASE_URL}/router/record", json={
            "model": "llama-2-70b",
            "latency": latency,
            "cost": cost,
            "success": success
        })
        print(f"  Request {i+1}/22: {response.status_code}")


def view_metrics():
    """View metrics summary for all models."""
    print("\n" + "=" * 60)
    print("📊 Metrics Summary")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/router/metrics")
    metrics = response.json()
    
    for model, data in metrics.items():
        if data["total_requests"] > 0:
            print(f"\n{model}:")
            print(f"  Total Requests: {data['total_requests']}")
            print(f"  Success Rate: {data['success_rate']:.2%}")
            print(f"  Avg Latency: {data['average_latency']:.3f}s")
            print(f"  Avg Cost: ${data['average_cost']:.4f}")
            print(f"  Score: {data['score']:.3f}")


def select_best_model():
    """Select the best model based on current metrics."""
    print("\n" + "=" * 60)
    print("🎯 Model Selection")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/router/select")
    result = response.json()
    
    print(f"\nSelected Model: {result['selected_model']}")
    print(f"Model Score: {result['score']:.3f}")
    print(f"\nCurrent Weights:")
    print(f"  Cost Weight: {result['weights']['cost_weight']:.3f}")
    print(f"  Quality Weight: {result['weights']['quality_weight']:.3f}")
    print(f"  Latency Weight: {result['weights']['latency_weight']:.3f}")


def optimize_weights():
    """Optimize selection weights based on performance variance."""
    print("\n" + "=" * 60)
    print("⚙️  Optimizing Weights (Weekly Task)")
    print("=" * 60)
    
    response = requests.post(f"{BASE_URL}/router/optimize")
    result = response.json()
    
    print(f"\nStatus: {result['status']}")
    print(f"\nOptimized Weights:")
    print(f"  Cost Weight: {result['weights']['cost_weight']:.3f}")
    print(f"  Quality Weight: {result['weights']['quality_weight']:.3f}")
    print(f"  Latency Weight: {result['weights']['latency_weight']:.3f}")
    
    # Show how this affects model selection
    print("\n🎯 New Model Selection with Optimized Weights:")
    select_response = requests.get(f"{BASE_URL}/router/select")
    select_result = select_response.json()
    print(f"  Selected Model: {select_result['selected_model']}")
    print(f"  Model Score: {select_result['score']:.3f}")


def main():
    """Run the example."""
    print("\n" + "=" * 60)
    print("Aurea Orchestrator - Model Router Example")
    print("=" * 60)
    
    try:
        # Check if server is running
        response = requests.get(BASE_URL, timeout=2)
        print(f"✓ Server is running at {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"✗ Server is not running at {BASE_URL}")
        print("  Please start the server with: uvicorn app.main:app --reload")
        return
    
    # Run the demo
    simulate_model_requests()
    view_metrics()
    select_best_model()
    optimize_weights()
    view_metrics()
    
    print("\n" + "=" * 60)
    print("✓ Example completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Visit http://localhost:8000/docs for API documentation")
    print("  2. Set up a weekly cron job to call /router/optimize")
    print("  3. Integrate model selection into your application")
    print()


if __name__ == "__main__":
    main()
