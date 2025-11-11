#!/usr/bin/env python3
"""
Demo script for the Aurea Orchestrator

This script demonstrates how to use the orchestrator API to create jobs
and monitor their progress.
"""
import requests
import time
import json


def main():
    base_url = "http://127.0.0.1:8000"
    
    print("=" * 60)
    print("Aurea Orchestrator Demo")
    print("=" * 60)
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(f"{base_url}/")
    print(json.dumps(response.json(), indent=2))
    
    # Create a job
    print("\n2. Creating a new job...")
    job_data = {
        "input_data": {"task": "Build and deploy a web application"},
        "max_iterations": 3
    }
    response = requests.post(f"{base_url}/jobs", json=job_data)
    job_info = response.json()
    job_id = job_info["job_id"]
    print(f"Job created with ID: {job_id}")
    print(json.dumps(job_info, indent=2))
    
    # Monitor job progress
    print("\n3. Monitoring job progress...")
    for i in range(10):
        time.sleep(2)
        response = requests.get(f"{base_url}/jobs/{job_id}/status")
        status = response.json()
        
        print(f"\n--- Check #{i+1} ---")
        print(f"Status: {status['status']}")
        print(f"Current Node: {status['current_node']}")
        print(f"Iteration: {status['iteration_count']}/{status['max_iterations']}")
        print(f"Nodes completed: {len([n for n in status['node_progress'] if n['status'] == 'completed'])}")
        
        if status['status'] == 'completed':
            print("\n4. Job completed! Final status:")
            print(json.dumps(status, indent=2, default=str))
            break
        elif status['status'] == 'failed':
            print("\n4. Job failed!")
            print(json.dumps(status, indent=2, default=str))
            break
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
