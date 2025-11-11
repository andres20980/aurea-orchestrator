"""
Example usage of Aurea Orchestrator API
"""
import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health: {response.json()}\n")

def create_task(task_id, description, model="gpt-4", max_tokens=1000):
    """Create a new task"""
    print(f"Creating task: {task_id} with model {model}...")
    
    payload = {
        "id": task_id,
        "description": description,
        "llm_model": model,
        "max_tokens": max_tokens
    }
    
    response = requests.post(f"{BASE_URL}/tasks", json=payload)
    result = response.json()
    
    print(f"✅ Task completed!")
    print(f"   - Tokens used: {result['tokens_used']}")
    print(f"   - Cost: ${result['cost_usd']}")
    print(f"   - Latency: {result['latency_ms']}ms\n")
    
    return result

def get_task(task_id):
    """Get task by ID"""
    print(f"Retrieving task: {task_id}...")
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    result = response.json()
    print(f"✅ Task status: {result['status']}\n")
    return result

def list_all_tasks():
    """List all tasks"""
    print("Listing all tasks...")
    response = requests.get(f"{BASE_URL}/tasks")
    tasks = response.json()
    print(f"✅ Found {len(tasks)} tasks\n")
    return tasks

def get_metrics_summary():
    """Get metrics summary"""
    print("Getting metrics summary...")
    response = requests.get(f"{BASE_URL}/metrics/summary")
    metrics = response.json()
    
    print(f"📊 Metrics Summary:")
    print(f"   - Total tasks processed: {metrics['total_tasks_processed']}")
    print(f"   - Total tokens used: {metrics['total_tokens_used']}")
    print(f"   - Total cost: ${metrics['total_cost_usd']}")
    print(f"   - Average latency: {metrics['avg_latency_ms']}ms\n")
    
    return metrics

def main():
    """Main example workflow"""
    print("=" * 60)
    print("Aurea Orchestrator - Example Usage")
    print("=" * 60 + "\n")
    
    # Test health
    test_health()
    
    # Create tasks with different models
    tasks = [
        ("task-1", "Analyze customer feedback sentiment", "gpt-4", 1000),
        ("task-2", "Summarize quarterly report", "gpt-3.5-turbo", 500),
        ("task-3", "Generate product description", "claude-2", 800),
        ("task-4", "Classify support ticket", "gpt-3.5-turbo", 300),
        ("task-5", "Extract key information from text", "llama-2", 600),
    ]
    
    for task_id, description, model, max_tokens in tasks:
        create_task(task_id, description, model, max_tokens)
        time.sleep(0.5)  # Small delay between tasks
    
    # List all tasks
    list_all_tasks()
    
    # Get specific task
    get_task("task-1")
    
    # Get metrics summary
    get_metrics_summary()
    
    print("=" * 60)
    print("Example completed! Check the following URLs:")
    print("  - API Docs: http://localhost:8000/docs")
    print("  - Metrics: http://localhost:8000/metrics")
    print("  - Prometheus: http://localhost:9090")
    print("  - Grafana: http://localhost:3000 (admin/admin)")
    print("=" * 60)

if __name__ == "__main__":
    main()
